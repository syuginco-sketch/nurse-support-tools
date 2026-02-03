import streamlit as st
import pandas as pd
import random
from datetime import datetime, date
import calendar
import jpholiday

# --- ページ設定 ---
st.set_page_config(page_title="看護師シフト生成AI", layout="wide")
st.title("🏥 究極の公平性・看護師シフト管理システム")

# --- セッション状態の初期化 ---
if 'staff_list' not in st.session_state:
    st.session_state.staff_list = []
if 'requests_strong' not in st.session_state:
    st.session_state.requests_strong = {}
if 'requests_weak' not in st.session_state:
    st.session_state.requests_weak = {}

# =========================================================
# 👤 サイドバー：スタッフ登録
# =========================================================
with st.sidebar:
    st.header("👤 メンバー登録")
    with st.form("staff_form", clear_on_submit=True):
        name = st.text_input("氏名")
        gender = st.selectbox("性別", ["女性", "男性"])
        role = st.selectbox("役割", ["L看護師", "看護師", "看護補助者"])
        work_type = st.selectbox("勤務形態", ["フル（夜勤あり）", "日勤のみ（シフト制）", "日勤のみ（土日祝休）"])

        support_shifts = []
        support_night_ok = False
        if role == "看護補助者":
            st.markdown("---")
            support_shifts = st.multiselect("補助者の勤務可能枠", ["早出(E)", "遅出(L)", "日勤(D)"], default=["日勤(D)"])
            support_night_ok = st.checkbox("夜勤可能", value=True)

        if st.form_submit_button("スタッフを追加"):
            if name and name not in [s['name'] for s in st.session_state.staff_list]:
                st.session_state.staff_list.append({
                    "name": name, "gender": gender, "role": role, 
                    "work_type": work_type, "support_shifts": support_shifts, 
                    "support_night_ok": support_night_ok
                })
            else:
                st.warning("名前を入力するか、重複していないか確認してください。")

    if st.button("全スタッフ削除"):
        st.session_state.staff_list = []
        st.session_state.requests_strong = {}
        st.session_state.requests_weak = {}
        st.rerun()

# =========================================================
# 🧩 メインエリア
# =========================================================
if not st.session_state.staff_list:
    st.info("左側のサイドバーからスタッフを登録してください。")
