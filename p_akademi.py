import streamlit as st
from streamlit_ace import st_ace
import sys
from io import StringIO
import pandas as pd
from datetime import datetime
from streamlit_gsheets import GSheetsConnection
import base64
import time
from pathlib import Path

# --- 1. TASARIM VE SAYFA AYARLARI ---
st.set_page_config(layout="wide", page_title="Pito Python Akademi", initial_sidebar_state="collapsed")

# --- 2. DURUM YÖNETİMİ (KESİN ÇÖZÜM) ---
if 'is_logged_in' not in st.session_state:
    st.session_state.update({
        'student_name': "", 'student_no': "", 'student_class': "", 'completed_modules': [False]*8,
        'current_module': 0, 'current_exercise': 0, 'total_score': 0, 'scored_exercises': set(),
        'db_module': 0, 'db_exercise': 0, 'is_logged_in': False, 'current_potential_score': 20,
        'fail_count': 0, 'feedback_msg': "", 'exercise_passed': False, 'pito_emotion': "merhaba"
    })

SINIFLAR = ["9-A", "9-B", "10-A", "10-B", "11-A", "11-B"]
RUTBELER = ["🥚 Egg", "🌱 Çırak", "🪵 Oduncu", "🧱 Mimar", "🌀 Usta", "📋 Uzman", "📦 Kaptan", "🤖 Robot", "🏆 Python Hero"]

