# Photodiode Transimpedance Amplifier — Design & Noise Analysis

Design tool for Butterworth-optimized photodiode transimpedance amplifiers (TIAs), with focus on balanced (differential) detection applications.

## Application

Two identical photodiodes are connected to two identical TIA channels. The small difference between their output voltages is extracted as the signal. This requires:

- **Low and stable $I_b$** (JFET-input opamp): inter-channel DC offset $= R_f \times \Delta I_b$
- **Low temperature drift of $I_b$**: bipolar opamps produce unacceptable offset drift for this application
- **Noise performance is secondary** to $I_b$ stability

## Features

- **Butterworth-optimized $C_f$** — exact solution (no approximation of $\omega_c R_f C_f \gg 1$)
- **2nd-order Butterworth NEB** — $\pi\sqrt{2}/4 \cdot f_{-3\text{dB}}$, not the single-pole approximation
- **Piecewise voltage noise integration** — accounts for noise gain shape (zero, rising, plateau, rolloff regions)
- **Opamp comparison table** — compare all opamps in the database with one function call
- **Parameter sweep & plotting** — explore $R_f$ vs SNR/bandwidth/shot-noise-limit trade-offs
- **CSV-based component database** — add new opamps or photodiodes by editing a CSV file

## Project structure

```
OPAMP_circuit_design/
├── tia_design.py                  # Calculation engine (functions & dataclasses)
├── Photodiode_TIA_design.ipynb    # Interactive notebook
├── technical_note_tia_theory.md   # Full derivations of TIA formulas
├── data/
│   ├── opamps.csv                 # Opamp parameter database
│   └── photodiodes.csv            # Photodiode parameter database
└── README.md
```

## Quick start

```python
from tia_design import *

opamps = load_opamps()
pd = load_photodiodes()['PIN-6D']

# Single design
result = design_tia(opamps['OPA827'], pd, R_f=20e3, Vb=12, E_photo=0.15e-3)
print_result(result)

# Compare all opamps
compare_opamps(opamps, pd, R_f=20e3, Vb=12, E_photo=0.15e-3)

# Compare JFET-input opamps only
jfet = {k: v for k, v in opamps.items() if v.input_type == 'JFET'}
compare_opamps(jfet, pd, R_f=20e3, Vb=12, E_photo=0.15e-3)
```

### Example output

```
=== TIA Design: OPA827 ===
  C_d  = 55.0 pF,  C_i = 73.0 pF
  C_f  = 7.26 pF  (Butterworth optimum)
  BW   = 1.48 MHz,  NEB = 1.64 MHz
  Noise gain peak = 11.1

  Noise breakdown (output-referred RMS):
    E_noe  (opamp voltage) = 79.7 uV
    E_noR  (Rf thermal)    = 23.2 uV
    E_no_bg    (total BG)  = 83.0 uV
    E_noi_sig  (sig shot)  = 131.6 uV

  Figures of merit:
    Signal         = 1650.00 mV
    SNR            = 10604  (80.5 dB)
    bg/shot ratio  = 0.63  (shot-noise limited)
    Offset/ch      = 60.0 nV
```

## Adding a new opamp

Add one row to `data/opamps.csv`.  Each column corresponds to a specific datasheet parameter:

| CSV column | Datasheet parameter | Unit | Where to find in datasheet |
| --- | --- | --- | --- |
| `name` | Part number | — | Front page |
| `f_c` | Gain Bandwidth Product (GBW or GBP) | Hz | "Electrical Characteristics" table, or "Open-Loop Gain vs Frequency" plot (frequency at 0 dB) |
| `I_b` | Input Bias Current | A | "Electrical Characteristics" table, typical value |
| `f_f` | 1/f noise corner frequency | Hz | "Input Voltage Noise Spectral Density vs Frequency" plot — the frequency where the 1/f slope meets the white-noise floor |
| `e_nif` | Input Voltage Noise Density (flat/white region) | V/sqrt(Hz) | Same plot as above — the flat floor level at high frequency (typically > 1 kHz) |
| `i_nif` | Input Current Noise Density (flat/white region) | A/sqrt(Hz) | "Input Current Noise Spectral Density vs Frequency" plot — the flat floor level. For JFET opamps this is often listed only in the characteristics table |
| `C_icm` | Common-Mode Input Capacitance | F | "Electrical Characteristics" table or "Typical Application" section |
| `C_id` | Differential Input Capacitance | F | Same as above. If not listed separately, set to 0 |
| `input_type` | Input stage type | — | `JFET`, `bipolar`, or `CMOS` — from product description or "Features" section |
| `notes` | Free-form description | — | — |

Example row:

```csv
OPA828,45e6,1e-12,200,3.4e-9,4.5e-15,5.2e-12,3e-12,JFET,New low-noise JFET opamp
```

## Photodiode parameters

Photodiode parameters are stored in `data/photodiodes.csv`:

