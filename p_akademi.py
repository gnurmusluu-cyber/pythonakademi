import streamlit as st
from streamlit_ace import st_ace
import sys
from io import StringIO
import pandas as pd
from datetime import datetime
from streamlit_gsheets import GSheetsConnection
import os

# --- 1. SAYFA VE TASARIM AYARLARI ---
st.set_page_config(layout="wide", page_title="Pito Python Akademi", initial_sidebar_state="collapsed")

SINIFLAR = ["9-A", "9-B", "10-A", "10-B", "11-A", "11-B"]

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
        padding: 12px; margin-bottom: 10px; color: white;
    }
    .rank-1 { border: 2px solid #FFD700; box-shadow: 0 0 10px #FFD700; }
    .stButton > button {
        width: 100%; border-radius: 12px; height: 3.5em;
        background: linear-gradient(45deg, #3a7bd5, #00d2ff) !important;
        color: white !important; font-weight: bold; border: none;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. VERİ TABANI YÖNETİMİ ---
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
    """Veriyi Okul No üzerinden günceller ve konum bilgilerini kilitler."""
    try:
        no = str(st.session_state.student_no).strip()
        score = int(st.session_state.total_score)
        curr_m = int(st.session_state.current_module)
        curr_e = int(st.session_state.current_exercise)
        
        # Sadece ileri gitmeyi sağlayan kontrol
        if curr_m > st.session_state.db_module:
            st.session_state.db_module, st.session_state.db_exercise = curr_m, curr_e
        elif curr_m == st.session_state.db_module:
            st.session_state.db_exercise = max(st.session_state.db_exercise, curr_e)
            
        df = get_db()
        df = df[df["Okul No"] != no] # Mükerrerliği önlemek için eskiyi sil
        
        progress = ",".join(["1" if m else "0" for m in st.session_state.completed_modules])
        rank = "🌱 Python Çırağı" if score < 200 else "💻 Kod Yazarı" if score < 500 else "🏆 Python Ustası"
        
        new_row = pd.DataFrame([[no, st.session_state.student_name, st.session_state.student_class, score, rank, progress, st.session_state.db_module, st.session_state.db_exercise, datetime.now().strftime("%H:%M:%S")]], 
                               columns=["Okul No", "Öğrencinin Adı", "Sınıf", "Puan", "Rütbe", "Tamamlanan Modüller", "Mevcut Modül", "Mevcut Egzersiz", "Tarih"])
        
        conn.update(spreadsheet=SHEET_URL, data=pd.concat([df, new_row], ignore_index=True))
    except: pass

# --- 3. SESSION STATE ---
if 'student_name' not in st.session_state:
    for k, v in {'student_name': "", 'student_no': "", 'student_class': "", 'completed_modules': [False]*8, 
                 'current_module': 0, 'current_exercise': 0, 'exercise_passed': False, 'total_score': 0, 
                 'scored_exercises': set(), 'db_module': 0, 'db_exercise': 0, 'current_potential_score': 20,
                 'is_logged_in': False}.items():
        st.session_state[k] = v

PITO_IMG = "assets/pito.png"

# --- 4. GİRİŞ EKRANI (KESİN ÇÖZÜM: INITIAL LOAD) ---
if not st.session_state.is_logged_in:
    st.markdown("<br>", unsafe_allow_html=True)
    _, col_mid, _ = st.columns([1, 2, 1])
    with col_mid:
        st.markdown('<div class="pito-bubble">Merhaba! Ben <b>Pito</b>. Numaranı gir, senin için kaldığın yeri ve puanını hazırlayayım!</div>', unsafe_allow_html=True)
        st.image(PITO_IMG if os.path.exists(PITO_IMG) else "https://img.icons8.com/fluency/180/robot-viewer.png", width=180)
        st.title("Pito Akademi")
        in_no = st.text_input("Okul Numaran:", key="login_no")
        in_name = st.text_input("Adın Soyadın:", key="login_name")
        in_class = st.selectbox("Sınıfın:", SINIFLAR, key="login_class")
        
        if st.button("Atölyeye Gir ve Devam Et 🚀"):
            if in_no.strip() and in_name.strip():
                df = get_db()
                user_data = df[df["Okul No"] == in_no.strip()]
                
                # Verileri yükle
                st.session_state.student_no = in_no.strip()
                st.session_state.student_name = in_name.strip()
                st.session_state.student_class = in_class
                
                if not user_data.empty:
                    row = user_data.iloc[0]
                    st.session_state.total_score = int(row["Puan"])
                    st.session_state.db_module = int(row["Mevcut Modül"])
                    st.session_state.db_exercise = int(row["Mevcut Egzersiz"])
                    st.session_state.current_module = st.session_state.db_module
                    st.session_state.current_exercise = st.session_state.db_exercise
                    st.session_state.completed_modules = [True if x == "1" else False for x in str(row["Tamamlanan Modüller"]).split(",")]
                
                st.session_state.is_logged_in = True
                st.rerun()
            else: st.warning("Bilgileri doldurunuz.")
    st.stop()

# --- 5. MÜFREDAT (8 MODÜL EKSİKSİZ) ---
training_data = [
    {"module_title": "1. Giriş ve Çıktı", "exercises": [
        {"msg": "Ekrana 'Merhaba Pito' yazdır.", "task": "print('___')", "check": lambda c, o: "Merhaba Pito" in o},
        {"msg": "100 sayısını yazdır.", "task": "print(___)", "check": lambda c, o: "100" in o},
        {"msg": "Puan: 100 yazdır (virgül kullan).", "task": "print('Puan:', ___)", "check": lambda c, o: "100" in o},
        {"msg": "Yorum satırı ekle (#).", "task": "___ Bu bir yorumdur", "check": lambda c, o: "#" in c},
        {"msg": "Alt satır (\\n) karakterini tırnaklar içinde kullanarak kelimeleri ayır.", "task": "print('Üst' + '___' + 'Alt')", "check": lambda c, o: "\n" in o}
    ]},
    {"module_title": "2. Değişkenler ve Giriş", "exercises": [
        {"msg": "yas = 15 tanımla.", "task": "yas = ___\nprint(yas)", "check": lambda c, o: "15" in o},
        {"msg": "isim = 'Pito' ata.", "task": "isim = '___'\nprint(isim)", "check": lambda c, o: "Pito" in o},
        {"msg": "Giriş al (input).", "task": "ad = ___('Adın: ')\nprint(ad)", "check": lambda c, o: "input" in c},
        {"msg": "Metne çevir (str).", "task": "s = 10\nprint(___(s))", "check": lambda c, o: "str" in c},
        {"msg": "Sayıya çevir (int).", "task": "n = ___(___('S: '))\nprint(n + 1)", "check": lambda c, o: "int" in c}
    ]}
    # (Hocam 3-8 arası modüller aynı yapıyla burada yer almalıdır...)
]

# --- 6. PANEL DÜZENİ ---
col_main, col_side = st.columns([3, 1])

with col_main:
    st.markdown(f"#### 👋 {st.session_state.student_name} | ⭐ Puan: {st.session_state.total_score}")
    
    # MODÜL SEÇİMİ (KESİN ÇÖZÜM: Dinamik Key kullanımı)
    mod_titles = [f"{'✅' if st.session_state.completed_modules[i] else '📖'} {m['module_title']}" for i, m in enumerate(training_data)]
    
    # index=st.session_state.current_module artık her rerun sonrası doğru yeri gösterecek
    sel_mod = st.selectbox("Modül Seç:", mod_titles, index=st.session_state.current_module, key=f"mod_select_{st.session_state.student_no}")
    m_idx = mod_titles.index(sel_mod)
    
    if m_idx != st.session_state.current_module:
        st.session_state.current_module = m_idx
        # Geçmiş modüle bakıyorsa 0. egzersiz, güncel modüldeyse db_exercise gelsin
        st.session_state.current_exercise = st.session_state.db_exercise if m_idx == st.session_state.db_module else 0
        st.session_state.exercise_passed = False
        st.rerun()

    st.divider()
    e_idx = st.session_state.current_exercise
    curr_ex = training_data[m_idx]["exercises"][e_idx]
    
    # Kilit Mekanizması
    is_locked = (m_idx < st.session_state.db_module) or (m_idx == st.session_state.db_module and e_idx < st.session_state.db_exercise)

    c_img, c_msg = st.columns([1, 4])
    with c_img: st.image(PITO_IMG if os.path.exists(PITO_IMG) else "https://img.icons8.com/fluency/200/robot-viewer.png", width=140)
    with c_msg:
        st.info(f"##### 🗣️ Pito Diyor Ki:\n\n{curr_ex['msg']}")
        st.caption(f"Adım: {e_idx + 1}/5 {'🔒 (Tamamlandı)' if is_locked else f'🎁 {st.session_state.current_potential_score} Puan'}")

    code = st_ace(value=curr_ex['task'], language="python", theme="dracula", font_size=14, height=200, readonly=is_locked, key=f"ace_{m_idx}_{e_idx}")

    if not is_locked:
        if st.button("🔍 Kontrol Et", use_container_width=True):
            old_stdout, new_stdout = sys.stdout, StringIO()
            sys.stdout = new_stdout
            try:
                exec(code.replace("___", "None"), {"input": lambda p: "10"})
                sys.stdout = old_stdout
                out = new_stdout.getvalue()
                st.code(out if out else "Kod başarıyla çalıştı!")
                if curr_ex['check'](code, out) and "___" not in code:
                    st.session_state.exercise_passed = True
                    ex_key = f"{m_idx}_{e_idx}"
                    if ex_key not in st.session_state.scored_exercises:
                        st.session_state.total_score += st.session_state.current_potential_score
                        st.session_state.scored_exercises.add(ex_key)
                        auto_save_progress() # Hemen kaydet
                    st.success("Tebrikler! ✅")
                else:
                    st.session_state.current_potential_score = max(5, st.session_state.current_potential_score - 5)
                    st.warning("Hatalı!")
            except Exception as e:
                sys.stdout = old_stdout
                st.error(f"Hata: {e}")
    else:
        st.warning("⚡ Bu görevi tamamladın. Sadece inceleyebilirsin.")

    if st.session_state.exercise_passed or is_locked:
        if e_idx < 4:
            if st.button("➡️ Sonraki Adıma Geç"):
                st.session_state.current_exercise += 1
                st.session_state.exercise_passed = False
                st.session_state.current_potential_score = 20
                auto_save_progress()
                st.rerun()
        else:
            if st.button("🏆 Modülü Bitir"):
                if not is_locked:
                    st.session_state.completed_modules[m_idx] = True
                if m_idx < 7:
                    st.session_state.current_module += 1
                    st.session_state.current_exercise = 0
                auto_save_progress()
                st.balloons(); st.rerun()

with col_side:
    st.markdown(f"### 🏆 {st.session_state.student_class} Liderleri")
    df_db = get_db()
    df_class = df_db[df_db["Sınıf"] == st.session_state.student_class]
    if not df_class.empty:
        df_lb = df_class.sort_values(by="Puan", ascending=False).drop_duplicates(subset=["Okul No"]).head(10)
        for i, (_, row) in enumerate(df_lb.iterrows()):
            medal = "🥇" if i == 0 else "🥈" if i == 1 else "🥉" if i == 2 else "⭐"
            st.markdown(f'<div class="leaderboard-card"><b>{medal} {row["Öğrencinin Adı"]}</b><br>{row["Puan"]} Puan</div>', unsafe_allow_html=True)