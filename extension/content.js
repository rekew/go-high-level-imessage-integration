console.log("EXTENSION LOADED 🚀");

const BASE_URL = "https://nontautological-proauthor-ramiro.ngrok-free.dev";

const HEADERS = {
  "Content-Type": "application/json",
  "ngrok-skip-browser-warning": "true",
};

function getLocationId() {
  const match = window.location.pathname.match(/\/location\/([^/]+)/);
  return match ? match[1] : null;
}

function getConversationId() {
  const parts = window.location.href.split("/conversations/conversations/");
  if (parts.length < 2) return null;
  return parts[1].split("?")[0];
}

async function apiCall(url, options = {}) {
  const res = await fetch(url, {
    ...options,
    headers: { ...HEADERS, ...(options.headers || {}) },
  });

  return {
    status: res.status,
    data: res.status !== 204 ? await res.json() : null,
  };
}

async function checkOrPromptConfig(locationId) {
  const { status, data } = await apiCall(
    `${BASE_URL}/getRowByLocationId/${locationId}`,
  );

  if (status === 200) {
    return data.pitToken;
  }

  if (status !== 404) {
    alert("❌ Unexpected error checking location config.");
    return null;
  }

  const pitToken = prompt(
    `⚙️ This location is not configured yet.\n\nPlease enter your PIT Token for location:\n${locationId}`,
  );

  if (!pitToken || !pitToken.trim()) {
    alert("❌ No PIT Token provided.");
    return null;
  }

  const saveResult = await apiCall(`${BASE_URL}/savePitConfig`, {
    method: "POST",
    body: JSON.stringify({ locationId, pitToken: pitToken.trim() }),
  });

  if (saveResult.status !== 200) {
    alert("❌ Failed to save configuration.");
    return null;
  }

  alert("✅ Configuration saved! Click Send again.");
  return null;
}

let cachedToken = null;

// =======================
// 🔥 ТВОЙ ОБРАБОТЧИК (ПОЧИНЕН)
// =======================
async function handleSend() {
  console.log("✅ SEND DETECTED");

  const textarea = document.querySelector("textarea");
  if (!textarea) {
    console.error("❌ No textarea found");
    return;
  }

  const message = textarea.value;
  const conversationId = getConversationId();
  const locationId = getLocationId();

  console.log("📋 message:", message);
  console.log("📋 conversationId:", conversationId);
  console.log("📋 locationId:", locationId);

  if (!conversationId || !locationId) {
    console.error("❌ Missing IDs");
    return;
  }

  if (!cachedToken) {
    console.log("🔑 Checking config...");
    cachedToken = await checkOrPromptConfig(locationId);
  }

  if (!cachedToken) {
    console.log("⚠️ No token, aborting");
    return;
  }

  console.log("📤 Sending webhook...");

  const { status } = await apiCall(`${BASE_URL}/webhook`, {
    method: "POST",
    body: JSON.stringify({ conversationId, message, locationId }),
  });

  if (status === 200) {
    console.log("✅ Message sent!");
  } else {
    console.error("❌ Webhook failed:", status);
  }
}

// =======================
// 🔥 FIX 1: CAPTURE PHASE CLICK
// =======================
document.addEventListener(
  "click",
  async (e) => {
    const sendBtn = e.target.closest("#conv-send-button-simple");
    if (!sendBtn) return;

    handleSend();
  },
  true, // 🔥 ключевой фикс
);

// =======================
// 🔥 FIX 2: ENTER KEY FALLBACK
// =======================
document.addEventListener("keydown", async (e) => {
  if (e.key === "Enter" && !e.shiftKey) {
    const textarea = document.querySelector("textarea");
    if (!textarea) return;

    if (document.activeElement === textarea) {
      console.log("⌨️ ENTER SEND DETECTED");
      handleSend();
    }
  }
});
