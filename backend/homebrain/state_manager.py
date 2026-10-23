import json
import os
import hashlib
import uuid
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from .models import Device, Scene, ScheduledTask, ActivityLogEntry, EnergyReport

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
STATE_FILE = os.path.join(DATA_DIR, "home_state.json")
LOG_FILE = os.path.join(DATA_DIR, "activity_log.json")

def get_iso_now() -> str:
    return datetime.now(timezone.utc).isoformat()

def get_default_devices() -> Dict[str, Dict[str, Any]]:
    return {
        "geyser_master": {
            "id": "geyser_master",
            "name": "Master Bath Geyser (Water Heater)",
            "room": "Master Bathroom",
            "type": "geyser",
            "state": "on",
            "power_watts": 2000.0,
            "current_draw_watts": 2000.0,
            "attributes": {"capacity_liters": 25, "target_temp_c": 60, "is_high_draw": True}
        },
        "ac_bedroom": {
            "id": "ac_bedroom",
            "name": "Master Bedroom Inverter AC",
            "room": "Master Bedroom",
            "type": "hvac",
            "state": "on",
            "power_watts": 1400.0,
            "current_draw_watts": 1400.0,
            "attributes": {"mode": "cool", "target_temp_c": 22, "fan_speed": "auto", "is_high_draw": True}
        },
        "ac_living": {
            "id": "ac_living",
            "name": "Living Room Dual Inverter AC",
            "room": "Living Room",
            "type": "hvac",
            "state": "off",
            "power_watts": 1500.0,
            "current_draw_watts": 0.0,
            "attributes": {"mode": "off", "target_temp_c": 24, "fan_speed": "medium", "is_high_draw": True}
        },
        "light_living_main": {
            "id": "light_living_main",
            "name": "Living Room Ambient Ceiling",
            "room": "Living Room",
            "type": "light",
            "state": "on",
            "power_watts": 60.0,
            "current_draw_watts": 60.0,
            "attributes": {"brightness": 85, "color_temp_k": 3000, "supports_simulation": True}
        },
        "light_living_accent": {
            "id": "light_living_accent",
            "name": "Living Room Floor Lamp",
            "room": "Living Room",
            "type": "light",
            "state": "on",
            "power_watts": 25.0,
            "current_draw_watts": 25.0,
            "attributes": {"brightness": 70, "color_temp_k": 2700, "supports_simulation": True}
        },
        "light_kitchen": {
            "id": "light_kitchen",
            "name": "Kitchen Pendant Downlights",
            "room": "Kitchen",
            "type": "light",
            "state": "on",
            "power_watts": 45.0,
            "current_draw_watts": 45.0,
            "attributes": {"brightness": 100, "color_temp_k": 4000, "supports_simulation": False}
        },
        "light_bedroom": {
            "id": "light_bedroom",
            "name": "Bedroom Cove Light",
            "room": "Master Bedroom",
            "type": "light",
            "state": "off",
            "power_watts": 35.0,
            "current_draw_watts": 0.0,
            "attributes": {"brightness": 0, "color_temp_k": 2700, "supports_simulation": True}
        },
        "light_patio": {
            "id": "light_patio",
            "name": "Patio Security Floodlight",
            "room": "Exterior",
            "type": "light",
            "state": "off",
            "power_watts": 30.0,
            "current_draw_watts": 0.0,
            "attributes": {"brightness": 0, "color_temp_k": 5000, "supports_simulation": True}
        },
        "plug_entertainment": {
            "id": "plug_entertainment",
            "name": "Living Room Media Console (OLED + Audio)",
            "room": "Living Room",
            "type": "plug",
            "state": "on",
            "power_watts": 140.0,
            "current_draw_watts": 140.0,
            "attributes": {"connected_device": "OLED TV & Soundbar", "is_phantom_draw": True}
        },
        "plug_kitchen_appliances": {
            "id": "plug_kitchen_appliances",
            "name": "Kitchen Counter Plug (Microwave/Coffee)",
            "room": "Kitchen",
            "type": "plug",
            "state": "on",
            "power_watts": 50.0,
            "current_draw_watts": 50.0,
            "attributes": {"connected_device": "Espresso & Microwave Standby", "is_phantom_draw": True}
        },
        "lock_front_door": {
            "id": "lock_front_door",
            "name": "Main Entrance Deadbolt",
            "room": "Entryway",
            "type": "lock",
            "state": "locked",
            "power_watts": 2.0,
            "current_draw_watts": 0.5,
            "attributes": {"battery_pct": 94, "security_protocol": "Matter/Zigbee 3.0", "tamper_detected": False}
        },
        "lock_back_door": {
            "id": "lock_back_door",
            "name": "Back Patio Sliding Deadbolt",
            "room": "Patio",
            "type": "lock",
            "state": "unlocked",  # Critical security risk before vacation plan!
            "power_watts": 2.0,
            "current_draw_watts": 0.5,
            "attributes": {"battery_pct": 88, "security_protocol": "Matter/Zigbee 3.0", "tamper_detected": False}
        },
        "lock_garage": {
            "id": "lock_garage",
            "name": "Garage Side Entry Door",
            "room": "Garage",
            "type": "lock",
            "state": "unlocked",  # Critical security risk before vacation plan!
            "power_watts": 2.0,
            "current_draw_watts": 0.5,
            "attributes": {"battery_pct": 91, "security_protocol": "Matter/Zigbee 3.0", "tamper_detected": False}
        },
        "sensor_perimeter": {
            "id": "sensor_perimeter",
            "name": "Perimeter Security & Door Monitors",
            "room": "Whole Home",
            "type": "sensor",
            "state": "disarmed",
            "power_watts": 5.0,
            "current_draw_watts": 2.0,
            "attributes": {"armed_mode": "disarmed", "zone_status": "all_contacts_active"}
        }
    }

