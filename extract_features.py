import numpy as np
import pandas as pd
from scipy import signal
import matplotlib.pyplot as plt

FILENAME = "data.lvm"
FS = 100000  # Hz
FREQ = 1000  # Hz of the input sine wave

# Load
df = pd.read_csv(FILENAME, header=None, names=["time", "voltage"])
x = df["voltage"].values
N = len(x)

# --- Time domain stats ---
mean = np.mean(x)
rms = np.sqrt(np.mean(x**2))
peak = np.max(np.abs(x))
crest_factor = peak / rms
skewness = pd.Series(x).skew()
kurtosis = pd.Series(x).kurtosis() + 3  # pandas gives excess kurtosis, +3 for absolute

print(f"N samples     : {N}")
print(f"Mean          : {mean:.6f} V")
print(f"RMS           : {rms:.6f} V")
print(f"Crest Factor  : {crest_factor:.4f}  (ideal sine = {np.sqrt(2):.4f})")
print(f"Skewness      : {skewness:.4f}  (ideal sine = 0)")
print(f"Kurtosis      : {kurtosis:.4f}  (ideal sine = 1.5)")

# --- FFT ---
window = np.ones(N)  # coherent sampling assumed, no window needed
X = np.fft.rfft(x * window)
freqs = np.fft.rfftfreq(N, d=1/FS)
mag = np.abs(X) / N
mag[1:-1] *= 2  # single-sided correction

# Find fundamental bin
fund_bin = np.argmin(np.abs(freqs - FREQ))
fund_power = mag[fund_bin]**2

# THD: find harmonics up to Nyquist
harmonic_power = 0
for h in range(2, 6):
    hfreq = FREQ * h
    if hfreq >= FS / 2:
        break
    hbin = np.argmin(np.abs(freqs - hfreq))
    harmonic_power += mag[hbin]**2

# Noise power: everything except fundamental and harmonics
mask = np.ones(len(mag), dtype=bool)
for h in range(1, 6):
    hfreq = FREQ * h
    if hfreq >= FS / 2:
        break
    hbin = np.argmin(np.abs(freqs - hfreq))
    mask[max(0, hbin-2):hbin+3] = False  # blank out ±2 bins around each harmonic
mask[0] = False  # exclude DC

noise_power = np.sum(mag[mask]**2)
total_distortion_noise = harmonic_power + noise_power

snr_db = 10 * np.log10(fund_power / noise_power)
thd_db = 10 * np.log10(harmonic_power / fund_power)
sinad_db = 10 * np.log10(fund_power / total_distortion_noise)
enob = (sinad_db - 1.76) / 6.02

# SFDR: largest spur outside fundamental (±2 bins)
spur_mask = np.ones(len(mag), dtype=bool)
spur_mask[max(0, fund_bin-2):fund_bin+3] = False
spur_mask[0] = False
sfdr_db = 10 * np.log10(fund_power / np.max(mag[spur_mask]**2))

print(f"\nSNR           : {snr_db:.2f} dB")
print(f"THD           : {thd_db:.2f} dB")
print(f"SINAD         : {sinad_db:.2f} dB")
print(f"ENOB          : {enob:.2f} bits")
print(f"SFDR          : {sfdr_db:.2f} dB")

# --- Plots ---
fig, axes = plt.subplots(2, 2, figsize=(12, 8))
fig.suptitle(f"{FILENAME} | Fs={FS/1000:.0f} kHz | Fin={FREQ/1000:.0f} kHz")

axes[0,0].plot(df["time"].values[:500], x[:500])
axes[0,0].set_title("Time Domain (first 500 samples)")
axes[0,0].set_xlabel("Time"); axes[0,0].set_ylabel("V")

axes[0,1].semilogy(freqs/1000, mag)
axes[0,1].set_title("Spectrum")
axes[0,1].set_xlabel("Frequency (kHz)"); axes[0,1].set_ylabel("V")

axes[1,0].hist(x, bins=100, density=True)
axes[1,0].set_title("Amplitude PDF")
axes[1,0].set_xlabel("V"); axes[1,0].set_ylabel("Density")

# Overlay theoretical sine PDF
amp = np.sqrt(2) * rms
v = np.linspace(-amp*1.1, amp*1.1, 300)
pdf_sine = 1 / (np.pi * np.sqrt(np.maximum(amp**2 - v**2, 1e-10)))
axes[1,0].plot(v, pdf_sine, 'r--', label="Ideal sine PDF")
axes[1,0].legend()

axes[1,1].axis("off")
summary = (
    f"Mean:         {mean:.4f} V\n"
    f"RMS:          {rms:.4f} V\n"
    f"Crest Factor: {crest_factor:.4f}  (√2 = {np.sqrt(2):.4f})\n"
    f"Skewness:     {skewness:.4f}  (ideal = 0)\n"
    f"Kurtosis:     {kurtosis:.4f}  (ideal = 1.5)\n\n"
    f"SNR:          {snr_db:.2f} dB\n"
    f"THD:          {thd_db:.2f} dB\n"
    f"SINAD:        {sinad_db:.2f} dB\n"
    f"ENOB:         {enob:.2f} bits\n"
    f"SFDR:         {sfdr_db:.2f} dB"
)
axes[1,1].text(0.1, 0.5, summary, transform=axes[1,1].transAxes,
               fontsize=11, verticalalignment="center", fontfamily="monospace")

plt.tight_layout()
plt.savefig(FILENAME.replace(".lvm", "_analysis.png"), dpi=150)
plt.show()
