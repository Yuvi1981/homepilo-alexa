/**
 * HomeBrain Web Application Logic
 * Implements Goal-to-Plan visualization, live device toggling,
 * MCP 12-tool workbench, and audit ledger tracking.
 */

document.addEventListener("DOMContentLoaded", () => {
  initApp();
});

let currentDevices = [];
let currentFilter = "all";
let mcpToolsList = [];

async function initApp() {
  setupNavigation();
  setupGoalOrchestrator();
  setupBenchmarkChart();
  setupModal();
  setupGlobalActions();

  // Initial load
  await refreshAll();

  // Auto-refresh periodically for live telemetry
  setInterval(refreshTelemetryAndDevices, 4000);
}

// Global Refresh
async function refreshAll() {
  try {
    await Promise.all([
      refreshTelemetryAndDevices(),
      loadMcpTools(),
      refreshAuditLogs()
    ]);
  } catch (err) {
    console.error("Error refreshing HomeBrain state:", err);
  }
}

// Navigation Tabs
function setupNavigation() {
  const tabs = document.querySelectorAll(".tab-btn");
  tabs.forEach(tab => {
    tab.addEventListener("click", () => {
      tabs.forEach(t => t.classList.remove("active"));
      tab.classList.add("active");

      const targetId = tab.dataset.tab;
      document.querySelectorAll(".tab-content").forEach(content => {
        content.classList.remove("active");
      });
      const activeContent = document.getElementById(targetId);
      if (activeContent) activeContent.classList.add("active");

      if (targetId === "tabAuditLedger") {
        refreshAuditLogs();
      }
    });
  });

  // Device Filter buttons
  const filterBtns = document.querySelectorAll(".pill-btn");
  filterBtns.forEach(btn => {
    btn.addEventListener("click", () => {
      filterBtns.forEach(b => b.classList.remove("active"));
      btn.classList.add("active");
      currentFilter = btn.dataset.filter;
      renderDevices(currentDevices);
    });
  });

  // Scene triggers
  const sceneBtns = document.querySelectorAll("[data-scene]");
  sceneBtns.forEach(btn => {
    btn.addEventListener("click", async () => {
      const sceneName = btn.dataset.scene;
      btn.disabled = true;
      try {
        await HomeBrainAPI.activateScene(sceneName);
        await refreshTelemetryAndDevices();
        await refreshAuditLogs();
      } catch (e) {
        alert("Failed to activate scene: " + e.message);
      } finally {
        btn.disabled = false;
      }
    });
  });
}

// Refresh Telemetry & Devices
async function refreshTelemetryAndDevices() {
  try {
    const status = await HomeBrainAPI.getStatus();
    const energy = await HomeBrainAPI.getEnergyReport();
    const devData = await HomeBrainAPI.getDevices();

    currentDevices = devData.devices || [];

    // Header pills
    const liveWatts = status.total_live_power_watts || 0;
    document.getElementById("hdrLivePower").textContent = `${liveWatts} W`;
    document.getElementById("txtLiveWatts").textContent = liveWatts.toLocaleString();
    
    // Power bar animation (based on 4000W max scale)
    const pct = Math.min(100, Math.max(2, Math.round((liveWatts / 4000) * 100)));
    const fillEl = document.getElementById("powerBarFill");
    if (fillEl) fillEl.style.width = `${pct}%`;

    // Security Pill
    const allLocked = status.all_doors_secured;
    const perimeterEl = document.getElementById("hdrPerimeter");
    const secDot = document.getElementById("dotSecurity");
    if (perimeterEl && secDot) {
      if (allLocked && status.perimeter_status === "armed") {
        perimeterEl.textContent = "Armed & Locked";
        secDot.className = "pulse-dot green";
      } else if (allLocked) {
        perimeterEl.textContent = "Doors Locked";
        secDot.className = "pulse-dot yellow";
      } else {
        perimeterEl.textContent = "Unsecured (!)";
        secDot.className = "pulse-dot red";
      }
    }

    // Vacation Mode Pill
    const modeEl = document.getElementById("hdrMode");
    if (modeEl) {
      modeEl.textContent = status.vacation_mode ? "Vacation (Extended)" : "Normal Residence";
    }

    // Daily Cost
    const dailyCostEl = document.getElementById("txtDailyCost");
    if (dailyCostEl && energy.daily_estimated_cost_inr !== undefined) {
      dailyCostEl.textContent = `₹${energy.daily_estimated_cost_inr}`;
    }

    // Security Items in Telemetry card
    updateSecurityCard(status.devices || {});

    // Verification Trust Hash
    const hashEl = document.getElementById("txtTrustHash");
    if (hashEl && status.verification_hash) {
      hashEl.textContent = status.verification_hash;
    }

    // Render device grid
    document.getElementById("countDevices").textContent = currentDevices.length;
    renderDevices(currentDevices);

  } catch (err) {
    console.warn("Could not refresh telemetry:", err);
  }
}

