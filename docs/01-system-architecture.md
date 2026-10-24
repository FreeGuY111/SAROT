# System architecture

This describes the full planned system. Only the device layer (L0, firmware) and a direct phone-to-device app are implemented so far; see the [README](../README.md).

## 1. Layered view

```text
┌──────────────────────────────────────────────────────────────────────────────┐
│ L5  APPS        Mobile app (React Native/Expo)          Web control room     │
│                 ├─ Operator mode   ├─ Field-crew mode   (React, later)       │
│                 └─ Citizen mode (lite)                                       │
├──────────────────────────────────────────────────────────────────────────────┤
│ L4  API         FastAPI  REST + WebSocket │ JWT/RBAC │ FCM push │ SMS fallback│
├──────────────────────────────────────────────────────────────────────────────┤
│ L3  INTELLIGENCE (Python workers)                                            │
│   Network Model (WNTR/EPANET) ─► State Estimator ─► Residual Generator       │
│        │                                                │                    │
│        ▼                                                ▼                    │
│   Calibration (C-factor,      Anomaly Engine ─► Classifier (leak / burst /   │
│   demand, wave speed)         (CUSUM, EWMA,      blockage / sensor fault /   │
│                               MNF/EWF)           demand / theft / quality)   │
│                                                         │                    │
│   NPW Transient Locator ──┐                             ▼                    │
│   Acoustic correlator ────┼──► Bayesian Localizer ─► Severity (FAVAD)        │
│   Citizen reports ────────┘         ▲                   │                    │
│                                     │ prior             ▼                    │
│   Risk Engine (fatigue, age, ───────┘          Prioritizer ─► Isolation      │
│   material, anomalies)                          (Risk×Consequence×Conf)  Planner│
│   Quality Engine (IS 10500, Cl decay, intrusion) │ Water Balance (IWA, ILI)  │
│   Pressure Advisor (PRV/pump) │ Sensor-Placement Optimizer │ Supply Equity   │
├──────────────────────────────────────────────────────────────────────────────┤
│ L2  DATA        MQTT broker (EMQX/Mosquitto) ─► Ingest service               │
│                 TimescaleDB (time-series) + PostGIS (network geometry)       │
│                 Redis (live state, pub/sub) │ MinIO (waveforms, photos)      │
├──────────────────────────────────────────────────────────────────────────────┤
│ L1  TRANSPORT   4G LTE Cat-1 (A7670C) │ Wi-Fi │ LoRaWAN IN865 → ChirpStack   │
│                 MQTT over TLS, store-and-forward on SD/flash                 │
├──────────────────────────────────────────────────────────────────────────────┤
│ L0  FIELD       ESP32 nodes: Sentinel │ Scout │ Quality │ Tank/Pump          │
│                 Edge DSP: filtering, CUSUM, transient trigger, GPS-PPS sync   │
│                 Integrations: existing utility meters via RS485 Modbus       │
└──────────────────────────────────────────────────────────────────────────────┘
```

## 2. Field layer: four node types

A single "do-everything" node is either too expensive or too weak, so SROT uses four specialised node types.

| Node | Where | Measures | Sampling | Power / link |
|---|---|---|---|---|
| **Sentinel (S)** | DMA inlets, trunk mains, pumping stations, major junctions | Pressure at **860 Hz** (ring buffer), flow, GPS-PPS time | Continuous; 1-min summaries; waveform upload on trigger | Mains or 20 W solar; 4G |
| **Scout (P)** | Spread through the network (tail ends, critical nodes) | Pressure | Every 1 s via the ESP32 ULP co-processor; wakes the main core when it sees an excursion; uploads 1/5/15-min stats | 2×18650 + 3 W solar; LoRa or 4G |
| **Quality (Q)** | Representative points, tail ends, after reservoirs | pH, TDS/EC, turbidity, temperature, ORP (optional) | Every 15–60 min through a flush-and-measure solenoid cycle | Solar/mains; 4G |
| **Tank/Pump (T)** | ESRs/OHTs, sumps, pump houses | Tank level (ultrasonic), pump kW/kWh (PZEM), suction/discharge pressure | 1 min | Mains; Wi-Fi/4G |

