#!/usr/bin/env node
// SROT device emulator: speaks the same HTTP + WebSocket API as the ESP32 firmware
// (firmware/API.md), so the mobile app can be developed and demoed without hardware.
// No dependencies: Node 18+.
//
//   node devsim/device-emulator.mjs                       # 2 sentinels + quality + tank
//   node devsim/device-emulator.mjs --devices sentinel,scout --base-port 9100
//
// Each device listens on HTTP port P and WebSocket port P+1. Sentinel A and B sit at the
// two ends of one 600 m uPVC main; a simulated burst at a random point produces events
// whose GPS-timed onsets differ by exactly (x/a − (L−x)/a), so the app's two-sensor
// localization can be checked against the printed truth.

import crypto from 'node:crypto';
import http from 'node:http';
import os from 'node:os';

const args = Object.fromEntries(
  process.argv.slice(2).reduce((acc, a, i, arr) => {
    if (a.startsWith('--')) acc.push([a.slice(2), arr[i + 1]?.startsWith('--') ? 'true' : arr[i + 1] ?? 'true']);
    return acc;
  }, []),
);
const ROLES = (args.devices ?? 'sentinel,sentinel,quality,tank').split(',');
const BASE_PORT = Number(args['base-port'] ?? 9000);
const PIPE_L = Number(args['pipe-length'] ?? 600);    // m between sentinel A and B
const WAVE_A = Number(args['wave-speed'] ?? 370);     // m/s (uPVC)
const AUTO_BURST_S = Number(args['auto-burst'] ?? 120);

const gauss = () => {
  let s = 0;
  for (let i = 0; i < 4; i++) s += Math.random();
  return (s - 2) * 1.732;
};
const nowUs = () => Date.now() * 1000;
const r = (v, d = 3) => (v == null || !isFinite(v) ? null : Math.round(v * 10 ** d) / 10 ** d);

// ---------------------------------------------------------------- shared "network" state
const burst = { active: false, t0Us: 0, x: 0 };   // burst onset at the source, position from A

function triggerBurst(x = Math.random() * PIPE_L) {
  burst.active = true;
  burst.t0Us = nowUs() + 200000;   // a moment in the future so both sides see the full wave
  burst.x = x;
  const sentinels = devices.filter((d) => d.role === 'sentinel');
  const tA = burst.t0Us + (x / WAVE_A) * 1e6;
  const tB = burst.t0Us + ((PIPE_L - x) / WAVE_A) * 1e6;
  if (sentinels[0]) sentinels[0].scheduleEvent(tA, 3.5);
  if (sentinels[1]) sentinels[1].scheduleEvent(tB, 3.5 * 0.85);   // a little attenuation
  console.log(
    `[burst] x = ${x.toFixed(1)} m from ${sentinels[0]?.name ?? 'A'} (L = ${PIPE_L} m, a = ${WAVE_A} m/s) ` +
      `Δt(A−B) = ${((tA - tB) / 1000).toFixed(3)} ms`,
  );
  setTimeout(() => (burst.active = false), 75000);
}

// ---------------------------------------------------------------- device model
class Device {
  constructor(index, role) {
    this.index = index;
    this.role = role;
    this.port = BASE_PORT + index * 2;
    this.wsPort = this.port + 1;
    this.id = `srot-emu${String(index).padStart(3, '0')}`;
    const n = devices.filter((d) => d.role === role).length;
    const DEMO_NAMES = {
      sentinel: ['Gandhi Nagar main line', 'Station Road main line'],
      scout: ['Ward 12 tail end', 'Ward 14 tail end'],
      quality: ['Ward 12 water quality'],
      tank: ['Ward 12 overhead tank'],
    };
    this.name = DEMO_NAMES[role]?.[n] ?? `${role} ${n + 1}`;
    this.boot = Date.now();
    this.sps = role === 'sentinel' ? 860 : role === 'scout' ? 128 : 128;
    this.cfg = {
      name: this.name, role, sim: true, wifiSsid: 'EmuNet', serverUrl: '', junction: role === 'sentinel' ? `J${10 + index}` : '',
      p1RangeMPa: 0.5, p2RangeMPa: 0.5, p1Gain: 1, p1Offset: 0, p2Gain: 1, p2Offset: 0, flowK1: 450, flowK2: 450,
      trigHeadM: 1.5, qualityIntervalS: 30, flushS: 20, ph7V: 2.5, ph4V: 3.05, phBufHigh: 7, phBufLow: 4,
      turbClearV: 4.2, tdsK: 1, tankSensorToBottomM: 2, tankFullLevelM: 1.8, tankAreaM2: 1, uplinkIntervalS: 10,
    };
    this.events = [];          // newest first, with waveform
    this.pendingOnsets = [];   // {onsetUs, amp}
    this.nextEventId = 1;
    this.tot1 = 0;
    this.tot2 = 0;
    this.kwh = 0;
    this.q = { ph: null, tds: null, ec: null, ntu: null, ts: 0, stage: 'idle', ok: true };
    this.lastQ = 0;
    this.clients = new Set();
    this.lastDisplayUs = nowUs();
    this.flowCal = { 1: 0, 2: 0 };
    this.pulses = { 1: 0, 2: 0 };
  }

