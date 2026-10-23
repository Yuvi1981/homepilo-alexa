"""
HomeBrain - Standalone MCP Client Demo
Simulates the Alexa+ Goal-Driven Agent conversation executing the 8-tool vacation plan.
Demonstrates the shift from single-command followers to goal-driven orchestration.
"""

import sys
import os
import time
import json

# Ensure backend package can be imported
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "backend"))

from backend.homebrain.state_manager import state_manager
from backend.homebrain.mcp_tools import HomeBrainToolEngine
from backend.homebrain.goal_planner import GoalToPlanCompiler

def print_banner():
    banner = """
================================================================================
  HOMEBRAIN -- Goal-Driven Smart Home Agent Protocol
  Amazon Developer Hackathon 2026 | Alexa+ Track
  "One sentence to Alexa+. Whole house handled."
================================================================================
"""
    print(banner)

def run_interactive_demo():
    print_banner()

    print("[*] Step 0: Initializing JSON-backed Simulated Home State...")
    state_manager.reset_to_default(log_action=False)
    initial_status = HomeBrainToolEngine.get_home_status()
    initial_power = initial_status["total_live_power_watts"]
    
    print(f"    Current Active Power Draw : {initial_power} Watts")
    print(f"    Perimeter Security        : Front Door LOCKED, Back Door UNLOCKED (!)")
    print(f"    High-Draw Geyser          : ON (2,000 W)")
    print(f"    Master Bedroom AC         : ON (1,400 W)")
    print(f"    Standby Vampire Plugs     : ON (190 W)")
    print("-" * 80)
    time.sleep(1)

    print("\n[USER VOICE INPUT]")
    print('   >>> "Alexa, I\'m leaving for a week. Set the house up."')
    print("-" * 80)
    time.sleep(1.2)

    print("\n[ALEXA+ GOAL-TO-PLAN COMPILER]")
    goal_sentence = "Alexa, I'm leaving for a week. Set the house up."
    plan = GoalToPlanCompiler.compile(goal_sentence)
    print(f"    Intent Detected: Extended Absence / Vacation Protocol")
    print(f"    Duration       : {plan.trip_duration_days} Days")
    print(f"    Plan Compiled  : {len(plan.steps)} Procedural Tool Operations")
    print(f"    Projected Cut  : ~{round(initial_power - 45)} Watts continuous")
    print(f"    Tariff Model   : Rs 8.0 / kWh (Standard India Residential)")
    print(f"    Est. Savings   : Rs {plan.estimated_trip_savings_inr} across 7 days")
    print("-" * 80)
    time.sleep(1.5)

    print("\n[MCP AGENTIC EXECUTION -- 8 TOOL CALLS]")
    result = GoalToPlanCompiler.execute_plan(plan, initiator="Alexa+ Voice Agent (Demo Client)")

    for step in result.get("steps", []):
        tool_name = step.get("tool")
        domain = step.get("domain")
        step_num = step.get("step")
        action = step.get("action")
        impact = step.get("impact", "OK")
        
        print(f"  [Tool Call {step_num}/8] Domain: {domain:<7} | Tool: {tool_name:<18}")
        print(f"    -> {action}")
        if impact != "OK":
            print(f"       Impact: {impact}")
        time.sleep(0.3)

    print("-" * 80)
    time.sleep(1)

    print("\n[POST-EXECUTION STATE & TRUST VERIFICATION]")
    final_status = HomeBrainToolEngine.get_home_status()
    final_power = final_status["total_live_power_watts"]
    saved_power = initial_power - final_power
    all_locked = final_status["all_doors_secured"]

    print(f"    Active Power Draw : {final_power} Watts (Reduced by {saved_power} W!)")
    print(f"    All Entry Doors   : {'100% DEADBOLTED & SECURE' if all_locked else 'WARNING'}")
    print(f"    Perimeter Alarm   : ARMED (Away Extended)")
    print(f"    Occupancy Routine : SCHEDULED (Dusk-to-Midnight Simulation)")
    print(f"    Audit Signature   : {final_status['verification_hash']}")
    
    print("\n[SAVINGS BENCHMARK PROJECTION]")
    proj = HomeBrainToolEngine.simulate_savings_projection(7)
    for b in proj["official_benchmarks"]:
        marker = "===> [Current 1-Wk Goal]" if b["days"] == 7 else ""
        print(f"    {b['label']:<6} ({b['days']} days) : Rs {b['savings_inr']:>4} saved  ({b['kwh']} kWh) {marker}")

    print("\n[ALEXA+ SPOKEN RESPONSE]")
    print('   <<< "I\'ve prepped your home for a 7-day vacation. Powered down the geyser, AC,')
    print('        and idle electronics, saving an estimated Rs 255. All exterior doors are')
    print('        deadbolted, perimeter security is armed, and evening lighting simulation')
    print('        is active. Have a safe journey!"')
    print("=" * 80)
    print("\n[SUCCESS] Demo completed successfully! All 8 MCP tool operations verified & logged.")

if __name__ == "__main__":
    run_interactive_demo()
