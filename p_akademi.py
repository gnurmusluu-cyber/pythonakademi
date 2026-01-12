import streamlit as st
import pandas as pd
import json
import time
from datetime import datetime
from streamlit_gsheets import GSheetsConnection

# --- 1. SAYFA VE TASARIM AYARLARI ---
st.set_page_config(page_title="Pito Python Akademi", layout="wide")

# --- 2. HATA AYIKLAMALI VERİ YÜKLEME ---
@st.cache_data(ttl=60)
def load_mufredat_guvenli():
    try:
        with open('mufredat.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        st.error("❌ HATA: 'mufredat.json' dosyası ana dizinde bulunamadı!")
    except json.JSONDecodeError:
        st.error("❌ HATA: 'mufredat.json' dosyasının formatı hatalı (virgül veya parantez hatası olabilir)!")
    except Exception as e:
        st.error(f"❌ Müfredat yüklenirken bilinmeyen hata: {e}")
    return None

# --- 3. SESSION STATE BAŞLATMA ---
if "user" not in st.session_state: st.session_state.user = None
if "error_count" not in st.session_state: st.session_state.error_count = 0
if "cevap_dogru" not in st.session_state: st.session_state.cevap_dogru = False
if "pito_mod" not in st.session_state: st.session_state.pito_mod = "merhaba"

# --- 4. VERİTABANI BAĞLANTISI ---
KULLANICILAR_URL = "https://docs.google.com/spreadsheets/d/1lat8rO2qm9QnzEUYlzC_fypG3cRkGlJfSfTtwNvs318/edit#gid=0"
KAYITLAR_URL = "https://docs.google.com/spreadsheets/d/14QoNr4FHZhSaUDUU-DDQEfNFHMo5Ge5t5lyDgqGRJ3k/edit#gid=0"

try:
    conn = st.connection("gsheets", type=GSheetsConnection)
except Exception as e:
    st.error(f"🔌 Google Sheets Bağlantı Hatası! secrets.toml dosyanızı kontrol edin. Detay: {e}")

# --- 5. ANA AKIŞ ---
mufredat = load_mufredat_guvenli()

if mufredat:
    # GİRİŞ EKRANI
    if st.session_state.user is None:
        st.title("🐍 Pito Python Akademi")
        try:
            st.image("assets/pito_merhaba.gif", width=200)
        except:
            st.warning("⚠️ Pito görseli yüklenemedi. 'assets/' klasörünü kontrol edin.")
            
        numara = st.number_input("Öğrenci Numaranız:", step=1, value=0)
        if st.button("Akademiye Giriş Yap"):
            try:
                df_users = conn.read(spreadsheet=KULLANICILAR_URL, ttl=0)
                user = df_users[df_users['ogrenci_no'] == numara]
                if not user.empty:
                    st.session_state.user = user.iloc[0].to_dict()
                    st.rerun()
                else:
                    st.error("Öğrenci numarası sistemde kayıtlı değil!")
            except Exception as e:
                st.error(f"⚠️ Veritabanı okuma hatası: {e}")

    # EĞİTİM PANELİ
    else:
        u = st.session_state.user
        try:
            m_idx = int(float(u['mevcut_modul'])) - 1
            modul = mufredat['pito_akademi_mufredat'][m_idx]
            egz = next((e for e in modul['egzersizler'] if e['id'] == str(u['mevcut_egzersiz'])), modul['egzersizler'][0])
            
            st.subheader(f"🚀 Modül {m_idx+1}: {modul['modul_adi']}")
            
            col1, col2 = st.columns([1, 2])
            with col1:
                ts = time.time()
                st.image(f"assets/pito_{st.session_state.pito_mod}.gif?t={ts}")
                st.info(f"**GÖREV:** {egz['yonerge']}")
                
                # Kademeli Dönütler
                if st.session_state.error_count == 3:
                    st.warning(f"💡 İpucu: {egz['ipucu']}")

            with col2:
                puan_pot = max(0, 20 - (st.session_state.error_count * 5))
                st.write(f"🎯 Kazanılacak Puan: **{puan_pot} XP**")
                
                # ... Geri kalan Kontrol/İlerleme mantığı ...
                if st.button("Kontrol Et"):
                    # Basit bir test örneği (Gerçek mantığa göre güncellenebilir)
                    st.success("Test başarılı! Kodunuz çalışıyor.")

        except Exception as e:
            st.error(f"🧩 Müfredat veya Kullanıcı verisi eşleştirme hatası: {e}")