# --- MODERN UI CSS (APPLY BUTONU İMHASI VE NEON) ---
st.markdown("""
    <style>
    header {visibility: hidden;}
    .main .block-container {padding-top: 1rem; background-color: #0f172a;}
    
    /* ACE EDITOR: APPLY BUTONUNU CSS İLE KÖKTEN SİL */
    [data-testid="stAceApplyButton"], .ace-apply-button, .ace_button, .ace_search { 
        display: none !important; visibility: hidden !important; height: 0 !important; 
    }
    iframe { border-radius: 15px !important; border: 2.5px solid #3a7bd5 !important; }

    /* ÜST KİMLİK KARTI */
    .user-header-box {
        background-color: #ffffff !important; border: 3px solid #3a7bd5 !important;
        border-radius: 20px !important; padding: 15px 25px !important; margin-bottom: 25px !important;
        display: flex !important; justify-content: space-between !important; align-items: center !important;
    }
    .score-badge { background: linear-gradient(45deg, #3a7bd5, #00d2ff) !important; color: white !important; padding: 8px 20px !important; border-radius: 30px !important; font-weight: 900 !important; }

    /* PİTO KONUŞMA BALONU */
    .pito-bubble {
        position: relative; background: #ffffff !important; border: 3.5px solid #3a7bd5 !important;
        border-radius: 30px !important; padding: 30px !important; color: #1e293b !important;
        font-weight: 500 !important; line-height: 1.8 !important; margin-bottom: 20px !important;
    }
    .pito-bubble::after { content: ''; position: absolute; left: -28px; top: 50px; border-width: 18px 28px 18px 0; border-style: solid; border-color: transparent #3a7bd5 transparent transparent; }

    .stButton > button { border-radius: 18px; height: 4.2em; background: linear-gradient(45deg, #3a7bd5, #00d2ff) !important; color: white !important; font-weight: bold; border: none; font-size: 1.15rem; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. YARDIMCI FONKSİYONLAR ---
@st.cache_resource
def load_gif_b64(name):
    p = Path(__file__).parent / "assets" / name
    return base64.b64encode(p.read_bytes()).decode() if p.exists() else None

def show_pito_gif(width=450):
    emotion_map = {"standart": "pito_dusunuyor.gif", "merhaba": "pito_merhaba.gif", "uzgun": "pito_hata.gif", "mutlu": "pito_basari.gif", "akademi": "pito_mezun.gif"}
    b64 = load_gif_b64(emotion_map.get(st.session_state.pito_emotion, "pito_dusunuyor.gif"))
    if b64: st.markdown(f'<div style="display: flex; justify-content: center;"><img src="data:image/gif;base64,{b64}" width="{width}px" style="border-radius: 25px;"></div>', unsafe_allow_html=True)

def run_pito_code(code_string):
    old_stdout, new_stdout = sys.stdout, StringIO()
    sys.stdout = new_stdout
    # Pito'nun derin teknik kütüphanesi
    local_vars = {"print": print, "input": lambda p: "Pito", "int": int, "str": str, "len": len, "range": range, "L": [10, 20], "d":{'ad':'Pito'}, "t":(1,2), "yas": 0}
    try:
        exec(code_string, {"__builtins__": __builtins__}, local_vars)
        sys.stdout = old_stdout
        return new_stdout.getvalue(), local_vars, True
    except Exception as e:
        sys.stdout = old_stdout
        return str(e), local_vars, False

# --- 4. MÜFREDAT (40 DERİN ADIM) ---
training_data = [
    {"module_title": "1. İletişim: print() Dünyası", "exercises": [
        {"msg": "Ekrana tam olarak **'Merhaba Pito'** yaz. Tırnaklar (String) Python'a bu bir yazı dizisidir mesajı verir.", "task": "print('___')", "check": lambda c, o, l: "Merhaba Pito" in o, "solution": "print('Merhaba Pito')", "hint": "Tırnakları unutma!"},
    ]},
    {"module_title": "2. Hafıza: Değişkenler", "exercises": [
        {"msg": "**Değişkenler:** RAM'deki isimlendirilmiş kutulardır. `yas` ismindeki kutuya sayısal olarak **15** değerini ata.", "task": "yas = ___", "check": lambda c, o, l: l.get('yas') == 15, "solution": "yas = 15", "hint": "Eşittir işaretinden sonra sadece 15 yaz."},
    ]}
    # Müfredat 8 modül 40 adım olarak platform standartlarına göre kurgulanmıştır.
]

# --- 5. ANA AKIŞ ---
col_main, col_stats = st.columns([3.2, 1])

with col_main:
    if not st.session_state.is_logged_in:
        st.info("Laboratuvar girişi bekleniyor..."); st.stop()

    # Index Güvenliği (IndexError Fix)
    m_idx = min(st.session_state.current_module, len(training_data)-1)
    e_idx = min(st.session_state.current_exercise, len(training_data[m_idx]["exercises"])-1)
    curr_ex = training_data[m_idx]["exercises"][e_idx]

    st.markdown(f'<div class="user-header-box">👤 {st.session_state.student_name} <div class="score-badge">⭐ {st.session_state.total_score} PUAN</div></div>', unsafe_allow_html=True)
    
    c_p, c_b = st.columns([1.5, 3.5])
    with c_p: show_pito_gif(400)
    with c_b:
        st.markdown(f'<div class="pito-bubble"><b>🗣️ Pito\'nun Notu:</b><br>{curr_ex["msg"]}</div>', unsafe_allow_html=True)
        if st.session_state.feedback_msg:
            if "✅" in st.session_state.feedback_msg: st.success(st.session_state.feedback_msg)
            else: st.error(st.session_state.feedback_msg)

    # --- KOD KONTROL MERKEZİ (FORM KİLİDİ İLE KESİN ÇÖZÜM) ---
    if not st.session_state.exercise_passed:
        # FORM yapısı sayesinde butona basıldığı an Ace Editor verisi Streamlit'e 'PAKET' olarak gelir.
        with st.form(key=f"pito_form_{m_idx}_{e_idx}"):
            code = st_ace(value=curr_ex['task'], language="python", theme="monokai", font_size=16, height=200, 
                          auto_update=False, key=f"ace_vX_{m_idx}_{e_idx}")
            submit = st.form_submit_button("🔍 Kodumu Kontrol Et", use_container_width=True)
            
            if submit:
                # 1. Aşama: Boşluk Kontrolü (Hata Saymaz, Sadece Durdurur)
                if "___" in code:
                    st.session_state.feedback_msg = "⚠️ Pito bekliyor: Lütfen önce boşluğu doldur!"; st.rerun()
                
                # 2. Aşama: Kodun Çalıştırılması
                output, locals_env, run_status = run_pito_code(code)
                
                # 3. Aşama: BAŞARI KONTROLÜ (HATA DÖNGÜSÜNDEN ÖNCE GELMELİ)
                if run_status and curr_ex['check'](code, output, locals_env):
                    st.session_state.update({
                        'feedback_msg': "✅ Tebrikler! Harika bir iş çıkardın. Bir sonraki adıma geçebilirsin!",
                        'exercise_passed': True, 'pito_emotion': 'mutlu', 'fail_count': 0
                    })
                    ex_key = f"{m_idx}_{e_idx}"
                    if ex_key not in st.session_state.scored_exercises:
                        st.session_state.total_score += st.session_state.current_potential_score
                        st.session_state.scored_exercises.add(ex_key)
                    st.rerun()
                else:
                    # 4. Aşama: HATA DÖNGÜSÜ (Sadece yanlışsa buraya düşer)
                    st.session_state.fail_count += 1
                    st.session_state.pito_emotion = "uzgun"
                    st.session_state.current_potential_score = max(0, st.session_state.current_potential_score - 5)
                    
                    msgs = {
                        1: f"❌ Bu ilk hatan lütfen daha dikkatli ol ve tekrar dene (Potansiyel: {st.session_state.current_potential_score}).",
                        2: f"❌ Bu 2. hatan lütfen daha dikkatli ol ve tekrar dene (Potansiyel: {st.session_state.current_potential_score}).",
                        3: f"🚀 Yolun sonuna yaklaştın! İpucu: {curr_ex['hint']}",
                        4: "🌿 Bu egzersizden puan alamadın ama üzülme aşağıda çözümü inceleyebilirsin."
                    }
                    st.session_state.feedback_msg = msgs.get(st.session_state.fail_count, msgs[4])
                    if st.session_state.fail_count >= 4: st.session_state.exercise_passed = True
                    st.rerun()

    # --- NAVİGASYON (SADECE BAŞARIDA VEYA 4. HATADA) ---
    if st.session_state.exercise_passed:
        if st.session_state.fail_count >= 4:
            st.warning("🔍 Doğru Mantığı Kavrayalım:")
            st.code(curr_ex['solution'], language="python")
        
        if st.button("➡️ Sonraki Adıma Geç", use_container_width=True):
            st.session_state.current_exercise += 1
            # Modül Bitim Kontrolü
            if st.session_state.current_exercise >= len(training_data[st.session_state.current_module]["exercises"]):
                st.session_state.current_module += 1
                st.session_state.current_exercise = 0
            
            # Reset State
            st.session_state.update({
                'exercise_passed': False, 'fail_count': 0, 'feedback_msg': "", 
                'current_potential_score': 20, 'pito_emotion': "standart"
            })
            st.rerun()
