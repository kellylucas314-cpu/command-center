#!/usr/bin/env python3
"""
HelioFlux Rolodex - Simple server
Run: python3 serve.py
Then open: http://localhost:8001
"""

import http.server
import socketserver
import os

PORT = 8001
DIRECTORY = os.path.dirname(os.path.abspath(__file__))

class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)

if __name__ == "__main__":
    os.chdir(DIRECTORY)
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        print(f"🗂️  HelioFlux Rolodex running at http://localhost:{PORT}")
        print("Press Ctrl+C to stop")
        httpd.serve_forever()
