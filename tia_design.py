"""TIA design calculator for balanced photodiode detection.

Application
-----------
Two identical photodiodes are connected to two identical TIA channels.
The small difference between their output voltages is extracted as the signal.
This imposes the following design constraints on the opamp selection:

- Low and stable I_b is essential: the inter-channel DC offset is R_f * dI_b,
  which directly contaminates the difference signal.  JFET-input opamps are required.
- Low temperature drift of I_b: bipolar opamps (e.g. LT1028, I_b ~ 25 nA) produce
  R_f * I_b ~ 500 uV per channel at R_f = 20 kOhm, and their I_b drift would
  dominate over the small difference signal.
- Noise performance is secondary to I_b stability.

Theory
------
ref: Graeme 1996, *Photodiode Amplifiers*

The TIA closed-loop transfer function with a single-pole opamp A(s) = wc/s is:

    Z_TI(s) = -R_f * wn^2 / (s^2 + 2*zeta*wn*s + wn^2)

where
    wn^2      = wc / (R_f * (C_i + C_f + C_s))           (natural frequency)
    2*zeta*wn = (1 + wc*R_f*C_f) / (R_f * (C_i + C_f + C_s))  (damping)

Butterworth condition (Q = 1/sqrt(2), no gain-peaking):
    (1 + wc*R_f*C_f)^2 = 2 * wc * R_f * (C_i + C_f + C_s)

Using C_c = 1/(wc*R_f), the optimal feedback capacitor is:
    C_f = sqrt(C_c * (2*C_i - C_c))

The -3 dB bandwidth equals the natural frequency:
    f_n = sqrt(f_c / (2*pi*R_f*(C_i + C_f + C_s)))   [Hz]

Noise equivalent bandwidth for a 2nd-order Butterworth:
    NEB = f_n * pi*sqrt(2)/4
"""

import numpy as np
import pandas
from dataclasses import dataclass, fields
from pathlib import Path

# ---------------------------------------------------------------------------
# Physical constants
# ---------------------------------------------------------------------------
KB = 1.38e-23   # Boltzmann constant  [J/K]
Q  = 1.6e-19    # electron charge     [C]

# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------

@dataclass
class Opamp:
    """Opamp parameters from datasheet."""
    name: str
    f_c: float       # gain-bandwidth product [Hz]
    I_b: float       # input bias current [A]
    f_f: float       # 1/f noise corner frequency [Hz]
    e_nif: float     # input voltage noise density (flat) [V/sqrt(Hz)]
    i_nif: float     # input current noise density (flat) [A/sqrt(Hz)]
    C_icm: float     # common-mode input capacitance [F]
    C_id: float      # differential input capacitance [F]
    input_type: str   # 'JFET', 'bipolar', 'CMOS'
    notes: str = ''


@dataclass
class Photodiode:
    """Photodiode parameters from datasheet."""
    name: str
    Cd_spec: float    # junction capacitance at Vb_spec [F]
    Vb_spec: float    # reverse bias for Cd_spec [V]
    phi_b: float      # built-in voltage [V]
    Id_spec: float    # dark current at Vb_spec [A]
    r_phi: float      # responsivity [A/W]
    wl: float         # wavelength [m]
    notes: str = ''

    def C_d(self, Vb: float) -> float:
        """Junction capacitance at reverse bias Vb [F]."""
        Cd0 = self.Cd_spec * (1 + self.Vb_spec / self.phi_b) ** 0.5
        return Cd0 / (1 + Vb / self.phi_b) ** 0.5

    def I_d(self, Vb: float) -> float:
        """Dark current at reverse bias Vb [A] (empirical sqrt model)."""
        return self.Id_spec * (Vb / self.Vb_spec) ** 0.5


