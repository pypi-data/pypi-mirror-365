# %% tx.py
import numpy as np
from digital_comms_lab import DigitalCommsLab, qam_pad_bits
from PIL import Image

from comms_lib.pluto import Pluto
from comms_lib.qam import qam_modulator

# --- Configuration ---
M = 16  # QAM order (16-QAM)
TX_IP = "ip:192.168.2.1"
IMAGE_FILE = "test.png"
DATA_FILE = "tx_data.npz"

# --- Initialize PlutoSDR and System Lab ---
print("Initializing transmitter...")
tx = Pluto(TX_IP)
sys = DigitalCommsLab(sample_rate=tx.sample_rate)

# --- Load image and convert to bitstream ---
print(f"Loading image: {IMAGE_FILE}")
img = Image.open(IMAGE_FILE)
img = img.resize((32, 32))  # Resize for faster transmission
img_array = np.array(img)  # Convert to NumPy array
bits = np.unpackbits(img_array)
original_img_shape = img_array.shape

# Pad bits to be a multiple of log2(M)
bits, padding = qam_pad_bits(bits, M=M)

# --- Modulation ---
print(f"Modulating bits to {M}-QAM symbols...")
data_syms = qam_modulator(bits, M=M)

# --- Prepare signal for transmission ---
print("Processing symbols for transmission...")
tx_signal = sys.process_tx_symbols(data_syms)

# --- Save data for receiver ---
# The receiver needs this data to decode and verify the transmission
print(f"Saving original data to {DATA_FILE}...")
np.savez(
    DATA_FILE,
    data_syms=data_syms,
    padding=padding,
    img_shape=original_img_shape,
    img_array=img_array,
    M=M,
)

# --- Transmit ---
print("Transmitting signal...")
tx.tx(tx_signal)
print("Transmission complete.")
