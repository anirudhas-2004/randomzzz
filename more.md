Good morning. Let me bring everything together clearly.

---

## (1) Why the physical fault experiments won't work — for your paper

Go through each category from Abhay's fault list:

**EMI, RFI, magnetic interference (the magnet experiment)**
Your BNC cables are coaxially shielded — the outer conductor is grounded and physically surrounds the inner signal conductor, blocking external electric fields entirely. The PXI-4472 uses differential inputs internally, meaning any noise induced equally on both conductors (which is what any external field would do) is mathematically cancelled at the ADC input. A permanent magnet generates a *static* field — it only induces a current in a conductor if the magnet is *moving*, and even then the induced frequency is "whatever speed your hand moves," which is maybe 1-2 Hz, completely inaudible in a 100 kHz acquisition system and not reproducible between trials. Proper EMI susceptibility testing uses calibrated RF injection equipment, coupling networks, and screened rooms per IEC 61000 standards. A handheld magnet is not a methodology.

**Ground loop, floating ground, shielding failure**
Ground loops require a current path between two points at different ground potentials. Your PXI chassis uses star grounding — all cards share a single common ground reference inside the chassis. To create a real ground loop you'd have to actively fight the chassis architecture, which would require modifying the hardware. Floating ground and shield disconnection on a BNC connector would simply show up as a dead channel or severe noise, which is trivially obvious and not an interesting fault to characterize.

**Loose connection, cable shaking, intermittent connection**
You tried this already. The shielding and the robust BNC locking mechanism suppressed it completely. Even if it had worked, the fault signature would be random and irreproducible — you can't quantify "how loose" a connection is, so you can't build a repeatable fault dataset from it.

**Cross-talk (signal on adjacent channels)**
You tried this too and saw nothing. The PXI-4472 has >100 dB channel isolation. Cross-talk between channels is a real concern for cheap DAQ hardware but this card is specifically engineered for dynamic signal acquisition and the isolation is exceptional.

**Open circuit, short circuit, cable impedance mismatch, cable attenuation**
These are real and measurable, but the correct instrument is a VNA (Vector Network Analyzer) using TDR (Time Domain Reflectometry) and S-parameter measurements. A DAQ card is not the right tool to characterize cable faults — you'd need to be measuring reflected signal energy, not acquired signal samples.

**Power supply noise and ripple**
Real phenomenon, but you'd need a power rail probe on an oscilloscope to measure voltage noise directly on the PXI chassis supply lines. It would appear as a very small signal in your acquisition data but is impossible to distinguish from other noise sources without direct access to the supply rail.

**The faults that ARE already verified by your metrics pipeline**
Gain error, offset error, non-linearity, quantization error, aliasing, timing jitter — every single one of these shows up directly in ENOB, THD, SNR, SINAD, SFDR, and crest factor. You are already characterizing these. The DAQ hardware fault category is covered.

**Sensor faults (drift, offset, saturation, failure)**
These are defined relative to a physical transducer measuring a real process variable. Without a sensor there is no reference "true value" to deviate from. These cannot be meaningfully tested without sensors.

**Conclusion for Vikas:** The faults that are physically testable require equipment you don't have (VNA, calibrated RF injection). The faults that are testable with your current setup are already characterized by the metrics pipeline. The sensor faults require sensors. The physical manipulation experiments were tried, produced no results, and cannot produce reproducible results for the reasons above.

---

## (2) What needs to be done with your data

You have data sitting on the LabVIEW PC. Here is the exact sequence:

**Step 1 — Verify the files**
Open each .lvm file and confirm the format matches what you showed me: two columns, comma separated, time on left, voltage on right, no header rows. If LabVIEW added headers you'll need to skip them in pandas with `skiprows=N`.

**Step 2 — Confirm coherent sampling**
Your sample rate is 100 kHz. Your sine frequencies are 1 kHz, 5 kHz, 10 kHz, 20 kHz. For coherent sampling you need an integer number of cycles in the record. Check: open the file, count the total samples N, compute N / (Fs / Freq). If that's a whole number you're fine. For example, 100,000 samples at 100 kHz and 1 kHz gives exactly 1000 cycles — perfect.

