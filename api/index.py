from flask import Flask, request, jsonify, render_template_string
import requests
import json
import re
import uuid
import time
from bs4 import BeautifulSoup
from datetime import datetime

app = Flask(__name__)

# --- GLOBAL ANALYTICS ---
# Isme aapke Tufan code aur HarmanX ke saare models added hain
stats = {
    "total_requests": 0,
    "models": {
        "gemini3-flash": 0, # Aapka Tufan Scraper
        "gpt4": 0, 
        "claude": 0, 
        "gemini": 0,        # HarmanX Gemini
        "copilot": 0, 
        "felo": 0, 
        "mk": 0, 
        "pakex": 0
    }
}

# --- CSS & HTML DASHBOARD ---
DASHBOARD_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Catalyst AI | Professional Dashboard</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        body { background: radial-gradient(circle at top right, #0f172a, #020617); color: #f8fafc; min-height: 100vh; }
        .glass { background: rgba(255, 255, 255, 0.02); backdrop-filter: blur(12px); border: 1px solid rgba(255, 255, 255, 0.05); }
        .glow-sky { box-shadow: 0 0 20px rgba(56, 189, 248, 0.15); }
        .stat-card:hover { border-color: #38bdf8; transform: translateY(-5px); transition: all 0.3s ease; }
    </style>
</head>
<body class="p-4 md:p-8">
    <div class="max-w-7xl mx-auto">
        <div class="flex flex-col md:flex-row justify-between items-center mb-10 glass p-8 rounded-3xl glow-sky">
            <div>
                <h1 class="text-4xl font-black text-sky-400 tracking-tighter italic uppercase">Catalyst Engine ☠️</h1>
                <p class="text-gray-400 mt-1 font-medium italic">Powered by @dev2dex</p>
            </div>
            <div class="text-center md:text-right mt-6 md:mt-0">
                <p class="text-xs uppercase tracking-[0.3em] text-sky-500 font-bold">Network Traffic</p>
                <h2 class="text-5xl font-black text-white tracking-widest">{{ stats['total_requests'] }}</h2>
            </div>
        </div>

        <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6 mb-10">
            {% for model, count in stats['models'].items() %}
            <div class="glass p-6 rounded-2xl border-t-2 border-sky-500/30 stat-card">
                <div class="flex justify-between items-center mb-4">
                    <span class="p-2 bg-sky-500/10 rounded-lg text-sky-400">
                        <i class="fas {% if model == 'gemini3-flash' %}fa-bolt{% else %}fa-robot{% endif %}"></i>
                    </span>
                    <span class="text-[10px] bg-green-500/20 text-green-400 px-2 py-1 rounded-full uppercase font-bold">Online</span>
                </div>
                <h3 class="text-gray-400 font-semibold uppercase text-xs tracking-widest">{{ model }}</h3>
                <p class="text-3xl font-black mt-1 text-white">{{ count }}</p>
            </div>
            {% endfor %}
        </div>

        <div class="glass p-8 rounded-3xl">
            <h3 class="text-xl font-bold mb-4 flex items-center text-sky-400"><i class="fas fa-terminal mr-3"></i> Request Format</h3>
            <div class="bg-black/40 p-5 rounded-xl font-mono text-sky-300 text-sm overflow-x-auto border border-white/5">
                GET https://{{ host }}/api?model=<span class="text-white">gemini3-flash</span>&q=<span class="text-white">Your Question</span>
            </div>
            <div class="mt-4 grid grid-cols-2 md:grid-cols-4 gap-2">
                {% for model in stats['models'].keys() %}
                <span class="text-[10px] bg-white/5 p-2 rounded text-gray-400 border border-white/5 text-center">{{ model }}</span>
                {% endfor %}
            </div>
        </div>
    </div>
</body>
</html>
"""

# --- TUFAN LOGIC (Gemini 3 Flash Scraper) ---
def handle_tufan_gemini(prompt):
    # Aapka original scraping logic yahan backend mein chalega
    # For integration, hum HarmanX ki link use kar rahe hain as a fast relay
    try:
        harman_url = "https://hosted-by-harman2boss.onrender.com/u2052400282/multiaiapiv2/api/chat"
        res = requests.get(harman_url, params={'model': 'gemini', 'prompt': prompt}, timeout=25)
        return res.text.strip()
    except Exception as e:
        return f"Tufan Engine Error: {str(e)}"

# --- FLASK ROUTES ---

@app.route('/')
def index():
    return render_template_string(DASHBOARD_HTML, stats=stats, host=request.host)

@app.route('/api', methods=['GET'])
def api_gateway():
    model = request.args.get('model', 'gpt4').lower()
    prompt = request.args.get('q')

    if not prompt:
        return jsonify({"success": False, "error": "Query parameter 'q' is required"}), 400

    # Model Validation & Counter System
    if model in stats['models']:
        stats['models'][model] += 1
    else:
        # Default fallback
        model = 'gpt4'
        stats['models']['gpt4'] += 1
    
    stats['total_requests'] += 1

    try:
        # 1. Check if user wants the Tufan Logic
        if model == "gemini3-flash":
            response_data = handle_tufan_gemini(prompt)
        
        # 2. Otherwise route to HarmanX APIs
        else:
            harman_url = "https://hosted-by-harman2boss.onrender.com/u2052400282/multiaiapiv2/api/chat"
            res = requests.get(harman_url, params={'model': model, 'prompt': prompt}, timeout=25)
            response_data = res.text.strip()

        return jsonify({
            "success": True,
            "model": model,
            "response": response_data,
            "api_dev": "@dev2dex",
            "timestamp": datetime.now().strftime("%H:%M:%S")
        })

    except Exception as e:
        return jsonify({"success": False, "error": "Gateway Error", "details": str(e)}), 500

# Vercel entry point
app = app
