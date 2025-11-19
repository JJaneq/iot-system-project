export function createWebSocket(onData) {
  const ws = new WebSocket("ws://localhost:8765");

  ws.onopen = () => {
    console.log("Połączono z WebSocket!");
  };

  ws.onmessage = (event) => {
    try {
      const data = JSON.parse(event.data);
      onData(data); // callback do app.js
    } catch (e) {
      console.error("Błąd parsowania JSON:", e);
    }
  };

  ws.onerror = (error) => {
    console.error("WebSocket error:", error);
  };

  ws.onclose = () => {
    console.log("WebSocket zamknięty");
  };

  return ws;
}
