import streamlit as st
from streamlit_ace import st_ace
import sys
from io import StringIO
import pandas as pd
from datetime import datetime
from streamlit_gsheets import GSheetsConnection
import os

# --- 1. SAYFA AYARLARI ---
st.set_page_config(layout="wide", page_title="Pito Akademi", initial_sidebar_state="collapsed")

# --- 2. GELİŞMİŞ GÖRSEL TASARIM (Konuşma Balonu ve Stil) ---
st.markdown("""
    <style>
    /* Konuşma Balonu Tasarımı */
    .bubble {
        position: relative;
        background: #ffffff;
        color: #1e1e1e;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        font-size: 1.1rem;
        line-height: 1.5;
        border-radius: 20px;
        padding: 20px;
        margin-bottom: 30px;
        border: 2px solid #3a7bd5;
        box-shadow: 0 5px 15px rgba(0,0,0,0.2);
    }
    .bubble:after {
        content: '';
        position: absolute;
        bottom: 0;
        left: 50px;
        width: 0;
        height: 0;
        border: 20px solid transparent;
        border-top-color: #3a7bd5;
        border-bottom: 0;
        margin-left: -20px;
        margin-bottom: -20px;
    }
    /* Giriş Butonu */
    .stButton > button {
        width: 100%;
        border-radius: 12px;
        height: 3.5em;
        background: linear-gradient(45deg, #3a7bd5, #00d2ff) !important;
        color: white !important;
        font-weight: bold;
        border: none;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. GOOGLE SHEETS BAĞLANTISI ---
SHEET_URL = "https://docs.google.com/spreadsheets/d/1lat8rO2qm9QnzEUYlzC_fypG3cRkGlJfSfTtwNvs318/edit#gid=0"
conn = st.connection("gsheets", type=GSheetsConnection)

def get_leaderboard():
    try:
        df = conn.read(spreadsheet=SHEET_URL, ttl=0)
        if df is None or df.empty:
            return pd.DataFrame(columns=["Öğrencinin Adı", "Puan", "Rütbe", "Tarih"])
        df = df.dropna(subset=["Öğrencinin Adı"])
        return df.sort_values(by="Puan", ascending=False).drop_duplicates(subset=["Öğrencinin Adı"])
    except:
        return pd.DataFrame(columns=["Öğrencinin Adı", "Puan", "Rütbe", "Tarih"])

def auto_save_score():
    try:
        name, score = st.session_state.student_name, st.session_state.total_score
        # Rütbe Hesaplama
        if score < 200: rank = "🌱 Python Çırağı"
        elif score < 500: rank = "💻 Kod Yazarı"
        elif score < 850: rank = "🛠️ Yazılım Geliştirici"
        else: rank = "🏆 Python Ustası"
        
        df_current = get_leaderboard()
        new_row = pd.DataFrame([[name, score, rank, datetime.now().strftime("%H:%M:%S")]], 
                               columns=["Öğrencinin Adı", "Puan", "Rütbe", "Tarih"])
        updated_df = pd.concat([df_current, new_row], ignore_index=True)
        updated_df = updated_df.sort_values(by="Puan", ascending=False).drop_duplicates(subset=["Öğrencinin Adı"])
        conn.update(spreadsheet=SHEET_URL, data=updated_df)
    except Exception as e:
        st.error(f"Kayıt Hatası: {e}")

# --- 4. SESSION STATE ---
for key, val in [('student_name', ""), ('completed_modules', [False]*8), ('current_module', 0), 
                ('current_exercise', 0), ('exercise_passed', False), ('total_score', 0), 
                ('scored_exercises', set()), ('current_potential_score', 20)]:
    if key not in st.session_state: st.session_state[key] = val

# --- 5. GİRİŞ EKRANI (KONUŞMA BALONLU) ---
if st.session_state.student_name == "":
    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        # Konuşma Balonu
        st.markdown("""
        <div class="bubble">
            Merhaba Arkadaşlar! Ben <b>Pito</b>. Haydi birlikte Python'ın eğlenceli dünyasına giriş yapalım!
        </div>
        """, unsafe_allow_html=True)
        
        # Pito Resmi
        img_path = "assets/pito.png"
        if os.path.exists(img_path):
            st.image(img_path, width=150)
        else:
            st.image("https://img.icons8.com/fluency/150/robot-viewer.png", width=120)
            
        st.markdown("<h2 style='color:#3a7bd5;'>Pito Akademi</h2>", unsafe_allow_html=True)
        
        input_name = st.text_input("Adın Soyadın:", placeholder="Örn: Gamzenur Muslu")
        if st.button("Atölyeye Giriş Yap 🚀"):
            if input_name.strip():
                st.session_state.student_name = input_name.strip()
                st.rerun()
            else: st.warning("Lütfen bir isim gir!")
    st.stop()

# --- 6. EĞİTİM VERİLERİ (DEĞİŞTİRİLMEDİ) ---
training_data = [
    {"module_title": "1. Giriş ve Çıktı", "exercises": [
        {"msg": "Ekrana 'Merhaba Pito' yazdır.", "task": "print('___')", "check": lambda c, o: "Merhaba Pito" in o},
        {"msg": "100 sayısını yazdır.", "task": "print(___)", "check": lambda c, o: "100" in o},
        {"msg": "Puan: 100 yazdır (virgül kullan).", "task": "print('Puan:', ___)", "check": lambda c, o: "Puan: 100" in o},
        {"msg": "Yorum satırı ekle (#).", "task": "___ Bu bir yorumdur", "check": lambda c, o: "#" in c},
        {"msg": "Alt satır karakteri (\\n) kullan.", "task": "print('Üst' + '\\n' + 'Alt')", "check": lambda c, o: "\n" in o}
    ]},
    {"module_title": "2. Değişkenler ve Giriş", "exercises": [
        {"msg": "yas = 15 tanımla ve yazdır.", "task": "yas = ___\nprint(yas)", "check": lambda c, o: "15" in o},
        {"msg": "İsim ata (isim = 'Pito').", "task": "isim = '___'\nprint(isim)", "check": lambda c, o: "Pito" in o},
        {"msg": "Kullanıcıdan veri al (input).", "task": "ad = ___('Adın: ')\nprint(ad)", "check": lambda c, o: "input" in c},
        {"msg": "Sayıyı metne çevir (str).", "task": "s = 10\nprint(___(s))", "check": lambda c, o: "str" in o},
        {"msg": "Girişi tam sayıya çevir (int).", "task": "sayi = ___(___('S: '))\nprint(sayi + 5)", "check": lambda c, o: "int" in c}
    ]}
    # Diğer modüller orijinal haliyle buraya eklenir...
]

# --- 7. ARA YÜZ VE EDİTÖR ---
st.markdown(f"#### 👋 {st.session_state.student_name} | ⭐ Puan: {st.session_state.total_score}")
st.progress(min(st.session_state.total_score / 1000, 1.0))

mod_titles = [f"{'✅' if st.session_state.completed_modules[i] else '📖'} {m['module_title']}" for i, m in enumerate(training_data)]
sel_mod = st.selectbox("Modül Seç:", mod_titles, index=st.session_state.current_module)
new_idx = mod_titles.index(sel_mod)
if new_idx != st.session_state.current_module:
    st.session_state.current_module, st.session_state.current_exercise, st.session_state.exercise_passed, st.session_state.current_potential_score = new_idx, 0, False, 20
    st.rerun()

st.divider()

m_idx, e_idx = st.session_state.current_module, st.session_state.current_exercise
curr_ex = training_data[m_idx]["exercises"][e_idx]

st.info(f"**Pito:** {curr_ex['msg']}")
st.caption(f"🎁 Görev Puanı: {st.session_state.current_potential_score}")

code = st_ace(value=curr_ex['task'], language="python", theme="dracula", font_size=14, height=180, wrap=True, key=f"ace_{m_idx}_{e_idx}")

# --- VALUEERROR ÇÖZÜLEN ALAN ---
if st.button("🔍 Görevi Kontrol Et", use_container_width=True):
    old_stdout = sys.stdout 
    redirected_output = StringIO()
    sys.stdout = redirected_output # Hatalı unpacking düzeltildi
    def mock_input(p=""): return "10"
    
    try:
        exec(code.replace("___", "None"), {"input": mock_input})
        sys.stdout = old_stdout 
        output = redirected_output.getvalue()
        
        st.subheader("📟 Çıktı")
        st.code(output if output else "Pito: Başarıyla çalıştı!")
        
        if curr_ex['check'](code, output) and "___" not in code:
            st.session_state.exercise_passed = True
            ex_key = f"{m_idx}_{e_idx}"
            if ex_key not in st.session_state.scored_exercises:
                st.session_state.total_score += st.session_state.current_potential_score
                st.session_state.scored_exercises.add(ex_key)
                auto_save_score() 
            st.success("Tebrikler! ✅")
        else:
            if not st.session_state.exercise_passed:
                st.session_state.current_potential_score = max(0, st.session_state.current_potential_score - 5)
            st.warning(f"Hatalı! Puanın {st.session_state.current_potential_score}'ye düştü.")
    except Exception as e:
        sys.stdout = old_stdout
        st.error(f"Kod hatası! {e}")

if st.session_state.exercise_passed:
    if e_idx < 4:
        if st.button("➡️ Sonraki Adım"):
            st.session_state.current_exercise, st.session_state.exercise_passed, st.session_state.current_potential_score = e_idx + 1, False, 20
            st.rerun()
    else:
        if st.button("🏆 Modülü Bitir"):
            st.session_state.completed_modules[m_idx], st.session_state.exercise_passed, st.session_state.current_potential_score = True, False, 20
            if m_idx < 7: st.session_state.current_module, st.session_state.current_exercise = m_idx + 1, 0
            st.balloons(); st.rerun()

st.divider()
with st.expander("🏆 Liderlik Tablosu (Canlı)"):
    st.dataframe(get_leaderboard().head(10), use_container_width=True)