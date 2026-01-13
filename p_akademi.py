import streamlit as st
import pandas as pd
import json
import time
import os
import re
import base64
from supabase import create_client, Client

# --- 1. SİBER-ESTETİK TASARIM VE EVRENSEL GÖRÜNÜM ---
st.set_page_config(
    page_title="Pito Python Akademi", 
    layout="wide", 
    initial_sidebar_state="collapsed"
)

st.markdown("""
    <style>
    /* 1. ANA TEMA VE SAYFA YAPISI */
    .stApp { 
        background-color: #0E1117 !important; 
        color: #FFFFFF !important; 
    }
    .stApp > header { display: none; }
    
    /* SAYFA ÜSTÜNDEKİ SIKIŞMAYI ÖNLEYEN DÜZENLEME */
    .block-container { 
        padding-top: 5rem !important; 
        padding-bottom: 2rem !important;
        padding-left: 5% !important;
        padding-right: 5% !important;
    }

    /* 2. GÖREV KUTUSU (CUSTOM BOX) - YÜKSEK KONTRAST TAMİRİ */
    .gorev-box {
        background-color: #1E1E2F !important;
        border: 2px solid #00CCFF !important; /* Mavi Çerçeve */
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 20px;
        box-shadow: 0 4px 15px rgba(0, 204, 255, 0.1);
    }
    .gorev-label {
        color: #00CCFF !important; /* Parlak Mavi Yazı */
        font-weight: 900 !important;
        font-size: 1.1em !important;
        text-transform: uppercase;
        letter-spacing: 1px;
        display: block;
        margin-bottom: 8px;
    }
    .gorev-text {
        color: #FFFFFF !important; /* Beyaz Metin */
        font-size: 1.05em !important;
        line-height: 1.5;
    }

    /* 3. ETİKETLER VE INPUTLAR - GÖRÜNÜRLÜK MÜHRÜ */
    /* st.text_area ve st.number_input etiketleri */
    [data-testid="stWidgetLabel"] p {
        color: #00FF00 !important; /* Parlayan Neon Yeşil */
        font-weight: 900 !important;
        font-size: 1.2em !important;
    }
    
    input, textarea {
        color: #FFFFFF !important;
        background-color: #000000 !important;
        border: 1px solid #3d3d3d !important;
    }

    /* 4. TABS (SEKMELER) */
    .stTabs [data-baseweb="tab-list"] {
        background-color: #1E1E2F !important;
        border-radius: 12px 12px 0 0;
        padding: 10px;
    }
    .stTabs [data-baseweb="tab"] p {
        color: #E0E0E0 !important;
        font-weight: bold !important;
    }
    .stTabs [aria-selected="true"] {
        background-color: #00FF00 !important;
    }
    .stTabs [aria-selected="true"] p {
        color: #000000 !important;
    }

    /* 5. MODÜL ANLATIMI VE HERO PANEL */
    [data-testid="stExpander"] {
        background-color: #1E1E2F !important;
        border: 1px solid #00FF00 !important;
        border-radius: 12px !important;
    }
    [data-testid="stExpander"] details summary p {
        color: #00FF00 !important;
        font-weight: 800 !important;
    }
    .anlatim-box {
        background-color: #000000 !important;
        border-radius: 10px; 
        padding: 20px;
        color: #e6edf3 !important; 
        border-left: 5px solid #00CCFF;
    }

    .hero-panel { 
        background: #161b22 !important; 
        padding: 20px; 
        border-radius: 15px; 
        border-left: 8px solid #00FF00; 
        margin-bottom: 20px;
        border: 1px solid #30363d;
    }
    .hero-panel h3 {
        color: #00FF00 !important;
        font-weight: 800 !important;
    }

    /* 6. STATUS VE CONSOLE */
    .status-bar { 
        display: flex; justify-content: space-between; background-color: #161b22; 
        padding: 18px; border-radius: 15px; border: 1px solid #30363d; margin-bottom: 20px;
    }
    .pito-notu { 
        background-color: #1E1E2F; border-radius: 12px; padding: 22px; 
        border-left: 6px solid #00FF00; margin-top: 15px; color: #E0E0E0;
    }
    .console-box { 
        background-color: #000000; border-radius: 0 0 12px 12px; padding: 18px; 
        font-family: 'Courier New', monospace; color: #00FF00; border: 1px solid #333;
    }
    
    /* BUTONLAR VE İLERLEME */
    .stButton>button { 
        border-radius: 12px; background-color: #00FF00 !important; color: black !important; font-weight: 800;
    }
    div.stProgress > div > div > div > div { background-color: #00FF00; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. MOTORLAR VE VERİ YÜKLEME ---
@st.cache_resource
def init_supabase():
    try:
        return create_client(st.secrets["supabase"]["url"], st.secrets["supabase"]["key"])
    except:
        st.error("Supabase Hatası!"); st.stop()

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

def pito_gorseli_yukle(mod, size=210):
    path = os.path.join(os.path.dirname(__file__), "assets", f"pito_{mod}.gif")
    if os.path.exists(path):
        with open(path, "rb") as f:
            data = f.read()
            encoded = base64.b64encode(data).decode()
        st.markdown(f'<img src="data:image/gif;base64,{encoded}" width="{size}">', unsafe_allow_html=True)

try:
    with open('mufredat.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
        mufredat = data['pito_akademi_mufredat']
except:
    st.error("mufredat.json okunamadı!"); st.stop()

if "user" not in st.session_state: st.session_state.user = None
if "error_count" not in st.session_state: st.session_state.error_count = 0
if "cevap_dogru" not in st.session_state: st.session_state.cevap_dogru = False
if "pito_mod" not in st.session_state: st.session_state.pito_mod = "merhaba"
if "current_code" not in st.session_state: st.session_state.current_code = ""

# --- 3. LİDERLİK TABLOSU ---
def liderlik_tablosu_goster(user_sinif=None):
    st.markdown("<h3 style='text-align:center; color:#00FF00;'>🏆 ONUR KÜRSÜSÜ</h3>", unsafe_allow_html=True)
    t_okul, t_sinif, t_pano = st.tabs(["🌍 Okul", "📍 Sınıfım", "🏫 Sınıflar"])
    try:
        res = supabase.table("kullanicilar").select("ad_soyad, sinif, toplam_puan").execute()
        df = pd.DataFrame(res.data)
        with t_okul:
            for i, r in enumerate(df.sort_values(by="toplam_puan", ascending=False).head(8).itertuples(), 1):
                st.markdown(f"<div class='leader-card'><span>{i}. {r.ad_soyad}</span><code>{int(r.toplam_puan)} XP</code></div>", unsafe_allow_html=True)
        with t_sinif:
            s_filter = user_sinif if user_sinif else "9-A"
            df_s = df[df['sinif'] == s_filter].sort_values(by="toplam_puan", ascending=False).head(8)
            for i, r in enumerate(df_s.itertuples(), 1):
                st.markdown(f"<div class='leader-card'><span>#{i} {r.ad_soyad}</span><code>{int(r.toplam_puan)} XP</code></div>", unsafe_allow_html=True)
        with t_pano:
            df_p = df.groupby('sinif')['toplam_puan'].sum().sort_values(ascending=False).reset_index()
            for i, r in enumerate(df_p.itertuples(), 1):
                st.markdown(f"<div class='leader-card'><span>🏆 {i}. {r.sinif}</span><code>{int(r.toplam_puan)} XP</code></div>", unsafe_allow_html=True)
    except: st.write("Yükleniyor...")

# --- 4. ANA PROGRAM ---
if st.session_state.user is None:
    col_login, col_board = st.columns([2, 1], gap="large")
    with col_login:
        st.markdown('<div class="academy-title">Pito Python<br>Akademi</div>', unsafe_allow_html=True)
        pito_gorseli_yukle("merhaba", size=200)
        numara = st.number_input("Okul Numaran:", step=1, value=0)
        if numara > 0 and st.button("Akademiye Gir 🚀"):
            res = supabase.table("kullanicilar").select("*").eq("ogrenci_no", int(numara)).execute()
            if res.data: st.session_state.user = res.data[0]; st.rerun()
            else: st.warning("Numara bulunamadı!")
    with col_board: liderlik_tablosu_goster()

else:
    u = st.session_state.user
    col_main, col_side = st.columns([7, 3])
    with col_main:
        m_idx = int(u['mevcut_modul']) - 1
        total_m = len(mufredat)
        st.markdown(f"<div class='progress-label'><span>🎓 Akademi Yolculuğu</span><span>{m_idx + 1} / {total_m} Modül</span></div>", unsafe_allow_html=True)
        st.progress((m_idx) / total_m if total_m > 0 else 0)

        if m_idx < total_m:
            modul = mufredat[m_idx]
            egz = next((e for e in modul['egzersizler'] if e['id'] == str(u['mevcut_egzersiz'])), modul['egzersizler'][0])
            st.markdown(f"<div class='hero-panel'><h3>🚀 {modul['modul_adi']}</h3><p>{u['ad_soyad']} | {u['rutbe']} | {int(u['toplam_puan'])} XP</p></div>", unsafe_allow_html=True)
            
            with st.expander(f"📖 KONU ANLATIMI", expanded=True):
                st.markdown(f"<div class='anlatim-box'>{modul.get('pito_anlatimi', 'Yükleniyor...')}</div>", unsafe_allow_html=True)

            c_idx, t_egz = modul['egzersizler'].index(egz) + 1, len(modul['egzersizler'])
            st.markdown(f"<div class='progress-label'><span>🗺️ Modül Görevleri</span><span>{c_idx} / {t_egz} Görev</span></div>", unsafe_allow_html=True)
            st.progress(c_idx / t_egz)
            
            # --- ÖZEL GÖREV KUTUSU (TAMİR EDİLEN BÖLÜM) ---
            st.markdown(f"""
                <div class='gorev-box'>
                    <span class='gorev-label'>📍 GÖREV {egz['id']}</span>
                    <div class='gorev-text'>{egz['yonerge']}</div>
                </div>
            """, unsafe_allow_html=True)

            p_pot = max(0, 20 - (st.session_state.error_count * 5))
            st.markdown(f'<div class="status-bar"><div>💎 Potansiyel: {p_pot} XP</div><div>⚠️ Hata: {st.session_state.error_count}/4</div></div>', unsafe_allow_html=True)
            
            c_p, c_e = st.columns([1, 2])
            with c_p: pito_gorseli_yukle(st.session_state.pito_mod, size=180)
            with c_e:
                if st.session_state.error_count == 1: st.error("🤔 Pito: 'Ufak bir yazım kazası mı?'")
                elif st.session_state.error_count == 3: st.warning(f"💡 İpucu: {egz['ipucu']}")
                st.markdown(f"<div class='pito-notu'>💬 <b>Pito:</b> {pito_notu_uret(st.session_state.pito_mod, u['ad_soyad'].split()[0])}</div>", unsafe_allow_html=True)

            if not st.session_state.cevap_dogru and st.session_state.error_count < 4:
                k_in = st.text_area("Pito Kod Editörü:", value=egz['sablon'], height=150, key="editor")
                if st.button("Kodu Kontrol Et 🔍"):
                    st.session_state.current_code = k_in
                    if kod_normalize_et(k_in) == kod_normalize_et(egz['dogru_cevap_kodu']):
                        st.session_state.cevap_dogru, st.session_state.pito_mod = True, "basari"
                    else: st.session_state.error_count += 1; st.rerun()
            elif st.session_state.cevap_dogru:
                st.success(f"✅ Harika! +{p_pot} XP")
                st.markdown("<div class='console-box'>💻 Çıktı: " + egz.get('beklenen_cikti', 'Tamamlandı.') + "</div>", unsafe_allow_html=True)
                if st.button("Sıradaki ➡️"):
                    s_idx = modul['egzersizler'].index(egz) + 1
                    n_id, n_m = (modul['egzersizler'][s_idx]['id'], u['mevcut_modul']) if s_idx < len(modul['egzersizler']) else (f"{m_idx + 2}.1", m_idx + 2)
                    # (ilerleme_kaydet fonksiyonu burada çağrılacak)
            elif st.session_state.error_count >= 4:
                st.error("🚫 Puan kazanılamadı.")
                with st.expander("📖 Pito'nun Çözümü", expanded=True): st.code(egz['cozum'])
                if st.button("Anladım, Geç ➡️"): pass

    with col_side: liderlik_tablosu_goster(u['sinif'])