@dataclass
class TIAResult:
    """Complete TIA design and noise analysis results."""
    # design
    opamp_name: str
    C_d: float         # photodiode capacitance [F]
    C_i: float         # total input capacitance [F]
    C_f: float         # optimal feedback capacitance [F]
    BW_t: float        # -3 dB bandwidth [Hz]
    NEB: float         # noise equivalent bandwidth [Hz]
    noise_gain_peak: float  # 1 + C_i/C_f

    # noise (output-referred RMS [V])
    E_noe: float       # opamp voltage noise
    E_noR: float       # R_f Johnson noise
    E_noi_bias: float  # bias current shot noise
    E_noi_dark: float  # dark current shot noise
    E_noi_nif: float   # opamp current noise
    E_no_bg: float     # total background noise
    E_noi_sig: float   # signal shot noise

    # figures of merit
    signal_V: float          # R_f * I_p [V]
    snr: float               # signal_V / sqrt(E_no_bg^2 + E_noi_sig^2)
    bg_to_shot_ratio: float  # E_no_bg / E_noi_sig
    offset_per_ch: float     # R_f * I_b [V]

    # Hobbs criteria (True = pass)
    hobbs: dict


# ---------------------------------------------------------------------------
# CSV loaders
# ---------------------------------------------------------------------------

def _csv_path(filename: str) -> Path:
    return Path(__file__).parent / 'data' / filename


def load_opamps(csv_path: str | Path | None = None) -> dict[str, Opamp]:
    """Load opamp database from CSV.  Returns {name: Opamp}."""
    path = Path(csv_path) if csv_path else _csv_path('opamps.csv')
    df = pandas.read_csv(path)
    # convert numeric columns from string scientific notation
    numeric_cols = ['f_c', 'I_b', 'f_f', 'e_nif', 'i_nif', 'C_icm', 'C_id']
    for col in numeric_cols:
        df[col] = df[col].apply(lambda x: float(x))
    result = {}
    for _, row in df.iterrows():
        result[row['name']] = Opamp(
            name=row['name'], f_c=row['f_c'], I_b=row['I_b'],
            f_f=row['f_f'], e_nif=row['e_nif'], i_nif=row['i_nif'],
            C_icm=row['C_icm'], C_id=row['C_id'],
            input_type=row['input_type'],
            notes=row.get('notes', ''),
        )
    return result


def load_photodiodes(csv_path: str | Path | None = None) -> dict[str, Photodiode]:
    """Load photodiode database from CSV.  Returns {name: Photodiode}."""
    path = Path(csv_path) if csv_path else _csv_path('photodiodes.csv')
    df = pandas.read_csv(path)
    numeric_cols = ['Cd_spec', 'Vb_spec', 'phi_b', 'Id_spec', 'r_phi', 'wl']
    for col in numeric_cols:
        df[col] = df[col].apply(lambda x: float(x))
    result = {}
    for _, row in df.iterrows():
        result[row['name']] = Photodiode(
            name=row['name'], Cd_spec=row['Cd_spec'], Vb_spec=row['Vb_spec'],
            phi_b=row['phi_b'], Id_spec=row['Id_spec'], r_phi=row['r_phi'],
            wl=row['wl'], notes=row.get('notes', ''),
        )
    return result


# ---------------------------------------------------------------------------
# Core design calculation
# ---------------------------------------------------------------------------

