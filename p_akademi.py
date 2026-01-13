import streamlit as st
import pandas as pd
import json
import os
import re
import base64
from supabase import create_client, Client

# --- 1. SİBER-ZIRH: AGRESİF GÖRSEL MÜHÜRLEME ---
st.set_page_config(
    page_title="Pito Python Akademi", 
    layout="wide", 
    initial_sidebar_state="collapsed"
)

st.markdown("""
    <style>
    /* KÜRESEL KARANLIK MOD ZORLAMASI */
    html, body, [data-testid="stAppViewContainer"], .stApp {
        background-color: #0E1117 !important;
        color: #E0E0E0 !important;
    }
    .stApp > header { display: none; }
    .block-container { 
        padding-top: 5rem !important; 
        padding-bottom: 2rem !important;
        padding-left: 5% !important;
        padding-right: 5% !important;
    }

    /* PARLAYAN NEON BAŞLIK */
    .academy-title { 
        font-size: 3.8em !important; font-weight: 900 !important;
        background: linear-gradient(90deg, #00FF00, #00CCFF) !important; 
        -webkit-background-clip: text !important; -webkit-text-fill-color: transparent !important; 
        margin-bottom: 30px !important; line-height: 1.1 !important;
        filter: drop-shadow(0 0 15px rgba(0, 255, 0, 0.4)) !important;
    }

    /* MODÜL İSMİ (HERO PANEL) - ELEKTRİK MAVİSİ */
    .hero-panel { 
        background-color: #161b22 !important; 
        padding: 25px !important; 
        border-radius: 15px !important; 
        border: 1px solid #30363d !important;
        border-left: 8px solid #00CCFF !important; 
        margin-bottom: 25px !important;
    }
    .hero-panel h3 { 
        color: #00CCFF !important; font-weight: 900 !important; margin: 0 !important;
        -webkit-text-fill-color: #00CCFF !important;
    }

    /* GÖREV KUTUSU - YÜKSEK KONTRAST */
    .gorev-box {
        background-color: #1E1E2F !important;
        border: 2px solid #00CCFF !important;
        border-radius: 12px; padding: 22px; margin-bottom: 25px;
    }
    .gorev-label { color: #00CCFF !important; font-weight: 900; font-size: 1.25em; display: block; margin-bottom: 12px; }
    .gorev-text { color: #FFFFFF !important; font-size: 1.15em; line-height: 1.6; }

    /* EXPANDER VE KOD BLOKLARI (BEYAZ EKRAN TAMİRİ) */
    [data-testid="stExpander"] {
        background-color: #1E1E2F !important;
        border: 1px solid #00CCFF !important;
        border-radius: 12px !important;
        margin-bottom: 25px;
    }
    .anlatim-box {
        background-color: #000000 !important; border-radius: 10px; padding: 20px;
        color: #FFFFFF !important; border: 1px solid #30363d; border-left: 5px solid #00CCFF;
    }
    [data-testid="stCodeBlock"], .stCodeBlock pre, code {
        background-color: #000000 !important; color: #00CCFF !important;
        border: 1px solid #333 !important;
    }

    /* ETİKETLER VE INPUTLAR */
    [data-testid="stWidgetLabel"] p { color: #00FF00 !important; font-weight: 900; font-size: 1.3em; }
    textarea, input { color: #00CCFF !important; background-color: #000000 !important; border: 1px solid #00FF00 !important; }

    /* LİDERLİK KARTLARI VE RÜTBE NİŞANLARI */
    .leader-card {
        background: #1E1E2F !important; border: 1px solid #30363d !important;
        border-radius: 12px !important; padding: 12px 18px !important; margin-bottom: 10px !important;
        display: flex !important; justify-content: space-between !important; align-items: center !important;
    }
    .rank-badge { padding: 3px 10px !important; border-radius: 20px !important; font-size: 0.75em !important; font-weight: 800 !important; text-transform: uppercase !important; }
    .badge-comez { background-color: #4B4B4B !important; color: #FFFFFF !important; }
    .badge-pythonist { background-color: #00CCFF !important; color: #000000 !important; }
    .badge-savasci { background-color: #FF4B4B !important; color: #FFFFFF !important; }
    .badge-bilge { background-color: #FFD700 !important; color: #000000 !important; box-shadow: 0 0 10px #FFD700; }

    /* MEZUNİYET DİPLOMASI */
    .diploma-box {
        text-align: center; padding: 50px; background: #161b22; 
        border-radius: 30px; border: 5px solid #FFD700;
        box-shadow: 0 0 30px rgba(255, 215, 0, 0.3); margin-top: 20px;
    }
    .diploma-title { color: #FFD700 !important; font-size: 3.5em !important; font-weight: 900 !important; }
    .diploma-name { color: #FFFFFF !important; font-size: 2.5em !important; margin: 20px 0; border-bottom: 2px solid #333; display: inline-block; padding: 0 50px; }

    /* BUTONLAR VE İLERLEME */
    .stButton>button { border-radius: 12px; background-color: #00FF00 !important; color: black !important; font-weight: 800; height: 3.8em; }
    div.stProgress > div > div > div > div { background-color: #00FF00 !important; }
    .progress-label { font-size: 0.95em; color: #00FF00 !important; font-weight: 900; display: flex; justify-content: space-between; margin-bottom: 8px; }
    .pito-notu { background-color: #1E1E2F !important; border-radius: 12px; padding: 22px; border-left: 6px solid #00FF00; color: #E0E0E0; font-style: italic; }
    .console-box { background-color: #000 !important; color: #00CCFF !important; padding: 15px; border-radius: 10px; border: 1px solid #00CCFF; font-family: monospace; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. SUPABASE BAĞLANTI MOTORU ---
@st.cache_resource
def init_supabase():
    try:
        return create_client(st.secrets["supabase"]["url"], st.secrets["supabase"]["key"])
    except:
        st.error("⚠️ Supabase anahtarları bulunamadı!"); st.stop()

supabase: Client = init_supabase()

# --- 3. YARDIMCI MOTORLAR ---
def kod_normalize_et(kod):
    return re.sub(r'\s+', '', str(kod)).strip().lower()

def pito_notu_uret(mod, ad="Genç Yazılımcı"):
    notlar = {
        "merhaba": f"Selam {ad}! Bugün hangi Python kapısını açacağız?",
        "basari": f"Vay canına {ad}! Kodun tertemiz çalıştı. Sonuç aşağıda!",
        "hata": f"Ufak bir yazım kazası {ad}... Python biraz titizdir, bir daha bak.",
        "mezun": f"İnanılmaz! Artık gerçek bir Python Bilgesisin!"
    }
    return notlar.get(mod, notlar["merhaba"])

def pito_gorseli_yukle(mod, size=210):
    path = os.path.join(os.path.dirname(__file__), "assets", f"pito_{mod}.gif")
    if os.path.exists(path):
        with open(path, "rb") as f:
            encoded = base64.b64encode(f.read()).decode()
        st.markdown(f'<img src="data:image/gif;base64,{encoded}" width="{size}">', unsafe_allow_html=True)

# --- 4. VERİ YÜKLEME ---
try:
    with open('mufredat.json', 'r', encoding='utf-8') as f:
        mufredat = json.load(f)['pito_akademi_mufredat']
except:
    st.error("❌ mufredat.json dosyası bulunamadı!"); st.stop()

# --- 5. SESSION STATE YÖNETİMİ ---
if "user" not in st.session_state: st.session_state.user = None
if "error_count" not in st.session_state: st.session_state.error_count = 0
if "cevap_dogru" not in st.session_state: st.session_state.cevap_dogru = False
if "pito_mod" not in st.session_state: st.session_state.pito_mod = "merhaba"
if "current_code" not in st.session_state: st.session_state.current_code = ""

# --- 6. NAVİGASYON MOTORU (TAKILMA ÖNLEYİCİ) ---
def ilerleme_kaydet(puan, kod, egz_id, n_id, n_m):
    try:
        yeni_xp = int(st.session_state.user['toplam_puan']) + puan
        r = "🏆 Bilge" if yeni_xp >= 1000 else "🔥 Savaşçı" if yeni_xp >= 500 else "🐍 Pythonist" if yeni_xp >= 200 else "🥚 Çömez"
        
        supabase.table("kullanicilar").update({
            "toplam_puan": yeni_xp, "mevcut_egzersiz": str(n_id), "mevcut_modul": int(n_m), "rutbe": r
        }).eq("ogrenci_no", int(st.session_state.user['ogrenci_no'])).execute()
        
        supabase.table("egzersiz_kayitlari").insert({
            "ogrenci_no": int(st.session_state.user['ogrenci_no']), 
            "egz_id": str(egz_id), "alinan_puan": int(puan), "basarili_kod": str(kod)
        }).execute()
        
        st.session_state.user.update({"toplam_puan": yeni_xp, "mevcut_egzersiz": str(n_id), "mevcut_modul": int(n_m), "rutbe": r})
        st.session_state.error_count, st.session_state.cevap_dogru, st.session_state.pito_mod, st.session_state.current_code = 0, False, "merhaba", ""
        st.rerun()
    except Exception as e:
        st.error(f"⚠️ Kayıt hatası: {e}")

# --- 7. LİDERLİK TABLOSU ---
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
            df_o = df.sort_values(by="toplam_puan", ascending=False).head(8)
            for i, r in enumerate(df_o.itertuples(), 1):
                st.markdown(f"<div class='leader-card'><div><b>{i}. {r.ad_soyad}</b> <br><span class='rank-badge {rütbe_stili(r.rutbe)}'>{r.rutbe}</span></div><code>{int(r.toplam_puan)} XP</code></div>", unsafe_allow_html=True)
    except: st.write("Tablolar yükleniyor...")

# --- 8. ANA UYGULAMA ---
if st.session_state.user is None:
    col_login, col_board = st.columns([2, 1], gap="large")
    with col_login:
        st.markdown('<div class="academy-title">Pito Python<br>Akademi</div>', unsafe_allow_html=True)
        pito_gorseli_yukle("merhaba", size=200)
        numara = st.number_input("Okul Numaran:", step=1, value=0)
        if numara > 0 and st.button("Akademiye Gir 🚀"):
            res = supabase.table("kullanicilar").select("*").eq("ogrenci_no", int(numara)).execute()
            if res.data: st.session_state.user = res.data[0]; st.rerun()
            else: st.warning("⚠️ Numara bulunamadı!")
    with col_board: liderlik_tablosu_goster()

else:
    u = st.session_state.user
    m_idx = int(u['mevcut_modul']) - 1
    total_m = len(mufredat)

    # --- MEZUNİYET EKRANI ---
    if m_idx >= total_m:
        st.balloons(); st.snow()
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            pito_gorseli_yukle("mezun", size=350)
            st.markdown(f"""<div class="diploma-box"><div class="diploma-title">BİLGE SERTİFİKASI</div><div class="diploma-name">{u['ad_soyad'].upper()}</div><div class="diploma-text">Nusaybin Süleyman Bölünmez Anadolu Lisesi <br> Pito Python Akademisi'ni Başarıyla Tamamladı.</div><h3 style="color:#FFD700; margin-top:20px;">Toplam XP: {int(u['toplam_puan'])}</h3></div>""", unsafe_allow_html=True)
            if st.button("🔄 Akademiyi Sıfırla"):
                supabase.table("kullanicilar").update({"toplam_puan": 0, "mevcut_egzersiz": "1.1", "mevcut_modul": 1, "rutbe": "🥚 Çömez"}).eq("ogrenci_no", u['ogrenci_no']).execute()
                st.session_state.user = None; st.rerun()
    
    # --- EĞİTİM AKIŞI ---
    else:
        modul = mufredat[m_idx]
        egz = next((e for e in modul['egzersizler'] if e['id'] == str(u['mevcut_egzersiz'])), modul['egzersizler'][0])
        
        # Çift İlerleme Çubuğu
        st.markdown(f"<div class='progress-label'><span>🎓 Akademi Yolculuğu</span><span>Modül {m_idx + 1} / {total_m}</span></div>", unsafe_allow_html=True)
        st.progress(min((m_idx) / total_m, 1.0))

        col_main, col_side = st.columns([7, 3])
        with col_main:
            st.markdown(f"<div class='hero-panel'><h3>🚀 {modul['modul_adi']}</h3><p>{u['ad_soyad']} | {u['rutbe']} | {int(u['toplam_puan'])} XP</p></div>", unsafe_allow_html=True)
            
            with st.expander(f"📖 KONU ANLATIMI: {modul['modul_adi']}", expanded=True):
                st.markdown(f"<div class='anlatim-box'>{modul.get('pito_anlatimi', 'Yükleniyor...')}</div>", unsafe_allow_html=True)

            # Modül İlerleme
            c_idx, t_egz = modul['egzersizler'].index(egz) + 1, len(modul['egzersizler'])
            st.markdown(f"<div class='progress-label'><span>🗺️ Modül Görevleri</span><span>{c_idx} / {t_egz} Görev</span></div>", unsafe_allow_html=True)
            st.progress(c_idx / t_egz)
            
            st.markdown(f"<div class='gorev-box'><span class='gorev-label'>📍 GÖREV {egz['id']}</span><div class='gorev-text'>{egz['yonerge']}</div></div>", unsafe_allow_html=True)

            # V74.0 Kademeli Hata Sistemi
            p_pot = max(0, 20 - (st.session_state.error_count * 5))
            st.markdown(f'<div class="status-bar"><div>💎 {p_pot} XP</div><div>⚠️ Hata: {st.session_state.error_count}/4</div></div>', unsafe_allow_html=True)
            
            c_p, c_e = st.columns([1, 2])
            with c_p: pito_gorseli_yukle(st.session_state.pito_mod, size=180)
            with c_e:
                if st.session_state.error_count in [1, 2]: st.error(f"🚨 Pito: {egz.get('hata_mesaji', 'Kodu tekrar incele!')}")
                elif st.session_state.error_count == 3: st.warning(f"💡 İpucu: {egz['ipucu']}")
                st.markdown(f"<div class='pito-notu'>💬 <b>Pito:</b> {pito_notu_uret(st.session_state.pito_mod, u['ad_soyad'].split()[0])}</div>", unsafe_allow_html=True)

            if not st.session_state.cevap_dogru and st.session_state.error_count < 4:
                k_in = st.text_area("Pito Kod Editörü:", value=egz['sablon'], height=150, key="editor")
                if st.button("Kodu Kontrol Et 🔍"):
                    st.session_state.current_code = k_in
                    if kod_normalize_et(k_in) == kod_normalize_et(egz['dogru_cevap_kodu']):
                        st.session_state.cevap_dogru, st.session_state.pito_mod = True, "basari"
                    else: st.session_state.error_count += 1; st.session_state.pito_mod = "hata"
                    st.rerun()
            elif st.session_state.cevap_dogru:
                st.success(f"✅ Harika! +{p_pot} XP")
                st.markdown(f"<div class='console-box'>💻 Çıktı: {egz.get('beklenen_cikti', 'Tamamlandı.')}</div>", unsafe_allow_html=True)
                if st.button("Sonraki Göreve Geç ➡️"):
                    s_idx = modul['egzersizler'].index(egz) + 1
                    if s_idx < len(modul['egzersizler']): n_id, n_m = modul['egzersizler'][s_idx]['id'], u['mevcut_modul']
                    else: n_id, n_m = f"{u['mevcut_modul']+1}.1", u['mevcut_modul'] + 1
                    ilerleme_kaydet(p_pot, st.session_state.current_code, egz['id'], n_id, n_m)
            elif st.session_state.error_count >= 4:
                with st.expander("📖 Pito'nun Kesin Çözümü", expanded=True):
                    st.code(egz['cozum'], language="python")
                    st.markdown(f"<div class='console-box'>💻 Beklenen Konsol Çıktısı:<br>> {egz.get('beklenen_cikti', 'İşlem Başarılı.')}</div>", unsafe_allow_html=True)
                if st.button("Anladım, Sıradaki Göreve Geç ➡️"):
                    s_idx = modul['egzersizler'].index(egz) + 1
                    if s_idx < len(modul['egzersizler']): n_id, n_m = modul['egzersizler'][s_idx]['id'], u['mevcut_modul']
                    else: n_id, n_m = f"{u['mevcut_modul']+1}.1", u['mevcut_modul'] + 1
                    ilerleme_kaydet(0, "Çözüm İncelendi", egz['id'], n_id, n_m)

        with col_side: liderlik_tablosu_goster(u['sinif'])