  // Burst seen by this sensor: drop at onset, damped water-hammer ringing, partial recovery.
  burstDev(tUs) {
    let dev = 0;
    for (const p of this.pendingOnsets) {
      if (tUs < p.onsetUs) continue;
      const dt = (tUs - p.onsetUs) / 1e6;
      let residual = 0.35;
      if (dt > 20) residual *= Math.exp(-(dt - 20) / 10);
      dev += -p.amp * (residual + 0.65 * Math.exp(-dt / 0.6) * Math.cos(2 * Math.PI * 6 * dt));
    }
    return dev;
  }

  baseHead(tUs) {
    const s = tUs / 1e6;
    const offset = this.role === 'sentinel' && this.index > 0 ? -2.1 : 0;
    return 24 + offset + 1.2 * Math.sin((2 * Math.PI * s) / 300);
  }

  head(tUs) {
    return this.baseHead(tUs) + this.burstDev(tUs) + 0.03 * gauss();
  }

  leakFraction() {
    const t = nowUs();
    return this.pendingOnsets.some((p) => t >= p.onsetUs && t - p.onsetUs < 70e6) ? 1 : 0;
  }

  scheduleEvent(onsetUs, amp) {
    this.pendingOnsets.push({ onsetUs, amp });
    // Capture completes 2.5 s after onset, like the firmware.
    setTimeout(() => this.captureEvent(onsetUs, amp), (onsetUs - nowUs()) / 1000 + 2600);
    setTimeout(() => (this.pendingOnsets = this.pendingOnsets.filter((p) => p.onsetUs !== onsetUs)), 80000);
  }

  captureEvent(onsetUs, amp) {
    const dtUs = 1e6 / this.sps;
    // Real sampling instants do not line up with the onset: random phase.
    const startUs = onsetUs - 1.5e6 + Math.random() * dtUs;
    const n = Math.round(4 * this.sps);
    const h = [];
    for (let i = 0; i < n; i++) h.push(this.head(startUs + i * dtUs));
    const base = this.baseHead(onsetUs);
    let peak = 0;
    for (const v of h) if (Math.abs(v - base) > Math.abs(peak)) peak = v - base;
    // Same onset picker as the firmware: 10 % of peak, linear interpolation.
    const lvl = 0.1 * Math.abs(peak);
    let pi = h.findIndex((v) => Math.abs(v - base) === Math.abs(peak));
    let i0 = pi;
    while (i0 > 0 && Math.abs(h[i0] - base) > lvl) i0--;
    const d0 = Math.abs(h[i0] - base), d1 = Math.abs(h[i0 + 1] - base);
    const frac = d1 > d0 ? Math.min(1, Math.max(0, (lvl - d0) / (d1 - d0))) : 0;
    const onsetEst = startUs + (i0 + frac) * dtUs;
    const ev = {
      eid: this.nextEventId++, dev: this.id, onsetUtcUs: Math.round(onsetEst), startUtcUs: Math.round(startUs),
      timeSrc: 'gps', baseM: r(base), ampM: r(peak), sps: this.sps, n, onsetIdx: i0,
      onsetOffsetUs: Math.round(onsetEst - startUs), h,
    };
    this.events.unshift(ev);
    this.events = this.events.slice(0, 16);
    console.log(`[${this.name}] event #${ev.eid} amp ${ev.ampM} m onset err ${((onsetEst - onsetUs)).toFixed(0)} µs`);
    this.broadcast({ type: 'event', event: this.meta(ev) });
  }