def design_tia(
    opamp: Opamp,
    pd: Photodiode,
    R_f: float,
    Vb: float,
    E_photo: float,
    T: float = 296.0,
    C_s: float = 0.0,
    C_d_override: float | None = None,
) -> TIAResult:
    """Run full Butterworth TIA design: C_f, bandwidth, and noise analysis.

    Parameters
    ----------
    opamp : Opamp
    pd : Photodiode
    R_f : feedback resistance [Ohm]
    Vb : reverse bias voltage [V]
    E_photo : incident optical power [W]
    T : temperature [K], default 296 (23 C)
    C_s : stray capacitance in parallel with C_f [F], default 0
    C_d_override : override photodiode capacitance [F], default None
    """
    # --- Photodiode ---
    C_d = C_d_override if C_d_override is not None else pd.C_d(Vb)
    I_d = pd.I_d(Vb)
    I_p = E_photo * pd.r_phi

    # --- Butterworth design ---
    C_i = C_d + opamp.C_icm + opamp.C_id
    C_c = 1.0 / (2.0 * np.pi * R_f * opamp.f_c)
    C_f = (C_c * (2.0 * C_i - C_c)) ** 0.5

    # -3 dB bandwidth (= natural frequency for Butterworth)
    #   f_n = sqrt( f_c / (2*pi * R_f * (C_i + C_f + C_s)) )
    C_tot = C_i + C_f + C_s
    BW_t = (opamp.f_c / (2.0 * np.pi * R_f * C_tot)) ** 0.5

    # Noise equivalent bandwidth for 2nd-order Butterworth
    NEB = (np.pi * np.sqrt(2) / 4.0) * BW_t

    noise_gain_peak = 1.0 + C_i / (C_f + C_s) if (C_f + C_s) > 0 else np.inf

    # --- Voltage noise (piecewise integration of e_ni * noise_gain) ---
    f_1 = 0.01  # low-frequency integration limit [Hz]
    e = opamp.e_nif
    f_f = opamp.f_f

    # E_noe1: 1/f noise region [f_1, f_f], noise gain = 1
    E_noe1 = e * (f_f * np.log(f_f / f_1)) ** 0.5

    # f_zf: noise-gain zero
    f_zf = 1.0 / (2.0 * np.pi * R_f * C_tot)

    # E_noe2: flat noise [f_f, f_zf], noise gain = 1
    E_noe2 = e * (f_zf - f_f) ** 0.5

    # f_pf: noise-gain pole
    f_pf = 1.0 / (2.0 * np.pi * R_f * (C_f + C_s)) if (C_f + C_s) > 0 else np.inf

    # E_noe3: rising noise gain [f_zf, f_pf], gain = f/f_zf
    E_noe3 = (e / f_zf) * ((f_pf**3 - f_zf**3) / 3.0) ** 0.5

    # f_i: unity loop-gain frequency
    f_i = opamp.f_c * (C_f + C_s) / C_tot if C_tot > 0 else opamp.f_c

    # E_noe4: plateau [f_pf, f_i], gain = 1 + C_i/(C_f+C_s)
    E_noe4 = noise_gain_peak * e * (f_i - f_pf) ** 0.5

    # E_noe5: above f_i, gain follows A(f) = f_c/f
    E_noe5 = e * opamp.f_c * (1.0 / f_i) ** 0.5

    E_noe = (E_noe1**2 + E_noe2**2 + E_noe3**2 + E_noe4**2 + E_noe5**2) ** 0.5

    # --- Current / thermal noise (flat spectra × NEB) ---
    E_noR      = (4.0 * KB * T * R_f * NEB) ** 0.5
    E_noi_bias = R_f * (2.0 * Q * NEB * opamp.I_b) ** 0.5
    E_noi_dark = R_f * (2.0 * Q * NEB * I_d) ** 0.5
    E_noi_nif  = R_f * opamp.i_nif * NEB ** 0.5

    E_no_bg = (E_noe**2 + E_noR**2 + E_noi_bias**2
               + E_noi_dark**2 + E_noi_nif**2) ** 0.5

    # --- Signal shot noise ---
    E_noi_sig = R_f * (2.0 * Q * NEB * I_p) ** 0.5

    # --- Figures of merit ---
    signal_V = R_f * I_p
    E_total = (E_no_bg**2 + E_noi_sig**2) ** 0.5
    snr = signal_V / E_total if E_total > 0 else np.inf
    bg_to_shot = E_no_bg / E_noi_sig if E_noi_sig > 0 else np.inf
    offset_per_ch = R_f * opamp.I_b

    # --- Hobbs opamp selection criteria ---
    i_Rf = (2.0 * KB * T / R_f) ** 0.5  # R_f thermal noise current density
    hobbs = {
        'i_nif < 0.5*sqrt(4kT/Rf)': opamp.i_nif < 0.5 * i_Rf,
        'e_nif < 0.5*Rf*sqrt(4kT/Rf)': opamp.e_nif < 0.5 * i_Rf * R_f,
        'e_nif < 0.5*sqrt(4kT/Rf)/(2pi*BW*Ci)': (
            opamp.e_nif < 0.5 * i_Rf / (2.0 * np.pi * BW_t * C_i)
        ),
        'f_c > 2*BW^2/f_pf': opamp.f_c > 2.0 * BW_t**2 / f_pf,
        'f_c < 10*BW^2/f_pf': opamp.f_c < 10.0 * BW_t**2 / f_pf,
    }

    return TIAResult(
        opamp_name=opamp.name,
        C_d=C_d, C_i=C_i, C_f=C_f, BW_t=BW_t, NEB=NEB,
        noise_gain_peak=noise_gain_peak,
        E_noe=E_noe, E_noR=E_noR,
        E_noi_bias=E_noi_bias, E_noi_dark=E_noi_dark, E_noi_nif=E_noi_nif,
        E_no_bg=E_no_bg, E_noi_sig=E_noi_sig,
        signal_V=signal_V, snr=snr, bg_to_shot_ratio=bg_to_shot,
        offset_per_ch=offset_per_ch, hobbs=hobbs,
    )


