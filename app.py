from flask import Flask, render_template_string
import requests, time, threading, statistics, os

app = Flask(__name__)

# ---------- PING ----------
def ping_test():
    times = []
    for _ in range(4):
        try:
            start = time.time()
            requests.get("https://www.google.com", timeout=2)
            times.append((time.time() - start) * 1000)
        except:
            pass
    return round(statistics.mean(times), 2) if times else 0

# ---------- DOWNLOAD ----------
def download_test():
    url = "http://speedtest.tele2.net/5MB.zip"
    results = []

    def worker():
        try:
            start = time.time()
            r = requests.get(url, timeout=10)
            size = len(r.content) / 1024 / 1024
            results.append(size / (time.time() - start))
        except:
            pass

    threads = []
    for _ in range(2):  # меньше потоков = стабильнее
        t = threading.Thread(target=worker)
        t.start()
        threads.append(t)

    for t in threads:
        t.join()

    return round(sum(results), 2) if results else 0

# ---------- UPLOAD ----------
def upload_test():
    data = "x" * 2000000  # 2MB
    start = time.time()
    try:
        requests.post("https://httpbin.org/post", data=data, timeout=10)
        return round(2 / (time.time() - start), 2)
    except:
        return 0

# ---------- HTML ----------
HTML = """
<!DOCTYPE html>
<html>
<head>
<title>NetSpeed Pro</title>
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<style>
body {
    margin:0;
    font-family: Arial;
    background: linear-gradient(135deg,#0f2027,#203a43,#2c5364);
    color:white;
    text-align:center;
}

h1 {
    margin-top:30px;
    font-size:32px;
}

.container {
    margin-top:40px;
}

.card {
    background: rgba(255,255,255,0.1);
    padding:20px;
    margin:10px;
    border-radius:15px;
    display:inline-block;
    width:140px;
}

button {
    margin-top:20px;
    padding:15px 25px;
    font-size:16px;
    border:none;
    border-radius:10px;
    background:#00ffcc;
    cursor:pointer;
}

.loader {
    margin:20px auto;
    border:6px solid #fff;
    border-top:6px solid #00ffcc;
    border-radius:50%;
    width:40px;
    height:40px;
    animation:spin 1s linear infinite;
}

@keyframes spin {
    100% { transform: rotate(360deg); }
}
</style>
</head>

<body>

<h1>⚡ NetSpeed Pro</h1>

<form action="/test">
<button>НАЧАТЬ ТЕСТ</button>
</form>

{% if loading %}
<div class="loader"></div>
<p>Проверка...</p>
{% endif %}

{% if data %}
<div class="container">
<div class="card">
<p>📡 Ping</p>
<h2>{{data.ping}}</h2>
</div>

<div class="card">
<p>⬇️ Down</p>
<h2>{{data.download}}</h2>
</div>

<div class="card">
<p>⬆️ Up</p>
<h2>{{data.upload}}</h2>
</div>
</div>
{% endif %}

</body>
</html>
"""

# ---------- ROUTES ----------
@app.route("/")
def home():
    return render_template_string(HTML, data=None)

@app.route("/test")
def test():
    ping = ping_test()
    download = download_test()
    upload = upload_test()

    data = {
        "ping": ping,
        "download": download,
        "upload": upload
    }

    return render_template_string(HTML, data=data)

# ---------- RUN ----------
port = int(os.environ.get("PORT", 5000))
app.run(host="0.0.0.0", port=port)