def get_default_scenes() -> Dict[str, Dict[str, Any]]:
    return {
        "away": {
            "id": "away",
            "name": "Away Mode",
            "description": "Shuts off all lights and sets ACs to eco mode.",
            "device_actions": [
                {"device_id": "light_living_main", "state": "off"},
                {"device_id": "light_living_accent", "state": "off"},
                {"device_id": "light_kitchen", "state": "off"},
                {"device_id": "light_bedroom", "state": "off"},
                {"device_id": "ac_bedroom", "state": "off"},
                {"device_id": "ac_living", "state": "off"}
            ]
        },
        "night": {
            "id": "night",
            "name": "Good Night Routine",
            "description": "Secures all deadbolts, turns off main areas, sets bedroom AC to 24°C.",
            "device_actions": [
                {"device_id": "light_living_main", "state": "off"},
                {"device_id": "light_living_accent", "state": "off"},
                {"device_id": "light_kitchen", "state": "off"},
                {"device_id": "lock_front_door", "state": "locked"},
                {"device_id": "lock_back_door", "state": "locked"},
                {"device_id": "lock_garage", "state": "locked"},
                {"device_id": "ac_bedroom", "state": "on", "attributes": {"target_temp_c": 24}}
            ]
        },
        "movie": {
            "id": "movie",
            "name": "Cinema Lounge",
            "description": "Dims living room lights to 20% warm, activates media console.",
            "device_actions": [
                {"device_id": "light_living_main", "state": "off"},
                {"device_id": "light_living_accent", "state": "on", "attributes": {"brightness": 20, "color_temp_k": 2200}},
                {"device_id": "plug_entertainment", "state": "on"}
            ]
        },
        "welcome": {
            "id": "welcome",
            "name": "Welcome Home",
            "description": "Unlocks front door, powers living lights to warm 75%, sets comfortable AC.",
            "device_actions": [
                {"device_id": "lock_front_door", "state": "unlocked"},
                {"device_id": "light_living_main", "state": "on", "attributes": {"brightness": 75}},
                {"device_id": "ac_living", "state": "on", "attributes": {"target_temp_c": 23}}
            ]
        }
    }

