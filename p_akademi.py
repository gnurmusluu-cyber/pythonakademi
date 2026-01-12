import streamlit as st
import pandas as pd
import json
import time
import os
import re
from datetime import datetime
from supabase import create_client, Client

# --- 1. SİSTEM VE GÖRSEL KONFİGÜRASYON ---
st.set_page_config(
    page_title="Pito Python Akademi", 
    layout="wide", 
    initial_sidebar_state="collapsed"
)

# Üst Boşluk Ayarı
top_pad = "5rem" if st.session_state.get("user") is None else "3.5rem"

st.markdown(f"""
    <style>
    .stApp {{ background-color: #0E1117; color: #FFFFFF; }}
    .stApp > header {{ display: none; }}
    .block-container {{ padding-top: {top_pad} !important; padding-bottom: 2rem !important; }}
    
    .login-container {{ text-align: center; max-width: 550px; margin: auto; }}
    .academy-title {{ 
        font-size: 3em; font-weight: 800; margin-bottom: 25px; 
        background: linear-gradient(90deg, #00FF00, #00CCFF); 
        -webkit-background-clip: text; -webkit-text-fill-color: transparent; 
        text-shadow: 2px 2px 10px rgba(0, 255, 0, 0.2);
        line-height: 1.2;
    }}
    .hero-panel {{ background: linear-gradient(90deg, #1E1E2F 0%, #2D2D44 100%); padding: 25px; border-radius: 15px; border-left: 8px solid #00FF00; margin-bottom: 25px; }}
    .status-bar {{ display: flex; justify-content: space-between; background-color: #262730; padding: 12px; border-radius: 10px; border: 1px solid #4B4B4B; margin-bottom: 15px; }}
    .console-box {{ background-color: #1E1E1E; border: 1px solid #333; border-radius: 10px; padding: 15px; font-family: monospace; color: #00FF00; margin-top: 10px; }}
    .pito-notu {{ background-color: #1E1E2F; border-radius: 10px; padding: 15px; border-left: 5px solid #00FF00; margin-top: 10px; font-style: italic; color: #E0E0E0; }}
    .stButton>button {{ border-radius: 10px; background-color: #00FF00 !important; color: black !important; font-weight: bold; width: 100%; height: 3.5em; }}
    </style>
    """, unsafe_allow_html=True)

# --- 2. SUPABASE BAĞLANTI MOTORU ---
@st.cache_resource
def init_supabase():
    try:
        url = st.secrets["supabase"]["url"]
        key = st.secrets["supabase"]["key"]
        return create_client(url, key)
    except Exception as e:
        st.error(f"⚠️ Bağlantı Bilgileri Eksik! Lütfen Secrets'ı kontrol edin: {e}")
        st.stop()

supabase: Client = init_supabase()

# --- 3. YARDIMCI MOTORLAR ---
def kod_normalize_et(kod):
    return re.sub(r'\s+', '', str(kod)).strip().lower()

def pito_notu_uret(mod, ad="Genç Yazılımcı"):
    notlar = {
        "merhaba": f"Selam {ad}! Bugün Python dünyasında hangi kapıları açacağız?",
        "basari": f"Vay canına {ad}! Kodun tertemiz çalıştı. Çıktıyı aşağıya bıraktım.",
        "hata": f"Ufak bir yazım kazası {ad}... Bir daha bak istersen.",
        "dusunuyor": f"Hımm, bu görev biraz terletiyor mu? Çözüm seni bekliyor.",
        "mezun": f"İnanılmaz! Artık gerçek bir Python Bilgesisin!"
    }
    return notlar.get(mod, notlar["merhaba"])

def pito_gorseli_yukle(mod):
    base_path = os.path.dirname(os.path.abspath(__file__))
    img_path = os.path.join(base_path, "assets", f"pito_{mod}.gif")
    if os.path.exists(img_path):
        st.image(img_path, use_container_width=True)

# --- 4. VERİ VE SESSION STATE ---
try:
    with open('mufredat.json', 'r', encoding='utf-8') as f:
        mufredat = json.load(f)
except:
    st.error("❌ Müfredat dosyası eksik!"); st.stop()

if "user" not in st.session_state: st.session_state.user = None
if "temp_user" not in st.session_state: st.session_state.temp_user = None
if "error_count" not in st.session_state: st.session_state.error_count = 0
if "cevap_dogru" not in st.session_state: st.session_state.cevap_dogru = False
if "pito_mod" not in st.session_state: st.session_state.pito_mod = "merhaba"

