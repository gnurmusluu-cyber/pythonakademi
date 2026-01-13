import streamlit as st
import pandas as pd
import json
import os
import re
import base64
import random
from supabase import create_client, Client
import mechanics  # Mezuniyet ve İnceleme Modu motoru
import auth       # Giriş ve Kayıt Mekanizması
import ranks      # Rütbe ve Liderlik Motoru

# --- 1. SİBER-ZIRH VE SES BANKASI YÜKLEME ---
st.set_page_config(page_title="Pito Python Akademi", layout="wide", initial_sidebar_state="collapsed")

def load_resources():
    try:
        # Görsel zırhı yükle
        with open('style.json', 'r', encoding='utf-8') as f:
            st.markdown(json.load(f)['siber_buz_armor'], unsafe_allow_html=True)
        # Pito'nun ses bankasını yükle
        with open('messages.json', 'r', encoding='utf-8') as f:
            st.session_state.pito_messages = json.load(f)
    except Exception as e:
        st.error(f"⚠️ Kritik Kaynak Hatası: style.json veya messages.json bulunamadı! {e}")

load_resources()

# --- 2. VERİTABANI VE YARDIMCI FONKSİYONLAR ---
@st.cache_resource
def init_supabase():
    try:
        return create_client(st.secrets["supabase"]["url"], st.secrets["supabase"]["key"])
    except:
        st.error("⚠️ Supabase bağlantısı kurulamadı!"); st.stop()

supabase: Client = init_supabase()

def normalize(k): 
    return re.sub(r'\s+', '', str(k)).strip().lower()

def load_pito(mod, size=180):
    path = os.path.join(os.path.dirname(__file__), "assets", f"pito_{mod}.gif")
    if os.path.exists(path):
        with open(path, "rb") as f:
            encoded = base64.b64encode(f.read()).decode()
        st.markdown(f'<img src="data:image/gif;base64,{encoded}" width="{size}">', unsafe_allow_html=True)

# --- 3. SESSION STATE (NAMEERROR VE MANTIK ZIRHI) ---
keys = ["user", "temp_user", "show_reg", "error_count", "cevap_dogru", "pito_mod", "current_code", "user_num", "in_review"]
for k in keys:
    if k not in st.session_state:
        if k in ["user", "temp_user"]: st.session_state[k] = None
        elif k in ["error_count", "user_num"]: st.session_state[k] = 0
        elif k in ["show_reg", "cevap_dogru", "in_review"]: st.session_state[k] = False
        elif k == "pito_mod": st.session_state[k] = "merhaba"
        else: st.session_state[k] = ""

# --- 4. İLERLEME VE KAYIT SİSTEMİ ---
def ilerleme_kaydet(puan, kod, egz_id, n_id, n_m):
    yeni_xp = int(st.session_state.user['toplam_puan']) + puan
    r_ad, _ = ranks.rütbe_ata(yeni_xp)
    
    # Veritabanını mühürle
    supabase.table("kullanicilar").update({
        "toplam_puan": yeni_xp, "mevcut_egzersiz": str(n_id), "mevcut_modul": int(n_m), "rutbe": r_ad
    }).eq("ogrenci_no", int(st.session_state.user['ogrenci_no'])).execute()
    
    # Egzersiz kaydını logla
    supabase.table("egzersiz_kayitlari").insert({
        "ogrenci_no": int(st.session_state.user['ogrenci_no']), "egz_id": str(egz_id), "alinan_puan": int(puan), "basarili_kod": str(kod)
    }).execute()
    
    # State'i güncelle
    st.session_state.user.update({"toplam_puan": yeni_xp, "mevcut_egzersiz": str(n_id), "mevcut_modul": int(n_m), "rutbe": r_ad})
    st.session_state.error_count, st.session_state.cevap_dogru, st.session_state.pito_mod, st.session_state.current_code = 0, False, "merhaba", ""
    st.rerun()

# --- 5. ANA PROGRAM AKIŞI ---
try:
    with open('mufredat.json', 'r', encoding='utf-8') as f:
        mufredat = json.load(f)['pito_akademi_mufredat']
except:
    st.error("mufredat.json bulunamadı!"); st.stop()

if st.session_state.user is None:
    # --- GİRİŞ KAPISI (pito_merhaba.gif ile karşılar) ---
    auth.login_ekrani(supabase, st.session_state.pito_messages, lambda: load_pito("merhaba"), 
                      lambda: ranks.liderlik_tablosu_goster(supabase))

