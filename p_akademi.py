import streamlit as st
import pandas as pd
import json
import time
import os
import re
from datetime import datetime
from streamlit_gsheets import GSheetsConnection

# --- 1. SİSTEM AYARLARI ---
st.set_page_config(page_title="Pito Python Akademi", layout="wide", initial_sidebar_state="collapsed")

# --- 2. GÜVENLİ VE AKILLI VERİ OKUMA (API ÇÖZÜMÜ) ---

@st.cache_data(ttl=300) # Liderlik tablosu için 5 dakikalık derin önbellek
def okul_verisini_getir(url):
    """Okul genel verilerini API'yi yormadan 5 dakikada bir çeker."""
    try:
        return conn.read(spreadsheet=url, ttl=300)
    except:
        return None

def kod_normalize_et(kod):
    return re.sub(r'\s+', '', str(kod)).strip().lower()

def pito_gorseli_yukle(mod):
    base_path = os.path.dirname(os.path.abspath(__file__))
    img_path = os.path.join(base_path, "assets", f"pito_{mod}.gif")
    if os.path.exists(img_path):
        st.image(img_path, use_container_width=True)
    else:
        st.warning(f"🖼️ Görsel Eksik: assets/pito_{mod}.gif")

# --- 3. BAĞLANTILAR ---
KULLANICILAR_URL = "https://docs.google.com/spreadsheets/d/1lat8rO2qm9QnzEUYlzC_fypG3cRkGlJfSfTtwNvs318/edit#gid=0"
KAYITLAR_URL = "https://docs.google.com/spreadsheets/d/14QoNr4FHZhSaUDUU-DDQEfNFHMo5Ge5t5lyDgqGRJ3k/edit#gid=0"

try:
    conn = st.connection("gsheets", type=GSheetsConnection)
except Exception as e:
    st.error(f"❌ Google Bağlantı Hatası: {e}")

# Müfredat Yükleme
try:
    with open('mufredat.json', 'r', encoding='utf-8') as f:
        mufredat = json.load(f)
except Exception as e:
    st.error(f"❌ Müfredat Dosyası Eksik: {e}")
    st.stop()

# --- 4. HAFIZA YÖNETİMİ ---
if "user" not in st.session_state: st.session_state.user = None
if "error_count" not in st.session_state: st.session_state.error_count = 0
if "cevap_dogru" not in st.session_state: st.session_state.cevap_dogru = False
if "pito_mod" not in st.session_state: st.session_state.pito_mod = "merhaba"
if "last_code" not in st.session_state: st.session_state.last_code = ""

# --- 5. VERİ YAZMA MOTORU ---
def ilerleme_kaydet(puan, kod, egz_id, m_id, n_id, n_m):
    try:
        # Yazma işleminde en güncel veriyi zorla oku (ttl=0)
        df_u = conn.read(spreadsheet=KULLANICILAR_URL, ttl=0)
        u_idx = df_u[df_u['ogrenci_no'] == st.session_state.user['ogrenci_no']].index[0]
        yeni_xp = int(float(df_u.at[u_idx, 'toplam_puan'])) + puan
        df_u.at[u_idx, 'toplam_puan'] = yeni_xp
        df_u.at[u_idx, 'mevcut_egzersiz'] = str(n_id)
        df_u.at[u_idx, 'mevcut_modul'] = int(float(n_m))
        
        # Rütbe
        if yeni_xp >= 1000: r = "🏆 Bilge"
        elif yeni_xp >= 500: r = "🔥 Savaşçı"
        elif yeni_xp >= 200: r = "🐍 Pythonist"
        else: r = "🥚 Çömez"
        df_u.at[u_idx, 'rutbe'] = r
        
        conn.update(spreadsheet=KULLANICILAR_URL, data=df_u)
        
        # Aktivite Logu
        df_k = conn.read(spreadsheet=KAYITLAR_URL, ttl=0)
        yeni_log = pd.DataFrame([{"kayit_id": f"{st.session_state.user['ogrenci_no']}_{egz_id}", "ogrenci_no": int(st.session_state.user['ogrenci_no']), "modul_id": int(float(m_id)), "egzersiz_id": str(egz_id), "alinan_puan": int(puan), "basarili_kod": kod, "tarih": datetime.now().strftime("%Y-%m-%d %H:%M")}])
        conn.update(spreadsheet=KAYITLAR_URL, data=pd.concat([df_k, yeni_log], ignore_index=True))
        
        # Hafızayı Güncelle
        st.session_state.user = df_u.iloc[u_idx].to_dict()
        st.session_state.error_count, st.session_state.cevap_dogru, st.session_state.pito_mod = 0, False, "merhaba"
        st.cache_data.clear() # Liderlik tablosunu yenilemeye zorla
        st.rerun()
    except Exception as e:
        st.error(f"❌ API Kotası dolu, 10 saniye sonra tekrar dene! ({e})")