# --- 5. KAYIT VE İLERLEME SİSTEMİ ---
def ilerleme_kaydet(puan, kod, egz_id, n_id, n_m):
    try:
        yeni_xp = int(st.session_state.user['toplam_puan']) + puan
        r = "🏆 Bilge" if yeni_xp >= 1000 else "🔥 Savaşçı" if yeni_xp >= 500 else "🐍 Pythonist" if yeni_xp >= 200 else "🥚 Çömez"
        
        # Güncelleme
        supabase.table("kullanicilar").update({
            "toplam_puan": yeni_xp, "mevcut_egzersiz": str(n_id), 
            "mevcut_modul": int(n_m), "rutbe": r
        }).eq("ogrenci_no", int(st.session_state.user['ogrenci_no'])).execute()
        
        # Log
        supabase.table("egzersiz_kayitlari").insert({
            "ogrenci_no": int(st.session_state.user['ogrenci_no']), 
            "egz_id": str(egz_id), "alinan_puan": int(puan), "basarili_kod": str(kod)
        }).execute()
        
        st.session_state.user.update({"toplam_puan": yeni_xp, "mevcut_egzersiz": str(n_id), "mevcut_modul": int(n_m), "rutbe": r})
        st.session_state.error_count, st.session_state.cevap_dogru, st.session_state.pito_mod = 0, False, "merhaba"
        st.rerun()
    except Exception as e:
        st.error(f"🛑 Kayıt hatası: {e}")

def akademi_sifirla():
    try:
        supabase.table("kullanicilar").update({
            "toplam_puan": 0, "mevcut_egzersiz": "1.1", "mevcut_modul": 1, "rutbe": "🥚 Çömez"
        }).eq("ogrenci_no", int(st.session_state.user['ogrenci_no'])).execute()
        st.session_state.user.update({"toplam_puan": 0, "mevcut_egzersiz": "1.1", "mevcut_modul": 1, "rutbe": "🥚 Çömez"})
        st.session_state.error_count, st.session_state.cevap_dogru, st.session_state.pito_mod = 0, False, "merhaba"
        st.rerun()
    except Exception as e:
        st.error(f"🛑 Sıfırlama hatası: {e}")

# --- 6. ANA PROGRAM AKIŞI ---
if st.session_state.user is None:
    empty_l, col_mid, empty_r = st.columns([1, 2, 1])
    with col_mid:
        st.markdown('<div class="login-container"><div class="academy-title">Pito Python Akademi</div>', unsafe_allow_html=True)
        pito_gorseli_yukle("merhaba")
        
        if st.session_state.temp_user is None:
            numara = st.number_input("Okul Numaranı Gir:", step=1, value=0)
            if numara > 0 and st.button("Akademi Kapısını Aç 🔑"):
                res = supabase.table("kullanicilar").select("*").eq("ogrenci_no", int(numara)).execute()
                if res.data:
                    st.session_state.temp_user = res.data[0]; st.rerun()
                else:
                    st.info("Haydi kaydolalım!")
                    y_ad = st.text_input("Ad Soyad:")
                    y_sin = st.selectbox("Sınıfın:", ["9-A", "9-B", "10-A", "10-B", "11-A", "12-A"])
                    
                    # --- TEŞHİS MODLU KAYIT BLOĞU ---
                    if st.button("Kaydı Tamamla 🎓") and y_ad:
                        try:
                            new_u = {
                                "ogrenci_no": int(numara), 
                                "ad_soyad": str(y_ad).strip(), 
                                "sinif": str(y_sin),
                                "toplam_puan": 0,
                                "mevcut_modul": 1,
                                "mevcut_egzersiz": "1.1",
                                "rutbe": "🥚 Çömez"
                            }
                            st.write("📡 Supabase'e gönderilen paket:", new_u)
                            response = supabase.table("kullanicilar").insert(new_u).execute()
                            st.write("📥 Sunucudan gelen ham yanıt:", response)
                            
                            if response.data and len(response.data) > 0:
                                st.success("✅ Kayıt başarılı! Yönlendiriliyorsunuz...")
                                st.session_state.user = response.data[0]
                                time.sleep(1.5); st.rerun()
                            else:
                                st.error("🛑 Sunucu veriyi almadı!")
                                st.info("Eğer yukarıdaki 'data' kısmı boş [] ise, Supabase'de RLS hala aktif olabilir.")
                        except Exception as e:
                            st.error(f"❌ Teknik Engel Oluştu: {e}")
        else:
            t_u = st.session_state.temp_user
            st.markdown(f'<div class="pito-notu" style="text-align:center;">👋 <b>Selam {t_u["ad_soyad"]}!</b><br>Bu sen misin?</div>', unsafe_allow_html=True)
            c1, c2 = st.columns(2)
            if c1.button("Evet, Benim! 🚀"): st.session_state.user = st.session_state.temp_user; st.session_state.temp_user = None; st.rerun()
            if c2.button("Hayır, Değilim! 👤"): st.session_state.temp_user = None; st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

