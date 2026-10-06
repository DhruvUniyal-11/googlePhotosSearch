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
        
        # API Endpoint: GET /api/photos
        if parsed_url.path == "/api/photos":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(json.dumps(engine.dataset).encode("utf-8"))
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

        if parsed_url.path == "/api/photos":
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

            import time
            photo_id = data.get("photo_id") or f"user_photo_{int(time.time()*1000)}"
            photo_obj = {
                "photo_id": photo_id,
                "image_url": data.get("image_url", ""),
                "date_taken": data.get("date_taken") or time.strftime("%Y-%m-%dT%H:%M:%SZ"),
                "approx_date_range": data.get("approx_date_range", "Recent"),
                "relationships": [r.strip() for r in data.get("relationships", []) if r.strip()],
                "tagged_names": [n.strip() for n in data.get("tagged_names", []) if n.strip()],
                "place_name": data.get("place_name") or None,
                "visual_descriptors": [v.strip() for v in data.get("visual_descriptors", []) if v.strip()],
                "event_tags": [e.strip() for e in data.get("event_tags", []) if e.strip()],
                "ocr_text": data.get("ocr_text") or None,
                "document_purpose": data.get("document_purpose") or None
            }

            engine.add_user_photo(photo_obj)

            self.send_response(201)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(json.dumps({
                "status": "success",
                "message": "Photo added and indexed successfully",
                "photo": photo_obj,
                "total_photos": len(engine.dataset)
            }).encode("utf-8"))
            return

        if parsed_url.path == "/api/photos/reset":
            engine.reset_user_photos()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(json.dumps({
                "status": "success",
                "message": "Reset to default seeded dataset",
                "total_photos": len(engine.dataset)
            }).encode("utf-8"))
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
