const state = {
  transcript: [],
  lastResponse: null,
};

const scenarios = [
  {
    label: "Cashflow",
    messages: ["כמה נשאר לי עד המשכורת?"],
  },
  {
    label: "Purchase with amount",
    messages: ["אפשר לקנות אוזניות ב-400 שקל?"],
  },
  {
    label: "Purchase follow-up",
    messages: ["אפשר לקנות את זה?", "400 שקל"],
  },
  {
    label: "Installments follow-up",
    messages: ["מה יקרה אם אפרוס לתשלומים?", "900 שקל ל-3 תשלומים"],
  },
  {
    label: "New-topic override",
    messages: ["אפשר לקנות את זה?", "כמה נשאר לי עד המשכורת?"],
  },
  {
    label: "Unknown",
    messages: ["ספר לי בדיחה"],
  },
  {
    label: "Invalid amount",
    messages: ["Can I buy this for -400 shekels?"],
  },
];

const elements = {
  serviceState: document.getElementById("service-state"),
  userId: document.getElementById("user-id"),
  sessionId: document.getElementById("session-id"),
  newSessionButton: document.getElementById("new-session-button"),
  clearButton: document.getElementById("clear-button"),
  scenarioList: document.getElementById("scenario-list"),
  chatLog: document.getElementById("chat-log"),
  chatForm: document.getElementById("chat-form"),
  messageInput: document.getElementById("message-input"),
  sendButton: document.getElementById("send-button"),
  fileInput: document.getElementById("file-input"),
  fileMeta: document.getElementById("file-meta"),
  filePreview: document.getElementById("file-preview"),
  copyRawButton: document.getElementById("copy-raw-button"),
  exportButton: document.getElementById("export-button"),
  rawJson: document.getElementById("raw-json"),
  debugIntent: document.getElementById("debug-intent"),
  debugStatus: document.getElementById("debug-status"),
  debugConfidence: document.getElementById("debug-confidence"),
  debugMissing: document.getElementById("debug-missing"),
  debugTool: document.getElementById("debug-tool"),
  debugExecuted: document.getElementById("debug-executed"),
  debugRisk: document.getElementById("debug-risk"),
  debugReasons: document.getElementById("debug-reasons"),
};

function init() {
  elements.sessionId.value = createSessionId();
  renderScenarios();
  renderEmptyChat();
  bindEvents();
  checkHealth();
}

function bindEvents() {
  elements.chatForm.addEventListener("submit", async (event) => {
    event.preventDefault();
    await sendMessage(elements.messageInput.value);
  });

  elements.newSessionButton.addEventListener("click", () => {
    elements.sessionId.value = createSessionId();
    clearTranscript();
    setRawResponse({});
  });

  elements.clearButton.addEventListener("click", () => {
    clearTranscript();
    setRawResponse({});
  });

  elements.fileInput.addEventListener("change", previewLocalFile);
  elements.copyRawButton.addEventListener("click", copyRawResponse);
  elements.exportButton.addEventListener("click", exportTranscript);
}

