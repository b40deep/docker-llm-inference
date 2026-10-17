const storageKey = "llmInference.session";
const $ = (selector) => document.querySelector(selector);

function showError(message = "") {
  const node = $("#login-error");
  node.textContent = message;
  node.hidden = !message;
}

function validSession() {
  const value = JSON.parse(localStorage.getItem(storageKey) || "null");
  return value && value.expiresAt > Math.floor(Date.now() / 1000);
}

if (validSession()) {
  location.replace("/workspace");
} else {
  localStorage.removeItem(storageKey);
  $("#password").focus();
}

$("#login-form").addEventListener("submit", async (event) => {
  event.preventDefault();
  showError();
  const password = $("#password").value;
  try {
    const response = await fetch("/api/auth/login", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ password }),
    });
    const data = await response.json().catch(() => ({}));
    if (!response.ok) throw new Error(data.error?.message || "Request failed.");
    localStorage.setItem(storageKey, JSON.stringify({ token: data.token, expiresAt: data.expiresAt }));
    location.assign("/workspace");
  } catch (error) {
    showError(error.message);
  }
});