Utilities already own bulk flow meters at many inlets. Sentinels read them over **RS485 Modbus** (₹60 MAX485 module), so SROT doesn't have to buy a ₹40k electromagnetic meter.

### Edge firmware (ESP32, FreeRTOS tasks)

```text
 sampler_task   ADS1115 continuous @860 SPS (ALERT/RDY interrupt) → ring buffer (PSRAM, 30 s)
 dsp_task       median-of-3 → EWMA baseline → onset detector (dP/dt + CUSUM)
                 └─ on trigger: freeze 10 s pre + 20 s post, timestamp onset with GPS-PPS µs clock
 stats_task     1-min min/mean/max/std, pulse-count flow, pressure-cycle counter
 quality_task   power one probe at a time (MOSFET) → avoids pH/TDS electrical interference
 comms_task     MQTT/TLS publish; on failure → append to SD queue; replay when link returns
 health_task    battery, RSSI, temperature, self-test, flat-line/stuck detection
 ota_task       signed OTA firmware updates
```

The edge only catches the event and timestamps it precisely. All network-wide inference happens on the server.

## 3. Transport and messaging

MQTT topic scheme:

```text
srot/{utility}/{zone}/{node_id}/telemetry   # 1-min stats (JSON, QoS 1)
srot/{utility}/{zone}/{node_id}/event       # transient onset + metadata (QoS 1)
srot/{utility}/{zone}/{node_id}/waveform    # binary pressure trace, chunked (QoS 1)
srot/{utility}/{zone}/{node_id}/health      # battery, RSSI, faults
srot/{utility}/{zone}/{node_id}/cmd         # config, calibration, OTA (server → node)
```

Example telemetry payload:

```json
{ "ts": 1791273600, "seq": 48211,
  "p":  {"mean": 23.41, "min": 22.90, "max": 24.02, "std": 0.21, "unit": "m"},
  "q":  {"vol_l": 4813.0, "mean_lps": 80.2},
  "cyc": 3, "bat": 3.94, "rssi": -81, "fw": "0.4.2" }
```

LoRa nodes go through a LoRaWAN gateway → ChirpStack, which republishes to the same MQTT topics, so the backend sees a single format.

## 4. Data layer

**TimescaleDB + PostGIS in one Postgres** (Docker). Time-series data and pipe geometry live together, so a query like "pressure history for every pipe within 200 m of this complaint" stays in one SQL statement.

Core tables:

```text
network:   node(id, type, geom, elevation, zone)       pipe(id, from, to, geom LineString, length, dia,
           valve(id, pipe_id, chainage, state, type)         material, install_year, C_factor, wave_speed)
devices:   device(id, node_id, kind, fw, calib_json, installed_at)
           sensor(id, device_id, quantity, unit, offset, gain, accuracy)
timeseries measurement(ts, sensor_id, value)  ← hypertable, compressed after 7 d
           stats_1m / stats_1h continuous aggregates
events:    transient_event(id, device_id, onset_us, amplitude, waveform_uri)
analysis:  anomaly(id, type, zone, started, ended, residual_json, status)
           hypothesis(anomaly_id, pipe_id, chainage_lo, chainage_hi, posterior, est_loss_lph)
           risk_score(pipe_id, date, score, factors_json)
ops:       alert, work_order, field_outcome (ground truth), citizen_report, lab_sample
```

## 5. Intelligence layer: how a minute of data flows