else:
    # --- AKADEMİ İÇERİĞİ ---
    u = st.session_state.user
    col_main, col_leader = st.columns([7, 3])
    
    with col_main:
        m_idx = int(u['mevcut_modul']) - 1
        if m_idx >= len(mufredat['pito_akademi_mufredat']):
            st.balloons(); pito_gorseli_yukle("mezun")
            st.markdown(f"<h2 style='text-align:center; color:#00FF00;'>🏆 TEBRİKLER {u['ad_soyad'].upper()}!</h2>", unsafe_allow_html=True)
            if st.button("🔄 Eğitimi Tekrar Al"): akademi_sifirla()
        else:
            modul = mufredat['pito_akademi_mufredat'][m_idx]
            egz = next((e for e in modul['egzersizler'] if e['id'] == str(u['mevcut_egzersiz'])), modul['egzersizler'][0])
            
            st.markdown(f"<div class='hero-panel'><h3>🚀 {u['ad_soyad']} | {u['sinif']}</h3><p>{u['rutbe']} • {int(u['toplam_puan'])} XP</p></div>", unsafe_allow_html=True)
            p_pot = max(0, 20 - (st.session_state.error_count * 5))
            st.markdown(f'<div class="status-bar"><div>📍 Görev {egz["id"]}</div><div>💎 {p_pot} XP</div><div>⚠️ Hata: {st.session_state.error_count}/4</div></div>', unsafe_allow_html=True)

            c_p, c_e = st.columns([1, 2])
            with c_p: pito_gorseli_yukle(st.session_state.pito_mod)
            with c_e:
                st.info(f"**GÖREV:** {egz['yonerge']}")
                st.markdown(f"<div class='pito-notu'>💬 <b>Pito:</b> {pito_notu_uret(st.session_state.pito_mod, u['ad_soyad'].split()[0])}</div>", unsafe_allow_html=True)
            
            if not st.session_state.cevap_dogru and st.session_state.error_count < 4:
                k_in = st.text_area("Kodunu Yaz:", value=egz['sablon'], height=200, key="editor_v27")
                if st.button("Kontrol Et"):
                    if kod_normalize_et(k_in) == kod_normalize_et(egz['dogru_cevap_kodu']):
                        st.session_state.cevap_dogru, st.session_state.pito_mod = True, "basari"
                    else:
                        st.session_state.error_count += 1
                        st.session_state.pito_mod = "hata" if st.session_state.error_count < 4 else "dusunuyor"
                    st.rerun()
            elif st.session_state.cevap_dogru:
                st.success(f"🌟 +{p_pot} XP!")
                if st.button("Sonraki Göreve Geç ➡️"):
                    sira = modul['egzersizler'].index(egz) + 1
                    n_id, n_m = (modul['egzersizler'][sira]['id'], u['mevcut_modul']) if sira < len(modul['egzersizler']) else (f"{m_idx + 2}.1", m_idx + 2)
                    ilerleme_kaydet(p_pot, "Başarılı", egz['id'], n_id, n_m)
            elif st.session_state.error_count >= 4:
                st.error("🚫 Kilitlendi."); with st.expander("📖 Çözüm", expanded=True): st.code(egz['cozum'])
                if st.button("Anladım, Sıradaki ➡️"):
                    sira = modul['egzersizler'].index(egz) + 1
                    n_id, n_m = (modul['egzersizler'][sira]['id'], u['mevcut_modul']) if sira < len(modul['egzersizler']) else (f"{m_idx + 2}.1", m_idx + 2)
                    ilerleme_kaydet(0, "Çözüm İncelendi", egz['id'], n_id, n_m)

    with col_leader:
        st.markdown("<h3 style='text-align:center;'>🏆 ONUR KÜRSÜSÜ</h3>", unsafe_allow_html=True)
        try:
            ld_res = supabase.table("kullanicilar").select("ad_soyad, sinif, toplam_puan").order("toplam_puan", desc=True).limit(10).execute()
            if ld_res.data:
                df_ld = pd.DataFrame(ld_res.data)
                for i, r in enumerate(df_ld.itertuples(), 1):
                    st.markdown(f"**{i}.** {r.ad_soyad} ({r.sinif}) • `{int(r.toplam_puan)} XP`")
        except: st.write("Sıralama yüklenemedi...")
