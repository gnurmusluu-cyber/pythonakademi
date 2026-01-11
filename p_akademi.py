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

# --- 2. DURUM YÖNETİMİ (SESSION STATE) ---
if 'is_logged_in' not in st.session_state:
    st.session_state.update({
        'student_name': "", 'student_no': "", 'student_class': "", 'completed_modules': [False]*8,
        'current_module': 0, 'current_exercise': 0, 'exercise_passed': False, 'total_score': 0,
        'scored_exercises': set(), 'db_module': 0, 'db_exercise': 0, 'is_logged_in': False,
        'current_potential_score': 20, 'fail_count': 0, 'feedback_msg': "", 'pito_emotion': "merhaba"
    })

SINIFLAR = ["9-A", "9-B", "10-A", "10-B", "11-A", "11-B"]
RUTBELER = ["🥚 Egg", "🌱 Çırak", "🪵 Oduncu", "🧱 Mimarı", "🌀 Usta", "📋 Uzman", "📦 Kaptan", "🤖 Robot", "🏆 Hero"]

# --- 3. CSS MÜHÜRÜ (CMD/APPLY BUTONUNU KÖKTEN SİL) ---
st.markdown("""
    <style>
    header {visibility: hidden;}
    .main .block-container {padding-top: 1rem; background-color: #0f172a;}
    
    /* ACE EDITOR: APPLY BUTONUNU CSS İLE KÖKTEN SİL */
    [data-testid="stAceApplyButton"], .ace-apply-button, .ace_button, .ace_search { 
        display: none !important; visibility: hidden !important; height: 0 !important; 
    }
    iframe { border-radius: 15px !important; border: 2px solid #3a7bd5 !important; }

    /* ÜST KİMLİK KARTI VE NEON */
    .user-header-box {
        background-color: #ffffff !important; border: 3px solid #3a7bd5 !important;
        border-radius: 20px !important; padding: 15px 25px !important; margin-bottom: 25px !important;
        display: flex !important; justify-content: space-between !important; align-items: center !important;
    }
    .score-badge { 
        background: linear-gradient(45deg, #3a7bd5, #00d2ff) !important; color: white !important;
        padding: 8px 20px !important; border-radius: 30px !important; font-weight: 900 !important;
    }

    /* KONUŞMA BALONU */
    .pito-bubble {
        position: relative; background: #ffffff !important; border: 3.5px solid #3a7bd5 !important;
        border-radius: 30px !important; padding: 30px !important; color: #1e293b !important;
        font-weight: 500 !important; line-height: 1.8 !important; margin-bottom: 20px !important;
    }
    .pito-bubble::after {
        content: ''; position: absolute; left: -28px; top: 50px;
        border-width: 18px 28px 18px 0; border-style: solid; border-color: transparent #3a7bd5 transparent transparent;
    }

    .stButton > button {
        border-radius: 18px; height: 4.2em; background: linear-gradient(45deg, #3a7bd5, #00d2ff) !important;
        color: white !important; font-weight: bold; border: none; font-size: 1.1rem;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 4. YARDIMCI FONKSİYONLAR ---
@st.cache_resource
def load_gif_b64(name):
    p = Path(__file__).parent / "assets" / name
    return base64.b64encode(p.read_bytes()).decode() if p.exists() else None

def show_pito_gif(width=450):
    emotion_map = {"standart": "pito_dusunuyor.gif", "merhaba": "pito_merhaba.gif", "uzgun": "pito_hata.gif", "mutlu": "pito_basari.gif"}
    b64 = load_gif_b64(emotion_map.get(st.session_state.pito_emotion, "pito_dusunuyor.gif"))
    if b64: st.markdown(f'<div style="display: flex; justify-content: center;"><img src="data:image/gif;base64,{b64}" width="{width}px" style="border-radius: 25px;"></div>', unsafe_allow_html=True)

def run_pito_code(code_string, user_input="Pito"):
    if "___" in code_string: return "⚠️ Boşluk Hatası"
    old_stdout, new_stdout = sys.stdout, StringIO()
    sys.stdout = new_stdout
    local_vars = {"print": print, "input": lambda p: str(user_input), "int": int, "str": str, "len": len, "range": range, "s": 10, "L": [10, 20], "d":{'ad':'Pito'}, "t":(1,2)}
    try:
        exec(code_string, {"__builtins__": __builtins__}, local_vars)
        sys.stdout = old_stdout
        return new_stdout.getvalue(), local_vars
    except Exception as e:
        sys.stdout = old_stdout
        return f"❌ Python Hatası: {e}", local_vars

# --- 5. VERİ VE MÜFREDAT ---
training_data = [
    {"module_title": "1. İletişim: print() ve Metin Dünyası", "exercises": [
        {"msg": "**GÖREV:** Editor içine tam olarak **'Merhaba Pito'** metnini tırnaklar içerisinde yaz!", "task": "print('___')", "check": lambda c, o, l: "Merhaba Pito" in o, "solution": "print('Merhaba Pito')", "hint": "Tırnakları unutma!"},
        {"msg": "**GÖREV:** Boşluğa tırnak kullanmadan sadece **100** sayısını yaz.", "task": "print(___)", "check": lambda c, o, l: "100" in o, "solution": "print(100)", "hint": "Sayılar tırnaksız yazılır."},
    ]},
    {"module_title": "2. Hafıza: Değişkenler", "exercises": [
        {"msg": "**GÖREV:** `yas` ismindeki kutuya sayısal olarak **15** değerini ata.", "task": "yas = ___", "check": lambda c, o, l: l.get('yas') == 15, "solution": "yas = 15", "hint": "Sadece 15 yaz."},
    ]}
    # Müfredatın devamı platform kurallarına göre 40 adımdır...
]

# --- 6. ANA AKIŞ ---
col_main, col_stats = st.columns([3.2, 1])

with col_main:
    # Giriş Kontrolü
    if not st.session_state.is_logged_in:
        st.info("Lütfen laboratuvar numaranızla giriş yapın.")
        # (Giriş sistemi buraya entegre edilir, test için true sayalım)
        if st.button("Sanal Giriş (Test)"): st.session_state.is_logged_in = True; st.rerun()
        st.stop()

    curr_ex = training_data[st.session_state.current_module]["exercises"][st.session_state.current_exercise]
    
    # KİMLİK KARTI
    st.markdown(f'<div class="user-header-box"><div><span class="info-label">AKADEMİ ÖĞRENCİSİ:</span><br><span class="info-value">👤 {st.session_state.student_name}</span></div><div class="score-badge">⭐ {st.session_state.total_score} PUAN</div></div>', unsafe_allow_html=True)

    # PİTO VE MESAJ
    c_p, c_b = st.columns([1.5, 3.5])
    with c_p: show_pito_gif(400)
    with c_b:
        st.markdown(f'<div class="pito-bubble"><b>Pito Diyor ki:</b><br>{curr_ex["msg"]}</div>', unsafe_allow_html=True)
        # GERİ BİLDİRİM PANELİ (MÜHÜRLÜ KONUM)
        if st.session_state.feedback_msg:
            if "✅" in st.session_state.feedback_msg: st.success(st.session_state.feedback_msg)
            else: st.error(st.session_state.feedback_msg)

    # --- KOD DEĞERLENDİRME SİSTEMİ (SIFIRDAN İNŞA) ---
    if not st.session_state.exercise_passed:
        # Editör (Key her seferinde sabit kalmalı ki metin silinmesin)
        code = st_ace(value=curr_ex['task'], language="python", theme="dracula", font_size=16, height=200, 
                      auto_update=True, key=f"ace_{st.session_state.current_module}_{st.session_state.current_exercise}")
        
        if st.button("🔍 Kodumu Kontrol Et", use_container_width=True):
            if "___" in code:
                st.session_state.feedback_msg = "⚠️ Pito bekliyor: Lütfen önce boşluğu doldur!"
                st.rerun()
            else:
                output, locals_env = run_pito_code(code)
                # DOĞRULUK KONTROLÜ
                is_correct = curr_ex['check'](code, output, locals_env)
                
                if is_correct:
                    # BAŞARI DURUMU
                    st.session_state.feedback_msg = "✅ Tebrikler! Harika bir iş çıkardın. Bir sonraki adıma geçebilirsin!"
                    st.session_state.exercise_passed = True
                    st.session_state.pito_emotion = "mutlu"
                    st.session_state.total_score += st.session_state.current_potential_score
                    st.rerun()
                else:
                    # HATA DURUMU
                    st.session_state.fail_count += 1
                    st.session_state.pito_emotion = "uzgun"
                    st.session_state.current_potential_score = max(0, st.session_state.current_potential_score - 5)
                    
                    # Pedagojik Hata Mesajları (Tam istediğiniz gibi)
                    if st.session_state.fail_count == 1:
                        st.session_state.feedback_msg = f"❌ Bu ilk hatan lütfen daha dikkatli ol ve tekrar dene (Kazanacağın puan {st.session_state.current_potential_score}'e düştü)."
                    elif st.session_state.fail_count == 2:
                        st.session_state.feedback_msg = f"❌ Bu 2. hatan lütfen daha dikkatli ol ve tekrar dene (Kazanacağın puan {st.session_state.current_potential_score}'e düştü)."
                    elif st.session_state.fail_count == 3:
                        st.session_state.feedback_msg = f"❌ Bu 3. hatan lütfen daha dikkatli ol ve tekrar dene. \n\n💡 İpucu: {curr_ex['hint']}"
                    else:
                        st.session_state.exercise_passed = True # 4. hatada geçişe izin ver
                        st.session_state.feedback_msg = "🌿 Bu egzersizden puan alamadın ama üzülme aşağıda çözümü inceleyebilirsin."
                    st.rerun()

    # BAŞARI VEYA 4 HATA SONRASI NAVİGASYON
    if st.session_state.exercise_passed:
        if st.session_state.fail_count >= 4:
            st.warning("🔍 Doğru Mantığı Kavrayalım:")
            st.code(curr_ex['solution'], language="python")
        
        if st.button("➡️ Sonraki Adıma Geç", use_container_width=True):
            st.session_state.current_exercise += 1
            if st.session_state.current_exercise >= len(training_data[st.session_state.current_module]["exercises"]):
                st.session_state.current_module += 1
                st.session_state.current_exercise = 0
            
            # Reset state for next exercise
            st.session_state.update({
                'exercise_passed': False, 'fail_count': 0, 'feedback_msg': "", 
                'current_potential_score': 20, 'pito_emotion': "standart"
            })
            st.rerun()
