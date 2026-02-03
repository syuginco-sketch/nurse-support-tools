import streamlit as st
import streamlit.components.v1 as components

# 画面を横長に設定
st.set_page_config(layout="wide", page_title="退院支援システム")

# HTMLコードを変数に格納
html_code = """
<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width,initial-scale=1" />
<title>退院支援マネジメントシステム</title>
<style>
  :root { --primary: #2c3e50; --accent: #e67e22; --bg: #f4f6f9; --border: #dee2e6; font-size: 14px; }
  body { font-family: "Meiryo", "Yu Gothic", sans-serif; margin: 0; padding: 15px; background: var(--bg); color: #333; }
  .container { max-width: 1600px; margin: 0 auto; background: #fff; padding: 20px; border-radius: 4px; box-shadow: 0 0 10px rgba(0,0,0,0.1); }
  .header { display: flex; justify-content: space-between; align-items: center; border-bottom: 3px solid var(--primary); margin-bottom: 15px; padding-bottom: 10px; }
  .controls { display: flex; gap: 8px; }
  .print-only-title { display: none; }
  .ai-input-area { background: #eef2f7; padding: 12px; border-radius: 4px; margin-bottom: 15px; border: 1px solid #d1d9e4; }
  textarea { width: 100%; border: 1px solid #ccc; border-radius: 4px; padding: 6px; font-family: inherit; box-sizing: border-box; resize: vertical; }
  .input-form { background: #fff; border: 1px solid var(--border); padding: 15px; border-radius: 4px; margin-bottom: 20px; }
  .grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(150px, 1fr)); gap: 10px; }
  .col-full { grid-column: 1 / -1; }
  .col-half { grid-column: span 2; }
  label { font-weight: bold; font-size: 0.8rem; color: #555; display: block; margin-bottom: 3px; }
  input, select { width: 100%; padding: 6px; border: 1px solid #ccc; border-radius: 3px; box-sizing: border-box; }
  button { cursor: pointer; border: none; padding: 8px 16px; border-radius: 3px; font-weight: bold; }
  .btn-main { background: var(--primary); color: white; }
  .btn-sub { background: #6c757d; color: white; }
  .btn-accent { background: var(--accent); color: white; }
  .btn-success { background: #27ae60; color: white; }
  table { width: 100%; border-collapse: collapse; font-size: 0.8rem; min-width: 1300px; }
  th, td { border: 1px solid #999; padding: 4px; text-align: left; vertical-align: top; line-height: 1.2; }
  th { background: #eee; text-align: center; white-space: nowrap; }
  .status-warning { color: #d9534f; font-weight: bold; }
  .status-expired { color: #007bff; font-weight: bold; }
  @media print {
    @page { size: A4 landscape; margin: 5mm; }
    .no-print { display: none !important; }
    .print-only-title { display: block; text-align: center; font-size: 1.4rem; font-weight: bold; margin-bottom: 5px; }
    table { width: 100%; table-layout: fixed; }
    th, td { font-size: 7.2pt; padding: 1.5px; border: 1px solid #000; overflow-wrap: break-word; }
    .col-op { display: none !important; }
  }
</style>
</head>
<body>
<div class="container">
  <div class="header no-print">
    <h1>退院支援マネジメントシステム</h1>
    <div class="controls">
      <input type="file" id="fileInput" accept=".json" style="display:none;" onchange="importData(event)">
      <button class="btn-success" onclick="exportData()">💾 保存</button>
      <button class="btn-sub" onclick="document.getElementById('fileInput').click()">📂 読込</button>
      <button class="btn-accent" onclick="window.print()">🖨️ 印刷</button>
    </div>
  </div>
  <div class="print-only-title">退院支援 患者一覧表</div>
  <div class="ai-input-area no-print">
    <label>🤖 ユビーAIや電子カルテの情報を解析</label>
    <textarea id="aiText" rows="2" placeholder="ここに情報を貼り付けて「解析反映」をクリック"></textarea>
    <button class="btn-main" style="margin-top:5px;" onclick="parseContent()">解析反映</button>
  </div>
  <div class="input-form no-print">
    <div class="grid">
      <div class="col-half"><label>氏名</label><div style="display:flex; gap:3px;"><input type="text" id="lastName" placeholder="姓"><input type="text" id="firstName" placeholder="名"></div></div>
      <div><label>病棟</label><input type="text" id="ward"></div>
      <div><label>性別</label><select id="gender"><option value="">-</option><option value="男">男</option><option value="女">女</option></select></div>
      <div><label>入院日</label><input type="date" id="admDate"></div>
      <div><label>担当看護師</label><input type="text" id="nurse"></div>
      <div><label>主治医</label><input type="text" id="doc"></div>
      <div><label>リハ担当</label><input type="text" id="rehab"></div>
      <div class="col-half"><label>家族構成・キーパーソン</label><input type="text" id="family"></div>
      <div><label>介護度</label><input type="text" id="careLevel"></div>
      <div><label>ケアマネ</label><input type="text" id="cm"></div>
      <div class="col-half"><label>入院目的</label><input type="text" id="purpose"></div>
      <div class="col-half"><label>退院先</label><input type="text" id="dest"></div>
      <div class="col-full"><label>現在の状況・問題点</label><textarea id="status" rows="2"></textarea></div>
      <div class="col-half"><label>目標ADL</label><textarea id="goal" rows="2"></textarea></div>
      <div class="col-half"><label>今後必要なサービス</label><textarea id="service" rows="2"></textarea></div>
      <div class="col-full"><label>連携状況・経過記録</label><textarea id="progress" rows="2"></textarea></div>
    </div>
    <div style="margin-top:10px;"><button id="mainBtn" class="btn-main" onclick="addPatient()">登録</button> <button class="btn-sub" onclick="resetForm()">クリア</button></div>
  </div>
  <div class="table-area">
    <table>
      <thead>
        <tr>
          <th style="width:65px;">入院日/期限</th><th style="width:30px;">病棟</th><th style="width:80px;">氏名</th><th style="width:25px;">性</th>
          <th style="width:120px;">病院担当/家族構成</th><th>現在の状況/入院目的</th><th>目標ADL</th><th>サービス/CM</th>
          <th style="width:75px;">退院先</th><th style="width:60px;" class="no-print col-op">操作</th>
        </tr>
      </thead>
      <tbody id="pTable"></tbody>
    </table>
  </div>
</div>
<script>
  let patients = JSON.parse(localStorage.getItem('hosp_v_final_master') || '[]');
  let editIdx = -1;
  function getDeadlineInfo(admDateStr, days) {
    if(!admDateStr) return { date: '', class: '' };
    const deadlineDate = new Date(admDateStr);
    deadlineDate.setDate(deadlineDate.getDate() + days);
    const today = new Date(); today.setHours(0,0,0,0);
    const diffDays = Math.ceil((deadlineDate - today) / (1000 * 60 * 60 * 24));
    let className = '';
    if (diffDays < 0) className = 'status-expired';
    else if (diffDays <= 14) className = 'status-warning';
    return { date: `${deadlineDate.getMonth() + 1}/${deadlineDate.getDate()}`, class: className };
  }
  function parseContent() {
    const txt = document.getElementById('aiText').value;
    if(!txt) return;
    const mapping = [
      { id: 'lastName', regex: /(?:氏名|名前|患者)[:：]\s*([^\n\r\s　]+)/ },
      { id: 'firstName', regex: /(?:氏名|名前|患者)[:：]\s*[^\n\r\s　]+[\s　]+([^\n\r\s　]+)/ },
      { id: 'ward', regex: /(?:病棟|場所)[:：]\s*([^\n\r\s]+)/ },
      { id: 'gender', regex: /(?:性別)[:：]\s*(男|女)/ },
      { id: 'admDate', regex: /(?:入院日)[:：]\s*([\d\/\-]+)/ },
      { id: 'nurse', regex: /(?:担当|看護師)[:：]\s*([^\n\r\s]+)/ },
      { id: 'doc', regex: /(?:主治医|医師)[:：]\s*([^\n\r\s]+)/ },
      { id: 'rehab', regex: /(?:リハ担当|リハ|PT|OT|ST)[:：]\s*([^\n\r\s]+)/ },
      { id: 'careLevel', regex: /(?:介護度|要介護度)[:：]\s*([^\n\r\s]+)/ },
      { id: 'cm', regex: /(?:ケアマネ|CM)[:：]\s*([^\n\r\s]+)/ },
      { id: 'purpose', regex: /(?:入院目的|診断|疾患)[:：]\s*([^\n\r]+)/ },
      { id: 'family', regex: /(?:家族構成|家族|同居|キーパーソン)[:：]\s*([^\n\r]+)/ },
      { id: 'dest', regex: /(?:退院先|転先)[:：]\s*([^\n\r]+)/ },
      { id: 'status', regex: /(?:状況|問題点|現在の状態)[:：]\s*([^\n\r]+)/ },
      { id: 'goal', regex: /(?:目標ADL|目標)[:：]\s*([^\n\r]+)/ },
      { id: 'service', regex: /(?:必要サービス|今後のサービス)[:：]\s*([^\n\r]+)/ },
      { id: 'progress', regex: /(?:連携状況|経過|記録)[:：]\s*([^\n\r]+)/ }
    ];
    mapping.forEach(m => {
      const match = txt.match(m.regex);
      if(match && match[1]) {
        let val = match[1].trim();
        if(m.id === 'admDate') {
          val = val.replace(/\//g,'-');
          if(val.length === 8 && !val.includes('-')) val = val.replace(/(\d{4})(\d{2})(\d{2})/,'$1-$2-$3');
        }
        if(document.getElementById(m.id)) document.getElementById(m.id).value = val;
      }
    });
    alert("解析完了");
  }
  function render() {
    const body = document.getElementById('pTable');
    body.innerHTML = '';
    patients.sort((a,b) => a.admDate > b.admDate ? 1 : -1);
    patients.forEach((p, i) => {
      const d40 = getDeadlineInfo(p.admDate, 40);
      const d60 = getDeadlineInfo(p.admDate, 60);
      const tr = document.createElement('tr');
      tr.innerHTML = `
        <td align="center"><b>${p.admDate.substring(5).replace('-','/')}</b><br><small>40d:<span class="${d40.class}">${d40.date}</span></small><br><small>60d:<span class="${d60.class}">${d60.date}</span></small></td>
        <td align="center">${p.ward}</td>
        <td><b>${p.lastName}</b><br><small>${p.firstName}</small><br><small>(${p.careLevel || '-'})</small></td>
        <td align="center">${p.gender}</td>
        <td><small>看:${p.nurse} 医:${p.doc}<br>リ:${p.rehab}</small><div style="border-top:1px solid #ccc; margin-top:1px;"><small><b>家:</b>${p.family || '-'}</small></div></td>
        <td><small>【${p.purpose}】</small><br>${p.status}</td>
        <td>${p.goal}</td>
        <td>${p.service}<br><small><b>CM:</b>${p.cm || '-'}</small></td>
        <td><small>${p.dest}</small></td>
        <td class="no-print col-op"><button class="btn-sub" style="padding:2px 4px;font-size:0.7rem;" onclick="edit(${i})">編</button> <button class="btn-accent" style="padding:2px 4px;font-size:0.7rem;" onclick="del(${i})">削</button></td>
      `;
      body.appendChild(tr);
    });
    localStorage.setItem('hosp_v_final_master', JSON.stringify(patients));
  }
  function addPatient() {
    const data = {};
    ['lastName','firstName','ward','gender','admDate','nurse','doc','rehab','careLevel','cm','purpose','family','dest','status','goal','service','progress'].forEach(id => { data[id] = document.getElementById(id).value; });
    if(!data.lastName) return alert("氏名必須");
    if(editIdx > -1) { patients[editIdx] = data; editIdx = -1; document.getElementById('mainBtn').textContent = "登録"; }
    else { patients.push(data); }
    render(); resetForm();
  }
  function edit(i) {
    const p = patients[i];
    Object.keys(p).forEach(key => { if(document.getElementById(key)) document.getElementById(key).value = p[key]; });
    editIdx = i; document.getElementById('mainBtn').textContent = "更新"; window.scrollTo(0,0);
  }
  function del(i) { if(confirm("削除？")) { patients.splice(i,1); render(); } }
  function resetForm() { document.querySelectorAll('.input-form input, .input-form textarea, .input-form select').forEach(el => el.value = ''); editIdx = -1; document.getElementById('mainBtn').textContent = "登録"; }
  function exportData() {
    const blob = new Blob([JSON.stringify(patients, null, 2)], {type: 'application/json'});
    const a = document.createElement('a'); a.href = URL.createObjectURL(blob);
    a.download = `退院支援リスト_${new Date().toLocaleDateString()}.json`; a.click();
  }
  function importData(e) {
    const reader = new FileReader();
    reader.onload = (ev) => { try { patients = JSON.parse(ev.target.result); render(); } catch(e) { alert("読込失敗"); } };
    reader.readAsText(e.target.files[0]);
  }
  render();
</script>
</body>
</html>
"""

# StreamlitのコンポーネントとしてHTMLを表示
components.html(html_code, height=1200, scrolling=True)