| CSV column | Datasheet parameter | Unit | Description |
| --- | --- | --- | --- |
| `name` | Part number | — | — |
| `Cd_spec` | Junction Capacitance at specified reverse bias | F | "Electrical Characteristics" table, at `Vb_spec` |
| `Vb_spec` | Reverse bias voltage for `Cd_spec` | V | The bias condition under which `Cd_spec` is specified |
| `phi_b` | Built-in voltage (contact potential) | V | Typically 0.2-0.6 V for Si. Used in the abrupt-junction model: C_d(Vb) = Cd0 / sqrt(1 + Vb/phi_b) |
| `Id_spec` | Dark current at specified reverse bias | A | "Electrical Characteristics" table, at `Vb_spec` |
| `r_phi` | Responsivity | A/W | "Responsivity vs Wavelength" plot, at operating wavelength |
| `wl` | Operating wavelength | m | Wavelength at which `r_phi` is specified |

## Operating conditions

The `design_tia()` function takes the following operating condition parameters:

| Parameter | Unit | Description |
| --- | --- | --- |
| `R_f` | Ohm | Feedback resistance of the TIA. Determines transimpedance gain (V_out = R_f x I_p). Larger R_f gives higher gain and lower relative thermal noise, but reduces bandwidth |
| `Vb` | V | Reverse bias voltage applied to the photodiode. Affects junction capacitance C_d (higher Vb reduces C_d) and dark current I_d |
| `E_photo` | W | Incident optical power on the photodiode. The signal photocurrent is I_p = E_photo x r_phi |
| `T` | K | Operating temperature (default 296 K = 23 C). Affects Johnson noise of R_f |
| `C_s` | F | Stray capacitance in parallel with C_f (e.g. PCB parasitic). Default 0 |
| `C_d_override` | F | Optional override for photodiode capacitance. Use when the measured C_d differs from the abrupt-junction model |

## Theory

> Full step-by-step derivations are given in [technical_note_tia_theory.pdf](technical_note_tia_theory.pdf).

### Closed-loop transfer function

The TIA uses an opamp with a single-pole open-loop gain $A(s) = \omega_c / s$,
where $\omega_c = 2\pi f_c$ (gain-bandwidth product in rad/s).
Applying feedback analysis to the inverting configuration with
feedback impedance $Z_f = R_f \parallel C_f$ and
input capacitance $C_i = C_d + C_{icm} + C_{id}$,
the closed-loop transimpedance is:

```math
Z_{TI}(s) = \frac{-R_f \, \omega_n^2}{s^2 + 2\zeta\omega_n s + \omega_n^2}
```

where the natural frequency and damping ratio are:

```math
\omega_n^2 = \frac{\omega_c}{R_f (C_i + C_f + C_s)}, \qquad 2\zeta\omega_n = \frac{1 + \omega_c R_f C_f}{R_f (C_i + C_f + C_s)}.
```

### Butterworth design

The Butterworth (maximally-flat) condition $Q = 1/\sqrt{2}$ (i.e. $\zeta = 1/\sqrt{2}$) eliminates gain peaking.
Substituting into the damping equation and using $C_c = 1/(\omega_c R_f)$:

```math
(1 + \omega_c R_f C_f)^2 = 2\,\omega_c R_f (C_i + C_f + C_s)
```

```math
\Rightarrow \quad C_f = \sqrt{C_c \bigl(2(C_i + C_s) - C_c\bigr)}, \qquad C_c = \frac{1}{2\pi f_c R_f}.
```

This is the exact solution without the common approximation $\omega_c R_f C_f \gg 1$.
See Graeme 1996.

### Bandwidth and noise equivalent bandwidth

For the Butterworth response, the $-3\,\text{dB}$ bandwidth equals the natural frequency:

```math
f_{-3\text{dB}} = \frac{\omega_n}{2\pi} = \sqrt{\frac{f_c}{2\pi R_f (C_i + C_f + C_s)}}.
```

The noise equivalent bandwidth for an $n$-th order Butterworth filter is
$\text{NEB} = f_{-3\text{dB}} \cdot \frac{\pi}{2n} / \sin\!\left(\frac{\pi}{2n}\right)$.
For $n = 2$:

```math
\text{NEB} = f_{-3\text{dB}} \cdot \frac{\pi\sqrt{2}}{4} \approx 1.11 \, f_{-3\text{dB}}.
```

This replaces the single-pole approximation $\text{NEB} = (\pi/2) f_{-3\text{dB}}$.

### References

- Graeme, J. (1996). *Photodiode Amplifiers: Op Amp Solutions*. McGraw-Hill.
- Hobbs, P. C. D. (2009). *Building Electro-Optical Systems: Making It All Work*. 2nd ed., Wiley.

## Requirements

Python >= 3.10. Install dependencies:

```bash
pip install -r requirements.txt
```
