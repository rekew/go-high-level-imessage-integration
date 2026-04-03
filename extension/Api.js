window.Api = {
  async getRowByLocationId(locationId) {
    try {
      const res = await fetch(
        `https://nontautological-proauthor-ramiro.ngrok-free.dev/getRowByLocationId/${locationId}`,
        {
          headers: { "ngrok-skip-browser-warning": "true" }, // ← add this
        },
      );

      if (!res.ok) {
        throw new Error(`HTTP error ${res.status}`);
      }

      return await res.json();
    } catch (err) {
      console.error("Api error:", err);
      throw err;
    }
  },
};
