from http.server import BaseHTTPRequestHandler
import json
from urllib.parse import urlparse, parse_qs
import sys
import os

# Add parent directory to path so we can import quant.py
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from quant import decompose_vix_change

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed_path = urlparse(self.path)
        params = parse_qs(parsed_path.query)
        
        underlying = params.get('underlying', ['SPX'])[0]
        date_from = params.get('date_from', ['2026-03-01'])[0]
        date_to = params.get('date_to', ['2026-03-05'])[0]
        method = params.get('method', ['cboe_like'])[0]
        
        try:
            result = decompose_vix_change(
                underlying=underlying, 
                date_from=date_from, 
                date_to=date_to, 
                methodology=method
            )
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(result).encode('utf-8'))
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({'error': str(e)}).encode('utf-8'))