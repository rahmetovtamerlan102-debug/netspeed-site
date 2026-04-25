from flask import Flask, jsonify, render_template_string
import random

app = Flask(__name__)

data = {
    "time": [],
    "requests": [],
    "errors": [],
    "users": []
}

HTML = """
<!DOCTYPE html>
<html>
<head>
<title>NetSpeed PRO</title>
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>

<style>
body {
    margin:0;
    font-family: Arial;
    background: linear-gradient(135deg,#0f2027,#203a43,#2c5364);
    color:white;
    text-align:center;
}

h1 {margin-top:20px;}

button {
    padding:15px 25px;
    font-size:18px;
    border:none;
    border-radius:10px;
    background:#00ffcc;
    color:black;
    cursor:pointer;
}

.card {
    margin:15px auto;
    width:220px;
    padding:20px;
    border-radius:15px;
    background:rgba(255,255,255,0.1);
}

ul {list-style:none;padding:0;}
</style>
</head>

<body>

<h1>⚡ NetSpeed PRO</h1>

<button onclick="startTest()">НАЧАТЬ ТЕСТ</button>

<div class="card">
<h3>📡 Ping</h3>
<p id="ping">-</p>
</div>

<div class="card">
<h3>⬇ Download</h3>
<p id="down">-</p>
</div>

<div class="card">
<h3>⬆ Upload</h3>
<p id="up">-</p>
</div>

<h2>📊 История</h2>
<ul id="history"></ul>

<canvas id="chart"></canvas>

<script>
let history = [];
let chart;

function startTest() {
    fetch('/speed')
    .then(r=>r.json())
    .then(d=>{

        document.getElementById('ping').innerText = d.ping;
        document.getElementById('down').innerText = d.download;
        document.getElementById('up').innerText = d.upload;

        let result = d.download + "↓ | " + d.upload + "↑ | " + d.ping;

        history.push(result);

        let list = document.getElementById('history');
        list.innerHTML="";
        history.slice().reverse().forEach(i=>{
            let li=document.createElement("li");
            li.innerText=i;
            list.appendChild(li);
        });
    });
}

async function updateChart(){
    let res = await fetch('/data');
    let d = await res.json();

    if(!chart){
        chart = new Chart(document.getElementById('chart'),{
            type:'line',
            data:{
                labels:d.time,
                datasets:[
                    {label:'Requests', data:d.requests},
                    {label:'Errors', data:d.errors},
                    {label:'Users', data:d.users}
                ]
            }
        });
    } else {
        chart.data.labels = d.time;
        chart.data.datasets[0].data = d.requests;
        chart.data.datasets[1].data = d.errors;
        chart.data.datasets[2].data = d.users;
        chart.update();
    }
}

setInterval(updateChart,1000);
</script>

</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(HTML)

@app.route('/speed')
def speed():
    return jsonify({
        "download": round(random.uniform(10,100),2),
        "upload": round(random.uniform(5,50),2),
        "ping": round(random.uniform(5,100),2)
    })

@app.route('/data')
def data_api():
    data["time"].append(len(data["time"]))
    data["requests"].append(random.randint(50,200))
    data["errors"].append(random.randint(0,10))
    data["users"].append(random.randint(5,50))

    return jsonify(data)

app.run(host="0.0.0.0", port=5000)
