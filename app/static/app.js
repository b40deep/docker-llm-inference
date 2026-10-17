const storageKeys = { session: "llmInference.session", responses: "llmInference.responses" };
const legacyConversationKey = "llmInference.conversation";
const $ = (selector) => document.querySelector(selector);

function session() { return JSON.parse(localStorage.getItem(storageKeys.session) || "null"); }
function saveSession(value) { localStorage.setItem(storageKeys.session, JSON.stringify(value)); }
function responses() { return JSON.parse(localStorage.getItem(storageKeys.responses) || "[]"); }
function saveResponses(items) { localStorage.setItem(storageKeys.responses, JSON.stringify(items)); }
function showError(selector, message = "") { const node = $(selector); node.textContent = message; node.hidden = !message; }

function migrateResponseStorage() {
  if (localStorage.getItem(storageKeys.responses) === null) {
    const legacyResponses = localStorage.getItem(legacyConversationKey);
    if (legacyResponses !== null) localStorage.setItem(storageKeys.responses, legacyResponses);
  }
  localStorage.removeItem(legacyConversationKey);
}

function renderMarkdown(markdown) {
  const parsed = marked.parse(markdown, { gfm: true, breaks: true });
  return DOMPurify.sanitize(parsed, { USE_PROFILES: { html: true } });
}

function showView() {
  const active = session() && session().expiresAt > Math.floor(Date.now() / 1000);
  $("#login-view").hidden = active;
  $("#workspace-view").hidden = !active;
  if (active) { renderResponses(); checkHealth(); }
  else { localStorage.removeItem(storageKeys.session); }
}

function renderResponses() {
  const root = $("#responses");
  root.replaceChildren();
  const items = responses();
  if (!items.length) {
    const empty = document.createElement("p"); empty.className = "text-body-secondary mb-0"; empty.textContent = "Your local search responses will appear here."; root.append(empty); return;
  }
  items.forEach((item) => {
    const line = document.createElement("div"); line.className = `message ${item.role} ${item.role === "user" ? "text-success" : "text-primary"}`; line.innerHTML = renderMarkdown(item.content);
    root.append(line);
  });
  root.scrollTop = root.scrollHeight;
}

function resizePrompt() {
  const prompt = $("#prompt");
  const maxHeight = parseFloat(getComputedStyle(prompt).lineHeight) * 10;
  prompt.style.height = "auto";
  prompt.style.height = `${Math.min(prompt.scrollHeight, maxHeight)}px`;
  prompt.classList.toggle("has-overflow", prompt.scrollHeight > maxHeight);
}

async function api(path, options = {}) {
  const current = session();
  const headers = { "Content-Type": "application/json", ...(options.headers || {}) };
  if (current?.token) headers.Authorization = `Bearer ${current.token}`;
  const response = await fetch(path, { ...options, headers });
  const data = await response.json().catch(() => ({}));
  if (!response.ok) throw new Error(data.error?.message || "Request failed.");
  return data;
}

async function checkHealth() {
  try { const data = await api("/api/health"); $("#service-status").textContent = `Inference: ${data.services.inference}`; }
  catch { $("#service-status").textContent = "Service unavailable"; }
}

$("#login-form").addEventListener("submit", async (event) => {
  event.preventDefault(); showError("#login-error");
  const password = $("#password").value;
  try {
    const data = await api("/api/auth/login", { method: "POST", body: JSON.stringify({ password }) });
    saveSession({ token: data.token, expiresAt: data.expiresAt }); $("#password").value = ""; showView();
  } catch (error) { showError("#login-error", error.message); }
});

$("#inference-form").addEventListener("submit", async (event) => {
  event.preventDefault(); showError("#inference-error");
  const prompt = $("#prompt").value.trim(); const input = $("#prompt");
  if (!prompt) return;
  input.disabled = true;
  try {
    const history = $("#use-history").checked ? responses().slice(-20).map(({ role, content }) => ({ role, content })) : [];
    const data = await api("/api/inference", { method: "POST", body: JSON.stringify({ prompt, history }) });
    const items = responses(); items.push({ role: "user", content: prompt, at: Date.now() }, { role: "assistant", content: data.response, at: Date.now() });
    saveResponses(items); input.value = ""; resizePrompt(); renderResponses();
  } catch (error) {
    if (error.message === "Authentication is required.") { localStorage.removeItem(storageKeys.session); showView(); }
    else showError("#inference-error", error.message);
  } finally { input.disabled = false; input.focus(); }
});

$("#prompt").addEventListener("input", resizePrompt);
$("#prompt").addEventListener("keydown", (event) => {
  if (event.ctrlKey && event.key === "Enter") {
    event.preventDefault();
    $("#inference-form").requestSubmit();
  }
});

$("#logout-button").addEventListener("click", () => { localStorage.removeItem(storageKeys.session); showView(); });
migrateResponseStorage();
$("#clear-history").addEventListener("click", () => { localStorage.removeItem(storageKeys.responses); renderResponses(); });
resizePrompt();
showView();
