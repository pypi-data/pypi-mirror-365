import { render_slides } from './plixlab.js';

document.addEventListener('DOMContentLoaded', function () {
  
  function getUrlParameter(name) {
    const urlParams = new URLSearchParams(window.location.search);
    return urlParams.get(name);
  }

  function setupSSE() {
    const eventSource = new EventSource("http://localhost:8889/events");

    eventSource.onopen = () => {
      // SSE connection established
    };

    eventSource.onmessage = (event) => {
      if (event.data === "ready") {
       
        connectWebSocket();
      }
    };

    // Handle errors if needed
    eventSource.onerror = (error) => {
    
    };
  }

  function connectWebSocket() {
    const ws = new WebSocket("ws://localhost:8889/data");
    ws.binaryType = "arraybuffer";

    ws.onopen = () => {
      // WebSocket connection opened
    };

    ws.onmessage = (event) => {
      const binaryData = event.data;
      const unpackedData = msgpackr.unpack(new Uint8Array(binaryData));
      render_slides(unpackedData);
    };

    ws.onerror = (error) => {
      //console.error("WebSocket error:", error);
    };

    ws.onclose = () => {
      //console.warn("WebSocket connection closed.");
    };
  }

  // Check for suppress_SSE parameter in the URL
  const suppressSSE = getUrlParameter('suppress_SSE') === 'true';

  if (!suppressSSE) {
    // Start listening for readiness via SSE
    setupSSE();
  } else {
    console.log("SSE suppressed due to suppress_SSE=true in the URL.");
  }
});
