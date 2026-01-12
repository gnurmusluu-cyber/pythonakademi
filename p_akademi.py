import streamlit as st
import pandas as pd
import json
import time
import os
import re
from datetime import datetime
from streamlit_gsheets import GSheetsConnection

# --- 1. SİSTEM AYARLARI VE TASARIM ---
st.set_page_config(page_title="Pito Python Akademi", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
    .stApp { background-color: #0E1117; color: #FFFFFF; }
    .hero-panel { background: linear-gradient(90deg, #1E1E2F 0%, #2D2D44 100%); padding: 20px; border-radius: 15px; border-left: 8px solid #00FF00; margin-bottom: 20px; box-shadow: 0 4px 15px rgba(0,255,0,0.2); }
    .leader-panel { background-color: #161B22; padding: 20px; border-radius: 15px; border: 1px solid #30363D; }
    .sampiyon-kart { background: linear-gradient(45deg, #FFD700, #FFA500); padding: 20px; border-radius: 12px; text-align: center; color: black; margin-bottom: 20px; font-weight: bold; font-size: 1.2em; }
    .stProgress > div > div > div > div { background-color: #00FF00; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. AKILLI VERİ MOTORLARI ---
def kod_normalize_et(kod):
    return re.sub(r'\s+', '', str(kod)).strip().lower()

@st.cache_data(ttl=300) # Liderlik verilerini 5 dk hafızada tutarak API'yi korur
def okul_verilerini_getir_guvenli(url):
    try:
        return conn.read(spreadsheet=url, ttl=300)
    except:
        return None

def pito_gorseli_yukle(mod):
    base_path = os.path.dirname(os.path.abspath(__file__))
    img_path = os.path.join(base_path, "assets", f"pito_{mod}.gif")
    if os.path.exists(img_path):
        st.image(img_path, use_container_width=True)

# --- 3. VERİTABANI VE MÜFREDAT BAĞLANTILARI ---
KULLANICILAR_URL = "https://docs.google.com/spreadsheets/d/1lat8rO2qm9QnzEUYlzC_fypG3cRkGlJfSfTtwNvs318/edit#gid=0"
KAYITLAR_URL = "https://docs.google.com/spreadsheets/d/14QoNr4FHZhSaUDUU-DDQEfNFHMo5Ge5t5lyDgqGRJ3k/edit#gid=0"

conn = st.connection("gsheets", type=GSheetsConnection)

try:
    with open('mufredat.json', 'r', encoding='utf-8') as f:
        mufredat = json.load(f)
except:
    st.error("Müfredat dosyası yüklenemedi!")
    st.stop()

# --- 4. SESSION STATE ---
if "user" not in st.session_state: st.session_state.user = None
if "error_count" not in st.session_state: st.session_state.error_count = 0
if "cevap_dogru" not in st.session_state: st.session_state.cevap_dogru = False
if "pito_mod" not in st.session_state: st.session_state.pito_mod = "merhaba"
if "last_code" not in st.session_state: st.session_state.last_code = ""

# --- 5. ANA AKIŞ ---
if st.session_state.user is None:
    # GİRİŞ EKRANI (Aynı Kalabilir)
    st.title("🐍 Pito Python Akademi")
    pito_gorseli_yukle("merhaba")
    numara = st.number_input("Öğrenci Numarası:", step=1, value=0)
    if st.button("Sisteme Giriş Yap 🚀") and numara > 0:
        df_u = conn.read(spreadsheet=KULLANICILAR_URL, ttl=0)
        user_data = df_u[df_u['ogrenci_no'] == numara]
        if not user_data.empty:
            st.session_state.user = user_data.iloc[0].to_dict()
            st.rerun()
        else: st.warning("Numara bulunamadı!")
else:
    # --- EĞİTİM VE LİDERLİK ARENASI (BURASI DÜZELDİ) ---
    u = st.session_state.user
    
    # 1. EKRANI BÖL (Sol: Eğitim, Sağ: Liderlik)
    col_main, col_leader = st.columns([7, 3])

    # --- SOL PANEL: EĞİTİM VE İLERLEME ---
    with col_main:
        m_idx = int(float(u['mevcut_modul'])) - 1
        modul = mufredat['pito_akademi_mufredat'][m_idx]
        egz_liste = modul['egzersizler']
        egz = next((e for e in egz_liste if e['id'] == str(u['mevcut_egzersiz'])), egz_liste[0])

        # A. Hero Header ve İlerleme Çubuğu
        st.markdown(f"<div class='hero-panel'><h3>🚀 {u['ad_soyad']} | {u['sinif']}</h3><p>{u['rutbe']} | {int(float(u['toplam_puan']))} XP</p></div>", unsafe_allow_html=True)
        
        # İlerleme Hesapla
        egz_sira = egz_liste.index(egz) + 1
        ilerleme_yuzde = (egz_sira / len(egz_liste))
        st.write(f"📊 **Modül İlerlemesi:** {egz_sira} / {len(egz_liste)}")
        st.progress(ilerleme_yuzde)

        # B. Eğitim Alanı
        c_p, c_e = st.columns([1, 2])
        with c_p:
            pito_gorseli_yukle(st.session_state.pito_mod)
            st.info(f"**GÖREV {egz['id']}:** {egz['yonerge']}")
            if st.session_state.error_count == 3: st.warning(f"💡 İpucu: {egz['ipucu']}")

        with c_e:
            p_pot = max(0, 20 - (st.session_state.error_count * 5))
            st.write(f"🎯 Kazanılacak: **{p_pot} XP**")
            k_in = st.text_area("Kodun:", value=egz['sablon'], height=200, key="editor")
            
            if st.button("Kontrol Et"):
                st.session_state.last_code = k_in
                if kod_normalize_et(k_in) == kod_normalize_et(egz['dogru_cevap_kodu']):
                    st.session_state.cevap_dogru, st.session_state.pito_mod = True, "basari"
                    st.rerun()
                else:
                    st.session_state.error_count += 1
                    st.session_state.pito_mod = "hata"
                    st.rerun()

        # C. Başarı ve Geçiş (Önceki İlerleme Kaydet Fonksiyonu Buraya Gelecek)
        if st.session_state.cevap_dogru:
            st.success("Tebrikler!")
            if st.button("Sonraki Göreve Geç ➡️"):
                # Buraya ilerleme_kaydet() fonksiyonu çağrısı gelecek
                pass

    # --- SAĞ PANEL: ONUR KÜRSÜSÜ ---
    with col_leader:
        st.markdown("<h3 style='text-align:center;'>🏆 Onur Kürsüsü</h3>", unsafe_allow_html=True)
        
        # API Kalkanı ile veriyi çek
        df_all = okul_verilerini_getir_guvenli(KULLANICILAR_URL)
        
        if df_all is not None:
            df_all['toplam_puan'] = pd.to_numeric(df_all['toplam_puan'], errors='coerce').fillna(0).astype(int)

            # 1. ŞAMPİYON SINIF PANOSU (Ortalama XP)
            s_an = df_all.groupby('sinif').agg(xp=('toplam_puan','sum'), sayi=('ogrenci_no','count'))
            s_an['ort'] = (s_an['xp'] / s_an['sayi']).round(1)
            s_an = s_an.sort_values(by='ort', ascending=False)
            
            st.markdown(f"""
                <div class='sampiyon-kart'>
                    ⭐ ŞAMPİYON SINIF ⭐<br>
                    <span style='font-size:24px;'>{s_an.index[0]}</span><br>
                    {s_an.iloc[0]['ort']} XP Ortalaması
                </div>
                """, unsafe_allow_html=True)

            # 2. LİDERLİK TABLOLARI (Sekmeler)
            with st.container():
                tab_s, tab_o = st.tabs(["👥 Sınıfım", "🏫 Okul En İyiler"])
                with tab_s:
                    s_df = df_all[df_all['sinif'] == u['sinif']].sort_values(by='toplam_puan', ascending=False).head(10)
                    for i, r in enumerate(s_df.itertuples(), 1):
                        st.markdown(f"**{i}.** {r.ad_soyad} • `{r.toplam_puan} XP`")
                with tab_o:
                    o_df = df_all.sort_values(by='toplam_puan', ascending=False).head(10)
                    for i, r in enumerate(o_df.itertuples(), 1):
                        p = "🥇" if i==1 else "🥈" if i==2 else "🥉" if i==3 else f"**{i}.**"
                        st.markdown(f"{p} {r.ad_soyad} ({r.sinif}) • `{r.toplam_puan} XP`")
        else:
            st.warning("📊 Liderlik tablosu şu an güncellenemiyor (API Limiti). Kodlamaya devam et!")
