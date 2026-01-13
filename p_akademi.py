import streamlit as st
import pandas as pd
import json
import time
import os
import re
import base64
from supabase import create_client, Client

# --- 1. SİBER-ESTETİK TASARIM VE GÖRSEL STANDARTLAR ---
st.set_page_config(
    page_title="Pito Python Akademi", 
    layout="wide", 
    initial_sidebar_state="collapsed"
)

# Tüm görsel şölen ve okunabilirlik mühürleri burada
st.markdown("""
    <style>
    /* 1. ANA TEMA VE SAYFA YAPISI */
    .stApp { 
        background-color: #0E1117 !important; 
        color: #FFFFFF !important; 
    }
    .stApp > header { display: none; }
    
    /* EKRAN ÜSTÜ SIKIŞMA VE GENEL DOLGU */
    .block-container { 
        padding-top: 5rem !important; 
        padding-bottom: 2rem !important;
        padding-left: 5% !important;
        padding-right: 5% !important;
    }

    /* 2. PARLAYAN NEON BAŞLIK */
    .academy-title { 
        font-size: 3.8em; font-weight: 900; text-align: left;
        background: linear-gradient(90deg, #00FF00, #00CCFF); 
        -webkit-background-clip: text; -webkit-text-fill-color: transparent; 
        margin-bottom: 30px; line-height: 1.1;
        filter: drop-shadow(0 0 10px rgba(0, 255, 0, 0.4));
    }

    /* 3. ETİKETLER VE INPUTLAR - GÖRÜNÜRLÜK MÜHRÜ */
    /* st.text_area ve st.number_input etiketleri (Okul No, Kod Editörü vb.) */
    [data-testid="stWidgetLabel"] p {
        color: #00FF00 !important; /* Parlayan Neon Yeşil */
        font-weight: 900 !important;
        font-size: 1.25em !important;
        text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.8);
    }
    
    input, textarea {
        color: #FFFFFF !important;
        background-color: #000000 !important;
        border: 1px solid #3d3d3d !important;
        font-size: 1.1em !important;
    }

    /* 4. TABS (SEKMELER) - KRİSTAL NETLİĞİ */
    .stTabs [data-baseweb="tab-list"] {
        background-color: #1E1E2F !important;
        border-radius: 12px 12px 0 0;
        padding: 10px;
        gap: 15px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 55px !important;
        background-color: #262730 !important;
        border-radius: 8px !important;
        border: 1px solid #3d3d3d !important;
    }
    .stTabs [data-baseweb="tab"] p {
        color: #E0E0E0 !important;
        font-weight: bold !important;
    }
    .stTabs [aria-selected="true"] {
        background-color: #00FF00 !important;
        border: 1px solid #00FF00 !important;
    }
    .stTabs [aria-selected="true"] p {
        color: #000000 !important;
    }

    /* 5. GÖREV KUTUSU - YÜKSEK KONTRAST */
    .gorev-box {
        background-color: #1E1E2F !important;
        border: 2px solid #00CCFF !important; /* Parlak Mavi Çerçeve */
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 25px;
        box-shadow: 0 4px 15px rgba(0, 204, 255, 0.1);
    }
    .gorev-label {
        color: #00CCFF !important; /* Parlak Mavi Etiket */
        font-weight: 900 !important;
        font-size: 1.2em !important;
        text-transform: uppercase;
        display: block;
        margin-bottom: 10px;
    }
    .gorev-text {
        color: #FFFFFF !important; /* Saf Beyaz Görev Metni */
        font-size: 1.1em !important;
        line-height: 1.6;
    }

    /* 6. MODÜL ANLATIMI VE HERO PANEL */
    [data-testid="stExpander"] {
        background-color: #1E1E2F !important;
        border: 1px solid #00FF00 !important;
        border-radius: 12px !important;
        margin-bottom: 25px;
    }
    [data-testid="stExpander"] details summary p {
        color: #00FF00 !important;
        font-weight: 800 !important;
    }
    .anlatim-box {
        background-color: #000000 !important;
        border-radius: 10px; 
        padding: 20px;
        color: #FFFFFF !important; 
        border: 1px solid #30363d;
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
        font-weight: 900 !important;
        margin: 0 !important;
    }

    /* 7. STATUS, CONSOLE VE İLERLEME */
    .progress-label {
        font-size: 0.9em; color: #00FF00; font-weight: bold; margin-bottom: 8px; 
        display: flex; justify-content: space-between;
    }
    .status-bar { 
        display: flex; justify-content: space-between; background-color: #161b22; 
        padding: 18px; border-radius: 15px; border: 1px solid #30363d; margin-bottom: 20px;
    }
    .pito-notu { 
        background-color: #1E1E2F; border-radius: 12px; padding: 22px; 
        border-left: 6px solid #00FF00; margin-top: 15px; color: #E0E0E0; font-style: italic;
    }
    .console-box { 
        background-color: #000000; border-radius: 12px; padding: 18px; 
        font-family: 'Courier New', monospace; color: #00FF00; border: 1px solid #333; margin-top: 10px;
    }
    
    .stButton>button { 
        border-radius: 12px; background-color: #00FF00 !important; color: black !important; font-weight: 800;
        height: 3.8em; border: none !important;
    }
    div.stProgress > div > div > div > div { background-color: #00FF00; }

    /* LİDERLİK KARTLARI */
    .leader-card {
        background: #1E1E2F; padding: 12px; border-radius: 10px; margin-bottom: 10px;
        border: 1px solid #30363d; display: flex; justify-content: space-between; align-items: center;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. SUPABASE BAĞLANTI MOTORU ---
@st.cache_resource
def init_supabase():
    try:
        url = st.secrets["supabase"]["url"]
        key = st.secrets["supabase"]["key"]
        return create_client(url, key)
    except Exception:
        st.error("⚠️ Supabase anahtarları bulunamadı!"); st.stop()

supabase: Client = init_supabase()

# --- 3. YARDIMCI MEKANİZMALAR ---
def kod_normalize_et(kod):
    return re.sub(r'\s+', '', str(kod)).strip().lower()

def pito_notu_uret(mod, ad="Genç Yazılımcı"):
    notlar = {
        "merhaba": f"Selam {ad}! Bugün Python dünyasında hangi kapıları açacağız?",
        "basari": f"Vay canına {ad}! Kodun tertemiz çalıştı. Sonuç aşağıda!",
        "hata": f"Ufak bir yazım kazası {ad}... Python biraz titizdir, bir daha bak.",
        "dusunuyor": f"Hımm, bu görev biraz terletiyor mu? Merak etme, çözüm seni bekliyor.",
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

# --- 4. VERİ YÜKLEME ---
try:
    with open('mufredat.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
        mufredat = data['pito_akademi_mufredat']
except:
    st.error("❌ mufredat.json dosyası eksik veya hatalı!"); st.stop()

# --- 5. SESSION STATE YÖNETİMİ ---
if "user" not in st.session_state: st.session_state.user = None
if "error_count" not in st.session_state: st.session_state.error_count = 0
if "cevap_dogru" not in st.session_state: st.session_state.cevap_dogru = False
if "pito_mod" not in st.session_state: st.session_state.pito_mod = "merhaba"
if "current_code" not in st.session_state: st.session_state.current_code = ""

# --- 6. NAVİGASYON VE İLERLEME MOTORU ---
def ilerleme_kaydet(puan, kod, egz_id, n_id, n_m):
    try:
        yeni_xp = int(st.session_state.user['toplam_puan']) + puan
        r = "🏆 Bilge" if yeni_xp >= 1000 else "🔥 Savaşçı" if yeni_xp >= 500 else "🐍 Pythonist" if yeni_xp >= 200 else "🥚 Çömez"
        
        # Veritabanı Güncelleme
        supabase.table("kullanicilar").update({
            "toplam_puan": yeni_xp, 
            "mevcut_egzersiz": str(n_id), 
            "mevcut_modul": int(n_m), 
            "rutbe": r
        }).eq("ogrenci_no", int(st.session_state.user['ogrenci_no'])).execute()
        
        supabase.table("egzersiz_kayitlari").insert({
            "ogrenci_no": int(st.session_state.user['ogrenci_no']), 
            "egz_id": str(egz_id), 
            "alinan_puan": int(puan), 
            "basarili_kod": str(kod)
        }).execute()
        
        # State Güncelleme
        st.session_state.user.update({"toplam_puan": yeni_xp, "mevcut_egzersiz": str(n_id), "mevcut_modul": int(n_m), "rutbe": r})
        st.session_state.error_count, st.session_state.cevap_dogru, st.session_state.pito_mod, st.session_state.current_code = 0, False, "merhaba", ""
        st.rerun()
    except Exception as e:
        st.error(f"⚠️ Kayıt hatası: {e}")

# --- 7. LİDERLİK TABLOSU ---
def liderlik_tablosu_goster(user_sinif=None):
    st.markdown("<h3 style='text-align:center; color:#00FF00;'>🏆 ONUR KÜRSÜSÜ</h3>", unsafe_allow_html=True)
    t_okul, t_sinif, t_pano = st.tabs(["🌍 Okul Geneli", "📍 Sınıfım", "🏫 Sınıf Ligleri"])
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

# --- 8. ANA UYGULAMA AKIŞI ---
if st.session_state.user is None:
    col_login, col_board = st.columns([2, 1], gap="large")
    with col_login:
        st.markdown('<div class="academy-title">Pito Python<br>Akademi</div>', unsafe_allow_html=True)
        pito_gorseli_yukle("merhaba", size=200)
        numara = st.number_input("Okul Numaran:", step=1, value=0)
        if numara > 0 and st.button("Akademiye Gir 🚀"):
            res = supabase.table("kullanicilar").select("*").eq("ogrenci_no", int(numara)).execute()
            if res.data: st.session_state.user = res.data[0]; st.rerun()
            else: st.warning("⚠️ Numara bulunamadı! Lütfen öğretmenine danış.")
    with col_board: 
        liderlik_tablosu_goster()

else:
    u = st.session_state.user
    col_main, col_side = st.columns([7, 3])
    with col_main:
        m_idx = int(u['mevcut_modul']) - 1
        total_m = len(mufredat)
        
        # Çift İlerleme Çubuğu (Global + Modül)
        st.markdown(f"<div class='progress-label'><span>🎓 Akademi Yolculuğu</span><span>{m_idx + 1} / {total_m} Modül</span></div>", unsafe_allow_html=True)
        st.progress(min((m_idx) / total_m, 1.0) if total_m > 0 else 0)

        if m_idx >= total_m:
            st.balloons(); pito_gorseli_yukle("mezun", size=280)
            st.markdown(f"<h2 style='text-align:center; color:#00FF00;'>🏆 TEBRİKLER {u['ad_soyad'].upper()}!</h2>", unsafe_allow_html=True)
            if st.button("🔄 Akademiyi Baştan Başlat"):
                supabase.table("kullanicilar").update({"toplam_puan": 0, "mevcut_egzersiz": "1.1", "mevcut_modul": 1}).eq("ogrenci_no", u['ogrenci_no']).execute()
                st.session_state.user = None; st.rerun()
        else:
            modul = mufredat[m_idx]
            egz = next((e for e in modul['egzersizler'] if e['id'] == str(u['mevcut_egzersiz'])), modul['egzersizler'][0])
            
            st.markdown(f"<div class='hero-panel'><h3>🚀 {modul['modul_adi']}</h3><p>{u['ad_soyad']} | {u['rutbe']} | {int(u['toplam_puan'])} XP</p></div>", unsafe_allow_html=True)
            
            with st.expander(f"📖 KONU ANLATIMI: {modul['modul_adi']}", expanded=True):
                st.markdown(f"<div class='anlatim-box'>{modul.get('pito_anlatimi', 'İçerik yükleniyor...')}</div>", unsafe_allow_html=True)

            c_idx, t_egz = modul['egzersizler'].index(egz) + 1, len(modul['egzersizler'])
            st.markdown(f"<div class='progress-label'><span>🗺️ Modül Görevleri</span><span>{c_idx} / {t_egz} Görev</span></div>", unsafe_allow_html=True)
            st.progress(c_idx / t_egz)
            
            # GÖREV KUTUSU (YÜKSEK KONTRASTLI BÖLÜM)
            st.markdown(f"""
                <div class='gorev-box'>
                    <span class='gorev-label'>📍 GÖREV {egz['id']}</span>
                    <div class='gorev-text'>{egz['yonerge']}</div>
                </div>
            """, unsafe_allow_html=True)

            p_pot = max(0, 20 - (st.session_state.error_count * 5))
            st.markdown(f'<div class="status-bar"><div>💎 {p_pot} XP</div><div>⚠️ Hata: {st.session_state.error_count}/4</div></div>', unsafe_allow_html=True)
            
            c_p, c_e = st.columns([1, 2])
            with c_p: pito_gorseli_yukle(st.session_state.pito_mod, size=180)
            with c_e:
                if st.session_state.error_count == 1: st.error("🤔 Pito: 'Ufak bir yazım kazası mı?'")
                elif st.session_state.error_count == 2: st.error("🧐 Pito: 'Parantezleri ve tırnakları bir daha say!'")
                elif st.session_state.error_count == 3: st.warning(f"💡 İpucu: {egz['ipucu']}")
                st.markdown(f"<div class='pito-notu'>💬 <b>Pito:</b> {pito_notu_uret(st.session_state.pito_mod, u['ad_soyad'].split()[0])}</div>", unsafe_allow_html=True)

            if not st.session_state.cevap_dogru and st.session_state.error_count < 4:
                # Kod Editörü Başlığı neon yeşili sabitlendi
                k_in = st.text_area("Pito Kod Editörü:", value=egz['sablon'], height=150, key="editor")
                if st.button("Kodu Kontrol Et 🔍"):
                    st.session_state.current_code = k_in
                    if kod_normalize_et(k_in) == kod_normalize_et(egz['dogru_cevap_kodu']):
                        st.session_state.cevap_dogru, st.session_state.pito_mod = True, "basari"
                    else:
                        st.session_state.error_count += 1
                        st.session_state.pito_mod = "hata"
                    st.rerun()
            elif st.session_state.cevap_dogru:
                st.success(f"✅ Harika! +{p_pot} XP Kazandın.")
                st.markdown(f"<div class='console-box'>💻 Çıktı: {egz.get('beklenen_cikti', 'Tamamlandı.')}</div>", unsafe_allow_html=True)
                if st.button("Sonraki Göreve Geç ➡️"):
                    s_idx = modul['egzersizler'].index(egz) + 1
                    if s_idx < len(modul['egzersizler']):
                        n_id, n_m = modul['egzersizler'][s_idx]['id'], u['mevcut_modul']
                    else:
                        n_id, n_m = f"{u['mevcut_modul']+1}.1", u['mevcut_modul'] + 1
                    ilerleme_kaydet(p_pot, st.session_state.current_code, egz['id'], n_id, n_m)
            elif st.session_state.error_count >= 4:
                st.error("🚫 Bu görevden puan kazanılamadı.")
                with st.expander("📖 Pito'nun Çözümü", expanded=True):
                    st.code(egz['cozum'], language="python")
                    st.markdown(f"<div class='console-box'>💻 Beklenen Çıktı: {egz.get('beklenen_cikti', 'Tamamlandı.')}</div>", unsafe_allow_html=True)
                if st.button("Anladım, Sıradaki Göreve Geç ➡️"):
                    s_idx = modul['egzersizler'].index(egz) + 1
                    if s_idx < len(modul['egzersizler']):
                        n_id, n_m = modul['egzersizler'][s_idx]['id'], u['mevcut_modul']
                    else:
                        n_id, n_m = f"{u['mevcut_modul']+1}.1", u['mevcut_modul'] + 1
                    ilerleme_kaydet(0, "Çözüm İncelendi", egz['id'], n_id, n_m)

    with col_side: 
        liderlik_tablosu_goster(u['sinif'])
