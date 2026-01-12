import streamlit as st
import pandas as pd
import json
import time
import os
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

# --- 2. GÜVENLİ GÖRSEL YÜKLEME ---
def pito_gorseli_yukle(mod):
    base_path = os.path.dirname(os.path.abspath(__file__))
    img_path = os.path.join(base_path, "assets", f"pito_{mod}.gif")
    if os.path.exists(img_path):
        st.image(image_path if 'image_path' in locals() else img_path, use_container_width=True)
    else:
        st.error(f"🖼️ Görsel Eksik: assets/pito_{mod}.gif")

# --- 3. VERİTABANI VE MÜFREDAT BAĞLANTILARI ---
KULLANICILAR_URL = "https://docs.google.com/spreadsheets/d/1lat8rO2qm9QnzEUYlzC_fypG3cRkGlJfSfTtwNvs318/edit#gid=0"
KAYITLAR_URL = "https://docs.google.com/spreadsheets/d/14QoNr4FHZhSaUDUU-DDQEfNFHMo5Ge5t5lyDgqGRJ3k/edit#gid=0"

conn = st.connection("gsheets", type=GSheetsConnection)

@st.cache_data(ttl=60)
def load_mufredat():
    try:
        with open('mufredat.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except: return None

# --- 4. SESSION STATE (HAFIZA SİSTEMİ) ---
if "user" not in st.session_state: st.session_state.user = None
if "error_count" not in st.session_state: st.session_state.error_count = 0
if "cevap_dogru" not in st.session_state: st.session_state.cevap_dogru = False
if "pito_mod" not in st.session_state: st.session_state.pito_mod = "merhaba"
if "last_code" not in st.session_state: st.session_state.last_code = ""

# --- 5. VERİ YAZMA MOTORU ---
def ilerleme_kaydet(puan, kod, egz_id, m_id, n_id, n_m):
    try:
        df_u = conn.read(spreadsheet=KULLANICILAR_URL, ttl=0)
        u_idx = df_u[df_u['ogrenci_no'] == st.session_state.user['ogrenci_no']].index[0]
        df_u.at[u_idx, 'toplam_puan'] = int(float(df_u.at[u_idx, 'toplam_puan'])) + puan
        df_u.at[u_idx, 'mevcut_egzersiz'] = str(n_id)
        df_u.at[u_idx, 'mevcut_modul'] = int(float(n_m))
        conn.update(spreadsheet=KULLANICILAR_URL, data=df_u)

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
        
        st.session_state.user = df_u.iloc[u_idx].to_dict()
        st.session_state.error_count, st.session_state.cevap_dogru, st.session_state.pito_mod = 0, False, "merhaba"
        st.session_state.last_code = ""
        st.rerun()
    except Exception as e: st.error(f"Kayıt Hatası: {e}")

# --- 6. ANA AKIŞ ---
mufredat = load_mufredat()
if not mufredat: st.error("Müfredat JSON Bulunamadı!"); st.stop()

if st.session_state.user is None:
    st.title("🐍 Pito Python Akademi")
    pito_gorseli_yukle("merhaba")
    numara = st.number_input("Öğrenci Numarası:", step=1, value=0)
    
    if numara > 0:
        df_u = conn.read(spreadsheet=KULLANICILAR_URL, ttl=0)
        user_data = df_u[df_u['ogrenci_no'] == numara]

        if not user_data.empty:
            if st.button("Akademiye Giriş Yap 🚀"):
                st.session_state.user = user_data.iloc[0].to_dict()
                st.rerun()
        else:
            st.warning("🧐 Pito: 'Seni listemde bulamadım. Yeni bir kayıt oluşturalım!'")
            c1, c2 = st.columns(2)
            with c1: yeni_ad = st.text_input("Adın ve Soyadın:")
            with c2: yeni_sinif = st.selectbox("Sınıfın:", ["9-A", "9-B", "9-C", "10-A", "10-B", "11-A", "12-A"])
            
            if st.button("Kayıt Ol ve Başla 🎓"):
                if yeni_ad.strip() != "":
                    yeni_ogrenci = pd.DataFrame([{
                        "ogrenci_no": int(numara), "ad_soyad": yeni_ad, "sinif": yeni_sinif,
                        "toplam_puan": 0, "mevcut_modul": 1, "mevcut_egzersiz": "1.1", "rutbe": "🥚"
                    }])
                    df_guncel = pd.concat([df_u, yeni_ogrenci], ignore_index=True)
                    conn.update(spreadsheet=KULLANICILAR_URL, data=df_guncel)
                    st.session_state.user = yeni_ogrenci.iloc[0].to_dict()
                    st.rerun()
                else: st.error("Lütfen ad soyad girin!")
else:
    u = st.session_state.user
    m_idx = int(float(u['mevcut_modul'])) - 1
    if m_idx >= len(mufredat['pito_akademi_mufredat']):
        st.balloons(); pito_gorseli_yukle("mezun"); st.success("🏆 MEZUN OLDUN!"); st.stop()

    modul = mufredat['pito_akademi_mufredat'][m_idx]
    egz = next((e for e in modul['egzersizler'] if e['id'] == str(u['mevcut_egzersiz'])), modul['egzersizler'][0])

    st.markdown(f"<div class='hero-panel'><h3>🚀 {u['ad_soyad']} | {u['sinif']}</h3><p>🏆 Rütbe: {u['rutbe']} | 📊 XP: {int(float(u['toplam_puan']))}</p></div>", unsafe_allow_html=True)
    col1, col2 = st.columns([1, 2])

    with col1:
        pito_gorseli_yukle(st.session_state.pito_mod)
        st.info(f"**GÖREV {egz['id']}:** {egz['yonerge']}")
        if st.session_state.error_count == 1: st.error("🤫 Pito: 'Ufak bir hata! Yazımı kontrol et.'")
        elif st.session_state.error_count == 2: st.error("🧐 Pito: 'Dikkatli bak, küçük bir eksik var!'")
        elif st.session_state.error_count == 3: st.warning(f"💡 İpucu: {egz['ipucu']}")

    with col2:
        puan_pot = max(0, 20 - (st.session_state.error_count * 5))
        st.write(f"🎯 Potansiyel Puan: **{puan_pot} XP**")

        if not st.session_state.cevap_dogru and st.session_state.error_count < 4:
            kod_input = st.text_area("Kodunu Yaz:", value=egz['sablon'], height=200, key="editor")
            if st.button("Kontrol Et"):
                st.session_state.last_code = kod_input
                if kod_input.strip() == egz['dogru_cevap_kodu'].strip():
                    st.session_state.cevap_dogru, st.session_state.pito_mod = True, "basari"
                    st.rerun()
                else:
                    st.session_state.error_count += 1
                    st.session_state.pito_mod = "hata" if st.session_state.error_count < 4 else "dusunuyor"
                    st.rerun()

        elif st.session_state.cevap_dogru:
            st.success("🌟 Harika! Pito seninle gurur duyuyor.")
            idx = modul['egzersizler'].index(egz)
            n_id, n_m = (modul['egzersizler'][idx+1]['id'], u['mevcut_modul']) if idx+1 < len(modul['egzersizler']) else (f"{m_idx + 2}.1", m_idx + 2)
            if st.button("Sonraki Göreve Geç ➡️"):
                ilerleme_kaydet(puan_pot, st.session_state.last_code, egz['id'], u['mevcut_modul'], n_id, n_m)

        elif st.session_state.error_count >= 4:
            st.error("🚫 Kilitlendi. Çözümü incele.")
            with st.expander("📖 Çözüm"):
                st.code(egz['cozum'])
            idx = modul['egzersizler'].index(egz)
            n_id, n_m = (modul['egzersizler'][idx+1]['id'], u['mevcut_modul']) if idx+1 < len(modul['egzersizler']) else (f"{m_idx + 2}.1", m_idx + 2)
            if st.button("Sıradaki Göreve Geç ➡️"):
                ilerleme_kaydet(0, "Çözüm İncelendi", egz['id'], u['mevcut_modul'], n_id, n_m)