# --- 6. ANA AKIŞ ---
if st.session_state.user is None:
    st.title("🐍 Pito Python Akademi")
    pito_gorseli_yukle("merhaba")
    numara = st.number_input("Öğrenci Numarası:", step=1, value=0)
    
    if numara > 0:
        # Sadece girişte veritabanına bak
        if st.button("Sistemde Kontrol Et"):
            df_u = conn.read(spreadsheet=KULLANICILAR_URL, ttl=0)
            user_data = df_u[df_u['ogrenci_no'] == numara]
            if not user_data.empty:
                st.session_state.user = user_data.iloc[0].to_dict()
                st.rerun()
            else:
                st.info("Kayıt bulunamadı, lütfen aşağıdan kaydolun.")
                # Kayıt formu burada açılabilir...
else:
    u = st.session_state.user
    col_main, col_leader = st.columns([7, 3])

    with col_main:
        # Eğitim İçeriği (Yönerge, Kod Alanı vb. - önceki kodlar buraya)
        m_idx = int(float(u['mevcut_modul'])) - 1
        modul = mufredat['pito_akademi_mufredat'][m_idx]
        egz = next((e for e in modul['egzersizler'] if e['id'] == str(u['mevcut_egzersiz'])), modul['egzersizler'][0])
        
        st.markdown(f"<div class='hero-panel'><h3>🚀 {u['ad_soyad']} | {u['sinif']}</h3><p>{u['rutbe']} | {int(float(u['toplam_puan']))} XP</p></div>", unsafe_allow_html=True)
        
        # Kontrol Mekanizması
        k_in = st.text_area("Kodun:", value=egz['sablon'], height=200, key="editor")
        if st.button("Kontrol Et"):
            if kod_normalize_et(k_in) == kod_normalize_et(egz['dogru_cevap_kodu']):
                st.session_state.cevap_dogru, st.session_state.pito_mod = True, "basari"
                st.rerun()
            else:
                st.session_state.error_count += 1
                st.session_state.pito_mod = "hata" if st.session_state.error_count < 4 else "dusunuyor"
                st.rerun()

        if st.session_state.cevap_dogru:
            if st.button("Sonraki Göreve Geç ➡️"):
                p_pot = max(0, 20 - (st.session_state.error_count * 5))
                idx = modul['egzersizler'].index(egz)
                n_id, n_m = (modul['egzersizler'][idx+1]['id'], u['mevcut_modul']) if idx+1 < len(modul['egzersizler']) else (f"{m_idx + 2}.1", m_idx + 2)
                ilerleme_kaydet(p_pot, k_in, egz['id'], u['mevcut_modul'], n_id, n_m)

    # --- SAĞ PANEL: LİDERLİK TABLOSU (API KALKANI BURADA) ---
    with col_leader:
        st.markdown("### 🏆 Onur Kürsüsü")
        df_all = okul_verisini_getir(KULLANICILAR_URL) # 5 dakikada bir çeker!
        
        if df_all is not None:
            df_all['toplam_puan'] = pd.to_numeric(df_all['toplam_puan'], errors='coerce').fillna(0).astype(int)
            # Sınıfım ve Okul sekmeleri buraya...
            st.dataframe(df_all.sort_values("toplam_puan", ascending=False)[['ad_soyad', 'toplam_puan']].head(10))
