import streamlit as st
import json
import re
import datetime
from supabase import create_client, Client

# Özel Modüllerimiz
import auth
import mechanics
import ranks
import emotions
import education

# --- 1. SİBER-ZIRH VE KAYNAK YÜKLEME ---
st.set_page_config(
    page_title="Pito Python Akademi", 
    layout="wide", 
    initial_sidebar_state="collapsed"
)

def load_resources():
    try:
        # style.json dosyasından CSS zırhını yükle
        with open('style.json', 'r', encoding='utf-8') as f:
            st.markdown(json.load(f)['siber_buz_armor'], unsafe_allow_html=True)
        # Pito'nun ses bankasını session state'e al
        with open('messages.json', 'r', encoding='utf-8') as f:
            st.session_state.pito_messages = json.load(f)
    except Exception as e:
        st.error(f"⚠️ Kritik Kaynak Hatası: JSON dosyaları eksik! {e}")

load_resources()

# --- 2. VERİTABANI MOTORU ---
@st.cache_resource
def init_supabase():
    try:
        # secrets üzerinden Supabase bağlantısını kur
        return create_client(st.secrets["supabase"]["url"], st.secrets["supabase"]["key"])
    except:
        st.error("⚠️ Supabase bağlantısı kurulamadı!"); st.stop()

supabase: Client = init_supabase()

def normalize(k): 
    # Kod kıyaslaması için boşlukları temizle ve küçült
    return re.sub(r'\s+', '', str(k)).strip().lower()

# --- 3. İLERLEME VE VERİ KAYIT SİSTEMİ (MODÜL KİLİTLİ VE SENKRONİZE) ---
def ilerleme_kaydet(puan, kod, egz_id, n_id, n_m):
    u = st.session_state.user
    mevcut_m = int(u['mevcut_modul'])
    
    # 🚨 MODÜL GEÇİŞ KONTROLÜ
    if int(n_m) > mevcut_m:
        # Öğretmenin bu sınıf için verdiği en güncel izni sorgula
        iz_res = supabase.table("ayarlar").select("deger").eq("anahtar", f"izin_{u['sinif']}").execute()
        izin_verilen = int(iz_res.data[0]['deger']) if iz_res.data else 1
        
        if int(n_m) > izin_verilen:
            st.warning(f"🚨 DUR GENÇ YAZILIMCI! Modül {mevcut_m} bitti ama Modül {n_m} henüz öğretmen tarafından açılmadı.")
            return

    # --- VERİTABANI GÜNCELLEME ---
    # Not: Puan zaten education.py içinde st.session_state.user['toplam_puan']'a eklendi
    yeni_xp = int(u['toplam_puan']) 
    r_ad, _ = ranks.rütbe_ata(yeni_xp)
    su_an = datetime.datetime.now().isoformat()
    
    try:
        # Kullanıcı verilerini ve tarih bilgisini güncelle
        supabase.table("kullanicilar").update({
            "toplam_puan": yeni_xp, 
            "mevcut_egzersiz": str(n_id), 
            "mevcut_modul": int(n_m), 
            "rutbe": r_ad,
            "tarih": su_an
        }).eq("ogrenci_no", int(u['ogrenci_no'])).execute()
        
        # Başarılı kod kaydını siber-arşive ekle
        supabase.table("egzersiz_kayitlari").insert({
            "ogrenci_no": int(u['ogrenci_no']), 
            "egz_id": str(egz_id), 
            "alinan_puan": int(puan), 
            "basarili_kod": str(kod)
        }).execute()
        
        # Session state senkronizasyonu
        st.session_state.user.update({
            "mevcut_egzersiz": str(n_id), 
            "mevcut_modul": int(n_m), 
            "rutbe": r_ad,
            "tarih": su_an
        })
        
        st.session_state.error_count = 0
        st.session_state.cevap_dogru = False
        st.session_state.current_code = ""
        st.rerun()
        
    except Exception as e:
        st.error(f"⚠️ İlerleme Kaydedilemedi: {e}")

# --- 4. SESSION STATE (HATA ÖNLEYİCİ) ---
keys = ["user", "temp_user", "show_reg", "error_count", "cevap_dogru", "current_code", "user_num", "in_review", "login_step", "temp_num", "reset_trigger"]
for k in keys:
    if k not in st.session_state:
        if k in ["user", "temp_user", "temp_num"]: st.session_state[k] = None
        elif k in ["error_count", "user_num", "reset_trigger"]: st.session_state[k] = 0
        elif k in ["show_reg", "cevap_dogru", "in_review"]: st.session_state[k] = False
        elif k in ["login_step"]: st.session_state[k] = "numara_girisi"
        else: st.session_state[k] = ""

# --- 5. ANA PROGRAM AKIŞI ---
try:
    with open('mufredat.json', 'r', encoding='utf-8') as f:
        mufredat = json.load(f)['pito_akademi_mufredat']
except: 
    st.error("mufredat.json bulunamadı!"); st.stop()

if st.session_state.user is None:
    auth.login_ekrani(supabase, st.session_state.pito_messages, emotions.pito_goster, lambda: ranks.liderlik_tablosu_goster(supabase))
else:
    u = st.session_state.user
    m_idx = int(u['mevcut_modul']) - 1
    
    if st.session_state.get('in_review', False):
        mechanics.inceleme_modu_paneli(u, mufredat, emotions.pito_goster, supabase)
    elif m_idx >= len(mufredat):
        mechanics.mezuniyet_ekrani(u, st.session_state.pito_messages, emotions.pito_goster, supabase, ranks)
    else:
        education.egitim_ekrani(u, mufredat, st.session_state.pito_messages, emotions, ranks, ilerleme_kaydet, normalize, supabase)
