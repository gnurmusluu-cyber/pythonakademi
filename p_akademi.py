import streamlit as st
import pandas as pd
import json
import time
import os
import re
import io
import sys
from contextlib import redirect_stdout
from datetime import datetime
from streamlit_gsheets import GSheetsConnection

# --- 1. SİBER TASARIM AYARLARI ---
st.set_page_config(page_title="Pito Python Akademi", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
    .stApp { background-color: #0E1117; color: #FFFFFF; }
    .hero-panel { background: linear-gradient(90deg, #1E1E2F 0%, #2D2D44 100%); padding: 25px; border-radius: 15px; border-left: 8px solid #00FF00; margin-bottom: 25px; box-shadow: 0 4px 15px rgba(0,255,0,0.2); }
    .status-bar { display: flex; justify-content: space-between; background-color: #262730; padding: 12px; border-radius: 10px; border: 1px solid #4B4B4B; margin-bottom: 15px; }
    .console-box { background-color: #1E1E1E; border: 1px solid #333; border-radius: 0 0 10px 10px; padding: 15px; font-family: 'Courier New', Courier, monospace; color: #00FF00; }
    .console-header { background-color: #333; padding: 5px 15px; border-radius: 10px 10px 0 0; font-size: 12px; color: #AAA; font-weight: bold; }
    .sampiyon-kart { background: linear-gradient(45deg, #FFD700, #FFA500); padding: 20px; border-radius: 12px; text-align: center; color: black; margin-bottom: 20px; font-weight: bold; }
    .pito-notu { background-color: #1E1E2F; border-radius: 10px; padding: 15px; border-left: 5px solid #00FF00; margin-top: 10px; font-style: italic; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. KOD ÇALIŞTIRMA MOTORU ---
def kod_calistir(kod):
    """Kodu çalıştırır ve çıktıları/hataları yakalar."""
    buffer = io.StringIO()
    try:
        with redirect_stdout(buffer):
            # Güvenli bir ortamda kodu çalıştır
            exec(kod, {"__builtins__": __builtins__}, {})
        output = buffer.getvalue()
        return output if output else "> Kod başarıyla çalıştı (Çıktı yok)."
    except Exception as e:
        return f"⚠️ Hata: {str(e)}"

def kod_normalize_et(kod):
    return re.sub(r'\s+', '', str(kod)).strip().lower()

def pito_gorseli_yukle(mod):
    base_path = os.path.dirname(os.path.abspath(__file__))
    img_path = os.path.join(base_path, "assets", f"pito_{mod}.gif")
    if os.path.exists(img_path):
        st.image(img_path, use_container_width=True)

# --- 3. VERİ VE BAĞLANTILAR ---
KULLANICILAR_URL = "https://docs.google.com/spreadsheets/d/1lat8rO2qm9QnzEUYlzC_fypG3cRkGlJfSfTtwNvs318/edit#gid=0"
KAYITLAR_URL = "https://docs.google.com/spreadsheets/d/14QoNr4FHZhSaUDUU-DDQEfNFHMo5Ge5t5lyDgqGRJ3k/edit#gid=0"
conn = st.connection("gsheets", type=GSheetsConnection)

with open('mufredat.json', 'r', encoding='utf-8') as f:
    mufredat = json.load(f)

# --- 4. SESSION STATE ---
if "user" not in st.session_state: st.session_state.user = None
if "error_count" not in st.session_state: st.session_state.error_count = 0
if "cevap_dogru" not in st.session_state: st.session_state.cevap_dogru = False
if "pito_mod" not in st.session_state: st.session_state.pito_mod = "merhaba"
if "last_code" not in st.session_state: st.session_state.last_code = ""

# --- 5. İLERLEME KAYDETME ---
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
        st.cache_data.clear()
        st.rerun()
    except Exception as e: st.error(f"Kayıt Hatası: {e}")

# --- 6. ANA PROGRAM ---
if st.session_state.user is None:
    st.title("🐍 Pito Python Akademi")
    pito_gorseli_yukle("merhaba")
    numara = st.number_input("Öğrenci Numarası:", step=1, value=0)
    if st.button("Sisteme Giriş Yap 🚀") and numara > 0:
        df_u = conn.read(spreadsheet=KULLANICILAR_URL, ttl=0)
        user_data = df_u[df_u['ogrenci_no'] == numara]
        if not user_data.empty:
            st.session_state.user = user_data.iloc[0].to_dict()
            st.rerun()
else:
    u = st.session_state.user
    col_main, col_leader = st.columns([7, 3])

    with col_main:
        m_idx = int(float(u['mevcut_modul'])) - 1
        modul = mufredat['pito_akademi_mufredat'][m_idx]
        egz = next((e for e in modul['egzersizler'] if e['id'] == str(u['mevcut_egzersiz'])), modul['egzersizler'][0])

        st.markdown(f"<div class='hero-panel'><h3>🚀 {u['ad_soyad']} | {u['sinif']}</h3><p>{u['rutbe']} • {int(float(u['toplam_puan']))} XP</p></div>", unsafe_allow_html=True)
        
        # Gösterge Paneli
        p_pot = max(0, 20 - (st.session_state.error_count * 5))
        st.markdown(f"""<div class="status-bar">
            <div>📍 Görev {egz['id']}</div><div>💎 {p_pot} XP</div><div>⚠️ Hatalar: {st.session_state.error_count}/4</div>
        </div>""", unsafe_allow_html=True)

        c_p, c_e = st.columns([1, 2])
        with c_p: pito_gorseli_yukle(st.session_state.pito_mod)
        with c_e:
            st.info(f"**YÖNERGE:** {egz['yonerge']}")
            if st.session_state.error_count == 3: st.warning(f"💡 İpucu: {egz['ipucu']}")

        # Editör ve Çıktı Kontrolü
        if not st.session_state.cevap_dogru and st.session_state.error_count < 4:
            k_in = st.text_area("Kodunu Yaz:", value=egz['sablon'], height=180)
            if st.button("Kontrol Et"):
                st.session_state.last_code = k_in
                if kod_normalize_et(k_in) == kod_normalize_et(egz['dogru_cevap_kodu']):
                    st.session_state.cevap_dogru, st.session_state.pito_mod = True, "basari"
                    st.rerun()
                else:
                    st.session_state.error_count += 1
                    st.session_state.pito_mod = "hata"
                    st.rerun()
        
        elif st.session_state.cevap_dogru:
            st.success(f"🌟 Tebrikler! +{p_pot} XP")
            # --- BAŞARILI ÇIKTI GÖRÜNTÜLEME ---
            st.markdown("<div class='console-header'>💻 KODUNUN ÇIKTISI</div>", unsafe_allow_html=True)
            st.markdown(f"<div class='console-box'>{kod_calistir(st.session_state.last_code)}</div>", unsafe_allow_html=True)
            
            n_id, n_m = (modul['egzersizler'][modul['egzersizler'].index(egz)+1]['id'], u['mevcut_modul']) if (modul['egzersizler'].index(egz)+1) < len(modul['egzersizler']) else (f"{m_idx + 2}.1", m_idx + 2)
            if st.button("Sonraki Göreve Geç ➡️"): ilerleme_kaydet(p_pot, st.session_state.last_code, egz['id'], u['mevcut_modul'], n_id, n_m)
        
        elif st.session_state.error_count >= 4:
            st.error("🚫 Görev Kilitlendi.")
            with st.expander("📖 Çözümü ve Beklenen Çıktıyı İncele", expanded=True):
                st.code(egz['cozum'], language="python")
                # --- ÇÖZÜM ÇIKTISI GÖRÜNTÜLEME ---
                output_cozum = kod_calistir(egz['cozum'])
                st.markdown("<div style='color:#00FF00; font-family:monospace; margin-top:10px;'>🚀 Beklenen Çıktı:</div>", unsafe_allow_html=True)
                st.markdown(f"<div style='background-color:#111; padding:10px; border-radius:5px; border:1px dashed #555;'>{output_cozum}</div>", unsafe_allow_html=True)

            n_id, n_m = (modul['egzersizler'][modul['egzersizler'].index(egz)+1]['id'], u['mevcut_modul']) if (modul['egzersizler'].index(egz)+1) < len(modul['egzersizler']) else (f"{m_idx + 2}.1", m_idx + 2)
            if st.button("Anladım, Sıradaki Göreve Geç ➡️"): ilerleme_kaydet(0, "Çözüm İncelendi", egz['id'], u['mevcut_modul'], n_id, n_m)

    # SAĞ PANEL: LİDERLİK TABLOSU
    with col_leader:
        st.markdown("<h3 style='text-align:center;'>🏆 ONUR KÜRSÜSÜ</h3>", unsafe_allow_html=True)
        df_all = conn.read(spreadsheet=KULLANICILAR_URL, ttl=60)
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
