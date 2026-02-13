from flask import Flask, request, jsonify, render_template_string
import requests

app = Flask(__name__)

# --- CONFIGURATION ---
SOURCE_API_URL = "https://hosted-by-harman2boss.onrender.com/u2052400282/multiaiapiv2/api/chat"

# NOTE: In-memory stats will reset when Vercel function goes idle.
# For permanent stats, connect a database like MongoDB or Upstash Redis.
stats = {
    "total_requests": 0,
    "models": {
        "gpt4": 0,
        "claude": 0,
        "gemini": 0,
        "copilot": 0,
        "felo": 0,
        "mk": 0,
        "pakex": 0
    }
}

# --- PROFESSIONAL DASHBOARD UI ---
DASHBOARD_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Catalyst AI | API Analytics</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        body { background-color: #050505; color: #e5e5e5; }
        .glass { background: rgba(255, 255, 255, 0.03); backdrop-filter: blur(10px); border: 1px solid rgba(255, 255, 255, 0.1); }
        .stat-card:hover { border-color: #38bdf8; transition: 0.3s; }
    </style>
</head>
<body class="p-4 md:p-10">
    <div class="max-w-6xl mx-auto">
        <div class="flex flex-col md:flex-row justify-between items-center mb-10 glass p-6 rounded-2xl">
            <div>
                <h1 class="text-3xl font-bold text-sky-400"><i class="fas fa-microchip mr-2"></i>Catalyst AI Wrapper</h1>
                <p class="text-gray-400">High-Performance AI Model Gateway</p>
            </div>
            <div class="mt-4 md:mt-0 text-center md:text-right">
                <span class="text-xs font-mono text-sky-500 uppercase tracking-widest">Global Traffic</span>
                <div class="text-4xl font-black text-white">{{ stats['total_requests'] }}</div>
            </div>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {% for model, count in stats['models'].items() %}
            <div class="glass p-6 rounded-2xl stat-card">
                <div class="flex justify-between items-start mb-4">
                    <div class="p-3 bg-sky-500/10 rounded-lg">
                        <i class="fas fa-robot text-sky-400"></i>
                    </div>
                    <span class="text-xs font-mono text-gray-500">Live</span>
                </div>
                <h3 class="text-lg font-semibold capitalize">{{ model }}</h3>
                <p class="text-3xl font-bold mt-2">{{ count }} <span class="text-sm font-normal text-gray-500">reqs</span></p>
            </div>
            {% endfor %}
        </div>

        <div class="mt-10 glass p-6 rounded-2xl">
            <h2 class="text-xl font-bold mb-4 text-sky-400">API Documentation</h2>
            <div class="bg-black/50 p-4 rounded-lg font-mono text-sm text-green-400 overflow-x-auto">
                GET /api?model={model_name}&q={your_prompt}
            </div>
        </div>
    </div>
</body>
</html>
"""

# --- ROUTES ---

@app.route('/')
def index():
    return render_template_string(DASHBOARD_HTML, stats=stats)

@app.route('/api', methods=['GET'])
def ai_wrapper():
    model_choice = request.args.get('model', 'gpt4').lower()
    prompt = request.args.get('q')

    if not prompt:
        return jsonify({"error": "Query parameter 'q' is missing"}), 400

    # Model Validation & Counter
    if model_choice in stats['models']:
        stats['models'][model_choice] += 1
        stats['total_requests'] += 1
    else:
        # If model not in list, default to gpt4 but don't count extra
        model_choice = 'gpt4'
        stats['models']['gpt4'] += 1
        stats['total_requests'] += 1

    params = {'model': model_choice, 'prompt': prompt}

    try:
        # Fast API fetch
        response = requests.get(SOURCE_API_URL, params=params, timeout=25)
        
        if response.status_code == 200:
            return jsonify({
                "status": "success",
                "model": model_choice,
                "data": response.text.strip()
            })
        else:
            return jsonify({"error": "Provider API offline", "code": response.status_code}), 502

    except Exception as e:
        return jsonify({"error": "Internal Gateway Timeout", "details": str(e)}), 500

# For Vercel, the app object needs to be exposed
app = app
