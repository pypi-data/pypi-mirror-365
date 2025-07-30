# %%
# ruff: noqa: F405
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image

# Directory for saving plots
from system import DigitalCommSystem

from comms_lib.dsp import (
    create_pulse_train,
    demod_nearest,
    get_qam_constellation,
    qam_demapper,
    qam_mapper,
    calc_symbol_error_rate
)
from comms_lib.pluto import Pluto

# %%
# ---------------------------------------------------------------
# Digital communication system parameters.
# ---------------------------------------------------------------
fs = 10e6  # baseband sampling rate (samples per second)
ts = 1 / fs  # baseband sampling period (seconds per sample)
sps = 3
T = ts * sps  # time between data symbols (seconds per symbol)

# ---------------------------------------------------------------
# Initialize transmitter and receiver.
# ---------------------------------------------------------------
if False:
    # tx = Pluto("ip:192.168.2.1")
    tx = Pluto("usb:2.6.5")
    rx = tx
else:
    tx = Pluto("usb:7.5.5")
    tx.tx_gain = 100
    rx = Pluto("usb:7.6.5")
    rx.rx_gain = 100

# %%

dir_plots = "plots/"

# ---------------------------------------------------------------
# Initialize digital communication system and define system parameters.
# ---------------------------------------------------------------
system = DigitalCommSystem()
system.set_transmitter(tx)
system.set_receiver(rx)

# digital modulation parameters
modulation_order = 4  # 4, 16, 64, 256, etc.
constellation = get_qam_constellation(modulation_order, Es=1)

img = Image.open("test.png")
img = img.resize((32, 32))
img = np.array(img)
bits = np.unpackbits(img)

transmit_symbols, padding = qam_mapper(bits, constellation)
num_transmit_symbols = len(transmit_symbols)
print("Number of transmit symbols: ", num_transmit_symbols)

# Shuffle the symbols if desired
if True:
    shuffler = np.random.permutation(
        num_transmit_symbols
    )  # returns indices to shuffle the list
else:
    shuffler = np.arange(num_transmit_symbols)  # don't shuffle

transmit_symbols_shuffled = transmit_symbols[shuffler]
# transmit_symbols_shuffled = transmit_symbols

# create transmit signal
pulse_train = create_pulse_train(transmit_symbols_shuffled, sps)
pulse_shape = np.ones((sps,))
transmit_signal = np.convolve(pulse_train, pulse_shape, "full")
transmit_signal = transmit_signal[:-sps]

# transmit from Pluto!
system.transmit_signal(
    transmit_signal
)  # keep transmit signal below 10,000 samples if possible, roughly around +/-1

# receive from Pluto!
receive_signal = system.receive_signal()

# plot transmitted and received signals
if True:
    plt.figure(figsize=(12, 10))
    plt.subplot(2, 1, 1)
    plt.plot(np.real(transmit_signal), color="blue", marker="o", label="Real Transmit")
    plt.plot(np.real(receive_signal), color="red", label="Real Receive")
    plt.title("Transmit and Receive Signals (Real)")
    plt.xlabel("Time Samples")
    plt.ylabel("Amplitude")
    plt.grid(True)
    plt.legend()
    plt.subplot(2, 1, 2)
    plt.plot(
        np.imag(transmit_signal), color="blue", marker="o", label="Imaginary Transmit"
    )
    plt.plot(np.imag(receive_signal), color="red", label="Imaginary Receive")
    plt.title("Transmit and Receive Signals (Imaginary)")
    plt.xlabel("Time Samples")
    plt.ylabel("Amplitude")
    plt.grid(True)
    plt.legend()
    filename = dir_plots + "main_test_04_v01_01" + ".pdf"
    plt.savefig(filename)
    filename = dir_plots + "main_test_04_v01_01" + ".svg"
    plt.savefig(filename)
    plt.show()

# take every sps-th sample
receive_symbols = receive_signal[sps // 2 :: sps]
print("Number of receive symbols: ", len(receive_symbols))

# associate received symbols with nearest in the constellation
detected_receive_symbols_shuffled = demod_nearest(receive_symbols, constellation)

# unshuffle received symbols
detected_receive_symbols = detected_receive_symbols_shuffled[np.argsort(shuffler)]

# demap symbols to bits
rx_bits = qam_demapper(detected_receive_symbols, padding, constellation)

# calculate symbol error rate
ser = calc_symbol_error_rate(transmit_symbols, detected_receive_symbols)
print("Symbol error rate: ", ser)

# calculate bit error rate
ber = calc_symbol_error_rate(bits, rx_bits)
print("Bit error rate: ", ber)

# plot
if True:
    plt.figure(figsize=(6, 6))
    plt.scatter(
        np.real(receive_symbols),
        np.imag(receive_symbols),
        color="red",
        label="Received Preamble",
    )
    plt.scatter(
        np.real(transmit_symbols),
        np.imag(transmit_symbols),
        color="blue",
        label="Transmitted Preamble",
    )
    plt.title("Transmitted and Received Symbols")
    plt.xlabel("Real Component")
    plt.ylabel("Imaginary Component")
    plt.grid(True)
    plt.axis("square")
    plt.legend()
    filename = dir_plots + "main_test_04_v01_09" + ".pdf"
    # plt.savefig(filename)
    filename = dir_plots + "main_test_04_v01_09" + ".svg"
    # plt.savefig(filename)
    plt.show()

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
