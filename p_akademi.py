import streamlit as st
import pandas as pd
import json
import time
from datetime import datetime
from streamlit_gsheets import GSheetsConnection

# --- 1. SAYFA VE TASARIM AYARLARI ---
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

def load_mufredat():
    try:
        with open('mufredat.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        st.error(f"⚠️ mufredat.json dosyası yüklenemedi! Hata: {e}")
        return None

# --- 3. SESSION STATE (SİSTEM HAFIZASI) ---
# Eğer ekran boşsa buradaki değişkenler tetiklenmemiş olabilir.
if "user" not in st.session_state: st.session_state.user = None
if "error_count" not in st.session_state: st.session_state.error_count = 0
if "cevap_dogru" not in st.session_state: st.session_state.cevap_dogru = False
if "pito_mod" not in st.session_state: st.session_state.pito_mod = "merhaba"

# --- 4. VERİTABANI İŞLEMLERİ ---
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
except Exception as e:
    st.error(f"🔌 Google Sheets bağlantı hatası: {e}")

def ilerleme_kaydet(kazanilan_puan, next_id, next_m):
    try:
        df = conn.read(spreadsheet=KULLANICILAR_URL, ttl=0)
        idx = df[df['ogrenci_no'] == st.session_state.user['ogrenci_no']].index[0]
        
        df.at[idx, 'toplam_puan'] = int(float(df.at[idx, 'toplam_puan'])) + kazanilan_puan
        df.at[idx, 'mevcut_egzersiz'] = str(next_id)
        df.at[idx, 'mevcut_modul'] = int(next_m)
        
        conn.update(spreadsheet=KULLANICILAR_URL, data=df)
        
        # Hafızayı tazele
        st.session_state.user = df.iloc[idx].to_dict()
        st.session_state.error_count = 0
        st.session_state.cevap_dogru = False
        st.session_state.pito_mod = "merhaba"
        st.rerun()
    except Exception as e:
        st.error(f"📝 Veritabanı güncellenirken hata oluştu: {e}")

# --- 5. ANA AKIŞ ---
mufredat_verisi = load_mufredat()

if mufredat_verisi:
    # GİRİŞ EKRANI
    if st.session_state.user is None:
        st.title("🐍 Pito Python Akademi")
        st.image("assets/pito_merhaba.gif", width=250)
        
        numara = st.number_input("Öğrenci Numaranı Yaz:", step=1, value=0)
        if st.button("Giriş Yap"):
            df_users = conn.read(spreadsheet=KULLANICILAR_URL, ttl=0)
            user_row = df_users[df_users['ogrenci_no'] == numara]
            
            if not user_row.empty:
                st.session_state.user = user_row.iloc[0].to_dict()
                st.rerun()
            else:
                st.warning("Numaran bulunamadı. Lütfen kayıt bilgilerini kontrol et.")

    # EĞİTİM PANELİ
    else:
        u = st.session_state.user
        # Verileri tam sayıya mühürle
        m_idx = int(float(u['mevcut_modul'])) - 1
        modul = mufredat_verisi['pito_akademi_mufredat'][m_idx]
        egz_listesi = modul['egzersizler']
        egz = next((e for e in egz_listesi if e['id'] == str(u['mevcut_egzersiz'])), egz_listesi[0])

        # Kahraman Paneli
        st.markdown(f"""<div class='hero-panel'>
            <h3>🚀 {u['ad_soyad']} | {u['rutbe']}</h3>
            <p>📊 Toplam XP: {int(float(u['toplam_puan']))} | Modül: {m_idx + 1}</p>
            </div>""", unsafe_allow_html=True)

        col1, col2 = st.columns([1, 2])
        
        with col1:
            ts = time.time() # GIF yenileme hilesi
            st.image(f"assets/pito_{st.session_state.pito_mod}.gif?t={ts}", use_container_width=True)
            st.info(f"**GÖREV {egz['id']}:** {egz['yonerge']}")
            if st.session_state.error_count == 3:
                st.warning(f"💡 İpucu: {egz['ipucu']}")

        with col2:
            st.subheader("💻 Komut Paneli")
            puan_potansiyeli = max(0, 20 - (st.session_state.error_count * 5))
            st.write(f"🎯 Kazanılacak: **{puan_potansiyeli} XP**")

            # DURUM 1: ÇALIŞMA ANI
            if not st.session_state.cevap_dogru and st.session_state.error_count < 4:
                kod_input = st.text_area("Kodunu Yaz:", value=egz['sablon'], height=200)
                if st.button("Kontrol Et"):
                    if kod_input.strip() == egz['dogru_cevap_kodu'].strip():
                        st.session_state.cevap_dogru = True
                        st.session_state.pito_mod = "tebrik" # Doğru GIF: tebrik
                        st.rerun()
                    else:
                        st.session_state.error_count += 1
                        st.session_state.pito_mod = "hata"
                        st.rerun()

            # DURUM 2: TEBRİKLER VE İLERLEME
            elif st.session_state.cevap_dogru:
                st.success("🌟 Harika! Pito seninle gurur duyuyor.")
                
                # Bir sonraki egzersiz hesaplama
                curr_idx = egz_listesi.index(egz)
                if curr_idx + 1 < len(egz_listesi):
                    n_id, n_m = egz_listesi[curr_idx + 1]['id'], u['mevcut_modul']
                else:
                    n_id, n_m = f"{int(float(u['mevcut_modul']))+1}.1", int(float(u['mevcut_modul'])) + 1

                if st.button("Sonraki Göreve Geç ➡️"):
                    ilerleme_kaydet(puan_potansiyeli, n_id, n_m)

            # DURUM 3: HATA SINIRI (KİLİT)
            elif st.session_state.error_count >= 4:
                st.session_state.pito_mod = "dusunuyor"
                st.error("🚫 Panel Kilitlendi. Çözümü incele.")
                with st.expander("📖 Çözümü Gör", expanded=True):
                    st.code(egz['cozum'], language='python')
                
                curr_idx = egz_listesi.index(egz)
                n_id = egz_listesi[curr_idx + 1]['id'] if curr_idx+1 < len(egz_listesi) else f"{int(float(u['mevcut_modul']))+1}.1"
                n_m = u['mevcut_modul'] if curr_idx+1 < len(egz_listesi) else int(float(u['mevcut_modul'])) + 1
                
                if st.button("Anladım, Sıradaki Göreve Geç ➡️"):
                    ilerleme_kaydet(0, n_id, n_m)
