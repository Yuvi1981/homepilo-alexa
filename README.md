# HomeBrain — Goal-Driven Smart Home Agent Protocol

> **"One sentence to Alexa+. Whole house handled."**  
> *Amazon Developer Hackathon 2026 | Alexa+ Track • Goal-Driven Smart Home Agent Protocol*

HomeBrain translates compound natural-language human intentions into robust, secure, multi-step execution plans. By implementing a **Model Context Protocol (MCP)** server with 12 atomic and composite tools, HomeBrain bridges the gap between high-level voice intents and smart home hardware.

---

## 🌟 The Paradigm Shift

| Dimension | Today's Standard Alexa | HomeBrain Automated Alexa+ |
| :--- | :--- | :--- |
| **Execution Model** | **Command-Follower**: Executes isolated, literal single-intent phrases (e.g. *"Turn off living room light"*). | **Goal-Driven Orchestrator**: Translates high-level human objectives (*"I'm leaving for a week"*) into multi-step execution plans. |
| **Tool Discovery** | Relies on rigid, hardcoded vendor integrations and siloed APIs. | Uses dynamic, standardized **Model Context Protocol (MCP)** servers with 12 discoverable tools. |
| **User Friction** | Requires user to manually script routines beforehand or tap 5+ separate apps. | **Zero manual pre-scripting**: 1 natural sentence initiates complex device sequencing across lighting, HVAC, and security. |
| **Transparency & Trust** | Opaque execution; minimal feedback if a routine fails. | **Fully auditable activity logs**: Verification tools (`get_activity_log`, `get_home_status`) track every step with cryptographic checksums. |
| **Energy Impact** | High waste from forgotten heavy appliances. | **Model-based Energy Optimizer**: Calibrated at ₹8/kWh, saving ~₹255/week automatically. |

---

## 🛠️ MCP 12-Tool Architecture

The protocol exposes **12 tools** across 4 functional domains:

### 1. Control Domain (State Mutation Primitives)
- `set_device`: Switch power, dimming, or level on lights, plugs, appliances, and geysers.
- `set_lock`: Motorized deadbolt state mutation (locked/unlocked) with safety validation.
- `activate_scene`: Triggers coordinated presets (`night`, `away`, `movie`, `welcome`).
- `set_thermostat`: HVAC climate regulation (cool, heat, eco, off) and target temperatures.

### 2. Plan Domain (Composite Macro-Tools)
- `plan_vacation_mode`: **The core composite macro-tool**. Coordinates 8 sequential actions: cuts geyser, suspends HVAC, isolates phantom plugs, deadbolts 3 exterior doors, arms perimeter security, schedules randomized occupancy lighting, and estimates monetary savings.
- `schedule_task`: Schedules delayed or periodic automations (e.g. occupancy lighting routines).
- `cancel_scheduled_task`: Revokes pending scheduled tasks.

### 3. Insight Domain (Telemetry & Analytics)
- `get_energy_report`: Real-time load analysis, daily kWh, daily/weekly cost calibrated at ₹8.00/kWh.
- `suggest_energy_savings`: Identifies phantom loads, idle geysers, and AC inefficiencies with rupee figures.
- `simulate_savings_projection`: Models cumulative savings across trip lengths (1 wk = ₹255, 2 wk = ₹510, 3 wk = ₹766, 4 wk = ₹1,021).

### 4. Trust Domain (Verification & Audit)
- `get_home_status`: Diagnostic utility returning verified physical state of all devices, locks, sensors, power draw, and cryptographic verification hash.
- `get_activity_log`: Immutable, timestamped audit ledger tracking every tool call, caller, parameters, and outcome.

---

## 🚀 Quick Start Guide

### 1. Requirements
- Python 3.10+
- Modern Web Browser

### 2. Launch the Workable Backend & Web Console
```bash
python run.py
```
- **Web Dashboard**: [http://localhost:8000](http://localhost:8000)
- **Interactive REST API Docs (Swagger UI)**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **MCP Tool Definitions**: [http://localhost:8000/api/mcp/tools](http://localhost:8000/api/mcp/tools)

### 3. Run the Standalone Alexa+ Terminal MCP Client Demo
```bash
python run_demo.py
```
This plays the complete Alexa+ conversation, executes the 8-tool vacation sequence, displays the pre/post state diffs, and computes savings.

---

## 📡 REST API Reference

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/api/status` | Current home status, perimeter state, power, and trust hash |
| `GET` | `/api/devices` | List all 14 simulated devices and real-time wattage |
| `POST` | `/api/devices/{id}` | Mutate device state (`state: "on"\|"off"`, `level: 0..100`) |
| `GET` | `/api/locks` | List all deadbolts and check perimeter security |
| `POST` | `/api/locks/{id}` | Engage or release deadbolt (`locked: true\|false`) |
| `GET` | `/api/energy` | Energy report calibrated at ₹8/kWh |
| `GET` | `/api/energy/projection` | Cumulative savings projection curve |
| `GET` | `/api/logs` | Query immutable audit ledger with domain filtering |
| `GET` | `/api/mcp/tools` | Discover all 12 Model Context Protocol tools |
| `POST` | `/api/mcp/execute` | Directly invoke any MCP tool with parameters |
| `POST` | `/api/alexa/compile` | Compile natural-language goal into a multi-step plan |
| `POST` | `/api/alexa/execute` | Compile and execute goal plan with live step results |
| `POST` | `/api/state/reset` | Reset simulation to un-optimized baseline for repeated demos |

---

## 📊 Benchmark Savings Model (₹8/kWh)

Matching Hackathon Slide 9:
- **1 Week (7 Days)**: ₹255 saved (31.9 kWh)
- **2 Weeks (14 Days)**: ₹510 saved (63.8 kWh)
- **3 Weeks (21 Days)**: ₹766 saved (95.8 kWh)
- **4 Weeks (28 Days)**: ₹1,021 saved (127.6 kWh)

---

## 🛡️ Honest Scope Note
The home is simulated via JSON-backed state (`backend/data/home_state.json`) and savings are estimates from a calibrated power model at ₹8/kWh. The MCP interface is 100% real and tested end-to-end with an MCP client; live Alexa+ device and Matter integration is the natural next step.
