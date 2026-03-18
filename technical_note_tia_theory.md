# Technical Note: Design Theory for the Butterworth-Optimized Photodiode Transimpedance Amplifier

**Author:** N. Moteki

**Last updated:** 2026-03-18 (corresponds to Photodiode-TIA v0.1.0)

This document provides a self-contained description of the mathematical theory implemented in the photodiode transimpedance amplifier (TIA) design tool. It covers the single-pole opamp model, the derivation of the closed-loop second-order transfer function, the exact Butterworth-optimum feedback capacitance without the common $\omega_{\mathrm{c}} R_{\mathrm{f}} C_{\mathrm{f}} \gg 1$ approximation, the $-3\,\mathrm{dB}$ bandwidth, the noise equivalent bandwidth for a second-order Butterworth response, the piecewise noise-gain integration for opamp voltage noise, and the shot/thermal noise analysis. All algebraic steps are shown explicitly.

## Contents

1. [Circuit model and assumptions](#1-circuit-model-and-assumptions)
2. [Closed-loop transimpedance transfer function](#2-closed-loop-transimpedance-transfer-function)
3. [Butterworth-optimum feedback capacitance](#3-butterworth-optimum-feedback-capacitance)
4. [Bandwidth](#4-bandwidth)
5. [Noise equivalent bandwidth](#5-noise-equivalent-bandwidth)
6. [Noise analysis](#6-noise-analysis)
7. [Implementation mapping](#7-implementation-mapping)
8. [References](#8-references)

---

## 1. Circuit model and assumptions

### Circuit topology

The TIA is an inverting opamp configuration with a photodiode at the input. The non-inverting input is connected to ground.

- $I_{\mathrm{pd}}$: photocurrent from the photodiode (signal source, modelled as ideal current source)
- $R_{\mathrm{f}}$, $C_{\mathrm{f}}$: feedback resistance and capacitance (in parallel), connected from the output to the inverting input
- $C_{\mathrm{i}}$: total input capacitance at the inverting node, $C_{\mathrm{i}} = C_{\mathrm{d}} + C_{\mathrm{icm}} + C_{\mathrm{id}}$
  - $C_{\mathrm{d}}$: photodiode junction capacitance
  - $C_{\mathrm{icm}}$: opamp common-mode input capacitance
  - $C_{\mathrm{id}}$: opamp differential input capacitance
- $C_{\mathrm{s}}$: stray (parasitic) capacitance at the inverting node to ground

### Opamp model

The opamp is modelled with a single-pole open-loop gain:

$$
A(s) = \frac{A_0 \,\omega_{\mathrm{p}}}{s + \omega_{\mathrm{p}}} \qquad \textrm{(1.1)}
$$

where $A_0$ is the DC open-loop gain and $\omega_{\mathrm{p}}$ is the dominant pole frequency. For frequencies well above the dominant pole ($s \gg \omega_{\mathrm{p}}$, i.e. $f \gg f_{\mathrm{p}}$, typically satisfied for $f > 10$ Hz), this simplifies to:

$$
A(s) \approx \frac{A_0 \,\omega_{\mathrm{p}}}{s} = \frac{\omega_{\mathrm{c}}}{s} \qquad \textrm{(1.2)}
$$

where $\omega_{\mathrm{c}} = A_0 \,\omega_{\mathrm{p}} = 2\pi f_{\mathrm{c}}$ is the gain-bandwidth product (GBW) in rad/s. This "integrator model" is the standard approximation used throughout TIA design literature and is accurate across the entire frequency range of interest (kHz to MHz).

---

## 2. Closed-loop transimpedance transfer function

### Goal

Derive the closed-loop transimpedance:

$$
Z_{\mathrm{TI}}(s) \equiv \frac{V_{\mathrm{out}}(s)}{I_{\mathrm{pd}}(s)}.
$$

### Step 1: Define the feedback impedance

$R_{\mathrm{f}}$ and $C_{\mathrm{f}}$ are in parallel:

$$
Z_{\mathrm{f}} = R_{\mathrm{f}} \;\|\; \frac{1}{sC_{\mathrm{f}}} = \frac{R_{\mathrm{f}}}{1 + sR_{\mathrm{f}}C_{\mathrm{f}}} \qquad \textrm{(2.1)}
$$

### Step 2: Opamp constraint

With the non-inverting input grounded:

$$
V_{\mathrm{out}} = -A(s) \cdot V^{-} = -\frac{\omega_{\mathrm{c}}}{s} \, V^{-}
$$

Solving for $V^-$:

$$
V^{-} = -\frac{s}{\omega_{\mathrm{c}}}\,V_{\mathrm{out}} \qquad \textrm{(2.2)}
$$

### Step 3: Kirchhoff's current law at the inverting node

All currents leaving the inverting node must sum to zero. The current into the node from the photodiode is $I_{\mathrm{pd}}$. The currents leaving the node are:

- Through the feedback network to the output: $(V^{-} - V_{\mathrm{out}}) / Z_{\mathrm{f}}$
- Through the total shunt capacitance $(C_{\mathrm{i}} + C_{\mathrm{s}})$ to ground: $V^{-} \cdot s(C_{\mathrm{i}} + C_{\mathrm{s}})$

KCL:

$$
I_{\mathrm{pd}} + \frac{V^{-} - V_{\mathrm{out}}}{Z_{\mathrm{f}}} + V^{-} \cdot s(C_{\mathrm{i}} + C_{\mathrm{s}}) = 0
$$

Note the sign convention: current flowing from the node through $Z_{\mathrm{f}}$ toward $V_{\mathrm{out}}$ is $(V^{-} - V_{\mathrm{out}})/Z_{\mathrm{f}}$. Rearranging with current into the node on the left:

$$
I_{\mathrm{pd}} = \frac{V_{\mathrm{out}} - V^{-}}{Z_{\mathrm{f}}} - V^{-} \cdot s(C_{\mathrm{i}} + C_{\mathrm{s}}) \qquad \textrm{(2.3)}
$$

### Step 4: Substitute the opamp constraint

Substitute (2.1) and (2.2) into (2.3).

First, compute $V_{\mathrm{out}} - V^-$:

$$
V_{\mathrm{out}} - V^{-} = V_{\mathrm{out}} - \left(-\frac{s}{\omega_{\mathrm{c}}}V_{\mathrm{out}}\right) = V_{\mathrm{out}}\left(1 + \frac{s}{\omega_{\mathrm{c}}}\right) = V_{\mathrm{out}} \cdot \frac{\omega_{\mathrm{c}} + s}{\omega_{\mathrm{c}}} \qquad \textrm{(2.4)}
$$

Substitute into the feedback current term:

$$
\frac{V_{\mathrm{out}} - V^{-}}{Z_{\mathrm{f}}} = V_{\mathrm{out}} \cdot \frac{\omega_{\mathrm{c}} + s}{\omega_{\mathrm{c}}} \cdot \frac{1 + sR_{\mathrm{f}}C_{\mathrm{f}}}{R_{\mathrm{f}}} \qquad \textrm{(2.5)}
$$

The shunt capacitance current term:

$$
-V^{-} \cdot s(C_{\mathrm{i}} + C_{\mathrm{s}}) = \frac{s}{\omega_{\mathrm{c}}}V_{\mathrm{out}} \cdot s(C_{\mathrm{i}} + C_{\mathrm{s}}) = \frac{s^2 (C_{\mathrm{i}} + C_{\mathrm{s}})}{\omega_{\mathrm{c}}}\,V_{\mathrm{out}} \qquad \textrm{(2.6)}
$$

### Step 5: Combine

Substituting (2.5) and (2.6) into (2.3):

$$
I_{\mathrm{pd}} = V_{\mathrm{out}} \left[\frac{(\omega_{\mathrm{c}} + s)(1 + sR_{\mathrm{f}}C_{\mathrm{f}})}{\omega_{\mathrm{c}} R_{\mathrm{f}}} + \frac{s^2(C_{\mathrm{i}} + C_{\mathrm{s}})}{\omega_{\mathrm{c}}}\right]
$$

Factor out $1/\omega_{\mathrm{c}}$:

$$
I_{\mathrm{pd}} = \frac{V_{\mathrm{out}}}{\omega_{\mathrm{c}}}\left[\frac{(\omega_{\mathrm{c}} + s)(1 + sR_{\mathrm{f}}C_{\mathrm{f}})}{R_{\mathrm{f}}} + s^2(C_{\mathrm{i}} + C_{\mathrm{s}})\right] \qquad \textrm{(2.7)}
$$

### Step 6: Expand the product

$$
(\omega_{\mathrm{c}} + s)(1 + sR_{\mathrm{f}}C_{\mathrm{f}}) = \omega_{\mathrm{c}} + \omega_{\mathrm{c}} s R_{\mathrm{f}} C_{\mathrm{f}} + s + s^2 R_{\mathrm{f}} C_{\mathrm{f}}
$$

Rearranging in powers of $s$:

$$
= s^2 R_{\mathrm{f}} C_{\mathrm{f}} + s(1 + \omega_{\mathrm{c}} R_{\mathrm{f}} C_{\mathrm{f}}) + \omega_{\mathrm{c}} \qquad \textrm{(2.8)}
$$

### Step 7: Divide by $R_{\mathrm{f}}$ and add the shunt term

$$
\frac{(\omega_{\mathrm{c}} + s)(1 + sR_{\mathrm{f}}C_{\mathrm{f}})}{R_{\mathrm{f}}} + s^2(C_{\mathrm{i}} + C_{\mathrm{s}})
$$

$$
= s^2 C_{\mathrm{f}} + \frac{s(1 + \omega_{\mathrm{c}} R_{\mathrm{f}} C_{\mathrm{f}})}{R_{\mathrm{f}}} + \frac{\omega_{\mathrm{c}}}{R_{\mathrm{f}}} + s^2(C_{\mathrm{i}} + C_{\mathrm{s}})
$$

$$
= s^2(C_{\mathrm{i}} + C_{\mathrm{f}} + C_{\mathrm{s}}) + s\,\frac{1 + \omega_{\mathrm{c}} R_{\mathrm{f}} C_{\mathrm{f}}}{R_{\mathrm{f}}} + \frac{\omega_{\mathrm{c}}}{R_{\mathrm{f}}} \qquad \textrm{(2.9)}
$$

### Step 8: Form the transfer function

From (2.7) and (2.9):

$$
I_{\mathrm{pd}} = \frac{V_{\mathrm{out}}}{\omega_{\mathrm{c}}}\left[s^2(C_{\mathrm{i}} + C_{\mathrm{f}} + C_{\mathrm{s}}) + s\,\frac{1 + \omega_{\mathrm{c}} R_{\mathrm{f}} C_{\mathrm{f}}}{R_{\mathrm{f}}} + \frac{\omega_{\mathrm{c}}}{R_{\mathrm{f}}}\right]
$$

$$
Z_{\mathrm{TI}}(s) = \frac{V_{\mathrm{out}}}{I_{\mathrm{pd}}} = \frac{\omega_{\mathrm{c}}}{s^2(C_{\mathrm{i}} + C_{\mathrm{f}} + C_{\mathrm{s}}) + s\,\frac{1 + \omega_{\mathrm{c}} R_{\mathrm{f}} C_{\mathrm{f}}}{R_{\mathrm{f}}} + \frac{\omega_{\mathrm{c}}}{R_{\mathrm{f}}}} \qquad \textrm{(2.10)}
$$

(The overall sign is negative for the inverting configuration; we write the magnitude here and note the 180 degree phase inversion separately.)

### Step 9: Identify the standard second-order form

A standard second-order low-pass transfer function has the form:

$$
H(s) = \frac{K\,\omega_{\mathrm{n}}^2}{s^2 + 2\zeta\omega_{\mathrm{n}}\,s + \omega_{\mathrm{n}}^2}
$$

Dividing numerator and denominator of (2.10) by $(C_{\mathrm{i}} + C_{\mathrm{f}} + C_{\mathrm{s}})$:

$$
Z_{\mathrm{TI}}(s) = \frac{\frac{\omega_{\mathrm{c}}}{C_{\mathrm{i}} + C_{\mathrm{f}} + C_{\mathrm{s}}}}{s^2 + \frac{1 + \omega_{\mathrm{c}} R_{\mathrm{f}} C_{\mathrm{f}}}{R_{\mathrm{f}}(C_{\mathrm{i}} + C_{\mathrm{f}} + C_{\mathrm{s}})}\,s + \frac{\omega_{\mathrm{c}}}{R_{\mathrm{f}}(C_{\mathrm{i}} + C_{\mathrm{f}} + C_{\mathrm{s}})}} \qquad \textrm{(2.11)}
$$

By comparison with the standard form, we identify:

$$
\omega_{\mathrm{n}}^2 = \frac{\omega_{\mathrm{c}}}{R_{\mathrm{f}}(C_{\mathrm{i}} + C_{\mathrm{f}} + C_{\mathrm{s}})} \qquad \textrm{(2.12)}
$$

$$
2\zeta\omega_{\mathrm{n}} = \frac{1 + \omega_{\mathrm{c}} R_{\mathrm{f}} C_{\mathrm{f}}}{R_{\mathrm{f}}(C_{\mathrm{i}} + C_{\mathrm{f}} + C_{\mathrm{s}})} \qquad \textrm{(2.13)}
$$

The DC gain ($s = 0$) of (2.11):

$$
Z_{\mathrm{TI}}(0) = \frac{\omega_{\mathrm{c}} / (C_{\mathrm{i}} + C_{\mathrm{f}} + C_{\mathrm{s}})}{\omega_{\mathrm{n}}^2} = \frac{\omega_{\mathrm{c}} / (C_{\mathrm{i}} + C_{\mathrm{f}} + C_{\mathrm{s}})}{\omega_{\mathrm{c}} / [R_{\mathrm{f}}(C_{\mathrm{i}} + C_{\mathrm{f}} + C_{\mathrm{s}})]} = R_{\mathrm{f}}.
$$

The numerator constant can therefore be written as $R_{\mathrm{f}}\,\omega_{\mathrm{n}}^2$, giving the final form (restoring the sign for the inverting configuration):

$$
Z_{\mathrm{TI}}(s) = \frac{-R_{\mathrm{f}}\,\omega_{\mathrm{n}}^2}{s^2 + 2\zeta\omega_{\mathrm{n}}\,s + \omega_{\mathrm{n}}^2} \qquad \textrm{(2.14)}
$$

---

## 3. Butterworth-optimum feedback capacitance

### Objective

Find the value of $C_{\mathrm{f}}$ that makes the closed-loop response maximally flat (Butterworth).

### Step 1: Butterworth condition

A second-order Butterworth (maximally flat magnitude) filter has quality factor:

$$
Q = \frac{1}{\sqrt{2}}
$$

The relationship between $Q$ and the damping ratio $\zeta$ is $Q = 1/(2\zeta)$, so:

$$
\zeta = \frac{1}{\sqrt{2}} \qquad \textrm{(3.1)}
$$

This is the unique damping ratio that produces zero gain peaking in the magnitude response (i.e. $|Z_{\mathrm{TI}}(j\omega)|$ is monotonically decreasing).

### Step 2: Translate the condition to circuit parameters

The Butterworth condition (3.1) implies:

$$
(2\zeta\omega_{\mathrm{n}})^2 = 4\zeta^2\omega_{\mathrm{n}}^2 = 4 \cdot \frac{1}{2} \cdot \omega_{\mathrm{n}}^2 = 2\,\omega_{\mathrm{n}}^2.
$$

Substituting (2.12) and (2.13):

$$
\left(\frac{1 + \omega_{\mathrm{c}} R_{\mathrm{f}} C_{\mathrm{f}}}{R_{\mathrm{f}}(C_{\mathrm{i}} + C_{\mathrm{f}} + C_{\mathrm{s}})}\right)^2 = 2 \cdot \frac{\omega_{\mathrm{c}}}{R_{\mathrm{f}}(C_{\mathrm{i}} + C_{\mathrm{f}} + C_{\mathrm{s}})}
$$

Multiply both sides by $[R_{\mathrm{f}}(C_{\mathrm{i}} + C_{\mathrm{f}} + C_{\mathrm{s}})]^2$:

$$
(1 + \omega_{\mathrm{c}} R_{\mathrm{f}} C_{\mathrm{f}})^2 = 2\,\omega_{\mathrm{c}} R_{\mathrm{f}}(C_{\mathrm{i}} + C_{\mathrm{f}} + C_{\mathrm{s}}) \qquad \textrm{(3.2)}
$$

### Step 3: Solve for $C_{\mathrm{f}}$

Define a characteristic capacitance:

$$
C_{\mathrm{c}} \equiv \frac{1}{\omega_{\mathrm{c}} R_{\mathrm{f}}} = \frac{1}{2\pi f_{\mathrm{c}} R_{\mathrm{f}}} \qquad \textrm{(3.3)}
$$

This has a physical interpretation: $C_{\mathrm{c}}$ is the capacitance whose impedance at $f_{\mathrm{c}}$ equals $R_{\mathrm{f}}$.

Rewrite (3.2) using $\omega_{\mathrm{c}} R_{\mathrm{f}} = 1/C_{\mathrm{c}}$:

$$
\left(1 + \frac{C_{\mathrm{f}}}{C_{\mathrm{c}}}\right)^2 = \frac{2(C_{\mathrm{i}} + C_{\mathrm{f}} + C_{\mathrm{s}})}{C_{\mathrm{c}}}
$$

Expand the left side:

$$
1 + \frac{2C_{\mathrm{f}}}{C_{\mathrm{c}}} + \frac{C_{\mathrm{f}}^2}{C_{\mathrm{c}}^2} = \frac{2(C_{\mathrm{i}} + C_{\mathrm{s}})}{C_{\mathrm{c}}} + \frac{2C_{\mathrm{f}}}{C_{\mathrm{c}}}
$$

The $2C_{\mathrm{f}}/C_{\mathrm{c}}$ terms cancel:

$$
1 + \frac{C_{\mathrm{f}}^2}{C_{\mathrm{c}}^2} = \frac{2(C_{\mathrm{i}} + C_{\mathrm{s}})}{C_{\mathrm{c}}}
$$

Multiply through by $C_{\mathrm{c}}^2$:

$$
C_{\mathrm{c}}^2 + C_{\mathrm{f}}^2 = 2(C_{\mathrm{i}} + C_{\mathrm{s}}) C_{\mathrm{c}}
$$

$$
C_{\mathrm{f}}^2 = 2(C_{\mathrm{i}} + C_{\mathrm{s}}) C_{\mathrm{c}} - C_{\mathrm{c}}^2 = C_{\mathrm{c}}\bigl(2(C_{\mathrm{i}} + C_{\mathrm{s}}) - C_{\mathrm{c}}\bigr) \qquad \textrm{(3.4)}
$$

Taking the positive root:

$$
C_{\mathrm{f}} = \sqrt{C_{\mathrm{c}}\bigl(2(C_{\mathrm{i}} + C_{\mathrm{s}}) - C_{\mathrm{c}}\bigr)}, \qquad C_{\mathrm{c}} = \frac{1}{2\pi f_{\mathrm{c}} R_{\mathrm{f}}} \qquad \textrm{(3.5)}
$$

### Validity condition

Equation (3.5) requires the argument of the square root to be non-negative:

$$
2(C_{\mathrm{i}} + C_{\mathrm{s}}) - C_{\mathrm{c}} > 0 \quad\Longleftrightarrow\quad C_{\mathrm{i}} + C_{\mathrm{s}} > \frac{C_{\mathrm{c}}}{2} = \frac{1}{2\omega_{\mathrm{c}} R_{\mathrm{f}}}.
$$

When this condition is violated, the opamp GBW is too low (or $R_{\mathrm{f}}$ too small) to achieve a Butterworth response --- the circuit is fundamentally underdamped regardless of $C_{\mathrm{f}}$.

### Relation to the common approximation

Many references simplify by assuming $\omega_{\mathrm{c}} R_{\mathrm{f}} C_{\mathrm{f}} \gg 1$ (equivalently $C_{\mathrm{f}} \gg C_{\mathrm{c}}$). Under this approximation, (3.2) becomes:

$$
(\omega_{\mathrm{c}} R_{\mathrm{f}} C_{\mathrm{f}})^2 \approx 2\,\omega_{\mathrm{c}} R_{\mathrm{f}}\,(C_{\mathrm{i}} + C_{\mathrm{s}}) \quad\Longrightarrow\quad C_{\mathrm{f}} \approx \sqrt{\frac{2(C_{\mathrm{i}} + C_{\mathrm{s}})}{\omega_{\mathrm{c}} R_{\mathrm{f}}}} = \sqrt{2(C_{\mathrm{i}} + C_{\mathrm{s}}) C_{\mathrm{c}}}.
$$

Equation (3.5) is the **exact** solution that does not rely on this approximation. The difference is significant when $C_{\mathrm{c}}$ is not negligible compared to $C_{\mathrm{i}} + C_{\mathrm{s}}$ (i.e. when $R_{\mathrm{f}}$ is small or $f_{\mathrm{c}}$ is low).

---

## 4. Bandwidth

### The $-3\,\mathrm{dB}$ bandwidth of a second-order Butterworth

For a general second-order transfer function with damping ratio $\zeta$, the squared magnitude response is:

$$
|H(j\omega)|^2 = \frac{\omega_{\mathrm{n}}^4}{(\omega_{\mathrm{n}}^2 - \omega^2)^2 + (2\zeta\omega_{\mathrm{n}}\omega)^2}
$$

For the Butterworth case $\zeta = 1/\sqrt{2}$, substituting and simplifying:

$$
|H(j\omega)|^2 = \frac{\omega_{\mathrm{n}}^4}{(\omega_{\mathrm{n}}^2 - \omega^2)^2 + 2\omega_{\mathrm{n}}^2\omega^2}
$$

Expand the denominator:

$$
= \omega_{\mathrm{n}}^4 - 2\omega_{\mathrm{n}}^2\omega^2 + \omega^4 + 2\omega_{\mathrm{n}}^2\omega^2 = \omega_{\mathrm{n}}^4 + \omega^4
$$

Therefore:

$$
|H(j\omega)|^2 = \frac{\omega_{\mathrm{n}}^4}{\omega_{\mathrm{n}}^4 + \omega^4} = \frac{1}{1 + (\omega/\omega_{\mathrm{n}})^4} \qquad \textrm{(4.1)}
$$

This is the defining form of a second-order Butterworth response.

At $\omega = \omega_{\mathrm{n}}$:

$$
|H(j\omega_{\mathrm{n}})|^2 = \frac{1}{1 + 1} = \frac{1}{2} \quad\Longrightarrow\quad |H(j\omega_{\mathrm{n}})| = \frac{1}{\sqrt{2}} \;(-3\,\mathrm{dB}).
$$

Therefore the $-3\,\mathrm{dB}$ bandwidth is exactly the natural frequency:

$$
\omega_{-3\,\mathrm{dB}} = \omega_{\mathrm{n}}.
$$

In terms of ordinary frequency:

$$
f_{-3\,\mathrm{dB}} = \frac{\omega_{\mathrm{n}}}{2\pi} \qquad \textrm{(4.2)}
$$

### Express in terms of circuit parameters

From (2.12):

$$
\omega_{\mathrm{n}} = \sqrt{\frac{\omega_{\mathrm{c}}}{R_{\mathrm{f}}(C_{\mathrm{i}} + C_{\mathrm{f}} + C_{\mathrm{s}})}} = \sqrt{\frac{2\pi f_{\mathrm{c}}}{R_{\mathrm{f}}(C_{\mathrm{i}} + C_{\mathrm{f}} + C_{\mathrm{s}})}}
$$

Therefore:

$$
f_{-3\,\mathrm{dB}} = \frac{\omega_{\mathrm{n}}}{2\pi} = \frac{1}{2\pi}\sqrt{\frac{2\pi f_{\mathrm{c}}}{R_{\mathrm{f}}(C_{\mathrm{i}} + C_{\mathrm{f}} + C_{\mathrm{s}})}} = \sqrt{\frac{f_{\mathrm{c}}}{2\pi R_{\mathrm{f}}(C_{\mathrm{i}} + C_{\mathrm{f}} + C_{\mathrm{s}})}} \qquad \textrm{(4.3)}
$$

---

## 5. Noise equivalent bandwidth

### Definition

The noise equivalent bandwidth (NEB) of a filter $H(f)$ is the bandwidth of an ideal rectangular (brick-wall) filter with the same peak gain that passes the same total noise power:

$$
\mathrm{NEB} = \frac{1}{|H_{\mathrm{max}}|^2}\int_0^{\infty} |H(f)|^2 \, df
$$

For a Butterworth filter, $|H_{\mathrm{max}}| = |H(0)| = 1$, so:

$$
\mathrm{NEB} = \int_0^{\infty} |H(f)|^2 \, df \qquad \textrm{(5.1)}
$$

### General $n$-th order Butterworth NEB

For an $n$-th order Butterworth filter, the squared magnitude response is:

$$
|H(f)|^2 = \frac{1}{1 + (f/f_{-3\,\mathrm{dB}})^{2n}}
$$

Substituting into (5.1) with $u = f/f_{-3\,\mathrm{dB}}$:

$$
\mathrm{NEB} = f_{-3\,\mathrm{dB}} \int_0^{\infty} \frac{du}{1 + u^{2n}} \qquad \textrm{(5.2)}
$$

The integral $\displaystyle I_n = \int_0^{\infty} \frac{du}{1 + u^{2n}}$ is a standard result that can be evaluated using the substitution $t = u^{2n}$ and recognizing the beta function.

Setting $t = u^{2n}$, so $u = t^{1/(2n)}$, $du = \frac{1}{2n}\,t^{1/(2n)-1}\,dt$:

$$
I_n = \int_0^{\infty} \frac{1}{1+t} \cdot \frac{1}{2n}\,t^{1/(2n)-1}\,dt = \frac{1}{2n}\,B\!\left(\frac{1}{2n},\; 1 - \frac{1}{2n}\right)
$$

where $B(a, b) = \Gamma(a)\Gamma(b)/\Gamma(a+b)$ is the beta function.

Using the reflection formula $\Gamma(z)\,\Gamma(1-z) = \pi/\sin(\pi z)$ with $z = 1/(2n)$:

$$
I_n = \frac{1}{2n} \cdot \frac{\pi}{\sin\!\left(\frac{\pi}{2n}\right)} \qquad \textrm{(5.3)}
$$

Therefore:

$$
\mathrm{NEB} = f_{-3\,\mathrm{dB}} \cdot \frac{\pi}{2n\,\sin\!\left(\frac{\pi}{2n}\right)} \qquad \textrm{(5.4)}
$$

### Specialization to $n = 2$

For the second-order Butterworth ($n = 2$):

$$
\mathrm{NEB} = f_{-3\,\mathrm{dB}} \cdot \frac{\pi}{2 \cdot 2 \cdot \sin\!\left(\frac{\pi}{4}\right)} = f_{-3\,\mathrm{dB}} \cdot \frac{\pi}{4 \cdot \frac{\sqrt{2}}{2}} = f_{-3\,\mathrm{dB}} \cdot \frac{\pi}{2\sqrt{2}}
$$

Rationalizing:

$$
= f_{-3\,\mathrm{dB}} \cdot \frac{\pi}{2\sqrt{2}} \cdot \frac{\sqrt{2}}{\sqrt{2}} = f_{-3\,\mathrm{dB}} \cdot \frac{\pi\sqrt{2}}{4}
$$

$$
\mathrm{NEB} = f_{-3\,\mathrm{dB}} \cdot \frac{\pi\sqrt{2}}{4} \approx 1.111\,f_{-3\,\mathrm{dB}} \qquad \textrm{(5.5)}
$$

### Comparison with the single-pole approximation

For a single-pole (first-order) system ($n = 1$):

$$
\mathrm{NEB}_{n=1} = f_{-3\,\mathrm{dB}} \cdot \frac{\pi}{2\sin(\pi/2)} = f_{-3\,\mathrm{dB}} \cdot \frac{\pi}{2} \approx 1.571\,f_{-3\,\mathrm{dB}}.
$$

Many TIA references use this single-pole approximation even when the circuit has a second-order response. The second-order Butterworth NEB is $1.111/1.571 = 0.707$ times the single-pole value --- a 29% difference that directly affects computed noise levels.

---

## 6. Noise analysis

The TIA output noise is the root-sum-square (RSS) of several independent noise sources. Each source has a spectral density that is shaped by the closed-loop gain before appearing at the output. The noise sources fall into two categories: (a) voltage noise of the opamp, which is amplified by the frequency-dependent noise gain, and (b) current/thermal noise sources whose spectra are flat and are shaped only by the closed-loop transimpedance $|Z_{\mathrm{TI}}(f)|^2$.

### 6.1 Noise gain

The noise gain $G_{\mathrm{n}}(f)$ is the closed-loop gain from the opamp's input voltage noise source $e_{\mathrm{ni}}$ to the output. For a TIA with feedback impedance $Z_{\mathrm{f}} = R_{\mathrm{f}} \| (1/sC_{\mathrm{f}})$ and total input-to-ground capacitance $(C_{\mathrm{i}} + C_{\mathrm{s}})$, the noise gain is:

$$
G_{\mathrm{n}}(f) = 1 + \frac{Z_{\mathrm{in}}}{Z_{\mathrm{f}}} = 1 + \frac{C_{\mathrm{i}} + C_{\mathrm{s}}}{C_{\mathrm{f}} + C_{\mathrm{s}}} \cdot \frac{1 + s R_{\mathrm{f}} (C_{\mathrm{f}} + C_{\mathrm{s}})}{1 + s R_{\mathrm{f}} (C_{\mathrm{i}} + C_{\mathrm{f}} + C_{\mathrm{s}})}
$$

This gain exhibits four distinct frequency regions that are exploited for piecewise integration:

1. **Low-frequency flat region** ($f < f_{\mathrm{zf}}$): $G_{\mathrm{n}} \approx 1$
2. **Rising region** ($f_{\mathrm{zf}} < f < f_{\mathrm{pf}}$): $G_{\mathrm{n}} \approx f / f_{\mathrm{zf}}$
3. **Plateau region** ($f_{\mathrm{pf}} < f < f_{\mathrm{i}}$): $G_{\mathrm{n}} \approx 1 + C_{\mathrm{i}} / (C_{\mathrm{f}} + C_{\mathrm{s}})$
4. **Roll-off region** ($f > f_{\mathrm{i}}$): $G_{\mathrm{n}}$ decreases as the loop gain falls below unity

where the characteristic frequencies are:

$$
f_{\mathrm{zf}} = \frac{1}{2\pi R_{\mathrm{f}} (C_{\mathrm{i}} + C_{\mathrm{f}} + C_{\mathrm{s}})} \qquad \textrm{(6.1)}
$$

$$
f_{\mathrm{pf}} = \frac{1}{2\pi R_{\mathrm{f}} (C_{\mathrm{f}} + C_{\mathrm{s}})} \qquad \textrm{(6.2)}
$$

$$
f_{\mathrm{i}} = f_{\mathrm{c}} \cdot \frac{C_{\mathrm{f}} + C_{\mathrm{s}}}{C_{\mathrm{i}} + C_{\mathrm{f}} + C_{\mathrm{s}}} \qquad \textrm{(6.3)}
$$

Here $f_{\mathrm{zf}}$ is the noise-gain zero frequency, $f_{\mathrm{pf}}$ is the noise-gain pole frequency, and $f_{\mathrm{i}}$ is the unity loop-gain (intersection) frequency.

### 6.2 Opamp voltage noise (piecewise integration)

The opamp input voltage noise spectral density has a $1/f$ component below the corner frequency $f_{\mathrm{f}}$ and a white (flat) floor $e_{\mathrm{nif}}$ above it:

$$
e_{\mathrm{ni}}(f) = e_{\mathrm{nif}} \sqrt{1 + f_{\mathrm{f}} / f} \qquad \textrm{(6.4)}
$$

The output-referred voltage noise RMS is obtained by integrating the product of $e_{\mathrm{ni}}^2(f)$ and $G_{\mathrm{n}}^2(f)$ over frequency, divided into five segments. Defining a low-frequency cutoff $f_1$ (set to 0.01 Hz in the implementation):

**Region 1** --- $1/f$ noise ($f_1$ to $f_{\mathrm{f}}$), noise gain $\approx 1$:

$$
E_{\mathrm{noe},1}^2 = e_{\mathrm{nif}}^2 \cdot f_{\mathrm{f}} \ln\!\left(\frac{f_{\mathrm{f}}}{f_1}\right) \qquad \textrm{(6.5)}
$$

**Region 2** --- white noise, flat gain ($f_{\mathrm{f}}$ to $f_{\mathrm{zf}}$), noise gain $\approx 1$:

$$
E_{\mathrm{noe},2}^2 = e_{\mathrm{nif}}^2 (f_{\mathrm{zf}} - f_{\mathrm{f}}) \qquad \textrm{(6.6)}
$$

**Region 3** --- white noise, rising gain ($f_{\mathrm{zf}}$ to $f_{\mathrm{pf}}$), noise gain $\approx f/f_{\mathrm{zf}}$:

$$
E_{\mathrm{noe},3}^2 = \frac{e_{\mathrm{nif}}^2}{f_{\mathrm{zf}}^2} \cdot \frac{f_{\mathrm{pf}}^3 - f_{\mathrm{zf}}^3}{3} \qquad \textrm{(6.7)}
$$

**Region 4** --- white noise, plateau ($f_{\mathrm{pf}}$ to $f_{\mathrm{i}}$), noise gain $\approx 1 + C_{\mathrm{i}}/(C_{\mathrm{f}} + C_{\mathrm{s}})$:

$$
E_{\mathrm{noe},4}^2 = e_{\mathrm{nif}}^2 \left(1 + \frac{C_{\mathrm{i}}}{C_{\mathrm{f}} + C_{\mathrm{s}}}\right)^2 (f_{\mathrm{i}} - f_{\mathrm{pf}}) \qquad \textrm{(6.8)}
$$

**Region 5** --- above unity loop gain ($f > f_{\mathrm{i}}$), gain $\approx f_{\mathrm{c}} / f$:

$$
E_{\mathrm{noe},5}^2 = e_{\mathrm{nif}}^2 \cdot \frac{f_{\mathrm{c}}^2}{f_{\mathrm{i}}} \qquad \textrm{(6.9)}
$$

Note: Eq. (6.9) arises from $\int_{f_{\mathrm{i}}}^{\infty} (f_{\mathrm{c}}/f)^2 \, df = f_{\mathrm{c}}^2 / f_{\mathrm{i}}$.

The total output-referred opamp voltage noise is:

$$
E_{\mathrm{noe}} = \sqrt{E_{\mathrm{noe},1}^2 + E_{\mathrm{noe},2}^2 + E_{\mathrm{noe},3}^2 + E_{\mathrm{noe},4}^2 + E_{\mathrm{noe},5}^2} \qquad \textrm{(6.10)}
$$

### 6.3 Feedback resistor thermal noise

The Johnson noise of $R_{\mathrm{f}}$ produces a current noise density $\sqrt{4k_{\mathrm{B}}T/R_{\mathrm{f}}}$, which flows through $R_{\mathrm{f}}$ to produce output voltage noise. Since this noise source sees the same transimpedance transfer function as the signal, the NEB (Eq. 5.5) is the appropriate bandwidth:

$$
E_{\mathrm{noR}} = \sqrt{4 k_{\mathrm{B}} T R_{\mathrm{f}} \cdot \mathrm{NEB}} \qquad \textrm{(6.11)}
$$

### 6.4 Shot noise

Shot noise from DC currents (bias current $I_{\mathrm{b}}$, dark current $I_{\mathrm{d}}$, and signal photocurrent $I_{\mathrm{p}}$) produces white current noise with spectral density $\sqrt{2qI}$. Each is converted to output voltage noise by the transimpedance $R_{\mathrm{f}}$ over the NEB:

$$
E_{\mathrm{noi,bias}} = R_{\mathrm{f}} \sqrt{2q \, I_{\mathrm{b}} \cdot \mathrm{NEB}} \qquad \textrm{(6.12)}
$$

$$
E_{\mathrm{noi,dark}} = R_{\mathrm{f}} \sqrt{2q \, I_{\mathrm{d}} \cdot \mathrm{NEB}} \qquad \textrm{(6.13)}
$$

$$
E_{\mathrm{noi,sig}} = R_{\mathrm{f}} \sqrt{2q \, I_{\mathrm{p}} \cdot \mathrm{NEB}} \qquad \textrm{(6.14)}
$$

### 6.5 Opamp current noise

The opamp input current noise floor $i_{\mathrm{nif}}$ (white spectral density) also flows through $R_{\mathrm{f}}$:

$$
E_{\mathrm{noi,nif}} = R_{\mathrm{f}} \, i_{\mathrm{nif}} \sqrt{\mathrm{NEB}} \qquad \textrm{(6.15)}
$$

### 6.6 Total noise and signal-to-noise ratio

The total background noise (all sources except signal shot noise) is:

$$
E_{\mathrm{no,bg}} = \sqrt{E_{\mathrm{noe}}^2 + E_{\mathrm{noR}}^2 + E_{\mathrm{noi,bias}}^2 + E_{\mathrm{noi,dark}}^2 + E_{\mathrm{noi,nif}}^2} \qquad \textrm{(6.16)}
$$

The signal voltage is $V_{\mathrm{sig}} = R_{\mathrm{f}} \cdot I_{\mathrm{p}} = R_{\mathrm{f}} \cdot r_\phi \cdot P_{\mathrm{opt}}$, where $r_\phi$ is the photodiode responsivity and $P_{\mathrm{opt}}$ is the incident optical power. The signal-to-noise ratio is:

$$
\mathrm{SNR} = \frac{V_{\mathrm{sig}}}{\sqrt{E_{\mathrm{no,bg}}^2 + E_{\mathrm{noi,sig}}^2}} \qquad \textrm{(6.17)}
$$

The ratio $E_{\mathrm{no,bg}} / E_{\mathrm{noi,sig}}$ indicates whether the system is shot-noise limited (ratio $< 1$) or background-noise limited (ratio $> 1$).

---

## 7. Implementation mapping

| Theory | Implementation | File |
| --- | --- | --- |
| Opamp model, Eq. (1.2) | `Opamp` dataclass (`f_c` field) | [tia_design.py](tia_design.py) |
| Input capacitance $C_{\mathrm{i}}$ | `C_i = C_d + opamp.C_icm + opamp.C_id` | [tia_design.py](tia_design.py) |
| Butterworth $C_{\mathrm{f}}$, Eq. (3.5) | `C_f = (C_c * (2*(C_i+C_s) - C_c))**0.5` | [tia_design.py](tia_design.py) |
| Bandwidth, Eq. (4.3) | `BW_t = (f_c / (2*pi*R_f*C_tot))**0.5` | [tia_design.py](tia_design.py) |
| NEB, Eq. (5.5) | `NEB = (pi*sqrt(2)/4) * BW_t` | [tia_design.py](tia_design.py) |
| Noise gain frequencies, Eqs. (6.1)--(6.3) | `f_zf`, `f_pf`, `f_i` | [tia_design.py](tia_design.py) |
| Piecewise voltage noise, Eqs. (6.5)--(6.10) | `E_noe1` ... `E_noe5`, `E_noe` | [tia_design.py](tia_design.py) |
| Thermal noise, Eq. (6.11) | `E_noR` | [tia_design.py](tia_design.py) |
| Shot noise, Eqs. (6.12)--(6.14) | `E_noi_bias`, `E_noi_dark`, `E_noi_sig` | [tia_design.py](tia_design.py) |
| Current noise, Eq. (6.15) | `E_noi_nif` | [tia_design.py](tia_design.py) |
| SNR, Eq. (6.17) | `snr` | [tia_design.py](tia_design.py) |
| Photodiode $C_{\mathrm{d}}(V_{\mathrm{b}})$ model | `Photodiode.C_d(Vb)` | [tia_design.py](tia_design.py) |
| Multi-opamp comparison | `compare_opamps(...)` | [tia_design.py](tia_design.py) |

## 8. References

1. J. Graeme, *Photodiode Amplifiers: Op Amp Solutions*. McGraw-Hill, 1996.
2. P. C. D. Hobbs, *Building Electro-Optical Systems: Making It All Work*, 2nd ed. Wiley, 2009.

## Acknowledgment

This document was prepared with the assistance of Claude (Anthropic). The author assumes full responsibility for the content.
