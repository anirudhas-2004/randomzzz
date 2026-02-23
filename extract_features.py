import numpy as np
import pandas as pd
from scipy.stats import skew, kurtosis as scipy_kurtosis
from scipy.signal import welch
import matplotlib.pyplot as plt

FILENAME = "data.lvm"
FS = 100000
FREQ = 1000

df = pd.read_csv(FILENAME, header=None, names=["time", "voltage"])
x = df["voltage"].values
N = len(x)
t = df["time"].values

# ── TIME DOMAIN ───────────────────────────────────────────────────
mean        = np.mean(x)
median      = np.median(x)
variance    = np.var(x)
std_dev     = np.std(x)
rms         = np.sqrt(np.mean(x**2))
peak        = np.max(np.abs(x))
peak_pos    = np.max(x)
peak_neg    = np.min(x)
peak_to_peak= peak_pos - peak_neg
mav         = np.mean(np.abs(x))
crest_factor= peak / rms
impulse_factor = peak / mav
coeff_var   = std_dev / mean if mean != 0 else np.inf
iqr         = np.percentile(x, 75) - np.percentile(x, 25)
skewness    = skew(x)
kurt        = scipy_kurtosis(x, fisher=False)  # absolute kurtosis (sine=1.5, noise=3)
dc_offset   = mean

zcr = np.sum(np.diff(np.sign(x)) != 0) / (N - 1)

# ── FREQUENCY DOMAIN ─────────────────────────────────────────────
X       = np.fft.rfft(x)
freqs   = np.fft.rfftfreq(N, d=1/FS)
mag     = np.abs(X) / N
mag[1:-1] *= 2

pwr     = mag**2
fund_bin = np.argmin(np.abs(freqs - FREQ))
fund_pwr = pwr[fund_bin]

# Harmonics (2nd–5th)
harmonic_bins = []
harmonic_pwr  = 0
for h in range(2, 6):
    hf = FREQ * h
    if hf >= FS / 2:
        break
    hb = np.argmin(np.abs(freqs - hf))
    harmonic_bins.append(hb)
    harmonic_pwr += pwr[hb]

# Noise mask: exclude DC, fundamental ±2 bins, harmonics ±2 bins
noise_mask = np.ones(len(mag), dtype=bool)
noise_mask[0] = False
for b in [fund_bin] + harmonic_bins:
    noise_mask[max(0, b-2):b+3] = False

noise_pwr       = np.sum(pwr[noise_mask])
noise_floor_db  = 10 * np.log10(np.min(pwr[1:]))
noise_rms       = np.sqrt(noise_pwr)
noise_var       = noise_pwr

total_dist_noise = harmonic_pwr + noise_pwr

snr_db      = 10 * np.log10(fund_pwr / noise_pwr)
thd_db      = 10 * np.log10(harmonic_pwr / fund_pwr)
sinad_db    = 10 * np.log10(fund_pwr / total_dist_noise)
thdn_db     = 10 * np.log10(total_dist_noise / fund_pwr)
enob        = (sinad_db - 1.76) / 6.02
dynamic_range_db = 10 * np.log10(fund_pwr / np.min(pwr[pwr > 0]))

# SFDR
spur_mask = np.ones(len(mag), dtype=bool)
spur_mask[max(0, fund_bin-2):fund_bin+3] = False
spur_mask[0] = False
sfdr_db = 10 * np.log10(fund_pwr / np.max(pwr[spur_mask]))

dominant_freq = freqs[np.argmax(pwr[1:]) + 1]

# Spectral features (weighted by power)
total_pwr       = np.sum(pwr[1:])
spec_centroid   = np.sum(freqs[1:] * pwr[1:]) / total_pwr
spec_spread     = np.sqrt(np.sum(pwr[1:] * (freqs[1:] - spec_centroid)**2) / total_pwr)
spec_flatness   = 10 * np.log10(np.exp(np.mean(np.log(pwr[1:] + 1e-30))) / np.mean(pwr[1:]))

pwr_norm        = pwr[1:] / total_pwr
pwr_norm        = np.clip(pwr_norm, 1e-30, None)
spec_entropy    = -np.sum(pwr_norm * np.log2(pwr_norm))

spec_skewness   = skew(pwr[1:])
spec_kurt       = scipy_kurtosis(pwr[1:], fisher=False)

# Bandwidth: -3dB around fundamental
half_pwr = fund_pwr / 2
bw_mask  = pwr >= half_pwr
bw       = freqs[bw_mask][-1] - freqs[bw_mask][0] if bw_mask.any() else 0

# Occupied bandwidth: 99% of total power
cum_pwr  = np.cumsum(pwr[1:])
occ_bw   = freqs[1:][np.searchsorted(cum_pwr, 0.99 * total_pwr)] - freqs[1]

