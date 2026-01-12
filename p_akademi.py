import streamlit as st
import pandas as pd
import json
import time
import os
from datetime import datetime
from streamlit_gsheets import GSheetsConnection

# --- 1. SİSTEM VE TASARIM AYARLARI ---
st.set_page_config(page_title="Pito Python Akademi", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
    .stApp { background-color: #0E1117; color: #FFFFFF; }
    .hero-panel { background: linear-gradient(90deg, #1E1E2F 0%, #2D2D44 100%); padding: 25px; border-radius: 15px; border-left: 8px solid #00FF00; margin-bottom: 25px; box-shadow: 0 4px 15px rgba(0,255,0,0.2); }
    .stButton>button { border-radius: 10px; background-color: #00FF00 !important; color: black !important; font-weight: bold; width: 100%; height: 3.5em; transition: 0.3s; }
    .stButton>button:hover { transform: scale(1.02); box-shadow: 0 0 20px #00FF00; }
    .stTextArea>div>div>textarea { background-color: #1E1E1E; color: #00FF00; font-family: 'Courier New', Courier, monospace; font-size: 16px; }
    .leaderboard-card { background-color: #1E1E2F; padding: 15px; border-radius: 10px; margin-bottom: 10px; border: 1px solid #3E3E5E; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. GÜVENLİ GÖRSEL YÜKLEME ---
def pito_gorseli_yukle(mod):
    base_path = os.path.dirname(os.path.abspath(__file__))
    img_path = os.path.join(base_path, "assets", f"pito_{mod}.gif")
    if os.path.exists(img_path):
        st.image(img_path, use_container_width=True)
    else:
        st.error(f"🖼️ Görsel Eksik: assets/pito_{mod}.gif")

# --- 3. VERİTABANI BAĞLANTILARI ---
KULLANICILAR_URL = "https://docs.google.com/spreadsheets/d/1lat8rO2qm9QnzEUYlzC_fypG3cRkGlJfSfTtwNvs318/edit#gid=0"
KAYITLAR_URL = "https://docs.google.com/spreadsheets/d/14QoNr4FHZhSaUDUU-DDQEfNFHMo5Ge5t5lyDgqGRJ3k/edit#gid=0"
conn = st.connection("gsheets", type=GSheetsConnection)

@st.cache_data(ttl=60)
def load_mufredat():
    try:
        with open('mufredat.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except: return None

# --- 4. SESSION STATE (HAFIZA) ---
if "user" not in st.session_state: st.session_state.user = None
if "error_count" not in st.session_state: st.session_state.error_count = 0
if "cevap_dogru" not in st.session_state: st.session_state.cevap_dogru = False
if "pito_mod" not in st.session_state: st.session_state.pito_mod = "merhaba"
if "last_code" not in st.session_state: st.session_state.last_code = ""

# --- 5. VERİ YAZMA MOTORU ---
def ilerleme_kaydet(puan, kod, egz_id, m_id, n_id, n_m):
    try:
        df_u = conn.read(spreadsheet=KULLANICILAR_URL, ttl=0)
        idx = df_u[df_u['ogrenci_no'] == st.session_state.user['ogrenci_no']].index[0]
        df_u.at[idx, 'toplam_puan'] = int(float(df_u.at[idx, 'toplam_puan'])) + puan
        df_u.at[idx, 'mevcut_egzersiz'] = str(n_id)
        df_u.at[idx, 'mevcut_modul'] = int(float(n_m))
        
        # Otomatik Rütbe Güncelleme
        xp = int(df_u.at[idx, 'toplam_puan'])
        if xp > 1000: r = "🏆 Bilge"
        elif xp > 500: r = "🔥 Savaşçı"
        elif xp > 200: r = "🐍 Pythonist"
        else: r = "🥚 Çömez"
        df_u.at[idx, 'rutbe'] = r
        
        conn.update(spreadsheet=KULLANICILAR_URL, data=df_u)

        df_k = conn.read(spreadsheet=KAYITLAR_URL, ttl=0)
        yeni_log = pd.DataFrame([{
            "kayit_id": f"{st.session_state.user['ogrenci_no']}_{egz_id}",
            "ogrenci_no": int(st.session_state.user['ogrenci_no']),
            "modul_id": int(float(m_id)),
            "egzersiz_id": str(egz_id),
            "alinan_puan": int(puan),
            "basarili_kod": kod,
            "tarih": datetime.now().strftime("%Y-%m-%d %H:%M")
        }])
        conn.update(spreadsheet=KAYITLAR_URL, data=pd.concat([df_k, yeni_log], ignore_index=True))
        
        st.session_state.user = df_u.iloc[idx].to_dict()
        st.session_state.error_count, st.session_state.cevap_dogru, st.session_state.pito_mod = 0, False, "merhaba"
        st.session_state.last_code = ""
        st.rerun()
    except Exception as e: st.error(f"Kayıt Hatası: {e}")

# --- 6. ANA AKIŞ ---
mufredat = load_mufredat()
if not mufredat: st.error("Müfredat Bulunamadı!"); st.stop()

if st.session_state.user is None:
    st.title("🐍 Pito Python Akademi")
    pito_gorseli_yukle("merhaba")
    numara = st.number_input("Öğrenci Numaranız:", step=1, value=0)
    
    if numara > 0:
        df_u = conn.read(spreadsheet=KULLANICILAR_URL, ttl=0)
        user_data = df_u[df_u['ogrenci_no'] == numara]

        if not user_data.empty:
            if st.button("Giriş Yap 🚀"):
                st.session_state.user = user_data.iloc[0].to_dict()
                st.rerun()
        else:
            st.warning("🧐 Pito: 'Seni tanımıyorum, haydi kaydol!'")
            c1, c2 = st.columns(2)
            with c1: yeni_ad = st.text_input("Ad Soyad:")
            with c2: yeni_sinif = st.selectbox("Sınıfın:", ["9-A", "9-B", "10-A", "10-B", "11-A", "12-A"])
            if st.button("Kaydol ve Başla 🎓"):
                if yeni_ad:
                    yeni_ogrenci = pd.DataFrame([{"ogrenci_no": int(numara), "ad_soyad": yeni_ad, "sinif": yeni_sinif, "toplam_puan": 0, "mevcut_modul": 1, "mevcut_egzersiz": "1.1", "rutbe": "🥚 Çömez"}])
                    conn.update(spreadsheet=KULLANICILAR_URL, data=pd.concat([df_u, yeni_ogrenci], ignore_index=True))
                    st.session_state.user = yeni_ogrenci.iloc[0].to_dict()
                    st.rerun()
else:
    # --- DASHBOARD & EĞİTİM ---
    u = st.session_state.user
    m_idx = int(float(u['mevcut_modul'])) - 1
    
    # Kahraman Paneli
    st.markdown(f"<div class='hero-panel'><h3>🚀 {u['ad_soyad']} | {u['sinif']}</h3><p>🏆 Rütbe: {u['rutbe']} | 📊 XP: {int(float(u['toplam_puan']))}</p></div>", unsafe_allow_html=True)

    tab_edu, tab_leader = st.tabs(["📚 Eğitim Alanı", "🏆 Liderlik Kürsüsü"])

    with tab_edu:
        if m_idx >= len(mufredat['pito_akademi_mufredat']):
            st.balloons(); pito_gorseli_yukle("mezun"); st.success("MEZUN OLDUN!"); st.stop()
        
        modul = mufredat['pito_akademi_mufredat'][m_idx]
        egz = next((e for e in modul['egzersizler'] if e['id'] == str(u['mevcut_egzersiz'])), modul['egzersizler'][0])
        
        col1, col2 = st.columns([1, 2])
        with col1:
            pito_gorseli_yukle(st.session_state.pito_mod)
            st.info(f"**GÖREV {egz['id']}:** {egz['yonerge']}")
            if st.session_state.error_count == 1: st.error("🤫 Ufak bir hata! Kontrol et.")
            elif st.session_state.error_count == 2: st.error("🧐 Dikkatli bak, eksik var!")
            elif st.session_state.error_count == 3: st.warning(f"💡 İpucu: {egz['ipucu']}")

        with col2:
            puan_pot = max(0, 20 - (st.session_state.error_count * 5))
            st.write(f"🎯 Kazanılacak: **{puan_pot} XP**")
            
            if not st.session_state.cevap_dogru and st.session_state.error_count < 4:
                k_in = st.text_area("Kodunu Yaz:", value=egz['sablon'], height=200, key="editor")
                if st.button("Kontrol Et"):
                    st.session_state.last_code = k_in
                    if k_in.strip() == egz['dogru_cevap_kodu'].strip():
                        st.session_state.cevap_dogru, st.session_state.pito_mod = True, "basari"
                        st.rerun()
                    else:
                        st.session_state.error_count += 1
                        st.session_state.pito_mod = "hata" if st.session_state.error_count < 4 else "dusunuyor"
                        st.rerun()
            elif st.session_state.cevap_dogru:
                st.success("🌟 Harika!"); idx = modul['egzersizler'].index(egz)
                n_id, n_m = (modul['egzersizler'][idx+1]['id'], u['mevcut_modul']) if idx+1 < len(modul['egzersizler']) else (f"{m_idx + 2}.1", m_idx + 2)
                if st.button("Sonraki Göreve Geç ➡️"): ilerleme_kaydet(puan_pot, st.session_state.last_code, egz['id'], u['mevcut_modul'], n_id, n_m)
            elif st.session_state.error_count >= 4:
                st.error("🚫 Kilitlendi."); with st.expander("📖 Çözüm"): st.code(egz['cozum'])
                idx = modul['egzersizler'].index(egz)
                n_id, n_m = (modul['egzersizler'][idx+1]['id'], u['mevcut_modul']) if idx+1 < len(modul['egzersizler']) else (f"{m_idx + 2}.1", m_idx + 2)
                if st.button("Sıradaki Göreve Geç ➡️"): ilerleme_kaydet(0, "Çözüm İncelendi", egz['id'], u['mevcut_modul'], n_id, n_m)

    with tab_leader:
        df_l = conn.read(spreadsheet=KULLANICILAR_URL, ttl=0)
        df_l['toplam_puan'] = pd.to_numeric(df_l['toplam_puan'], errors='coerce').fillna(0).astype(int)
        
        l1, l2, l3 = st.tabs(["👥 Sınıfım", "🏫 Okul En İyiler", "🔥 Şampiyon Sınıf"])
        
        with l1:
            s_df = df_l[df_l['sinif'] == u['sinif']].sort_values(by='toplam_puan', ascending=False).reset_index(drop=True)
            s_df.index += 1
            st.table(s_df[['ad_soyad', 'toplam_puan', 'rutbe']].rename(columns={'ad_soyad':'Öğrenci','toplam_puan':'XP'}))
            
        with l2:
            o_df = df_l.sort_values(by='toplam_puan', ascending=False).head(10).reset_index(drop=True)
            o_df.index += 1
            st.dataframe(o_df[['ad_soyad', 'sinif', 'toplam_puan', 'rutbe']], use_container_width=True)
            
        with l3:
            st.subheader("⚔️ Sınıf Başarı Ortalamaları")
            s_analiz = df_l.groupby('sinif').agg(toplam_xp=('toplam_puan', 'sum'), sayi=('ogrenci_no', 'count'))
            s_analiz['ortalama'] = (s_analiz['toplam_xp'] / s_analiz['sayi']).round(1)
            s_analiz = s_analiz.sort_values(by='ortalama', ascending=False)
            
            st.markdown(f"<div style='background:linear-gradient(45deg, #FFD700, #FFA500); padding:20px; border-radius:15px; text-align:center; color:black;'><h2>⭐ ŞAMPİYON SINIF: {s_analiz.index[0]} ⭐</h2><h3>Ortalama: {s_analiz.iloc[0]['ortalama']} XP</h3></div>", unsafe_allow_html=True)
            st.bar_chart(s_analiz['ortalama'], color="#00FF00")
