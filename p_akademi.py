import streamlit as st
from streamlit_ace import st_ace
import sys
from io import StringIO
import pandas as pd
from datetime import datetime
from streamlit_gsheets import GSheetsConnection
import os

# --- 1. SAYFA YAPILANDIRMASI ---
st.set_page_config(layout="wide", page_title="Pito Python Akademi", initial_sidebar_state="collapsed")

SINIFLAR = ["9-A", "9-B", "10-A", "10-B", "11-A", "11-B"]

# --- 2. GÖRSEL TASARIM (CSS) ---
st.markdown("""
    <style>
    header {visibility: hidden;}
    .main .block-container {padding-top: 1rem;}
    
    .pito-bubble {
        position: relative; background: #f0f2f6; border: 2px solid #3a7bd5;
        border-radius: 15px; padding: 20px; margin-bottom: 20px;
        color: #1e1e1e; font-size: 1.1rem; font-weight: 500;
        box-shadow: 4px 4px 10px rgba(0,0,0,0.1);
    }
    .pito-bubble:after {
        content: ''; position: absolute; bottom: -20px; left: 40px;
        border-width: 20px 20px 0; border-style: solid;
        border-color: #3a7bd5 transparent; display: block; width: 0;
    }
    
    .leaderboard-card {
        background: linear-gradient(135deg, #1e1e1e, #2d2d2d);
        border: 1px solid #444; border-radius: 15px;
        padding: 15px; margin-bottom: 10px; color: white;
    }
    .rank-1 { border: 2px solid #FFD700; box-shadow: 0 0 10px #FFD700; }
    .rank-2 { border: 2px solid #C0C0C0; }
    .rank-3 { border: 2px solid #CD7F32; }
    
    .stButton > button {
        width: 100%; border-radius: 12px; height: 3.5em;
        background: linear-gradient(45deg, #3a7bd5, #00d2ff) !important;
        color: white !important; font-weight: bold; border: none;
        transition: 0.3s;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. VERİ YÖNETİMİ ---
SHEET_URL = "https://docs.google.com/spreadsheets/d/1lat8rO2qm9QnzEUYlzC_fypG3cRkGlJfSfTtwNvs318/edit#gid=0"
conn = st.connection("gsheets", type=GSheetsConnection)

def get_db():
    try:
        df = conn.read(spreadsheet=SHEET_URL, ttl=0)
        if df is None or df.empty:
            return pd.DataFrame(columns=["Okul No", "Öğrencinin Adı", "Sınıf", "Puan", "Rütbe", "Tamamlanan Modüller", "Mevcut Modül", "Mevcut Egzersiz", "Tarih"])
        df["Okul No"] = df["Okul No"].astype(str).str.strip()
        return df.dropna(subset=["Okul No"])
    except:
        return pd.DataFrame(columns=["Okul No", "Öğrencinin Adı", "Sınıf", "Puan", "Rütbe", "Tamamlanan Modüller", "Mevcut Modül", "Mevcut Egzersiz", "Tarih"])

def auto_save_progress():
    try:
        no = str(st.session_state.student_no).strip()
        score = st.session_state.total_score
        # Veri tabanındaki en son kaydedilmiş konumu korumak için kontrol
        df_old = get_db()
        user_row = df_old[df_old["Okul No"] == no]
        
        # Eğer öğrenci geçmişe bakıyorsa veri tabanındaki ilerlemesini düşürme
        if not user_row.empty:
            db_m = int(user_row.iloc[0]["Mevcut Modül"])
            db_e = int(user_row.iloc[0]["Mevcut Egzersiz"])
            save_m = max(db_m, st.session_state.current_module)
            save_e = max(db_e, st.session_state.current_exercise) if save_m == db_m else st.session_state.current_exercise
        else:
            save_m, save_e = st.session_state.current_module, st.session_state.current_exercise

        progress = ",".join(["1" if m else "0" for m in st.session_state.completed_modules])
        rank = "🌱 Python Çırağı" if score < 200 else "💻 Kod Yazarı" if score < 500 else "🛠️ Yazılım Geliştirici" if score < 850 else "🏆 Python Ustası"
        
        df_clean = df_old[df_old["Okul No"] != no]
        new_row = pd.DataFrame([[no, st.session_state.student_name, st.session_state.student_class, score, rank, progress, save_m, save_e, datetime.now().strftime("%H:%M:%S")]], 
                               columns=["Okul No", "Öğrencinin Adı", "Sınıf", "Puan", "Rütbe", "Tamamlanan Modüller", "Mevcut Modül", "Mevcut Egzersiz", "Tarih"])
        
        conn.update(spreadsheet=SHEET_URL, data=pd.concat([df_clean, new_row], ignore_index=True))
    except: pass

# --- 4. SESSION STATE ---
if 'student_name' not in st.session_state:
    for k, v in {'student_name': "", 'student_no': "", 'student_class': "", 'completed_modules': [False]*8, 
                 'current_module': 0, 'current_exercise': 0, 'exercise_passed': False, 'total_score': 0, 
                 'scored_exercises': set(), 'db_module': 0, 'db_exercise': 0}.items():
        st.session_state[k] = v

PITO_IMG = "assets/pito.png"

# --- 5. GİRİŞ VE RECOVERY ---
if st.session_state.student_name == "":
    st.markdown("<br>", unsafe_allow_html=True)
    _, col_mid, _ = st.columns([1, 2, 1])
    with col_mid:
        st.markdown('<div class="pito-bubble">Merhaba! Ben <b>Pito</b>. Numaranı gir, senin için kaldığın yeri hatırlayayım!</div>', unsafe_allow_html=True)
        if os.path.exists(PITO_IMG): st.image(PITO_IMG, width=180)
        else: st.image("https://img.icons8.com/fluency/180/robot-viewer.png", width=150)
        
        st.title("Pito Akademi")
        in_no = st.text_input("Okul Numaran:")
        in_name = st.text_input("Adın Soyadın:")
        in_class = st.selectbox("Sınıfın:", SINIFLAR)
        
        if st.button("Atölyeye Gir 🚀"):
            if in_no.strip() and in_name.strip():
                st.session_state.student_no, st.session_state.student_name, st.session_state.student_class = in_no.strip(), in_name.strip(), in_class
                df = get_db()
                user_data = df[df["Okul No"] == in_no.strip()]
                if not user_data.empty:
                    row = user_data.iloc[0]
                    st.session_state.total_score = int(row["Puan"])
                    st.session_state.current_module = int(row["Mevcut Modül"])
                    st.session_state.current_exercise = int(row["Mevcut Egzersiz"])
                    st.session_state.db_module = st.session_state.current_module
                    st.session_state.db_exercise = st.session_state.current_exercise
                    st.session_state.completed_modules = [True if x == "1" else False for x in str(row["Tamamlanan Modüller"]).split(",")]
                st.rerun()
            else: st.warning("Alanları doldur!")
    st.stop()

# --- 6. MÜFREDAT ---
training_data = [
    {"module_title": "1. Giriş ve Çıktı", "exercises": [
        {"msg": "Ekrana 'Merhaba Pito' yazdır.", "task": "print('___')", "check": lambda c, o: "Merhaba Pito" in o},
        {"msg": "100 sayısını yazdır.", "task": "print(___)", "check": lambda c, o: "100" in o},
        {"msg": "Puan: 100 yazdır.", "task": "print('Puan:', ___)", "check": lambda c, o: "100" in o},
        {"msg": "Yorum satırı ekle (#).", "task": "___ Bu bir yorumdur", "check": lambda c, o: "#" in c},
        {"msg": "Alt satır (\\n) karakteri kullan.", "task": "print('Üst' + '___' + 'Alt')", "check": lambda c, o: "\n" in o}
    ]},
    {"module_title": "2. Değişkenler ve Giriş", "exercises": [
        {"msg": "yas = 15 tanımla.", "task": "yas = ___\nprint(yas)", "check": lambda c, o: "15" in o},
        {"msg": "isim = 'Pito' ata.", "task": "isim = '___'\nprint(isim)", "check": lambda c, o: "Pito" in o},
        {"msg": "Giriş al (input).", "task": "ad = ___('Adın: ')\nprint(ad)", "check": lambda c, o: "input" in c},
        {"msg": "Metne çevir (str).", "task": "s = 10\nprint(___(s))", "check": lambda c, o: "str" in c},
        {"msg": "Sayıya çevir (int).", "task": "n = ___(___('S: '))\nprint(n + 5)", "check": lambda c, o: "int" in c}
    ]}
]

# --- 7. PANEL DÜZENİ ---
col_main, col_side = st.columns([3, 1])

with col_main:
    st.markdown(f"#### 👋 {st.session_state.student_name} ({st.session_state.student_class}) | ⭐ Puan: {st.session_state.total_score}")
    
    mod_titles = [f"{'✅' if st.session_state.completed_modules[i] else '📖'} {m['module_title']}" for i, m in enumerate(training_data)]
    sel_mod = st.selectbox("Modül Seç:", mod_titles, index=st.session_state.current_module)
    new_idx = mod_titles.index(sel_mod)
    
    if new_idx != st.session_state.current_module:
        st.session_state.current_module = new_idx
        # Eğer geçmiş bir modüle gidilirse, o modülün ilk egzersizinden başlat
        if new_idx < st.session_state.db_module: st.session_state.current_exercise = 0
        else: st.session_state.current_exercise = st.session_state.db_exercise
        st.session_state.exercise_passed = False
        st.rerun()

    st.divider()
    m_idx, e_idx = st.session_state.current_module, st.session_state.current_exercise
    curr_ex = training_data[m_idx]["exercises"][e_idx]

    # KİLİTLEME MANTIĞI: Geçmiş modül veya egzersiz mi?
    is_locked = False
    if m_idx < st.session_state.db_module: is_locked = True
    elif m_idx == st.session_state.db_module and e_idx < st.session_state.db_exercise: is_locked = True

    c_img, c_msg = st.columns([1, 4])
    with c_img:
        st.image(PITO_IMG if os.path.exists(PITO_IMG) else "https://img.icons8.com/fluency/200/robot-viewer.png", width=140)
    with c_msg:
        st.info(f"##### 🗣️ Pito Diyor Ki:\n\n{curr_ex['msg']}")
        st.caption(f"Adım: {e_idx + 1}/5 {'🔒 (Tamamlandı)' if is_locked else ''}")

    # ACE Editör (Kilitli ise readonly)
    code = st_ace(value=curr_ex['task'], language="python", theme="dracula", font_size=14, height=200, readonly=is_locked, key=f"ace_{m_idx}_{e_idx}")

    if not is_locked:
        if st.button("🔍 Görevi Kontrol Et"):
            old_stdout, new_stdout = sys.stdout, StringIO()
            sys.stdout = new_stdout
            try:
                exec(code.replace("___", "None"), {"input": lambda p: "10"})
                sys.stdout = old_stdout
                output = new_stdout.getvalue()
                st.code(output if output else "Başarılı!")
                if curr_ex['check'](code, output) and "___" not in code:
                    st.session_state.exercise_passed = True
                    st.success("Tebrikler! ✅")
                else: st.warning("Hatalı!")
            except Exception as e:
                sys.stdout = old_stdout
                st.error(f"Hata: {e}")
    else:
        st.warning("⚡ Bu görevi daha önce tamamladın. Sadece kodunu inceleyebilirsin.")

    if st.session_state.exercise_passed or is_locked:
        if e_idx < 4:
            if st.button("➡️ Sonraki Adım"):
                if not is_locked: st.session_state.db_exercise += 1
                st.session_state.current_exercise += 1
                st.session_state.exercise_passed = False
                auto_save_progress(); st.rerun()
        else:
            if st.button("🏆 Modülü Bitir" if not is_locked else "🏠 Sonraki Modüle Bak"):
                if not is_locked:
                    st.session_state.completed_modules[m_idx] = True
                    st.session_state.db_module += 1
                    st.session_state.db_exercise = 0
                st.session_state.current_module += 1
                st.session_state.current_exercise = 0
                auto_save_progress(); st.balloons(); st.rerun()

with col_side:
    st.markdown(f"### 🏆 Sınıf Liderleri")
    df_db = get_db()
    df_class = df_db[df_db["Sınıf"] == st.session_state.student_class]
    if not df_class.empty:
        df_lb = df_class.sort_values(by="Puan", ascending=False).drop_duplicates(subset=["Okul No"]).head(10)
        for i, (_, row) in enumerate(df_lb.iterrows()):
            medal = "🥇" if i == 0 else "🥈" if i == 1 else "🥉" if i == 2 else "⭐"
            st.markdown(f'<div class="leaderboard-card"><b>{medal} {row["Öğrencinin Adı"]}</b><br>{row["Puan"]} Puan</div>', unsafe_allow_html=True)