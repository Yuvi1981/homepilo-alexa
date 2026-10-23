import os
import sys
from typing import Dict, Any, Optional
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

# Add current and parent dir to sys.path so imports work cleanly
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

try:
    from backend.homebrain.models import GoalPlan
    from backend.homebrain.state_manager import state_manager
    from backend.homebrain.mcp_tools import MCP_TOOL_DEFINITIONS, HomeBrainToolEngine
    from backend.homebrain.goal_planner import GoalToPlanCompiler
except ImportError:
    from homebrain.models import GoalPlan
    from homebrain.state_manager import state_manager
    from homebrain.mcp_tools import MCP_TOOL_DEFINITIONS, HomeBrainToolEngine
    from homebrain.goal_planner import GoalToPlanCompiler

app = FastAPI(
    title="HomeBrain REST API & MCP Server",
    description="Goal-Driven Smart Home Agent Protocol for Alexa+ (Amazon Developer Hackathon 2026)",
    version="1.0.0"
)

# Enable CORS for local development and web frontends
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request payloads
class DeviceMutationRequest(BaseModel):
    state: str
    level: Optional[int] = None
    initiator: Optional[str] = "User (Web REST API)"

class LockMutationRequest(BaseModel):
    locked: bool
    initiator: Optional[str] = "User (Web REST API)"

class ThermostatMutationRequest(BaseModel):
    mode: str
    target_temp_c: Optional[int] = None
    initiator: Optional[str] = "User (Web REST API)"

class MCPExecuteRequest(BaseModel):
    tool_name: str
    parameters: Dict[str, Any] = {}
    initiator: Optional[str] = "Developer MCP Workbench"

class AlexaGoalRequest(BaseModel):
    goal: str
    initiator: Optional[str] = "Alexa+ Voice Agent"

class VacationPlanRequest(BaseModel):
    trip_duration_days: int = 7
    simulate_occupancy: bool = True
    initiator: Optional[str] = "Alexa+ Voice Agent"

# ================= REST API ENDPOINTS =================

@app.get("/api/status", summary="Trust: Real-time Home State & Security Perimeter")
def get_home_status():
    return HomeBrainToolEngine.get_home_status()

@app.get("/api/devices", summary="Control: List all smart devices")
def get_all_devices():
    return {
        "count": len(state_manager.devices),
        "total_watts": state_manager.get_total_live_power(),
        "devices": list(state_manager.devices.values())
    }

@app.get("/api/devices/{device_id}", summary="Control: Get individual device")
def get_device(device_id: str):
    dev = state_manager.get_device(device_id)
    if not dev:
        raise HTTPException(status_code=404, detail=f"Device '{device_id}' not found")
    return dev

@app.post("/api/devices/{device_id}", summary="Control: Mutate device state")
def mutate_device(device_id: str, req: DeviceMutationRequest):
    res = HomeBrainToolEngine.set_device(
        device_id=device_id,
        state=req.state,
        level=req.level,
        initiator=req.initiator or "User (Web REST API)"
    )
    if not res.get("success"):
        raise HTTPException(status_code=400, detail=res.get("error"))
    return res

@app.get("/api/locks", summary="Control: List all deadbolts")
def get_locks():
    locks = [d for d in state_manager.devices.values() if d.type == "lock"]
    all_locked = all(l.state == "locked" for l in locks)
    return {
        "all_locked": all_locked,
        "count": len(locks),
        "locks": locks
    }

@app.post("/api/locks/{lock_id}", summary="Control: Lock or unlock deadbolt")
def mutate_lock(lock_id: str, req: LockMutationRequest):
    res = HomeBrainToolEngine.set_lock(
        lock_id=lock_id,
        locked=req.locked,
        initiator=req.initiator or "User (Web REST API)"
    )
    if not res.get("success"):
        raise HTTPException(status_code=400, detail=res.get("error"))
    return res

@app.get("/api/scenes", summary="Control: Predefined lifestyle scenes")
def get_scenes():
    return {
        "scenes": list(state_manager.scenes.values())
    }

@app.post("/api/scenes/{scene_name}", summary="Control: Activate scene")
def trigger_scene(scene_name: str, initiator: Optional[str] = "User (Web REST API)"):
    res = HomeBrainToolEngine.activate_scene(scene_name, initiator=initiator)
    if not res.get("success"):
        raise HTTPException(status_code=400, detail=res.get("error"))
    return res