```text
every 1 min   ingest → validate (range, rate-of-change, flat-line) → store → Redis live state
every 5 min   State estimator: WLS fit of zone demand multipliers to the measured heads/flows
              Residual r = z_measured − h(x̂)  →  CUSUM per sensor + network-level χ² test
on χ² alarm   Classifier compares r against signature library (leak, blockage, sensor fault, demand)
              → if leak-like: Bayesian localizer over pipe chainages (25 m virtual nodes)
on NPW event  Pair events from neighbouring sentinels within the wave-travel window
              → x = (L + a·Δt)/2 → becomes a sharp likelihood term in the Bayesian localizer
nightly       Water balance (IWA), MNF/EWF, leak-vs-theft split, C-factor recalibration,
              risk score update (fatigue damage accumulates), sensor drift check
weekly        Sensor-placement optimizer re-ranks "next best sensor locations"
on outcome    Field confirmation → update priors, recalibrate confidence, append ML label
```

All physics lives in `02-physics-engine.md`.

### Why WNTR/EPANET and not a custom solver

EPANET (US EPA, open source) is the standard tool for hydraulic simulation, and WNTR (Sandia/EPA) wraps it in Python. WNTR adds pressure-dependent demand and a leak model, and it can run water-quality and water-age simulations. A looped-network solver is a lot of work to write and verify, and utility engineers already know EPANET. The project's own code sits on top of it: estimation, localization, classification and decisions.

The plan is to validate on the BattLeDIM 2020 L-Town benchmark (782 junctions, 905 pipes, 33 real leak events, SCADA-like data). Published leak-localization methods report results on it, so the numbers can be compared directly.

## 6. API layer

```text
GET  /network/geojson?layer=pressure|risk|quality|age     map layers
GET  /pipes/{id}                                          pipe card (health, live vs expected, history)
GET  /anomalies?status=open                               incident list
GET  /anomalies/{id}                                      evidence: residuals, posterior curve, waveforms
POST /anomalies/{id}/workorder                            create job (includes isolation plan)
POST /workorders/{id}/outcome                             field ground truth (found? where? cause? photos)
GET  /balance?zone=&from=&to=                             IWA water balance, ILI, real vs apparent loss
GET  /supply/schedule?zone=                               supply windows + live supply status
POST /citizen/reports                                     citizen complaint (photo, GPS, type)
POST /sim/whatif                                          close valve / change PRV → predicted impact
POST /devices/{id}/commission                             bind node to junction, store calibration
WS   /live                                                pushes live readings + new alerts
```

Auth: phone-OTP login, JWT, roles `admin`, `engineer`, `operator`, `field`, `citizen`, all scoped per zone.

## 7. Alerting

| Tier | Examples | Channel | Escalation |
|---|---|---|---|
| **P1 critical** | Burst (NPW + flow step), contamination signal, intrusion during depressurization, pump trip | Push + SMS | Unacknowledged after 10 min → next person on the roster |
| **P2 high** | Persistent leak hypothesis, pressure out of band, chlorine below 0.2 mg/L | Push | Daily reminder |
| **P3 info** | Sensor drift, calibration due, battery low, new placement recommendation | In-app + daily digest | — |

Duplicate alerts are suppressed: all evidence for one physical event attaches to one **incident**, so a burst doesn't fire 15 alerts.

## 8. Security and reliability

- Per-device X.509 or username/password-plus-token credentials, MQTT over TLS, signed OTA firmware.
- Nodes buffer readings for **≥ 7 days** on SD. Each message has a sequence number, so the server spots gaps and backfills them.
- The server marks data as *stale* rather than *zero* when a node goes silent. Silence must never look like a leak.
- Every model output stores the model version and inputs, so any alert can be audited later.

## 9. Deployment

`docker compose up` brings up: `emqx`, `timescaledb(postgis)`, `redis`, `minio`, `api` (FastAPI), `worker` (physics/analytics, APScheduler or Celery), and `simulator`.

The **simulator** service runs WNTR on a network with injected leaks, bursts, blockages and sensor faults, and publishes **fake MQTT telemetry in exactly the node format**. The mobile app and the analytics can therefore be built and demoed before a single sensor is soldered.