function updateSecurityCard(devMap) {
  const front = devMap["lock_front_door"] || {};
  const back = devMap["lock_back_door"] || {};
  const garage = devMap["lock_garage"] || {};
  const perimeter = devMap["sensor_perimeter"] || {};

  setSecStatus("secFrontDoor", front.state === "locked", "LOCKED", "UNLOCKED (!)");
  setSecStatus("secBackDoor", back.state === "locked", "LOCKED", "UNLOCKED (!)");
  setSecStatus("secGarageDoor", garage.state === "locked", "LOCKED", "UNLOCKED (!)");
  setSecStatus("secPerimeterAlarm", perimeter.state === "armed", "ARMED", "DISARMED");
}

function setSecStatus(elId, isSecure, goodText, badText) {
  const el = document.getElementById(elId);
  if (!el) return;
  if (isSecure) {
    el.className = "sec-status locked";
    el.textContent = goodText;
  } else {
    el.className = elId.includes("Alarm") ? "sec-status disarmed" : "sec-status unlocked";
    el.textContent = badText;
  }
}

// Render Devices Grid
function renderDevices(devices) {
  const container = document.getElementById("devicesGrid");
  if (!container) return;

  const filtered = devices.filter(d => {
    if (currentFilter === "all") return true;
    if (currentFilter === "heavy") return d.type === "geyser" || d.type === "hvac";
    if (currentFilter === "light") return d.type === "light";
    if (currentFilter === "lock") return d.type === "lock";
    if (currentFilter === "plug") return d.type === "plug";
    return true;
  });

  container.innerHTML = filtered.map(d => {
    const isOn = d.state === "on" || d.state === "locked" || d.state === "armed";
    const isLock = d.type === "lock";
    const isHighDraw = d.attributes?.is_high_draw;
    const isPhantom = d.attributes?.is_phantom_draw;

    return `
      <div class="device-card ${isOn ? 'on' : ''}" id="card_${d.id}">
        <div class="device-card-header">
          <div class="device-info">
            <h4>${escapeHtml(d.name)}</h4>
            <div class="device-room">${escapeHtml(d.room)} • <span style="text-transform: capitalize;">${d.type}</span></div>
          </div>
          <label class="switch">
            <input type="checkbox" ${isOn ? 'checked' : ''} onchange="handleDeviceToggle('${d.id}', '${d.type}', this.checked)">
            <span class="slider"></span>
          </label>
        </div>

        <div class="device-card-footer">
          <div class="device-wattage">
            ${isLock ? (d.state.toUpperCase()) : (d.current_draw_watts + ' W')}
          </div>
          ${isHighDraw ? '<span class="high-draw-badge">HIGH DRAW</span>' : ''}
          ${isPhantom ? '<span class="badge-mini" style="background: rgba(244,63,94,0.15); color: #fda4af;">PHANTOM LOAD</span>' : ''}
          ${d.type === 'hvac' && isOn ? `<span class="badge-mini neon">${d.attributes?.target_temp_c || 22}°C (${d.attributes?.mode || 'cool'})</span>` : ''}
        </div>
      </div>
    `;
  }).join("");
}

// Device Toggle Handler
window.handleDeviceToggle = async function(deviceId, deviceType, isChecked) {
  try {
    if (deviceType === "lock") {
      await HomeBrainAPI.mutateLock(deviceId, isChecked);
    } else {
      const newState = isChecked ? "on" : "off";
      await HomeBrainAPI.mutateDevice(deviceId, newState);
    }
    await refreshTelemetryAndDevices();
    await refreshAuditLogs();
  } catch (err) {
    alert("Error changing device state: " + err.message);
    await refreshTelemetryAndDevices();
  }
};

