import streamlit as st
import json
import re
from supabase import create_client, Client

# Özel Modüllerimiz
import auth
import mechanics
import ranks
import emotions
import education

# --- 1. KAYNAK VE GÖRSEL ZIRH YÜKLEME ---
st.set_page_config(page_title="Pito Python Akademi", layout="wide", initial_sidebar_state="collapsed")

def load_resources():
    try:
        # style.json'dan CSS zırhını yükle
        with open('style.json', 'r', encoding='utf-8') as f:
            st.markdown(json.load(f)['siber_buz_armor'], unsafe_allow_html=True)
        # messages.json'dan Pito ses bankasını yükle
        with open('messages.json', 'r', encoding='utf-8') as f:
            st.session_state.pito_messages = json.load(f)
    except Exception as e:
        st.error(f"⚠️ Kritik Kaynak Hatası: JSON dosyaları eksik! {e}")

load_resources()

# --- 2. VERİTABANI MOTORU ---
@st.cache_resource
def init_supabase():
    try:
        c = create_client(st.secrets["supabase"]["url"], st.secrets["supabase"]["key"])
        st.session_state.supabase_client = c 
        return c
    except:
        st.error("⚠️ Supabase bağlantısı kurulamadı!"); st.stop()

supabase: Client = init_supabase()

def normalize(k): 
    return re.sub(r'\s+', '', str(k)).strip().lower()

# --- 3. İLERLEME VE VERİ KAYIT SİSTEMİ ---
def ilerleme_kaydet(puan, kod, egz_id, n_id, n_m):
    yeni_xp = int(st.session_state.user['toplam_puan']) + puan
    r_ad, _ = ranks.rütbe_ata(yeni_xp)
    
    # Veritabanı Güncelle
    supabase.table("kullanicilar").update({
        "toplam_puan": yeni_xp, 
        "mevcut_egzersiz": str(n_id), 
        "mevcut_modul": int(n_m), 
        "rutbe": r_ad
    }).eq("ogrenci_no", int(st.session_state.user['ogrenci_no'])).execute()
    
    # Egzersiz Loglama
    supabase.table("egzersiz_kayitlari").insert({
        "ogrenci_no": int(st.session_state.user['ogrenci_no']), 
        "egz_id": str(egz_id), 
        "alinan_puan": int(puan), 
        "basarili_kod": str(kod)
    }).execute()
    
    # Session State Güncelle
    st.session_state.user.update({
        "toplam_puan": yeni_xp, 
        "mevcut_egzersiz": str(n_id), 
        "mevcut_modul": int(n_m), 
        "rutbe": r_ad
    })
    st.session_state.error_count, st.session_state.cevap_dogru, st.session_state.current_code = 0, False, ""
    st.rerun()

# --- 4. SESSION STATE (NAMEERROR ZIRHI) ---
keys = ["user", "temp_user", "show_reg", "error_count", "cevap_dogru", "current_code", "user_num", "in_review"]
for k in keys:
    if k not in st.session_state:
        if k in ["user", "temp_user"]: st.session_state[k] = None
        elif k in ["error_count", "user_num"]: st.session_state[k] = 0
        elif k in ["show_reg", "cevap_dogru", "in_review"]: st.session_state[k] = False
        else: st.session_state[k] = ""

# --- 5. ANA PROGRAM AKIŞI ---
try:
    with open('mufredat.json', 'r', encoding='utf-8') as f:
        mufredat = json.load(f)['pito_akademi_mufredat']
except: 
    st.error("mufredat.json bulunamadı!"); st.stop()

# --- DURUM 1: GİRİŞ EKRANI ---
if st.session_state.user is None:
    auth.login_ekrani(
        supabase, 
        st.session_state.pito_messages, 
        emotions.pito_goster, 
        lambda: ranks.liderlik_tablosu_goster(supabase)
    )

# --- DURUM 2: AKADEMİ İÇİ ---
else:
    u = st.session_state.user
    m_idx = int(u['mevcut_modul']) - 1
    
    # Üst Navigasyon (İnceleme Modu Butonu)
    c_nav1, c_nav2 = st.columns([4, 1])
    with c_nav2:
        if st.button("🔍 İnceleme Modu"):
            st.session_state.in_review = True
            st.rerun()

    # İnceleme Modu Aktifse
    if st.session_state.in_review:
        mechanics.inceleme_modu_paneli(u, mufredat, emotions.pito_goster)
    
    # Mezuniyet Durumu (Tüm modüller bittiyse)
    elif m_idx >= len(mufredat):
        mechanics.mezuniyet_ekrani(u, st.session_state.pito_messages, emotions.pito_goster, supabase)
    
    # Eğitim Motoru (Ders İşleme Modu)
    else:
        education.egitim_ekrani(
            u, 
            mufredat, 
            st.session_state.pito_messages, 
            emotions, 
            ranks, 
            ilerleme_kaydet, 
            normalize
        )
