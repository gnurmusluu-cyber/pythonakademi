import streamlit as st
import pandas as pd
import json
import time
import os
import re
import base64
from supabase import create_client, Client

# --- 1. SİBER-BUZ: MUTLAK KARANLIK VE ELEKTRİK MAVİSİ ---
st.set_page_config(
    page_title="Pito Python Akademi", 
    layout="wide", 
    initial_sidebar_state="collapsed"
)

st.markdown("""
    <style>
    /* KÜRESEL SIFIRLAMA */
    html, body, [data-testid="stAppViewContainer"], .stApp {
        background-color: #0E1117 !important;
        color: #E0E0E0 !important;
    }
    .block-container { padding-top: 5rem !important; padding-bottom: 2rem !important; padding-left: 5% !important; padding-right: 5% !important; }

    /* PARLAYAN NEON BAŞLIK */
    .academy-title { 
        font-size: 3.8em !important; font-weight: 900 !important;
        background: linear-gradient(90deg, #00FF00, #00CCFF) !important; 
        -webkit-background-clip: text !important; -webkit-text-fill-color: transparent !important; 
        margin-bottom: 30px !important; line-height: 1.1 !important;
        filter: drop-shadow(0 0 15px rgba(0, 255, 0, 0.5)) !important;
    }

    /* MODÜL İSMİ (HERO PANEL) */
    .hero-panel { 
        background-color: #161b22 !important; padding: 25px !important; border-radius: 15px !important; 
        border: 1px solid #30363d !important; border-left: 8px solid #00CCFF !important; margin-bottom: 25px !important;
    }
    .hero-panel h3 { color: #00CCFF !important; font-weight: 900 !important; margin: 0 !important; -webkit-text-fill-color: #00CCFF !important; }

    /* KOD BLOKLARI VE ÇÖZÜM - ZİFİRİ SİYAH ÜSTÜNE MAVİ */
    [data-testid="stCodeBlock"], code, pre, .stCodeBlock pre {
        background-color: #000000 !important;
        color: #00CCFF !important;
        border: 1px solid #00CCFF !important;
        border-radius: 10px !important;
    }
    [data-testid="stCodeBlock"] span { color: inherit !important; }

    /* EXPANDER (ÇÖZÜM KUTUSU) */
    [data-testid="stExpander"] {
        background-color: #1E1E2F !important;
        border: 1px solid #00CCFF !important;
        border-radius: 12px !important;
    }
    [data-testid="stExpander"] summary p { color: #00CCFF !important; font-weight: 800 !important; }
    [data-testid="stExpander"] div[role="region"] { background-color: #000000 !important; color: #E0E0E0 !important; }

    /* GÖREV KUTUSU */
    .gorev-box {
        background-color: #1E1E2F !important; border: 2px solid #00CCFF !important;
        border-radius: 12px; padding: 22px; margin-bottom: 25px;
    }
    .gorev-label { color: #00CCFF !important; font-weight: 900 !important; font-size: 1.2em !important; display: block; margin-bottom: 12px; }
    .gorev-text { color: #FFFFFF !important; font-size: 1.15em !important; line-height: 1.6; }

    /* ETİKETLER VE INPUTLAR */
    [data-testid="stWidgetLabel"] p { color: #00FF00 !important; font-weight: 900 !important; font-size: 1.25em !important; }
    textarea, input { color: #00CCFF !important; background-color: #000000 !important; border: 1px solid #00FF00 !important; }

    /* LİDERLİK KARTLARI */
    .leader-card { background: #1E1E2F !important; border: 1px solid #30363d !important; border-radius: 12px !important; padding: 12px 18px !important; margin-bottom: 10px !important; display: flex !important; justify-content: space-between !important; align-items: center !important; }
    .rank-badge { padding: 3px 10px !important; border-radius: 20px !important; font-size: 0.75em !important; font-weight: 800 !important; text-transform: uppercase !important; }
    .badge-comez { background-color: #4B4B4B !important; color: #FFFFFF !important; }
    .badge-pythonist { background-color: #00CCFF !important; color: #000000 !important; }
    .badge-savasci { background-color: #FF4B4B !important; color: #FFFFFF !important; }
    .badge-bilge { background-color: #FFD700 !important; color: #000000 !important; box-shadow: 0 0 10px #FFD700; }
    
    .stButton>button { border-radius: 12px; background-color: #00FF00 !important; color: black !important; font-weight: 800; height: 3.8em; }
    div.stProgress > div > div > div > div { background-color: #00FF00 !important; }
    .pito-notu { background-color: #1E1E2F !important; border-radius: 12px !important; padding: 22px !important; border-left: 6px solid #00FF00 !important; color: #E0E0E0 !important; font-style: italic; }
    .console-box { background-color: #000 !important; color: #00CCFF !important; padding: 15px; border-radius: 10px; border: 1px solid #00CCFF; font-family: monospace; margin-top: 10px; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. MOTORLAR ---
@st.cache_resource
def init_supabase():
    return create_client(st.secrets["supabase"]["url"], st.secrets["supabase"]["key"])

supabase: Client = init_supabase()

def kod_normalize_et(kod):
    return re.sub(r'\s+', '', str(kod)).strip().lower()

def pito_notu_uret(mod, ad="Genç Yazılımcı"):
    notlar = {
        "merhaba": f"Selam {ad}! Bugün Python dünyasında hangi kapıları açacağız?",
        "basari": f"Vay canına {ad}! Kodun tertemiz çalıştı. Sonuç aşağıda!",
        "hata": f"Ufak bir yazım kazası {ad}... Python biraz titizdir, bir daha bak.",
        "mezun": f"İnanılmaz! Artık gerçek bir Python Bilgesisin!"
    }
    return notlar.get(mod, notlar["merhaba"])

# --- 3. SESSION STATE ---
if "user" not in st.session_state: st.session_state.user = None
if "error_count" not in st.session_state: st.session_state.error_count = 0
if "cevap_dogru" not in st.session_state: st.session_state.cevap_dogru = False
if "pito_mod" not in st.session_state: st.session_state.pito_mod = "merhaba"
if "current_code" not in st.session_state: st.session_state.current_code = ""

# --- 4. NAVİGASYON VE İLERLEME ---
def ilerleme_kaydet(puan, kod, egz_id, n_id, n_m):
    yeni_xp = int(st.session_state.user['toplam_puan']) + puan
    r = "🏆 Bilge" if yeni_xp >= 1000 else "🔥 Savaşçı" if yeni_xp >= 500 else "🐍 Pythonist" if yeni_xp >= 200 else "🥚 Çömez"
    supabase.table("kullanicilar").update({"toplam_puan": yeni_xp, "mevcut_egzersiz": str(n_id), "mevcut_modul": int(n_m), "rutbe": r}).eq("ogrenci_no", int(st.session_state.user['ogrenci_no'])).execute()
    supabase.table("egzersiz_kayitlari").insert({"ogrenci_no": int(st.session_state.user['ogrenci_no']), "egz_id": str(egz_id), "alinan_puan": int(puan), "basarili_kod": str(kod)}).execute()
    st.session_state.user.update({"toplam_puan": yeni_xp, "mevcut_egzersiz": str(n_id), "mevcut_modul": int(n_m), "rutbe": r})
    st.session_state.error_count, st.session_state.cevap_dogru, st.session_state.pito_mod, st.session_state.current_code = 0, False, "merhaba", ""
    st.rerun()

# --- 5. LİDERLİK TABLOSU ---
def liderlik_tablosu_goster(user_sinif=None):
    st.markdown("<h3 style='text-align:center; color:#00FF00;'>🏆 ONUR KÜRSÜSÜ</h3>", unsafe_allow_html=True)
    t_okul, t_sinif, t_pano = st.tabs(["🌍 Okul", "📍 Sınıfım", "🏫 Ligler"])
    def rütbe_stili(r):
        if "Bilge" in r: return "badge-bilge"
        if "Savaşçı" in r: return "badge-savasci"
        if "Pythonist" in r: return "badge-pythonist"
        return "badge-comez"
    try:
        res = supabase.table("kullanicilar").select("ad_soyad, sinif, toplam_puan, rutbe").execute()
        df = pd.DataFrame(res.data)
        with t_okul:
            for i, r in enumerate(df.sort_values(by="toplam_puan", ascending=False).head(8).itertuples(), 1):
                st.markdown(f"<div class='leader-card'><div><b>{i}. {r.ad_soyad}</b> <br><span class='rank-badge {rütbe_stili(r.rutbe)}'>{r.rutbe}</span></div><code>{int(r.toplam_puan)} XP</code></div>", unsafe_allow_html=True)
    except: st.write("Yükleniyor...")

# --- 6. ANA PROGRAM AKIŞI ---
# (Giriş ekranı ve mufredat yükleme bölümleri önceki sürümle aynıdır)

if st.session_state.user:
    u = st.session_state.user
    # ... (Müfredat ve egzersiz seçimi)
    
    # --- HATA YÖNETİM SİSTEMİ (V74.0 GÜNCELLEMESİ) ---
    if not st.session_state.cevap_dogru:
        # 1. ve 2. Hata Durumu: Sadece mesaj
        if st.session_state.error_count == 1 or st.session_state.error_count == 2:
            st.error(f"🚨 Pito Notu: {egz.get('hata_mesaji', 'Ufak bir hata var, kodu tekrar incele!')}")
        
        # 3. Hata Durumu: İpucu
        elif st.session_state.error_count == 3:
            st.warning(f"💡 Pito İpucu: {egz['ipucu']}")
            
        # 4. Hata ve Üzeri: Kesin Çözüm ve Çıktı
        elif st.session_state.error_count >= 4:
            st.error("🚫 Maksimum hata sayısına ulaştın. İşte çözüm yolu:")
            with st.expander("📖 Pito'nun Kesin Çözümü", expanded=True):
                st.code(egz['cozum'], language="python")
                st.markdown(f"<div class='console-box'>💻 Beklenen Konsol Çıktısı:<br>> {egz.get('beklenen_cikti', 'İşlem Başarılı.')}</div>", unsafe_allow_html=True)
            if st.button("Anladım, Sıradaki Göreve Geç ➡️"):
                # Navigasyon mantığı (s_idx kontrolüyle)
                pass # ilerleme_kaydet(0, ...)
        
        # Kod Giriş Alanı (Sadece 4 hatadan az ise gösterilir veya çözümle beraber kalabilir)
        if st.session_state.error_count < 4:
            k_in = st.text_area("Pito Kod Editörü:", value=egz['sablon'], height=150, key="editor")
            if st.button("Kodu Kontrol Et 🔍"):
                if kod_normalize_et(k_in) == kod_normalize_et(egz['dogru_cevap_kodu']):
                    st.session_state.cevap_dogru, st.session_state.pito_mod = True, "basari"
                    st.rerun()
                else:
                    st.session_state.error_count += 1
                    st.session_state.pito_mod = "hata"
                    st.rerun()

    else: # Doğru Cevap Durumu
        st.success(f"✅ Harika! +{max(0, 20 - (st.session_state.error_count * 5))} XP Kazandın.")
        st.markdown(f"<div class='console-box'>💻 Çıktı: {egz.get('beklenen_cikti', 'Tamamlandı.')}</div>", unsafe_allow_html=True)
        if st.button("Sonraki Göreve Geç ➡️"):
            pass # ilerleme_kaydet(puan, ...)
