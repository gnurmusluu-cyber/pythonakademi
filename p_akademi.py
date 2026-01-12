import streamlit as st
from streamlit_ace import st_ace
import sys
from io import StringIO
import pandas as pd
from datetime import datetime
from streamlit_gsheets import GSheetsConnection
import os
import base64
import time
from pathlib import Path

# --- 1. TASARIM VE SAYFA AYARLARI ---
st.set_page_config(layout="wide", page_title="Pito Python Akademi", initial_sidebar_state="collapsed")

# --- 2. SESSION STATE (MANTIKSAL ANAYASA) ---
if 'is_logged_in' not in st.session_state:
    for k, v in {
        'student_name': "", 'student_no': "", 'student_class': "", 'completed_modules': [False]*8,
        'current_module': 0, 'current_exercise': 0, 'exercise_passed': False, 'total_score': 0,
        'scored_exercises': set(), 'db_module': 0, 'db_exercise': 0, 'is_logged_in': False,
        'current_potential_score': 20, 'fail_count': 0, 'feedback_msg': "", 'last_output': "",
        'graduation_view': False, 'no_input_error': False, 'pito_emotion': "merhaba"
    }.items():
        st.session_state[k] = v

SINIFLAR = ["9-A", "9-B", "10-A", "10-B", "11-A", "11-B"]
RUTBELER = ["🥚 Egg", "🌱 Çırağı", "🪵 Oduncu", "🧱 Mimar", "🌀 Usta", "📋 Uzman", "📦 Kaptan", "🤖 Robot", "🏆 Python Hero"]

# --- MODERN UI CSS (APPLY BUTONUNU KÖKTEN KAZI VE GÖRÜNÜRLÜK) ---
st.markdown("""
    <style>
    header {visibility: hidden;}
    .main .block-container {padding-top: 1rem; background-color: #f8fafc;}
    
    /* ACE EDITOR: APPLY BUTONUNU CSS İLE KÖKTEN SİL (KESİN ÇÖZÜM) */
    [data-testid="stAceApplyButton"], .ace-apply-button, .ace_button, .ace_search { 
        display: none !important; visibility: hidden !important; height: 0 !important; width: 0 !important;
    }
    iframe { border-radius: 15px !important; border: 2.5px solid #3a7bd5 !important; }

    /* ÜST KİMLİK KARTI */
    .user-card {
        background: white; border: 2.5px solid #3a7bd5; border-radius: 15px;
        padding: 12px 20px; display: flex; align-items: center; gap: 20px;
        box-shadow: 0 4px 6px rgba(58, 123, 213, 0.1); margin-bottom: 15px; width: fit-content;
    }
    .user-card-text { color: #1e293b; font-weight: bold; font-size: 1.1rem; }
    .user-card-badge { background: #3a7bd5; color: white; padding: 4px 12px; border-radius: 20px; font-size: 0.9rem; }

    /* İLERLEME PANELİ */
    .quest-container {
        background: white; padding: 20px; border-radius: 20px;
        box-shadow: 0 10px 15px -3px rgba(0,0,0,0.1); margin-bottom: 25px; border-top: 6px solid #3a7bd5;
    }
    .quest-bar { height: 16px; background: #e2e8f0; border-radius: 15px; margin: 10px 0; overflow: hidden; }
    .quest-fill { height: 100%; background: linear-gradient(90deg, #3a7bd5, #00d2ff); transition: width 0.8s ease-in-out; }

    /* PİTO KONUŞMA BALONU */
    .pito-bubble {
        position: relative; background: #ffffff; border: 3px solid #3a7bd5;
        border-radius: 25px; padding: 30px; color: #1e293b;
        font-weight: 500; font-size: 1.2rem; box-shadow: 10px 10px 30px rgba(58, 123, 213, 0.1);
        line-height: 1.7; width: 100%; margin-top: 10px;
    }
    .pito-bubble::after {
        content: ''; position: absolute; left: -25px; top: 40px;
        border-width: 15px 25px 15px 0; border-style: solid; border-color: transparent #3a7bd5 transparent transparent;
    }

    .stButton > button {
        width: 100%; border-radius: 15px; height: 3.8em; 
        background: linear-gradient(45deg, #3a7bd5, #00d2ff) !important;
        color: white !important; font-weight: bold; border: none; font-size: 1.15rem;
        box-shadow: 0 4px 15px rgba(58, 123, 213, 0.3); transition: transform 0.2s;
    }
    .stButton > button:hover { transform: scale(1.02); }
    </style>
    """, unsafe_allow_html=True)

