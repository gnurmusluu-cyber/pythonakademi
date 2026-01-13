import streamlit as st
import random
import os
import base64

def egitim_ekrani(u, mufredat, msgs, emotions_module, ranks_module, ilerleme_fonksiyonu, normalize_fonksiyonu, supabase):
    # --- 0. SİBER-HUD VE OPAK ZIRH CSS (HAYALET GÖRÜNTÜ ÖNLEYİCİ) ---
    st.markdown('''
        <style>
        /* 1. STREAMLIT VARSAYILANLARINI İMHA ET */
        header[data-testid="stHeader"] { visibility: hidden; height: 0px; display: none; }
        #MainMenu { visibility: hidden; }
        footer { visibility: hidden; }
        
        /* 2. ANA UYGULAMA ZEMİNİNİ SABİTLE */
        .stApp { 
            background-color: #0e1117 !important; 
        }
        
        /* 3. SIDEBAR STABİLİZASYONU (OPAKLIK ZIRHI) */
        [data-testid="stSidebar"] {
            min-width: 320px !important;
            max-width: 320px !important;
            background-color: #161b22 !important; /* Sidebar da tamamen opak */
            border-right: 2px solid #00E5FF;
            opacity: 1 !important;
        }

        /* 4. SABİT ÜST HUD BAR (TAM OPAK - SIFIR GEÇİRGENLİK) */
        .cyber-hud {
            position: fixed; 
            top: 0; 
            left: 0; 
            width: 100%;
            background-color: #0e1117 !important; /* Kesinlikle opak siyah-buz */
            border-bottom: 2px solid #00E5FF;
            z-index: 9999999 !important; /* En üst katmana mühürle */
            padding: 10px 25px;
            display: flex; 
            justify-content: space-between; 
            align-items: center;
            /* Blur (bulanıklık) efektini kaldırdık çünkü şeffaflık hissi yaratıyor */
            box-shadow: 0 15px 35px rgba(0, 0, 0, 1) !important; 
            height: 85px; /* Yüksekliği sabitle */
        }

        /* 5. PITO KOKPİT GÖRSELİ */
        .hud-pito-gif img {
            width: 70px; 
            height: 70px;
            border-radius: 50%; 
            border: 3px solid #00E5FF;
            object-fit: cover; 
            background: #000;
            margin-right: 15px;
        }

        /* 6. METİN VE VERİ ÖGELERİ */
        .hud-item { color: #E0E0E0; font-family: 'Fira Code', monospace; font-size: 0.95rem; margin: 0 10px; }
        .hud-v { color: #00E5FF; font-weight: bold; text-shadow: 0 0 8px #00E5FF; }

        /* 7. ANA İÇERİK KAYDIRMA (HUD ALTINDA KALMAMASI İÇİN) */
        .main-container { 
            margin-top: 105px !important; /* HUD yüksekliğinden fazla boşluk bırak */
            padding: 20px;
            background-color: #0e1117 !important;
        }

        /* MOBİL UYUMLULUK */
        @media (max-width: 768px) {
            .cyber-hud { padding: 5px 10px; justify-content: center; height: auto; }
            .main-container { margin-top: 150px !important; }
            .hud-pito-gif img { width: 55px; height: 55px; }
        }
        </style>
    ''', unsafe_allow_html=True)

    # --- 1. HUD VERİLERİ VE PİTO GIF HAZIRLIĞI ---
    p_xp = max(0, 20 - (st.session_state.error_count * 5))
    p_mod = emotions_module.pito_durum_belirle(st.session_state.error_count, st.session_state.cevap_dogru)
    
    # Base64 dönüşümü (HUD içinde GIF için)
    def get_base64_gif(mod):
        path = os.path.join(os.path.dirname(__file__), "assets", f"pito_{mod}.gif")
        if os.path.exists(path):
            with open(path, "rb") as f:
                encoded = base64.b64encode(f.read()).decode()
            return f"data:image/gif;base64,{encoded}"
        return ""

    pito_gif = get_base64_gif(p_mod)

    # KOKPİT (HUD) HTML ÇIKTISI
    st.markdown(f'''
        <div class="cyber-hud">
            <div style="display: flex; align-items: center;">
                <div class="hud-pito-gif"><img src="{pito_gif}" alt="Pito"></div>
                <div class="hud-item">👤 <span class="hud-v">{u['ad_soyad']}</span></div>
            </div>
            <div style="display: flex; align-items: center; flex-wrap: wrap; justify-content: center;">
                <div class="hud-item">💎 Potansiyel: <span class="hud-v">{p_xp} XP</span></div>
                <div class="hud-item">⚠️ Hata: <span class="hud-v">{st.session_state.error_count}/4</span></div>
                <div class="hud-item">🏆 Toplam: <span class="hud-v">{int(u['toplam_puan'])} XP</span></div>
            </div>
        </div>
    ''', unsafe_allow_html=True)

    # --- 2. ANA İÇERİK ---
    st.markdown('<div class="main-container">', unsafe_allow_html=True)
    st.markdown(f"<h1 style='text-align:center; color:#00E5FF; text-shadow: 0 0 15px #00E5FF;'>🎓 PİTO PYTHON AKADEMİ</h1>", unsafe_allow_html=True)

    m_idx = int(u['mevcut_modul']) - 1
    modul = mufredat[m_idx]
    egz = next((e for e in modul['egzersizler'] if e['id'] == str(u['mevcut_egzersiz'])), modul['egzersizler'][0])
    ad_k = u['ad_soyad'].split()[0]

    # İlerleme Göstergeleri
    c1, c2 = st.columns(2)
    with c1: st.progress(min((m_idx) / len(mufredat), 1.0)); st.caption("Akademi İlerlemesi")
    with c2: st.progress((modul['egzersizler'].index(egz) + 1) / len(modul['egzersizler'])); st.caption("Modül Görevi")

    st.markdown("<br>", unsafe_allow_html=True)
    cl, cr = st.columns([7.5, 2.5])
    
    with cl:
        # Pito Mesajı ve Navigasyon
        msg_col, nav_col = st.columns([0.7, 0.3])
        with msg_col:
            st.markdown(f"<div style='color:#00E5FF; font-style:italic; font-size:1.1rem;'>💬 {msgs['welcome'].format(ad_k)}</div>", unsafe_allow_html=True)
        with nav_col:
            if st.button("🔍 Önceki egzersizleri incele", use_container_width=True, key="rev_btn"):
                st.session_state.in_review = True; st.rerun()

        with st.expander(f"📖 {modul['modul_adi']}", expanded=True):
            st.markdown(modul['pito_anlatimi'])
            st.markdown(f"### 🎯 GÖREV {egz['id']}")
            st.info(egz['yonerge'])

        # --- EDİTÖR ---
        if not st.session_state.cevap_dogru and st.session_state.error_count < 4:
            if st.session_state.error_count > 0:
                st.error(f"🚨 Pito: {random.choice(msgs['errors'][f'level_{min(st.session_state.error_count, 4)}']).format(ad_k)}")
            
            user_code = st.text_area("Siber-Editor", value=egz['sablon'], height=180, key=f"ed_{egz['id']}", label_visibility="collapsed")
            
            b1, b2 = st.columns([4, 1])
            with b1:
                if st.button("KODU KONTROL ET 🚀", type="primary", use_container_width=True):
                    st.session_state.current_code = user_code
                    if normalize_fonksiyonu(user_code) == normalize_fonksiyonu(egz['dogru_cevap_kodu']):
                        st.session_state.cevap_dogru = True; st.balloons()
                    else: st.session_state.error_count += 1
                    st.rerun()
            with b2:
                if st.button("🔄", help="Sıfırla", use_container_width=True): st.rerun()

        elif st.session_state.cevap_dogru:
            st.success(f"✅ Harika iş çıkardın {ad_k}!")
            if st.button("SIRADAKİ GÖREVE GEÇ ➡️", type="primary", use_container_width=True):
                s_idx = modul['egzersizler'].index(egz) + 1
                n_id, n_m = (modul['egzersizler'][s_idx]['id'], u['mevcut_modul']) if s_idx < len(modul['egzersizler']) else (f"{int(u['mevcut_modul'])+1}.1", int(u['mevcut_modul']) + 1)
                ilerleme_fonksiyonu(p_xp, st.session_state.current_code, egz['id'], n_id, n_m)

        elif st.session_state.error_count >= 4:
            st.warning("🚨 Çözümü incele ve devam et:")
            st.code(egz['cozum'])
            if st.button("DEVAM ET ➡️", type="primary", use_container_width=True):
                s_idx = modul['egzersizler'].index(egz) + 1
                n_id, n_m = (modul['egzersizler'][s_idx]['id'], u['mevcut_modul']) if s_idx < len(modul['egzersizler']) else (f"{int(u['mevcut_modul'])+1}.1", int(u['mevcut_modul']) + 1)
                ilerleme_fonksiyonu(0, "İncelendi", egz['id'], n_id, n_m)

    with cr:
        ranks_module.liderlik_tablosu_goster(supabase, current_user=u)

    st.markdown('</div>', unsafe_allow_html=True)