  meta(ev) {
    const { h, ...m } = ev;
    return m;
  }

  info() {
    return {
      id: this.id, name: this.cfg.name, fw: '0.1.0-emu', role: this.cfg.role, sim: true, mac: `EM:00:00:00:00:${String(this.index).padStart(2, '0')}`,
      ip: lanIp(), ssid: 'EmuNet', rssi: -55 - this.index, ap: false, apSsid: `SROT-emu${this.index}`,
      up: Math.round((Date.now() - this.boot) / 1000), time: 'gps', sps: this.sps, wsPort: this.wsPort,
      junction: this.cfg.junction, server: this.cfg.serverUrl, heap: 182000, gaps: 0,
      sensors: { ads1: true, ads2: true, rtc: true, ds18b20: true, sd: false, gpsPps: true },
      ...(this.cfg.lat != null ? { lat: this.cfg.lat, lon: this.cfg.lon } : {}),
    };
  }

  live() {
    const t = nowUs();
    const role = this.cfg.role;
    const h1 = this.head(t);
    const L = {
      id: this.id, ts: Math.round(t / 1000), up: Math.round((Date.now() - this.boot) / 1000), role, sim: true, sps: this.sps,
      p1: { h: r(h1), bar: r(h1 * 0.0980665, 4), ok: role !== 'quality' },
      p2: { h: r(h1 - 2.1 + 0.03 * gauss()), bar: r((h1 - 2.1) * 0.0980665, 4), ok: role === 'sentinel' || role === 'scout' },
      t: r(28 + 0.3 * Math.sin(Date.now() / 600000) + 0.02 * gauss(), 2),
      vbus: 5.01, vbat: r(12.6 + 0.05 * gauss(), 2), rssi: -55 - this.index, time: 'gps',
      gps: { fix: true, sats: 9, pps: Math.round((Date.now() - this.boot) / 1000), lat: 23.2599 + this.index * 0.001, lon: 77.4126 },
      ev: this.events[0]?.eid ?? 0,
    };
    if (role === 'sentinel' || role === 'scout') {
      const q1 = 80 + 1.5 * gauss() + 8 * this.leakFraction();
      const q2 = 78 + 1.5 * gauss();
      L.f1 = { lpm: r(q1, 2), tot: r(this.tot1, 1), ok: true };
      L.f2 = { lpm: r(q2, 2), tot: r(this.tot2, 1), ok: true };
    }
    if (role === 'quality') L.q = { ...this.q };
    if (role === 'tank') {
      const s = Date.now() / 1000;
      const lvl = 0.9 + 0.7 * Math.sin((2 * Math.PI * s) / 900);
      const filling = Math.cos((2 * Math.PI * s) / 900) > 0;
      const kw = filling ? 0.75 + 0.01 * gauss() : 0;
      L.tank = {
        lvl: r(lvl), pct: r((100 * lvl) / this.cfg.tankFullLevelM, 1), vol: r(lvl * this.cfg.tankAreaM2),
        v: r(231 + gauss(), 1), a: r((kw * 1000) / (231 * 0.85), 2), kw: r(kw), kwh: r(this.kwh), pf: filling ? 0.85 : 0,
        lvlOk: true, pzemOk: true,
      };
    }
    return L;
  }

  tick1s() {
    const L = this.live();
    if (L.f1) {
      this.tot1 += L.f1.lpm / 60;
      this.tot2 += L.f2.lpm / 60;
      this.pulses[1] += Math.round((L.f1.lpm / 60) * this.cfg.flowK1);
      this.pulses[2] += Math.round((L.f2.lpm / 60) * this.cfg.flowK2);
    }
    if (L.tank) this.kwh += L.tank.kw / 3600;
    if (this.cfg.role === 'quality' && Date.now() - this.lastQ > this.cfg.qualityIntervalS * 1000) this.runQuality();
  }

