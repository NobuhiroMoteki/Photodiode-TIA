# Technical Note: TIA Theory — Full Derivations

This document provides complete, step-by-step derivations of the formulas
used in the transimpedance amplifier (TIA) design tool.
No steps are omitted; every algebraic manipulation is shown explicitly.

## Table of contents

1. [Circuit model and assumptions](#1-circuit-model-and-assumptions)
2. [Closed-loop transimpedance transfer function](#2-closed-loop-transimpedance-transfer-function)
3. [Butterworth-optimum feedback capacitance](#3-butterworth-optimum-feedback-capacitance)
4. [Bandwidth](#4-bandwidth)
5. [Noise equivalent bandwidth](#5-noise-equivalent-bandwidth)

---

## 1. Circuit model and assumptions

### Circuit topology

The TIA is an inverting opamp configuration with a photodiode at the input.
The non-inverting input is connected to ground.

- $I_{pd}$: photocurrent from the photodiode (signal source, modelled as ideal current source)
- $R_f$, $C_f$: feedback resistance and capacitance (in parallel), connected from the output to the inverting input
- $C_i$: total input capacitance at the inverting node, $C_i = C_d + C_{icm} + C_{id}$
  - $C_d$: photodiode junction capacitance
  - $C_{icm}$: opamp common-mode input capacitance
  - $C_{id}$: opamp differential input capacitance
- $C_s$: stray (parasitic) capacitance at the inverting node to ground

### Opamp model

The opamp is modelled with a single-pole open-loop gain:

```math
A(s) = \frac{A_0 \,\omega_p}{s + \omega_p}
```

where $A_0$ is the DC open-loop gain and $\omega_p$ is the dominant pole frequency.
For frequencies well above the dominant pole ($s \gg \omega_p$, i.e. $f \gg f_p$,
typically satisfied for $f > 10$ Hz), this simplifies to:

```math
A(s) \approx \frac{A_0 \,\omega_p}{s} = \frac{\omega_c}{s}
```

where $\omega_c = A_0 \,\omega_p = 2\pi f_c$ is the gain-bandwidth product (GBW) in rad/s.
This "integrator model" is the standard approximation used throughout TIA design literature
and is accurate across the entire frequency range of interest (kHz to MHz).

---

## 2. Closed-loop transimpedance transfer function

### Goal

Derive the closed-loop transimpedance:

```math
Z_{TI}(s) \equiv \frac{V_{\text{out}}(s)}{I_{pd}(s)}.
```

### Step 1: Define the feedback impedance

$R_f$ and $C_f$ are in parallel:

```math
Z_f = R_f \;\|\; \frac{1}{sC_f} = \frac{R_f}{1 + sR_fC_f}.
```

### Step 2: Opamp constraint

With the non-inverting input grounded:

```math
V_{\text{out}} = -A(s) \cdot V^{-} = -\frac{\omega_c}{s} \, V^{-}
```

Solving for $V^-$:

```math
V^{-} = -\frac{s}{\omega_c}\,V_{\text{out}}.
```

### Step 3: Kirchhoff's current law at the inverting node

All currents leaving the inverting node must sum to zero.
The current into the node from the photodiode is $I_{pd}$.
The currents leaving the node are:

- Through the feedback network to the output: $(V^{-} - V_{\text{out}}) / Z_f$
- Through the total shunt capacitance $(C_i + C_s)$ to ground: $V^{-} \cdot s(C_i + C_s)$

KCL:

```math
I_{pd} + \frac{V^{-} - V_{\text{out}}}{Z_f} + V^{-} \cdot s(C_i + C_s) = 0
```

Note the sign convention: current flowing from the node through $Z_f$ toward $V_{\text{out}}$
is $(V^{-} - V_{\text{out}})/Z_f$. Rearranging with current into the node on the left:

```math
I_{pd} = \frac{V_{\text{out}} - V^{-}}{Z_f} - V^{-} \cdot s(C_i + C_s).
```

### Step 4: Substitute the opamp constraint

Substitute (2.1) and (2.2) into (2.3).

First, compute $V_{\text{out}} - V^-$:

```math
V_{\text{out}} - V^{-} = V_{\text{out}} - \left(-\frac{s}{\omega_c}V_{\text{out}}\right) = V_{\text{out}}\left(1 + \frac{s}{\omega_c}\right) = V_{\text{out}} \cdot \frac{\omega_c + s}{\omega_c}
```

Substitute into the feedback current term:

```math
\frac{V_{\text{out}} - V^{-}}{Z_f} = V_{\text{out}} \cdot \frac{\omega_c + s}{\omega_c} \cdot \frac{1 + sR_fC_f}{R_f}
```

The shunt capacitance current term:

```math
-V^{-} \cdot s(C_i + C_s) = \frac{s}{\omega_c}V_{\text{out}} \cdot s(C_i + C_s) = \frac{s^2 (C_i + C_s)}{\omega_c}\,V_{\text{out}}.
```

### Step 5: Combine

Substituting (2.5) and (2.6) into (2.3):

```math
I_{pd} = V_{\text{out}} \left[\frac{(\omega_c + s)(1 + sR_fC_f)}{\omega_c R_f} + \frac{s^2(C_i + C_s)}{\omega_c}\right]
```

Factor out $1/\omega_c$:

```math
I_{pd} = \frac{V_{\text{out}}}{\omega_c}\left[\frac{(\omega_c + s)(1 + sR_fC_f)}{R_f} + s^2(C_i + C_s)\right].
```

### Step 6: Expand the product

```math
(\omega_c + s)(1 + sR_fC_f) = \omega_c + \omega_c s R_f C_f + s + s^2 R_f C_f
```

Rearranging in powers of $s$:

```math
= s^2 R_f C_f + s(1 + \omega_c R_f C_f) + \omega_c.
```

### Step 7: Divide by $R_f$ and add the shunt term

```math
\frac{(\omega_c + s)(1 + sR_fC_f)}{R_f} + s^2(C_i + C_s)
```

```math
= s^2 C_f + \frac{s(1 + \omega_c R_f C_f)}{R_f} + \frac{\omega_c}{R_f} + s^2(C_i + C_s)
```

```math
= s^2(C_i + C_f + C_s) + s\,\frac{1 + \omega_c R_f C_f}{R_f} + \frac{\omega_c}{R_f}.
```

### Step 8: Form the transfer function

From (2.7) and (2.9):

```math
I_{pd} = \frac{V_{\text{out}}}{\omega_c}\left[s^2(C_i + C_f + C_s) + s\,\frac{1 + \omega_c R_f C_f}{R_f} + \frac{\omega_c}{R_f}\right]
```

```math
Z_{TI}(s) = \frac{V_{\text{out}}}{I_{pd}} = \frac{\omega_c}{s^2(C_i + C_f + C_s) + s\,\frac{1 + \omega_c R_f C_f}{R_f} + \frac{\omega_c}{R_f}}.
```

(The overall sign is negative for the inverting configuration; we write the magnitude here
and note the 180 degree phase inversion separately.)

### Step 9: Identify the standard second-order form

A standard second-order low-pass transfer function has the form:

```math
H(s) = \frac{K\,\omega_n^2}{s^2 + 2\zeta\omega_n\,s + \omega_n^2}
```

Dividing numerator and denominator of (2.10) by $(C_i + C_f + C_s)$:

```math
Z_{TI}(s) = \frac{\frac{\omega_c}{C_i + C_f + C_s}}{s^2 + \frac{1 + \omega_c R_f C_f}{R_f(C_i + C_f + C_s)}\,s + \frac{\omega_c}{R_f(C_i + C_f + C_s)}}
```

By comparison with the standard form, we identify:

```math
\omega_n^2 = \frac{\omega_c}{R_f(C_i + C_f + C_s)}.
```

```math
2\zeta\omega_n = \frac{1 + \omega_c R_f C_f}{R_f(C_i + C_f + C_s)}.
```

The DC gain ($s = 0$) of (2.11):

```math
Z_{TI}(0) = \frac{\omega_c / (C_i + C_f + C_s)}{\omega_n^2} = \frac{\omega_c / (C_i + C_f + C_s)}{\omega_c / [R_f(C_i + C_f + C_s)]} = R_f.
```

The numerator constant can therefore be written as $R_f\,\omega_n^2$, giving the final form
(restoring the sign for the inverting configuration):

```math
Z_{TI}(s) = \frac{-R_f\,\omega_n^2}{s^2 + 2\zeta\omega_n\,s + \omega_n^2}.
```

---

## 3. Butterworth-optimum feedback capacitance

### Goal

Find the value of $C_f$ that makes the closed-loop response maximally flat (Butterworth).

### Step 1: Butterworth condition

A second-order Butterworth (maximally flat magnitude) filter has quality factor:

```math
Q = \frac{1}{\sqrt{2}}
```

The relationship between $Q$ and the damping ratio $\zeta$ is $Q = 1/(2\zeta)$, so:

```math
\zeta = \frac{1}{\sqrt{2}}.
```

This is the unique damping ratio that produces zero gain peaking in the magnitude response
(i.e. $|Z_{TI}(j\omega)|$ is monotonically decreasing).

### Step 2: Translate the condition to circuit parameters

The Butterworth condition (3.1) implies:

```math
(2\zeta\omega_n)^2 = 4\zeta^2\omega_n^2 = 4 \cdot \frac{1}{2} \cdot \omega_n^2 = 2\,\omega_n^2.
```

Substituting (2.12) and (2.13):

```math
\left(\frac{1 + \omega_c R_f C_f}{R_f(C_i + C_f + C_s)}\right)^2 = 2 \cdot \frac{\omega_c}{R_f(C_i + C_f + C_s)}
```

Multiply both sides by $[R_f(C_i + C_f + C_s)]^2$:

```math
(1 + \omega_c R_f C_f)^2 = 2\,\omega_c R_f(C_i + C_f + C_s).
```

### Step 3: Solve for $C_f$ (with $C_s = 0$ for clarity)

Setting $C_s = 0$ (the typical case; if $C_s \neq 0$, it can be absorbed into $C_i$
by defining $C_i' = C_i + C_s$):

```math
(1 + \omega_c R_f C_f)^2 = 2\,\omega_c R_f(C_i + C_f).
```

Define a characteristic capacitance:

```math
C_c \equiv \frac{1}{\omega_c R_f} = \frac{1}{2\pi f_c R_f}.
```

This has a physical interpretation: $C_c$ is the capacitance whose impedance at $f_c$
equals $R_f$.

Rewrite (3.3) using $\omega_c R_f = 1/C_c$:

```math
\left(1 + \frac{C_f}{C_c}\right)^2 = \frac{2(C_i + C_f)}{C_c}
```

Expand the left side:

```math
1 + \frac{2C_f}{C_c} + \frac{C_f^2}{C_c^2} = \frac{2C_i}{C_c} + \frac{2C_f}{C_c}
```

The $2C_f/C_c$ terms cancel:

```math
1 + \frac{C_f^2}{C_c^2} = \frac{2C_i}{C_c}
```

Multiply through by $C_c^2$:

```math
C_c^2 + C_f^2 = 2C_i C_c
```

```math
C_f^2 = 2C_i C_c - C_c^2 = C_c(2C_i - C_c).
```

Taking the positive root:

```math
C_f = \sqrt{C_c(2C_i - C_c)}, \qquad C_c = \frac{1}{2\pi f_c R_f}.
```

### Validity condition

Equation (3.6) requires the argument of the square root to be non-negative:

```math
2C_i - C_c > 0 \quad\Longleftrightarrow\quad C_i > \frac{C_c}{2} = \frac{1}{2\omega_c R_f}.
```

When this condition is violated, the opamp GBW is too low (or $R_f$ too small) to achieve
a Butterworth response — the circuit is fundamentally underdamped regardless of $C_f$.

### Relation to the common approximation

Many references simplify by assuming $\omega_c R_f C_f \gg 1$ (equivalently $C_f \gg C_c$).
Under this approximation, (3.3) becomes:

```math
(\omega_c R_f C_f)^2 \approx 2\,\omega_c R_f\,C_i \quad\Longrightarrow\quad C_f \approx \sqrt{\frac{2C_i}{\omega_c R_f}} = \sqrt{2C_i C_c}.
```

Equation (3.6) is the **exact** solution that does not rely on this approximation.
The difference is significant when $C_c$ is not negligible compared to $C_i$
(i.e. when $R_f$ is small or $f_c$ is low).

---

## 4. Bandwidth

### $-3\,\text{dB}$ bandwidth of a second-order Butterworth

For a general second-order transfer function with damping ratio $\zeta$,
the squared magnitude response is:

```math
|H(j\omega)|^2 = \frac{\omega_n^4}{(\omega_n^2 - \omega^2)^2 + (2\zeta\omega_n\omega)^2}
```

For the Butterworth case $\zeta = 1/\sqrt{2}$, substituting and simplifying:

```math
|H(j\omega)|^2 = \frac{\omega_n^4}{(\omega_n^2 - \omega^2)^2 + 2\omega_n^2\omega^2}
```

Expand the denominator:

```math
= \omega_n^4 - 2\omega_n^2\omega^2 + \omega^4 + 2\omega_n^2\omega^2 = \omega_n^4 + \omega^4
```

Therefore:

```math
|H(j\omega)|^2 = \frac{\omega_n^4}{\omega_n^4 + \omega^4} = \frac{1}{1 + (\omega/\omega_n)^4}.
```

This is the defining form of a second-order Butterworth response.

At $\omega = \omega_n$:

```math
|H(j\omega_n)|^2 = \frac{1}{1 + 1} = \frac{1}{2} \quad\Longrightarrow\quad |H(j\omega_n)| = \frac{1}{\sqrt{2}} \;(-3\,\text{dB}).
```

Therefore the $-3\,\text{dB}$ bandwidth is exactly the natural frequency:

```math
\omega_{-3\text{dB}} = \omega_n.
```

In terms of ordinary frequency:

```math
f_{-3\text{dB}} = \frac{\omega_n}{2\pi}.
```

### Express in terms of circuit parameters

From (2.12):

```math
\omega_n = \sqrt{\frac{\omega_c}{R_f(C_i + C_f + C_s)}} = \sqrt{\frac{2\pi f_c}{R_f(C_i + C_f + C_s)}}
```

Therefore:

```math
f_{-3\text{dB}} = \frac{\omega_n}{2\pi} = \frac{1}{2\pi}\sqrt{\frac{2\pi f_c}{R_f(C_i + C_f + C_s)}} = \sqrt{\frac{f_c}{2\pi R_f(C_i + C_f + C_s)}}.
```

---

## 5. Noise equivalent bandwidth

### Definition

The noise equivalent bandwidth (NEB) of a filter $H(f)$ is the bandwidth of
an ideal rectangular (brick-wall) filter with the same peak gain that passes the same
total noise power:

```math
\text{NEB} = \frac{1}{|H_{\max}|^2}\int_0^{\infty} |H(f)|^2 \, df
```

For a Butterworth filter, $|H_{\max}| = |H(0)| = 1$, so:

```math
\text{NEB} = \int_0^{\infty} |H(f)|^2 \, df.
```

### General $n$-th order Butterworth NEB

For an $n$-th order Butterworth filter, the squared magnitude response is:

```math
|H(f)|^2 = \frac{1}{1 + (f/f_{-3\text{dB}})^{2n}}
```

Substituting into (5.1) with $u = f/f_{-3\text{dB}}$:

```math
\text{NEB} = f_{-3\text{dB}} \int_0^{\infty} \frac{du}{1 + u^{2n}}.
```

The integral $\displaystyle I_n = \int_0^{\infty} \frac{du}{1 + u^{2n}}$ is a standard result
that can be evaluated using the substitution $t = u^{2n}$ and recognizing the beta function.

Setting $t = u^{2n}$, so $u = t^{1/(2n)}$, $du = \frac{1}{2n}\,t^{1/(2n)-1}\,dt$:

```math
I_n = \int_0^{\infty} \frac{1}{1+t} \cdot \frac{1}{2n}\,t^{1/(2n)-1}\,dt = \frac{1}{2n}\,B\!\left(\frac{1}{2n},\; 1 - \frac{1}{2n}\right)
```

where $B(a, b) = \Gamma(a)\Gamma(b)/\Gamma(a+b)$ is the beta function.

Using the reflection formula $\Gamma(z)\,\Gamma(1-z) = \pi/\sin(\pi z)$ with $z = 1/(2n)$:

```math
I_n = \frac{1}{2n} \cdot \frac{\pi}{\sin\!\left(\frac{\pi}{2n}\right)}.
```

Therefore:

```math
\text{NEB} = f_{-3\text{dB}} \cdot \frac{\pi}{2n\,\sin\!\left(\frac{\pi}{2n}\right)}.
```

### Specialization to $n = 2$

For the second-order Butterworth ($n = 2$):

```math
\text{NEB} = f_{-3\text{dB}} \cdot \frac{\pi}{2 \cdot 2 \cdot \sin\!\left(\frac{\pi}{4}\right)} = f_{-3\text{dB}} \cdot \frac{\pi}{4 \cdot \frac{\sqrt{2}}{2}} = f_{-3\text{dB}} \cdot \frac{\pi}{2\sqrt{2}}
```

Rationalizing:

```math
= f_{-3\text{dB}} \cdot \frac{\pi}{2\sqrt{2}} \cdot \frac{\sqrt{2}}{\sqrt{2}} = f_{-3\text{dB}} \cdot \frac{\pi\sqrt{2}}{4}
```

```math
\text{NEB} = f_{-3\text{dB}} \cdot \frac{\pi\sqrt{2}}{4} \approx 1.111\,f_{-3\text{dB}}.
```

### Comparison with the single-pole approximation

For a single-pole (first-order) system ($n = 1$):

```math
\text{NEB}_{n=1} = f_{-3\text{dB}} \cdot \frac{\pi}{2\sin(\pi/2)} = f_{-3\text{dB}} \cdot \frac{\pi}{2} \approx 1.571\,f_{-3\text{dB}}.
```

Many TIA references use this single-pole approximation even when the circuit
has a second-order response. The second-order Butterworth NEB is
$1.111/1.571 = 0.707$ times the single-pole value — a 29% difference
that directly affects computed noise levels.
