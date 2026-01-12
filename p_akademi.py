import streamlit as st
import pandas as pd
import json
import time
from datetime import datetime
from streamlit_gsheets import GSheetsConnection

# --- 1. SAYFA AYARLARI ---
st.set_page_config(page_title="Pito Python Akademi", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #0E1117; color: #FFFFFF; }
    .hero-panel { background: linear-gradient(90deg, #1E1E2F 0%, #2D2D44 100%); padding: 20px; border-radius: 15px; border-left: 5px solid #00FF00; margin-bottom: 20px; }
    .stButton>button { border-radius: 10px; background-color: #00FF00 !important; color: black !important; font-weight: bold; width: 100%; height: 3.5em; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. BAĞLANTILAR VE MÜFREDAT ---
KULLANICILAR_URL = "https://docs.google.com/spreadsheets/d/1lat8rO2qm9QnzEUYlzC_fypG3cRkGlJfSfTtwNvs318/edit#gid=0"
KAYITLAR_URL = "https://docs.google.com/spreadsheets/d/14QoNr4FHZhSaUDUU-DDQEfNFHMo5Ge5t5lyDgqGRJ3k/edit#gid=0"

conn = st.connection("gsheets", type=GSheetsConnection)

def load_mufredat():
    with open('mufredat.json', 'r', encoding='utf-8') as f:
        return json.load(f)

# --- 3. SESSION STATE ---
if "user" not in st.session_state: st.session_state.user = None
if "error_count" not in st.session_state: st.session_state.error_count = 0
if "cevap_dogru" not in st.session_state: st.session_state.cevap_dogru = False
if "pito_mod" not in st.session_state: st.session_state.pito_mod = "merhaba"

# --- 4. VERİ MOTORU ---
def ilerleme_kaydet(puan, kod, egz_id, m_id, n_id, n_m):
    df_u = conn.read(spreadsheet=KULLANICILAR_URL, ttl=0)
    idx = df_u[df_u['ogrenci_no'] == st.session_state.user['ogrenci_no']].index[0]
    df_u.at[idx, 'toplam_puan'] = int(float(df_u.at[idx, 'toplam_puan'])) + puan
    df_u.at[idx, 'mevcut_egzersiz'] = str(n_id)
    df_u.at[idx, 'mevcut_modul'] = int(float(n_m))
    conn.update(spreadsheet=KULLANICILAR_URL, data=df_u)

    df_k = conn.read(spreadsheet=KAYITLAR_URL, ttl=0)
    log = pd.DataFrame([{"kayit_id": f"{st.session_state.user['ogrenci_no']}_{egz_id}", "ogrenci_no": int(st.session_state.user['ogrenci_no']), "modul_id": int(float(m_id)), "egzersiz_id": str(egz_id), "alinan_puan": int(puan), "basarili_kod": kod, "tarih": datetime.now().strftime("%Y-%m-%d %H:%M")}])
    conn.update(spreadsheet=KAYITLAR_URL, data=pd.concat([df_k, log], ignore_index=True))
    
    st.session_state.user = df_u.iloc[idx].to_dict()
    st.session_state.error_count, st.session_state.cevap_dogru, st.session_state.pito_mod = 0, False, "merhaba"
    st.rerun()

# --- 5. EĞİTİM PANELİ ---
mufredat = load_mufredat()

if st.session_state.user:
    u = st.session_state.user
    m_idx = int(float(u['mevcut_modul'])) - 1
    modul = mufredat['pito_akademi_mufredat'][m_idx]
    egz = next((e for e in modul['egzersizler'] if e['id'] == str(u['mevcut_egzersiz'])), modul['egzersizler'][0])

    st.markdown(f"<div class='hero-panel'><h3>🚀 {u['ad_soyad']} | {u['rutbe']}</h3><p>XP: {int(float(u['toplam_puan']))} | Modül: {m_idx+1}</p></div>", unsafe_allow_html=True)

    col1, col2 = st.columns([1, 2])
    with col1:
        ts = time.time()
        # 3. hatada da 'hata' gifinin oynatılması sağlandı
        st.image(f"assets/pito_{st.session_state.pito_mod}.gif?t={ts}")
        st.info(f"**GÖREV {egz['id']}:** {egz['yonerge']}")
        
        # --- KADEMELİ DÖNÜT SİSTEMİ ---
        if st.session_state.error_count == 1:
            st.error("🤫 Pito: 'Ufak bir hata! Yazım kurallarını kontrol et.'")
        elif st.session_state.error_count == 2:
            st.error("🧐 Pito: 'Dikkatli bak, küçük bir eksik var!'")
        elif st.session_state.error_count == 3:
            # Burası pito_hata.gif ile birlikte görünecek
            st.warning(f"💡 Pito: 'Sana yardımcı olayım, işte ipucun: {egz['ipucu']}'")

    with col2:
        puan_pot = max(0, 20 - (st.session_state.error_count * 5))
        st.write(f"💰 Kazanılacak: **{puan_pot} XP**")

        if not st.session_state.cevap_dogru and st.session_state.error_count < 4:
            kod_input = st.text_area("Kodunu Yaz:", value=egz['sablon'], height=200)
            if st.button("Kontrol Et"):
                if kod_input.strip() == egz['dogru_cevap_kodu'].strip():
                    st.session_state.cevap_dogru, st.session_state.pito_mod = True, "tebrik"
                    st.rerun()
                else:
                    st.session_state.error_count += 1
                    # 4. hataya kadar GIF 'hata' modunda kalır
                    if st.session_state.error_count < 4:
                        st.session_state.pito_mod = "hata"
                    else:
                        st.session_state.pito_mod = "dusunuyor"
                    st.rerun()

        elif st.session_state.cevap_dogru:
            st.success(f"🌟 Harika! {puan_pot} XP Kazandın.")
            idx = modul['egzersizler'].index(egz)
            n_id, n_m = (modul['egzersizler'][idx+1]['id'], u['mevcut_modul']) if idx+1 < len(modul['egzersizler']) else (f"{m_idx + 2}.1", m_idx + 2)
            if st.button("Sonraki Göreve Geç ➡️"):
                ilerleme_kaydet(puan_pot, kod_input, egz['id'], u['mevcut_modul'], n_id, n_m)

        elif st.session_state.error_count >= 4:
            st.error("🚫 Kilitlendi! Çözümü inceleyip ilerle.")
            with st.expander("📖 Pito'nun Çözümü", expanded=True): st.code(egz['cozum'])
            idx = modul['egzersizler'].index(egz)
            n_id, n_m = (modul['egzersizler'][idx+1]['id'], u['mevcut_modul']) if idx+1 < len(modul['egzersizler']) else (f"{m_idx + 2}.1", m_idx + 2)
            if st.button("Anladım, Sıradaki Göreve Geç ➡️"):
                ilerleme_kaydet(0, "Çözüm İncelendi", egz['id'], u['mevcut_modul'], n_id, n_m)