class StateManager:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(StateManager, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        os.makedirs(DATA_DIR, exist_ok=True)
        self.tariff_rate_inr = 8.0  # Rs 8/kWh as specified in PRD & slides
        self.vacation_mode = False
        self.vacation_metadata = {}
        self.scheduled_tasks: List[Dict[str, Any]] = []
        self._load_or_init_state()
        self._initialized = True

    def _load_or_init_state(self):
        if os.path.exists(STATE_FILE):
            try:
                with open(STATE_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.devices = {k: Device(**v) for k, v in data.get("devices", {}).items()}
                    self.scenes = {k: Scene(**v) for k, v in data.get("scenes", {}).items()}
                    self.vacation_mode = data.get("vacation_mode", False)
                    self.vacation_metadata = data.get("vacation_metadata", {})
                    self.scheduled_tasks = data.get("scheduled_tasks", [])
                    return
            except Exception as e:
                print(f"[StateManager] Warning loading state: {e}. Reverting to defaults.")
        
        self.reset_to_default(log_action=False)

    def save_state(self):
        data = {
            "home_name": "Skyline Smart Residence",
            "tariff_rate_inr": self.tariff_rate_inr,
            "vacation_mode": self.vacation_mode,
            "vacation_metadata": self.vacation_metadata,
            "scheduled_tasks": self.scheduled_tasks,
            "devices": {k: v.model_dump() for k, v in self.devices.items()},
            "scenes": {k: v.model_dump() for k, v in self.scenes.items()}
        }
        with open(STATE_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    def reset_to_default(self, log_action: bool = True):
        self.devices = {k: Device(**v) for k, v in get_default_devices().items()}
        self.scenes = {k: Scene(**v) for k, v in get_default_scenes().items()}
        self.vacation_mode = False
        self.vacation_metadata = {}
        self.scheduled_tasks = []
        self.save_state()

        if log_action:
            self.log_activity(
                initiator="System Simulator",
                tool_name="reset_state",
                domain="trust",
                action="Reset simulated smart home state to un-optimized default baseline",
                parameters={"status": "initial_unprepared_state"},
                result={"active_power_watts": self.get_total_live_power()},
                energy_impact="Baseline restored (~3,720W live draw)"
            )

    def log_activity(
        self,
        initiator: str,
        tool_name: str,
        domain: str,
        action: str,
        parameters: Dict[str, Any],
        result: Dict[str, Any],
        status: str = "success",
        energy_impact: Optional[str] = None,
        state_diff: Optional[Dict[str, Any]] = None
    ) -> ActivityLogEntry:
        entry_id = str(uuid.uuid4())[:8]
        timestamp = get_iso_now()
        
        # Calculate cryptographic hash for trust/audit integrity
        hash_seed = f"{entry_id}:{timestamp}:{tool_name}:{action}:{json.dumps(parameters, sort_keys=True)}"
        verification_hash = hashlib.sha256(hash_seed.encode("utf-8")).hexdigest()[:16]
        result_with_hash = {**result, "audit_hash": f"hb-v_{verification_hash}"}

        entry = ActivityLogEntry(
            id=entry_id,
            timestamp=timestamp,
            initiator=initiator,
            tool_name=tool_name,
            domain=domain,
            action=action,
            parameters=parameters,
            result=result_with_hash,
            status=status,
            energy_impact=energy_impact,
            state_diff=state_diff
        )

        logs = self.get_activity_logs(limit=100)
        logs.insert(0, entry.model_dump())
        
        # Persist to activity_log.json
        with open(LOG_FILE, "w", encoding="utf-8") as f:
            json.dump(logs[:200], f, indent=2)
            
        return entry

    def get_activity_logs(self, limit: int = 50, domain: Optional[str] = None) -> List[Dict[str, Any]]:
        if not os.path.exists(LOG_FILE):
            return []
        try:
            with open(LOG_FILE, "r", encoding="utf-8") as f:
                logs = json.load(f)
                if domain:
                    logs = [l for l in logs if l.get("domain", "").lower() == domain.lower()]
                return logs[:limit]
        except Exception:
            return []

    def get_device(self, device_id: str) -> Optional[Device]:
        return self.devices.get(device_id)

    def update_device_state(self, device_id: str, new_state: str, attributes: Optional[Dict[str, Any]] = None) -> Optional[Device]:
        device = self.devices.get(device_id)
        if not device:
            return None
        
        old_state = device.state
        device.state = new_state

        if attributes:
            device.attributes.update(attributes)

        # Recalculate power draw
        if device.type == "lock":
            device.current_draw_watts = 0.5
        elif device.state in ("off", "standby", "unlocked"):
            if device.state == "standby":
                device.current_draw_watts = device.power_watts * 0.15
            else:
                device.current_draw_watts = 0.0
        elif device.state in ("on", "locked"):
            # Check for dimming on lights
            if device.type == "light":
                brightness = device.attributes.get("brightness", 100)
                device.current_draw_watts = round((device.power_watts * (brightness / 100.0)), 1)
            else:
                device.current_draw_watts = device.power_watts

        self.save_state()
        return device

    def get_total_live_power(self) -> float:
        return round(sum(d.current_draw_watts for d in self.devices.values()), 1)

    def get_energy_report(self) -> EnergyReport:
        total_watts = self.get_total_live_power()
        active_count = sum(1 for d in self.devices.values() if d.current_draw_watts > 1.0)
        
        # Category breakdown
        category_draws: Dict[str, float] = {}
        room_draws: Dict[str, float] = {}
        top_consumers: List[Dict[str, Any]] = []

        for d in self.devices.values():
            category_draws[d.type] = category_draws.get(d.type, 0.0) + d.current_draw_watts
            room_draws[d.room] = room_draws.get(d.room, 0.0) + d.current_draw_watts
            if d.current_draw_watts > 0:
                top_consumers.append({
                    "device_id": d.id,
                    "name": d.name,
                    "room": d.room,
                    "watts": d.current_draw_watts,
                    "type": d.type
                })

        top_consumers.sort(key=lambda x: x["watts"], reverse=True)

        # Cost calculations calibrated at Rs 8.0 per kWh
        # Daily kWh assumes running at current average pattern over 24h
        daily_kwh = round((total_watts * 24.0) / 1000.0, 2)
        daily_cost = round(daily_kwh * self.tariff_rate_inr, 2)
        weekly_cost = round(daily_cost * 7.0, 2)
        monthly_cost = round(daily_cost * 30.0, 2)

        return EnergyReport(
            timestamp=get_iso_now(),
            tariff_rate_inr=self.tariff_rate_inr,
            total_live_watts=total_watts,
            active_device_count=active_count,
            daily_estimated_kwh=daily_kwh,
            daily_estimated_cost_inr=daily_cost,
            weekly_estimated_cost_inr=weekly_cost,
            monthly_estimated_cost_inr=monthly_cost,
            breakdown_by_category={k: round(v, 1) for k, v in category_draws.items()},
            breakdown_by_room={k: round(v, 1) for k, v in room_draws.items()},
            top_consumers=top_consumers[:5]
        )

# Global singleton
state_manager = StateManager()
