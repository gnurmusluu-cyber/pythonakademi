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
    .login-box { padding: 2rem; border-radius: 15px; background-color: #1e1e1e; border: 1px solid #333; text-align: center; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. GOOGLE SHEETS BAĞLANTISI ---
# ÖNEMLİ: Kendi Google Sheets linkinizi buraya yapıştırın
SHEET_URL = "https://docs.google.com/spreadsheets/d/BURAYA_KENDI_LINKINIZI_EKLEYIN/edit#gid=0"

conn = st.connection("gsheets", type=GSheetsConnection)

def get_leaderboard():
    try:
        # Veriyi oku ve temizle
        df = conn.read(spreadsheet=SHEET_URL, usecols=[0,1,2,3], ttl=0) # ttl=0 anlık veri çekmeyi sağlar
        df = df.dropna(subset=["Öğrenci Adı"])
        return df.sort_values(by="Puan", ascending=False).drop_duplicates(subset=["Öğrenci Adı"])
    except:
        return pd.DataFrame(columns=["Öğrenci Adı", "Puan", "Rütbe", "Tarih"])

def auto_save_score():
    """Skoru otomatik olarak Google Sheets'e kaydeder."""
    try:
        name = st.session_state.student_name
        score = st.session_state.total_score
        # Mevcut rütbeyi hesapla
        if score < 200: rank = "🌱 Python Çırağı"
        elif score < 500: rank = "💻 Kod Yazarı"
        elif score < 850: rank = "🛠️ Yazılım Geliştirici"
        else: rank = "🏆 Python Ustası"
        
        # Güncel tabloyu al ve yeni skoru ekle/güncelle
        df = get_leaderboard()
        new_row = pd.DataFrame([[name, score, rank, datetime.now().strftime("%H:%M:%S")]], 
                               columns=["Öğrenci Adı", "Puan", "Rütbe", "Tarih"])
        
        updated_df = pd.concat([df, new_row], ignore_index=True)
        conn.update(spreadsheet=SHEET_URL, data=updated_df)
    except:
        pass # Arka planda hata olsa bile öğrencinin ekranı donmasın

# --- 3. SESSION STATE ---
if 'student_name' not in st.session_state: st.session_state.student_name = ""
if 'completed_modules' not in st.session_state: st.session_state.completed_modules = [False] * 8
if 'current_module' not in st.session_state: st.session_state.current_module = 0
if 'current_exercise' not in st.session_state: st.session_state.current_exercise = 0
if 'exercise_passed' not in st.session_state: st.session_state.exercise_passed = False
if 'total_score' not in st.session_state: st.session_state.total_score = 0
if 'scored_exercises' not in st.session_state: st.session_state.scored_exercises = set()
if 'current_potential_score' not in st.session_state: st.session_state.current_potential_score = 20

# --- 4. GİRİŞ EKRANI ---
if st.session_state.student_name == "":
    st.markdown("<br><br>", unsafe_allow_html=True)
    col_l, col_mid, col_r = st.columns([1, 2, 1])
    with col_mid:
        st.markdown("<div class='login-box'>", unsafe_allow_html=True)
        try: st.image("assets/pito.png", width=150)
        except: st.image("https://img.icons8.com/fluency/96/robot-viewer.png", width=100)
        st.title("Pito Akademi")
        st.write("Python yolculuğuna isminle başla!")
        input_name = st.text_input("Adın Soyadın:", placeholder="Örn: Ahmet Yılmaz")
        if st.button("Eğitimi Başlat 🚀"):
            if input_name.strip() != "":
                st.session_state.student_name = input_name.strip()
                st.rerun()
            else: st.warning("İsim girmelisin!")
        st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

# --- 5. ANA UYGULAMA ---
def get_rank(score):
    if score < 200: return "🌱 Python Çırağı"
    if score < 500: return "💻 Kod Yazarı"
    if score < 850: return "🛠️ Yazılım Geliştirici"
    return "🏆 Python Ustası"

# Orijinal Modül Verileri (Kısaltılmıştır, mevcut 8 modülünüzü buraya ekleyin)
training_data = [
    {"module_title": "1. Giriş ve Çıktı", "exercises": [
        {"msg": "Ekrana 'Pito' yazdır.", "task": "print('___')", "check": lambda c, o: "Pito" in o},
        {"msg": "100 sayısını yazdır.", "task": "print(___)", "check": lambda c, o: "100" in o},
        {"msg": "Puan: 100 yazdır.", "task": "print('Puan:', ___)", "check": lambda c, o: "100" in o},
        {"msg": "Yorum ekle.", "task": "___ Test", "check": lambda c, o: "#" in c},
        {"msg": "Alt satır (\\n).", "task": "print('A' + '\\n' + 'B')", "check": lambda c, o: "\n" in o}
    ]}
    # ... (Diğer 7 modül)
]

# Üst Bilgi
st.markdown(f"#### 👋 {st.session_state.student_name} | **{get_rank(st.session_state.total_score)}** | ⭐ Puan: {st.session_state.total_score}")
st.progress(min(st.session_state.total_score / 1000, 1.0))

# Modül Navigasyonu
mod_titles = [f"{'✅' if st.session_state.completed_modules[i] else '📖'} {m['module_title']}" for i, m in enumerate(training_data)]
sel_mod = st.selectbox("Modül Değiştir:", mod_titles, index=st.session_state.current_module)
new_idx = mod_titles.index(sel_mod)
if new_idx != st.session_state.current_module:
    st.session_state.current_module, st.session_state.current_exercise, st.session_state.exercise_passed, st.session_state.current_potential_score = new_idx, 0, False, 20
    st.rerun()

st.divider()

# Egzersiz Alanı
m_idx, e_idx = st.session_state.current_module, st.session_state.current_exercise
curr_ex = training_data[m_idx]["exercises"][e_idx]

st.info(f"**Pito:** {curr_ex['msg']}")
st.caption(f"🎁 Potansiyel Puan: {st.session_state.current_potential_score}")

code = st_ace(value=curr_ex['task'], language="python", theme="dracula", font_size=14, height=180, wrap=True, key=f"ace_{m_idx}_{e_idx}")

if st.button("🔍 Görevi Kontrol Et", use_container_width=True):
    old_stdout, redirected_output = sys.stdout, sys.stdout = StringIO()
    def mock_input(p=""): return "10"
    try:
        exec(code.replace("___", "None"), {"input": mock_input})
        sys.stdout, output = old_stdout, redirected_output.getvalue()
        
        if curr_ex['check'](code, output) and "___" not in code:
            st.session_state.exercise_passed = True
            ex_key = f"{m_idx}_{e_idx}"
            if ex_key not in st.session_state.scored_exercises:
                st.session_state.total_score += st.session_state.current_potential_score
                st.session_state.scored_exercises.add(ex_key)
                # --- KRİTİK NOKTA: OTOMATİK KAYIT ---
                auto_save_score() 
                st.toast(f"Puanın otomatik kaydedildi! (+{st.session_state.current_potential_score})", icon="☁️")
            st.success("Tebrikler! Doğru cevap. ✅")
        else:
            if not st.session_state.exercise_passed:
                st.session_state.current_potential_score = max(0, st.session_state.current_potential_score - 5)
            st.warning(f"Hatalı! Puanın {st.session_state.current_potential_score}'ye düştü.")
    except:
        sys.stdout = old_stdout
        st.error("Kodda hata var, puanın azaldı.")

if st.session_state.exercise_passed:
    if e_idx < 4:
        if st.button("➡️ Sonraki Adıma Geç", use_container_width=True):
            st.session_state.current_exercise, st.session_state.exercise_passed, st.session_state.current_potential_score = e_idx + 1, False, 20
            st.rerun()
    else:
        if st.button("🏆 Modülü Bitir", use_container_width=True):
            st.session_state.completed_modules[m_idx], st.session_state.exercise_passed, st.session_state.current_potential_score = True, False, 20
            if m_idx < 7: st.session_state.current_module, st.session_state.current_exercise = m_idx + 1, 0
            st.balloons(); st.rerun()

# Liderlik Tablosu
st.divider()
with st.expander("🏆 Liderlik Tablosu (Canlı)"):
    st.subheader("En İyi 10 Öğrenci")
    st.dataframe(get_leaderboard().head(10), use_container_width=True)