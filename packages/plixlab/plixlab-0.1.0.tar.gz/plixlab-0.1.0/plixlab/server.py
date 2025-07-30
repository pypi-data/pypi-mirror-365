import webbrowser
import os
import msgpack
from tornado import autoreload, websocket
import tornado.ioloop
import tornado.web

def make_app(data_provider):
    """Create the Tornado application with routes."""
    base_dir = os.path.dirname(__file__)
    public_dir = os.path.join(base_dir, "../web")

    return tornado.web.Application([
        (r"/", NoCacheHandler, {"path": os.path.join(public_dir, "index.html")}),
        (r"/static/(.*)", tornado.web.StaticFileHandler, {"path": os.path.join(public_dir, "static")}),
        (r"/assets/(.*)", tornado.web.StaticFileHandler, {"path": os.path.join(public_dir, "assets")}),
        (r"/data", ReloadWebSocketHandler, {"data_provider": data_provider}),
        (r"/events", ReadySSEHandler),  # SSE handler for sending "ready"
    ])

class ReadySSEHandler(tornado.web.RequestHandler):
    """Handler for server-sent events (SSE)."""
    def set_default_headers(self):
        self.set_header("Content-Type", "text/event-stream")
        self.set_header("Cache-Control", "no-cache")
        self.set_header("Connection", "keep-alive")

    async def get(self):
        """Handle SSE connections and send 'ready' signals."""
        global active_sse_connections
        active_sse_connections.append(self)

        try:
            print("New SSE connection established.")
            self.write("retry: 3000\n")  # Retry after 2 seconds if disconnected
            self.write("data: ready\n\n")  # Initial SSE signal
            await self.flush()  # Ensure immediate transmission

            # Keep the connection alive with periodic messages
            while True:
                await tornado.gen.sleep(10)
                self.write("data: keep-alive\n\n")
                self.flush()
        except tornado.iostream.StreamClosedError:
            print("SSE client disconnected.")
        except Exception as e:
            print(f"Unexpected error in SSE handler: {e}")
        finally:
            active_sse_connections.remove(self)
            print("SSE connection closed.")

class NoCacheHandler(tornado.web.RequestHandler):
    """Handler for serving the index.html file without caching."""
    def initialize(self, path):
        self.file_path = path

    def set_default_headers(self):
        self.set_header("Cache-Control", "no-store, no-cache, must-revalidate, max-age=0")
        self.set_header("Pragma", "no-cache")
        self.set_header("Expires", "0")

    def get(self):
        """Serve the index.html file."""
        if os.path.exists(self.file_path):
            with open(self.file_path, "r") as f:
                self.write(f.read())
        else:
            self.set_status(404)
            self.write("404: index.html not found")

class ReloadWebSocketHandler(websocket.WebSocketHandler):
    """Handler for WebSocket connections."""
    def initialize(self, data_provider):
        self.data_provider = data_provider

    def open(self):
        print("WebSocket connection opened.")
        self.send_data_to_client()

    def on_close(self):
        print("WebSocket connection closed.")

    def send_data_to_client(self):
        """Send packed data to the client."""
        self.write_message(msgpack.packb(self.data_provider), binary=True)

def cleanup_connections():
    """Clean up SSE connections during server reload."""
    print("Cleaning up active SSE connections...")
    for connection in active_sse_connections:
        try:
            connection.finish()
        except Exception as e:
            print(f"Error closing SSE connection: {e}")
    active_sse_connections.clear()

def run(data_provider,**kwargs):
    """Run the Tornado server."""
    print("Starting Tornado server...")
    port = 8889
    app = make_app(data_provider)
    app.listen(port)

    if kwargs.setdefault("carousel",False):
        options = "?carousel=True"
    else:
        options = ""

    # Open the browser on the first run
    if not os.environ.get("BROWSER_OPENED"):
        webbrowser.open(f"http://localhost:{port}{options}")
        os.environ["BROWSER_OPENED"] = "True"

    # Set up autoreload hooks
    autoreload.add_reload_hook(cleanup_connections)
    autoreload.add_reload_hook(lambda: tornado.ioloop.IOLoop.current().stop())
    autoreload.start()

    print(f"Server running at http://localhost:{port}")
    tornado.ioloop.IOLoop.current().start()

# Global list to track active SSE connections
active_sse_connections = []

if __name__ == "__main__":
    # Example data provider
    example_data = {"key": "value"}
    run(example_data)

        