async function checkHealth() {
  try {
    const response = await fetch("/health");
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`);
    }
    const body = await response.json();
    elements.serviceState.textContent = `${body.status} · ${body.service}`;
    elements.serviceState.className = "service-state ok";
  } catch (error) {
    elements.serviceState.textContent = `API unavailable · ${error.message}`;
    elements.serviceState.className = "service-state error";
  }
}

function renderScenarios() {
  elements.scenarioList.innerHTML = "";
  scenarios.forEach((scenario) => {
    const button = document.createElement("button");
    button.type = "button";
    button.textContent = scenario.label;
    button.addEventListener("click", async () => {
      clearTranscript();
      elements.sessionId.value = createSessionId();
      await runScenario(scenario);
    });
    elements.scenarioList.appendChild(button);
  });
}

async function runScenario(scenario) {
  for (const message of scenario.messages) {
    await sendMessage(message, { keepInput: true });
  }
}

async function sendMessage(message, options = {}) {
  const cleaned = message.trim();
  if (!cleaned) {
    return;
  }

  appendMessage("user", cleaned);
  if (!options.keepInput) {
    elements.messageInput.value = "";
  }

  elements.sendButton.disabled = true;
  try {
    const response = await fetch("/chat/message", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        user_id: elements.userId.value.trim() || "tester_user",
        session_id: elements.sessionId.value.trim() || createSessionId(),
        message: cleaned,
      }),
    });
    const body = await response.json();
    if (!response.ok) {
      throw new Error(JSON.stringify(body));
    }

    state.lastResponse = body;
    setRawResponse(body);
    renderDebug(body);
    appendMessage("bot", body.answer || "(no answer)");
    state.transcript.push({
      user: cleaned,
      response: body,
      created_at: new Date().toISOString(),
    });
  } catch (error) {
    appendMessage("error", `Request failed: ${error.message}`);
  } finally {
    elements.sendButton.disabled = false;
    elements.messageInput.focus();
  }
}

function appendMessage(role, text) {
  removeEmptyState();
  const wrapper = document.createElement("article");
  wrapper.className = `message ${role} ${hasHebrew(text) ? "rtl" : "ltr"}`;

  const label = document.createElement("div");
  label.className = "message-label";
  label.textContent = role === "bot" ? "Bot" : role === "user" ? "You" : "Error";

  const body = document.createElement("div");
  body.className = "message-body";
  body.textContent = text;

  wrapper.append(label, body);
  elements.chatLog.appendChild(wrapper);
  elements.chatLog.scrollTop = elements.chatLog.scrollHeight;
}

function renderDebug(response) {
  const debug = response.debug || {};
  elements.debugIntent.textContent = response.intent || "-";
  elements.debugStatus.textContent = response.status || "-";
  elements.debugConfidence.textContent = formatValue(response.confidence);
  elements.debugMissing.textContent = formatList(response.missing_fields);
  elements.debugTool.textContent = response.tool_called || "-";
  elements.debugExecuted.textContent = formatValue(debug.tool_executed);
  elements.debugRisk.textContent = debug.risk_level || "-";
  elements.debugReasons.textContent = formatList(debug.reason_codes);
}

function setRawResponse(value) {
  elements.rawJson.textContent = JSON.stringify(value, null, 2);
}

function clearTranscript() {
  state.transcript = [];
  state.lastResponse = null;
  elements.chatLog.innerHTML = "";
  renderEmptyChat();
  renderDebug({});
}

function renderEmptyChat() {
  if (elements.chatLog.children.length > 0) {
    return;
  }
  const empty = document.createElement("div");
  empty.className = "empty-state";
  empty.textContent =
    "Use the message box or run a scenario. This tester calls the real /chat/message endpoint and shows the structured debug response.";
  elements.chatLog.appendChild(empty);
}

function removeEmptyState() {
  const empty = elements.chatLog.querySelector(".empty-state");
  if (empty) {
    empty.remove();
  }
}

function previewLocalFile() {
  const file = elements.fileInput.files && elements.fileInput.files[0];
  if (!file) {
    elements.fileMeta.textContent = "No file selected.";
    elements.filePreview.textContent = "";
    return;
  }

  elements.fileMeta.textContent = `${file.name} · ${formatBytes(file.size)} · ${
    file.type || "unknown type"
  }`;

  const reader = new FileReader();
  reader.onload = () => {
    const text = String(reader.result || "");
    elements.filePreview.textContent = text.slice(0, 5000);
    if (text.length > 5000) {
      elements.filePreview.textContent += "\n\n[Preview truncated locally]";
    }
  };
  reader.onerror = () => {
    elements.filePreview.textContent = "Could not preview this file locally.";
  };
  reader.readAsText(file);
}

async function copyRawResponse() {
  const text = elements.rawJson.textContent || "{}";
  await navigator.clipboard.writeText(text);
}

function exportTranscript() {
  const payload = {
    user_id: elements.userId.value,
    session_id: elements.sessionId.value,
    exported_at: new Date().toISOString(),
    transcript: state.transcript,
  };
  const blob = new Blob([JSON.stringify(payload, null, 2)], {
    type: "application/json",
  });
  const link = document.createElement("a");
  link.href = URL.createObjectURL(blob);
  link.download = `bot-v1-transcript-${Date.now()}.json`;
  link.click();
  URL.revokeObjectURL(link.href);
}

function createSessionId() {
  return `tester_${Date.now()}_${Math.random().toString(16).slice(2, 8)}`;
}

function formatBytes(bytes) {
  if (bytes < 1024) {
    return `${bytes} B`;
  }
  if (bytes < 1024 * 1024) {
    return `${(bytes / 1024).toFixed(1)} KB`;
  }
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

function formatList(value) {
  if (!Array.isArray(value) || value.length === 0) {
    return "-";
  }
  return value.join(", ");
}

function formatValue(value) {
  if (value === null || value === undefined) {
    return "-";
  }
  return String(value);
}

function hasHebrew(text) {
  return /[\u0590-\u05ff]/.test(text);
}

init();
