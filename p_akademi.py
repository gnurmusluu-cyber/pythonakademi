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
    st.session_state.update({
        'student_name': "", 'student_no': "", 'student_class': "", 'completed_modules': [False]*8,
        'current_module': 0, 'current_exercise': 0, 'exercise_passed': False, 'total_score': 0,
        'scored_exercises': set(), 'db_module': 0, 'db_exercise': 0, 'is_logged_in': False,
        'current_potential_score': 20, 'fail_count': 0, 'feedback_msg': "", 'last_output': "",
        'graduation_view': False, 'pito_emotion': "merhaba"
    })

SINIFLAR = ["9-A", "9-B", "10-A", "10-B", "11-A", "11-B"]
RUTBELER = ["🥚 Yeni Başlayan", "🌱 Python Çırağı", "🪵 Kod Oduncusu", "🧱 Mantık Mimarı", "🌀 Döngü Ustası", "📋 Liste Uzmanı", "📦 Fonksiyon Kaptanı", "🤖 OOP Robotu", "🏆 Python Kahramanı"]

# --- MODERN UI CSS (APPLY BUTONUNU KÖKTEN SİL) ---
st.markdown("""
    <style>
    header {visibility: hidden;}
    .main .block-container {padding-top: 1rem; background-color: #f8fafc;}
    
    /* ACE EDITOR: APPLY BUTONUNU CSS İLE KESİN OLARAK YOK ET */
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

    /* FORM BUTON STİLİ */
    .stButton > button {
        width: 100%; border-radius: 15px; height: 3.8em; 
        background: linear-gradient(45deg, #3a7bd5, #00d2ff) !important;
        color: white !important; font-weight: bold; border: none; font-size: 1.15rem;
        box-shadow: 0 4px 15px rgba(58, 123, 213, 0.3);
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. HIZLI ASSET YÜKLEME ---
@st.cache_resource
def load_gif_b64(name):
    p = Path(__file__).parent / "assets" / name
    return base64.b64encode(p.read_bytes()).decode() if p.exists() else None

def show_pito_gif(width=450):
    emotion_map = {"standart": "pito_dusunuyor.gif", "merhaba": "pito_merhaba.gif", "uzgun": "pito_hata.gif", "mutlu": "pito_basari.gif", "akademi": "pito_mezun.gif"}
    b64 = load_gif_b64(emotion_map.get(st.session_state.pito_emotion, "pito_dusunuyor.gif"))
    if b64:
        st.markdown(f'<div style="display: flex; justify-content: center;"><img src="data:image/gif;base64,{b64}" width="{width}px" style="border-radius: 20px;"></div>', unsafe_allow_html=True)

# --- 4. VERİ TABANI ---
SHEET_URL = "https://docs.google.com/spreadsheets/d/1lat8rO2qm9QnzEUYlzC_fypG3cRkGlJfSfTtwNvs318/edit#gid=0"
conn = st.connection("gsheets", type=GSheetsConnection)

def force_save():
    try:
        df_all = conn.read(spreadsheet=SHEET_URL, ttl=0)
        no = str(st.session_state.student_no).strip()
        df_clean = df_all[df_all["Okul No"].astype(str).str.split('.').str[0] != no]
        prog = ",".join(["1" if m else "0" for m in st.session_state.completed_modules])
        rank = RUTBELER[min(sum(st.session_state.completed_modules), 8)]
        new_row = pd.DataFrame([[no, st.session_state.student_name, st.session_state.student_class, int(st.session_state.total_score), rank, prog, int(st.session_state.db_module), int(st.session_state.db_exercise), datetime.now().strftime("%H:%M")]], columns=["Okul No", "Öğrencinin Adı", "Sınıf", "Puan", "Rütbe", "Tamamlanan Modüller", "Mevcut Modül", "Mevcut Egzersiz", "Tarih"])
        conn.update(spreadsheet=SHEET_URL, data=pd.concat([df_clean, new_row], ignore_index=True))
    except: pass

# --- 5. DEĞERLENDİRME MOTORU ---
def run_pito_code(c, user_input="Pito"):
    old_stdout, new_stdout = sys.stdout, StringIO()
    sys.stdout = new_stdout
    try:
        mock_env = {"print": print, "input": lambda p: str(user_input), "int": int, "str": str, "yas": 0, "isim": "", "L": [10,20], "d":{'ad':'Pito'}, "t":(1,2)}
        exec(c, {"__builtins__": __builtins__}, mock_env)
        sys.stdout = old_stdout
        return new_stdout.getvalue(), mock_env, True
    except Exception as e:
        sys.stdout = old_stdout
        return str(e), {}, False

# --- 6. MÜFREDAT ---
training_data = [
    {"module_title": "1. İletişim: print() ve Metinler", "exercises": [
        {"msg": "Editor içine tam olarak **'Merhaba Pito'** metnini tırnaklar içerisinde yaz!", "task": "print('___')", "check": lambda c, o, l: "Merhaba Pito" in o, "solution": "print('Merhaba Pito')", "hint": "Tırnakları unutma."},
        {"msg": "Boşluğa tırnak kullanmadan sadece **100** sayısını yaz.", "task": "print(___)", "check": lambda c, o, l: "100" in o, "solution": "print(100)", "hint": "Sayılar tırnaksız yazılır."},
    ]},
    {"module_title": "2. Hafıza: Değişkenler", "exercises": [
        {"msg": "`yas` kutusuna sayısal olarak **15** değerini ata.", "task": "yas = ___", "check": lambda c, o, l: l.get('yas') == 15, "solution": "yas = 15", "hint": "Sadece 15 yaz."},
    ]}
]

# --- 7. PANEL VE AKIŞ ---
col_main, col_sidebar = st.columns([3.3, 1])

with col_sidebar:
    st.markdown("### 🏆 Onur Kurulu")
    try:
        db_l = conn.read(spreadsheet=SHEET_URL, ttl="1m")
        if not db_l.empty:
            db_l["Puan"] = pd.to_numeric(db_l["Puan"], errors='coerce').fillna(0)
            for _, r in db_l.sort_values(by="Puan", ascending=False).head(10).iterrows():
                st.markdown(f'<div style="background:white;padding:10px;margin-bottom:5px;border-radius:10px;border-left:5px solid #3a7bd5;color:#1e293b;"><b>{r["Öğrencinin Adı"]}</b><br>{int(r["Puan"])} PT</div>', unsafe_allow_html=True)
    except: pass

with col_main:
    if st.session_state.is_logged_in:
        curr_r = RUTBELER[min(sum(st.session_state.completed_modules), 8)]
        st.markdown(f'<div class="user-card"><div class="user-card-text">👤 {st.session_state.student_name} ({st.session_state.student_class})</div><div class="user-card-badge">⭐ {st.session_state.total_score} PT</div></div>', unsafe_allow_html=True)

    if not st.session_state.is_logged_in:
        c1, c2 = st.columns([1.6, 3.4]); with c1: st.session_state.pito_emotion = "merhaba"; show_pito_gif(450)
        with c2:
            st.markdown('<div class="pito-bubble" style="margin-top: 60px;">Merhaba! Ben <b>Pito</b>. Python macerasına hazır mısın? Numaranı gir ve dünyaya katıl!</div>', unsafe_allow_html=True)
            in_no = st.text_input("Okul Numaran:", placeholder="Numaranı mühürle...").strip()
            if in_no and in_no.isdigit():
                db = conn.read(spreadsheet=SHEET_URL, ttl=0)
                user_data = db[db["Okul No"].astype(str).str.contains(in_no)] if not db.empty else pd.DataFrame()
                if not user_data.empty:
                    row = user_data.iloc[0]; st.info(f"🔍 **{row['Öğrencinin Adı']}**, Hoş geldin!")
                    if st.button("🚀 Devam Et"):
                        st.session_state.update({'student_no': in_no, 'student_name': row["Öğrencinin Adı"], 'student_class': row["Sınıf"], 'total_score': int(row["Puan"]), 'db_module': int(row['Mevcut Modül']), 'db_exercise': int(row['Mevcut Egzersiz']), 'current_module': min(int(row['Mevcut Modül']), 7), 'current_exercise': int(row['Mevcut Egzersiz']), 'completed_modules': [True if x == "1" else False for x in str(row["Tamamlanan Modüller"]).split(",")], 'is_logged_in': True, 'pito_emotion': 'standart'}); st.rerun()
                else:
                    in_name = st.text_input("Adın Soyadın:"); in_class = st.selectbox("Sınıfın:", SINIFLAR)
                    if st.button("✨ Kayıt Ol ve Başla") and in_name:
                        st.session_state.update({'student_no': in_no, 'student_name': in_name, 'student_class': in_class, 'is_logged_in': True}); force_save(); st.rerun()
        st.stop()

    # Boundary Check (IndexError Fix)
    m_idx = min(st.session_state.current_module, len(training_data)-1)
    e_idx = min(st.session_state.current_exercise, len(training_data[m_idx]["exercises"])-1)
    curr_ex = training_data[m_idx]["exercises"][e_idx]

    # NEON PROGRESS
    perc = ((m_idx * 5 + e_idx + 1) / 40) * 100
    st.markdown(f'''<div class="quest-container"><b>📍 {training_data[m_idx]['module_title']}</b><div class="quest-bar"><div class="quest-fill" style="width: {perc}%;"></div></div></div>''', unsafe_allow_html=True)

    c_pito, c_bubble = st.columns([1.5, 3.5]); with c_pito: show_pito_gif(450)
    with c_bubble:
        st.markdown(f'<div class="pito-bubble"><b>🗣️ Pito\'nun Notu:</b><br><br>{curr_ex["msg"]}</div>', unsafe_allow_html=True)
        st.markdown(f'''<div style="display:flex; gap:15px; margin-top:10px;">
            <div style="background:white; padding:10px; border-radius:10px; flex:1; text-align:center; border:1px solid #e2e8f0; font-weight:bold; color:#1e293b;">🐾 Adım: {e_idx + 1}/5</div>
            <div style="background:white; padding:10px; border-radius:10px; flex:1; text-align:center; border:1px solid #e2e8f0; font-weight:bold; color:#ef4444;">❌ Hatalar: {st.session_state.fail_count}/4</div>
        </div>''', unsafe_allow_html=True)

    if st.session_state.feedback_msg:
        if "✅" in st.session_state.feedback_msg: st.success(st.session_state.feedback_msg)
        else: st.error(st.session_state.feedback_msg)

    # --- KOD KONTROL MERKEZİ (FORM MÜHÜRLEME: KESİN ÇÖZÜM) ---
    if not st.session_state.exercise_passed and st.session_state.fail_count < 4:
        with st.form(key=f"pito_form_{m_idx}_{e_idx}"):
            # auto_update=False: Sadece butona basıldığında veri çekilir (Sync Fix)
            code = st_ace(value=curr_ex['task'], language="python", theme="monokai", font_size=16, height=200, 
                          auto_update=False, key=f"ace_{m_idx}_{e_idx}")
            submit = st.form_submit_button("🔍 Kodumu Kontrol Et")
            
            if submit:
                # 1. KONTROL: Placeholder (Boşluk) Kontrolü
                if "___" in code:
                    st.session_state.feedback_msg = "⚠️ Pito bekliyor: Boşluğu doldurmalısın!"
                    st.rerun()
                
                # 2. KONTROL: Doğruluk Analizi
                out, env, status = run_pito_code(code)
                if status and curr_ex['check'](code, out, env):
                    # BAŞARI: Hata sayacı asla artmaz
                    st.session_state.update({'feedback_msg': "✅ Tebrikler! Harika bir iş çıkardın. Bir sonraki adıma geçebilirsin!", 'exercise_passed': True, 'pito_emotion': 'mutlu', 'fail_count': 0})
                    st.session_state.total_score += st.session_state.current_potential_score; force_save(); st.rerun()
                else:
                    # HATA: Kademeli mesajlar
                    st.session_state.fail_count += 1
                    st.session_state.pito_emotion = "uzgun"
                    st.session_state.current_potential_score = max(0, st.session_state.current_potential_score - 5)
                    msgs = {1: "❌ Bu ilk hatan lütfen daha dikkatli ol ve tekrar dene!", 2: "❌ Bu 2. hatan!", 3: f"💡 İpucu: {curr_ex['hint']}", 4: "🌿 Mantığı inceleyelim."}
                    st.session_state.feedback_msg = msgs.get(st.session_state.fail_count, msgs[4])
                    if st.session_state.fail_count >= 4: st.session_state.exercise_passed = True
                    st.rerun()

    # NAVİGASYON
    if st.session_state.exercise_passed or st.session_state.fail_count >= 4:
        if st.session_state.fail_count >= 4:
            st.markdown('🔍 **Pito\'nun Mühürlü Çözümü:**')
            st.code(curr_ex['solution'], language="python")
        if st.button("➡️ Sonraki Adıma Geç", use_container_width=True):
            st.session_state.current_exercise += 1
            if st.session_state.current_exercise >= 5:
                st.session_state.current_module += 1; st.session_state.current_exercise = 0; st.session_state.db_module += 1; st.session_state.completed_modules[st.session_state.current_module-1] = True; force_save()
            st.session_state.update({'exercise_passed': False, 'fail_count': 0, 'feedback_msg': "", 'current_potential_score': 20, 'pito_emotion': 'standart'}); st.rerun()
