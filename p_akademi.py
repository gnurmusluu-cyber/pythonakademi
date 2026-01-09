import streamlit as st
from streamlit_ace import st_ace
import sys
from io import StringIO
import pandas as pd
from datetime import datetime
from streamlit_gsheets import GSheetsConnection

# --- 1. SAYFA VE GÖRSEL AYARLAR ---
st.set_page_config(
    layout="wide", 
    page_title="Pito Akademi: Python Atölyesi",
    initial_sidebar_state="collapsed"
)

# Mobil ve Giriş Ekranı için Özel CSS
st.markdown("""
    <style>
    .stButton > button { width: 100%; border-radius: 8px; height: 3.5em; margin-bottom: 5px; font-weight: bold; }
    .ace_editor { border-radius: 10px; border: 1px solid #333; }
    /* Giriş ekranı kutusu */
    .login-box {
        padding: 2rem;
        border-radius: 15px;
        background-color: #1e1e1e;
        border: 1px solid #333;
        text-align: center;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. GOOGLE SHEETS BAĞLANTISI ---
# ÖNEMLİ: Kendi Google Sheets linkinizi buraya yapıştırın
SHEET_URL = "https://docs.google.com/spreadsheets/d/BURAYA_KENDI_LINKINIZI_EKLEYIN/edit#gid=0"

conn = st.connection("gsheets", type=GSheetsConnection)

def get_leaderboard():
    try:
        df = conn.read(spreadsheet=SHEET_URL, usecols=[0,1,2,3])
        df = df.dropna(subset=["Öğrenci Adı"])
        return df.sort_values(by="Puan", ascending=False).drop_duplicates(subset=["Öğrenci Adı"])
    except:
        return pd.DataFrame(columns=["Öğrenci Adı", "Puan", "Rütbe", "Tarih"])

def save_score(name, score, rank):
    try:
        df = get_leaderboard()
        new_row = pd.DataFrame([[name, score, rank, datetime.now().strftime("%d/%m/%Y %H:%M")]], 
                               columns=["Öğrenci Adı", "Puan", "Rütbe", "Tarih"])
        updated_df = pd.concat([df, new_row], ignore_index=True)
        conn.update(spreadsheet=SHEET_URL, data=updated_df)
        st.toast(f"Tebrikler {name}, skorun kaydedildi! ☁️", icon="✅")
    except Exception as e:
        st.error("Kayıt yapılamadı. Lütfen Sheets bağlantısını kontrol edin.")

# --- 3. SESSION STATE (DURUM TAKİBİ) ---
if 'student_name' not in st.session_state: st.session_state.student_name = ""
if 'completed_modules' not in st.session_state: st.session_state.completed_modules = [False] * 8
if 'current_module' not in st.session_state: st.session_state.current_module = 0
if 'current_exercise' not in st.session_state: st.session_state.current_exercise = 0
if 'exercise_passed' not in st.session_state: st.session_state.exercise_passed = False
if 'total_score' not in st.session_state: st.session_state.total_score = 0
if 'scored_exercises' not in st.session_state: st.session_state.scored_exercises = set()
if 'current_potential_score' not in st.session_state: st.session_state.current_potential_score = 20

# --- 4. GİRİŞ EKRANI (İSİM İSTEME) ---
if st.session_state.student_name == "":
    st.markdown("<br><br>", unsafe_allow_html=True)
    col_l, col_mid, col_r = st.columns([1, 2, 1])
    
    with col_mid:
        st.markdown("<div class='login-box'>", unsafe_allow_html=True)
        try: st.image("assets/pito.png", width=150)
        except: st.image("https://img.icons8.com/fluency/96/robot-viewer.png", width=100)
        
        st.title("Pito Akademi'ye Hoş Geldin!")
        st.write("Python yolculuğuna başlamadan önce seni tanımak isterim.")
        
        input_name = st.text_input("Adın Soyadın:", placeholder="Örn: Ahmet Yılmaz")
        
        if st.button("Atölyeye Gir 🚀"):
            if input_name.strip() != "":
                st.session_state.student_name = input_name.strip()
                st.rerun()
            else:
                st.warning("Lütfen bir isim giriniz.")
        st.markdown("</div>", unsafe_allow_html=True)
    st.stop() # İsim girilene kadar uygulamanın geri kalanını durdurur

# --- 5. ANA UYGULAMA İÇERİĞİ (Giriş Yapıldıktan Sonra) ---

def get_rank(score):
    if score < 200: return "🌱 Python Çırağı"
    if score < 500: return "💻 Kod Yazarı"
    if score < 850: return "🛠️ Yazılım Geliştirici"
    return "🏆 Python Ustası"

# Orijinal 8 Modül İçeriği
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
        {"msg": "Sayıyı metne çevir (str).", "task": "s = 10\nprint(___(s))", "check": lambda c, o: "str" in c},
        {"msg": "Girişi tam sayıya çevir (int).", "task": "sayi = ___(___('S: '))\nprint(sayi + 5)", "check": lambda c, o: "int" in c}
    ]},
    # (Daha önce paylaşılan 3-8 arası modüller burada aynen yer alır)
]

# Üst Bilgi Paneli
st.markdown(f"#### 👋 Hoş geldin, {st.session_state.student_name}!")
st.markdown(f"**{get_rank(st.session_state.total_score)}** | ⭐ Toplam Puan: {st.session_state.total_score}")
st.progress(min(st.session_state.total_score / 1000, 1.0))

# Modül Seçimi
mod_titles = [f"{'✅' if st.session_state.completed_modules[i] else '📖'} {m['module_title']}" for i, m in enumerate(training_data)]
selected_mod = st.selectbox("Gitmek istediğin Modül:", mod_titles, index=st.session_state.current_module)
new_mod_idx = mod_titles.index(selected_mod)

if new_mod_idx != st.session_state.current_module:
    st.session_state.current_module = new_mod_idx
    st.session_state.current_exercise = 0
    st.session_state.exercise_passed = False
    st.session_state.current_potential_score = 20
    st.rerun()

st.divider()

# Ana Egzersiz Alanı
m_idx, e_idx = st.session_state.current_module, st.session_state.current_exercise
curr_ex = training_data[m_idx]["exercises"][e_idx]

st.info(f"**Pito:** {curr_ex['msg']}")
st.caption(f"🎁 Görev Puanı: {st.session_state.current_potential_score} | Adım: {e_idx + 1}/5")

code = st_ace(value=curr_ex['task'], language="python", theme="dracula", font_size=14, height=180, wrap=True, key=f"ace_{m_idx}_{e_idx}")

if st.button("🔍 Görevi Kontrol Et", use_container_width=True):
    old_stdout = sys.stdout
    redirected_output = sys.stdout = StringIO()
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
                st.toast(f"+{st.session_state.current_potential_score} Puan!", icon="💰")
            st.success("Tebrikler! ✅")
        else:
            if not st.session_state.exercise_passed:
                st.session_state.current_potential_score = max(0, st.session_state.current_potential_score - 5)
            st.warning(f"Hatalı! Puanın {st.session_state.current_potential_score}'ye düştü.")
    except Exception as e:
        sys.stdout = old_stdout
        if not st.session_state.exercise_passed: st.session_state.current_potential_score = max(0, st.session_state.current_potential_score - 5)
        st.error(f"Kod hatası! Puan azaldı.")

if st.session_state.exercise_passed:
    if e_idx < 4:
        if st.button("➡️ Sonraki Adıma Geç", use_container_width=True):
            st.session_state.current_exercise, st.session_state.exercise_passed, st.session_state.current_potential_score = e_idx + 1, False, 20
            st.rerun()
    else:
        if st.button("🏆 Modülü Tamamla", use_container_width=True):
            st.session_state.completed_modules[m_idx], st.session_state.exercise_passed, st.session_state.current_potential_score = True, False, 20
            if m_idx < 7: st.session_state.current_module, st.session_state.current_exercise = m_idx + 1, 0
            st.balloons(); st.rerun()

# Liderlik Tablosu
st.divider()
with st.expander("🏆 Liderlik Tablosu & Skor Kaydı"):
    st.write(f"Mevcut Skorun: **{st.session_state.total_score}**")
    if st.button(f"Skorumu '{st.session_state.student_name}' Olarak Kaydet"):
        save_score(st.session_state.student_name, st.session_state.total_score, get_rank(st.session_state.total_score))
    
    st.subheader("En İyi 10 Öğrenci")
    st.dataframe(get_leaderboard().head(10), use_container_width=True)