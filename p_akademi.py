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

# --- 2. GÜVENLİ VE AKILLI VERİ OKUMA (KRİTİK ÇÖZÜM) ---

@st.cache_data(ttl=60) # Veriyi 60 saniye boyunca hafızada tutar, API'yi yormaz.
def veri_oku_akilli(url):
    try:
        # Burada bağlantıyı kurup veriyi döndürüyoruz
        return conn.read(spreadsheet=url, ttl=60)
    except Exception as e:
        # Hata anında en azından uygulamayı çökertmez
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

conn = st.connection("gsheets", type=GSheetsConnection)

try:
    with open('mufredat.json', 'r', encoding='utf-8') as f:
        mufredat = json.load(f)
except:
    st.error("❌ Müfredat dosyası yüklenemedi!")
    st.stop()

# --- 4. SESSION STATE ---
if "user" not in st.session_state: st.session_state.user = None
if "error_count" not in st.session_state: st.session_state.error_count = 0
if "cevap_dogru" not in st.session_state: st.session_state.cevap_dogru = False
if "pito_mod" not in st.session_state: st.session_state.pito_mod = "merhaba"
if "last_code" not in st.session_state: st.session_state.last_code = ""

# --- 5. VERİ YAZMA MOTORU ---
def ilerleme_kaydet(puan, kod, egz_id, m_id, n_id, n_m):
    try:
        # Yazma sırasında en güncel veriyi okumalıyız (Sadece bu anlık ttl=0 olabilir)
        df_u = conn.read(spreadsheet=KULLANICILAR_URL, ttl=0)
        u_idx = df_u[df_u['ogrenci_no'] == st.session_state.user['ogrenci_no']].index[0]
        
        yeni_xp = int(float(df_u.at[u_idx, 'toplam_puan'])) + puan
        df_u.at[u_idx, 'toplam_puan'] = yeni_xp
        df_u.at[u_idx, 'mevcut_egzersiz'] = str(n_id)
        df_u.at[u_idx, 'mevcut_modul'] = int(float(n_m))
        
        # Rütbe Sistemi
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
        
        # Hafızayı temizle ve güncelle
        st.session_state.user = df_u.iloc[u_idx].to_dict()
        st.session_state.error_count, st.session_state.cevap_dogru, st.session_state.pito_mod = 0, False, "merhaba"
        
        # KRİTİK: Yazma sonrası cache'i temizle ki liderlik tablosu güncellensin
        st.cache_data.clear()
        st.rerun()
    except Exception as e:
        st.error(f"⚠️ Google API Limiti aşıldı! Lütfen 10 saniye bekleyip tekrar deneyin. Hata: {e}")

# --- 6. ANA AKIŞ ---
if st.session_state.user is None:
    st.title("🐍 Pito Python Akademi")
    pito_gorseli_yukle("merhaba")
    
    numara = st.number_input("Öğrenci Numarası:", step=1, value=0)
    if st.button("Sisteme Giriş Yap 🚀"):
        # Giriş yaparken bir kereye mahsus ttl=0 ile taze veri alıyoruz
        df_u = conn.read(spreadsheet=KULLANICILAR_URL, ttl=0)
        user_data = df_u[df_u['ogrenci_no'] == numara]
        if not user_data.empty:
            st.session_state.user = user_data.iloc[0].to_dict()
            st.rerun()
        else:
            st.warning("Kayıt bulunamadı. Lütfen yeni kayıt oluşturun.")
else:
    # Dashboard ve Eğitim Alanı
    u = st.session_state.user
    col_main, col_leader = st.columns([7, 3])

    with col_main:
        m_idx = int(float(u['mevcut_modul'])) - 1
        modul = mufredat['pito_akademi_mufredat'][m_idx]
        egz = next((e for e in modul['egzersizler'] if e['id'] == str(u['mevcut_egzersiz'])), modul['egzersizler'][0])
        
        st.markdown(f"<div class='hero-panel'><h3>🚀 {u['ad_soyad']} | {u['sinif']}</h3><p>{u['rutbe']} | {int(float(u['toplam_puan']))} XP</p></div>", unsafe_allow_html=True)
        
        # Eğitim ve Kontrol Butonları...
        k_in = st.text_area("Kodun:", value=egz['sablon'], height=200)
        if st.button("Kontrol Et"):
            st.session_state.last_code = k_in
            if kod_normalize_et(k_in) == kod_normalize_et(egz['dogru_cevap_kodu']):
                st.session_state.cevap_dogru, st.session_state.pito_mod = True, "basari"
                st.rerun()
            else:
                st.session_state.error_count += 1
                st.session_state.pito_mod = "hata"
                st.rerun()
        
        if st.session_state.cevap_dogru:
            if st.button("Sonraki Göreve Geç ➡️"):
                p_pot = max(0, 20 - (st.session_state.error_count * 5))
                idx = modul['egzersizler'].index(egz)
                n_id, n_m = (modul['egzersizler'][idx+1]['id'], u['mevcut_modul']) if idx+1 < len(modul['egzersizler']) else (f"{m_idx + 2}.1", m_idx + 2)
                ilerleme_kaydet(p_pot, st.session_state.last_code, egz['id'], u['mevcut_modul'], n_id, n_m)

    # SAĞ PANEL: LİDERLİK (API KALKANI BURADA ÇALIŞIR)
    with col_leader:
        st.markdown("### 🏆 Onur Kürsüsü")
        # Burası veriyi 60 saniyede bir çeker, Google'ı yormaz.
        df_all = veri_oku_akilli(KULLANICILAR_URL)
        if df_all is not None:
            st.dataframe(df_all.sort_values("toplam_puan", ascending=False)[['ad_soyad', 'toplam_puan']].head(10))
