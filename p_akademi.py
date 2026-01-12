import streamlit as st
import pandas as pd
import json
import time
import os
import re
from datetime import datetime
from streamlit_gsheets import GSheetsConnection

# --- 1. SİSTEM VE SİBER TASARIM ---
st.set_page_config(page_title="Pito Python Akademi", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
    .stApp { background-color: #0E1117; color: #FFFFFF; }
    .hero-panel { background: linear-gradient(90deg, #1E1E2F 0%, #2D2D44 100%); padding: 20px; border-radius: 15px; border-left: 8px solid #00FF00; margin-bottom: 20px; box-shadow: 0 4px 15px rgba(0,255,0,0.2); }
    .leader-panel { background-color: #161B22; padding: 15px; border-radius: 15px; border: 1px solid #30363D; }
    .sampiyon-kart { background: linear-gradient(45deg, #FFD700, #FFA500); padding: 20px; border-radius: 12px; text-align: center; color: black; margin-bottom: 20px; font-weight: bold; box-shadow: 0 0 15px #FFD700; }
    .pito-notu { background-color: #1E1E2F; border-radius: 10px; padding: 15px; border-left: 5px solid #00FF00; margin-top: 10px; font-style: italic; }
    .stButton>button { border-radius: 10px; background-color: #00FF00 !important; color: black !important; font-weight: bold; width: 100%; height: 3em; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. YARDIMCI MOTORLAR ---
def kod_normalize_et(kod):
    return re.sub(r'\s+', '', str(kod)).strip().lower()

def pito_gorseli_yukle(mod):
    base_path = os.path.dirname(os.path.abspath(__file__))
    img_path = os.path.join(base_path, "assets", f"pito_{mod}.gif")
    if os.path.exists(img_path):
        st.image(img_path, use_container_width=True)
    else:
        st.warning(f"🖼️ Pito nerede? (assets/pito_{mod}.gif eksik)")

# Pito'nun Duruma Göre Değişen Notları
def pito_notu_uret(mod, ad="Dostum"):
    notlar = {
        "merhaba": f"Merhaba {ad}! Bugün harika bir gün, Python dünyasını keşfetmeye hazır mısın?",
        "basari": f"Vay canına {ad}! Bu kod tam bir sanat eseri. Nusaybin'in gururusun!",
        "hata": f"Ufak bir tökezleme {ad}, sakın pes etme! Bir daha bak, o hatayı bulacaksın.",
        "dusunuyor": f"Hımm... {ad}, bu biraz zorlayıcı olabilir ama çözümü hemen aşağıda seni bekliyor.",
        "mezun": f"İnanamıyorum {ad}! Tüm engelleri aştın ve Pito Python Akademi'den mezun oldun!"
    }
    return notlar.get(mod, notlar["merhaba"])

# --- 3. VERİ OKUMA (API KALKANIYLA) ---
KULLANICILAR_URL = "https://docs.google.com/spreadsheets/d/1lat8rO2qm9QnzEUYlzC_fypG3cRkGlJfSfTtwNvs318/edit#gid=0"
conn = st.connection("gsheets", type=GSheetsConnection)

@st.cache_data(ttl=60) # 1 dakikalık önbellek API hatasını önler
def verileri_cek():
    try:
        return conn.read(spreadsheet=KULLANICILAR_URL, ttl=60)
    except:
        return None

# --- 4. SESSION STATE ---
if "user" not in st.session_state: st.session_state.user = None
if "pito_mod" not in st.session_state: st.session_state.pito_mod = "merhaba"
if "cevap_dogru" not in st.session_state: st.session_state.cevap_dogru = False
if "error_count" not in st.session_state: st.session_state.error_count = 0

# --- 5. ANA AKIŞ ---
with open('mufredat.json', 'r', encoding='utf-8') as f:
    mufredat = json.load(f)

if st.session_state.user is None:
    # GİRİŞ EKRANI
    st.title("🐍 Pito Python Akademi")
    pito_gorseli_yukle("merhaba")
    numara = st.number_input("Öğrenci Numarası:", step=1)
    if st.button("Sisteme Bağlan"):
        df = conn.read(spreadsheet=KULLANICILAR_URL, ttl=0)
        user = df[df['ogrenci_no'] == numara]
        if not user.empty:
            st.session_state.user = user.iloc[0].to_dict()
            st.rerun()
else:
    u = st.session_state.user
    
    # EKRAN DÜZENİ: SOL (7) - SAĞ (3)
    col_main, col_leader = st.columns([7, 3])

    # --- SOL TARAF: EĞİTİM ALANI ---
    with col_main:
        m_idx = int(float(u['mevcut_modul'])) - 1
        modul = mufredat['pito_akademi_mufredat'][m_idx]
        egz_liste = modul['egzersizler']
        egz = next((e for e in egz_liste if e['id'] == str(u['mevcut_egzersiz'])), egz_liste[0])

        # Hero Header
        st.markdown(f"<div class='hero-panel'><h3>🚀 {u['ad_soyad']} | {u['sinif']}</h3><p>{u['rutbe']} | {int(float(u['toplam_puan']))} XP</p></div>", unsafe_allow_html=True)

        # İlerleme Çubuğu
        sira = egz_liste.index(egz) + 1
        st.write(f"📊 **Modül İlerlemesi:** {sira}/{len(egz_liste)}")
        st.progress(sira / len(egz_liste))

        # Pito ve Görev
        c1, c2 = st.columns([1, 2])
        with c1:
            pito_gorseli_yukle(st.session_state.pito_mod)
        with c2:
            st.info(f"**GÖREV {egz['id']}:**\n{egz['yonerge']}")
            # PİTO'NUN NOTU (BURADA GÖRÜNECEK)
            st.markdown(f"<div class='pito-notu'>💬 <b>Pito:</b> {pito_notu_uret(st.session_state.pito_mod, u['ad_soyad'].split()[0])}</div>", unsafe_allow_html=True)

        # Editör Alanı
        kod_in = st.text_area("Kodunu Yaz:", value=egz['sablon'], height=180, key="editor")
        if st.button("Kontrol Et"):
            if kod_normalize_et(kod_in) == kod_normalize_et(egz['dogru_cevap_kodu']):
                st.session_state.cevap_dogru, st.session_state.pito_mod = True, "basari"
                st.rerun()
            else:
                st.session_state.error_count += 1
                st.session_state.pito_mod = "hata"
                st.rerun()

        if st.session_state.cevap_dogru:
            st.success("Tebrikler!")
            if st.button("Sıradaki Göreve Geç ➡️"):
                # İlerleme Kaydetme Fonksiyonu buraya...
                pass

    # --- SAĞ TARAF: ONUR KÜRSÜSÜ ---
    with col_leader:
        st.markdown("<h3 style='text-align:center;'>🏆 ONUR KÜRSÜSÜ</h3>", unsafe_allow_html=True)
        
        df_all = verileri_cek()
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
            t1, t2 = st.tabs(["👥 Sınıfım", "🏫 Okul Geneli"])
            with t1:
                sinif_df = df_all[df_all['sinif'] == u['sinif']].sort_values(by='toplam_puan', ascending=False).head(10)
                for i, r in enumerate(sinif_df.itertuples(), 1):
                    st.markdown(f"**{i}.** {r.ad_soyad} • `{r.toplam_puan} XP`")
            with t2:
                okul_df = df_all.sort_values(by='toplam_puan', ascending=False).head(10)
                for i, r in enumerate(okul_df.itertuples(), 1):
                    p = "🥇" if i==1 else "🥈" if i==2 else "🥉" if i==3 else f"**{i}.**"
                    st.markdown(f"{p} {r.ad_soyad} ({r.sinif}) • `{r.toplam_puan} XP`")
