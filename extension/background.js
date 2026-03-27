chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message.type === "API_CALL") {
    fetch(message.url)
      .then(res => res.json())
      .then(data => sendResponse({ data }))
      .catch(err => sendResponse({ error: err.toString() }));

    return true; 
  }
});