# --- 3. ASSET & DB MANTIĞI ---
def get_pito_gif_b64(file_name):
    base_path = Path(__file__).parent.absolute()
    asset_path = base_path / "assets" / file_name
    if asset_path.exists():
        with open(asset_path, "rb") as f: return base64.b64encode(f.read()).decode()
    return None

def show_pito_gif(width=450):
    emotion_map = {"standart": "pito_dusunuyor.gif", "merhaba": "pito_merhaba.gif", "uzgun": "pito_hata.gif", "mutlu": "pito_basari.gif", "akademi": "pito_mezun.gif"}
    b64 = get_pito_gif_b64(emotion_map.get(st.session_state.pito_emotion, "pito_dusunuyor.gif"))
    if b64:
        st.markdown(f'<div style="display: flex; justify-content: center;"><img src="data:image/gif;base64,{b64}" width="{width}px" style="border-radius: 20px;"></div>', unsafe_allow_html=True)

SHEET_URL = "https://docs.google.com/spreadsheets/d/1lat8rO2qm9QnzEUYlzC_fypG3cRkGlJfSfTtwNvs318/edit#gid=0"
conn = st.connection("gsheets", type=GSheetsConnection)

def get_db():
    try:
        df = conn.read(spreadsheet=SHEET_URL, ttl=0)
        if df is None or df.empty: return pd.DataFrame(columns=["Okul No", "Öğrencinin Adı", "Sınıf", "Puan", "Rütbe", "Tamamlanan Modüller", "Mevcut Modül", "Mevcut Egzersiz", "Tarih"])
        df.columns = df.columns.str.strip()
        df["Okul No"] = df["Okul No"].astype(str).str.split('.').str[0].str.strip()
        df["Puan"] = pd.to_numeric(df["Puan"], errors='coerce').fillna(0).astype(int)
        return df.dropna(subset=["Okul No"])
    except: return None

db_current = get_db()

def force_save():
    try:
        no = str(st.session_state.student_no).strip()
        df_all = get_db()
        df_clean = df_all[df_all["Okul No"] != no]
        prog = ",".join(["1" if m else "0" for m in st.session_state.completed_modules])
        rank = RUTBELER[min(sum(st.session_state.completed_modules), 8)]
        new_row = pd.DataFrame([[no, st.session_state.student_name, st.session_state.student_class, int(st.session_state.total_score), rank, prog, int(st.session_state.db_module), int(st.session_state.db_exercise), datetime.now().strftime("%H:%M")]], columns=["Okul No", "Öğrencinin Adı", "Sınıf", "Puan", "Rütbe", "Tamamlanan Modüller", "Mevcut Modül", "Mevcut Egzersiz", "Tarih"])
        conn.update(spreadsheet=SHEET_URL, data=pd.concat([df_clean, new_row], ignore_index=True))
    except: pass

# --- 4. MÜFREDAT ---
training_data = [
    {"module_title": "1. İletişim: print() ve Metinler", "exercises": [
        {"msg": "**GÖREV:** Editor içine tam olarak **'Merhaba Pito'** metnini tırnaklar içerisinde yaz!", "task": "print('___')", "check": lambda c, o, l: "Merhaba Pito" in o, "solution": "print('Merhaba Pito')", "hint": "Tırnak koymayı unutma."},
        {"msg": "**GÖREV:** Boşluğa tırnak kullanmadan sadece **100** sayısını yaz.", "task": "print(___)", "check": lambda c, o, l: "100" in o, "solution": "print(100)", "hint": "Rakamları doğrudan yaz."},
    ]},
    {"module_title": "2. Hafıza: Değişkenler", "exercises": [
        {"msg": "**GÖREV:** `yas` kutusuna sayısal olarak **15** değerini ata.", "task": "yas = ___", "check": lambda c, o, l: l.get('yas') == 15, "solution": "yas = 15", "hint": "Eşittir işaretinden sonra sadece 15 yaz."},
    ]}
]

# --- 5. ANA PANEL VE DEĞİŞKEN TANIMLARI (NAMEERROR FIX) ---
col_main, col_sidebar = st.columns([3.3, 1])

