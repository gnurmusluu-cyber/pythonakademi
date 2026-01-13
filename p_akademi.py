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
    /* Uygulamanın her modda koyu temada kalmasını zorunlu kılıyoruz (Siber-Estetik için en iyisi) */
    .stApp { 
        background-color: #0E1117 !important; 
        color: #FFFFFF !important; 
    }
    .stApp > header { display: none; }
    
    /* EKRAN ÜSTÜ SIKIŞMA TAMİRİ */
    .block-container { 
        padding-top: 5rem !important; 
        padding-bottom: 2rem !important;
        padding-left: 5% !important;
        padding-right: 5% !important;
    }
    
    /* 2. TABS (SEKMELER) - HER KOŞULDA NET OKUNURLUK */
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
        padding: 0 20px !important;
    }
    .stTabs [data-baseweb="tab"] p {
        color: #B0B0B0 !important; /* Seçili olmayan yazı: Açık Gri */
        font-weight: bold !important;
        font-size: 1em !important;
    }
    .stTabs [aria-selected="true"] {
        background-color: #00FF00 !important; /* Seçili: Parlayan Yeşil */
        border: 1px solid #00FF00 !important;
        box-shadow: 0 0 15px rgba(0, 255, 0, 0.2);
    }
    .stTabs [aria-selected="true"] p {
        color: #000000 !important; /* Seçili Yazı: Siyah */
    }

    /* 3. MODÜL ANLATIMI (EXPANDER) - BEYAZ EKRAN TAMİRİ */
    [data-testid="stExpander"] {
        background-color: #1E1E2F !important;
        border: 1px solid #00FF00 !important;
        border-radius: 12px !important;
        margin-bottom: 20px;
    }
    [data-testid="stExpander"] details summary p {
        color: #00FF00 !important;
        font-weight: 800 !important;
        font-size: 1.1em !important;
    }
    .anlatim-box {
        background-color: #161b22; 
        border-radius: 10px; 
        padding: 20px;
        line-height: 1.7; 
        color: #e6edf3 !important; 
        border-left: 5px solid #00CCFF;
        margin: 10px 0;
    }

    /* 4. KARTLAR VE BAŞLIKLAR */
    .academy-title { 
        font-size: 3.5em; font-weight: 800; text-align: left;
        background: linear-gradient(90deg, #00FF00, #00CCFF); 
        -webkit-background-clip: text; -webkit-text-fill-color: transparent; 
        margin-bottom: 25px;
    }
    .hero-panel { 
        background: linear-gradient(135deg, #1E1E2F 0%, #2D2D44 100%); 
        padding: 20px; border-radius: 15px; border-left: 8px solid #00FF00; 
        margin-bottom: 20px;
    }
    .status-bar { 
        display: flex; justify-content: space-between; background-color: #161b22; 
        padding: 18px; border-radius: 15px; border: 1px solid #30363d; margin-bottom: 20px;
    }
    .pito-notu { 
        background-color: #1E1E2F; border-radius: 12px; padding: 22px; 
        border-left: 6px solid #00FF00; margin-top: 15px; font-style: italic; color: #E0E0E0;
    }
    .console-box { 
        background-color: #000000; border-radius: 0 0 12px 12px; padding: 18px; 
        font-family: 'Courier New', monospace; color: #00FF00; border: 1px solid #333; border-top: none;
    }
    .console-header {
        background-color: #333; color: white; padding: 7px 18px;
        border-radius: 12px 12px 0 0; font-size: 0.85em; font-weight: bold; margin-top: 20px;
    }
    
    /* BUTONLAR */
    .stButton>button { 
        border-radius: 12px; background-color: #00FF00 !important; 
        color: black !important; font-weight: 800; width: 100%; height: 3.8em;
        border: none !important; transition: transform 0.2s;
    }
    .stButton>button:hover { transform: scale(1.02); }

    /* LİDERLİK KARTLARI */
    .leader-card {
        background: #1E1E2F; padding: 12px; border-radius: 10px; margin-bottom: 10px;
        border: 1px solid #30363d; display: flex; justify-content: space-between; align-items: center;
    }
    .champion-class {
        background: linear-gradient(90deg, #FFD700, #FFA500) !important;
        color: black !important; font-weight: bold;
    }
    
    /* Progress Bar */
    div.stProgress > div > div > div > div { background-color: #00FF00; }
    
    /* Input alanları metin rengi sabitleme */
    .stTextArea textarea { color: #FFFFFF !important; background-color: #000000 !important; }
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

# --- 3. FONKSİYONEL MÜHÜRLER ---
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
    else:
        st.warning(f"Görsel bulunamadı: pito_{mod}.gif")

# --- 4. MÜFREDAT YÜKLEME ---
try:
    with open('mufredat.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
        mufredat = data['pito_akademi_mufredat']
except Exception:
    st.error("❌ mufredat.json dosyası eksik veya hatalı!"); st.stop()

# --- 5. SESSION STATE YÖNETİMİ ---
if "user" not in st.session_state: st.session_state.user = None
if "temp_user" not in st.session_state: st.session_state.temp_user = None
if "error_count" not in st.session_state: st.session_state.error_count = 0
if "cevap_dogru" not in st.session_state: st.session_state.cevap_dogru = False
if "pito_mod" not in st.session_state: st.session_state.pito_mod = "merhaba"
if "current_code" not in st.session_state: st.session_state.current_code = ""

# --- 6. LİDERLİK TABLOSU ---
def liderlik_tablosu_goster(user_sinif=None):
    st.markdown("<h3 style='text-align:center; font-size:1.4em; color:#00FF00;'>🏆 ONUR KÜRSÜSÜ</h3>", unsafe_allow_html=True)
    t_okul, t_sinif, t_pano = st.tabs(["🌍 Okul", "📍 Sınıfım", "🏫 Sınıflar"])
    try:
        res = supabase.table("kullanicilar").select("ad_soyad, sinif, toplam_puan").execute()
        df = pd.DataFrame(res.data)
        with t_okul:
            for i, r in enumerate(df.sort_values(by="toplam_puan", ascending=False).head(8).itertuples(), 1):
                e = "🥇" if i==1 else "🥈" if i==2 else "🥉" if i==3 else f"{i}."
                st.markdown(f"<div class='leader-card'><span>{e} {r.ad_soyad}</span><code>{int(r.toplam_puan)} XP</code></div>", unsafe_allow_html=True)
        with t_sinif:
            s_filter = user_sinif if user_sinif else "9-A"
            df_s = df[df['sinif'] == s_filter].sort_values(by="toplam_puan", ascending=False).head(8)
            for i, r in enumerate(df_s.itertuples(), 1):
                st.markdown(f"<div class='leader-card'><span>#{i} {r.ad_soyad}</span><code>{int(r.toplam_puan)} XP</code></div>", unsafe_allow_html=True)
        with t_pano:
            df_p = df.groupby('sinif')['toplam_puan'].sum().sort_values(ascending=False).reset_index()
            for i, r in enumerate(df_p.itertuples(), 1):
                cls = "leader-card champion-class" if i == 1 else "leader-card"
                st.markdown(f"<div class='{cls}'><span>🏆 {i}. {r.sinif}</span><code>{int(r.toplam_puan)} XP</code></div>", unsafe_allow_html=True)
    except: st.write("Tablolar güncelleniyor...")

# --- 7. İLERLEME KAYDET ---
def ilerleme_kaydet(puan, kod, egz_id, n_id, n_m):
    try:
        yeni_xp = int(st.session_state.user['toplam_puan']) + puan
        r = "🏆 Bilge" if yeni_xp >= 1000 else "🔥 Savaşçı" if yeni_xp >= 500 else "🐍 Pythonist" if yeni_xp >= 200 else "🥚 Çömez"
        supabase.table("kullanicilar").update({"toplam_puan": yeni_xp, "mevcut_egzersiz": str(n_id), "mevcut_modul": int(n_m), "rutbe": r}).eq("ogrenci_no", int(st.session_state.user['ogrenci_no'])).execute()
        supabase.table("egzersiz_kayitlari").insert({"ogrenci_no": int(st.session_state.user['ogrenci_no']), "egz_id": str(egz_id), "alinan_puan": int(puan), "basarili_kod": str(kod)}).execute()
        st.session_state.user.update({"toplam_puan": yeni_xp, "mevcut_egzersiz": str(n_id), "mevcut_modul": int(n_m), "rutbe": r})
        st.session_state.error_count, st.session_state.cevap_dogru, st.session_state.pito_mod, st.session_state.current_code = 0, False, "merhaba", ""
        st.rerun()
    except Exception as e: st.error(f"Kayıt Hatası: {e}")

# --- 8. ANA UYGULAMA AKIŞI ---
if st.session_state.user is None:
    col_login, col_board = st.columns([2, 1], gap="large")
    with col_login:
        st.markdown('<div class="academy-title">Pito Python<br>Akademi</div>', unsafe_allow_html=True)
        pito_gorseli_yukle("merhaba", size=200)
        if st.session_state.temp_user is None:
            numara = st.number_input("Okul Numaran:", step=1, value=0)
            if numara > 0 and st.button("Akademiye Gir 🚀"):
                res = supabase.table("kullanicilar").select("*").eq("ogrenci_no", int(numara)).execute()
                if res.data: st.session_state.temp_user = res.data[0]; st.rerun()
                else:
                    st.warning("⚠️ Numara bulunamadı, yeni kayıt oluştur!")
                    y_ad = st.text_input("Ad Soyad:")
                    y_sin = st.selectbox("Sınıfın:", ["9-A", "9-B", "10-A", "10-B", "11-A", "12-A"])
                    if st.button("Kaydı Tamamla 🎓") and y_ad:
                        new_u = {"ogrenci_no": int(numara), "ad_soyad": str(y_ad).strip(), "sinif": y_sin, "toplam_puan": 0, "mevcut_modul": 1, "mevcut_egzersiz": "1.1", "rutbe": "🥚 Çömez"}
                        reg = supabase.table("kullanicilar").insert(new_u).execute()
                        if reg.data: st.session_state.user = reg.data[0]; st.rerun()
        else:
            u_t = st.session_state.temp_user
            st.markdown(f'<div class="pito-notu">👋 <b>Selam {u_t["ad_soyad"]}!</b><br>Seninle devam edelim mi?</div>', unsafe_allow_html=True)
            c1, c2 = st.columns(2)
            if c1.button("Evet, Benim! ✅"): st.session_state.user = u_t; st.session_state.temp_user = None; st.rerun()
            if c2.button("Hayır, Değilim! ❌"): st.session_state.temp_user = None; st.rerun()
    with col_board: liderlik_tablosu_goster()

else:
    u = st.session_state.user
    col_main, col_side = st.columns([7, 3])
    with col_main:
        m_idx = int(u['mevcut_modul']) - 1
        if m_idx >= len(mufredat):
            st.balloons(); pito_gorseli_yukle("mezun", size=280)
            st.markdown(f"<h2 style='text-align:center; color:#00FF00;'>🏆 TEBRİKLER {u['ad_soyad'].upper()}!</h2>", unsafe_allow_html=True)
            if st.button("🔄 Akademiyi Baştan Başlat"):
                supabase.table("kullanicilar").update({"toplam_puan": 0, "mevcut_egzersiz": "1.1", "mevcut_modul": 1}).eq("ogrenci_no", u['ogrenci_no']).execute()
                st.session_state.user = None; st.rerun()
        else:
            modul = mufredat[m_idx]
            egz = next((e for e in modul['egzersizler'] if e['id'] == str(u['mevcut_egzersiz'])), modul['egzersizler'][0])
            
            st.markdown(f"<div class='hero-panel'><h3>🚀 {u['ad_soyad']} | MODÜL {u['mevcut_modul']}</h3><p>{u['rutbe']} • {int(u['toplam_puan'])} XP</p></div>", unsafe_allow_html=True)
            
            with st.expander(f"📖 {modul['modul_adi']} - Pito Anlatımı", expanded=True):
                st.markdown(f"<div class='anlatim-box'>{modul.get('pito_anlatimi', 'Konu içeriği hazırlanıyor...')}</div>", unsafe_allow_html=True)

            c_idx, t_egz = modul['egzersizler'].index(egz) + 1, len(modul['egzersizler'])
            st.progress(c_idx / t_egz)
            p_pot = max(0, 20 - (st.session_state.error_count * 5))
            st.markdown(f'<div class="status-bar"><div>📍 Görev {egz["id"]}</div><div>💎 {p_pot} XP</div><div>⚠️ Hata: {st.session_state.error_count}/4</div></div>', unsafe_allow_html=True)
            
            c_p, c_e = st.columns([1, 2])
            with c_p: pito_gorseli_yukle(st.session_state.pito_mod, size=180)
            with c_e:
                st.info(f"**GÖREV:** {egz['yonerge']}")
                # --- SABİT FEEDBACK ALANI ---
                if st.session_state.error_count == 1: st.error("🤔 Pito: 'Ufak bir yazım kazası mı?'")
                elif st.session_state.error_count == 2: st.error("🧐 Pito: 'Parantezleri ve tırnakları bir daha say!'")
                elif st.session_state.error_count == 3: st.warning(f"💡 İpucu: {egz['ipucu']}")
                st.markdown(f"<div class='pito-notu'>💬 <b>Pito:</b> {pito_notu_uret(st.session_state.pito_mod, u['ad_soyad'].split()[0])}</div>", unsafe_allow_html=True)

            if not st.session_state.cevap_dogru and st.session_state.error_count < 4:
                k_in = st.text_area("Kodunu Yaz:", value=egz['sablon'], height=150, key="editor")
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
                st.markdown("<div class='console-header'>💻 Konsol Çıktısı:</div>", unsafe_allow_html=True)
                st.markdown(f"<div class='console-box'>{egz.get('beklenen_cikti', '> Tamamlandı.')}</div>", unsafe_allow_html=True)
                if st.button("Sıradaki Göreve Geç ➡️"):
                    s_idx = modul['egzersizler'].index(egz) + 1
                    n_id, n_m = (modul['egzersizler'][s_idx]['id'], u['mevcut_modul']) if s_idx < len(modul['egzersizler']) else (f"{m_idx + 2}.1", m_idx + 2)
                    ilerleme_kaydet(p_pot, st.session_state.current_code, egz['id'], n_id, n_m)
            elif st.session_state.error_count >= 4:
                st.error("🚫 Bu görevden puan kazanılamadı.")
                with st.expander("📖 Pito'nun Çözümü", expanded=True):
                    st.code(egz['cozum'], language="python")
                    st.markdown("<div class='console-header'>💻 Beklenen Çıktı:</div>", unsafe_allow_html=True)
                    st.markdown(f"<div class='console-box'>{egz.get('beklenen_cikti', '> Tamamlandı.')}</div>", unsafe_allow_html=True)
                if st.button("Anladım, Sıradaki Göreve Geç ➡️"):
                    s_idx = modul['egzersizler'].index(egz) + 1
                    n_id, n_m = (modul['egzersizler'][s_idx]['id'], u['mevcut_modul']) if s_idx < len(modul['egzersizler']) else (f"{m_idx + 2}.1", m_idx + 2)
                    ilerleme_kaydet(0, "Çözüm İncelendi", egz['id'], n_id, n_m)

    with col_side: liderlik_tablosu_goster(u['sinif'])