// Setup Goal Orchestrator & Preset Chips
function setupGoalOrchestrator() {
  const chips = document.querySelectorAll(".chip");
  const inputGoal = document.getElementById("inputGoal");
  const btnRun = document.getElementById("btnExecuteGoal");

  chips.forEach(chip => {
    chip.addEventListener("click", () => {
      chips.forEach(c => c.classList.remove("active-chip"));
      chip.classList.add("active-chip");
      inputGoal.value = chip.dataset.goal;
    });
  });

  window.handleCompileAndRun = function() {
    const input = document.getElementById("inputGoal");
    if (input) runGoalExecution(input.value.trim());
  };

  btnRun.addEventListener("click", () => {
    window.handleCompileAndRun();
  });
}

// Run Goal Execution with Stepper Animation
async function runGoalExecution(goalText) {
  if (!goalText) return;

  const micEl = document.getElementById("micIndicator");
  const btnRun = document.getElementById("btnExecuteGoal");
  const badgeStatus = document.getElementById("planBadgeStatus");
  const planTitle = document.getElementById("planTitle");
  const planSummary = document.getElementById("planSummaryText");
  const stepperGrid = document.getElementById("stepperGrid");
  const spokenEl = document.getElementById("alexaSpokenText");

  // Activate microphone animation
  if (micEl) micEl.classList.add("mic-active");
  btnRun.disabled = true;
  badgeStatus.className = "badge-status executing";
  badgeStatus.textContent = "COMPILING...";

  try {
    // 1. Compile Plan via REST API
    const plan = await HomeBrainAPI.compileAlexaGoal(goalText);

    planTitle.textContent = `${plan.steps.length}-Step Orchestration Plan`;
    planSummary.textContent = plan.summary;
    document.getElementById("planSavedWatts").textContent = `~3,720 W`;
    document.getElementById("planSavedMoney").textContent = `₹${plan.estimated_trip_savings_inr}`;
    document.getElementById("planDuration").textContent = `${plan.trip_duration_days} Days`;

    // Render skeleton steps
    stepperGrid.innerHTML = plan.steps.map((st, i) => `
      <div class="step-card" id="step_${st.step_number}">
        <div class="step-icon-col">${st.step_number}</div>
        <div class="step-body">
          <div class="step-meta">
            <span class="step-domain-tag ${st.domain.toLowerCase()}">${st.domain}</span>
            <span class="step-tool-name">${st.tool_name}</span>
          </div>
          <div class="step-desc">${escapeHtml(st.description)}</div>
          <div class="step-impact">${escapeHtml(st.expected_impact)}</div>
        </div>
      </div>
    `).join("");

    badgeStatus.textContent = "EXECUTING 8 MCP CALLS...";

    // 2. Execute Compiled Plan via REST API
    const execRes = await HomeBrainAPI.executeAlexaGoal(goalText);

    // Animate execution sequentially
    for (let i = 1; i <= plan.steps.length; i++) {
      const stepEl = document.getElementById(`step_${i}`);
      if (stepEl) {
        stepEl.classList.add("active");
        await delay(280);
        stepEl.classList.remove("active");
        stepEl.classList.add("completed");
        const iconCol = stepEl.querySelector(".step-icon-col");
        if (iconCol) iconCol.innerHTML = "✓";
      }
    }

    badgeStatus.className = "badge-status";
    badgeStatus.textContent = "EXECUTED & AUDITED";

    // Spoken response
    const tripDays = plan.trip_duration_days || 7;
    const savings = plan.estimated_trip_savings_inr || 255;
    spokenEl.textContent = `"I've prepped your home for ${tripDays} days. High-draw appliances and phantom loads are isolated, saving an estimated ₹${savings}. All exterior doors are deadbolted, perimeter sensors armed, and occupancy lighting simulation scheduled. Safe travels!"`;

    // Refresh state and audit ledger
    await refreshTelemetryAndDevices();
    await refreshAuditLogs();

  } catch (err) {
    alert("Goal execution error: " + err.message);
    badgeStatus.className = "badge-status";
    badgeStatus.textContent = "ERROR";
  } finally {
    if (micEl) micEl.classList.remove("mic-active");
    btnRun.disabled = false;
  }
}

