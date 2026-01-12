import streamlit as st
import pandas as pd
import time

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="Pito Python Akademi", layout="wide", page_icon="🤖")

# --- CSS: MODERN & LİSE SEVİYESİNE UYGUN ARAYÜZ ---
st.markdown("""
    <style>
    .stApp { background-color: #f0f2f6; }
    .sidebar-text { font-size: 14px; font-weight: bold; }
    .stButton>button { width: 100%; border-radius: 10px; height: 3em; }
    .pito-note { background-color: #e1f5fe; padding: 20px; border-radius: 15px; border-left: 5px solid #03a9f4; }
    .leaderboard-card { background-color: white; padding: 10px; border-radius: 10px; margin-bottom: 10px; box-shadow: 2px 2px 5px rgba(0,0,0,0.1); }
    </style>
    """, unsafe_allow_html=True)

# --- VERİ TABANI BAĞLANTISI (GOOGLE SHEETS) ---
# Not: .streamlit/secrets.toml dosyasında bağlantı bilgileri olmalı
def load_data():
    sheet_url = "https://docs.google.com/spreadsheets/d/1lat8rO2qm9QnzEUYlzC_fypG3cRkGlJfSfTtwNvs318/edit#gid=0"
    # Burası sizin gerçek GSheets bağlantınızla değiştirilecek
    try:
        # Örnek dummy veri (GSheets okunamadığı durumlar için)
        return pd.DataFrame([
            {"Okul No": 12, "Öğrencinin Adı": "Ali Veli", "Sınıf": "9-A", "Puan": 120, "Rütbe": "🌱 Python Çırağı", "Mevcut Modül": 1, "Mevcut Egzersiz": 3}
        ])
    except:
        st.error("Veri tabanına bağlanılamadı!")
        return None

# --- RÜTBE SİSTEMİ ---
RANKS = ["🥚 Yeni Başlayan", "🌱 Python Çırağı", "🪵 Kod Oduncusu", "🧱 Mantık Mimarı", 
         "🌀 Döngü Ustası", "📋 Liste Uzmanı", "📦 Fonksiyon Kaptanı", "🤖 OOP Robotu", "🏆 Python Kahramanı"]

# --- MÜFREDAT VERİSİ (8 MODÜL / 40 ADIM) ---
# Bilgisayar Bilimi Kur 1 PDF'inden referansla zenginleştirilecek
MÜFREDAT = {
    1: {
        "başlık": "Modül 1: Python'a Merhaba",
        "egzersizler": [
            {"id": 1, "task": "Ekrana 'Merhaba Dünya' yazdır.", "code": "print('______')", "answer": "Merhaba Dünya", "hint": "Tırnak içindeki metne dikkat et!", "solution": "print('Merhaba Dünya')"},
            # Diğer 4 egzersiz buraya...
        ]
    },
    # Diğer 7 modül buraya eklenecek...
}

# --- SESSION STATE (DURUM YÖNETİMİ) ---
if 'user' not in st.session_state: st.session_state.user = None
if 'step' not in st.session_state: st.session_state.step = "login"
if 'attempts' not in st.session_state: st.session_state.attempts = 0
if 'current_score' not in st.session_state: st.session_state.current_score = 20

# --- SİDEBAR: LİDERLİK TABLOLARI ---
def show_sidebar():
    with st.sidebar:
        st.title("🏆 Başarı Tablosu")
        st.subheader("🥇 Şampiyon Sınıf: 9-A")
        
        st.markdown("---")
        st.markdown("### 👑 Okul Liderleri (Top 10)")
        # GSheets verisinden çekilecek
        st.markdown('<div class="leaderboard-card">1. Ali Veli - 🧱 Mantık Mimarı</div>', unsafe_allow_html=True)
        
        st.markdown("---")
        if st.session_state.user:
            st.write(f"**Mevcut Rütben:** {st.session_state.user['Rütbe']}")
            if st.button("Çıkış Yap"):
                st.session_state.user = None
                st.session_state.step = "login"
                st.rerun()

