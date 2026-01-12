import streamlit as st
import pandas as pd
import json
import time
from datetime import datetime
from streamlit_gsheets import GSheetsConnection

# --- 1. AYARLAR VE TASARIM ---
st.set_page_config(page_title="Pito Python Akademi", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #0E1117; color: #FFFFFF; }
    .hero-panel { background: linear-gradient(90deg, #1E1E2F 0%, #2D2D44 100%); padding: 20px; border-radius: 15px; border-left: 5px solid #00FF00; margin-bottom: 20px; }
    .stButton>button { border-radius: 10px; background-color: #00FF00 !important; color: black !important; font-weight: bold; width: 100%; height: 3.5em; }
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
    except Exception as e:
        st.error(f"❌ mufredat.json bulunamadı: {e}")
        return None

# --- 3. SESSION STATE ---
if "user" not in st.session_state: st.session_state.user = None
if "error_count" not in st.session_state: st.session_state.error_count = 0
if "cevap_dogru" not in st.session_state: st.session_state.cevap_dogru = False
if "pito_mod" not in st.session_state: st.session_state.pito_mod = "merhaba"

# --- 4. VERİTABANI İŞLEMLERİ (ÇİFT TABLO GÜNCELLEME) ---
def ilerleme_kaydet(kazanilan_puan, kod, egz_id, modul_id, n_id, n_m):
    try:
        # A. KULLANICILAR TABLOSUNU GÜNCELLE
        df_u = conn.read(spreadsheet=KULLANICILAR_URL, ttl=0)
        idx = df_u[df_u['ogrenci_no'] == st.session_state.user['ogrenci_no']].index[0]
        
        df_u.at[idx, 'toplam_puan'] = int(float(df_u.at[idx, 'toplam_puan'])) + kazanilan_puan
        df_u.at[idx, 'mevcut_egzersiz'] = str(n_id)
        df_u.at[idx, 'mevcut_modul'] = int(float(n_m))
        conn.update(spreadsheet=KULLANICILAR_URL, data=df_u)

        # B. EGZERSİZ KAYITLARI TABLOSUNA EKLE
        df_k = conn.read(spreadsheet=KAYITLAR_URL, ttl=0)
        yeni_log = pd.DataFrame([{
            "kayit_id": f"{st.session_state.user['ogrenci_no']}_{egz_id}",
            "ogrenci_no": int(st.session_state.user['ogrenci_no']),
            "modul_id": int(float(modul_id)),
            "egzersiz_id": str(egz_id),
            "alinan_puan": int(kazanilan_puan),
            "basarili_kod": kod,
            "tarih": datetime.now().strftime("%Y-%m-%d %H:%M")
        }])
        df_yeni_k = pd.concat([df_k, yeni_log], ignore_index=True)
        conn.update(spreadsheet=KAYITLAR_URL, data=df_yeni_k)
        
        # Hafızayı Sıfırla ve Yenile
        st.session_state.user = df_u.iloc[idx].to_dict()
        st.session_state.error_count = 0
        st.session_state.cevap_dogru = False
        st.session_state.pito_mod = "merhaba"
        st.rerun()
    except Exception as e:
        st.error(f"📝 Veri yazma hatası: {e}")

# --- 5. ANA AKIŞ ---
mufredat = load_mufredat()
if not mufredat: st.stop()

if st.session_state.user is None:
    st.title("🐍 Pito Python Akademi")
    st.image("assets/pito_merhaba.gif", width=250)
    numara = st.number_input("Öğrenci Numarası:", step=1, value=0)
    if st.button("Giriş Yap"):
        df_users = conn.read(spreadsheet=KULLANICILAR_URL, ttl=0)
        user_row = df_users[df_users['ogrenci_no'] == numara]
        if not user_row.empty:
            st.session_state.user = user_row.iloc[0].to_dict()
            st.rerun()
        else:
            st.warning("Numara bulunamadı!")
else:
    # Egzersiz Verisini Çek
    u = st.session_state.user
    m_idx = int(float(u['mevcut_modul'])) - 1
    modul = mufredat['pito_akademi_mufredat'][m_idx]
    egz = next((e for e in modul['egzersizler'] if e['id'] == str(u['mevcut_egzersiz'])), modul['egzersizler'][0])

    # Header
    st.markdown(f"<div class='hero-panel'><h3>🚀 {u['ad_soyad']} | {u['rutbe']}</h3><p>📊 XP: {int(float(u['toplam_puan']))} | Modül: {m_idx+1}</p></div>", unsafe_allow_html=True)

    col1, col2 = st.columns([1, 2])
    with col1:
        ts = time.time()
        st.image(f"assets/pito_{st.session_state.pito_mod}.gif?t={ts}")
        st.info(f"**GÖREV {egz['id']}:** {egz['yonerge']}")
        if st.session_state.error_count == 3: st.warning(f"💡 İpucu: {egz['ipucu']}")

    with col2:
        puan_pot = max(0, 20 - (st.session_state.error_count * 5))
        st.write(f"🎯 Kazanılacak: **{puan_pot} XP**")

        if not st.session_state.cevap_dogru and st.session_state.error_count < 4:
            kod_input = st.text_area("Kodunu Yaz:", value=egz['sablon'], height=200)
            if st.button("Kontrol Et"):
                if kod_input.strip() == egz['dogru_cevap_kodu'].strip():
                    st.session_state.cevap_dogru = True
                    st.session_state.pito_mod = "tebrik"
                    st.rerun()
                else:
                    st.session_state.error_count += 1
                    st.session_state.pito_mod = "hata"
                    st.rerun()

        elif st.session_state.cevap_dogru:
            st.success("🌟 Harika! Pito tebrik eder.")
            # İlerletme Hesaplama
            curr_idx = modul['egzersizler'].index(egz)
            if curr_idx + 1 < len(modul['egzersizler']):
                n_id, n_m = modul['egzersizler'][curr_idx+1]['id'], u['mevcut_modul']
            else:
                n_id, n_m = f"{int(float(u['mevcut_modul']))+1}.1", int(float(u['mevcut_modul'])) + 1
            
            if st.button("Sonraki Göreve Geç ➡️"):
                ilerleme_kaydet(puan_pot, kod_input, egz['id'], u['mevcut_modul'], n_id, n_m)

        elif st.session_state.error_count >= 4:
            st.session_state.pito_mod = "dusunuyor"
            st.error("🚫 Kilitlendi. Çözümü incele.")
            with st.expander("📖 Çözüm"): st.code(egz['cozum'])
            curr_idx = modul['egzersizler'].index(egz)
            n_id = modul['egzersizler'][curr_idx+1]['id'] if curr_idx+1 < len(modul['egzersizler']) else f"{int(float(u['mevcut_modul']))+1}.1"
            n_m = u['mevcut_modul'] if curr_idx+1 < len(modul['egzersizler']) else int(float(u['mevcut_modul'])) + 1
            if st.button("Sıradaki Göreve Geç ➡️"):
                ilerleme_kaydet(0, "Çözüm İncelendi", egz['id'], u['mevcut_modul'], n_id, n_m)
