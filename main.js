const header = document.getElementById("siteHeader");
window.addEventListener("scroll", () => {
  if (header) header.classList.toggle("scrolled", window.scrollY > 12);
});

const toggle = document.querySelector(".nav-toggle");
const nav = document.querySelector(".nav-links");
if (toggle && nav) toggle.addEventListener("click", () => nav.classList.toggle("open"));

const launcher = document.getElementById("chatLauncher");
const chatbox = document.getElementById("chatbox");
const close = document.getElementById("chatClose");
if (launcher && chatbox) {
  launcher.addEventListener("click", () => {
    chatbox.classList.toggle("open");
    chatbox.setAttribute("aria-hidden", chatbox.classList.contains("open") ? "false" : "true");
  });
}
if (close && chatbox) close.addEventListener("click", () => chatbox.classList.remove("open"));

const form = document.getElementById("chatForm");
const input = document.getElementById("chatInput");
const messages = document.getElementById("chatMessages");

function addMessage(text, type) {
  const el = document.createElement("div");
  el.className = "chat-bubble " + type;
  el.textContent = text;
  messages.appendChild(el);
  messages.scrollTop = messages.scrollHeight;
}

if (form) {
  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    const message = input.value.trim();
    if (!message) return;
    addMessage(message, "user");
    input.value = "";
    addMessage("Thinking…", "bot typing");
    const typing = messages.lastElementChild;
    try {
      const res = await fetch("/api/chat", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({message})
      });
      const data = await res.json();
      typing.remove();
      addMessage(data.reply || "Sorry, I couldn't answer that.", "bot");
    } catch (err) {
      typing.remove();
      addMessage("The assistant is temporarily unavailable. Please use WhatsApp.", "bot");
    }
  });
}
