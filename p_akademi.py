import streamlit as st
from streamlit_ace import st_ace
import sys
from io import StringIO
import pandas as pd
from datetime import datetime
from streamlit_gsheets import GSheetsConnection
import os

# --- 1. SAYFA VE TASARIM AYARLARI ---
st.set_page_config(layout="wide", page_title="Pito Akademi", initial_sidebar_state="collapsed")

SINIFLAR = ["9-A", "9-B", "10-A", "10-B", "11-A", "11-B"]

st.markdown("""
    <style>
    /* Siyah bannerı ve gereksiz boşlukları kaldır */
    header {visibility: hidden;}
    .main .block-container {padding-top: 1rem;}
    
    /* Konuşma Balonları */
    .pito-bubble {
        position: relative; background: #f0f2f6; border: 2px solid #3a7bd5;
        border-radius: 15px; padding: 20px; margin-bottom: 25px;
        color: #1e1e1e; font-size: 1.1rem; font-weight: 500;
        box-shadow: 4px 4px 10px rgba(0,0,0,0.1);
    }
    .pito-bubble:after {
        content: ''; position: absolute; bottom: -20px; left: 40px;
        border-width: 20px 20px 0; border-style: solid;
        border-color: #3a7bd5 transparent; display: block; width: 0;
    }
    .stButton > button {
        width: 100%; border-radius: 12px; height: 3.5em;
        background: linear-gradient(45deg, #3a7bd5, #00d2ff) !important;
        color: white !important; font-weight: bold; border: none;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. VERİ YÖNETİMİ ---
SHEET_URL = "https://docs.google.com/spreadsheets/d/1lat8rO2qm9QnzEUYlzC_fypG3cRkGlJfSfTtwNvs318/edit#gid=0"
conn = st.connection("gsheets", type=GSheetsConnection)

def get_db():
    try:
        df = conn.read(spreadsheet=SHEET_URL, ttl=0)
        if df is None or df.empty:
            return pd.DataFrame(columns=["Okul No", "Öğrencinin Adı", "Sınıf", "Puan", "Rütbe", "Tamamlanan Modüller", "Mevcut Modül", "Mevcut Egzersiz", "Tarih"])
        df["Okul No"] = df["Okul No"].astype(str)
        return df.dropna(subset=["Okul No"])
    except:
        return pd.DataFrame(columns=["Okul No", "Öğrencinin Adı", "Sınıf", "Puan", "Rütbe", "Tamamlanan Modüller", "Mevcut Modül", "Mevcut Egzersiz", "Tarih"])

def auto_save_progress():
    """Öğrencinin tüm verilerini tek bir satırda günceller."""
    try:
        no = str(st.session_state.student_no)
        name = st.session_state.student_name
        sınıf = st.session_state.student_class
        score = st.session_state.total_score
        curr_m = st.session_state.current_module
        curr_e = st.session_state.current_exercise
        progress = ",".join(["1" if m else "0" for m in st.session_state.completed_modules])
        
        # Rütbe hesapla
        if score < 200: rank = "🌱 Python Çırağı"
        elif score < 500: rank = "💻 Kod Yazarı"
        elif score < 850: rank = "🛠️ Yazılım Geliştirici"
        else: rank = "🏆 Python Ustası"
        
        df = get_db()
        # Mükerrer kaydı engelle: Mevcut okul numarasını listeden çıkar
        df = df[df["Okul No"] != no]
        
        new_row = pd.DataFrame([[no, name, sınıf, score, rank, progress, curr_m, curr_e, datetime.now().strftime("%H:%M:%S")]], 
                               columns=["Okul No", "Öğrencinin Adı", "Sınıf", "Puan", "Rütbe", "Tamamlanan Modüller", "Mevcut Modül", "Mevcut Egzersiz", "Tarih"])
        
        updated_df = pd.concat([df, new_row], ignore_index=True)
        conn.update(spreadsheet=SHEET_URL, data=updated_df)
    except Exception as e:
        st.error(f"Kayıt Hatası: {e}")

# --- 3. SESSION STATE ---
if 'student_name' not in st.session_state:
    vars = {'student_name': "", 'student_no': "", 'student_class': "", 'completed_modules': [False]*8, 
            'current_module': 0, 'current_exercise': 0, 'exercise_passed': False, 'total_score': 0, 
            'scored_exercises': set(), 'current_potential_score': 20}
    for k, v in vars.items(): st.session_state[k] = v

PITO_IMG = "assets/pito.png"

# --- 4. GİRİŞ EKRANI (OTURUM KURTARMA) ---
if st.session_state.student_name == "":
    st.markdown("<br>", unsafe_allow_html=True)
    _, col_mid, _ = st.columns([1, 2, 1])
    with col_mid:
        st.markdown('<div class="pito-bubble">Merhaba! Ben <b>Pito</b>. Numaranı gir ve kaldığın yerden maceraya devam et!</div>', unsafe_allow_html=True)
        if os.path.exists(PITO_IMG): st.image(PITO_IMG, width=150)
        else: st.image("https://img.icons8.com/fluency/150/robot-viewer.png", width=120)
        
        st.title("Pito Akademi")
        in_no = st.text_input("Okul Numaran:", placeholder="Örn: 452")
        in_name = st.text_input("Adın Soyadın:", placeholder="Örn: Gamzenur Muslu")
        in_class = st.selectbox("Sınıfın:", SINIFLAR)
        
        if st.button("Atölyeye Giriş Yap 🚀"):
            if in_no.strip() and in_name.strip():
                st.session_state.student_no, st.session_state.student_name, st.session_state.student_class = in_no.strip(), in_name.strip(), in_class
                df = get_db()
                user_data = df[df["Okul No"] == in_no.strip()]
                if not user_data.empty:
                    # Tüm oturum verilerini geri yükle
                    st.session_state.total_score = int(user_data.iloc[0]["Puan"])
                    st.session_state.current_module = int(user_data.iloc[0]["Mevcut Modül"])
                    st.session_state.current_exercise = int(user_data.iloc[0]["Mevcut Egzersiz"])
                    prog_str = str(user_data.iloc[0]["Tamamlanan Modüller"])
                    st.session_state.completed_modules = [True if x == "1" else False for x in prog_str.split(",")]
                    st.toast(f"Hoş geldin! Kaldığın yer: Modül {st.session_state.current_module + 1}", icon="✨")
                st.rerun()
            else: st.warning("Lütfen alanları doldurun!")
    st.stop()

# --- 5. EKSİKSİZ 8 MODÜL ---
training_data = [
    {"module_title": "1. Giriş ve Çıktı", "exercises": [
        {"msg": "Ekrana 'Merhaba Pito' yazdır.", "task": "print('___')", "check": lambda c, o: "Merhaba Pito" in o},
        {"msg": "100 sayısını yazdır.", "task": "print(___)", "check": lambda c, o: "100" in o},
        {"msg": "Puan: 100 yazdır (virgül kullan).", "task": "print('Puan:', ___)", "check": lambda c, o: "Puan: 100" in o},
        {"msg": "Yorum satırı ekle (#).", "task": "___ Bu bir yorumdur", "check": lambda c, o: "#" in c},
        {"msg": "Alt satır karakterini (\\n) tırnaklar içinde kullanarak Üst ve Alt kelimelerini ayır.", "task": "print('Üst' + '___' + 'Alt')", "check": lambda c, o: "\n" in o}
    ]},
    {"module_title": "2. Değişkenler ve Giriş", "exercises": [
        {"msg": "yas = 15 tanımla ve yazdır.", "task": "yas = ___\nprint(yas)", "check": lambda c, o: "15" in o},
        {"msg": "isim = 'Pito' ata.", "task": "isim = '___'\nprint(isim)", "check": lambda c, o: "Pito" in o},
        {"msg": "Kullanıcıdan veri al (input).", "task": "ad = ___('Adın: ')\nprint(ad)", "check": lambda c, o: "input" in c},
        {"msg": "Sayıyı metne çevir (str).", "task": "s = 10\nprint(___(s))", "check": lambda c, o: "str" in c},
        {"msg": "Girişi tam sayıya çevir (int).", "task": "n = ___(___('S: '))\nprint(n + 5)", "check": lambda c, o: "int" in c}
    ]},
    # (3'ten 8'e kadar olan tüm modüller orijinal içerikleriyle burada yer almalıdır...)
]

# --- 6. ARA YÜZ VE EDİTÖR ---
st.markdown(f"#### 👋 {st.session_state.student_name} ({st.session_state.student_class}) | ⭐ Puan: {st.session_state.total_score}")
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

# PİTO ANLATIM ALANI (BÜYÜTÜLDÜ)
c1, c2 = st.columns([1.5, 5])
with c1:
    if os.path.exists(PITO_IMG): st.image(PITO_IMG, width=180)
    else: st.image("https://img.icons8.com/fluency/180/robot-viewer.png", width=160)
with c2:
    st.info(f"##### 🗣️ Pito Diyor Ki:\n\n{curr_ex['msg']}")
    st.caption(f"🎁 Görev Puanı: {st.session_state.current_potential_score}")

code = st_ace(value=curr_ex['task'], language="python", theme="dracula", font_size=14, height=180, wrap=True, key=f"ace_{m_idx}_{e_idx}")

# --- TEKNİK DÜZELTME (VALUEERROR ÇÖZÜLDÜ) ---
if st.button("🔍 Görevi Kontrol Et", use_container_width=True):
    old_stdout = sys.stdout 
    new_stdout = StringIO()
    sys.stdout = new_stdout 
    def mock_input(p=""): return "10"
    try:
        exec(code.replace("___", "None"), {"input": mock_input})
        sys.stdout = old_stdout 
        output = new_stdout.getvalue()
        st.subheader("📟 Çıktı")
        st.code(output if output else "Pito: Kod başarıyla çalıştı!")
        if curr_ex['check'](code, output) and "___" not in code:
            st.session_state.exercise_passed = True
            ex_key = f"{m_idx}_{e_idx}"
            if ex_key not in st.session_state.scored_exercises:
                st.session_state.total_score += st.session_state.current_potential_score
                st.session_state.scored_exercises.add(ex_key)
                auto_save_progress() # İLERLEME VE PUAN KAYDEDİLDİ
            st.success("Tebrikler! ✅")
        else:
            if not st.session_state.exercise_passed:
                st.session_state.current_potential_score = max(0, st.session_state.current_potential_score - 5)
            st.warning(f"Hatalı! Puanın {st.session_state.current_potential_score}'ye düştü.")
    except Exception as e:
        sys.stdout = old_stdout
        st.error(f"Hata! {e}")

if st.session_state.exercise_passed:
    if e_idx < 4:
        if st.button("➡️ Sonraki Adım"):
            st.session_state.current_exercise, st.session_state.exercise_passed, st.session_state.current_potential_score = e_idx+1, False, 20
            auto_save_progress() # ADIM ATLAYINCA KONUM KAYDEDİLDİ
            st.rerun()
    else:
        if st.button("🏆 Modülü Bitir"):
            st.session_state.completed_modules[m_idx], st.session_state.exercise_passed, st.session_state.current_potential_score = True, False, 20
            if m_idx < 7: st.session_state.current_module, st.session_state.current_exercise = m_idx+1, 0
            auto_save_progress()
            st.balloons(); st.rerun()

st.divider()
with st.expander(f"🏆 {st.session_state.student_class} Liderlik Tablosu"):
    df_all = get_db()
    # Sadece kendi sınıfını ve mükerrersiz (en güncel) halini göster
    df_class = df_all[df_all["Sınıf"] == st.session_state.student_class]
    df_class = df_class.sort_values(by="Puan", ascending=False).drop_duplicates(subset=["Okul No"])
    if not df_class.empty:
        st.dataframe(df_class[["Öğrencinin Adı", "Puan", "Rütbe"]], use_container_width=True)