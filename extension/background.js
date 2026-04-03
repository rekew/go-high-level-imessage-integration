chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message.type === "API_CALL") {
    fetch(message.url, {
      headers: {
        "ngrok-skip-browser-warning": "true"  // ← add this
      }
    })
      .then(res => {
        if (!res.ok) throw new Error(`HTTP error ${res.status}`);
        return res.json();
      })
      .then(data => sendResponse({ data }))
      .catch(err => sendResponse({ error: err.toString() }));

    return true;
  }
});