else:
    tab1, tab2 = st.tabs(["📅 希望休・設定", "✨ シフト生成"])

    # --- タブ1: 希望休設定 ---
    with tab1:
        col1, col2 = st.columns(2)
        year = col1.number_input("年", 2024, 2030, 2026)
        month = col2.number_input("月", 1, 12, 2)
        num_days = calendar.monthrange(year, month)[1]

        st.subheader("📌 強制休（必ず休み）")
        for s in st.session_state.staff_list:
            st.session_state.requests_strong[s['name']] = st.multiselect(
                f"{s['name']} さん", range(1, num_days + 1), key=f"s_{s['name']}")

        st.subheader("💡 任意休（可能なら休み）")
        for s in st.session_state.staff_list:
            st.session_state.requests_weak[s['name']] = st.multiselect(
                f"{s['name']} さん", range(1, num_days + 1), key=f"w_{s['name']}")

    # --- タブ2: シフト生成 ---
    with tab2:
        if st.button("🚀 シフトを自動生成する"):
            staff_data = st.session_state.staff_list
            names = [s['name'] for s in staff_data]
            schedule = {name: [""] * num_days for name in names}
            night_counts = {name: 0 for name in names}
            
            support_info = {s["name"]: {"shifts": s["support_shifts"], "night_ok": s["support_night_ok"]} 
                            for s in staff_data if s["role"] == "看護補助者"}

            for d in range(num_days):
                curr_date = date(year, month, d + 1)
                is_holiday = (curr_date.weekday() == 6) or jpholiday.is_holiday(curr_date)

                # 1. 強制ルール適用（休み・明け）
                for s in staff_data:
                    n = s["name"]
                    if (d + 1) in st.session_state.requests_strong.get(n, []):
                        schedule[n][d] = "休"
                    elif s["work_type"] == "日勤のみ（土日祝休）" and is_holiday:
                        schedule[n][d] = "休"
                    elif d > 0:
                        if schedule[n][d-1] == "★":
                            schedule[n][d] = "/" # 夜勤明け
                        elif schedule[n][d-1] == "/":
                            schedule[n][d] = "休" # 明け翌日

                # 2. 夜勤選定 (3名体制: 看護師2 + 補助1)
                cands_n = [s for s in staff_data if s["role"] != "看護補助者" and schedule[s["name"]][d] == "" and s["work_type"] == "フル（夜勤あり）"]
                cands_s = [s for s in staff_data if s["role"] == "看護補助者" and schedule[s["name"]][d] == "" and support_info[s["name"]]["night_ok"]]
                
                # 公平性のために夜勤回数が少ない人を優先（ランダム要素を加えて偏りを防ぐ）
                cands_n.sort(key=lambda x: night_counts[x["name"]] + random.random()*0.1)
                cands_s.sort(key=lambda x: night_counts[x["name"]] + random.random()*0.1)

                if len(cands_n) >= 2 and len(cands_s) >= 1:
                    team = [cands_n[0], cands_n[1], cands_s[0]]
                    # 男性2名禁止チェック
                    if len([t for t in team if t["gender"] == "男性"]) < 2:
                        for t in team:
                            schedule[t["name"]][d] = "★"
                            night_counts[t["name"]] += 1

                # 3. 4連勤禁止ロジック
                for s in staff_data:
                    n = s["name"]
                    if schedule[n][d] == "" and d >= 3:
                        # 直近3日間が勤務（日勤系）であれば休みを入れる
                        recent = schedule[n][d-3:d]
                        if all(x in ["〇", "E", "L", "D"] for x in recent):
                            schedule[n][d] = "休"

                # 4. 日勤・補助者枠・任意休の適用
                for s in staff_data:
                    n = s["name"]
                    if schedule[n][d] == "":
                        if (d + 1) in st.session_state.requests_weak.get(n, []):
                            schedule[n][d] = "休"
                        else:
                            if s["role"] == "看護補助者":
                                possible = support_info[n]["shifts"]
                                schedule[n][d] = random.choice(possible) if possible else "D"
                            else:
                                schedule[n][d] = "〇"

            st.session_state.generated_schedule = schedule
            st.session_state.generated_stats = night_counts

        # --- 表示セクション ---
        if "generated_schedule" in st.session_state:
            res_df = pd.DataFrame(st.session_state.generated_schedule).T
            # 列ラベル作成
            days_labels = []
            for i in range(num_days):
                curr = date(year, month, i + 1)
                wd = ['月','火','水','木','金','土','日'][curr.weekday()]
                label = f"{i+1}({wd})"
                if jpholiday.is_holiday(curr) or curr.weekday() == 6:
                    label += "祝"
                days_labels.append(label)
            res_df.columns = days_labels
            
            def color_rule(val):
                colors = {
                    '★': 'background-color: #ffcccc; font-weight: bold;', # 夜勤
                    '/': 'background-color: #e1f5fe;', # 明け
                    '休': 'background-color: #f5f5f5; color: #999999;', # 休み
                    '〇': 'background-color: #e8f5e9;', # 日勤
                    'E': 'background-color: #fff3cd;', # 早出
                    'L': 'background-color: #ffe0b2;', # 遅出
                    'D': 'background-color: #dcedc8;'  # 補助日勤
                }
                return colors.get(val, "")

            st.subheader(f"🗓️ {year}年{month}月 生成されたシフト表")
            st.dataframe(res_df.style.applymap(color_rule), height=500)
            
            # 統計表示
            st.subheader("📊 勤務合計（公平性チェック）")
            stats_list = []
            for name, sch in st.session_state.generated_schedule.items():
                stats_list.append({
                    "氏名": name,
                    "夜勤(★)": sch.count("★"),
                    "日勤系": sch.count("〇") + sch.count("E") + sch.count("L") + sch.count("D"),
                    "休み(休)": sch.count("休") + sch.count("/")
                })
            st.table(pd.DataFrame(stats_list))

            # CSVダウンロード
            csv = res_df.to_csv().encode('utf_8_sig')
            st.download_button("📥 Excel用CSVをダウンロード", csv, f"shift_{year}_{month}.csv", "text/csv")