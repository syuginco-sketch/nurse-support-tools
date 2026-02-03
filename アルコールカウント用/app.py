import streamlit as st
import streamlit.components.v1 as components

# 画面を横長に設定
st.set_page_config(layout="wide", page_title="退院支援システム")

# HTMLコードを変数に格納
html_code = """
<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>アルコール使用量 総合分析システム</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        :root { --primary: #1a73e8; --success: #28a745; --danger: #dc3545; --bg: #f8f9fa; }
        body { font-family: "Segoe UI", Meiryo, sans-serif; background-color: var(--bg); color: #333; margin: 0; padding: 20px; }
        .container { max-width: 1200px; margin: 0 auto; }
        .card { background: white; padding: 20px; border-radius: 12px; box-shadow: 0 2px 10px rgba(0,0,0,0.05); margin-bottom: 20px; }
        h1 { text-align: center; color: var(--primary); margin-bottom: 30px; }
        h2 { border-left: 5px solid var(--primary); padding-left: 10px; font-size: 1.2em; color: var(--primary); }
        
        .setup-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; }
        label { display: block; font-size: 0.85em; font-weight: bold; margin-top: 10px; }
        input, select { width: 100%; padding: 10px; margin-top: 5px; border: 1px solid #ddd; border-radius: 6px; box-sizing: border-box; }
        
        .btn { padding: 10px 15px; border: none; border-radius: 6px; cursor: pointer; font-weight: bold; transition: 0.2s; margin-top: 10px; }
        .btn-primary { background: var(--primary); color: white; }
        .btn-success { background: var(--success); color: white; }
        .btn-danger { background: var(--danger); color: white; font-size: 0.8em; padding: 5px; }
        
        table { width: 100%; border-collapse: collapse; margin-top: 15px; }
        th, td { border: 1px solid #eee; padding: 10px; text-align: center; }
        th { background: #f1f3f4; }
        
        .chart-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-top: 20px; }
        .chart-box { min-height: 300px; border: 1px solid #f0f0f0; padding: 10px; border-radius: 8px; }
        .summary-stats { display: flex; gap: 15px; margin: 20px 0; }
        .stat-item { flex: 1; background: #e8f0fe; padding: 15px; border-radius: 10px; text-align: center; }
        .stat-item b { display: block; font-size: 1.5em; color: var(--primary); }

        .tab-btn { padding: 10px 20px; cursor: pointer; border: none; background: #ddd; border-radius: 5px 5px 0 0; }
        .tab-btn.active { background: white; border: 1px solid #ddd; border-bottom: none; font-weight: bold; }
    </style>
</head>
<body>

<div class="container">
    <h1>🏥 アルコール使用量 総合分析ダッシュボード</h1>

    <div class="setup-grid">
        <div class="card">
            <h2>部署・フロア設定</h2>
            <div style="display:flex; gap:5px;">
                <input type="text" id="deptInput" placeholder="例: 3F病棟、リハビリ科">
                <button class="btn btn-primary" onclick="addDept()">追加</button>
            </div>
            <div id="deptList" style="margin-top:10px; display:flex; flex-wrap:wrap; gap:5px;"></div>
        </div>

        <div class="card">
            <h2>銘柄設定</h2>
            <div style="display:flex; gap:5px;">
                <input type="text" id="itemName" placeholder="名称" style="flex:2">
                <input type="number" id="itemMl" placeholder="ml/push" style="flex:1" step="0.1">
                <button class="btn btn-primary" onclick="addItem()">追加</button>
            </div>
            <div id="itemListDisplay" style="margin-top:10px; font-size:0.85em;"></div>
        </div>
    </div>

    <div class="card">
        <h2>データ入力シート</h2>
        <div style="display:flex; gap:15px; align-items:flex-end;">
            <div style="flex:1"><label>対象月</label><input type="month" id="workMonth" onchange="refreshInputs()"></div>
            <div style="flex:1"><label>部署選択</label><select id="deptSelect" onchange="refreshInputs()"></select></div>
            <button class="btn btn-primary" style="margin-bottom:0;" onclick="copyPrev()">前月の構成をコピー</button>
        </div>

        <table id="inputTable">
            <thead>
                <tr><th>日付</th><th>対象名 (部屋/個人)</th><th>銘柄</th><th>使用量(ml)</th><th>操作</th></tr>
            </thead>
            <tbody id="inputBody"></tbody>
        </table>
        <button class="btn btn-success" style="width:100%" onclick="saveDailyData()">この部署のデータを保存</button>

        <h3 style="margin-top:20px; font-size:1em;">この部署の患者数入力</h3>
        <div id="censusContainer" class="setup-grid" style="grid-template-columns: repeat(auto-fill, minmax(60px, 1fr));"></div>
        <button class="btn btn-success" onclick="saveCensus()">患者数を保存</button>
    </div>

    <div class="card">
        <h2>分析レポート</h2>
        <div style="display:flex; gap:10px;">
            <input type="month" id="viewMonth">
            <button class="btn btn-primary" onclick="generateReport()" style="margin:0">レポート生成</button>
        </div>

        <div id="reportSection" style="display:none;">
            <div class="summary-stats">
                <div class="stat-item">病院全体プッシュ<b><span id="totalPush">0</span>回</b></div>
                <div class="stat-item">延べ患者数<b><span id="totalCen">0</span>名</b></div>
                <div class="stat-item">病院全体平均<b><span id="totalAvg">0</span>回</b></div>
            </div>

            <div class="chart-grid">
                <div class="chart-box"><canvas id="chartDept"></canvas></div>
                <div class="chart-box"><canvas id="chartItem"></canvas></div>
                <div class="chart-box"><canvas id="chartDaily"></canvas></div>
                <div class="chart-box"><canvas id="chartTrend"></canvas></div>
            </div>
        </div>
    </div>
</div>

<script>
let depts = JSON.parse(localStorage.getItem('v4_depts')) || [];
let items = JSON.parse(localStorage.getItem('v4_items')) || [];
let logs = JSON.parse(localStorage.getItem('v4_logs')) || {}; 
let census = JSON.parse(localStorage.getItem('v4_census')) || {};

let charts = {};

window.onload = () => {
    const now = new Date().toISOString().slice(0, 7);
    document.getElementById('workMonth').value = now;
    document.getElementById('viewMonth').value = now;
    renderDepts();
    renderItems();
    refreshInputs();
};

function addDept() {
    const val = document.getElementById('deptInput').value;
    if(val) { depts.push(val); localStorage.setItem('v4_depts', JSON.stringify(depts)); renderDepts(); }
    document.getElementById('deptInput').value = '';
}

function renderDepts() {
    document.getElementById('deptList').innerHTML = depts.map((d,i)=>`<span class="stat-item" style="padding:5px;">${d} <button onclick="depts.splice(${i},1);renderDepts();" class="btn-danger">×</button></span>`).join('');
    const sel = document.getElementById('deptSelect');
    sel.innerHTML = depts.map(d=>`<option value="${d}">${d}</option>`).join('');
}

function addItem() {
    const n = document.getElementById('itemName').value;
    const m = document.getElementById('itemMl').value;
    if(n && m) { items.push({name:n, ml:parseFloat(m)}); localStorage.setItem('v4_items', JSON.stringify(items)); renderItems(); }
}

function renderItems() {
    document.getElementById('itemListDisplay').innerHTML = items.map((it,i)=>`<div>${it.name} (${it.ml}ml) <button onclick="items.splice(${i},1);renderItems();" class="btn-danger">×</button></div>`).join('');
}

function refreshInputs() {
    const month = document.getElementById('workMonth').value;
    const dept = document.getElementById('deptSelect').value;
    const body = document.getElementById('inputBody');
    body.innerHTML = '';
    
    const key = `${month}_${dept}`;
    const data = logs[key] || [];
    data.forEach((row, i) => {
        body.innerHTML += `<tr>
            <td><input type="number" value="${row.day}" style="width:45px" onchange="updateLogData(${i},'day',this.value)"></td>
            <td><input type="text" value="${row.name}" onchange="updateLogData(${i},'name',this.value)"></td>
            <td><select onchange="updateLogData(${i},'itemIdx',this.value)">${items.map((it,idx)=>`<option value="${idx}" ${row.itemIdx==idx?'selected':''}>${it.name}</option>`).join('')}</select></td>
            <td><input type="number" value="${row.ml}" onchange="updateLogData(${i},'ml',this.value)" onkeydown="if(event.key==='Enter')addRow()"></td>
            <td><button class="btn-danger" onclick="deleteRow(${i})">削除</button></td>
        </tr>`;
    });
    body.innerHTML += `<tr><td colspan="5"><button class="btn btn-primary" onclick="addRow()">+ 行追加</button></td></tr>`;
    
    // 患者数
    const cCon = document.getElementById('censusContainer');
    cCon.innerHTML = '';
    const days = new Date(month.split('-')[0], month.split('-')[1], 0).getDate();
    const cData = census[key] || Array(days).fill(0);
    for(let i=0; i<days; i++) {
        cCon.innerHTML += `<div style="text-align:center">${i+1}日<input type="number" class="c-in" value="${cData[i]}" onkeydown="if(event.key==='Enter')this.parentElement.nextElementSibling.querySelector('input').focus()"></div>`;
    }
}

function addRow() {
    const month = document.getElementById('workMonth').value;
    const dept = document.getElementById('deptSelect').value;
    const key = `${month}_${dept}`;
    if(!logs[key]) logs[key] = [];
    logs[key].push({day: new Date().getDate(), name: '', itemIdx: 0, ml: 0});
    refreshInputs();
}

function updateLogData(i, k, v) {
    const key = `${document.getElementById('workMonth').value}_${document.getElementById('deptSelect').value}`;
    logs[key][i][k] = (k==='ml'||k==='day'||k==='itemIdx') ? parseFloat(v) : v;
}

function deleteRow(i) {
    const key = `${document.getElementById('workMonth').value}_${document.getElementById('deptSelect').value}`;
    logs[key].splice(i, 1);
    refreshInputs();
}

function saveDailyData() { localStorage.setItem('v4_logs', JSON.stringify(logs)); alert("部署データを保存しました"); }
function saveCensus() {
    const key = `${document.getElementById('workMonth').value}_${document.getElementById('deptSelect').value}`;
    census[key] = Array.from(document.querySelectorAll('.c-in')).map(el=>parseInt(el.value)||0);
    localStorage.setItem('v4_census', JSON.stringify(census));
    alert("患者数を保存しました");
}

function copyPrev() {
    const currentMonth = document.getElementById('workMonth').value;
    const dept = document.getElementById('deptSelect').value;
    const d = new Date(currentMonth + "-01");
    d.setMonth(d.setMonth()-1);
    const prevKey = `${d.toISOString().slice(0, 7)}_${dept}`;
    if(!logs[prevKey]) return alert("前月データなし");
    logs[`${currentMonth}_${dept}`] = logs[prevKey].map(r=>({...r, ml:0}));
    refreshInputs();
}

function generateReport() {
    const month = document.getElementById('viewMonth').value;
    document.getElementById('reportSection').style.display = 'block';

    let totalPush = 0;
    let totalCen = 0;
    let deptStats = {};
    let itemStats = {};
    let dailyPush = Array(31).fill(0);
    let itemTrend = {}; // {itemName: [31days]}

    items.forEach(it => itemTrend[it.name] = Array(31).fill(0));

    depts.forEach(d => {
        const key = `${month}_${d}`;
        // ログ集計
        (logs[key] || []).forEach(l => {
            const p = l.ml / (items[l.itemIdx]?.ml || 1);
            totalPush += p;
            deptStats[d] = (deptStats[d] || 0) + p;
            itemStats[items[l.itemIdx].name] = (itemStats[items[l.itemIdx].name] || 0) + p;
            if(l.day <= 31) {
                dailyPush[l.day-1] += p;
                if(itemTrend[items[l.itemIdx].name]) itemTrend[items[l.itemIdx].name][l.day-1] += p;
            }
        });
        // 患者数
        totalCen += (census[key] || []).reduce((a,b)=>a+b, 0);
    });

    document.getElementById('totalPush').innerText = Math.round(totalPush).toLocaleString();
    document.getElementById('totalCen').innerText = totalCen.toLocaleString();
    document.getElementById('totalAvg').innerText = totalCen > 0 ? (totalPush / totalCen).toFixed(2) : 0;

    renderChart('chartDept', 'bar', '部署別プッシュ数', Object.keys(deptStats), Object.values(deptStats), '#1a73e8');
    renderChart('chartItem', 'pie', '銘柄別シェア', Object.keys(itemStats), Object.values(itemStats));
    renderChart('chartDaily', 'line', '病院全体 日次推移', Array.from({length:31},(_,i)=>i+1), dailyPush, '#28a745');
    
    // 銘柄別トレンド（複数線）
    if(charts['chartTrend']) charts['chartTrend'].destroy();
    charts['chartTrend'] = new Chart(document.getElementById('chartTrend'), {
        type: 'line',
        data: {
            labels: Array.from({length:31},(_,i)=>i+1),
            datasets: Object.keys(itemTrend).map((name, idx) => ({
                label: name,
                data: itemTrend[name],
                borderColor: `hsl(${idx * 137.5}, 70%, 50%)`,
                fill: false
            }))
        },
        options: { responsive: true, plugins: { title: { display: true, text: '銘柄別使用推移' } } }
    });
}

function renderChart(id, type, label, labels, data, color) {
    if(charts[id]) charts[id].destroy();
    charts[id] = new Chart(document.getElementById(id), {
        type: type,
        data: {
            labels: labels,
            datasets: [{ label: label, data: data, backgroundColor: color || ['#4285f4','#34a853','#fbbc05','#ea4335','#af5cf7'] }]
        },
        options: { responsive: true, plugins: { title: { display: true, text: label } } }
    });
}
</script>
</body>
</html>"""

# StreamlitのコンポーネントとしてHTMLを表示
components.html(html_code, height=1200, scrolling=True)