else:
    u = st.session_state.user
    m_idx = int(u['mevcut_modul']) - 1
    total_m = len(mufredat)
    msgs = st.session_state.pito_messages
    ad_k = u['ad_soyad'].split()[0]

    # --- ÜST NAVİGASYON (İNCELEME BUTONU) ---
    c_nav1, c_nav2 = st.columns([4, 1])
    with c_nav2:
        if st.button("🔍 İnceleme Modu"):
            st.session_state.in_review = True
            st.rerun()

    # --- DURUM YÖNETİMİ ---
    if st.session_state.in_review:
        mechanics.inceleme_modu_paneli(u, mufredat, load_pito)
    elif m_idx >= total_m:
        # MEZUNİYET: pito_mezun.gif ve balonlar/karlar
        mechanics.mezuniyet_ekrani(u, msgs, load_pito, supabase)
    else:
        # --- EĞİTİM AKIŞI ---
        st.markdown(f"<div class='progress-label'><span>🎓 Akademi Yolculuğu</span><span>Modül {m_idx + 1} / {total_m}</span></div>", unsafe_allow_html=True)
        st.progress(min((m_idx) / total_m, 1.0))

        modul = mufredat[m_idx]
        egz = next((e for e in modul['egzersizler'] if e['id'] == str(u['mevcut_egzersiz'])), modul['egzersizler'][0])
        c_i, t_i = modul['egzersizler'].index(egz) + 1, len(modul['egzersizler'])
        
        st.markdown(f"<div class='progress-label'><span>🗺️ Modül Görevleri</span><span>{c_i} / {t_i} Görev</span></div>", unsafe_allow_html=True)
        st.progress(c_i / t_i)

        cl, cr = st.columns([7, 3])
        with cl:
            rn, rc = ranks.rütbe_ata(u['toplam_puan'])
            st.markdown(f"<div class='hero-panel'><h3>🚀 {modul['modul_adi']}</h3><p>{u['ad_soyad']} | <span class='rank-badge' style='background:black; color:#ADFF2F;'>{rn}</span></p></div>", unsafe_allow_html=True)
            
            with st.expander("📖 KONU ANLATIMI", expanded=True):
                st.markdown(f"<div style='background:#000; padding:15px; border-radius:10px;'>{modul.get('pito_anlatimi', '...')}</div>", unsafe_allow_html=True)
            
            p_xp = max(0, 20 - (st.session_state.error_count * 5))
            st.markdown(f'<div style="background:#161b22; padding:12px; border-radius:12px; border:1px solid #ADFF2F; color:#ADFF2F; font-weight:bold;">💎 {p_xp} XP | ⚠️ Hata: {st.session_state.error_count}/4</div>', unsafe_allow_html=True)
            
            # --- PİTO DUYGU MOTORU ---
            if st.session_state.cevap_dogru:
                st.session_state.pito_mod = "basari"
            elif st.session_state.error_count in [1, 2, 3]:
                st.session_state.pito_mod = "hata"
            elif st.session_state.error_count >= 4:
                st.session_state.pito_mod = "dusunuyor"
            else:
                st.session_state.pito_mod = "merhaba"

            cp1, cp2 = st.columns([1, 2])
            with cp1:
                load_pito(st.session_state.pito_mod)
            with cp2:
                if st.session_state.error_count > 0:
                    lvl = f"level_{min(st.session_state.error_count, 4)}"
                    msg = random.choice(msgs['errors'][lvl]).format(ad_k)
                    st.error(f"🚨 Pito: {msg}")
                    if st.session_state.error_count == 3:
                        st.warning(f"💡 İpucu: {egz['ipucu']}")
                else:
                    st.markdown(f"<div class='pito-notu'>💬 <b>Pito:</b> {msgs['welcome'].format(ad_k)}</div>", unsafe_allow_html=True)

            # --- ETKİLEŞİM ALANI ---
            if not st.session_state.cevap_dogru and st.session_state.error_count < 4:
                st.markdown(f"<div class='gorev-box'><span class='gorev-label'>📍 GÖREV {egz['id']}</span><div class='gorev-text'>{egz['yonerge']}</div></div>", unsafe_allow_html=True)
                k_i = st.text_area("Pito Kod Editörü:", value=egz['sablon'], height=150)
                if st.button("Kodu Kontrol Et 🔍"):
                    st.session_state.current_code = k_i
                    if normalize(k_i) == normalize(egz['dogru_cevap_kodu']):
                        st.session_state.cevap_dogru = True
                    else:
                        st.session_state.error_count += 1
                    st.rerun()
            elif st.session_state.cevap_dogru:
                st.success(f"✅ {random.choice(msgs['success']).format(ad_k, p_xp)}")
                st.markdown(f"<div class='console-box'>💻 Senin Çıktın:<br>> {egz['beklenen_cikti']}</div>", unsafe_allow_html=True)
                if st.button("Sonraki Göreve Geç ➡️"):
                    s_idx = modul['egzersizler'].index(egz) + 1
                    n_id, n_m = (modul['egzersizler'][s_idx]['id'], u['mevcut_modul']) if s_idx < len(modul['egzersizler']) else (f"{u['mevcut_modul']+1}.1", u['mevcut_modul'] + 1)
                    ilerleme_kaydet(p_xp, st.session_state.current_code, egz['id'], n_id, n_m)
            elif st.session_state.error_count >= 4:
                with st.expander("📖 PİTO'NUN KESİN ÇÖZÜMÜ", expanded=True):
                    st.code(egz['cozum'], language="python")
                    st.markdown(f"<div class='console-box'>💻 Beklenen Çıktı:<br>> {egz['beklenen_cikti']}</div>", unsafe_allow_html=True)
                if st.button("Sıradaki Göreve Geç ➡️"):
                    s_idx = modul['egzersizler'].index(egz) + 1
                    n_id, n_m = (modul['egzersizler'][s_idx]['id'], u['mevcut_modul']) if s_idx < len(modul['egzersizler']) else (f"{u['mevcut_modul']+1}.1", u['mevcut_modul'] + 1)
                    ilerleme_kaydet(0, "Çözüm İncelendi", egz['id'], n_id, n_m)
        
        with cr:
            # Liderlik tablosu her zaman güncel kalır
            ranks.liderlik_tablosu_goster(supabase, current_user=u)
