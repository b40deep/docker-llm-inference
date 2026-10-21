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

async function requireSession() {
  const active = session() && session().expiresAt > Math.floor(Date.now() / 1000);
  if (!active) {
    localStorage.removeItem(storageKeys.session);
    location.replace("/");
    return false;
  }
  try {
    await api("/api/auth/session");
    return true;
  } catch {
    localStorage.removeItem(storageKeys.session);
    location.replace("/");
    return false;
  }
}

function renderResponses() {
  const items = responses();
  [$("#responses"), $("#responses-tab-2")].forEach((root) => {
    root.replaceChildren();
    if (!items.length) {
      const empty = document.createElement("p"); empty.className = "text-body-secondary mb-0"; empty.textContent = "Your previous results will appear here."; root.append(empty); return;
    }
    items.forEach((item) => {
      const line = document.createElement("div"); line.className = `message ${item.role} ${item.role === "user" ? "text-success" : "text-primary"}`; line.innerHTML = renderMarkdown(item.content);
      line.querySelectorAll("p").forEach((paragraph) => paragraph.classList.add("mb-0"));
      if (item.role === "assistant") {
        const divider = document.createElement("hr");
        divider.className = "my-2";
        line.append(divider);
      }
      root.append(line);
    });
    root.scrollTop = root.scrollHeight;
  });
}

function resizePrompt(prompt = $("#prompt")) {
  const lineHeight = parseFloat(getComputedStyle(prompt).lineHeight);
  const maxHeight = lineHeight * 10;
  const minHeight = lineHeight * 2;
  prompt.style.height = "auto";
  prompt.style.height = `${Math.max(minHeight, Math.min(prompt.scrollHeight, maxHeight))}px`;
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
  const statusNodes = document.querySelectorAll(".service-status");
  try { const data = await api("/api/health"); statusNodes.forEach((node) => { node.textContent = `Inference: ${data.services.inference}`; }); }
  catch { statusNodes.forEach((node) => { node.textContent = "Service unavailable"; }); }
}

async function submitInference(event) {
  event.preventDefault();
  const form = event.currentTarget;
  const input = form.querySelector("textarea");
  const errorSelector = form.id === "inference-form" ? "#inference-error" : "#inference-error-tab-2";
  showError(errorSelector);
  const prompt = input.value.trim();
  if (!prompt) return;
  input.disabled = true;
  try {
    const history = $("#use-history").checked ? responses().slice(-20).map(({ role, content }) => ({ role, content })) : [];
    const data = await api("/api/inference", { method: "POST", body: JSON.stringify({ prompt, history }) });
    const items = responses(); items.push({ role: "user", content: prompt, at: Date.now() }, { role: "assistant", content: data.response, at: Date.now() });
    saveResponses(items); input.value = ""; resizePrompt(input); renderResponses();
  } catch (error) {
    if (error.message === "Authentication is required.") { localStorage.removeItem(storageKeys.session); location.replace("/"); }
    else showError(errorSelector, error.message);
  } finally { input.disabled = false; input.focus(); }
}

[ $("#inference-form"), $("#inference-form-tab-2") ].forEach((form) => form.addEventListener("submit", submitInference));
[ $("#prompt"), $("#prompt-tab-2") ].forEach((prompt) => {
  prompt.addEventListener("input", () => resizePrompt(prompt));
  prompt.addEventListener("keydown", (event) => {
    if (!(event.ctrlKey && event.key === "Enter")) return;
    event.preventDefault();
    prompt.closest("form").requestSubmit();
  });
});

$("#logout-button").addEventListener("click", () => { localStorage.removeItem(storageKeys.session); location.assign("/"); });
migrateResponseStorage();
[ $("#clear-history"), $("#clear-history-tab-2") ].forEach((button) => button.addEventListener("click", () => { localStorage.removeItem(storageKeys.responses); renderResponses(); }));
$("#alternate-tab").addEventListener("shown.bs.tab", () => {
  renderResponses();
  resizePrompt($("#prompt-tab-2"));
  $("#prompt-tab-2").focus();
});
async function initializeWorkspace() {
  if (!await requireSession()) return;
  document.body.hidden = false;
  [$("#prompt"), $("#prompt-tab-2")].forEach(resizePrompt);
  renderResponses();
  checkHealth();
  $("#prompt").focus();
}

initializeWorkspace();