**Step 3 — Run the Python script**
Set `FILENAME`, `FS = 100000`, and `FREQ` to match whichever file you're running. Run it. You get a full printout of all ~35 metrics and a saved PNG with four plots. Do this for each frequency and each waveform type you collected.

**Step 4 — Compare against expected values**
For a clean sine wave from a calibrated AFG, your sanity checks are:

- Crest factor: should be 1.414 (√2)
- Kurtosis: should be 1.5
- Skewness: should be ~0
- Dominant frequency: should match your AFG setting exactly
- Mean / DC offset: should be ~0
- ENOB: the PXI-4472 spec is ~110 dB SNR, which corresponds to ~18 ENOB. You won't hit that with a sine wave in a real environment but you should be in the 14–18 range.

Any large deviations from these expected values are findings worth documenting.

**Step 5 — Document everything in a table**
One row per file (frequency + waveform type), columns are your key metrics. This is your DAQ validation result table. The DAQ is verified when these numbers are consistent across frequencies and close to expected values.

**On square waves and impulses:** The metrics script as written assumes a sine wave input for things like THD harmonic identification and the theoretical PDF overlay. For square waves and impulses, the time-domain statistics (mean, RMS, kurtosis, crest factor) still work correctly and are meaningful. The FFT metrics will look different — a square wave has legitimate odd harmonics (3f, 5f, 7f...) so THD will be high by design, not by fault. Just note this in your documentation.

---

## (3) What else you should know — where this is going

Here is the full project arc, clearly:

**Where you are now:** DAQ chain validation. Nearly complete. Once you run the Python script on your collected data and produce the results table, this phase is done. You can write it up.

**The problem you're solving for GTRE:** During Kaveri engine test runs, they see anomalous sensor readings and have to stop the test to determine if it's the engine or the sensor. Stopping a jet engine test is expensive and time consuming. They want a system that can quickly flag "this is a sensor fault, not an engine fault" so they can continue the test or swap the sensor without a full shutdown.

**What the solution looks like:** A real-time or near-real-time signal processing pipeline that takes sensor data, extracts features (your metrics), and classifies the signal as healthy or one of several fault types. With a GUI that displays this clearly to the test cell operator.

**The path to get there:**

Right now, at home, you build a synthetic fault injection pipeline. Take your clean sine wave data (or generate synthetic clean signals). Inject the standard fault types — bias, gain error, drift, noise degradation, spike/impulse, stuck-at — at multiple severities. Extract all features from each. This gives you a labeled dataset.

Train a classifier on this synthetic dataset. Start with Random Forest — it works well on tabular feature data, gives you feature importance rankings (which tells you which of your 35 metrics actually matter for which fault), and is explainable. This is important: Vikas needs to understand what the system is doing, not treat it as a black box.

When sensors arrive, you collect real healthy and faulty sensor data, re-train or fine-tune the classifier on real data, and validate that it generalizes.

The GUI comes last — it's a wrapper around the classifier that shows incoming signal, extracted features, and the classification result in real time.

**What you should ask Vikas for this week:**
First, a clear timeline on when sensors will be available. Second, the approved procedure for moving data files out of the lab — this is a logistical blocker and needs to be resolved. Third, permission to work from home this week building the simulation pipeline, with the deliverable being a working fault injection + feature extraction + classifier prototype ready to test on real data.

**For your report:**
The project title is something like *"Sensor Fault Detection for Aero Engine Test Cell Instrumentation using Signal Processing and Machine Learning."* Your report covers: the problem statement (GTRE test interruptions), DAQ chain validation methodology and results, fault taxonomy, synthetic fault injection methodology, feature extraction, classifier design, and GUI prototype. This is a complete, credible report even before real sensors arrive. The synthetic results demonstrate the methodology works — real sensor data is validation of the approach, not a prerequisite for having done the work.

You're in a better position than you think. The project is well-scoped, the methodology is sound, and you have everything you need to make significant progress this week without touching the lab.
