import streamlit as st
import pandas as pd
import json
import time
import os
import re
from supabase import create_client, Client

# --- SİSTEM AYARLARI ---
st.set_page_config(page_title="Pito Python Akademi", layout="wide")

# Görsel Stil (CSS)
st.markdown("""
    <style>
    .stApp { background-color: #0E1117; color: #FFFFFF; }
    .academy-title { font-size: 3em; font-weight: 800; text-align: center; color: #00FF00; }
    .pito-notu { background-color: #1E1E2F; border-left: 5px solid #00FF00; padding: 15px; border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

# --- SUPABASE BAĞLANTISI ---
@st.cache_resource
def init_supabase():
    try:
        return create_client(st.secrets["supabase"]["url"], st.secrets["supabase"]["key"])
    except Exception as e:
        st.error(f"Bağlantı hatası: {e}"); st.stop()

supabase: Client = init_supabase()

# --- YARDIMCI MOTORLAR ---
def pito_gorseli_yukle(mod):
    path = os.path.join(os.path.dirname(__file__), "assets", f"pito_{mod}.gif")
    if os.path.exists(path): st.image(path, use_container_width=True)

# --- SESSION STATE ---
if "user" not in st.session_state: st.session_state.user = None
if "error_count" not in st.session_state: st.session_state.error_count = 0

# --- GİRİŞ VE KAYIT EKRANI ---
if st.session_state.user is None:
    st.markdown('<div class="academy-title">Pito Python Akademi</div>', unsafe_allow_html=True)
    pito_gorseli_yukle("merhaba")
    
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        numara = st.number_input("Okul Numaran:", step=1, value=0)
        if numara > 0:
            res = supabase.table("kullanicilar").select("*").eq("ogrenci_no", int(numara)).execute()
            
            if res.data:
                u = res.data[0]
                st.success(f"Hoş geldin {u['ad_soyad']}!")
                if st.button("Eğitime Devam Et 🚀"):
                    st.session_state.user = u
                    st.rerun()
            else:
                st.warning("Kaydın bulunamadı. Yeni profil oluşturalım:")
                y_ad = st.text_input("Ad Soyad:")
                y_sin = st.selectbox("Sınıfın:", ["9-A", "9-B", "10-A", "10-B", "11-A", "12-A"])
                
                if st.button("Kaydı Tamamla 🎓") and y_ad:
                    try:
                        # VERİ PAKETİ
                        new_u = {
                            "ogrenci_no": int(numara),
                            "ad_soyad": str(y_ad).strip(),
                            "sinif": str(y_sin),
                            "toplam_puan": 0,
                            "mevcut_modul": 1,
                            "mevcut_egzersiz": "1.1",
                            "rutbe": "🥚 Çömez"
                        }
                        
                        # TEŞHİS MODU: Gönderilen veriyi ekrana yaz
                        st.write("📡 Gönderiliyor:", new_u)
                        
                        # INSERT İŞLEMİ
                        response = supabase.table("kullanicilar").insert(new_u).execute()
                        
                        # YANIT ANALİZİ
                        st.write("📥 Yanıt:", response)
                        
                        if response.data:
                            st.success("✅ Kayıt başarılı!")
                            st.session_state.user = response.data[0]
                            time.sleep(1); st.rerun()
                        else:
                            st.error("🛑 Kayıt başarısız! Veritabanı boş döndü.")
                    except Exception as e:
                        st.error(f"❌ KRİTİK HATA: {e}")

else:
    # --- EĞİTİM AKIŞI ---
    u = st.session_state.user
    st.sidebar.write(f"👤 {u['ad_soyad']}")
    st.sidebar.write(f"🏆 Puan: {u['toplam_puan']}")
    if st.sidebar.button("Çıkış Yap"):
        st.session_state.user = None; st.rerun()
    
    st.title("🐍 Eğitim Başladı")
    st.write("Burası ana eğitim alanı. Kayıt başarılı olduysa burayı görüyorsun!")
