from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field

class Device(BaseModel):
    id: str
    name: str
    room: str
    type: str  # light, lock, hvac, geyser, plug, sensor
    state: str  # "on", "off", "locked", "unlocked", "standby"
    power_watts: float = 0.0  # nominal active draw
    current_draw_watts: float = 0.0  # real-time draw
    attributes: Dict[str, Any] = Field(default_factory=dict)

class Scene(BaseModel):
    id: str
    name: str
    description: str
    device_actions: List[Dict[str, Any]]

class ScheduledTask(BaseModel):
    id: str
    name: str
    tool_name: str
    parameters: Dict[str, Any]
    trigger_time: str
    delay_seconds: int = 0
    status: str = "pending"  # pending, executed, cancelled

class ActivityLogEntry(BaseModel):
    id: str
    timestamp: str
    initiator: str
    tool_name: str
    domain: str  # control, plan, insight, trust
    action: str
    parameters: Dict[str, Any] = Field(default_factory=dict)
    result: Dict[str, Any] = Field(default_factory=dict)
    status: str = "success"  # success, warning, error
    energy_impact: Optional[str] = None
    state_diff: Optional[Dict[str, Any]] = None

class EnergyReport(BaseModel):
    timestamp: str
    tariff_rate_inr: float
    total_live_watts: float
    active_device_count: int
    daily_estimated_kwh: float
    daily_estimated_cost_inr: float
    weekly_estimated_cost_inr: float
    monthly_estimated_cost_inr: float
    breakdown_by_category: Dict[str, float]
    breakdown_by_room: Dict[str, float]
    top_consumers: List[Dict[str, Any]]

class PlannedStep(BaseModel):
    step_number: int
    tool_name: str
    domain: str
    description: str
    parameters: Dict[str, Any]
    expected_impact: str

class GoalPlan(BaseModel):
    goal: str
    summary: str
    steps: List[PlannedStep]
    estimated_daily_savings_inr: float
    estimated_trip_savings_inr: float
    trip_duration_days: int
    security_clearance: str

class MCPToolDefinition(BaseModel):
    name: str
    domain: str  # Control, Plan, Insight, Trust
    description: str
    parameters: Dict[str, Any]
    returns: Dict[str, Any]
