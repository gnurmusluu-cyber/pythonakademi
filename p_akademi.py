import streamlit as st
import pandas as pd
import json
import time
from streamlit_gsheets import GSheetsConnection

# --- 1. SAYFA AYARLARI VE TASARIM ---
st.set_page_config(page_title="Pito Python Akademi", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #0E1117; color: #FFFFFF; }
    .hero-panel { background: linear-gradient(90deg, #1E1E2F 0%, #2D2D44 100%); padding: 20px; border-radius: 15px; border-left: 5px solid #00FF00; margin-bottom: 20px; }
    .stButton>button { border-radius: 10px; background-color: #00FF00; color: black; font-weight: bold; width: 100%; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. VERİTABANI VE MÜFREDAT BAĞLANTILARI ---
KULLANICILAR_URL = "https://docs.google.com/spreadsheets/d/1lat8rO2qm9QnzEUYlzC_fypG3cRkGlJfSfTtwNvs318/edit#gid=0"
KAYITLAR_URL = "https://docs.google.com/spreadsheets/d/14QoNr4FHZhSaUDUU-DDQEfNFHMo5Ge5t5lyDgqGRJ3k/edit#gid=0"

def load_data():
    conn = st.connection("gsheets", type=GSheetsConnection)
    kullanicilar = conn.read(spreadsheet=KULLANICILAR_URL, ttl=0)
    return conn, kullanicilar

def load_mufredat():
    with open('mufredat.json', 'r', encoding='utf-8') as f:
        return json.load(f)

# --- 3. SESSION STATE (SİSTEM HAFIZASI) ---
if "user_data" not in st.session_state: st.session_state.user_data = None
if "error_count" not in st.session_state: st.session_state.error_count = 0
if "pito_mod" not in st.session_state: st.session_state.pito_mod = "merhaba"

# --- 4. GİRİŞ VE KAYIT SİSTEMİ ---
conn, df_users = load_data()
mufredat = load_mufredat()

if st.session_state.user_data is None:
    st.title("🐍 Pito Python Akademi")
    st.image("assets/pito_merhaba.gif", width=200)
    
    numara = st.number_input("Öğrenci Numaranı Yaz:", step=1, value=0)
    
    if st.button("Giriş Yap"):
        user = df_users[df_users['ogrenci_no'] == numara]
        if not user.empty:
            st.session_state.user_data = user.iloc[0].to_dict()
            st.success(f"Hoş geldin {st.session_state.user_data['ad_soyad']}!")
            st.rerun()
        else:
            st.error("Seni tanıyamadım! Lütfen öğretmenine danış veya numaranı kontrol et.")
            if st.button("Yeni Kayıt Ol"): # Kayıt butonu [cite: 2026-01-12]
                st.info("Kayıt formu buraya gelecek.")

# --- 5. EĞİTİM PANELİ ---
else:
    u = st.session_state.user_data
    # Hero Header [cite: 2026-01-12]
    st.markdown(f"""<div class='hero-panel'>
        <h3>🚀 {u['ad_soyad']} | {u['rutbe']}</h3>
        <p>📊 Toplam Puan: {u['toplam_puan']} | Modül: {u['mevcut_modul']}</p>
        </div>""", unsafe_allow_html=True)

    col1, col2 = st.columns([1, 2])
    
    # Mevcut Egzersizi JSON'dan bul
    m_id = int(u['mevcut_modul'])
    egz_id = u['mevcut_egzersiz']
    # Örnek olarak ilk egzersiz çekiliyor:
    egzersiz = mufredat['pito_akademi_mufredat'][m_id-1]['egzersizler'][0] 

    with col1:
        st.image(f"assets/pito_{st.session_state.pito_mod}.gif")
        st.info(f"**GÖREV {egz_id}:** {egzersiz['yonerge']}")
        
        if st.session_state.error_count >= 3:
            st.warning(f"💡 İpucu: {egzersiz['ipucu']}")

    with col2:
        st.subheader("💻 Komut Paneli")
        kod = st.text_area("Kodunu buraya yaz:", value=egzersiz['sablon'], height=250)
        
        # Puanlama Mantığı [cite: 2026-01-12]
        puan = max(0, 20 - (st.session_state.error_count * 5))
        st.write(f"💰 Kazanılacak Puan: **{puan} XP**")
        
        # Kontrol Butonu [cite: 2026-01-12]
        if st.button("Kontrol Et"):
            if kod.strip() == egzersiz['dogru_cevap_kodu'].strip():
                st.session_state.pito_mod = "basari"
                st.balloons()
                # Veritabanı güncelleme işlemleri burada yapılacak
                st.success(f"Mükemmel! {puan} puan kazandın.")
                time.sleep(2)
                # İlerleme mantığı...
            else:
                st.session_state.error_count += 1
                st.session_state.pito_mod = "hata"
                if st.session_state.error_count >= 4:
                    st.session_state.pito_mod = "dusunuyor"
                    st.error("Panel Kilitlendi! Çözümü incele.")
                    st.code(egzersiz['cozum'])
                st.rerun()
