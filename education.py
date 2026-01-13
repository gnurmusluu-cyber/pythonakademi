import streamlit as st
import pandas as pd
import json
import random
from supabase import create_client, Client
import mechanics  # Mezuniyet/İnceleme
import auth       # Giriş/Kayıt
import ranks      # Rütbe ve Liderlik (Yeni!)

# --- 1. KAYNAK YÜKLEME ---
st.set_page_config(page_title="Pito Python Akademi", layout="wide", initial_sidebar_state="collapsed")

def load_resources():
    try:
        with open('style.json', 'r', encoding='utf-8') as f:
            st.markdown(json.load(f)['siber_buz_armor'], unsafe_allow_html=True)
        with open('messages.json', 'r', encoding='utf-8') as f:
            st.session_state.pito_messages = json.load(f)
    except: st.error("⚠️ Kaynak dosyaları eksik!")

load_resources()

# --- 2. MOTORLAR ---
@st.cache_resource
def init_supabase():
    try: return create_client(st.secrets["supabase"]["url"], st.secrets["supabase"]["key"])
    except: st.error("⚠️ Supabase hatası!"); st.stop()

supabase: Client = init_supabase()

# --- 3. SESSION STATE ---
keys = ["user", "temp_user", "show_reg", "error_count", "cevap_dogru", "pito_mod", "current_code", "in_review"]
for k in keys:
    if k not in st.session_state:
        st.session_state[k] = None if "user" in k else (0 if "count" in k else (False if "show" in k or "cevap" in k or "in_" in k else ("merhaba" if "mod" in k else "")))

# --- 4. NAVİGASYON ---
def ilerleme_kaydet(puan, kod, egz_id, n_id, n_m):
    y_xp = int(st.session_state.user['toplam_puan']) + puan
    r_ad, _ = ranks.rütbe_ata(y_xp)  # ranks.py'den çağırıyoruz
    # Veritabanı ve state güncellemeleri... (V110 standartları)
    # ...
    st.rerun()

# --- 5. ANA AKIŞ ---
try:
    with open('mufredat.json', 'r', encoding='utf-8') as f:
        mufredat = json.load(f)['pito_akademi_mufredat']
except: st.error("mufredat.json eksik!"); st.stop()

if st.session_state.user is None:
    # Liderlik tablosu fonksiyonunu parametre olarak auth modülüne gönderiyoruz
    auth.login_ekrani(supabase, st.session_state.pito_messages, mechanics.load_pito, 
                      lambda: ranks.liderlik_tablosu_goster(supabase))

else:
    u = st.session_state.user
    m_idx = int(u['mevcut_modul']) - 1
    total_m = len(mufredat)
    
    # Üst Navigasyon
    if st.button("🔍 İnceleme Modu"): st.session_state.in_review = True; st.rerun()

    if st.session_state.in_review:
        mechanics.inceleme_modu_paneli(u, mufredat, mechanics.load_pito)
    elif m_idx >= total_m:
        mechanics.mezuniyet_ekrani(u, st.session_state.pito_messages, mechanics.load_pito, supabase)
    else:
        # Eğitim akışı sırasında sağ kolonda liderlik tablosu gösterimi
        cl, cr = st.columns([7, 3])
        with cl:
            # Eğitim kutuları...
            pass
        with cr:
            ranks.liderlik_tablosu_goster(supabase, current_user=u)
