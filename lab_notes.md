---
title: Lab Notes — Signal Acquisition & Analysis
index: 01
date: 2026-02-28
---

## Reference

[ChatGPT Session](https://chatgpt.com/share/699ad022-1fb0-8012-a9c9-2450fe1898a6)

## Frequencies Tested

10 Hz, 100 Hz, 1 kHz, 5 kHz, 10 kHz

*Data for remaining frequencies to be appended after acquisition.*

## Team Division

**Team A** — Data Acquisition

**Team B** — Parallel Data Analysis (compute the following metrics as data comes in)

## Metrics to Compute

### Compulsory

Mean (DC Offset), Standard Deviation, Variance, RMS, Peak Value, Peak-to-Peak Value, Minimum, Maximum, Range, SNR, Noise RMS, Noise Floor, Crest Factor, Form Factor, Skewness, Kurtosis, Zero Crossing Rate, THD, THD+N, SINAD, Dynamic Range, ENOB, Dominant Frequency, Bandwidth, Autocorrelation, INL, DNL

### Full List

**Statistics** — Mean, Median, Mode, Variance, Standard Deviation, Standard Error, RMS, Peak Value, Peak-to-Peak Value, Minimum, Maximum, Range, Sum, Energy, Power

**Distortion & Noise** — SNR, SINAD, THD, THD+N, Noise Floor, Noise RMS, Noise Variance, Quantization Noise, ENOB, Dynamic Range

**Shape Descriptors** — Skewness, Kurtosis, Crest Factor, Form Factor, Shape Factor, Impulse Factor, Margin Factor, Clearance Factor, Coefficient of Variation, Mean Absolute Value, MAD, IQR

**Time Domain** — Zero Crossing Rate, Autocorrelation, Cross-correlation, Covariance, DC Offset

**Frequency Domain** — Dominant Frequency, Frequency Mean, Frequency Variance, Spectral Centroid, Spectral Spread, Spectral Flatness, Spectral Entropy, Spectral Kurtosis, Spectral Skewness, Bandwidth, Occupied Bandwidth, Total Energy, Average Power, Peak Power

**Linearity** — Linearity Error, INL, DNL

## Fault Types Reference

### Grounding & Shielding
Ground fault, Ground loop, Floating ground, Improper grounding, Shielding failure, Unshielded cable, Shield disconnected

### Interference
EMI, RFI, Power line interference (50/60 Hz), Cross-talk, External noise coupling, Noise injection

### Connection & Cable
Loose connection, Intermittent connection, Open circuit, Short circuit, Cable fault, Cable attenuation, Cable impedance mismatch, Cable damage

### Signal Issues
Signal attenuation, Signal clipping, Signal distortion

### Sensor Faults
Sensor fault, Sensor drift, Sensor offset, Sensor saturation

### DAQ Hardware
DAQ hardware fault, Gain error, Offset error, Non-linearity, Quantization error

### Sampling Faults
Aliasing, Timing jitter, Sample loss

### Power Supply
Power supply noise, Power supply ripple, Power supply fluctuation
