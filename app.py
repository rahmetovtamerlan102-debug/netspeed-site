from flask import Flask, jsonify, request, render_template_string
import threading, time, requests

app = Flask(__name__)

state = {
    "running": False,
    "requests": 0,
    "errors": 0,
    "concurrency": 0,
    "rps": 0.0
}

lock = threading.Lock()
stop_event = threading.Event()

HTML = """
<!DOCTYPE html>
<html>
<head>
<title>Load Test (safe)</title>
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<style>
body{background:#0f172a;color:#fff;font-family:Arial;text-align:center}
button{padding:12px 18px;margin:6px;border:none;border-radius:10px;cursor:pointer}
.main{background:#00ffd5;color:#000}
.mode{background:#ffffff22;color:#fff}
.card{margin:12px auto;width:260px;padding:16px;background:#ffffff11;border-radius:14px}
</style>
</head>
<body>
<h1>⚡ Safe Load Test</h1>

<div>
  <button class="mode" onclick="start('low')">Лёгкий (5–15)</button>
  <button class="mode" onclick="start('medium')">Средний (15–40)</button>
  <button class="mode" onclick="start('high')">Высокий (40–80)</button>
</div>

<div>
  <button class="main" onclick="stop()">⛔ Стоп</button>
</div>

<div class="card">
  <p>Статус: <b id="st">OFF</b></p>
  <p>Параллельность: <span id="cc">0</span></p>
  <p>RPS: <span id="rps">0</span></p>
  <p>Requests: <span id="req">0</span></p>
  <p>Errors: <span id="err">0</span></p>
</div>

<script>
function start(mode){ fetch('/start?mode='+mode); }
function stop(){ fetch('/stop'); }

setInterval(async ()=>{
  let r = await fetch('/stats'); let d = await r.json();
  document.getElementById('st').innerText = d.running ? 'ON' : 'OFF';
  document.getElementById('cc').innerText = d.concurrency;
  document.getElementById('rps').innerText = d.rps.toFixed(1);
  document.getElementById('req').innerText = d.requests;
  document.getElementById('err').innerText = d.errors;
}, 1000);
</script>
</body>
</html>
"""

@app.route("/")
def home():
    return render_template_string(HTML)

def worker(url):
    session = requests.Session()
    while not stop_event.is_set():
        try:
            resp = session.get(url, timeout=5)
            with lock:
                state["requests"] += 1
        except:
            with lock:
                state["errors"] += 1

def run_test(target_url, target_concurrency, ramp_seconds=10):
    # плавный рост параллельности
    threads = []
    start_time = time.time()
    last_req = 0

    for i in range(1, target_concurrency + 1):
        if stop_event.is_set():
            break
        t = threading.Thread(target=worker, args=(target_url,), daemon=True)
        t.start()
        threads.append(t)
        with lock:
            state["concurrency"] = i
        # ramp-up
        time.sleep(max(0.01, ramp_seconds / max(1, target_concurrency)))

    # расчёт RPS
    while not stop_event.is_set():
        time.sleep(1)
        with lock:
            cur = state["requests"]
            state["rps"] = cur - last_req
            last_req = cur

@app.route("/start")
def start():
    mode = request.args.get("mode", "low")
    # разумные диапазоны
    if mode == "low":
        target = 10
    elif mode == "medium":
        target = 30
    else:
        target = 60  # high

    if not state["running"]:
        stop_event.clear()
        with lock:
            state["running"] = True
            state["requests"] = 0
            state["errors"] = 0
            state["concurrency"] = 0
            state["rps"] = 0.0

        # ТОЛЬКО свой сайт!
        url = "https://netspeed-site.onrender.com"

        threading.Thread(target=run_test, args=(url, target, 10), daemon=True).start()

    return "started"

@app.route("/stop")
def stop():
    stop_event.set()
    with lock:
        state["running"] = False
        state["concurrency"] = 0
        state["rps"] = 0.0
    return "stopped"

@app.route("/stats")
def stats():
    with lock:
        return jsonify(state)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