# ── PRINT ─────────────────────────────────────────────────────────
results = {
    "Mean":               (mean,           "V",   "~0 for AC"),
    "Median":             (median,         "V",   ""),
    "DC Offset":          (dc_offset,      "V",   "~0 for AC"),
    "Variance":           (variance,       "V²",  ""),
    "Std Dev":            (std_dev,        "V",   ""),
    "RMS":                (rms,            "V",   ""),
    "Peak":               (peak,           "V",   ""),
    "Peak-to-Peak":       (peak_to_peak,   "V",   ""),
    "Min / Max":          (f"{peak_neg:.4f} / {peak_pos:.4f}", "V", ""),
    "MAV":                (mav,            "V",   ""),
    "Crest Factor":       (crest_factor,   "",    f"ideal sine={np.sqrt(2):.4f}"),
    "Impulse Factor":     (impulse_factor, "",    ""),
    "Coeff of Variation": (coeff_var,      "",    ""),
    "IQR":                (iqr,            "V",   ""),
    "Skewness":           (skewness,       "",    "ideal sine=0"),
    "Kurtosis":           (kurt,           "",    "ideal sine=1.5, noise=3"),
    "Zero Crossing Rate": (zcr,            "/samp",""),
    "SNR":                (snr_db,         "dB",  ""),
    "THD":                (thd_db,         "dB",  ""),
    "SINAD":              (sinad_db,       "dB",  ""),
    "THD+N":              (thdn_db,        "dB",  ""),
    "ENOB":               (enob,           "bits",""),
    "SFDR":               (sfdr_db,        "dB",  ""),
    "Dynamic Range":      (dynamic_range_db,"dB", ""),
    "Noise Floor":        (noise_floor_db, "dB",  ""),
    "Noise RMS":          (noise_rms,      "V",   ""),
    "Noise Variance":     (noise_var,      "V²",  ""),
    "Dominant Frequency": (dominant_freq,  "Hz",  f"expected={FREQ}"),
    "Spectral Centroid":  (spec_centroid,  "Hz",  ""),
    "Spectral Spread":    (spec_spread,    "Hz",  ""),
    "Spectral Flatness":  (spec_flatness,  "dB",  ""),
    "Spectral Entropy":   (spec_entropy,   "bits",""),
    "Spectral Skewness":  (spec_skewness,  "",    ""),
    "Spectral Kurtosis":  (spec_kurt,      "",    ""),
    "Bandwidth (-3dB)":   (bw,             "Hz",  ""),
    "Occupied BW (99%)":  (occ_bw,         "Hz",  ""),
}

print(f"\n{'Metric':<25} {'Value':>14}  {'Unit':<6}  Note")
print("-" * 65)
for name, (val, unit, note) in results.items():
    valstr = f"{val:.4f}" if isinstance(val, float) else str(val)
    print(f"{name:<25} {valstr:>14}  {unit:<6}  {note}")

# ── PLOTS ─────────────────────────────────────────────────────────
fig, axes = plt.subplots(2, 2, figsize=(13, 9))
fig.suptitle(f"{FILENAME}  |  Fs={FS/1000:.0f} kHz  |  Fin={FREQ/1000:.1f} kHz")

axes[0,0].plot(t[:1000], x[:1000])
axes[0,0].set_title("Time Domain (first 1000 samples)")
axes[0,0].set_xlabel("Time (s)"); axes[0,0].set_ylabel("V")

axes[0,1].semilogy(freqs/1000, mag)
axes[0,1].axvline(FREQ/1000, color='r', linestyle='--', alpha=0.5, label='Fundamental')
axes[0,1].set_title("Spectrum"); axes[0,1].set_xlabel("Frequency (kHz)")
axes[0,1].set_ylabel("V"); axes[0,1].legend()

axes[1,0].hist(x, bins=100, density=True, alpha=0.7)
amp = np.sqrt(2) * rms
v   = np.linspace(-amp*1.1, amp*1.1, 300)
pdf = 1 / (np.pi * np.sqrt(np.maximum(amp**2 - v**2, 1e-10)))
axes[1,0].plot(v, pdf, 'r--', label="Ideal sine PDF")
axes[1,0].set_title("Amplitude PDF"); axes[1,0].set_xlabel("V")
axes[1,0].set_ylabel("Density"); axes[1,0].legend()

axes[1,1].semilogy(freqs/1000, pwr)
axes[1,1].set_title("Power Spectrum"); axes[1,1].set_xlabel("Frequency (kHz)")
axes[1,1].set_ylabel("V²")

plt.tight_layout()
plt.savefig(FILENAME.replace(".lvm", "_analysis.png"), dpi=150)
plt.show()
