# Mobile app design

This is the plan for the full app. The app in [mobile/](../mobile/README.md) implements a smaller part of it: it talks directly to monitors on the local network (live readings, alerts, setup, calibration, burst location). Maps, work orders, the field and citizen modes and the server-backed screens below are not built.

## 1. Who the app is for

A water utility doesn't run from a control room alone. Most of the work happens in the field, and residents often notice problems first. So the plan is one app with three role-based modes:

| Mode | User | Core job |
|---|---|---|
| **Operator** | JE/AE engineers, zone operators | Know the network's state, decide what to fix first, dispatch crews |
| **Field** | Plumbers, valve men, maintenance crews, installers | Find the leak, fix it, report what they found, install and calibrate nodes |
| **Citizen (lite)** | Residents | Know when water comes, report problems, see if water is safe |

Field mode supplies ground truth: every confirmed or rejected leak is a label (see §N of the [physics doc](02-physics-engine.md)). Citizen mode adds coarse sensing: a low-pressure complaint is a rough pressure reading at a location with no sensor, and it feeds the Bayesian prior.

---

## 2. Operator mode

### 2.1 Network Pulse (home)
- **Network health** (0–100) and a count of open incidents by tier (P1/P2/P3)
- **Today's water balance**: supplied / accounted / lost, shown in **litres and ₹**
- **Supply status per zone**: ON/OFF, how long since start, next scheduled window, zones short on supply
- Top 3 priorities with one-tap "Dispatch"

### 2.2 Live Map (digital twin)
- MapLibre map with pipes drawn from PostGIS GeoJSON
- **Layer switcher:** pressure (live vs expected) · flow direction · pipe health · failure risk · water age / predicted chlorine · intrusion risk · sensor coverage
- **Leak hypotheses** shown as a glowing band *along the pipe polyline*, so they still read correctly when the pipe turns; opacity = posterior probability
- Tap a pipe → **Pipe card**: length, diameter, material, age, live vs expected pressure, health score with its top 3 factors, anomalies, repair history
- Tap a node → live charts (24 h, 7 d), device status

### 2.3 Incident detail
Each incident answers what, where, how bad, how sure, why, and what to do:
- **Type:** burst / leak / blockage / sensor fault / theft-like loss / quality / intrusion / pressure
- **Where:** ranked candidate segments, e.g. *P42: 390–435 m from J12 (62%)*, shown on a mini-map
- **How bad:** L/h, L/day, ₹/day, people affected
- **How sure:** confidence plus *which evidence agrees*: residual pattern ✔, NPW timing ✔, citizen reports (3) ✔, acoustic ✖
- **Why (explainability):** observed vs expected chart, residual bar chart per sensor, posterior curve along the pipe, the NPW waveforms from both sentinels with arrival markers
- **What to do:** recommended action, **isolation plan** (valves to close, connections affected, estimated outage), "Create work order"

### 2.4 Water balance and NRW
- IWA water balance per DMA (system input → billed → real losses → apparent losses)
- MNF trend (24×7 zones) / **End-of-Window Flow** trend (intermittent zones)
- **Leak-vs-theft split** over time
- ILI, NRW %, L/connection/day; target vs actual (AMRUT 2.0 goals)

### 2.5 Pressure and supply equity
- Hours of adequate pressure per zone, tail-end deprivation list
- Pressure Advisor cards: *"Lower PRV-3 to 33 m at night → −3,100 L/h, critical node OK"* with Accept / Simulate
- Pump energy: kWh/m³, efficiency trend, alerts when efficiency drops

### 2.6 Water quality
- Per Quality node: pH, TDS, turbidity, temperature, estimated chlorine, each against IS 10500 bands
- Network-wide predicted chlorine map from the water-age model
- First-flush events after supply restarts, intrusion-risk pipes
- Contamination trace: highlights the candidate source region upstream

### 2.7 Assets and risk
- Pipes ranked by failure risk; filter by zone, material, age
- Each pipe's fatigue damage, transient count, and repair history

### 2.8 Maintenance queue
- Priority-ranked work orders (Risk × Consequence × Confidence); drag to reorder, assign to crew, set an SLA
- Kanban: New → Assigned → On site → Fixed → Verified

### 2.9 Devices and coverage
- Every node: last seen, battery, signal, firmware, calibration due date, suspected sensor fault
- **Sensor placement advisor:** *"Add a sensor at J23 → +18% leak localization coverage"*, shown on the map

### 2.10 What-if simulator (lite)
- Close or open a valve, change a PRV set-point, or switch off a pump → the backend runs WNTR → map shows the predicted pressure change and the connections that lose supply
- Used to plan repairs and shutdowns *before* touching anything

---

## 3. Field mode

### 3.1 My Jobs
- Today's assigned jobs, sorted by priority and travel distance
- Works **offline**: map tiles, job data and network geometry are downloaded per zone

