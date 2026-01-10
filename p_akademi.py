import streamlit as st
from streamlit_ace import st_ace
import sys
from io import StringIO
import pandas as pd
from datetime import datetime
from streamlit_gsheets import GSheetsConnection
import os
import base64

# --- 1. TASARIM VE SAYFA AYARLARI ---
st.set_page_config(layout="wide", page_title="Pito Python Akademi", initial_sidebar_state="collapsed")

# --- 2. KESİN GÖRSEL STABİLİZASYON (CSS) ---
st.markdown("""
    <style>
    [data-testid="stAppViewContainer"], [data-testid="stHeader"] { background-color: #FFFFFF !important; }
    header {visibility: hidden;}
    html, body, [class*="st-"] { color: #1E293B !important; font-family: 'Inter', sans-serif; }
    h1, h2, h3, h4, h5, h6, p, span, label, .stMarkdown { color: #1E293B !important; }

    /* Widget Görünürlük Garantisi */
    div[data-baseweb="input"] > div, div[data-baseweb="select"] > div, div[data-baseweb="base-input"] {
        background-color: #F8FAFC !important;
        color: #1E293B !important;
        border: 2px solid #E2E8F0 !important;
    }
    input { color: #1E293B !important; background-color: transparent !important; }
    div[data-baseweb="popover"] li { color: #1E293B !important; background-color: #FFFFFF !important; }

    .pito-bubble {
        position: relative; background: #F8FAFC; border: 2px solid #3a7bd5;
        border-radius: 20px; padding: 25px; margin-bottom: 25px; 
        color: #1E293B !important; font-weight: 500; font-size: 1.15rem; 
        box-shadow: 0 10px 25px rgba(58, 123, 213, 0.08);
    }
    .pito-bubble:after {
        content: ''; position: absolute; bottom: -20px; left: 40px;
        border-width: 20px 20px 0; border-style: solid; border-color: #3a7bd5 transparent;
    }

    .solution-box {
        background-color: #F0FDF4 !important; border: 2px solid #BBF7D0 !important;
        padding: 15px; border-radius: 12px; color: #166534 !important; margin: 10px 0;
    }

    .leaderboard-card { 
        background: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 15px; 
        padding: 12px; margin-bottom: 10px; color: #1E293B !important;
        box-shadow: 0 4px 6px rgba(0,0,0,0.02);
    }
    .rank-tag { display: inline-block; background: #3a7bd5; color: white !important; padding: 2px 8px; border-radius: 10px; font-size: 0.75rem; font-weight: bold; }

    .stButton > button { width: 100%; border-radius: 12px; height: 3.5em; background: linear-gradient(45deg, #3a7bd5, #00d2ff) !important; color: white !important; font-weight: 600; border: none; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. VERİ TABANI VE HAFIZA ---
SHEET_URL = "https://docs.google.com/spreadsheets/d/1lat8rO2qm9QnzEUYlzC_fypG3cRkGlJfSfTtwNvs318/edit#gid=0"
conn = st.connection("gsheets", type=GSheetsConnection)

def get_db():
    try:
        df = conn.read(spreadsheet=SHEET_URL, ttl=0)
        df["Okul No"] = df["Okul No"].astype(str).str.split('.').str[0].str.strip()
        for col in ["Puan", "Mevcut Modül", "Mevcut Egzersiz"]:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype(int)
        return df.dropna(subset=["Okul No"])
    except: return pd.DataFrame()

def force_save():
    try:
        no = str(st.session_state.student_no).strip()
        df_all = get_db()
        df_clean = df_all[df_all["Okul No"] != no]
        prog_str = ",".join(["1" if m else "0" for m in st.session_state.completed_modules])
        rank = RUTBELER[sum(st.session_state.completed_modules)]
        new_row = pd.DataFrame([[no, st.session_state.student_name, st.session_state.student_class, int(st.session_state.total_score), rank, prog_str, int(st.session_state.db_module), int(st.session_state.db_exercise), datetime.now().strftime("%H:%M:%S")]], columns=["Okul No", "Öğrencinin Adı", "Sınıf", "Puan", "Rütbe", "Tamamlanan Modüller", "Mevcut Modül", "Mevcut Egzersiz", "Tarih"])
        conn.update(spreadsheet=SHEET_URL, data=pd.concat([df_clean, new_row], ignore_index=True))
    except: pass

if 'is_logged_in' not in st.session_state:
    for k, v in {'student_name': "", 'student_no': "", 'student_class': "", 'completed_modules': [False]*8, 
                 'current_module': 0, 'current_exercise': 0, 'exercise_passed': False, 'total_score': 0, 
                 'scored_exercises': set(), 'db_module': 0, 'db_exercise': 0, 'is_logged_in': False, 
                 'current_potential_score': 20, 'celebrated': False, 'rejected_user': False, 'pito_emotion': "pito_merhaba",
                 'feedback_type': None, 'feedback_msg': ""}.items():
        st.session_state[k] = v

SINIFLAR = ["9-A", "9-B", "10-A", "10-B", "11-A", "11-B"]
RUTBELER = ["🥚 Yeni Başlayan", "🌱 Python Çırağı", "🪵 Kod Oduncusu", "🧱 Mantık Mimarı", "🌀 Döngü Ustası", "📋 Liste Uzmanı", "📦 Fonksiyon Kaptanı", "🤖 OOP Robotu", "🏆 Python Kahramanı"]

# --- 4. GİRİŞ EKRANI ---
if not st.session_state.is_logged_in:
    _, col_mid, _ = st.columns([1, 2, 1])
    with col_mid:
        st.markdown('<div class="pito-bubble">Merhaba! Ben <b>Pito</b>.<br>Python Dünyası macerasına hoş geldin!</div>', unsafe_allow_html=True)
        in_no = st.text_input("Okul Numaran:", key="login_field").strip()
        if in_no and in_no.isdigit():
            df = get_db()
            user_data = df[df["Okul No"] == in_no] if not df.empty else pd.DataFrame()
            if not user_data.empty:
                row = user_data.iloc[0]
                st.info(f"🔍 Hoş geldin **{row['Öğrencinin Adı']}**.")
                if st.button("✅ Maceraya Devam Et"):
                    mv, ev = int(row['Mevcut Modül']), int(row['Mevcut Egzersiz'])
                    st.session_state.update({'student_no': in_no, 'student_name': row["Öğrencinin Adı"], 'student_class': row["Sınıf"], 'total_score': int(row["Puan"]), 'db_module': mv, 'db_exercise': ev, 'current_module': min(mv, 7), 'current_exercise': ev, 'completed_modules': [True if x == "1" else False for x in str(row["Tamamlanan Modüller"]).split(",")], 'is_logged_in': True})
                    st.rerun()
            else:
                in_name = st.text_input("Adın Soyadın:")
                in_class = st.selectbox("Sınıfın:", SINIFLAR)
                if st.button("Akademiye Kaydol! ✨") and in_name:
                    st.session_state.update({'student_no': in_no, 'student_name': in_name, 'student_class': in_class, 'is_logged_in': True})
                    force_save(); st.rerun()
    st.stop()

# --- 5. EKSİKSİZ 8 MODÜLLÜK MÜFREDAT ---
training_data = [
    {"module_title": "1. Merhaba Dünya: print()", "exercises": [
        {"msg": "Ekrana yazı yazdırmak için **print()** kullanılır. Metinler **tırnak** içinde olmalıdır.", "task": "print('___')", "check": lambda c, o: "Merhaba" in o, "solution": "print('Merhaba Pito')"},
        {"msg": "Sayılar için tırnak gerekmez. **100** sayısını yazdır.", "task": "print(___)", "check": lambda c, o: "100" in o, "solution": "print(100)"},
        {"msg": "Farklı verileri **virgül (,)** ile ayırırız.", "task": "print('Puan:', ___)", "check": lambda c, o: "100" in o, "solution": "print('Puan:', 100)"},
        {"msg": "Yorum satırı için **#** kullanılır.", "task": "___ Not", "check": lambda c, o: "#" in c, "solution": "# Bu bir not"},
        {"msg": "Alt satır için **\\n** kullanılır.", "task": "print('Üst' + '___' + 'Alt')", "check": lambda c, o: "\n" in o, "solution": "print('Üst\\nAlt')"}
    ]},
    {"module_title": "2. Değişkenler ve input()", "exercises": [
        {"msg": "Değişkenler bilgi saklar. **yas**'a 15 ata.", "task": "yas = ___\nprint(yas)", "check": lambda c, o: "15" in o, "solution": "yas = 15"},
        {"msg": "**input()** ile bilgi al.", "task": "ad = ___('Adın: ')\nprint(ad)", "check": lambda c, o: "input" in c, "solution": "ad = input('Adın: ')"}
    ]},
    {"module_title": "3. Karar Yapıları", "exercises": [
        {"msg": "Eşitlik için **==** kullanılır.", "task": "if 10 ___ 10: print('X')", "check": lambda c, o: "==" in c, "solution": "if 10 == 10: print('X')"}
    ]},
    {"module_title": "4. Döngüler", "exercises": [
        {"msg": "**range(3)** ile 3 tur dön.", "task": "for i in ___(3): print('X')", "check": lambda c, o: o.count("X")==3, "solution": "range(3)"}
    ]},
    {"module_title": "5. Listeler", "exercises": [
        {"msg": "Liste oluştur.", "task": "L = [___, 20]", "check": lambda c, o: "10" in c, "solution": "L=[10, 20]"}
    ]},
    {"module_title": "6. Fonksiyonlar & Sözlükler", "exercises": [
        {"msg": "**def** ile fonksiyon kur.", "task": "___ f(): print('X')", "check": lambda c, o: "def" in c, "solution": "def f(): print('X')"}
    ]},
    {"module_title": "7. OOP (Nesne Tabanlı)", "exercises": [
        {"msg": "**class** ile Sınıf kur.", "task": "___ Robot: pass", "check": lambda c, o: "class" in c, "solution": "class Robot: pass"}
    ]},
    {"module_title": "8. Dosya Yönetimi", "exercises": [
        {"msg": "**'w'** kipiyle dosya aç.", "task": "dosya = ___('n.txt', '___')", "check": lambda c, o: "open" in c, "solution": "open('n.txt', 'w')"}
    ]}
]

# --- 6. ARA YÜZ VE GÜVENLİ İNDEX ---
col_main, col_side = st.columns([3, 1])

m_idx = min(st.session_state.current_module, len(training_data)-1)
if st.session_state.current_exercise >= len(training_data[m_idx]["exercises"]):
    st.session_state.current_exercise = 0

with col_main:
    # Öğrenci Bilgisi ve Rütbe
    rank_idx = sum(st.session_state.completed_modules)
    st.markdown(f"#### 👋 {RUTBELER[min(rank_idx, 8)]} {st.session_state.student_name} | ⭐ Puan: {int(st.session_state.total_score)}")
    
    prog_val = (rank_idx * 5 + st.session_state.current_exercise) / 40
    st.progress(min(prog_val, 1.0), text=f"Akademi İlerlemesi: %{int(prog_val*100)}")

    if st.session_state.db_module >= 8:
        st.success("🎉 Tebrikler! Tüm eğitim bitti."); st.stop()

    # Modül Seçimi
    mod_titles = [f"{'✅' if st.session_state.completed_modules[i] else '📖'} Modül {i+1}" for i in range(len(training_data))]
    sel_mod = st.selectbox("Ders Listesi:", mod_titles, index=m_idx, label_visibility="collapsed")
    new_m_idx = mod_titles.index(sel_mod)
    if new_m_idx != st.session_state.current_module:
        st.session_state.update({'current_module': new_m_idx, 'current_exercise': 0, 'feedback_type': None}); st.rerun()

    st.divider()
    curr_ex = training_data[m_idx]["exercises"][st.session_state.current_exercise]
    is_locked = (m_idx < st.session_state.db_module) # İNCELEME MODU KONTROLÜ

    st.info(f"##### 🗣️ Pito:\n{curr_ex['msg']}")
    code = st_ace(value=curr_ex['task'], language="python", theme="dracula", font_size=15, height=200, readonly=is_locked, key=f"ace_{m_idx}_{st.session_state.current_exercise}", auto_update=True)

    # --- ÇÖZÜM: SADECE İNCELEME MODUNDA ---
    if is_locked:
        st.markdown('<div class="solution-box">✅ <b>Pito\'nun Çözüm Örneği:</b></div>', unsafe_allow_html=True)
        st.code(curr_ex['solution'], language="python")

    if not is_locked:
        u_in = st.text_input("👇 Terminal:", key=f"t_{m_idx}") if "input(" in code else ""
        if st.button("🔍 Kodumu Kontrol Et"):
            old_stdout, new_stdout = sys.stdout, StringIO()
            sys.stdout = new_stdout
            try:
                exec(code.replace("___", "None"), {"input": lambda p: str(u_in or "10"), "print": print, "int": int, "str": str, "len": len, "open": open, "range": range})
                out = new_stdout.getvalue()
                if curr_ex['check'](code, out) and "___" not in code:
                    st.session_state.update({'exercise_passed': True, 'feedback_type': "success", 'feedback_msg': "Tebrikler!"})
                    if f"{m_idx}_{st.session_state.current_exercise}" not in st.session_state.scored_exercises:
                        st.session_state.total_score += 20
                        st.session_state.scored_exercises.add(f"{m_idx}_{st.session_state.current_exercise}")
                        if st.session_state.db_exercise < len(training_data[m_idx]["exercises"]) - 1: st.session_state.db_exercise += 1
                        else: st.session_state.db_module += 1; st.session_state.db_exercise = 0; st.session_state.completed_modules[m_idx] = True
                        force_save()
                else: st.warning("Hatalı yanıt.")
            except Exception as e: st.error(f"Hata: {e}")
            st.rerun()

    nb1, nb2 = st.columns(2)
    with nb1:
        if is_locked and st.session_state.current_exercise > 0:
            if st.button("⬅️ Önceki Adım"): st.session_state.current_exercise -= 1; st.rerun()
    with nb2:
        if st.session_state.exercise_passed or is_locked:
            if st.session_state.current_exercise < len(training_data[m_idx]["exercises"]) - 1:
                if st.button("➡️ Sonraki Adım"): st.session_state.current_exercise += 1; st.session_state.exercise_passed = False; st.rerun()

with col_side:
    st.markdown("### 🏆 Sıralama")
    df = get_db()
    t1, t2 = st.tabs(["👥 Sınıf", "🏫 Okul"])
    for t, data in zip([t1, t2], [df[df["Sınıf"] == st.session_state.student_class], df]):
        with t:
            if not data.empty:
                for _, r in data.sort_values("Puan", ascending=False).head(8).iterrows():
                    st.markdown(f'''<div class="leaderboard-card"><b>{r["Öğrencinin Adı"]}</b><br><span class="rank-tag">{r["Rütbe"]}</span> <small>({r["Sınıf"]})</small><br>⭐ {int(r["Puan"])} Puan</div>''', unsafe_allow_html=True)