// Benchmark Chart Interactive Clicks (Slide 9)
function setupBenchmarkChart() {
  const cols = document.querySelectorAll(".chart-col");
  const descEl = document.getElementById("txtBenchmarkDesc");

  const benchmarks = {
    7: { label: "1 Week", savings: 255, kwh: 31.9 },
    14: { label: "2 Weeks", savings: 510, kwh: 63.8 },
    21: { label: "3 Weeks", savings: 766, kwh: 95.8 },
    28: { label: "4 Weeks", savings: 1021, kwh: 127.6 }
  };

  cols.forEach(col => {
    col.addEventListener("click", () => {
      cols.forEach(c => c.classList.remove("active"));
      col.classList.add("active");
      const days = parseInt(col.dataset.days);
      const b = benchmarks[days];
      if (b && descEl) {
        descEl.innerHTML = `${b.label} Absence: <strong>₹${b.savings} saved</strong> (${b.kwh} kWh at ₹8/kWh)`;
      }
    });
  });

  const btnCustom = document.getElementById("btnTestProjection");
  if (btnCustom) {
    btnCustom.addEventListener("click", () => {
      openModal("Custom Trip Savings Projection", `
        <div style="display: flex; flex-direction: column; gap: 16px;">
          <label style="font-size: 0.9rem; color: var(--text-muted);">
            Select Planned Absence Duration: <strong id="lblSliderDays" style="color: var(--accent-neon); font-size: 1.1rem;">7 Days</strong>
          </label>
          <input type="range" id="rangeDays" min="1" max="45" value="7" style="width: 100%; accent-color: var(--accent-neon);">
          
          <div style="background: rgba(255,255,255,0.04); padding: 16px; border-radius: 8px; border: 1px solid var(--border-subtle);">
            <div style="font-size: 0.85rem; color: var(--text-muted); margin-bottom: 6px;">PROJECTED MONETARY BENEFIT</div>
            <div style="font-size: 2.2rem; font-family: var(--font-display); font-weight: 800; color: var(--accent-neon);" id="modalProjSavings">₹255</div>
            <div style="font-size: 0.85rem; color: var(--text-dim);" id="modalProjKwh">31.9 kWh power reduction @ ₹8/kWh</div>
          </div>
          
          <button class="btn btn-primary" onclick="applyCustomVacation(document.getElementById('rangeDays').value)">
            Apply & Execute Vacation Protocol for this Duration
          </button>
        </div>
      `);

      const slider = document.getElementById("rangeDays");
      if (slider) {
        slider.addEventListener("input", (e) => {
          const val = parseInt(e.target.value);
          document.getElementById("lblSliderDays").textContent = `${val} Days (${(val / 7).toFixed(1)} wks)`;
          const savedInr = Math.round(val * (255 / 7));
          const savedKwh = (savedInr / 8.0).toFixed(1);
          document.getElementById("modalProjSavings").textContent = `₹${savedInr}`;
          document.getElementById("modalProjKwh").textContent = `${savedKwh} kWh power reduction @ ₹8/kWh`;
        });
      }
    });
  }
}

window.applyCustomVacation = async function(days) {
  closeModal();
  const inputGoal = document.getElementById("inputGoal");
  if (inputGoal) {
    inputGoal.value = `Alexa, I'm leaving for ${days} days. Set the house up.`;
    runGoalExecution(inputGoal.value);
  }
};

// Load MCP 12 Tools
async function loadMcpTools() {
  try {
    const data = await HomeBrainAPI.getMcpTools();
    mcpToolsList = data.tools || [];
    const container = document.getElementById("mcpToolsGrid");
    if (!container) return;

    container.innerHTML = mcpToolsList.map(t => `
      <div class="mcp-tool-card">
        <div>
          <div class="mcp-tool-header">
            <span class="mcp-tool-name">${escapeHtml(t.name)}</span>
            <span class="dom-tag ${t.domain.toLowerCase()}">${t.domain}</span>
          </div>
          <div class="mcp-tool-desc">${escapeHtml(t.description)}</div>
        </div>
        <div class="mcp-tool-footer">
          <span style="font-size: 0.72rem; color: var(--text-dim); font-family: var(--font-mono);">JSON-RPC 2.0</span>
          <button class="btn btn-outline btn-sm" onclick="openToolRunnerModal('${t.name}')">Run Tool</button>
        </div>
      </div>
    `).join("");
  } catch (err) {
    console.warn("Could not load MCP tools:", err);
  }
}