with col_sidebar:
    st.markdown("### 🏆 Onur Kurulu")
    if db_current is not None and not db_current.empty:
        df_l = db_current.copy()
        top_c = df_l.groupby("Sınıf")["Puan"].sum().idxmax()
        st.markdown(f'<div style="background:linear-gradient(135deg,#FFD700,#F59E0B);color:black;border-radius:12px;padding:15px;text-align:center;font-weight:900;">🥇 LİDER SINIF: {top_c}</div>', unsafe_allow_html=True)
        st.divider()
        t1, t2 = st.tabs(["👥 Sınıfım", "🏫 Okul"])
        with t1:
            if st.session_state.is_logged_in:
                my_c = df_l[df_l["Sınıf"] == st.session_state.student_class].sort_values(by="Puan", ascending=False).head(8)
                for _, r in my_c.iterrows(): st.markdown(f'<div style="background:white;padding:8px;margin-bottom:5px;border-radius:10px;border-left:5px solid #3a7bd5;"><b>{r["Öğrencinin Adı"]}</b><br>{int(r["Puan"])} Puan</div>', unsafe_allow_html=True)
        with t2:
            for _, r in df_l.sort_values(by="Puan", ascending=False).head(10).iterrows(): st.markdown(f'<div style="background:white;padding:8px;margin-bottom:5px;border-radius:10px;border-left:5px solid #3a7bd5;"><b>{r["Öğrencinin Adı"]} ({r["Sınıf"]})</b><br>{int(r["Puan"])} Puan</div>', unsafe_allow_html=True)