  runQuality() {
    this.lastQ = Date.now();
    const stages = ['flush', 'settle', 'turbidity', 'tds', 'ph'];
    stages.forEach((s, i) => setTimeout(() => (this.q.stage = s), i * 600));
    setTimeout(() => {
      const flush = Math.random() < 0.08;
      const tds = 310 + 5 * gauss();
      this.q = {
        ph: r(7.25 + 0.04 * gauss(), 2), tds: r(tds, 0), ec: r(tds * 2, 0),
        ntu: r(flush ? 1.5 + 2.5 * Math.random() : Math.abs(0.6 + 0.2 * gauss()), 2), ts: Date.now(), stage: 'idle', ok: true,
      };
    }, stages.length * 600);
  }

  displayFrame() {
    const now = nowUs();
    const w = [];
    for (let t = this.lastDisplayUs + 20000; t <= now; t += 20000) w.push(r(this.head(t)));
    this.lastDisplayUs += w.length * 20000;
    return w;
  }

  broadcast(obj) {
    const s = JSON.stringify(obj);
    for (const c of this.clients) wsSend(c, s);
  }

  // ---------------------------------------------------------------- HTTP API
  async handle(req, res) {
    const url = new URL(req.url, 'http://x');
    const body = req.method === 'POST' ? await readJson(req) : {};
    const send = (code, obj) => {
      res.writeHead(code, { 'Content-Type': 'application/json', ...CORS });
      res.end(JSON.stringify(obj));
    };
    if (req.method === 'OPTIONS') return res.writeHead(204, CORS).end();
    const p = url.pathname;
    switch (`${req.method} ${p}`) {
      case 'GET /': return res.writeHead(200, { 'Content-Type': 'text/plain' }).end(`SROT emulator ${this.id}`);
      case 'GET /api/info': return send(200, this.info());
      case 'GET /api/live': return send(200, this.live());
      case 'GET /api/config': { const { ...c } = this.cfg; return send(200, c); }
      case 'POST /api/config': {
        const restart = (body.role && body.role !== this.cfg.role) || (body.sim != null && body.sim !== this.cfg.sim);
        Object.assign(this.cfg, body);
        this.cfg.sim = true;
        if (body.role) this.role = body.role;
        return send(200, { ok: true, restart: !!restart });
      }
      case 'GET /api/scan': return send(200, { networks: [{ ssid: 'EmuNet', rssi: -48, secure: true }, { ssid: 'JalBoard-Office', rssi: -67, secure: true }] });
      case 'POST /api/wifi': return send(200, { ok: true });
      case 'GET /api/wifi/status': return send(200, { state: 'connected', ip: lanIp(), ssid: 'EmuNet', rssi: -55, ap: false });
      case 'POST /api/wifi/forget': return send(200, { ok: true });
      case 'GET /api/events': return send(200, { events: this.events.map((e) => this.meta(e)) });
      case 'GET /api/event': {
        const ev = this.events.find((e) => e.eid === Number(url.searchParams.get('id')));
        if (!ev) return send(404, { ok: false, error: 'no such event' });
        const decim = Math.max(1, Number(url.searchParams.get('decim') ?? 1));
        return send(200, { ...this.meta(ev), decim, h: ev.h.filter((_, i) => i % decim === 0).map((v) => r(v)) });
      }
      case 'POST /api/cal/pressure-zero': return send(200, { ok: true, offset: r(-0.12 + 0.02 * gauss()) });
      case 'POST /api/cal/pressure-ref': return send(200, { ok: true, gain: r(1 + 0.01 * gauss(), 4), offset: -0.12 });
      case 'POST /api/cal/ph': await sleep(2000); return send(200, { ok: true, volts: body.buffer > 5.5 ? 2.5 : 3.05, ph7V: 2.5, ph4V: 3.05 });
      case 'POST /api/cal/turbidity-clear': return send(200, { ok: true, volts: 4.19 });
      case 'POST /api/cal/flow/start': this.flowCal[body.ch ?? 1] = this.pulses[body.ch ?? 1]; return send(200, { ok: true });
      case 'POST /api/cal/flow/finish': {
        const ch = body.ch ?? 1;
        const pulses = this.pulses[ch] - this.flowCal[ch];
        if (pulses < 10 || !(body.litres > 0)) return send(409, { ok: false, error: 'not enough pulses counted (need > 10) or litres missing' });
        const k = pulses / body.litres;
        this.cfg[ch === 1 ? 'flowK1' : 'flowK2'] = k;
        return send(200, { ok: true, k, pulses });
      }
      case 'POST /api/quality/run': this.runQuality(); return send(200, { ok: true });
      case 'POST /api/sim/burst': triggerBurst(); return send(200, { ok: true });
      case 'POST /api/reboot': this.boot = Date.now(); return send(200, { ok: true });
      default: return send(404, { ok: false, error: 'not found' });
    }
  }

