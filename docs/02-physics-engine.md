# Physics and analytics engine

Design notes for the server-side analytics (not implemented yet). Each section covers what is computed, the physics behind it and where it stops working. Formulas are the standard ones from the hydraulics literature (Hazen-Williams, Darcy-Weisbach, Korteweg, FAVAD, Miner's rule) applied to this setup.

---

## A. Steady-state hydraulics (the "expected network")

The engine runs on EPANET via WNTR, with three refinements:

**Friction.** India's design manual (CPHEEO) uses Hazen–Williams; Darcy–Weisbach is the more accurate choice for calibration. Support both:

```text
Hazen–Williams (SI):  h_f = 10.67 · L · Q^1.852 / (C^1.852 · D^4.87)
Darcy–Weisbach:       h_f = f · (L/D) · v²/2g
Swamee–Jain:          f = 0.25 / [ log10( ε/(3.7D) + 5.74/Re^0.9 ) ]²     (Re = vD/ν)
Minor losses:         h_m = Σ K · v²/2g    (bends, tees, valves, reducers)
```

Indian water runs at 25–35 °C, where viscosity is ~20% lower than at 20 °C. Re uses ν(T) from the measured temperature.

**Pressure-dependent demand (PDD).** In intermittent and low-pressure networks a house gets less water when pressure is low. Demand-driven models then go wrong, so SROT uses WNTR's PDD (Wagner) model:
`q = q_req · ((H − H_min)/(H_req − H_min))^0.5`.

**Calibration (nightly).** The C-factor or roughness per pipe group, and zone demand multipliers, are fitted to sensor data by weighted least squares. When a pipe's fitted roughness drifts upward, the cause is **tuberculation or a partly closed valve**, so the drift is a blockage signal.

---

## B. State estimation and residuals

The network's "expected" state at each moment comes from:

```text
x̂ = argmin_x  Σ_i w_i (z_i − h_i(x))²  +  λ‖x − x_prior‖²
   x       = zone demand multipliers (+ tank levels, pump states as known inputs)
   z       = measured heads, inlet flows, tank levels
   x_prior = demand pattern for this time of day/day of week (pseudo-measurements)
   w_i     = 1/σ_i²  (sensor accuracy, from the device record)
```

Residual `r = z − h(x̂)`, normalised by σ.

**Network-level detection:** `J = rᵀWr` follows χ² with m degrees of freedom when the network is healthy. An alarm needs `J > χ²_{m,0.999}` to persist (CUSUM on J), so a single noisy minute never triggers one. Each sensor also runs its own CUSUM to catch drift.

---

## C. Which fault is it? Hypothesis competition

Instead of fixed thresholds, the engine fits several competing physical explanations and keeps the one with the best Bayesian Information Criterion (BIC):

| Hypothesis H | Signature it predicts | Parameters |
|---|---|---|
| H0: normal | r ≈ 0 | — |
| Leak at node/chainage j | `r ≈ q·s_j` with s_j = ∂h/∂q_j (leak sensitivity column) | q ≥ 0 |
| Blockage on pipe k | `r ≈ ΔR·b_k` with b_k = ∂h/∂R_k (resistance sensitivity) | ΔR ≥ 0 |
| Sensor fault on sensor i | r concentrated on sensor i alone (`r ≈ δ·e_i`) | offset δ |
| Demand surge at known large consumer | leak-like column at a known node, follows a schedule, not pressure-driven | q |
| Burst | NPW event at ≥ 2 sentinels + flow step + leak-like column | q, x, t₀ |

A real leak pulls the pressure down at several neighbouring sensors in a coherent pattern. A broken sensor disagrees alone, and no leak column can produce that. This is how a pipe problem is told apart from a measurement problem (analytical redundancy).

Cheap sensor-health checks run before this: flat-line (σ = 0 for N minutes), impossible jumps (|ΔH| larger than the Joukowsky bound `a·ΔV/g` allows), out-of-range values, and slow drift against neighbours.

---

## D. Leak localization, three complementary methods

### D1. Steady-state Bayesian localization (works for slow leaks)

Pipes are split into **25 m virtual segments**. For each candidate location j:

```text
q̂_j        = max(0, s_jᵀW r / s_jᵀW s_j)                    best-fit leak size
likelihood  L_j ∝ exp(−½ (r − q̂_j s_j)ᵀ W (r − q̂_j s_j))
prior       π_j ∝ length_j · λ_j  ·  Π_k (1 + w_k · exp(−d(j,k)²/2σ_c²))
                     ▲ failure rate     ▲ citizen complaints / field reports near j
posterior   P(j | data) ∝ L_j · π_j
```

**Output:** the smallest set of segments that holds 80% of the posterior, reported as e.g. *"Pipe P42, 390–435 m from J12 (p = 0.62); P43 0–50 m (p = 0.21)"*.

**Limitation:** with sparse pressure sensors, a steady-state method usually narrows a leak down to a cluster of pipes (roughly 100–300 m of main), not to metres. D2 and D3 are there to sharpen that.

### D2. Negative-Pressure-Wave (transient) localization (bursts, sudden leaks)

A pipe that suddenly ruptures drops the pressure locally. The drop travels both ways at wave speed *a*.

```text
Wave speed (Korteweg):   a = √(K/ρ) / √(1 + ψ·K·D/(E·e))      K = 2.2 GPa (water)
   uPVC  SDR 21 (E≈3 GPa)      → a ≈ 370 m/s
   HDPE  SDR 11 (E≈0.9 GPa)    → a ≈ 280 m/s
   Ductile iron (E≈170 GPa)    → a ≈ 1,200 m/s

Wave amplitude:          ΔH ≈ a · q_L / (2 g A)
   e.g. 2 L/s burst in 100 mm uPVC → ΔH ≈ 4.8 m  (clearly visible)

Two sensors, distance L apart, arrival times t_A, t_B:
                         x_from_A = (L + a·(t_A − t_B)) / 2
Error:                   δx ≈ (a/2)·√(δt_sync² + 2·δt_pick²)  +  (Δt/2)·δa
```

**Why GPS:** NTP over 4G jitters by 10–50 ms, which is ±2–30 m of error. A GPS **PPS** pulse gives ~1 µs sync, so the 1.16 ms sample period becomes the limit: ±0.2 m in PVC, ±0.7 m in DI. Interpolating between samples narrows it further.

**Looped networks:** the two-sensor formula only holds on a single pipe. In a loop, treat it like locating an earthquake. Every sentinel that sees the wave gives an arrival time `t_i = t₀ + τ(x, s_i)`, where τ is the shortest *travel time* on the pipe graph (Dijkstra with edge weight L/a). Solve for (x, t₀) by least squares over all candidate points. Because t₀ is solved for, the exact moment the burst began doesn't need to be known.

**Calibrate *a* on site:** snap a valve shut and time the wave between two sentinels a known distance apart.

**Limits:** this needs a fairly *sudden* onset. Slow-growing leaks make no clear wave, and D1/MNF handle those. Junctions and branches reflect and weaken the wave, so it works best on trunk mains and DMA feeders.

### D3. Acoustic correlation (optional, metal pipes)

A leak hisses at roughly 20 Hz–1 kHz. Two clamp-on vibration sensors are cross-correlated, and the lag τ at peak correlation gives `x = (L − c·τ)/2`. It works well on metal pipe. In plastic pipe the sound fades quickly, so treat it as experimental. Any result feeds D1 as one more likelihood term.

**Last-metre pinpointing** stays a field job: a step test guided by the app, or a ground microphone.

---

## E. How much water is being lost: FAVAD

A fixed-area orifice gives Q ∝ √P. Real cracks in plastic pipe **open wider as pressure rises**, so SROT uses FAVAD (Fixed And Variable Area Discharge):

```text
Q_L = C_d·√(2g)·(A₀·H^0.5 + m·H^1.5)        or, in practice,   Q_L1/Q_L0 = (H₁/H₀)^N₁
   N₁ ≈ 0.5  rigid round holes (metal)
   N₁ ≈ 1.0  typical mixed network
   N₁ ≈ 1.5  plastic pipes, splits that open under pressure
```

N₁ is fitted per zone from data, either the leak-vs-theft regression (§F) or a night step test.

Reported: L/h, L/day, ₹/day (at the utility's production cost per kL), and severity band.

---

## F. Water balance and the leak-vs-theft split

**IWA water balance** per DMA per day: system input → billed authorised → unbilled authorised → **apparent losses** (theft, meter error) + **real losses** (leaks).

**Leak vs theft split:** leaks are driven by pressure, and consumption follows the demand pattern. Fitting both to the unexplained flow separates them:

```text
Q_unexplained(t) = α · (H(t)/H_ref)^N  +  β · D(t)  + ε        (α, β ≥ 0, NNLS; N grid 0.5–1.5)
   α-term → real losses (leakage)        β-term → apparent losses (illegal / unbilled use)
```

**Minimum Night Flow (24×7 zones):** leak at night = MNF − legitimate night use. Daily leak = night leak × Night-Day Factor, where `NDF = Σ_t (H(t)/H_night)^N`. Leaks run all day too, but at lower daytime pressure.

**End-of-Window Flow (intermittent zones):** most Indian supply runs only a few hours a day. Early in the window, household sumps and tanks fill. Once their float valves close, inlet flow decays toward a plateau:

```text
Q(t) = Q_∞ + (Q₀ − Q_∞)·e^(−t/τ)      →   Q_∞ ≈ leakage + continuous direct draw
```

The pressure-normalised Q_∞ is tracked day by day. A rising Q_∞ means a new leak. EWF does for intermittent networks what MNF does for 24×7 ones.

**KPIs:** NRW %, real losses in L/connection/day, and **ILI** (Infrastructure Leakage Index):

```text
UARL (L/day) = (18·L_m + 0.8·N_c + 25·L_p) · P        L_m km mains, N_c connections, L_p km service pipe, P avg pressure (m)
ILI = Current Annual Real Losses / UARL
```

---

## G. Pressure management advisor

```text
Leak reduction from a pressure cut:   Q_L,new = Q_L,old · (H_new/H_old)^N₁
   e.g. 45 m → 35 m with N₁ = 1.15  →  ~25% less leakage, and fewer bursts
Constraint: head at critical node ≥ H_min (CPHEEO: ~7 m 1-storey, 12 m 2-storey, 17 m 3-storey)
Flow-modulated PRV set-point:          H_PRV(t) = H_min + Δh_friction(Q(t)) to critical node
```

Output example: *"Lower PRV-3 night set-point from 42 m to 33 m: est. −3,100 L/h leakage, critical node J88 stays ≥ 9 m."*

**Pump efficiency:** `η_ww = ρ·g·Q·(H_d − H_s) / P_elec` and specific energy `kWh/m³`. When efficiency drifts down, the cause is impeller wear, cavitation or a clogged suction.

---

## H. Supply equity and intrusion risk (intermittent supply)

**Supply equity:** for each node, *Adequate-Service Hours* = hours with H ≥ H_min. The Gini coefficient of ASH (or of delivered L/connection) across zones measures inequity, and tail-end zones get flagged. A what-if simulator tests valve-throttling schedules that even out supply.

**Contamination intrusion:** when supply stops, pipes depressurise. Wherever the pipe pressure falls below the outside water level (groundwater, a flooded drain or sewer), dirty water can enter through leaks and joints:

```text
Intrusion flow at a defect:      q_in = C_d·A·√(2g·(H_ext − H))      when H < H_ext
Intrusion Potential Index (pipe): IPI = Σ_t max(0, H_ext − H(t)) · leak_likelihood · sewer_proximity
```

When supply restarts, a turbidity "first flush" is expected at downstream Q-nodes. A first flush that is high or persistent next to a high-IPI pipe raises a P1 contamination alert.

---

## I. Water quality engine

- **Limits (IS 10500:2012):** pH 6.5–8.5; turbidity 1 NTU acceptable / 5 NTU permissible; TDS 500 / 2,000 mg/L; residual free chlorine ≥ 0.2 mg/L.
- **Chlorine everywhere without chlorine sensors:** WNTR computes **water age** at every node, and first-order decay `C = C₀·e^(−k·age)` (k = bulk + wall) gives the predicted residual. k is calibrated from Q-nodes and monthly DPD kit tests. The output names the tail-end nodes likely below 0.2 mg/L and the dose change at source that would fix them.
- **Cheap chlorine proxy:** ORP responds mostly to HOCl, and the HOCl fraction depends on pH: `α = 1/(1 + 10^(pH − 7.5))`. ORP + pH, calibrated per site against DPD tests, estimate free chlorine. It is labelled an estimate, never a lab value.
- **TDS ↔ EC:** `EC₂₅ = EC_T / (1 + 0.02(T − 25))`, `TDS ≈ 0.55–0.7 · EC₂₅`, with temperature from the DS18B20.
- **Trends:** Theil–Sen slope + Mann–Kendall test catch slow deterioration; CUSUM catches steps.
- **Source tracing:** when Q-nodes A and B see contamination and C doesn't, take the upstream flow paths at the right travel time. The candidate source region is `upstream(A) ∩ upstream(B) − upstream(C)`.

---

## J. Pipe health and failure risk

**Physics from day one:**

- **Pressure-cycle fatigue.** Rainflow counting of the 1-min (and transient) pressure series gives cycles of range ΔH. Hoop stress is `σ = ρg·ΔH·D/(2e)`, and Miner's rule gives damage `D_f = Σ n_k / N_k(Δσ_k)` from the material's S-N curve. Plastic pipes in intermittent networks go through **daily fill/empty cycles plus water hammer**, so this factor is expected to matter in Indian networks.
- Age, material, diameter, P95 pressure, transient count, past failures, anomaly history, soil/traffic (if GIS has it).

**Model:** a proportional-hazards form with literature-default coefficients, refitted (Cox/Weibull) once the utility's failure records exist:

```text
λ_pipe = λ₀(material, D) · exp(β_age·age + β_fat·D_f + β_P·P95 + β_tr·transients + β_hist·failures + β_an·anomalies)
Health score = 100 · exp(−λ_pipe · horizon)      (shown with its top-3 contributing factors)
```

λ_pipe also serves as the **prior** for leak localization (§D1), which links prediction and detection.

---

## K. Maintenance priority and isolation planning

```text
Priority = P(active leak or failure) × Consequence × Confidence
Consequence = downstream population (graph reachability) + critical users (hospital, school)
            + water lost ₹/day + isolation impact + road/traffic class
```

**Isolation planner:** the **valve-segment graph** is built by cutting the network at every valve, so each connected part becomes a segment. To repair pipe P, close the valves around its segment. A BFS from the sources then lists every node that loses supply, giving *"Close V12, V15, V19 → 340 connections affected for ~3 h, including 1 school."* This also flags valves whose failure would isolate large areas.

---

## L. Sensor-placement optimizer

1. Simulate a nominal leak at every candidate segment j (WNTR) → signature matrix S (all candidate sensor locations × leak locations).
2. Objective = number of leak pairs (j, k) a sensor set can tell apart (normalised signature angle > threshold), + coverage of trunk segments by sentinel pairs (for NPW).
3. **Greedy selection.** The objective is submodular, so greedy is provably within ~63% of optimal, and it ranks candidates in order.

Output: *"Next best: J23 (+18% distinguishable leak pairs), J7 (+11%), J51 (+6%)."* The ranking updates as sensors are added.

---

## M. Virtual sensors (no hardware needed)

| Virtual quantity | From | Physics |
|---|---|---|
| Tank outflow | Ultrasonic level + inlet flow | `A(h)·dh/dt = Q_in − Q_out` |
| Pipe flow | Δh between two pressure sensors on a calibrated pipe | `Q = 0.2785·C·D^2.63·S^0.54` (HW, SI) |
| Free chlorine at any node | Source dose + water age | `C₀·e^(−k·age)` |
| Free chlorine at a Q-node | ORP + pH | HOCl fraction + site calibration |
| Pump flow (approx.) | Electrical power + head | Pump curve + η |
| Supply on/off per zone | Sentinel pressure step | Threshold + travel time downstream |

---

## N. Field feedback loop

Every field outcome (*found at 412 m / not found / it was a valve / it was theft*) is stored with the hypothesis it answers. Each week the system:

- measures localization error and calibration: do the "80%" intervals contain the leak 80% of the time? If not, σ is rescaled.
- updates failure-rate priors per material/age.
- builds a labelled dataset. A **physics-informed ML** layer is trained on it later, only after enough labels exist (e.g. a GNN on residuals; BattLeDIM-style methods).

---

## Validation plan

| Step | Data | Metric |
|---|---|---|
| 1 | Synthetic: WNTR on Net3 + an Indian-style intermittent network with injected leaks/faults | Detection time, false alarms/week, localization error (m), classification accuracy |
| 2 | **BattLeDIM L-Town** (public benchmark, 33 real leak events) | Same metrics as published methods |
| 3 | Physical test rig (doc 03) with leak taps at known chainages | NPW error (m), FAVAD flow estimate vs measured bucket flow |
| 4 | Pilot DMA with the utility | Leaks confirmed by field crews, L/day recovered |
