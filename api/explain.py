from http.server import BaseHTTPRequestHandler
import json
import os
import requests

class handler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def do_POST(self):
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data)
            
            hf_token = os.environ.get("HF_TOKEN", "")
            
            prompt = f"""<|begin_of_text|><|start_header_id|>system<|end_header_id|>
You are an expert quantitative volatility trader. Analyze the following VIX/Volatility decomposition data and explain what it implies for the market in 2 short, punchy paragraphs. Be highly analytical. Use professional trader terminology (e.g., vanna, volga, skew, parallel shift, delta-hedging).
<|eot_id|><|start_header_id|>user<|end_header_id|>
Underlying: {data.get('underlying', 'Unknown')}
Spot Move: {data.get('spot', {}).get('pct_change', 0)}%
Volatility Change: {data.get('vix', {}).get('abs_change', 0)} pts
Parallel Shift: {data.get('factors', {}).get('parallel_shift', 0)} pts
Sticky Strike (Spot Delta): {data.get('factors', {}).get('sticky_strike', 0)} pts
Put Skew: {data.get('factors', {}).get('put_skew', 0)} pts
<|eot_id|><|start_header_id|>assistant<|end_header_id|>"""
            
            headers = {
                "Authorization": f"Bearer {hf_token}" if hf_token else "",
                "Content-Type": "application/json"
            }
            
            payload = {
                "inputs": prompt,
                "parameters": {"max_new_tokens": 250, "temperature": 0.6, "return_full_text": False}
            }
            
            if not hf_token:
                generated_text = "⚠️ <b>HF_TOKEN missing.</b><br/><br/>Please add your Hugging Face API Token in your Vercel Project Settings (Environment Variables) to enable the Llama 3 analysis engine."
            else:
                # Use the new Hugging Face Inference Router endpoint
                api_url = "https://router.huggingface.co/hf-inference/models/meta-llama/Meta-Llama-3-8B-Instruct"
                resp = requests.post(api_url, headers=headers, json=payload, timeout=15)
                
                if resp.status_code == 200:
                    result = resp.json()
                    generated_text = result[0].get('generated_text', '').strip()
                    generated_text = generated_text.replace('\n', '<br/>')
                elif resp.status_code == 503:
                    # Fallback to an ungated Qwen model if Llama 3 is down or spinning up
                    fallback_url = "https://router.huggingface.co/hf-inference/models/Qwen/Qwen2.5-32B-Instruct"
                    resp_fallback = requests.post(fallback_url, headers=headers, json=payload, timeout=15)
                    if resp_fallback.status_code == 200:
                        result = resp_fallback.json()
                        generated_text = result[0].get('generated_text', '').strip()
                        generated_text = generated_text.replace('\n', '<br/>')
                    else:
                        generated_text = "⏳ AI Engine is currently cold-booting on Hugging Face infrastructure. Please click analyze again in 30 seconds."
                elif resp.status_code in [401, 403]:
                    generated_text = "🔒 <b>Access Denied.</b><br/><br/>Ensure your HF_TOKEN is valid and that your Hugging Face account has been granted access to the Meta-Llama-3 repository."
                else:
                    generated_text = f"API Error {resp.status_code}: Could not generate insights."
                    
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({"analysis": generated_text}).encode('utf-8'))
            
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({"error": str(e)}).encode('utf-8'))