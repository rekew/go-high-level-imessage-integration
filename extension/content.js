console.log("GHL extension loaded");

function getConversationId() {
  const url = window.location.href;

  const parts = url.split("/conversations/conversations/");

  if (parts.length < 2) return null;

  return parts[1].split("?")[0];
}

document.addEventListener("click", async (e) => {

  const btn = e.target.closest("button");
  if (!btn) return;

  if (!btn.innerText.includes("Send")) return;

  const textarea = document.querySelector("textarea");

  if (!textarea) return;

  const message = textarea.value;

  const conversationId = getConversationId();

  console.log("Message:", message);
  console.log("Conversation:", conversationId);

  await fetch("https://nontautological-proauthor-ramiro.ngrok-free.dev/webhook", {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify({
      conversationId: conversationId,
      message: message
    })
  });

});