window.openToolRunnerModal = function(toolName) {
  const tool = mcpToolsList.find(t => t.name === toolName);
  if (!tool) return;

  const defaultParams = getDefaultParamsForTool(toolName);

  openModal(`MCP Tool Runner: ${toolName}`, `
    <div style="display: flex; flex-direction: column; gap: 14px;">
      <p style="font-size: 0.85rem; color: var(--text-muted);">${escapeHtml(tool.description)}</p>
      
      <div>
        <label style="font-size: 0.78rem; font-weight: 600; color: var(--text-muted); display: block; margin-bottom: 6px;">
          PARAMETERS (JSON Schema):
        </label>
        <textarea id="txtToolParams" rows="6" style="width: 100%; background: #070b12; border: 1px solid var(--border-subtle); border-radius: 6px; color: var(--accent-neon); font-family: var(--font-mono); padding: 10px; font-size: 0.82rem;">${JSON.stringify(defaultParams, null, 2)}</textarea>
      </div>

      <button class="btn btn-primary" id="btnExecuteSingleTool" onclick="executeSingleToolModal('${toolName}')">
        Execute Tool via MCP Dispatch
      </button>

      <div id="toolExecutionOutput" style="display: none; margin-top: 10px;">
        <label style="font-size: 0.78rem; font-weight: 600; color: var(--text-muted); display: block; margin-bottom: 6px;">
          RESPONSE (Standard MCP Content):
        </label>
        <pre id="preToolResp" style="background: #070b12; border: 1px solid rgba(0,245,155,0.3); border-radius: 6px; padding: 12px; font-size: 0.8rem; color: #a7f3d0; max-height: 200px; overflow-y: auto;"></pre>
      </div>
    </div>
  `);
};

function getDefaultParamsForTool(toolName) {
  switch(toolName) {
    case "set_device": return { device_id: "geyser_master", state: "off" };
    case "set_lock": return { lock_id: "lock_back_door", locked: true };
    case "activate_scene": return { scene_name: "night" };
    case "set_thermostat": return { device_id: "ac_bedroom", mode: "off" };
    case "plan_vacation_mode": return { trip_duration_days: 7, simulate_occupancy: true };
    case "schedule_task": return { task_name: "Custom Routine", delay_seconds: 3600, tool_name: "set_device", parameters: { device_id: "light_living_main", state: "off" } };
    case "cancel_scheduled_task": return { task_id: "task_123" };
    case "get_energy_report": return { tariff_rate_inr: 8.0 };
    case "suggest_energy_savings": return {};
    case "simulate_savings_projection": return { days: 14 };
    case "get_home_status": return {};
    case "get_activity_log": return { limit: 10 };
    default: return {};
  }
}

window.executeSingleToolModal = async function(toolName) {
  const txtArea = document.getElementById("txtToolParams");
  const outputWrap = document.getElementById("toolExecutionOutput");
  const preResp = document.getElementById("preToolResp");
  const btn = document.getElementById("btnExecuteSingleTool");

  let parsedParams = {};
  try {
    parsedParams = JSON.parse(txtArea.value);
  } catch (e) {
    alert("Invalid JSON parameters format: " + e.message);
    return;
  }

  btn.disabled = true;
  try {
    const res = await HomeBrainAPI.executeMcpTool(toolName, parsedParams);
    outputWrap.style.display = "block";
    preResp.textContent = JSON.stringify(res, null, 2);
    await refreshTelemetryAndDevices();
    await refreshAuditLogs();
  } catch (err) {
    alert("Execution error: " + err.message);
  } finally {
    btn.disabled = false;
  }
};

