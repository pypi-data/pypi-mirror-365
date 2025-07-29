from guriz.documentation.registry import DOCUMENTED_ROUTES
from guriz.documentation.documentate import import_controllers_from
import json
from http.server import BaseHTTPRequestHandler, HTTPServer
import threading
import webbrowser

def build_openapi_spec():
    import_controllers_from("app/controllers")

    paths = {}
    for route in DOCUMENTED_ROUTES:
        path = route["path"]
        method = route["method"].lower()

        if path not in paths:
            paths[path] = {}

        paths[path][method] = {
            "summary": route["handler"],
            "requestBody": {
                "content": {
                    "application/json": {
                        "schema": {
                            "type": "object",
                            "properties": {
                                k: {"type": "string"}  # simplificado
                                for k in getattr(route["request_model"], '__annotations__', {}).keys()
                            }
                        }
                    }
                }
            } if route["request_model"] else {},
            "responses": {
                "200": {
                    "description": "Success",
                    "content": {
                        "application/json": {
                            "schema": {"type": "object"}
                        }
                    }
                }
            }
        }

    return {
        "openapi": "3.0.0",
        "info": {
            "title": "Guriz API Docs",
            "version": "1.0.0"
        },
        "paths": paths
    }


class SwaggerHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/swagger.json":
            spec = build_openapi_spec()
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(spec).encode('utf-8'))
        else:
            self.send_response(200)
            self.send_header('Content-Type', 'text/html')
            self.end_headers()
            self.wfile.write(SWAGGER_UI_HTML.encode('utf-8'))


SWAGGER_UI_HTML = """
<!DOCTYPE html>
<html>
  <head>
    <title>Guriz Docs</title>
    <link rel="stylesheet" type="text/css" href="https://unpkg.com/swagger-ui-dist/swagger-ui.css" />
  </head>
  <body>
    <div id="swagger-ui"></div>
    <script src="https://unpkg.com/swagger-ui-dist/swagger-ui-bundle.js"></script>
    <script>
      SwaggerUIBundle({
        url: '/swagger.json',
        dom_id: '#swagger-ui'
      });
    </script>
  </body>
</html>
"""

def serve_docs():
    port = 7070
    server = HTTPServer(('localhost', port), SwaggerHandler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    webbrowser.open(f"http://localhost:{port}")
    try:
        print(f"Servidor rodando em http://localhost:{port} (CTRL+C para sair)")
        while True:
            pass
    except KeyboardInterrupt:
        print("Servidor finalizado.")
        server.shutdown()