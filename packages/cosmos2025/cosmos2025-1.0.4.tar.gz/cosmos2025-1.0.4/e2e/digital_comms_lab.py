# %%
# ruff: noqa: F405
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image

from comms_lib.cfo import estimate_cfo
from comms_lib.pluto import Pluto
from comms_lib.pulse import get_rrc_pulse, pulse_shape
from comms_lib.qam import detect_qam, qam_demodulator, qam_modulator
from comms_lib.sequence import zadoff_chu_sequence
from comms_lib.utils import plot_symbols


class DigitalCommsLab:
    def __init__(self, sample_rate: float = 1e6):
        self.pulse_span: int = 20  # Pulse span in symbols
        self.pulse_sps: int = 11  # Samples per symbol
        self.beta: float = 0.5  # RRC filter roll-off factor
        self.pulse: np.ndarray = get_rrc_pulse(
            self.beta, self.pulse_span, self.pulse_sps
        )

        self.n_zc: int = 131  # Length of Zadoff-Chu sequence
        self.q_zc: int = 1  # root index for Zadoff-Chu sequence

        self.sample_rate = sample_rate

        self.ltf_len: int = 931  # Length of long training sequence
        self.stf_len: int = 31  # Length of short training sequence
        self.stf_num: int = 16  # Number of short training sequences
        self.ltf_num: int = 2  # Number of long training sequences
        self.pilots = self.gen_pilots()  # Generate pilots using Zadoff-Chu sequence

    def gen_pilots(self) -> np.ndarray:
        """
        Generate Zadoff-Chu sequence for pilots with long and short training fields.
        LTF is generated first, followed by STF.

        | LTF | ...(repeated) ... | STF | ... (repeated) ... |

        Returns:
            np.ndarray: Concatenated Zadoff-Chu sequence for STF and LTF.
        """

        ltf = np.tile(zadoff_chu_sequence(self.ltf_len, self.q_zc), self.ltf_num)
        stf = np.tile(zadoff_chu_sequence(self.stf_len, self.q_zc), self.stf_num)
        return np.concatenate((ltf, stf))

    @property
    def pilot_length(self) -> int:
        return self.pilots.shape[0]

    def frame_sync_sc(self, rx_signal: np.ndarray, seq_len: int) -> np.ndarray:
        """
        Perform Schmidl-Cox timing synchronization on the received signal.

        Args:
            rx_signal (np.ndarray): Received signal.
            seq_len (int): Length of the sequence to synchronize with.

        Returns:
            int: Index of the detected peak in the cross-correlation.
        """

        # Cross correlate the rx signal with itself on a window of seq_len:
        # Correlat rx_signal[i:i+seq_len] with rx_signal[i+seq_len:i+2*seq_len]

        # inds shoule be like [[0, 1, 2, ...], [1, 2, 3, ...], ...]
        # also, only filter ~first half of the cross-correlation, it's pretty handwavy
        # start = np.arange((rx_signal.shape[0] - seq_len) // 2)

        # first_inds = start[:, None] + np.arange(seq_len)[None, :]
        # second_inds = first_inds + seq_len
        # corr = np.sum(rx_signal[first_inds] * rx_signal[second_inds].conj(), axis=1)
        # energy = np.sum(np.abs(rx_signal[first_inds]) ** 2, axis=1)
        # corr = corr / energy  # normalize by energy
        # peak_idx = np.argmax(np.abs(corr))  # sample index where max magnitude occurs

        N = seq_len
        x = rx_signal
        x = np.asarray(x).flatten()
        M = len(x)
        num_windows = M - 2 * N + 1

        if num_windows < 1:
            raise ValueError("Signal too short for even one sliding N-to-N comparison.")

        correlations = np.zeros(num_windows, dtype=np.complex128)

        for k in range(num_windows):
            seg1 = x[k : k + N]
            seg2 = x[k + N : k + 2 * N]
            correlations[k] = np.vdot(seg1, seg2) / np.sqrt(
                N
            )  # Optional: normalize fully if desired

        peak_index = np.argmax(
            np.abs(correlations)
        )  # sample index where max magnitude occurs

        # assert peak_index == peak_idx, (
        #     f"Peak index mismatch: {peak_index} != {peak_idx}. "
        #     "This indicates a potential issue with the synchronization algorithm."
        # )

        return peak_index, correlations

    def process_tx_symbols(self, symbols: np.ndarray):
        # concatenate pilots and data symbols
        all_syms = np.concatenate((self.pilots, symbols))

        # pulse shape the symbols
        tx_signal = pulse_shape(all_syms, self.pulse, self.pulse_sps)
        return tx_signal

    def process_rx_signal(
        self, rx_signal: np.ndarray, symbol_length: int, match_filter: bool = True
    ):
        if match_filter:
            # Apply matched filter
            rx_signal = (
                np.convolve(rx_signal, self.pulse, mode="valid") / self.pulse_sps
            )

        # ========== Use MOE for symbol synchronization ==========
        """ This section is a vectorized version of the loop
        ```
        phase_energies = []
        for phase in range(self.pulse_sps):
            samples = rx_signal[start_idx + phase : end_idx : self.pulse_sps]
            energy = np.mean(np.abs(samples) ** 2)
            phase_energies.append(energy)
        ```
        Because rx_signal is of an integer times `sps`,
            we can reshape it so that each column corresponds to a different phase.
        """
        # each column corresponds to the downsampled signal for a different phase,
        # so we take the mean across the columns (axis=0)
        # reshaped_signal = rx_signal[start_idx:end_idx].reshape(-1, self.pulse_sps)
        # phase_energies = np.mean(np.abs(reshaped_signal) ** 2, axis=0)

        NN = len(rx_signal) // self.pulse_sps - 1
        rx_signal_ = rx_signal[0 : NN * self.pulse_sps]
        rx_signal_ = rx_signal_.reshape(NN, self.pulse_sps)
        phase_energies = np.mean(np.abs(rx_signal_) ** 2, axis=0)

        optimal_phase = np.argmax(phase_energies)
        print(f"Optimal phase: {optimal_phase}")
        ds_signal = rx_signal[optimal_phase :: self.pulse_sps]

        # ========== Frame synchronization with downsampled signal ==========
        # # only consider the first parts of the cross-correlation so we don't run out of buffer
        # self.cross_corr = np.correlate(ds_signal, self.pilots, mode="valid")
        # self.peak_idx = np.argmax(np.abs(self.cross_corr)[: len(self.cross_corr) // 2])

        # Use Schmidl-Cox timing synchronization
        self.peak_idx, self.cross_corr = self.frame_sync_sc(
            ds_signal[: ds_signal.shape[0] // 2], self.ltf_len
        )

        # Extract symbols starting from the detected frame boundary
        synced_symbols = ds_signal[
            self.peak_idx : self.peak_idx + self.pilot_length + symbol_length
        ]

        # ========== Extract received symbols ==========
        self.rx_pilots = synced_symbols[: self.pilot_length]
        self.rx_data_syms = synced_symbols[
            self.pilot_length : self.pilot_length + symbol_length
        ]
        pilot_phase_diff = np.angle(self.rx_pilots) - np.angle(self.pilots)
        print(f"Pilot phase diff before CFOC: {np.round(pilot_phase_diff, 2)}")

        # ========== CFO estimation and correction ==========
        # Estimate the CFO using the pilots
        total_ltf_len = self.ltf_len * self.ltf_num
        total_stf_len = self.stf_len * self.stf_num
        rx_ltf = self.rx_pilots[:total_ltf_len]
        rx_stf = self.rx_pilots[total_ltf_len : total_ltf_len + total_stf_len]

        Ts = self.pulse_sps / self.sample_rate  # Sample period in seconds

        course_cfo = estimate_cfo(
            rx_stf, seq_num=self.stf_num, seq_len=self.stf_len, Ts=Ts
        )
        rx_ltf = rx_ltf * np.exp(
            -2j * np.pi * course_cfo * np.arange(rx_ltf.shape[0]) * Ts
        )

        fine_cfo = estimate_cfo(
            rx_ltf, seq_num=self.ltf_num, seq_len=self.ltf_len, Ts=Ts
        )

        self.rx_pilots = self.rx_pilots * np.exp(
            -2j
            * np.pi
            * (course_cfo + fine_cfo)
            * np.arange(self.rx_pilots.shape[0])
            * Ts
        )

        time_offset = self.rx_pilots.shape[0]
        self.rx_data_syms = self.rx_data_syms * np.exp(
            -2j
            * np.pi
            * (course_cfo + fine_cfo)
            * (np.arange(self.rx_data_syms.shape[0]) + time_offset)
            * Ts
        )

        print(f"CFOs: course: {course_cfo:.2f}, fine: {fine_cfo:.2f}")
        pilot_phase_diff = np.angle(self.rx_pilots) - np.angle(self.pilots)
        print(f"Pilot phase diff: {np.round(pilot_phase_diff, 2)}")

        # drop the smallest pilots to avoid numerical issues
        sort_inds = np.argsort(np.abs(self.rx_pilots))
        sort_inds = sort_inds[100:-100]

        # ========== Estimate the channel and equalize the symbols ==========
        self.H = np.linalg.lstsq(
            self.pilots[sort_inds][:, None], self.rx_pilots[sort_inds], rcond=None
        )[0]
        self.eq_pilots = self.rx_pilots / self.H
        self.eq_data_syms = self.rx_data_syms / self.H

        # ch_est = np.mean(rx)
        # self.H = np.mean(self.rx_pilots / self.pilots)
        # self.eq_pilots = self.rx_pilots / self.H
        # self.eq_data_syms = self.rx_data_syms / self.H

        # ch_est_fine = np.mean(received_pilot_symbols / pilot_symbols)
        # received_qam_symbols /= ch_est_fine
        eq_data_syms = self.eq_data_syms
        return eq_data_syms

    def plot_frame_sync(self):
        """Plot the cross-correlation and the detected peak."""
        fig, ax = plt.subplots(figsize=(10, 4))
        ax.plot(np.abs(self.cross_corr), label="Cross-Correlation Magnitude")
        ax.axvline(x=self.peak_idx, color="r", linestyle="--", label="Detected Peak")
        ax.set_title(
            f"Frame Synchronization: Cross-Correlation Magnitude, Detected Peak:{self.peak_idx}"
        )
        ax.set_xlabel("Sample Index")
        ax.set_ylabel("Magnitude")
        ax.legend()
        plt.grid(True)
        plt.show()

    def calculate_ser(self, detected_symbols: np.ndarray, original_symbols: np.ndarray):
        """Calculate Symbol Error Rate (SER) between detected and original symbols."""
        return np.mean(detected_symbols != original_symbols)


def qam_pad_bits(bits: np.ndarray, M: int = 4) -> np.ndarray:
    """
    Pad bits before QAM modulation to ensure the number of bits is a multiple of the bits per symbol.
    """

    bits = bits.flatten()  # Ensure bits is a 1D array
    n_bits_per_symbol = int(np.log2(M))

    # Pad bits if necessary
    padding = (n_bits_per_symbol - len(bits) % n_bits_per_symbol) % n_bits_per_symbol
    if padding > 0:
        bits = np.concatenate([bits, np.zeros(padding, dtype=int)])

    return bits, padding


if __name__ == "__main__":
    tx = Pluto("ip:192.168.2.1")
    rx = tx
    rx = Pluto("ip:192.168.3.1")
    rx.rx_buffer_size = int(1e6)
    sys = DigitalCommsLab()
    M = 16  # QAM order

    # Load image and convert to bits
    img = Image.open("test.png")
    img = img.resize((32, 32))
    img = np.array(img)  # Convert to NumPy array
    bits = np.unpackbits(img)

    bits, padding = qam_pad_bits(bits, M=M)
    # bits = np.random.randint(0, 2, len(bits))  # Generate random bits for testing

    data_syms = qam_modulator(bits, M=M)  # Modulate bits to QAM symbols

    # Process the symbols for transmission
    tx_signal = sys.process_tx_symbols(data_syms)
    tx.tx(tx_signal)  # Transmit the signal
    rx_signal = rx.rx()  # Receive the signal

    # rx_signal = np.concatenate(
    #     (np.zeros(10 * sys.pulse_sps + 3), tx_signal)
    # )  # Simulate transmission with padding

    # H = 1 + 1j
    # rx_signal = rx_signal * H  # Simulate channel effect

    # add cfo and noise for testing
    # cfo = 500  # Simulated carrier frequency offset
    # rx_signal = rx_signal * np.exp(
    #     1j * 2 * np.pi * cfo * np.arange(len(rx_signal)) / tx.sample_rate
    # )

    rx_syms = sys.process_rx_signal(rx_signal, len(data_syms))
    det_rx_syms = detect_qam(rx_syms, M=M)  # Detect the received symbols
    rx_bits = qam_demodulator(rx_syms, M=M)  # Demodulate the received symbols

    # plot the received image
    rx_img = np.packbits(rx_bits[: rx_bits.shape[0] - padding]).reshape(img.shape)

    fig, ax = plt.subplots(1, 2, figsize=(12, 6))
    ax[0].imshow(img)
    ax[0].set_title("Original Image")
    ax[0].axis("off")
    ax[1].imshow(rx_img)
    ax[1].set_title("Received Image")
    ax[1].axis("off")
    plt.tight_layout()
    plt.show()

    sys.plot_frame_sync()  # Plot the frame synchronization results

    fig, ax = plt.subplots(1, 3, figsize=(15, 5))
    fig.suptitle("Data Symbols Comparison")
    plot_symbols(data_syms, "Original Data Symbols", ax=ax[0], alpha=0.7, s=30)
    plot_symbols(
        sys.rx_data_syms,
        "Received Data Symbols",
        ax=ax[1],
        alpha=0.7,
        s=30,
        color="red",
    )
    plot_symbols(
        rx_syms, "Equalized Data Symbols", ax=ax[2], alpha=0.7, s=30, color="green"
    )
    plt.tight_layout()
    plt.show()

    ser = sys.calculate_ser(det_rx_syms, data_syms)  # Calculate SER
    print(f"Symbol Error Rate (SER): {ser:.4f}")  # Print SER

    print(f"Estimated H: {sys.H}")

# %%
