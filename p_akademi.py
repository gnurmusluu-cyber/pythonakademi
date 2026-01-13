import streamlit as st
import pandas as pd
import json
import os
import re
import base64
from supabase import create_client, Client

# --- 1. SİBER-ZIRH: GÖRSEL ANAYASA ---
st.set_page_config(page_title="Pito Python Akademi", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
    html, body, [data-testid="stAppViewContainer"], .stApp { background-color: #0E1117 !important; color: #E0E0E0 !important; }
    .stApp > header { display: none; }
    .block-container { padding-top: 4rem !important; padding-left: 5% !important; padding-right: 5% !important; }

    /* NEON BAŞLIKLAR (YEŞİL-SARI ÜSTÜNE SİYAH) */
    .academy-title { font-size: 3.5em !important; font-weight: 900 !important; background: linear-gradient(90deg, #ADFF2F, #00CCFF) !important; -webkit-background-clip: text !important; -webkit-text-fill-color: transparent !important; margin-bottom: 20px !important; }
    .hero-panel { background-color: #ADFF2F !important; padding: 20px !important; border-radius: 12px !important; margin-bottom: 20px !important; border: 2px solid #FFFFFF !important; box-shadow: 0 0 15px rgba(173, 255, 47, 0.3) !important;}
    .hero-panel h3, .hero-panel p { color: #000000 !important; font-weight: 950 !important; margin: 0 !important; text-transform: uppercase; }

    /* ÇİFT İLERLEME ÇUBUĞU */
    .progress-label { font-size: 0.9em; color: #ADFF2F; font-weight: 900; display: flex; justify-content: space-between; margin-bottom: 2px; margin-top: 10px; }
    div.stProgress > div > div > div > div { background-color: #ADFF2F !important; }

    /* GÖREV KUTUSU VE KONSOL */
    .gorev-box { background-color: #1E1E2F !important; border: 2px solid #00CCFF !important; border-radius: 12px; padding: 22px; margin-bottom: 20px; }
    .gorev-label { color: #00CCFF !important; font-weight: 900; font-size: 1.25em; display: block; margin-bottom: 10px; }
    .gorev-text { color: #FFFFFF !important; font-size: 1.15em !important; line-height: 1.6; }
    .console-box { background-color: #000000 !important; color: #00CCFF !important; padding: 15px; border-radius: 10px; border: 1px solid #00CCFF; font-family: monospace; margin-top: 10px; }

    /* RÜTBE NİŞANLARI */
    .rank-badge { padding: 4px 12px !important; border-radius: 20px !important; font-size: 0.7em !important; font-weight: 800 !important; text-transform: uppercase !important; border: 1px solid #000; display: inline-block; }
    .badge-comez { background-color: #4B4B4B !important; color: #FFFFFF !important; }
    .badge-pythonist { background-color: #00CCFF !important; color: #000000 !important; }
    .badge-savasci { background-color: #FF4B4B !important; color: #FFFFFF !important; }
    .badge-bilge { background-color: #FFD700 !important; color: #000000 !important; box-shadow: 0 0 10px #FFD700; }

    /* LİDERLİK KARTI */
    .leader-card { background: #1E1E2F !important; border: 1px solid #30363d !important; border-radius: 10px !important; padding: 10px 15px !important; margin-bottom: 8px !important; display: flex !important; justify-content: space-between !important; align-items: center !important; }

    /* EXPANDER VE TABS */
    [data-testid="stExpander"] { background-color: #1E1E2F !important; border: 2px solid #ADFF2F !important; border-radius: 12px !important; margin-bottom: 15px; }
    [data-testid="stExpander"] summary { background-color: #ADFF2F !important; border-radius: 10px 10px 0 0 !important; color: #000000 !important; }
    [data-testid="stExpander"] summary p { color: #000000 !important; font-weight: 900 !important; margin: 0 !important; }
    .stTabs [data-baseweb="tab-list"] { background-color: #1E1E2F !important; border-radius: 12px; padding: 5px; }
    .stTabs [data-baseweb="tab"] p { color: #ADFF2F !important; font-weight: bold !important; }
    .stTabs [aria-selected="true"] { background-color: #ADFF2F !important; border-radius: 8px; }
    .stTabs [aria-selected="true"] p { color: #000000 !important; font-weight: 900 !important; }

    /* INPUT VE BUTONLAR */
    [data-testid="stWidgetLabel"] p { color: #ADFF2F !important; font-weight: 900; }
    textarea, input { color: #00CCFF !important; background-color: #000000 !important; border: 1px solid #ADFF2F !important; }
    .stButton>button { border-radius: 12px; background-color: #ADFF2F !important; color: black !important; font-weight: 900; height: 3.5em; width: 100%; }
    .pito-notu { background-color: #1E1E2F !important; border-radius: 12px; padding: 20px; border-left: 6px solid #ADFF2F; color: #E0E0E0; font-style: italic; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. MOTORLAR ---
@st.cache_resource
def init_supabase():
    try: return create_client(st.secrets["supabase"]["url"], st.secrets["supabase"]["key"])
    except: st.error("Supabase Bağlantısı Eksik!"); st.stop()

supabase: Client = init_supabase()
def kod_normalize_et(kod): return re.sub(r'\s+', '', str(kod)).strip().lower()

def rütbe_bilgisi(puan):
    if puan >= 1000: return "🏆 Bilge", "badge-bilge"
    if puan >= 500: return "🔥 Savaşçı", "badge-savasci"
    if puan >= 200: return "🐍 Pythonist", "badge-pythonist"
    return "🥚 Çömez", "badge-comez"

def pito_gorseli_yukle(mod, size=180):
    path = os.path.join(os.path.dirname(__file__), "assets", f"pito_{mod}.gif")
    if os.path.exists(path):
        with open(path, "rb") as f: encoded = base64.b64encode(f.read()).decode()
        st.markdown(f'<img src="data:image/gif;base64,{encoded}" width="{size}">', unsafe_allow_html=True)

# --- 3. SESSION STATE ---
keys = ["user", "temp_user", "show_reg", "error_count", "cevap_dogru", "pito_mod", "current_code"]
for k in keys:
    if k not in st.session_state:
        st.session_state[k] = None if k in ["user", "temp_user"] else (False if k in ["show_reg", "cevap_dogru"] else (0 if k == "error_count" else ("merhaba" if k == "pito_mod" else "")))

# --- 4. LİDERLİK TABLOSU ---
def liderlik_tablosu_goster(user_sinif=None):
    st.markdown("<h3 style='text-align:center; color:#ADFF2F;'>🏆 ONUR KÜRSÜSÜ</h3>", unsafe_allow_html=True)
    t1, t2, t3 = st.tabs(["🌍 Okul", "📍 Sınıfım", "🏫 Ligler"])
    try:
        res = supabase.table("kullanicilar").select("*").execute()
        df = pd.DataFrame(res.data)
        with t1:
            for i, r in enumerate(df.sort_values(by="toplam_puan", ascending=False).head(8).itertuples(), 1):
                r_ad, r_cls = rütbe_bilgisi(r.toplam_puan)
                st.markdown(f"<div class='leader-card'><div><b>{i}. {r.ad_soyad}</b> <br><span class='rank-badge {r_cls}'>{r_ad}</span></div><code>{int(r.toplam_puan)} XP</code></div>", unsafe_allow_html=True)
        with t2:
            s_f = user_sinif if user_sinif else "9-A"
            df_s = df[df['sinif'] == s_f].sort_values(by="toplam_puan", ascending=False).head(8)
            for i, r in enumerate(df_s.itertuples(), 1):
                r_ad, r_cls = rütbe_bilgisi(r.toplam_puan)
                st.markdown(f"<div class='leader-card'><div><b>#{i} {r.ad_soyad}</b> <br><span class='rank-badge {r_cls}'>{r_ad}</span></div><code>{int(r.toplam_puan)} XP</code></div>", unsafe_allow_html=True)
        with t3:
            df_p = df.groupby('sinif')['toplam_puan'].sum().sort_values(ascending=False).reset_index()
            for i, r in enumerate(df_p.itertuples(), 1):
                st.markdown(f"<div class='leader-card'><span>🏆 {i}. {r.sinif}</span><code>{int(r.toplam_puan)} XP</code></div>", unsafe_allow_html=True)
    except: st.write("Yükleniyor...")

# --- 5. İLERLEME KAYDI ---
def ilerleme_kaydet(puan, kod, egz_id, n_id, n_m):
    yeni_xp = int(st.session_state.user['toplam_puan']) + puan
    r_ad, _ = rütbe_bilgisi(yeni_xp)
    supabase.table("kullanicilar").update({"toplam_puan": yeni_xp, "mevcut_egzersiz": str(n_id), "mevcut_modul": int(n_m), "rutbe": r_ad}).eq("ogrenci_no", int(st.session_state.user['ogrenci_no'])).execute()
    supabase.table("egzersiz_kayitlari").insert({"ogrenci_no": int(st.session_state.user['ogrenci_no']), "egz_id": str(egz_id), "alinan_puan": int(puan), "basarili_kod": str(kod)}).execute()
    st.session_state.user.update({"toplam_puan": yeni_xp, "mevcut_egzersiz": str(n_id), "mevcut_modul": int(n_m), "rutbe": r_ad})
    st.session_state.error_count, st.session_state.cevap_dogru, st.session_state.pito_mod, st.session_state.current_code = 0, False, "merhaba", ""
    st.rerun()

# --- 6. ANA PROGRAM AKIŞI ---
try:
    with open('mufredat.json', 'r', encoding='utf-8') as f:
        mufredat = json.load(f)['pito_akademi_mufredat']
except: st.error("mufredat.json dosyası eksik!"); st.stop()

if st.session_state.user is None:
    col_l, col_r = st.columns([2, 1], gap="large")
    with col_l:
        st.markdown('<div class="academy-title">Pito Python Akademi</div>', unsafe_allow_html=True)
        pito_gorseli_yukle("merhaba")
        if not st.session_state.show_reg and st.session_state.temp_user is None:
            num = st.number_input("Okul Numaran:", step=1, value=0)
            if num > 0 and st.button("Akademiye Gir 🚀"):
                res = supabase.table("kullanicilar").select("*").eq("ogrenci_no", int(num)).execute()
                if res.data: st.session_state.temp_user = res.data[0]; st.rerun()
                else: st.session_state.user_num = int(num); st.session_state.show_reg = True; st.rerun()
        elif st.session_state.show_reg:
            st.markdown(f"<div class='pito-notu'>👋 Hoş geldin! {st.session_state.user_num} numarasını ilk kez görüyorum. Kaydını yapalım!</div>", unsafe_allow_html=True)
            name = st.text_input("Adın Soyadın:")
            sınıf = st.selectbox("Sınıfın:", ["9-A","9-B","10-A","10-B","11-A","11-B","12-A","12-B"])
            if st.button("Kaydı Tamamla ✨"):
                new_u = {"ogrenci_no": st.session_state.user_num, "ad_soyad": name, "sinif": sınıf, "toplam_puan": 0, "mevcut_egzersiz": "1.1", "mevcut_modul": 1, "rutbe": "🥚 Çömez"}
                supabase.table("kullanicilar").insert(new_u).execute(); st.session_state.user = new_u; st.session_state.show_reg = False; st.rerun()
        elif st.session_state.temp_user:
            st.markdown(f"<div class='pito-notu'>👋 Selam {st.session_state.temp_user['ad_soyad']}! Bu sen misin arkadaşım?</div>", unsafe_allow_html=True)
            c1, c2 = st.columns(2)
            if c1.button("✅ Evet, Benim!"): st.session_state.user = st.session_state.temp_user; st.session_state.temp_user = None; st.rerun()
            if c2.button("❌ Hayır, Değilim"): st.session_state.temp_user = None; st.rerun()
    with col_r: liderlik_tablosu_goster()

else:
    u = st.session_state.user
    m_idx = int(u['mevcut_modul']) - 1
    total_m = len(mufredat)

    # --- ÇİFT İLERLEME ÇUBUĞU (EN ÜSTTE) ---
    st.markdown(f"<div class='progress-label'><span>🎓 Akademi Yolculuğu</span><span>Modül {m_idx + 1} / {total_m}</span></div>", unsafe_allow_html=True)
    st.progress(min((m_idx) / total_m, 1.0) if total_m > 0 else 0)

    if m_idx >= total_m:
        st.balloons(); pito_gorseli_yukle("mezun", size=350)
        st.markdown("<div class='hero-panel'><h3>🏆 TEBRİKLER BİLGE!</h3><p>Akademiyi başarıyla bitirdin arkadaşım!</p></div>", unsafe_allow_html=True)
    else:
        modul = mufredat[m_idx]
        egz = next((e for e in modul['egzersizler'] if e['id'] == str(u['mevcut_egzersiz'])), modul['egzersizler'][0])
        c_i, t_i = modul['egzersizler'].index(egz) + 1, len(modul['egzersizler'])
        st.markdown(f"<div class='progress-label'><span>🗺️ Modül Görevleri</span><span>{c_i} / {t_i} Görev</span></div>", unsafe_allow_html=True)
        st.progress(c_i / t_i)

        cl, cr = st.columns([7, 3])
        with cl:
            r_ad, r_cls = rütbe_bilgisi(u['toplam_puan'])
            st.markdown(f"<div class='hero-panel'><h3>🚀 {modul['modul_adi']}</h3><p>{u['ad_soyad']} | <span class='rank-badge'>{r_ad}</span> | {int(u['toplam_puan'])} XP</p></div>", unsafe_allow_html=True)
            with st.expander("📖 KONU ANLATIMI", expanded=True): st.markdown(f"<div style='background:#000; padding:15px; border-radius:10px;'>{modul.get('pito_anlatimi', '...')}</div>", unsafe_allow_html=True)
            
            p_xp = max(0, 20 - (st.session_state.error_count * 5))
            st.markdown(f'<div style="background:#161b22; padding:12px; border-radius:12px; margin-bottom:15px; border: 1px solid #ADFF2F; color: #ADFF2F; font-weight:bold;">💎 {p_xp} XP | ⚠️ Hata: {st.session_state.error_count}/4</div>', unsafe_allow_html=True)

            # --- PİTO'NUN YENİ (ESKİ) KONUMU VE GERİ BİLDİRİM ---
            col_p, col_n = st.columns([1, 2])
            with col_p: pito_gorseli_yukle(st.session_state.pito_mod)
            with col_n:
                ad_k = u['ad_soyad'].split()[0]
                if st.session_state.error_count in [1, 2]: st.error(f"🚨 Pito: {ad_k}, bu senin {st.session_state.error_count}. hatan arkadaşım!"); st.session_state.pito_mod = "hata"
                elif st.session_state.error_count == 3: st.warning(f"💡 İpucu: {egz['ipucu']}"); st.session_state.pito_mod = "hata"
                elif st.session_state.error_count >= 4: 
                    st.error("🚫 Bu görevden puan kazanılamadı!"); st.session_state.pito_mod = "dusunuyor"
                st.markdown(f"<div class='pito-notu'>💬 <b>Pito:</b> {ad_k}, pes etmek yok arkadaşım!</div>", unsafe_allow_html=True)

            if not st.session_state.cevap_dogru and st.session_state.error_count < 4:
                st.markdown(f"<div class='gorev-box'><span class='gorev-label'>📍 GÖREV {egz['id']}</span><div class='gorev-text'>{egz['yonerge']}</div></div>", unsafe_allow_html=True)
                k_i = st.text_area("Pito Kod Editörü:", value=egz['sablon'], height=150)
                if st.button("Kontrol Et 🔍"):
                    st.session_state.current_code = k_i
                    if kod_normalize_et(k_i) == kod_normalize_et(egz['dogru_cevap_kodu']): st.session_state.cevap_dogru, st.session_state.pito_mod = True, "basari"
                    else: st.session_state.error_count += 1; st.session_state.pito_mod = "hata" if st.session_state.error_count < 4 else "dusunuyor"
                    st.rerun()
            elif st.session_state.cevap_dogru:
                st.success(f"✅ Harika bildin arkadaşım! +{p_xp} XP")
                st.markdown(f"<div class='console-box'>💻 Senin Çıktın:<br>> {egz.get('beklenen_cikti', '...')}</div>", unsafe_allow_html=True)
                if st.button("Sonraki Göreve Geç ➡️"):
                    s_idx = modul['egzersizler'].index(egz) + 1
                    n_id, n_m = (modul['egzersizler'][s_idx]['id'], u['mevcut_modul']) if s_idx < len(modul['egzersizler']) else (f"{u['mevcut_modul']+1}.1", u['mevcut_modul'] + 1)
                    ilerleme_kaydet(p_xp, st.session_state.current_code, egz['id'], n_id, n_m)
            elif st.session_state.error_count >= 4:
                with st.expander("📖 PİTO'NUN KESİN ÇÖZÜMÜ", expanded=True):
                    st.code(egz['cozum'], language="python")
                    st.markdown(f"<div class='console-box'>💻 Beklenen Çıktı:<br>> {egz.get('beklenen_cikti', '...')}</div>", unsafe_allow_html=True)
                if st.button("Sıradaki Göreve Geç ➡️"):
                    s_idx = modul['egzersizler'].index(egz) + 1
                    n_id, n_m = (modul['egzersizler'][s_idx]['id'], u['mevcut_modul']) if s_idx < len(modul['egzersizler']) else (f"{u['mevcut_modul']+1}.1", u['mevcut_modul'] + 1)
                    ilerleme_kaydet(0, "Çözüm İncelendi", egz['id'], n_id, n_m)

        with cr: liderlik_tablosu_goster(u['sinif'])
