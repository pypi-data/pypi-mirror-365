from guriz.documentation.registry import DOCUMENTED_ROUTES
from guriz.documentation.documentate import import_controllers_from
import json
from http.server import BaseHTTPRequestHandler, HTTPServer
import threading
import webbrowser
from typing import get_origin, get_args

def build_openapi_spec():
    import_controllers_from("app/controllers")

    paths = {}
    for route in DOCUMENTED_ROUTES:
        path = route["path"]
        method = route["method"].lower()

        if path not in paths:
            paths[path] = {}

        # --- REQUEST BODY ---
        request_model = route["request_model"]
        if request_model:
            request_body = {
                "content": {
                    "application/json": {
                        "schema": {
                            "type": "object",
                            "properties": {
                                k: {"type": "string"}
                                for k in getattr(request_model, '__annotations__', {}).keys()
                            }
                        }
                    }
                }
            }
        else:
            request_body = {}

        # --- RESPONSE SCHEMA ---
        response_model = route["response_model"]
        if response_model:
            if get_origin(response_model) is list:
                item_model = get_args(response_model)[0]
                schema = {
                    "type": "array",
                    "items": item_model.schema()
                }
            else:
                schema = response_model.schema()
        else:
            schema = {"type": "object"}

        paths[path][method] = {
            "summary": route["handler"],
            "requestBody": request_body,
            "responses": {
                "200": {
                    "description": "Success",
                    "content": {
                        "application/json": {
                            "schema": schema
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
