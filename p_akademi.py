import streamlit as st
import pandas as pd
import json
import time
import os
import re
from supabase import create_client, Client

# --- 1. SİBER TASARIM VE SAYFA AYARLARI ---
st.set_page_config(
    page_title="Pito Python Akademi", 
    layout="wide", 
    initial_sidebar_state="collapsed"
)

# Hero Header ve Siber Stil
st.markdown("""
    <style>
    .stApp { background-color: #0E1117; color: #FFFFFF; }
    .stApp > header { display: none; }
    .block-container { padding-top: 4rem !important; }
    
    .academy-title { 
        font-size: 3.5em; font-weight: 800; text-align: center;
        background: linear-gradient(90deg, #00FF00, #00CCFF); 
        -webkit-background-clip: text; -webkit-text-fill-color: transparent; 
        margin-bottom: 30px;
    }
    .hero-panel { 
        background: linear-gradient(135deg, #1E1E2F 0%, #2D2D44 100%); 
        padding: 25px; border-radius: 15px; border-left: 8px solid #00FF00; 
        margin-bottom: 25px; box-shadow: 0 10px 30px rgba(0,255,0,0.1);
    }
    .status-bar { 
        display: flex; justify-content: space-between; background-color: #262730; 
        padding: 15px; border-radius: 12px; border: 1px solid #4B4B4B; margin-bottom: 20px;
    }
    .pito-notu { 
        background-color: #1E1E2F; border-radius: 10px; padding: 20px; 
        border-left: 5px solid #00FF00; margin-top: 15px; font-style: italic; color: #E0E0E0;
    }
    .console-box { 
        background-color: #1E1E1E; border-radius: 10px; padding: 15px; 
        font-family: 'Courier New', monospace; color: #00FF00; border: 1px solid #333;
    }
    .stButton>button { 
        border-radius: 10px; background-color: #00FF00 !important; 
        color: black !important; font-weight: bold; width: 100%; height: 3.5em;
    }
    .stTextArea>div>div>textarea { background-color: #1E1E1E; color: #00FF00; font-family: monospace; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. VERİTABANI BAĞLANTISI ---
@st.cache_resource
def init_supabase():
    return create_client(st.secrets["supabase"]["url"], st.secrets["supabase"]["key"])

supabase: Client = init_supabase()

# --- 3. YARDIMCI MOTORLAR ---
def kod_normalize_et(kod):
    return re.sub(r'\s+', '', str(kod)).strip().lower()

def pito_notu_uret(mod, ad="Genç Yazılımcı"):
    notlar = {
        "merhaba": f"Selam {ad}! Bugün Python dünyasında hangi kapıları açacağız?",
        "basari": f"Vay canına {ad}! Kodun tertemiz çalıştı. Sonuç aşağıda!",
        "hata": f"Ufak bir yazım kazası {ad}... Python biraz titizdir, bir daha bak.",
        "dusunuyor": f"Hımm, bu görev biraz terletiyor mu? Merak etme, çözüm seni bekliyor.",
        "mezun": f"İnanılmaz! Artık gerçek bir Python Bilgesisin!"
    }
    return notlar.get(mod, notlar["merhaba"])

def pito_gorseli_yukle(mod):
    path = os.path.join(os.path.dirname(__file__), "assets", f"pito_{mod}.gif")
    if os.path.exists(path):
        st.image(path, use_container_width=True)

# --- 4. VERİ VE SESSION STATE ---
try:
    with open('mufredat.json', 'r', encoding='utf-8') as f:
        mufredat = json.load(f)
except Exception:
    st.error("Müfredat dosyası bulunamadı!")
    st.stop()

if "user" not in st.session_state: st.session_state.user = None
if "error_count" not in st.session_state: st.session_state.error_count = 0
if "cevap_dogru" not in st.session_state: st.session_state.cevap_dogru = False
if "pito_mod" not in st.session_state: st.session_state.pito_mod = "merhaba"

# --- 5. KAYIT VE İLERLEME FONKSİYONLARI ---
def ilerleme_kaydet(puan, kod, egz_id, n_id, n_m):
    try:
        yeni_xp = int(st.session_state.user['toplam_puan']) + puan
        r = "🏆 Bilge" if yeni_xp >= 1000 else "🔥 Savaşçı" if yeni_xp >= 500 else "🐍 Pythonist" if yeni_xp >= 200 else "🥚 Çömez"
        
        supabase.table("kullanicilar").update({
            "toplam_puan": yeni_xp, 
            "mevcut_egzersiz": str(n_id), 
            "mevcut_modul": int(n_m), 
            "rutbe": r
        }).eq("ogrenci_no", int(st.session_state.user['ogrenci_no'])).execute()
        
        supabase.table("egzersiz_kayitlari").insert({
            "ogrenci_no": int(st.session_state.user['ogrenci_no']), 
            "egz_id": str(egz_id), 
            "alinan_puan": int(puan), 
            "basarili_kod": str(kod)
        }).execute()
        
        st.session_state.user.update({"toplam_puan": yeni_xp, "mevcut_egzersiz": str(n_id), "mevcut_modul": int(n_m), "rutbe": r})
        st.session_state.error_count, st.session_state.cevap_dogru, st.session_state.pito_mod = 0, False, "merhaba"
        st.rerun()
    except Exception as e:
        st.error(f"Kayıt Hatası: {e}")

# --- 6. ANA AKIŞ ---
if st.session_state.user is None:
    st.markdown('<div class="academy-title">Pito Python Akademi</div>', unsafe_allow_html=True)
    pito_gorseli_yukle("merhaba")
    
    col_l, col_mid, col_r = st.columns([1, 2, 1])
    with col_mid:
        numara = st.number_input("Okul Numaranı Gir:", step=1, value=0)
        if numara > 0:
            res = supabase.table("kullanicilar").select("*").eq("ogrenci_no", int(numara)).execute()
            if res.data:
                u = res.data[0]
                st.markdown(f'<div class="pito-notu" style="text-align:center;">👋 <b>Selam {u["ad_soyad"]}!</b><br>Senin için hazırız.</div>', unsafe_allow_html=True)
                if st.button("Akademiye Giriş Yap 🚀"):
                    st.session_state.user = u
                    st.rerun()
            else:
                st.warning("Numaranı bulamadım, haydi yeni profil oluşturalım!")
                y_ad = st.text_input("Ad Soyad:")
                y_sin = st.selectbox("Sınıfın:", ["9-A", "9-B", "10-A", "10-B", "11-A", "12-A"])
                if st.button("Kaydı Tamamla 🎓") and y_ad:
                    new_u = {
                        "ogrenci_no": int(numara), "ad_soyad": str(y_ad).strip(), "sinif": y_sin,
                        "toplam_puan": 0, "mevcut_modul": 1, "mevcut_egzersiz": "1.1", "rutbe": "🥚 Çömez"
                    }
                    reg_res = supabase.table("kullanicilar").insert(new_u).execute()
                    if reg_res.data:
                        st.session_state.user = reg_res.data[0]
                        st.success("Akademiye Hoş Geldin!")
                        time.sleep(1)
                        st.rerun()

else:
    u = st.session_state.user
    col_main, col_leader = st.columns([7, 3])
    
    with col_main:
        m_idx = int(u['mevcut_modul']) - 1
        if m_idx >= len(mufredat['pito_akademi_mufredat']):
            st.balloons()
            pito_gorseli_yukle("mezun")
            st.markdown(f"<h2 style='text-align:center;'>🏆 TEBRİKLER {u['ad_soyad'].upper()}!</h2>", unsafe_allow_html=True)
        else:
            modul = mufredat['pito_akademi_mufredat'][m_idx]
            egz = next((e for e in modul['egzersizler'] if e['id'] == str(u['mevcut_egzersiz'])), modul['egzersizler'][0])
            
            st.markdown(f"""
                <div class='hero-panel'>
                    <h3>🚀 {u['ad_soyad']} | {u['sinif']}</h3>
                    <p>{u['rutbe']} • {int(u['toplam_puan'])} XP</p>
                </div>""", unsafe_allow_html=True)
            
            p_pot = max(0, 20 - (st.session_state.error_count * 5))
            st.markdown(f'<div class="status-bar"><div>📍 Görev {egz["id"]}</div><div>💎 {p_pot} XP Potansiyel</div><div>⚠️ Hata: {st.session_state.error_count}/4</div></div>', unsafe_allow_html=True)

            c_p, c_e = st.columns([1, 2])
            with c_p: pito_gorseli_yukle(st.session_state.pito_mod)
            with c_e:
                st.info(f"**GÖREV:** {egz['yonerge']}")
                st.markdown(f"<div class='pito-notu'>💬 <b>Pito:</b> {pito_notu_uret(st.session_state.pito_mod, u['ad_soyad'].split()[0])}</div>", unsafe_allow_html=True)
                if st.session_state.error_count == 3:
                    st.warning(f"💡 İpucu: {egz['ipucu']}")

            if not st.session_state.cevap_dogru and st.session_state.error_count < 4:
                k_in = st.text_area("Kodunu Yaz:", value=egz['sablon'], height=180, key="pito_editor")
                if st.button("Kodu Kontrol Et"):
                    if kod_normalize_et(k_in) == kod_normalize_et(egz['dogru_cevap_kodu']):
                        st.session_state.cevap_dogru, st.session_state.pito_mod = True, "basari"
                    else:
                        st.session_state.error_count += 1
                        st.session_state.pito_mod = "hata" if st.session_state.error_count < 4 else "dusunuyor"
                    st.rerun()
            elif st.session_state.cevap_dogru:
                st.success(f"Tebrikler! +{p_pot} XP Kazandın.")
                st.markdown(f"<div class='console-box'><b>💻 Çıktı:</b><br>{egz.get('beklenen_cikti', '> Kod başarıyla çalıştırıldı.')}</div>", unsafe_allow_html=True)
                if st.button("Sonraki Göreve Geç ➡️"):
                    sira = modul['egzersizler'].index(egz) + 1
                    n_id, n_m = (modul['egzersizler'][sira]['id'], u['mevcut_modul']) if sira < len(modul['egzersizler']) else (f"{m_idx + 2}.1", m_idx + 2)
                    ilerleme_kaydet(p_pot, k_in, egz['id'], n_id, n_m)
            elif st.session_state.error_count >= 4:
                st.error("Puan Kazanılamadı. Çözümü incele.")
                with st.expander("📖 Doğru Çözüm", expanded=True):
                    st.code(egz['cozum'], language="python")
                if st.button("Anladım, Sıradaki ➡️"):
                    sira = modul['egzersizler'].index(egz) + 1
                    n_id, n_m = (modul['egzersizler'][sira]['id'], u['mevcut_modul']) if sira < len(modul['egzersizler']) else (f"{m_idx + 2}.1", m_idx + 2)
                    ilerleme_kaydet(0, "Çözüm İncelendi", egz['id'], n_id, n_m)

    with col_leader:
        st.markdown("<h3 style='text-align:center;'>🏆 ONUR KÜRSÜSÜ</h3>", unsafe_allow_html=True)
        try:
            ld = supabase.table("kullanicilar").select("ad_soyad, sinif, toplam_puan").order("toplam_puan", desc=True).limit(10).execute()
            if ld.data:
                for i, r in enumerate(ld.data, 1):
                    p = "🥇" if i==1 else "🥈" if i==2 else "🥉" if i==3 else f"{i}."
                    st.markdown(f"{p} **{r['ad_soyad']}** ({r['sinif']}) <br> `{int(r['toplam_puan'])} XP`", unsafe_allow_html=True)
        except Exception:
            st.write("Liderlik tablosu hazırlanıyor...")