@app.post("/api/thermostat/{device_id}", summary="Control: Regulate HVAC setpoint")
def mutate_thermostat(device_id: str, req: ThermostatMutationRequest):
    res = HomeBrainToolEngine.set_thermostat(
        device_id=device_id,
        mode=req.mode,
        target_temp_c=req.target_temp_c,
        initiator=req.initiator or "User (Web REST API)"
    )
    if not res.get("success"):
        raise HTTPException(status_code=400, detail=res.get("error"))
    return res

@app.get("/api/energy", summary="Insight: Detailed energy report (Rs 8/kWh)")
def get_energy_report(tariff: float = Query(8.0, description="Tariff in Rs/kWh")):
    return HomeBrainToolEngine.get_energy_report(tariff_rate_inr=tariff)

@app.get("/api/energy/suggestions", summary="Insight: Energy saving opportunities")
def get_energy_suggestions():
    return HomeBrainToolEngine.suggest_energy_savings()

@app.get("/api/energy/projection", summary="Insight: Benchmark savings curve by trip length")
def get_savings_projection(days: int = Query(7, description="Duration in days")):
    return HomeBrainToolEngine.simulate_savings_projection(days=days)

@app.get("/api/logs", summary="Trust: Immutable agentic activity audit ledger")
def get_activity_logs(
    limit: int = Query(50, description="Max entries to return"),
    domain: Optional[str] = Query(None, description="Optional domain filter")
):
    return HomeBrainToolEngine.get_activity_log(limit=limit, domain=domain)

@app.get("/api/mcp/tools", summary="MCP Protocol: Discover 12 Tools")
def list_mcp_tools():
    return {
        "protocol": "Model Context Protocol (MCP) 2024-11-05",
        "tool_count": len(MCP_TOOL_DEFINITIONS),
        "domains": ["Control", "Plan", "Insight", "Trust"],
        "tools": [t.model_dump() for t in MCP_TOOL_DEFINITIONS]
    }

@app.post("/api/mcp/execute", summary="MCP Protocol: Direct Tool Execution Runner")
def execute_mcp_tool(req: MCPExecuteRequest):
    res = HomeBrainToolEngine.execute_tool(
        tool_name=req.tool_name,
        parameters=req.parameters,
        initiator=req.initiator or "Developer MCP Workbench"
    )
    return res

@app.post("/api/alexa/compile", summary="Alexa+ Goal-to-Plan Compilation")
def compile_alexa_goal(req: AlexaGoalRequest):
    plan = GoalToPlanCompiler.compile(req.goal)
    return plan.model_dump()

@app.post("/api/alexa/execute", summary="Alexa+ Compile & Execute Voice Goal")
def execute_alexa_goal(req: AlexaGoalRequest):
    plan = GoalToPlanCompiler.compile(req.goal)
    execution_result = GoalToPlanCompiler.execute_plan(plan, initiator=req.initiator or "Alexa+ Voice Agent")
    return execution_result

@app.post("/api/demo/run-vacation-demo", summary="Execute Hackathon PRD 8-Tool Vacation Demo")
def run_vacation_demo(req: VacationPlanRequest):
    res = HomeBrainToolEngine.plan_vacation_mode(
        trip_duration_days=req.trip_duration_days,
        simulate_occupancy=req.simulate_occupancy,
        initiator=req.initiator or "Alexa+ Voice Agent"
    )
    return res

@app.post("/api/state/reset", summary="Reset simulation to un-optimized baseline")
def reset_home_state():
    state_manager.reset_to_default(log_action=True)
    return {
        "success": True,
        "message": "Simulated home state reset to default baseline (un-optimized, doors unlocked, geyser active)",
        "status": HomeBrainToolEngine.get_home_status()
    }

# ================= STATIC FILES / FRONTEND =================
frontend_dir = os.path.join(parent_dir, "frontend")
if os.path.exists(frontend_dir):
    app.mount("/", StaticFiles(directory=frontend_dir, html=True), name="frontend")

if __name__ == "__main__":
    import uvicorn
    print("\n" + "="*60)
    print(" HomeBrain REST API & MCP Server Initializing...")
    print(" API Documentation: http://localhost:8000/docs")
    print(" Interactive Web Console: http://localhost:8000")
    print("="*60 + "\n")
    uvicorn.run("backend.server:app", host="127.0.0.1", port=8000, reload=True)