# --- GİRİŞ EKRANI ---
def login_screen():
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.image("assets/pito_merhaba.gif", width=300)
        st.header("Pito Python Akademi'ye Hoş Geldin!")
        
        okul_no = st.text_input("Okul Numaranı Gir:", key="login_no")
        
        if okul_no:
            df = load_data()
            student = df[df["Okul No"] == int(okul_no)]
            
            if not student.empty:
                s_data = student.iloc[0]
                st.info(f"Merhaba **{s_data['Öğrencinin Adı']}**! {s_data['Mevcut Modül']}. Modül, {s_data['Mevcut Egzersiz']}. Egzersizde kalmışsın.")
                
                col_btn1, col_btn2 = st.columns(2)
                with col_btn1:
                    if st.button("Evet, Benim! Devam Et 🚀"):
                        st.session_state.user = s_data
                        st.session_state.step = "learning"
                        st.rerun()
                with col_btn2:
                    if st.button("Hayır, Ben Değilim ❌"):
                        st.rerun()
            else:
                st.warning("Numaran kayıtlı değil! Yeni profil oluşturalım.")
                with st.form("register_form"):
                    ad = st.text_input("Adın Soyadın:")
                    sinif = st.selectbox("Sınıfın:", ["9-A", "9-B", "10-A", "10-B"])
                    if st.form_submit_button("Kayıt Ol ve Başla"):
                        # GSheets'e yeni satır ekleme fonksiyonu buraya gelecek
                        st.success("Kayıt başarılı! 1. Modülden başlıyorsun.")
                        st.session_state.step = "learning"
                        st.rerun()

# --- EĞİTİM EKRANI ---
def learning_screen():
    u = st.session_state.user
    mod_id = u["Mevcut Modül"]
    ex_id = u["Mevcut Egzersiz"]
    
    # İlerleme Çubuğu
    progress = (mod_id - 1) * 12.5 + (ex_id * 2.5)
    st.progress(progress / 100)
    st.write(f"**İlerleme:** %{progress} | **Modül:** {mod_id} | **Egzersiz:** {ex_id}")

    col_main, col_pito = st.columns([3, 1])
    
    with col_pito:
        # Duygu durumuna göre GIF
        gif_path = "assets/pito_dusunuyor.gif"
        if st.session_state.attempts >= 1: gif_path = "assets/pito_hata.gif"
        st.image(gif_path, use_column_width=True)
    
    with col_main:
        st.markdown(f"""<div class="pito-note">
            <h3>🤖 Pito'nun Notu</h3>
            {MÜFREDAT[mod_id]['başlık']} içeriği ve detaylı konu anlatımı burada yer alacak. 
            Python'da değişkenler kutular gibidir...
        </div>""", unsafe_allow_html=True)
        
        st.divider()
        
        # Egzersiz Paneli
        current_ex = MÜFREDAT[mod_id]['egzersizler'][ex_id-1]
        st.subheader(f"📝 Görev {ex_id}")
        st.write(current_ex['task'])
        
        # Boşluk doldurma alanı
        user_input = st.text_input("Kodunuzu buraya yazın (boşluğu doldurun):", placeholder=current_ex['code'])
        
        if st.button("Kontrol Et ✅"):
            if user_input.strip() == current_ex['answer']:
                st.session_state.attempts = 0
                st.image("assets/pito_basari.gif", width=100)
                st.success(f"Tebrikler! +{st.session_state.current_score} Puan Kazandın!")
                # Print içeren egzersiz ise çıktı gösterimi
                if "print" in current_ex['code']:
                    st.code(f"Çıktı: {current_ex['answer']}", language="bash")
                
                # Bir sonraki egzersize geçiş
                if st.button("Sonraki Adım ➡️"):
                    # Veri tabanı güncelleme ve ilerleme mantığı
                    st.rerun()
            else:
                st.session_state.attempts += 1
                st.session_state.current_score -= 5
                
                if st.session_state.attempts < 3:
                    st.error(f"Hatalı cevap! {st.session_state.attempts}. hatan. Puanın düşüyor! Tekrar dene.")
                elif st.session_state.attempts == 3:
                    st.warning(f"💡 İpucu: {current_ex['hint']}")
                else:
                    st.error("4 kez hata yaptın. Bu sorudan puan alamadın.")
                    st.info(f"✅ Doğru Çözüm: {current_ex['solution']}")
                    if st.button("Sonraki Soruya Geç"):
                        st.rerun()

# --- ANA DÖNGÜ ---
show_sidebar()
if st.session_state.step == "login":
    login_screen()
else:
    learning_screen()
