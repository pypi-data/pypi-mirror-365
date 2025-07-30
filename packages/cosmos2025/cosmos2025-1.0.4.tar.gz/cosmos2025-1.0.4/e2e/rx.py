# %% rx.py
import numpy as np
from digital_comms_lab import DigitalCommsLab
from matplotlib import pyplot as plt

from comms_lib.pluto import Pluto
from comms_lib.qam import detect_qam, qam_demodulator
from comms_lib.utils import plot_symbols

# --- Configuration ---
RX_IP = "ip:192.168.3.1"
DATA_FILE = "tx_data.npz"

# --- Load data from transmitter ---
print(f"Loading data from {DATA_FILE}...")
try:
    tx_data = np.load(DATA_FILE)
    data_syms = tx_data['data_syms']
    padding = tx_data['padding']
    img_shape = tx_data['img_shape']
    original_img = tx_data['img_array']
    M = int(tx_data['M'])
except FileNotFoundError:
    print(f"Error: {DATA_FILE} not found. Please run the tx.py script first.")
    exit()

# --- Initialize PlutoSDR and System Lab ---
print("Initializing receiver...")
rx = Pluto(RX_IP)
rx.rx_buffer_size = int(2e6) # Ensure buffer is large enough
sys = DigitalCommsLab(sample_rate=rx.sample_rate)

# --- Receive Signal ---
print("Receiving signal...")
rx_signal = rx.rx()

# --- Signal Processing and Demodulation ---
print("Processing received signal...")
# Process the signal to get symbols (includes sync, equalization)
rx_syms = sys.process_rx_signal(rx_signal, len(data_syms))

# Demodulate symbols to bits
rx_bits = qam_demodulator(rx_syms, M=M)

# Detect symbols for SER calculation
det_rx_syms = detect_qam(rx_syms, M=M)

# --- Reconstruct Image ---
print("Reconstructing image...")
# Remove padding and pack bits into bytes, then reshape to image dimensions
total_bits = rx_bits.shape[0]
if padding > 0:
    rx_bits_unpadded = rx_bits[: total_bits - padding]
else:
    rx_bits_unpadded = rx_bits

rx_img_array = np.packbits(rx_bits_unpadded).reshape(img_shape)

# --- Analysis and Visualization ---
print("Analyzing results...")

# Calculate and print Symbol Error Rate (SER)
ser = sys.calculate_ser(det_rx_syms, data_syms)
print(f"Symbol Error Rate (SER): {ser:.4f}")
print(f"Estimated Channel (H): {sys.H}")

# Plot Original vs. Received Image
fig, ax = plt.subplots(1, 2, figsize=(12, 6))
fig.suptitle("Image Transmission Result")
ax[0].imshow(original_img)
ax[0].set_title("Original Image")
ax[0].axis("off")
ax[1].imshow(rx_img_array)
ax[1].set_title("Received Image")
ax[1].axis("off")
plt.tight_layout()
plt.show()

# Plot Frame Synchronization
sys.plot_frame_sync()

# Plot Symbol Constellations
fig, ax = plt.subplots(1, 3, figsize=(18, 6))
fig.suptitle("Data Symbols Comparison")
plot_symbols(data_syms, "1. Original Symbols", ax=ax[0])
plot_symbols(sys.rx_data_syms, "2. Received (Post-Sync)", ax=ax[1], color="red")
plot_symbols(rx_syms, "3. Equalized", ax=ax[2], color="green")
plt.tight_layout()
plt.show()