  start() {
    http.createServer((req, res) => this.handle(req, res).catch((e) => res.writeHead(500).end(String(e)))).listen(this.port, '0.0.0.0');
    const wsServer = http.createServer((req, res) => res.writeHead(426).end());
    wsServer.on('upgrade', (req, socket) => {
      const key = req.headers['sec-websocket-key'];
      if (!key) return socket.destroy();
      const accept = crypto.createHash('sha1').update(key + '258EAFA5-E914-47DA-95CA-C5AB0DC85B11').digest('base64');
      socket.write(`HTTP/1.1 101 Switching Protocols\r\nUpgrade: websocket\r\nConnection: Upgrade\r\nSec-WebSocket-Accept: ${accept}\r\n\r\n`);
      this.clients.add(socket);
      wsSend(socket, JSON.stringify({ type: 'hello', info: this.info() }));
      socket.on('data', (buf) => {
        const op = buf[0] & 0x0f;
        if (op === 0x8) socket.end();
        if (op === 0x9) socket.write(Buffer.from([0x8a, 0x00]));
      });
      const drop = () => this.clients.delete(socket);
      socket.on('close', drop);
      socket.on('error', drop);
    });
    wsServer.listen(this.wsPort, '0.0.0.0');
    setInterval(() => this.tick1s(), 1000);
    setInterval(() => {
      if (this.clients.size === 0) {
        this.lastDisplayUs = nowUs();
        return;
      }
      this.broadcast({ type: 'live', ...this.live(), w: this.displayFrame() });
    }, 200);
  }
}

// ---------------------------------------------------------------- helpers
const CORS = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Methods': 'GET,POST,OPTIONS',
  'Access-Control-Allow-Headers': 'Content-Type',
};
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

function readJson(req) {
  return new Promise((resolve) => {
    let s = '';
    req.on('data', (c) => (s += c));
    req.on('end', () => {
      try {
        resolve(s ? JSON.parse(s) : {});
      } catch {
        resolve({});
      }
    });
  });
}

function wsSend(socket, text) {
  const payload = Buffer.from(text);
  let header;
  if (payload.length < 126) header = Buffer.from([0x81, payload.length]);
  else if (payload.length < 65536) {
    header = Buffer.alloc(4);
    header[0] = 0x81;
    header[1] = 126;
    header.writeUInt16BE(payload.length, 2);
  } else {
    header = Buffer.alloc(10);
    header[0] = 0x81;
    header[1] = 127;
    header.writeBigUInt64BE(BigInt(payload.length), 2);
  }
  if (!socket.destroyed) socket.write(Buffer.concat([header, payload]));
}

function lanIp() {
  for (const list of Object.values(os.networkInterfaces())) {
    for (const a of list ?? []) if (a.family === 'IPv4' && !a.internal) return a.address;
  }
  return '127.0.0.1';
}

// ---------------------------------------------------------------- main
const devices = [];
ROLES.forEach((role, i) => {
  const d = new Device(i, role.trim());
  devices.push(d);
});
devices.forEach((d) => d.start());

console.log(`SROT emulator — ${devices.length} devices on ${lanIp()}`);
for (const d of devices) console.log(`  ${d.name.padEnd(14)} ${d.id}  http://${lanIp()}:${d.port}  (ws ${d.wsPort})  role=${d.role}`);
console.log(`In the app: Add → "Demo monitors on a PC" → enter ${lanIp()}   (phone on the same Wi-Fi)`);
if (AUTO_BURST_S > 0 && devices.some((d) => d.role === 'sentinel')) {
  setTimeout(function loop() {
    triggerBurst();
    setTimeout(loop, AUTO_BURST_S * 1000 * (0.75 + Math.random() * 0.5));
  }, 45000);
}
