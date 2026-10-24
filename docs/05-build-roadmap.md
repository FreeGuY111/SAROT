# Build roadmap

## Target repository layout

This is the planned end state. Today the repository has `docs/`, `firmware/` (one image for all roles instead of the per-role projects below), `mobile/`, `devsim/` and `hardware/`; `backend/`, `networks/`, `rig/` and `docker-compose.yml` do not exist yet.

```text
srot
├─ docs/                      architecture & design (this folder)
├─ firmware/                  PlatformIO projects (ESP32 / ESP32-S3)
│  ├─ lib/srot_core/          sampling, ring buffer, CUSUM, NPW trigger, GPS-PPS clock, MQTT, SD queue
│  ├─ sentinel/  scout/  quality/  tank/
├─ backend/                   FastAPI + workers (Python 3.11)
│  ├─ api/                    REST + WebSocket
│  ├─ ingest/                 MQTT → TimescaleDB
│  ├─ engine/                 hydraulics (WNTR), estimator, localizer, npw, favad, balance, quality, risk, placement, isolation
│  ├─ simulator/              WNTR scenario runner → publishes fake node MQTT
│  └─ tests/
├─ mobile/                    React Native + Expo (TypeScript)
├─ networks/                  .inp models: test rig, demo town, L-Town
├─ rig/                       test-rig drawings, calibration logs
└─ docker-compose.yml         emqx, timescaledb+postgis, redis, minio, api, worker, simulator
```

## Build order: simulation first, hardware in parallel

Phases 3 and 4 are partly done: the firmware and a device-direct app exist, without the backend they were meant to feed.

| Phase | Deliverable | Done when |
|---|---|---|
| **0. Model** | `.inp` model of the test rig + a demo town network; WNTR scenarios (leak, burst, blockage, sensor fault, intermittent supply) | Scenarios run and export synthetic sensor data |
| **1. Backbone** | docker-compose stack, DB schema, MQTT ingest, simulator publishing realistic telemetry | Live synthetic data in TimescaleDB |
| **2. Engine v1** | State estimator, χ²/CUSUM detection, hypothesis competition, Bayesian localizer, FAVAD, water balance | On synthetic data: detects injected leaks, localizes the right pipe, separates sensor faults |
| **3. Hardware v1** *(parallel to 1–2)* | Scout + Sentinel firmware on the bench, ADS1115 at 860 SPS, GPS-PPS timestamps, MQTT | Real pressure on the dashboard; two nodes agree on time within 10 µs |
| **4. Mobile v1** | Operator: Pulse, Map, Incident detail; Field: Jobs, Outcome report, BLE commissioning | End-to-end: simulated leak → push alert → incident → work order → outcome |
| **5. Test rig** | Physical rig + NPW localization + quality node | Leak tap localized < 0.5 m; blockage and sensor fault classified correctly |
| **6. Engine v2** | NPW multilateration on the graph, EWF/intermittent mode, leak-vs-theft split, intrusion index, chlorine-age model, risk + fatigue, isolation planner, placement optimizer | Validated on BattLeDIM L-Town; metrics table published |
| **7. Citizen + polish** | Supply-arrival alerts, reports, Hindi UI, offline maps | Usable on a ₹8k Android phone without network |

## Demo storyline (5 minutes)

1. Map: the network is healthy, supply is ON in Zone A.
2. Open a leak tap on the rig → within seconds a **P1 burst** arrives. Incident shows *"Pipe R2, 4.6–5.3 m from S1"* (truth: 5.0 m), est. 9 L/min (bucket: 8.7 L/min).
3. Show the **why**: NPW waveforms from two nodes, the residual pattern, the posterior curve along the pipe.
4. Partly close the branch gate → *"Blockage, not leak"*. Unplug a sensor → *"Sensor fault, no dispatch"*.
5. Field mode: guided step test → mark found → localization error is logged → confidence calibration updates.
6. Citizen: *"Water arriving in your area in ~15 min"*.
7. Close with the numbers: node cost vs commercial loggers, L/day saved, ₹/year for a 10,000-connection town.
