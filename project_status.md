---
title: Project Status — Direction & Next Steps
index: 02
date: 2026-02-28
---

## What We Have Done

Set up the DAQ system — PXI-4472 with AFG1022 as the signal source — and acquired data for sine waves at 1 kHz, 5 kHz, 10 kHz, and 20 kHz at 100 kHz sample rate. Also collected square waves, impulse signals, and ramp signals.

Figured out LabVIEW enough to acquire multi-channel data, write to `.lvm` files, and understand the signal flow.

Written a Python analysis pipeline that takes any `.lvm` file and computes:

**Time Domain** — Mean, Median, DC Offset, Variance, Std Dev, RMS, Peak, Peak-to-Peak, Min/Max, Mean Absolute Value, Crest Factor, Impulse Factor, Coefficient of Variation, IQR, Skewness, Kurtosis, Zero Crossing Rate

**Frequency Domain** — SNR, THD, THD+N, SINAD, ENOB, SFDR, Dynamic Range, Noise Floor, Noise RMS, Noise Variance, Dominant Frequency, Spectral Centroid, Spectral Spread, Spectral Flatness, Spectral Entropy, Spectral Kurtosis, Spectral Skewness, Bandwidth (-3dB), Occupied Bandwidth (99%)

**Output** — Printed table of all metrics + a saved 4-panel plot (time domain, spectrum, power spectrum, amplitude PDF with theoretical overlay).

Next step is running this on collected data and documenting results as DAQ validation output.

## Why Physical Fault Experiments Will Not Work

Every fault category was attempted or considered. Here is why none are viable:

**EMI / Magnetic interference** — A permanent magnet produces a static field and only induces current when moving. Moving-hand frequency (~1–2 Hz) is invisible at 100 kHz acquisition. BNC cables are coaxially shielded and the PXI-4472 uses differential inputs that cancel equally-induced noise. Proper EMI testing requires calibrated RF injection equipment per IEC 61000.

**Ground loops** — The PXI chassis uses star grounding with a shared common reference. Creating a real ground loop requires modifying hardware. The experiment cannot produce a visible result without that.

**Loose / intermittent connections** — Tried. BNC locking mechanism and shielding suppressed it. Even if something appeared, it would be random and irreproducible — cannot quantify "how loose" a connection is, so no repeatable dataset is possible.

**Crosstalk** — PXI-4472 has >100 dB channel isolation. Tried adjacent channel injection. Saw nothing, as expected.

**Cable faults** — Real and measurable, but the correct instrument is a VNA using TDR measurements. A DAQ card is not the right tool. We do not have a VNA.

**Power supply noise** — Requires a power rail probe on an oscilloscope connected directly to chassis supply lines. Cannot be isolated in signal acquisition data.

**DAQ hardware faults** — Already captured by our pipeline: ENOB, THD, SNR, SINAD, SFDR. This is covered.

**Sensor faults** — Defined relative to a physical transducer measuring a real process variable. Without a sensor there is no "true value" to deviate from.

> Physical manipulation experiments have no further productive path.

## What Should Be Done Next

Two paths forward, both previously discussed:

**(a) Software simulation of sensor faults** — can begin immediately.

1. Take clean captured data (or generate synthetic clean signals)
2. Inject standard fault types at controlled, parameterized severities:
   - Bias / DC offset fault (add a constant)
   - Gain fault (multiply by a factor ≠ 1)
   - Drift fault (add a slow ramp over time)
   - Noise degradation (add Gaussian noise)
   - Spike / impulse fault (inject random large samples)
   - Stuck-at / complete failure (replace with a constant)
3. Extract all features from each clean and faulty signal window
4. Build a labeled dataset: each row is one window, each column is a feature, label is fault type and severity
5. Train a classifier (Random Forest — explainable, works well on tabular data, gives feature importance rankings)
6. When real sensors arrive, test on real data and retrain if needed
7. Build the GUI around the classifier

**(b) Real sensors** — Asking sir: is there a timeline on when sensors — working or faulty — might be available? Even one faulty sensor would let us validate that the simulation approach generalises to real hardware.

Also need to ask about **data transfer** — all acquired data is on the LabVIEW PC. What is the approved procedure for moving files to our machines?

## What This Project Becomes

**Problem** — Test cell engineers stop engine runs when sensor readings look anomalous. Often this is a sensor fault, not an engine fault. Identifying this quickly avoids unnecessary test interruptions.

**Solution** — A real-time signal processing pipeline that takes sensor data, extracts features, classifies the signal as healthy or a specific fault type, and displays the result to the operator through a GUI.

**Deliverables**

- DAQ chain validation (done — pending results documentation)
- Fault taxonomy with physical justification of each fault type
- Synthetic fault injection pipeline and labeled dataset
- Trained fault classifier with feature importance analysis
- GUI prototype displaying signal health and fault classification
- Full written report suitable for college submission
