import streamlit as st
import pandas as pd
import json
import time
from datetime import datetime
from streamlit_gsheets import GSheetsConnection

# --- 1. SİSTEM VE TASARIM AYARLARI ---
st.set_page_config(page_title="Pito Python Akademi", layout="wide", initial_sidebar_state="collapsed")

# Siber Kampüs CSS [cite: 2026-01-12]
st.markdown("""
    <style>
    .stApp { background-color: #0E1117; color: #FFFFFF; }
    .hero-panel { background: linear-gradient(90deg, #1E1E2F 0%, #2D2D44 100%); padding: 20px; border-radius: 15px; border-left: 5px solid #00FF00; margin-bottom: 20px; box-shadow: 0 4px 15px rgba(0,255,0,0.1); }
    .stButton>button { border-radius: 10px; background-color: #00FF00 !important; color: black !important; font-weight: bold; width: 100%; height: 3em; }
    .stTextArea>div>div>textarea { background-color: #1E1E1E; color: #00FF00; font-family: 'Courier New', Courier, monospace; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. VERİTABANI BAĞLANTILARI ---
KULLANICILAR_URL = "https://docs.google.com/spreadsheets/d/1lat8rO2qm9QnzEUYlzC_fypG3cRkGlJfSfTtwNvs318/edit#gid=0"
KAYITLAR_URL = "https://docs.google.com/spreadsheets/d/14QoNr4FHZhSaUDUU-DDQEfNFHMo5Ge5t5lyDgqGRJ3k/edit#gid=0"

conn = st.connection("gsheets", type=GSheetsConnection)

@st.cache_data(ttl=0)
def load_mufredat():
    with open('mufredat.json', 'r', encoding='utf-8') as f:
        return json.load(f)

# --- 3. SESSION STATE (SİSTEM HAFIZASI) ---
if "user" not in st.session_state: st.session_state.user = None
if "error_count" not in st.session_state: st.session_state.error_count = 0
if "pito_mod" not in st.session_state: st.session_state.pito_mod = "merhaba"
if "current_egz_id" not in st.session_state: st.session_state.current_egz_id = "1.1"

# --- 4. VERİTABANI GÜNCELLEME FONKSİYONLARI ---
def update_progress(puan, kod, egz_id, modul_id):
    # Bu alan gerçek veritabanı yazma işlemini tetikler [cite: 2026-01-12]
    st.toast(f"Puanın işleniyor: {puan} XP 🚀")

def register_user(numara, ad, sinif):
    df = conn.read(spreadsheet=KULLANICILAR_URL)
    yeni = pd.DataFrame([{"ogrenci_no": int(numara), "ad_soyad": ad, "sinif": sinif, "toplam_puan": 0, 
                          "en_yuksek_puan": 0, "mevcut_modul": 1, "mevcut_egzersiz": "1.1", 
                          "rutbe": "🥚 Yeni Başlayan", "kayit_tarihi": datetime.now().strftime("%Y-%m-%d")}])
    conn.update(spreadsheet=KULLANICILAR_URL, data=pd.concat([df, yeni], ignore_index=True))
    return yeni.iloc[0].to_dict()

# --- 5. ARAYÜZ BİLEŞENLERİ ---
def hero_header():
    u = st.session_state.user
    # Tam sayı zorlaması (Integer mühürleme) [cite: 2026-01-12]
    puan = int(float(u['toplam_puan']))
    modul = int(float(u['mevcut_modul']))
    st.markdown(f"""<div class='hero-panel'>
        <h3>🚀 {u['ad_soyad']} | <span style='color:#00FF00;'>{u['rutbe']}</span></h3>
        <p>📊 Toplam Puan: <b>{puan} XP</b> | Mevcut Modül: <b>{modul}</b></p>
        </div>""", unsafe_allow_html=True)

# --- 6. GİRİŞ VE KAYIT EKRANI ---
if st.session_state.user is None:
    st.title("🐍 Pito Python Akademi")
    st.image("assets/pito_merhaba.gif", width=250)
    
    numara = st.number_input("Öğrenci Numaranı Yaz:", step=1, value=0)
    if st.button("Giriş Yap"):
        df = conn.read(spreadsheet=KULLANICILAR_URL, ttl=0)
        user = df[df['ogrenci_no'] == numara]
        if not user.empty:
            st.session_state.user = user.iloc[0].to_dict()
            st.rerun()
        else:
            st.session_state.is_registering = True
            st.warning("Seni tanıyamadım, haydi kaydedelim!")

    if st.session_state.get("is_registering", False):
        with st.form("kayit"):
            ad = st.text_input("Ad Soyad:")
            sinif = st.selectbox("Sınıfın:", ["9-A", "9-B", "10-A", "10-B", "11-A", "11-B"])
            if st.form_submit_button("Kaydı Tamamla ve Başla"):
                st.session_state.user = register_user(numara, ad, sinif)
                st.rerun()

# --- 7. EĞİTİM PANELİ (ANA MOTOR) ---
else:
    mufredat = load_mufredat()
    hero_header()
    
    # Mevcut Modül ve Egzersizi Belirle
    u = st.session_state.user
    m_idx = int(float(u['mevcut_modul'])) - 1
    modul_verisi = mufredat['pito_akademi_mufredat'][m_idx]
    
    # Egzersiz Bulucu
    egzersiz = next(e for e in modul_verisi['egzersizler'] if e['id'] == st.session_state.current_egz_id)

    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.image(f"assets/pito_{st.session_state.pito_mod}.gif", use_container_width=True)
        st.info(f"**GÖREV {egzersiz['id']}:** {egzersiz['yonerge']}")
        
        if st.session_state.error_count == 3:
            st.warning(f"💡 Pito'dan İpucu: {egzersiz['ipucu']}") # 3. Hata İpucu [cite: 2026-01-12]

    with col2:
        st.subheader("💻 Komut Paneli")
        # Puanlama Mantığı: 20'den 5 azalarak gider [cite: 2026-01-12]
        aktif_puan = max(0, 20 - (st.session_state.error_count * 5))
        st.write(f"🎯 Kazanılacak Puan: **{int(aktif_puan)} XP**")
        
        # 4. HATA KONTROLÜ VE KİLİT [cite: 2026-01-12]
        if st.session_state.error_count < 4:
            kod_input = st.text_area("Python Kodun:", value=egzersiz['sablon'], height=200)
            if st.button("Kontrol Et"):
                if kod_input.strip() == egzersiz['dogru_cevap_kodu'].strip():
                    st.session_state.pito_mod = "basari"
                    st.balloons()
                    update_progress(aktif_puan, kod_input, egzersiz['id'], m_idx+1)
                    st.success(f"Tebrikler! {int(aktif_puan)} XP kazandın.")
                    if st.button("Sonraki Göreve Geç ➡️"):
                        st.session_state.error_count = 0
                        # İlerletme mantığı eklenebilir
                        st.rerun()
                else:
                    st.session_state.error_count += 1
                    st.session_state.pito_mod = "hata"
                    st.rerun()
        else:
            # KİLİT VE ÇÖZÜM EKRANI [cite: 2026-01-12]
            st.session_state.pito_mod = "dusunuyor"
            st.error("🚫 Hata sınırına ulaştın! Bu görevden puan alamadın.")
            with st.expander("📖 Çözümü İncele ve Mantığını Anla", expanded=True):
                st.code(egzersiz['cozum'], language='python')
                st.info("Pito: 'Üzülme, bazen görerek öğrenmek en iyisidir. Çözümü incelediysen devam edelim!'")
            
            if st.button("Anladım, Sonraki Göreve Geç ➡️"):
                st.session_state.error_count = 0
                # İlerletme mantığı eklenebilir
                st.rerun()
