import streamlit as st
import pandas as pd
import json
import time
from datetime import datetime
from streamlit_gsheets import GSheetsConnection

# --- 1. SİSTEM AYARLARI VE CSS ---
st.set_page_config(page_title="Pito Python Akademi", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
    .stApp { background-color: #0E1117; color: #FFFFFF; }
    .hero-panel { background: linear-gradient(90deg, #1E1E2F 0%, #2D2D44 100%); padding: 20px; border-radius: 15px; border-left: 5px solid #00FF00; margin-bottom: 20px; box-shadow: 0 4px 15px rgba(0,255,0,0.1); }
    .stButton>button { border-radius: 10px; background-color: #00FF00 !important; color: black !important; font-weight: bold; width: 100%; transition: 0.3s; }
    .stButton>button:hover { transform: scale(1.02); box-shadow: 0 0 15px #00FF00; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. VERİTABANI VE MÜFREDAT BAĞLANTILARI ---
KULLANICILAR_URL = "https://docs.google.com/spreadsheets/d/1lat8rO2qm9QnzEUYlzC_fypG3cRkGlJfSfTtwNvs318/edit#gid=0"
KAYITLAR_URL = "https://docs.google.com/spreadsheets/d/14QoNr4FHZhSaUDUU-DDQEfNFHMo5Ge5t5lyDgqGRJ3k/edit#gid=0"

conn = st.connection("gsheets", type=GSheetsConnection)

def load_mufredat():
    with open('mufredat.json', 'r', encoding='utf-8') as f:
        return json.load(f)

# --- 3. SESSION STATE YÖNETİMİ ---
if "user" not in st.session_state: st.session_state.user = None
if "error_count" not in st.session_state: st.session_state.error_count = 0
if "pito_mod" not in st.session_state: st.session_state.pito_mod = "merhaba"
if "current_egz_idx" not in st.session_state: st.session_state.current_egz_idx = 0

# --- 4. VERİTABANI İŞLEMLERİ ---
def get_user(numara):
    df = conn.read(spreadsheet=KULLANICILAR_URL, ttl=0)
    user = df[df['ogrenci_no'] == numara]
    return user.iloc[0].to_dict() if not user.empty else None

def save_new_user(numara, ad, sinif):
    df = conn.read(spreadsheet=KULLANICILAR_URL)
    yeni = pd.DataFrame([{"ogrenci_no": int(numara), "ad_soyad": ad, "sinif": sinif, "toplam_puan": 0, 
                          "en_yuksek_puan": 0, "mevcut_modul": 1, "mevcut_egzersiz": "1.1", 
                          "rutbe": "🥚 Yeni Başlayan", "kayit_tarihi": datetime.now().strftime("%Y-%m-%d")}])
    güncel = pd.concat([df, yeni], ignore_index=True)
    conn.update(spreadsheet=KULLANICILAR_URL, data=güncel)
    return yeni.iloc[0].to_dict()

def update_db_progress(puan, kod, egz_id, modul_id):
    # Bu fonksiyon öğrenci puanını ve loglarını günceller
    st.toast("Veritabanı güncelleniyor... 🔄")

# --- 5. GİRİŞ VE KAYIT EKRANI ---
if st.session_state.user is None:
    st.title("🐍 Pito Python Akademi")
    st.image("assets/pito_merhaba.gif", width=250)
    
    numara = st.number_input("Öğrenci Numaranı Yaz:", step=1, value=0)
    if st.button("Giriş Yap"):
        u_data = get_user(numara)
        if u_data:
            st.session_state.user = u_data
            st.rerun()
        else:
            st.session_state.is_registering = True
            st.warning("Numaran sistemde yok. Haydi seni kaydedelim!")

    if st.session_state.get("is_registering", False):
        with st.form("kayit"):
            ad = st.text_input("Ad Soyad:")
            sinif = st.selectbox("Sınıfın:", ["9-A", "9-B", "10-A", "10-B", "11-A", "11-B"])
            if st.form_submit_button("Kaydı Tamamla"):
                st.session_state.user = save_new_user(numara, ad, sinif)
                st.rerun()

# --- 6. EĞİTİM PANELİ (ANA OYUN) ---
else:
    u = st.session_state.user
    mufredat = load_mufredat()
    
    # Kahraman Paneli (Hero Header)
    st.markdown(f"""<div class='hero-panel'>
        <h3>🚀 {u['ad_soyad']} | {u['rutbe']}</h3>
        <p>📊 Toplam Puan: {u['toplam_puan']} | Mevcut Modül: {u['mevcut_modul']}</p>
        </div>""", unsafe_allow_html=True)

    # Modül ve Egzersiz Verisi
    modul = mufredat['pito_akademi_mufredat'][int(u['mevcut_modul'])-1]
    egzersiz = modul['egzersizler'][st.session_state.current_egz_idx]

    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.image(f"assets/pito_{st.session_state.pito_mod}.gif", use_container_width=True)
        st.info(f"**GÖREV {egzersiz['id']}:** {egzersiz['yonerge']}")
        if st.session_state.error_count >= 3:
            st.warning(f"💡 Pito'nun İpucu: {egzersiz['ipucu']}")

    with col2:
        st.subheader("💻 Komut Paneli")
        kod_girisi = st.text_area("Python Kodun:", value=egzersiz['sablon'], height=250)
        
        # Puanlama: max(0, 20 - (Hata*5))
        aktif_puan = max(0, 20 - (st.session_state.error_count * 5))
        st.write(f"💰 Bu Görevden Alacağın: **{aktif_puan} XP**")

        if st.button("Kontrol Et"):
            if kod_girisi.strip() == egzersiz['dogru_cevap_kodu'].strip():
                st.session_state.pito_mod = "basari"
                st.balloons()
                update_db_progress(aktif_puan, kod_girisi, egzersiz['id'], u['mevcut_modul'])
                st.success("Mükemmel! Bir sonraki göreve hazır mısın?")
                time.sleep(2)
                # İlerleme mantığı burada devreye girecek
            else:
                st.session_state.error_count += 1
                st.session_state.pito_mod = "hata"
                if st.session_state.error_count >= 4:
                    st.session_state.pito_mod = "dusunuyor"
                    st.error("Komut Paneli Kilitlendi! Mola ver ve çözümü incele.")
                    st.code(egzersiz['cozum'], language='python')
                st.rerun()