# ---------------------------------------------------------------------------
# Multi-opamp comparison
# ---------------------------------------------------------------------------

def compare_opamps(
    opamps: dict[str, Opamp],
    pd: Photodiode,
    R_f: float,
    Vb: float,
    E_photo: float,
    **kwargs,
) -> pandas.DataFrame:
    """Compare multiple opamps and return a summary DataFrame.

    Parameters are the same as design_tia().
    """
    rows = []
    for name, op in opamps.items():
        r = design_tia(op, pd, R_f, Vb, E_photo, **kwargs)
        rows.append({
            'opamp': name,
            'input': op.input_type,
            'e_nif [nV/rtHz]': op.e_nif * 1e9,
            'I_b [pA]': op.I_b * 1e12,
            'C_in [pF]': (op.C_icm + op.C_id) * 1e12,
            'C_f [pF]': r.C_f * 1e12,
            'BW [MHz]': r.BW_t * 1e-6,
            'E_noe [uV]': r.E_noe * 1e6,
            'E_noR [uV]': r.E_noR * 1e6,
            'E_no_bg [uV]': r.E_no_bg * 1e6,
            'E_noi_sig [uV]': r.E_noi_sig * 1e6,
            'bg/shot': r.bg_to_shot_ratio,
            'SNR': r.snr,
            'offset/ch [uV]': r.offset_per_ch * 1e6,
            'Hobbs pass': sum(r.hobbs.values()),
        })
    df = pandas.DataFrame(rows)
    df = df.sort_values('bg/shot', ascending=True).reset_index(drop=True)
    return df


# ---------------------------------------------------------------------------
# Display helpers
# ---------------------------------------------------------------------------

def print_result(r: TIAResult) -> None:
    """Print a formatted summary of a TIA design result."""
    print(f"=== TIA Design: {r.opamp_name} ===")
    print(f"  C_d  = {r.C_d/1e-12:.1f} pF,  C_i = {r.C_i/1e-12:.1f} pF")
    print(f"  C_f  = {r.C_f/1e-12:.2f} pF  (Butterworth optimum)")
    print(f"  BW   = {r.BW_t/1e6:.2f} MHz,  NEB = {r.NEB/1e6:.2f} MHz")
    print(f"  Noise gain peak = {r.noise_gain_peak:.1f}")
    print()
    print("  Noise breakdown (output-referred RMS):")
    print(f"    E_noe  (opamp voltage) = {r.E_noe*1e6:.1f} uV")
    print(f"    E_noR  (Rf thermal)    = {r.E_noR*1e6:.1f} uV")
    print(f"    E_noi_bias (Ib shot)   = {r.E_noi_bias*1e6:.3f} uV")
    print(f"    E_noi_dark (Id shot)   = {r.E_noi_dark*1e6:.3f} uV")
    print(f"    E_noi_nif  (in floor)  = {r.E_noi_nif*1e6:.3f} uV")
    print(f"    E_no_bg    (total BG)  = {r.E_no_bg*1e6:.1f} uV")
    print(f"    E_noi_sig  (sig shot)  = {r.E_noi_sig*1e6:.1f} uV")
    print()
    print("  Figures of merit:")
    print(f"    Signal         = {r.signal_V*1e3:.2f} mV")
    print(f"    SNR            = {r.snr:.0f}  ({20*np.log10(r.snr):.1f} dB)")
    print(f"    bg/shot ratio  = {r.bg_to_shot_ratio:.2f}"
          f"  {'(shot-noise limited)' if r.bg_to_shot_ratio < 1 else ''}")
    print(f"    Offset/ch      = {r.offset_per_ch*1e9:.1f} nV")
    print()
    print("  Hobbs criteria:")
    for criterion, passed in r.hobbs.items():
        print(f"    {'PASS' if passed else 'FAIL'}  {criterion}")
