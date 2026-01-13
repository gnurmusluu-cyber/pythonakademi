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

# --- 1. SİBER-ZIRH VE KAYNAK YÜKLEME ---
st.set_page_config(
    page_title="Pito Python Akademi", 
    layout="wide", 
    initial_sidebar_state="collapsed"
)

def load_resources():
    try:
        # style.json'dan siber-buz temasını yükle
        with open('style.json', 'r', encoding='utf-8') as f:
            st.markdown(json.load(f)['siber_buz_armor'], unsafe_allow_html=True)
        # messages.json'dan Pito ses bankasını yükle
        with open('messages.json', 'r', encoding='utf-8') as f:
            st.session_state.pito_messages = json.load(f)
    except Exception as e:
        st.error(f"⚠️ Kritik Kaynak Hatası: JSON dosyaları eksik! {e}")

load_resources()

# --- 2. VERİTABANI MOTORU (GÜVENLİ BAĞLANTI) ---
@st.cache_resource
def init_supabase():
    try:
        return create_client(st.secrets["supabase"]["url"], st.secrets["supabase"]["key"])
    except Exception as e:
        st.error(f"📡 Veritabanı Bağlantı Hatası: {e}")
        return None

supabase = init_supabase()

# --- 3. SİBER-HAFIZA (SESSION STATE) ---
if 'user' not in st.session_state: st.session_state.user = None
if 'error_count' not in st.session_state: st.session_state.error_count = 0
if 'cevap_dogru' not in st.session_state: st.session_state.cevap_dogru = False
if 'current_code' not in st.session_state: st.session_state.current_code = ""
if 'in_review' not in st.session_state: st.session_state.in_review = False

# --- 4. MÜFREDAT (SİBER-ARŞİV) ---
mufredat = [
    {
        "modul_adi": "Modül 1: Python'a Giriş ve Ekrana Yazdırma",
        "pito_anlatimi": "Merhaba genç yazılımcı! Ben Pito. Bugün Python dünyasına ilk adımını atacaksın. `print()` fonksiyonu, bilgisayarla konuşmanın en temel yoludur.",
        "egzersizler": [
            {
                "id": "1.1",
                "yonerge": "Ekrana 'Merhaba Python' yazdıran kodu yaz.",
                "sablon": "print('...')",
                "dogru_cevap_kodu": "print('Merhaba Python')",
                "beklenen_cikti": "Merhaba Python",
                "cozum": "print('Merhaba Python')",
                "ipucu": "Tırnak işaretlerine ve büyük/küçük harfe dikkat et!"
            }
        ]
    }
]

# --- 5. YARDIMCI SİBER-FONKSİYONLAR ---
def normalize_code(code):
    """Kodu boşluklardan ve tırnak farklarından arındırır."""
    return re.sub(r'\s+', '', code).replace('"', "'")

def ilerleme_kaydet(puan, kod, egz_id, n_id, n_m):
    """Öğrencinin başarısını veritabanına mühürler."""
    try:
        u = st.session_state.user
        yeni_toplam = int(u['toplam_puan']) + puan
        # Kullanıcı tablosunu güncelle
        supabase.table("kullanicilar").update({
            "toplam_puan": yeni_toplam,
            "mevcut_egzersiz": n_id,
            "mevcut_modul": n_m
        }).eq("ogrenci_no", int(u['ogrenci_no'])).execute()
        
        # Egzersiz kaydını mühürle
        supabase.table("egzersiz_kayitlari").insert({
            "ogrenci_no": int(u['ogrenci_no']),
            "egz_id": egz_id,
            "alinan_puan": puan,
            "kod": kod
        }).execute()
        
        # Hafızayı sıfırla ve veriyi tazele
        st.session_state.error_count = 0
        st.session_state.cevap_dogru = False
        res = supabase.table("kullanicilar").select("*").eq("ogrenci_no", int(u['ogrenci_no'])).execute()
        st.session_state.user = res.data[0]
        st.rerun()
    except Exception as e:
        st.error(f"⚠️ Mühürleme Hatası: {e}")

# --- 6. ANA AKIŞ KONTROLÜ ---
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
    
    # [BİLGİ: İnceleme Modu butonu buradan kaldırıldı, artık education.py içinde.]

    # DURUM YÖNETİMİ
    if st.session_state.in_review:
        # Geçmiş kodları inceleme paneli
        mechanics.inceleme_modu_paneli(u, mufredat, emotions.pito_goster, supabase)
    
    elif m_idx >= len(mufredat):
        # Mezuniyet: Sertifika, Onur Kürsüsü ve Sıfırlama
        mechanics.mezuniyet_ekrani(u, st.session_state.pito_messages, emotions.pito_goster, supabase, ranks)
        
    else:
        # Eğitim Motoru: Ders anlatımı ve kod editörü
        education.egitim_ekrani(
            u, mufredat, st.session_state.pito_messages, 
            emotions, ranks, ilerleme_kaydet, normalize_code, supabase
        )
