# %%
import numpy as np
from digital_comms_lab import DigitalCommsLab, qam_pad_bits
from matplotlib import pyplot as plt
from PIL import Image

from comms_lib.pluto import Pluto
from comms_lib.qam import detect_qam, qam_demodulator, qam_modulator
from comms_lib.utils import plot_symbols

tx = Pluto("ip:192.168.2.1")
rx = tx
rx = Pluto("ip:192.168.3.1")
rx.rx_buffer_size = int(1e6)
sys = DigitalCommsLab(sample_rate=rx.sample_rate)
M = 16  # QAM order

# Load image and convert to bits
img = Image.open("test.png")
img = img.resize((32, 32))
img = np.array(img)  # Convert to NumPy array
bits = np.unpackbits(img)

bits, padding = qam_pad_bits(bits, M=M)
# bits = np.random.randint(0, 2, len(bits))  # Generate random bits for testing

data_syms = qam_modulator(bits, M=M)  # Modulate bits to QAM symbols

tx_signal = sys.process_tx_symbols(data_syms)  # Process the symbols for transmission
tx.tx(tx_signal)  # Transmit the signal
rx_signal = rx.rx()  # Receive the signal

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
    sys.rx_data_syms, "Received Data Symbols", ax=ax[1], alpha=0.7, s=30, color="red"
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
