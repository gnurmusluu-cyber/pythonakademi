import streamlit as st
import pandas as pd
import json
import time
import os
import re
from datetime import datetime
from streamlit_gsheets import GSheetsConnection

# --- 1. KONFİGÜRASYON VE SİBER TASARIM ---
st.set_page_config(page_title="Pito Python Akademi", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
    .stApp { background-color: #0E1117; color: #FFFFFF; }
    .hero-panel { background: linear-gradient(90deg, #1E1E2F 0%, #2D2D44 100%); padding: 25px; border-radius: 15px; border-left: 8px solid #00FF00; margin-bottom: 25px; box-shadow: 0 4px 15px rgba(0,255,0,0.2); }
    .status-bar { display: flex; justify-content: space-between; background-color: #262730; padding: 12px; border-radius: 10px; border: 1px solid #4B4B4B; margin-bottom: 15px; }
    .console-box { background-color: #1E1E1E; border: 1px solid #333; border-radius: 0 0 10px 10px; padding: 15px; font-family: 'Courier New', Courier, monospace; color: #00FF00; }
    .console-header { background-color: #333; padding: 5px 15px; border-radius: 10px 10px 0 0; font-size: 12px; color: #AAA; font-weight: bold; }
    .sampiyon-kart { background: linear-gradient(45deg, #FFD700, #FFA500); padding: 20px; border-radius: 12px; text-align: center; color: black; margin-bottom: 20px; font-weight: bold; box-shadow: 0 0 15px #FFD700; }
    .pito-notu { background-color: #1E1E2F; border-radius: 10px; padding: 15px; border-left: 5px solid #00FF00; margin-top: 10px; font-style: italic; color: #E0E0E0; }
    .stButton>button { border-radius: 10px; background-color: #00FF00 !important; color: black !important; font-weight: bold; width: 100%; height: 3.2em; transition: 0.3s; }
    .stTextArea>div>div>textarea { background-color: #1E1E1E; color: #00FF00; font-family: 'Courier New', Courier, monospace; font-size: 16px; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. YARDIMCI MOTORLAR ---

def kod_normalize_et(kod):
    """Boşluk ve parantez farklarını yok sayarak esnek kontrol sağlar."""
    return re.sub(r'\s+', '', str(kod)).strip().lower()

def pito_notu_uret(mod, ad="Genç Yazılımcı"):
    notlar = {
        "merhaba": f"Selam {ad}! Bugün Python dünyasında hangi kapıları açacağız?",
        "basari": f"Vay canına {ad}! Kodun tertemiz çalıştı. Çıktıyı aşağıya bıraktım.",
        "hata": f"Ufak bir yazım kazası {ad}... Python biraz titizdir, bir daha bak istersen.",
        "dusunuyor": f"Hımm, bu görev biraz terletiyor mu? Merak etme, çözüm ve çıktı seni bekliyor.",
        "mezun": f"İnanılmaz! Nusaybin'in gururu {ad} artık bir Python Bilgesi!"
    }
    return notlar.get(mod, notlar["merhaba"])

def pito_gorseli_yukle(mod):
    base_path = os.path.dirname(os.path.abspath(__file__))
    img_path = os.path.join(base_path, "assets", f"pito_{mod}.gif")
    if os.path.exists(img_path):
        st.image(img_path, use_container_width=True)

@st.cache_data(ttl=60)
def veri_oku_akilli(url):
    try: return conn.read(spreadsheet=url, ttl=60)
    except: return None

# --- 3. BAĞLANTILAR VE MÜFREDAT ---
KULLANICILAR_URL = "https://docs.google.com/spreadsheets/d/1lat8rO2qm9QnzEUYlzC_fypG3cRkGlJfSfTtwNvs318/edit#gid=0"
KAYITLAR_URL = "https://docs.google.com/spreadsheets/d/14QoNr4FHZhSaUDUU-DDQEfNFHMo5Ge5t5lyDgqGRJ3k/edit#gid=0"
conn = st.connection("gsheets", type=GSheetsConnection)

try:
    with open('mufredat.json', 'r', encoding='utf-8') as f:
        mufredat = json.load(f)
except Exception as e:
    st.error(f"❌ Müfredat dosyası yüklenemedi: {e}")
    st.stop()

# --- 4. SESSION STATE ---
if "user" not in st.session_state: st.session_state.user = None
if "error_count" not in st.session_state: st.session_state.error_count = 0
if "cevap_dogru" not in st.session_state: st.session_state.cevap_dogru = False
if "pito_mod" not in st.session_state: st.session_state.pito_mod = "merhaba"
if "last_code" not in st.session_state: st.session_state.last_code = ""

# --- 5. İLERLEME KAYDETME MOTORU ---
def ilerleme_kaydet(puan, kod, egz_id, m_id, n_id, n_m):
    try:
        df_u = conn.read(spreadsheet=KULLANICILAR_URL, ttl=0)
        u_idx = df_u[df_u['ogrenci_no'] == st.session_state.user['ogrenci_no']].index[0]
        yeni_xp = int(float(df_u.at[u_idx, 'toplam_puan'])) + puan
        df_u.at[u_idx, 'toplam_puan'], df_u.at[u_idx, 'mevcut_egzersiz'], df_u.at[u_idx, 'mevcut_modul'] = yeni_xp, str(n_id), int(float(n_m))
        
        if yeni_xp >= 1000: r = "🏆 Bilge"
        elif yeni_xp >= 500: r = "🔥 Savaşçı"
        elif yeni_xp >= 200: r = "🐍 Pythonist"
        else: r = "🥚 Çömez"
        df_u.at[u_idx, 'rutbe'] = r
        
        conn.update(spreadsheet=KULLANICILAR_URL, data=df_u)
        df_k = conn.read(spreadsheet=KAYITLAR_URL, ttl=0)
        yeni_log = pd.DataFrame([{"kayit_id": f"{st.session_state.user['ogrenci_no']}_{egz_id}", "ogrenci_no": int(st.session_state.user['ogrenci_no']), "alinan_puan": int(puan), "basarili_kod": kod, "tarih": datetime.now().strftime("%Y-%m-%d %H:%M")}])
        conn.update(spreadsheet=KAYITLAR_URL, data=pd.concat([df_k, yeni_log], ignore_index=True))
        
        st.session_state.user = df_u.iloc[u_idx].to_dict()
        st.session_state.error_count, st.session_state.cevap_dogru, st.session_state.pito_mod, st.session_state.last_code = 0, False, "merhaba", ""
        st.cache_data.clear(); st.rerun()
    except Exception as e: st.error(f"Kayıt Hatası: {e}")

# --- 6. ANA AKIŞ ---
if st.session_state.user is None:
    st.title("🐍 Pito Python Akademi")
    pito_gorseli_yukle("merhaba")
    numara = st.number_input("Öğrenci Numarası:", step=1, value=0)
    if numara > 0:
        df_u = conn.read(spreadsheet=KULLANICILAR_URL, ttl=0)
        u_data = df_u[df_u['ogrenci_no'] == numara]
        if not u_data.empty:
            if st.button("Giriş Yap 🚀"):
                st.session_state.user = u_data.iloc[0].to_dict(); st.rerun()
        else:
            st.warning("🧐 Kayıt bulunamadı, aramıza katıl!")
            c1, c2 = st.columns(2)
            with c1: y_ad = st.text_input("Ad Soyad:")
            with c2: y_sinif = st.selectbox("Sınıfın:", ["9-A", "9-B", "10-A", "10-B", "11-A", "12-A"])
            if st.button("Kaydol ve Başla 🎓") and y_ad:
                y_og = pd.DataFrame([{"ogrenci_no": int(numara), "ad_soyad": y_ad, "sinif": y_sinif, "toplam_puan": 0, "mevcut_modul": 1, "mevcut_egzersiz": "1.1", "rutbe": "🥚 Çömez"}])
                conn.update(spreadsheet=KULLANICILAR_URL, data=pd.concat([df_u, y_og], ignore_index=True))
                st.session_state.user = y_og.iloc[0].to_dict(); st.rerun()
else:
    u = st.session_state.user
    col_main, col_leader = st.columns([7, 3])

    with col_main:
        m_idx = int(float(u['mevcut_modul'])) - 1
        if m_idx >= len(mufredat['pito_akademi_mufredat']):
            st.balloons(); pito_gorseli_yukle("mezun"); st.success("🏆 AKADEMİ BİTTİ!"); st.stop()
        
        modul = mufredat['pito_akademi_mufredat'][m_idx]
        egz_liste = modul['egzersizler']
        egz = next((e for e in egz_liste if e['id'] == str(u['mevcut_egzersiz'])), egz_liste[0])

        # Hero Header ve İlerleme
        st.markdown(f"<div class='hero-panel'><h3>🚀 {u['ad_soyad']} | {u['sinif']}</h3><p>{u['rutbe']} • {int(float(u['toplam_puan']))} XP</p></div>", unsafe_allow_html=True)
        sira = egz_liste.index(egz) + 1
        st.write(f"📊 **Modül İlerlemesi:** {sira}/{len(egz_liste)}")
        st.progress(sira / len(egz_liste))

        # Görev Bilgi Çubuğu
        p_pot = max(0, 20 - (st.session_state.error_count * 5))
        st.markdown(f"""
            <div class="status-bar">
                <div style="color: #00FF00; font-weight: bold;">📍 Modül {u['mevcut_modul']} | Görev {egz['id']}</div>
                <div style="color: #FFD700; font-weight: bold;">💎 Kazanılacak: {p_pot} XP</div>
                <div style="color: #FF4B4B; font-weight: bold;">⚠️ Hatalar: {st.session_state.error_count} / 4</div>
            </div>
        """, unsafe_allow_html=True)

        c_p, c_e = st.columns([1, 2])
        with c_p: pito_gorseli_yukle(st.session_state.pito_mod)
        with c_e:
            st.info(f"**GÖREV {egz['id']}:**\n{egz['yonerge']}")
            st.markdown(f"<div class='pito-notu'>💬 <b>Pito:</b> {pito_notu_uret(st.session_state.pito_mod, u['ad_soyad'].split()[0])}</div>", unsafe_allow_html=True)
            if st.session_state.error_count == 1: st.error("🤫 Yazımı kontrol et!")
            elif st.session_state.error_count == 2: st.error("🧐 Bir şeyler eksik!")
            elif st.session_state.error_count == 3: st.warning(f"💡 İpucu: {egz['ipucu']}")

        if not st.session_state.cevap_dogru and st.session_state.error_count < 4:
            k_in = st.text_area("Kodunu Yaz:", value=egz['sablon'], height=200, key="editor")
            if st.button("Kontrol Et"):
                st.session_state.last_code = k_in
                if kod_normalize_et(k_in) == kod_normalize_et(egz['dogru_cevap_kodu']):
                    st.session_state.cevap_dogru, st.session_state.pito_mod = True, "basari"; st.rerun()
                else:
                    st.session_state.error_count += 1
                    st.session_state.pito_mod = "hata" if st.session_state.error_count < 4 else "dusunuyor"; st.rerun()
        
        elif st.session_state.cevap_dogru:
            st.success(f"🌟 +{p_pot} XP Kazandın!")
            # --- JSON'DAN ÇIKTI ÇEKME (BAŞARI) ---
            st.markdown("<div class='console-header'>💻 Kodunun Çıktısı:</div>", unsafe_allow_html=True)
            st.markdown(f"<div class='console-box'>{egz.get('cikti', '> Çıktı bulunamadı.')}</div>", unsafe_allow_html=True)
            
            n_id, n_m = (egz_liste[sira]['id'], u['mevcut_modul']) if sira < len(egz_liste) else (f"{m_idx + 2}.1", m_idx + 2)
            if st.button("Sonraki Göreve Geç ➡️"): ilerleme_kaydet(p_pot, st.session_state.last_code, egz['id'], u['mevcut_modul'], n_id, n_m)
        
        elif st.session_state.error_count >= 4:
            st.error("🚫 Kilitlendi.")
            with st.expander("📖 Çözümü ve Beklenen Çıktıyı İncele", expanded=True):
                st.code(egz['cozum'], language="python")
                # --- JSON'DAN ÇIKTI ÇEKME (ÇÖZÜM) ---
                st.markdown("<div style='color:#00FF00; font-family:monospace; margin-top:10px;'>🚀 Beklenen Çıktı:</div>", unsafe_allow_html=True)
                st.markdown(f"<div style='background-color:#111; padding:10px; border-radius:5px; border:1px dashed #555;'>{egz.get('cikti', '> Beklenen çıktı tanımlanmamış.')}</div>", unsafe_allow_html=True)
            
            n_id, n_m = (egz_liste[sira]['id'], u['mevcut_modul']) if sira < len(egz_liste) else (f"{m_idx + 2}.1", m_idx + 2)
            if st.button("Anladım, Sıradaki ➡️"): ilerleme_kaydet(0, "Çözüm İncelendi", egz['id'], u['mevcut_modul'], n_id, n_m)

    with col_leader:
        st.markdown("<h3 style='text-align:center;'>🏆 ONUR KÜRSÜSÜ</h3>", unsafe_allow_html=True)
        df_all = veri_oku_akilli(KULLANICILAR_URL)
        if df_all is not None:
            df_all['toplam_puan'] = pd.to_numeric(df_all['toplam_puan'], errors='coerce').fillna(0).astype(int)
            s_an = df_all.groupby('sinif').agg(xp=('toplam_puan','sum'), sayi=('ogrenci_no','count'))
            s_an['ort'] = (s_an['xp'] / s_an['sayi']).round(1)
            s_an = s_an.sort_values(by='ort', ascending=False)
            st.markdown(f"<div class='sampiyon-kart'>⭐ ŞAMPİYON SINIF ⭐<br><span style='font-size:24px;'>{s_an.index[0]}</span><br>{s_an.iloc[0]['ort']} XP Ort.</div>", unsafe_allow_html=True)
            t1, t2 = st.tabs(["👥 Sınıfım", "🏫 Okul (Top 10)"])
            with t1:
                sinif_df = df_all[df_all['sinif'] == u['sinif']].sort_values(by='toplam_puan', ascending=False).head(10)
                for i, r in enumerate(sinif_df.itertuples(), 1): st.markdown(f"**{i}.** {r.ad_soyad} • `{r.toplam_puan} XP`")
            with t2:
                okul_df = df_all.sort_values(by='toplam_puan', ascending=False).head(10)
                for i, r in enumerate(okul_df.itertuples(), 1):
                    p = "🥇" if i==1 else "🥈" if i==2 else "🥉" if i==3 else f"**{i}.**"
                    st.markdown(f"{p} {r.ad_soyad} ({r.sinif}) • `{r.toplam_puan} XP`")
