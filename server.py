import http.server
import socketserver
import json
import os
import urllib.parse
from search_engine import SearchEngine

PORT = int(os.environ.get("PORT", 8000))
DATA_PATH = os.path.join(os.path.dirname(__file__), "data", "dataset.json")
PUBLIC_DIR = os.path.join(os.path.dirname(__file__), "public")

engine = SearchEngine(DATA_PATH)

class PhotoAssistantHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=PUBLIC_DIR, **kwargs)

    def do_GET(self):
        parsed_url = urllib.parse.urlparse(self.path)
        query_params = urllib.parse.parse_qs(parsed_url.query)
        
        # API Endpoint: GET /api/photos (Always serves the clean, baseline seeded dataset)
        if parsed_url.path == "/api/photos":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            with open(DATA_PATH, "r", encoding="utf-8") as f:
                self.wfile.write(f.read().encode("utf-8"))
            return

        # API Endpoint: GET /api/search?q=...&mode=ai|literal&refinement=...&skip=true|false
        if parsed_url.path == "/api/search":
            q = query_params.get("q", [""])[0]
            mode = query_params.get("mode", ["ai"])[0]
            refinement = query_params.get("refinement", [""])[0]
            skip = query_params.get("skip", ["false"])[0].lower() == "true"
            
            if mode == "literal":
                res = engine.search_literal_baseline(q)
            else:
                res = engine.search_ai_decomposed(q, refinement=refinement, skip_clarification=skip)

            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(json.dumps(res).encode("utf-8"))
            return

        # API Endpoint: GET /api/health
        if parsed_url.path == "/api/health":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            response = {"status": "ok", "phase": 5, "message": "MemoryLens Photo API active", "total_photos": len(engine.dataset)}
            self.wfile.write(json.dumps(response).encode("utf-8"))
            return

        # Serve static frontend files
        return super().do_GET()

    def do_POST(self):
        parsed_url = urllib.parse.urlparse(self.path)

        # POST /api/search: Evaluates search queries with optional browser-isolated custom photos in memory
        if parsed_url.path == "/api/search":
            content_length = int(self.headers.get("Content-Length", 0))
            post_data = self.rfile.read(content_length)
            try:
                data = json.loads(post_data.decode("utf-8"))
            except Exception as e:
                self.send_response(400)
                self.send_header("Content-Type", "application/json")
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()
                self.wfile.write(json.dumps({"error": f"Invalid JSON: {str(e)}"}).encode("utf-8"))
                return

            q = data.get("q", "")
            mode = data.get("mode", "ai")
            refinement = data.get("refinement")
            skip = bool(data.get("skip", False))
            custom_photos = data.get("custom_photos", [])

            # Evaluates in-memory for this single user session with zero disk persistence
            res = engine.search_with_custom_photos(
                q, custom_photos, mode=mode, refinement=refinement, skip_clarification=skip
            )

            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(json.dumps(res).encode("utf-8"))
            return

        self.send_response(404)
        self.end_headers()

if __name__ == "__main__":
    os.makedirs(PUBLIC_DIR, exist_ok=True)
    with socketserver.TCPServer(("", PORT), PhotoAssistantHandler) as httpd:
        print(f"Phase 4 MemoryLens Server running at http://localhost:{PORT}")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nServer stopped.")
