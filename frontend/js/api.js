/**
 * HomeBrain REST API Client
 * Interfaces with FastAPI endpoints on http://localhost:8000/api
 */

const API_BASE = window.location.origin ? `${window.location.origin}/api` : "/api";

const HomeBrainAPI = {
  async getStatus() {
    const res = await fetch(`${API_BASE}/status`);
    if (!res.ok) throw new Error("Failed to fetch home status");
    return res.json();
  },

  async getDevices() {
    const res = await fetch(`${API_BASE}/devices`);
    if (!res.ok) throw new Error("Failed to fetch devices");
    return res.json();
  },

  async mutateDevice(deviceId, state, level = null) {
    const res = await fetch(`${API_BASE}/devices/${deviceId}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ state, level, initiator: "User (Web Dashboard)" })
    });
    if (!res.ok) throw new Error(`Failed to update device ${deviceId}`);
    return res.json();
  },

  async getLocks() {
    const res = await fetch(`${API_BASE}/locks`);
    if (!res.ok) throw new Error("Failed to fetch locks");
    return res.json();
  },

  async mutateLock(lockId, locked) {
    const res = await fetch(`${API_BASE}/locks/${lockId}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ locked, initiator: "User (Web Dashboard)" })
    });
    if (!res.ok) throw new Error(`Failed to update lock ${lockId}`);
    return res.json();
  },

  async activateScene(sceneName) {
    const res = await fetch(`${API_BASE}/scenes/${sceneName}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" }
    });
    if (!res.ok) throw new Error(`Failed to activate scene ${sceneName}`);
    return res.json();
  },

  async mutateThermostat(deviceId, mode, targetTempC = null) {
    const res = await fetch(`${API_BASE}/thermostat/${deviceId}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ mode, target_temp_c: targetTempC, initiator: "User (Web Dashboard)" })
    });
    if (!res.ok) throw new Error(`Failed to update thermostat ${deviceId}`);
    return res.json();
  },

  async getEnergyReport(tariff = 8.0) {
    const res = await fetch(`${API_BASE}/energy?tariff=${tariff}`);
    if (!res.ok) throw new Error("Failed to fetch energy report");
    return res.json();
  },

  async getSavingsProjection(days = 7) {
    const res = await fetch(`${API_BASE}/energy/projection?days=${days}`);
    if (!res.ok) throw new Error("Failed to fetch savings projection");
    return res.json();
  },

  async getLogs(limit = 50, domain = null) {
    const url = domain ? `${API_BASE}/logs?limit=${limit}&domain=${domain}` : `${API_BASE}/logs?limit=${limit}`;
    const res = await fetch(url);
    if (!res.ok) throw new Error("Failed to fetch audit logs");
    return res.json();
  },

  async getMcpTools() {
    const res = await fetch(`${API_BASE}/mcp/tools`);
    if (!res.ok) throw new Error("Failed to fetch MCP tools");
    return res.json();
  },

  async executeMcpTool(toolName, parameters = {}) {
    const res = await fetch(`${API_BASE}/mcp/execute`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ tool_name: toolName, parameters, initiator: "Developer MCP Workbench" })
    });
    if (!res.ok) throw new Error(`Failed to execute MCP tool ${toolName}`);
    return res.json();
  },

  async compileAlexaGoal(goal) {
    const res = await fetch(`${API_BASE}/alexa/compile`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ goal, initiator: "Alexa+ Voice Agent" })
    });
    if (!res.ok) throw new Error("Failed to compile Alexa goal");
    return res.json();
  },

  async executeAlexaGoal(goal) {
    const res = await fetch(`${API_BASE}/alexa/execute`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ goal, initiator: "Alexa+ Voice Agent" })
    });
    if (!res.ok) throw new Error("Failed to execute Alexa goal");
    return res.json();
  },

  async resetState() {
    const res = await fetch(`${API_BASE}/state/reset`, {
      method: "POST"
    });
    if (!res.ok) throw new Error("Failed to reset home state");
    return res.json();
  }
};