// Audit Logs Table
async function refreshAuditLogs() {
  try {
    const data = await HomeBrainAPI.getLogs(40);
    const logs = data.logs || [];
    document.getElementById("countLogs").textContent = logs.length;

    const tbody = document.getElementById("auditTableBody");
    if (!tbody) return;

    if (logs.length === 0) {
      tbody.innerHTML = `<tr><td colspan="7" style="text-align: center; color: var(--text-dim); padding: 24px;">No audit records found.</td></tr>`;
      return;
    }

    tbody.innerHTML = logs.map(l => {
      const timeStr = l.timestamp ? new Date(l.timestamp).toLocaleTimeString() : "--";
      const hashStr = l.result?.audit_hash || "verified";

      return `
        <tr>
          <td class="audit-ts">${timeStr}</td>
          <td class="audit-initiator">${escapeHtml(l.initiator)}</td>
          <td><span class="step-domain-tag ${(l.domain || '').toLowerCase()}">${escapeHtml(l.domain)}</span></td>
          <td class="audit-tool">${escapeHtml(l.tool_name)}</td>
          <td>${escapeHtml(l.action)}</td>
          <td style="color: var(--accent-neon); font-family: var(--font-mono); font-size: 0.78rem;">${escapeHtml(l.energy_impact || 'OK')}</td>
          <td style="font-family: var(--font-mono); font-size: 0.75rem; color: var(--accent-cyan);">${escapeHtml(hashStr)}</td>
        </tr>
      `;
    }).join("");
  } catch (err) {
    console.warn("Could not refresh logs:", err);
  }
}

// Global actions
function setupGlobalActions() {
  const btnReset = document.getElementById("btnResetState");
  if (btnReset) {
    btnReset.addEventListener("click", async () => {
      if (!confirm("Reset simulated home state back to un-optimized baseline? (This turns geyser ON, bedroom AC ON, and unlocks back door for testing).")) return;
      btnReset.disabled = true;
      try {
        await HomeBrainAPI.resetState();
        await refreshTelemetryAndDevices();
        await refreshAuditLogs();

        // Reset stepper
        document.getElementById("planBadgeStatus").className = "badge-status";
        document.getElementById("planBadgeStatus").textContent = "BASELINE RESTORED";
        document.getElementById("stepperGrid").innerHTML = "";
        document.getElementById("alexaSpokenText").textContent = `"Simulated baseline restored. Active power draw is 3,720 Watts. Ready for your goal command."`;
      } catch (e) {
        alert("Failed to reset: " + e.message);
      } finally {
        btnReset.disabled = false;
      }
    });
  }

  const btnDocs = document.getElementById("btnOpenDocs");
  if (btnDocs) {
    btnDocs.addEventListener("click", () => {
      window.open("/docs", "_blank");
    });
  }

  const btnExport = document.getElementById("btnExportLogs");
  if (btnExport) {
    btnExport.addEventListener("click", async () => {
      const data = await HomeBrainAPI.getLogs(200);
      const blob = new Blob([JSON.stringify(data, null, 2)], { type: "application/json" });
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `homebrain_activity_log_${Date.now()}.json`;
      a.click();
      URL.revokeObjectURL(url);
    });
  }

  const btnRefreshLogs = document.getElementById("btnRefreshLogs");
  if (btnRefreshLogs) {
    btnRefreshLogs.addEventListener("click", refreshAuditLogs);
  }
}

// Modal Utility
function setupModal() {
  const backdrop = document.getElementById("modalBackdrop");
  const btnClose = document.getElementById("btnCloseModal");

  if (btnClose) {
    btnClose.addEventListener("click", closeModal);
  }
  if (backdrop) {
    backdrop.addEventListener("click", (e) => {
      if (e.target === backdrop) closeModal();
    });
  }
}

function openModal(title, htmlContent) {
  const backdrop = document.getElementById("modalBackdrop");
  const modalTitle = document.getElementById("modalTitle");
  const modalBody = document.getElementById("modalBody");
  if (!backdrop || !modalTitle || !modalBody) return;

  modalTitle.textContent = title;
  modalBody.innerHTML = htmlContent;
  backdrop.classList.add("open");
}

function closeModal() {
  const backdrop = document.getElementById("modalBackdrop");
  if (backdrop) backdrop.classList.remove("open");
}

// Helpers
function delay(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

function escapeHtml(str) {
  if (!str) return "";
  return String(str)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
}
