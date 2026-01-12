import streamlit as st
import pandas as pd
import json
import time
from datetime import datetime
from streamlit_gsheets import GSheetsConnection

# --- 1. SİSTEM VE SİBER TASARIM AYARLARI ---
st.set_page_config(page_title="Pito Python Akademi", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
    .stApp { background-color: #0E1117; color: #FFFFFF; }
    .hero-panel { background: linear-gradient(90deg, #1E1E2F 0%, #2D2D44 100%); padding: 20px; border-radius: 15px; border-left: 5px solid #00FF00; margin-bottom: 20px; box-shadow: 0 4px 15px rgba(0,255,0,0.1); }
    .stButton>button { border-radius: 10px; background-color: #00FF00 !important; color: black !important; font-weight: bold; width: 100%; height: 3.5em; transition: 0.3s; }
    .stButton>button:hover { transform: scale(1.02); box-shadow: 0 0 15px #00FF00; }
    .stTextArea>div>div>textarea { background-color: #1E1E1E; color: #00FF00; font-family: 'Courier New', Courier, monospace; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. VERİTABANI VE MÜFREDAT BAĞLANTILARI ---
KULLANICILAR_URL = "https://docs.google.com/spreadsheets/d/1lat8rO2qm9QnzEUYlzC_fypG3cRkGlJfSfTtwNvs318/edit#gid=0"
KAYITLAR_URL = "https://docs.google.com/spreadsheets/d/14QoNr4FHZhSaUDUU-DDQEfNFHMo5Ge5t5lyDgqGRJ3k/edit#gid=0"

conn = st.connection("gsheets", type=GSheetsConnection)

@st.cache_data(ttl=60)
def load_mufredat():
    try:
        with open('mufredat.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return None

# --- 3. SESSION STATE (SİSTEM HAFIZASI) ---
if "user" not in st.session_state: st.session_state.user = None
if "error_count" not in st.session_state: st.session_state.error_count = 0
if "cevap_dogru" not in st.session_state: st.session_state.cevap_dogru = False
if "pito_mod" not in st.session_state: st.session_state.pito_mod = "merhaba"

# --- 4. VERİ MOTORU (ÇİFT TABLO SENKRONİZASYONU) ---
def ilerleme_kaydet(puan, kod, egz_id, m_id, n_id, n_m):
    try:
        # A. Kullanıcı Profilini Güncelle
        df_u = conn.read(spreadsheet=KULLANICILAR_URL, ttl=0)
        u_idx = df_u[df_u['ogrenci_no'] == st.session_state.user['ogrenci_no']].index[0]
        df_u.at[u_idx, 'toplam_puan'] = int(float(df_u.at[u_idx, 'toplam_puan'])) + puan
        df_u.at[u_idx, 'mevcut_egzersiz'] = str(n_id)
        df_u.at[u_idx, 'mevcut_modul'] = int(float(n_m))
        conn.update(spreadsheet=KULLANICILAR_URL, data=df_u)

        # B. Egzersiz Kayıtlarını Güncelle
        df_k = conn.read(spreadsheet=KAYITLAR_URL, ttl=0)
        yeni_log = pd.DataFrame([{
            "kayit_id": f"{st.session_state.user['ogrenci_no']}_{egz_id}",
            "ogrenci_no": int(st.session_state.user['ogrenci_no']),
            "modul_id": int(float(m_id)),
            "egzersiz_id": str(egz_id),
            "alinan_puan": int(puan),
            "basarili_kod": kod,
            "tarih": datetime.now().strftime("%Y-%m-%d %H:%M")
        }])
        conn.update(spreadsheet=KAYITLAR_URL, data=pd.concat([df_k, yeni_log], ignore_index=True))
        
        # Hafızayı Sıfırla
        st.session_state.user = df_u.iloc[u_idx].to_dict()
        st.session_state.error_count = 0
        st.session_state.cevap_dogru = False
        st.session_state.pito_mod = "merhaba"
        st.rerun()
    except Exception as e:
        st.error(f"Kayıt Hatası: {e}")

# --- 5. ANA AKIŞ ---
mufredat = load_mufredat()
if not mufredat: st.error("Müfredat yüklenemedi!"); st.stop()

# GİRİŞ EKRANI
if st.session_state.user is None:
    st.title("🐍 Pito Python Akademi")
    st.image("assets/pito_merhaba.gif", width=200)
    numara = st.number_input("Öğrenci Numaranız:", step=1, value=0)
    if st.button("Giriş Yap"):
        df_users = conn.read(spreadsheet=KULLANICILAR_URL, ttl=0)
        user = df_users[df_users['ogrenci_no'] == numara]
        if not user.empty:
            st.session_state.user = user.iloc[0].to_dict()
            st.rerun()
        else: st.warning("Numara bulunamadı!")

# EĞİTİM PANELİ
else:
    u = st.session_state.user
    m_idx = int(float(u['mevcut_modul'])) - 1
    modul = mufredat['pito_akademi_mufredat'][m_idx]
    egz = next((e for e in modul['egzersizler'] if e['id'] == str(u['mevcut_egzersiz'])), modul['egzersizler'][0])

    # Hero Header
    p_int = int(float(u['toplam_puan']))
    st.markdown(f"<div class='hero-panel'><h3>🚀 {u['ad_soyad']} | {u['rutbe']}</h3><p>XP: {p_int} | Modül: {m_idx+1}</p></div>", unsafe_allow_html=True)

    col1, col2 = st.columns([1, 2])
    with col1:
        # Hata Fix: Zaman damgası (timestamp) yerel dosyalar için kaldırıldı.
        st.image(f"assets/pito_{st.session_state.pito_mod}.gif")
        st.info(f"**GÖREV {egz['id']}:** {egz['yonerge']}")
        
        # Kademeli Dönütler
        if st.session_state.error_count == 1:
            st.error("🤫 Pito: 'Ufak bir hata oldu galiba? Bir daha dene!'")
        elif st.session_state.error_count == 2:
            st.error("🧐 Pito: 'Hadi dostum, pes etmek yok! Kodunu kontrol et.'")
        elif st.session_state.error_count == 3:
            st.warning(f"💡 Pito'nun İpucu: {egz['ipucu']}")

    with col2:
        puan_pot = max(0, 20 - (st.session_state.error_count * 5))
        st.write(f"🎯 Kazanılacak Puan: **{puan_pot} XP**")

        # DURUM 1: DENEME ANI
        if not st.session_state.cevap_dogru and st.session_state.error_count < 4:
            kod_input = st.text_area("Kodunu Yaz:", value=egz['sablon'], height=200, key="editor")
            if st.button("Kontrol Et"):
                if kod_input.strip() == egz['dogru_cevap_kodu'].strip():
                    st.session_state.cevap_dogru, st.session_state.pito_mod = True, "tebrik"
                    st.rerun()
                else:
                    st.session_state.error_count += 1
                    st.session_state.pito_mod = "hata" if st.session_state.error_count < 4 else "dusunuyor"
                    st.rerun()

        # DURUM 2: BAŞARI
        elif st.session_state.cevap_dogru:
            st.success(f"🌟 Harika! {puan_pot} XP Kazandın.")
            curr_idx = modul['egzersizler'].index(egz)
            n_id, n_m = (modul['egzersizler'][curr_idx+1]['id'], u['mevcut_modul']) if curr_idx+1 < len(modul['egzersizler']) else (f"{m_idx + 2}.1", m_idx + 2)
            if st.button("Sonraki Göreve Geç ➡️"):
                ilerleme_kaydet(puan_pot, kod_input, egz['id'], u['mevcut_modul'], n_id, n_m)

        # DURUM 3: KİLİT (4 HATA)
        elif st.session_state.error_count >= 4:
            st.error("🚫 Üzgünüm, 4 hata sınırı doldu. Çözümü incele.")
            with st.expander("📖 Pito'nun Çözümü", expanded=True): st.code(egz['cozum'])
            curr_idx = modul['egzersizler'].index(egz)
            n_id, n_m = (modul['egzersizler'][curr_idx+1]['id'], u['mevcut_modul']) if curr_idx+1 < len(modul['egzersizler']) else (f"{m_idx + 2}.1", m_idx + 2)
            if st.button("Anladım, Sıradaki Göreve Geç ➡️"):
                ilerleme_kaydet(0, "Çözüm İncelendi", egz['id'], u['mevcut_modul'], n_id, n_m)