with col_main:
    if not st.session_state.is_logged_in:
        c1, c2 = st.columns([1.6, 3.4]); with c1: st.session_state.pito_emotion = "merhaba"; show_pito_gif(450)
        with c2:
            st.markdown('<div class="pito-bubble" style="margin-top: 50px;">Ben <b>Pito</b>. Python macerasına hazır mısın? Numaranı gir ve dünyaya katıl!</div>', unsafe_allow_html=True)
            in_no = st.text_input("Okul Numaran:", placeholder="Numaranı mühürle...").strip()
            if in_no and in_no.isdigit():
                user_data = db_current[db_current["Okul No"] == in_no] if db_current is not None else pd.DataFrame()
                if not user_data.empty:
                    row = user_data.iloc[0]; st.info(f"🔍 **{row['Öğrencinin Adı']}**, Hoş geldin!")
                    if st.button("🚀 Devam Et"):
                        st.session_state.update({'student_no': in_no, 'student_name': row["Öğrencinin Adı"], 'student_class': row["Sınıf"], 'total_score': int(row["Puan"]), 'db_module': int(row['Mevcut Modül']), 'db_exercise': int(row['Mevcut Egzersiz']), 'current_module': min(int(row['Mevcut Modül']), len(training_data)-1), 'current_exercise': int(row['Mevcut Egzersiz']), 'completed_modules': [True if x == "1" else False for x in str(row["Tamamlanan Modüller"]).split(",")], 'is_logged_in': True}); st.rerun()
                else:
                    in_name = st.text_input("Adın Soyadın:"); in_class = st.selectbox("Sınıfın:", SINIFLAR)
                    if st.button("✨ Başla") and in_name:
                        st.session_state.update({'student_no': in_no, 'student_name': in_name, 'student_class': in_class, 'is_logged_in': True}); force_save(); st.rerun()
        st.stop()

    if st.session_state.graduation_view:
        st.session_state.pito_emotion = "akademi"; show_pito_gif(550)
        st.markdown('<div class="pito-bubble" style="text-align:center;">🎊 <b>MEZUNİYET MÜHÜRLENDİ!</b></div>', unsafe_allow_html=True); st.balloons(); st.stop()

    # Boundary Check (IndexError Fix)
    m_idx = min(st.session_state.current_module, len(training_data)-1)
    e_idx = min(st.session_state.current_exercise, len(training_data[m_idx]["exercises"])-1)
    curr_ex = training_data[m_idx]["exercises"][e_idx]
    is_review_mode = (st.session_state.current_module < st.session_state.db_module)

    # KİMLİK KARTI
    curr_rank = RUTBELER[min(sum(st.session_state.completed_modules), 8)]
    st.markdown(f'<div class="user-card"><div class="user-card-text">👤 {st.session_state.student_name} ({st.session_state.student_class})</div><div class="user-card-text">{curr_rank}</div><div class="user-card-badge">⭐ {st.session_state.total_score} Puan</div></div>', unsafe_allow_html=True)

    # PROGRESS BAR
    perc = ((m_idx * 5 + e_idx + 1) / 40) * 100
    st.markdown(f'''<div class="quest-container"><b>📍 {training_data[m_idx]['module_title']}</b><div class="quest-bar"><div class="quest-fill" style="width: {perc}%;"></div></div></div>''', unsafe_allow_html=True)

    # HERO SECTION
    cp, cb = st.columns([1.5, 3.5]); with cp: show_pito_gif(450)
    with cb:
        st.markdown(f'<div class="pito-bubble"><b>🗣️ Pito\'nun Notu:</b><br><br>{curr_ex["msg"]}</div>', unsafe_allow_html=True)
        st.markdown(f'''<div style="display:flex; gap:15px; margin-top:10px;">
            <div class="stat-card" style="flex:1;">🐾 Adım: {e_idx + 1}/5</div>
            <div class="stat-card" style="flex:1;">🎁 Potansiyel: {st.session_state.current_potential_score} PT</div>
            <div class="stat-card" style="flex:1; color:#ef4444;">❌ Hatalar: {st.session_state.fail_count}/4</div>
        </div>''', unsafe_allow_html=True)

    # GERİ BİLDİRİM PANELİ (MÜHÜRLÜ KONUM)
    if st.session_state.feedback_msg:
        if "✅" in st.session_state.feedback_msg: st.success(st.session_state.feedback_msg)
        else: st.error(st.session_state.feedback_msg)

    if not st.session_state.exercise_passed and st.session_state.fail_count == 3:
        st.warning(f"💡 **Pito'dan İpucu:** {curr_ex['hint']}")
    
    if st.session_state.fail_count >= 4 or is_review_mode:
        st.markdown('🔍 **Doğru Mantığı Kavrayalım (Mühürlü Çözüm):**')
        st.code(curr_ex['solution'], language="python")

    # --- KOD KONTROL SİSTEMİ (SIFIRDAN İNŞA) ---
    def run_pito_code(c):
        old_stdout, new_stdout = sys.stdout, StringIO(); sys.stdout = new_stdout
        local_vars = {"print": print, "input": lambda p: "Pito", "int": int, "str": str, "len": len, "range": range, "yas": 0}
        try:
            exec(c, {"__builtins__": __builtins__}, local_vars)
            sys.stdout = old_stdout; return new_stdout.getvalue(), local_vars, True
        except Exception as e:
            sys.stdout = old_stdout; return str(e), local_vars, False

    if not is_review_mode and not st.session_state.exercise_passed and st.session_state.fail_count < 4:
        code = st_ace(value=curr_ex['task'], language="python", theme="monokai", font_size=16, height=180, key=f"ace_vF_{m_idx}_{e_idx}", auto_update=True)
        
        if st.button("🔍 Kodumu Kontrol Et", use_container_width=True):
            if "___" in code:
                st.session_state.feedback_msg = "⚠️ Pito bekliyor: Boşluğu doldurmalısın!"; st.rerun()
            else:
                out, env, status = run_pito_code(code)
                # BAŞARI KONTROLÜ (HATA DÖNGÜSÜNDEN ÖNCE)
                if status and curr_ex['check'](code, out, env):
                    st.session_state.update({'feedback_msg': "✅ Tebrikler! Harika bir iş çıkardın. Bir sonraki adıma geçebilirsin!", 'exercise_passed': True, 'pito_emotion': 'mutlu', 'fail_count': 0})
                    ex_key = f"{m_idx}_{e_idx}"
                    if ex_key not in st.session_state.scored_exercises:
                        st.session_state.total_score += st.session_state.current_potential_score
                        st.session_state.scored_exercises.add(ex_key); force_save()
                    st.rerun()
                else:
                    # HATA DÖNGÜSÜ
                    st.session_state.fail_count += 1
                    st.session_state.pito_emotion = "uzgun"
                    st.session_state.current_potential_score = max(0, st.session_state.current_potential_score - 5)
                    msgs = {1: "❌ Bu ilk hatan!", 2: "❌ Bu 2. hatan!", 3: "🚀 Pes etme! İpucuna bak.", 4: "🌿 Mantığı inceleyelim."}
                    st.session_state.feedback_msg = msgs.get(st.session_state.fail_count, msgs[4])
                    if st.session_state.fail_count >= 4: st.session_state.exercise_passed = True
                    st.rerun()

    # NAVİGASYON
    if st.session_state.exercise_passed or is_review_mode or st.session_state.fail_count >= 4:
        if st.button("➡️ Sonraki Adıma Geç", use_container_width=True):
            st.session_state.current_exercise += 1
            if st.session_state.current_exercise >= 5:
                st.session_state.current_module += 1; st.session_state.current_exercise = 0; st.session_state.db_module += 1; st.session_state.completed_modules[st.session_state.current_module-1] = True; force_save()
            st.session_state.update({'exercise_passed': False, 'fail_count': 0, 'feedback_msg': "", 'current_potential_score': 20, 'pito_emotion': 'standart'}); st.rerun()
