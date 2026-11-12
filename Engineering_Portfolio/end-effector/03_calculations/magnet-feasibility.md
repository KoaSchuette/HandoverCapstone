# Magnet Feasibility

This calculation evaluates whether it is feasible for the electromagnet acquired, rated for 400 N, to hold a 1/4 inch (6.35 mm) steel screwdriver shaft without slipping, up to the 0.45 kg required by R3.

## 1. Pull force

For a flux density $B$ (in tesla) crossing a gap, the pull per unit area is

$$p = \frac{B^2}{2\mu_0}$$

where $\mu_0 = 4\pi \times 10^{-7}\ \mathrm{N/A^2}$ is the permeability of free space. The force on a contact of area $A$ is therefore

$$F = \frac{B^2 A}{2\mu_0}$$

Steel cannot carry unlimited flux. Above its saturation flux density $B_{sat}$, adding more current does not raise $B$ any further.

## 2. Force available at the shaft

The screwdriver shaft lies parallel to the magnet face. Flux enters the shaft from the face and travels along the shaft, so the flux the shaft can carry is limited by its cross-section:

$$A_s = \frac{\pi d^2}{4} = \frac{\pi (6.35)^2}{4} = 31.7\ \mathrm{mm^2}$$

The flux crossing the contact is at most $B_{sat} A_s$, and the flux density at the contact is at most $B_{sat}$, so the most force the contact can transmit is

$$F_{sat} = \frac{B_{sat}^2 A_s}{2\mu_0}$$

Assuming a saturation flux density of $B_{sat} = 1.5\ \mathrm{T}$,

$$F_{sat} = \frac{(1.5)^2 (31.7\times10^{-6})}{2(4\pi\times10^{-7})} = 28.4\ \mathrm{N}$$

For a single contact between the face and the shaft, the force available at the shaft is $F_n = 28.4\ \mathrm{N}$.

## 3. Required force

The tool weight is

$$W = mg$$

with $g = 9.81\ \mathrm{m/s^2}$. Acceleration of the arm is neglected.

| Tool mass | $W$ |
|---|---|
| 0.15 kg (screwdriver) | 1.47 N |
| 0.45 kg (R3) | 4.41 N |

**Vertical lift.** The magnet face points down and the tool hangs from it, so the weight acts straight off the face. The tool stays on while

$$F_n \ge W$$

**Horizontal lift.** The magnet face is vertical and the weight acts along the face. Friction must prevent sliding:

$$\mu F_n \ge W \quad\Rightarrow\quad F_n \ge \frac{W}{\mu}$$

Assuming clean, dry steel on steel, $\mu = 0.5$.

## 4. Evaluation

The margin is $F_n / F_{required}$, with $F_n = 28.4\ \mathrm{N}$. The check passes when the margin is at least 1.

**Vertical lift**

| Tool mass | $F_{required}$ | Margin | Result |
|---|---|---|---|
| 0.15 kg | 1.47 N | 19.3 | Pass |
| 0.45 kg | 4.41 N | 6.4 | Pass |

**Horizontal lift**

| Tool mass | $F_{required}$ | Margin | Result |
|---|---|---|---|
| 0.15 kg | 2.94 N | 9.6 | Pass |
| 0.45 kg | 8.83 N | 3.2 | Pass |

## Assumptions

- The saturation flux density of the screwdriver steel is $B_{sat} = 1.5\ \mathrm{T}$, below the 1.6 T to 2 T typical of iron-core electromagnets. It has not been measured.
- The friction coefficient of clean, dry steel on steel is $\mu = 0.5$, the low end of the tabulated range. It has not been measured on the real parts.
- The shaft touches the magnet face at a single contact. A shaft bridging the centre and outer poles has two contacts, so the single-contact value is conservative.
- The saturation limit of the shaft is taken as the force available. Air gaps and the narrow line contact of a round shaft would reduce the real force.

## Sources

- [ZYE1-P series electro holding magnets datasheet](https://static.chipdip.ru/lib/802/DOC033802024.pdf): 400 N rating.
- [Magnet Energy: Maxwell magnetic force equation](https://www.magnetnrg.com/?p=370): $F = B^2 A / 2\mu_0$.
- [US patent 10547218, background on electromagnets](https://image-ppubs.uspto.gov/dirsearch-public/print/downloadPdf/10547218): iron-core field limited to about 1.6 T to 2 T.
- [Misumi: coefficient of friction](https://us.misumi-ec.com/blog/coefficient-of-friction/): 0.5 to 0.8 for clean, dry steel on steel.
- Project proposal, Table 2: R3 and the 0.15 kg tool mass.