### 3.2 Go to search zone
- Navigation to the start of the probable leak band
- On site: *"You are 40 m from the search zone start"*. The band is highlighted along the real pipe route, with valve and chamber locations marked.

### 3.3 Guided step test
The classic utility method, made easier:
1. The app lists the valves in order, from the isolation plan
2. The crew closes valve 1 → the app shows the **live inlet flow** from the Sentinel
3. A large drop in flow means the leak lies in that section
4. Repeat until the leak is down to one section; the app records each step automatically

### 3.4 Outcome report (closing the loop)
- **Found it?** Yes / No / Something else (valve passing, theft, meter fault, private-side leak)
- **Exact spot:** drop a pin on the pipe → the app computes the chainage and the error against the prediction
- Leak type (joint, crack, burst, service connection), pipe condition, estimated flow
- Photos/video (geotagged), repair materials, time spent
- These records become training data, so the form should take under a minute to fill.

### 3.5 Node commissioning over BLE
1. Scan the QR code on the node
2. The phone connects over BLE → firmware version, self-test
3. **Bind to the network:** choose the junction on the map (or "nearest junction" from the phone's GPS)
4. Set Wi-Fi/APN, sampling profile (Sentinel/Scout/Quality/Tank)
5. **Calibration wizards:**
   - Pressure: zero with the port open to air → compare with a reference gauge → save offset/gain
   - pH: dip in buffer 7 → buffer 4 → slope saved
   - TDS: standard solution
   - Turbidity: clear-water baseline
   - Flow: bucket test (fill 10 L, the app times it and counts pulses)
6. Photo of the installation → done. The device record goes to the server.

### 3.6 Manual readings
- Enter DPD chlorine and portable pressure gauge readings. Each one becomes a calibration point for the virtual sensors.

---

## 4. Citizen mode (lite)

| Feature | Purpose |
|---|---|
| "When is water coming?": the zone schedule plus a live push alert (*"Water reaching your area in ~15 min"*), worked out from the upstream Sentinel's supply-start detection plus travel time | Useful in intermittent-supply cities, and gives residents a reason to install the app |
| Report a problem: leak/overflow, no water, low pressure, dirty/smelly water, with photo and GPS | Reports feed the Bayesian localizer and quality alerts |
| Is my water safe?: zone status (green/amber/red) from Quality nodes and the chlorine model | Public information |
| Track my complaint: status updates when the crew is assigned or the job is fixed | Accountability |

Anti-abuse: phone-OTP login, rate limits, and duplicate grouping (several reports near one point merge into one cluster).

---

## 5. Notifications

| Tier | Who | How |
|---|---|---|
| P1 (burst, contamination, intrusion) | On-duty operator + zone engineer | Push with an **alarm sound** + SMS. Escalates if not acknowledged in 10 min. |
| P2 (persistent leak, pressure out of range, low chlorine) | Zone operator | Push |
| P3 (sensor drift, battery, calibration due) | Device owner | Daily digest |
| Citizen | Residents of the zone | Supply arrival, outage notices, safety advisories |

---

## 6. Non-functional requirements

- **Runs on low-end Android** (2–3 GB RAM, Android 9+). Keep the APK small and lazy-load charts.
- **Offline-first:** local SQLite cache with a sync queue. Field reports made without network upload later.
- **Data-light:** live updates over a WebSocket with diffs only; map tiles cached.
- **Languages:** English + Hindi from day one; JSON i18n files so regional languages can be added easily.
- **Accessibility:** big touch targets for field use, high-contrast sunlight mode, icons alongside colours (never colour alone).
- **Security:** role-based access by zone; citizens never see network geometry beyond their zone's status.

---

## 7. Tech stack

| Concern | Choice | Reason |
|---|---|---|
| Framework | React Native + Expo (TypeScript) | Logic and skills can be shared with a React web control room later |
| Maps | `@maplibre/maplibre-react-native` | Open source, no per-load fees, supports **offline tile packs** |
| Charts | `victory-native` (Skia) | Fast enough for live charts on cheap phones |
| BLE commissioning | `react-native-ble-plx` | ESP32 BLE GATT provisioning (needs an Expo dev build, not Expo Go) |
| Offline DB | `expo-sqlite` (or WatermelonDB) + sync queue | Field crews in areas with poor signal |
| Push | `expo-notifications` + FCM | |
| State/data | TanStack Query + Zustand | Caching, retries, offline mutations |
| Auth | Phone OTP → JWT (refresh tokens in SecureStore) | |
| i18n | `i18next` | English/Hindi + regional |

## 8. Screen map

```text
Login (OTP) → role detection
├─ Operator:  Pulse │ Map │ Incidents │ Balance │ Quality │ Maintenance │ More(Assets, Devices, What-if, Equity, Settings)
├─ Field:     My Jobs │ Map (offline) │ Step test │ Commission node │ Manual reading │ Profile
└─ Citizen:   My Supply │ Report │ My Reports │ Water Safety
```
