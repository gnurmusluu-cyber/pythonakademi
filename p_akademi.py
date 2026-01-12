import streamlit as st
import pandas as pd
import json
import time
import os
import re # Düzenli ifadeler için gerekli
from datetime import datetime
from streamlit_gsheets import GSheetsConnection

# --- 1. SİSTEM AYARLARI ---
st.set_page_config(page_title="Pito Python Akademi", layout="wide", initial_sidebar_state="collapsed")

# --- 2. AKILLI KOD TEMİZLEME FONKSİYONU ---
def kod_normalize_et(kod):
    """Kod içindeki tüm boşlukları siler ve küçük harfe çevirir."""
    # Tüm beyaz boşlukları (\s) siler ve metni temizler
    return re.sub(r'\s+', '', kod).strip().lower()

# --- 3. GÜVENLİ VERİ OKUMA ---
def veri_oku_guvenli(url, cache_suresi=10):
    try:
        return conn.read(spreadsheet=url, ttl=cache_suresi)
    except:
        return None

# --- 4. VERİ YAZMA ---
def ilerleme_kaydet(puan, kod, egz_id, m_id, n_id, n_m):
    try:
        df_u = veri_oku_guvenli(KULLANICILAR_URL, 0)
        if df_u is None: return
        u_idx = df_u[df_u['ogrenci_no'] == st.session_state.user['ogrenci_no']].index[0]
        yeni_puan = int(float(df_u.at[u_idx, 'toplam_puan'])) + puan
        df_u.at[u_idx, 'toplam_puan'] = yeni_puan
        df_u.at[u_idx, 'mevcut_egzersiz'] = str(n_id)
        df_u.at[u_idx, 'mevcut_modul'] = int(float(n_m))
        
        if yeni_puan >= 1000: r = "🏆 Bilge"
        elif yeni_puan >= 500: r = "🔥 Savaşçı"
        elif yeni_puan >= 200: r = "🐍 Pythonist"
        else: r = "🥚 Çömez"
        df_u.at[u_idx, 'rutbe'] = r
        
        conn.update(spreadsheet=KULLANICILAR_URL, data=df_u)
        df_k = veri_oku_guvenli(KAYITLAR_URL, 0)
        yeni_log = pd.DataFrame([{"kayit_id": f"{st.session_state.user['ogrenci_no']}_{egz_id}", "ogrenci_no": int(st.session_state.user['ogrenci_no']), "modul_id": int(float(m_id)), "egzersiz_id": str(egz_id), "alinan_puan": int(puan), "basarili_kod": kod, "tarih": datetime.now().strftime("%Y-%m-%d %H:%M")}])
        conn.update(spreadsheet=KAYITLAR_URL, data=pd.concat([df_k, yeni_log], ignore_index=True))
        
        st.session_state.user = df_u.iloc[u_idx].to_dict()
        st.session_state.error_count, st.session_state.cevap_dogru, st.session_state.pito_mod = 0, False, "merhaba"
        st.session_state.last_code = ""
        st.rerun()
    except Exception as e: st.error(f"API Hatası: {e}")

# --- (VERİTABANI VE SESSION TANIMLAMALARI AYNI) ---
KULLANICILAR_URL = "https://docs.google.com/spreadsheets/d/1lat8rO2qm9QnzEUYlzC_fypG3cRkGlJfSfTtwNvs318/edit#gid=0"
KAYITLAR_URL = "https://docs.google.com/spreadsheets/d/14QoNr4FHZhSaUDUU-DDQEfNFHMo5Ge5t5lyDgqGRJ3k/edit#gid=0"
conn = st.connection("gsheets", type=GSheetsConnection)

if "user" not in st.session_state: st.session_state.user = None
if "error_count" not in st.session_state: st.session_state.error_count = 0
if "cevap_dogru" not in st.session_state: st.session_state.cevap_dogru = False
if "pito_mod" not in st.session_state: st.session_state.pito_mod = "merhaba"
if "last_code" not in st.session_state: st.session_state.last_code = ""

with open('mufredat.json', 'r', encoding='utf-8') as f:
    mufredat = json.load(f)

# --- ANA PROGRAM AKIŞI ---
if st.session_state.user is None:
    # (Giriş Ekranı Kodları Buraya...)
    pass
else:
    u = st.session_state.user
    col_main, col_leader = st.columns([7, 3])

    with col_main:
        m_idx = int(float(u['mevcut_modul'])) - 1
        modul = mufredat['pito_akademi_mufredat'][m_idx]
        egz = next((e for e in modul['egzersizler'] if e['id'] == str(u['mevcut_egzersiz'])), modul['egzersizler'][0])
        
        # (Dashboard Tasarımı Buraya...)
        
        with st.container():
            # KONTROL BUTONU BÖLÜMÜ (GÜNCELLENDİ)
            k_in = st.text_area("Kodunu Yaz:", value=egz['sablon'], height=200, key="editor")
            if st.button("Kontrol Et"):
                st.session_state.last_code = k_in
                
                # KRİTİK DEĞİŞİKLİK: Normalleştirilmiş Karşılaştırma
                if kod_normalize_et(k_in) == kod_normalize_et(egz['dogru_cevap_kodu']):
                    st.session_state.cevap_dogru, st.session_state.pito_mod = True, "basari"
                    st.rerun()
                else:
                    st.session_state.error_count += 1
                    st.session_state.pito_mod = "hata" if st.session_state.error_count < 4 else "dusunuyor"
                    st.rerun()
    
    # --- SAĞ PANEL (LİDERLİK TABLOSU) ---
    with col_leader:
        # (Önceki liderlik tablosu kodları, veri_oku_guvenli kullanarak buraya...)
        pass
