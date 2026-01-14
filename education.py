import streamlit as st
import random
import os
import base64

def egitim_ekrani(u, mufredat, msgs, emotions_module, ranks_module, ilerleme_fonksiyonu, normalize_fonksiyonu, supabase):
    # --- 0. SİBER-BETON CSS (MOBİL OPTİMİZE EDİLMİŞ) ---
    st.markdown('''
        <style>
        /* STREAMLIT VARSAYILANLARINI KÖKTEN SİL */
        header[data-testid="stHeader"] { display: none !important; }
        [data-testid="stDecoration"] { display: none !important; }
        footer { display: none !important; }
        
        .stApp { background-color: #0e1117 !important; }

        /* FİZİKSEL ENGEL: İçeriği HUD'ın arkasına asla sokma */
        [data-testid="stMainViewContainer"] {
            padding-top: 110px !important;
        }

        /* SIDEBAR STABİLİZASYONU */
        [data-testid="stSidebar"] {
            min-width: 320px !important;
            max-width: 320px !important;
            background-color: #161b22 !important;
            border-right: 2px solid #00E5FF;
        }

        /* SABİT ÜST HUD BAR (SIFUR SIZINTI ZIRHI) */
        .cyber-hud {
            position: fixed; top: 0; left: 0; right: 0;
            height: 110px;
            background-color: #0e1117 !important; /* TAM OPAK */
            border-bottom: 3px solid #00E5FF;
            z-index: 10000000 !important;
            padding: 0 30px;
            display: flex; justify-content: space-between; align-items: center;
            box-shadow: 0 20px 50px #000000 !important;
        }

        /* PITO KOKPİT GÖRSELİ (80px) */
        .hud-pito-gif img {
            width: 80px; height: 80px;
            border-radius: 50%; border: 3px solid #00E5FF;
            object-fit: cover; background: #000;
            margin-right: 20px;
            box-shadow: 0 0 15px #00E5FF;
        }

        .hud-item { color: #E0E0E0; font-family: 'Fira Code', monospace; font-size: 1rem; margin: 0 15px; }
        .hud-v { color: #00E5FF; font-weight: bold; text-shadow: 0 0 10px #00E5FF; }

        /* --- SİBER-MOBİL DÜZENLEME (SIKIŞMAYI ÖNLEYEN MÜHÜR) --- */
        @media (max-width: 768px) {
            .cyber-hud { 
                padding: 10px; 
                flex-direction: column;
                justify-content: center; 
                height: 150px !important; /* Yükseklik esnetildi */
            }
            [data-testid="stMainViewContainer"] { padding-top: 165px !important; }
            .hud-pito-gif img { 
                width: 65px !important; 
                height: 65px !important; 
                margin-right: 0;
                margin-bottom: 8px;
            }
            .hud-item { font-size: 0.85rem !important; margin: 2px 5px !important; }
        }

        .main-container { position: relative; z-index: 1; padding: 10px; }

        .console-box {
            background-color: #000 !important; color: #ADFF2F !important;
            border: 1px solid #333; border-radius: 8px;
            padding: 15px; font-family: 'Courier New', monospace; margin: 10px 0;
            box-shadow: 0 0 10px rgba(173, 255, 47, 0.2);
        }
        </style>
    ''', unsafe_allow_html=True)

    # --- 1. HUD VERİLERİ VE PİTO GIF HAZIRLIĞI ---
    p_xp = max(0, 20 - (st.session_state.error_count * 5))
    p_mod = emotions_module.pito_durum_belirle(st.session_state.error_count, st.session_state.cevap_dogru)
    
    def get_base64_gif(mod):
        path = os.path.join(os.path.dirname(__file__), "assets", f"pito_{mod}.gif")
        if os.path.exists(path):
            with open(path, "rb") as f:
                encoded = base64.b64encode(f.read()).decode()
            return f"data:image/gif;base64,{encoded}"
        return ""

    pito_gif_base64 = get_base64_gif(p_mod)

    # KOKPİT (HUD) HTML ÇIKTISI
    st.markdown(f'''
        <div class="cyber-hud">
            <div style="display: flex; align-items: center; flex-direction: inherit;">
                <div class="hud-pito-gif"><img src="{pito_gif_base64}" alt="Pito"></div>
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
    st.markdown(f"<h1 style='text-align:center; color:#00E5FF; text-shadow: 0 0 15px #00E5FF; margin-bottom:30px;'>🎓 PİTO PYTHON AKADEMİ</h1>", unsafe_allow_html=True)

    m_idx = int(u['mevcut_modul']) - 1
    total_m = len(mufredat)
    ad_k = u['ad_soyad'].split()[0]
    modul = mufredat[m_idx]
    egz = next((e for e in modul['egzersizler'] if e['id'] == str(u['mevcut_egzersiz'])), modul['egzersizler'][0])

    # İlerleme Barları
    col_p1, col_p2 = st.columns(2)
    with col_p1:
        st.markdown(f"<div style='color:#00E5FF; font-weight:bold; font-size:0.85rem;'>🚀 AKADEMİ: %{int((m_idx/total_m)*100)}</div>", unsafe_allow_html=True)
        st.progress(min((m_idx) / total_m, 1.0))
    with col_p2:
        st.markdown(f"<div style='color:#00E5FF; font-weight:bold; font-size:0.85rem;'>📍 MODÜL {m_idx + 1} - GÖREV {modul['egzersizler'].index(egz) + 1}/{len(modul['egzersizler'])}</div>", unsafe_allow_html=True)
        st.progress((modul['egzersizler'].index(egz) + 1) / len(modul['egzersizler']))

    st.markdown("<br>", unsafe_allow_html=True)
    cl, cr = st.columns([7.5, 2.5])
    
    with cl:
        c_msg, c_rev, c_exit = st.columns([0.45, 0.35, 0.2])
        with c_msg: st.markdown(f"<div style='color:#00E5FF; font-style:italic; font-size:1.1rem;'>💬 {msgs['welcome'].format(ad_k)}</div>", unsafe_allow_html=True)
        with c_rev:
            if st.button("🔍 Geçmiş egzersizler", use_container_width=True, key="rev_btn_master"):
                st.session_state.in_review = True; st.rerun()
        with c_exit:
            if st.button("🚪 Çıkış", help="Oturumu kapat", use_container_width=True, key="exit_btn_master"):
                st.session_state.user = None
                st.session_state.in_review = False; st.rerun()

        with st.expander(f"📖 {modul['modul_adi']}", expanded=True):
            st.markdown(f"<div style='background:rgba(0,229,255,0.03); padding:15px; border-radius:10px;'>{modul['pito_anlatimi']}</div>", unsafe_allow_html=True)
            st.markdown(f"### 🎯 GÖREV {egz['id']}")
            st.info(egz['yonerge'])

        # --- EDİTÖR VE KONTROL AKIŞI ---
        if not st.session_state.cevap_dogru and st.session_state.error_count < 4:
            if st.session_state.error_count > 0:
                st.error(f"🚨 **Pito:** {random.choice(msgs['errors'][f'level_{min(st.session_state.error_count, 4)}']).format(ad_k)}")
                if st.session_state.error_count == 3:
                    st.warning(f"💡 **Pito'nun İpucu:** {egz.get('ipucu', 'Kodu tekrar kontrol et!')}")

            if "reset_trigger" not in st.session_state: st.session_state.reset_trigger = 0
            user_code = st.text_area("Siber-Editor", value=egz['sablon'], height=180, key=f"ed_{egz['id']}_{st.session_state.reset_trigger}", label_visibility="collapsed")
            
            b1, b2 = st.columns([4, 1.2])
            with b1:
                if st.button("KODU KONTROL ET 🚀", type="primary", use_container_width=True):
                    st.session_state.current_code = user_code
                    if normalize_fonksiyonu(user_code) == normalize_fonksiyonu(egz['dogru_cevap_kodu']):
                        st.session_state.cevap_dogru = True; st.balloons()
                    else: st.session_state.error_count += 1
                    st.rerun()
            with b2:
                if st.button("🔄 SIFIRLA", use_container_width=True):
                    st.session_state.reset_trigger += 1; st.rerun()

        elif st.session_state.cevap_dogru:
            st.markdown("💻 **Konsol Çıktısı:**")
            st.markdown(f"<div class='console-box'>{egz.get('beklenen_cikti', '...')}</div>", unsafe_allow_html=True)
            st.success(f"✅ Harika iş çıkardın {ad_k}! (+{p_xp} XP)")
            if st.button("SIRADAKİ GÖREVE GEÇ ➡️", type="primary", use_container_width=True):
                s_idx = modul['egzersizler'].index(egz) + 1
                n_id, n_m = (modul['egzersizler'][s_idx]['id'], u['mevcut_modul']) if s_idx < len(modul['egzersizler']) else (f"{int(u['mevcut_modul'])+1}.1", int(u['mevcut_modul']) + 1)
                ilerleme_fonksiyonu(p_xp, st.session_state.current_code, egz['id'], n_id, n_m)

        elif st.session_state.error_count >= 4:
            st.warning("🚨 Limit doldu! Çözümü incele:")
            st.code(egz['cozum'], language="python")
            st.markdown(f"<div class='console-box'>{egz.get('beklenen_cikti', '...')}</div>", unsafe_allow_html=True)
            if st.button("DEVAM ET ➡️", type="primary", use_container_width=True):
                s_idx = modul['egzersizler'].index(egz) + 1
                n_id, n_m = (modul['egzersizler'][s_idx]['id'], u['mevcut_modul']) if s_idx < len(modul['egzersizler']) else (f"{int(u['mevcut_modul'])+1}.1", int(u['mevcut_modul']) + 1)
                ilerleme_fonksiyonu(0, "Çözüm İncelendi", egz['id'], n_id, n_m)

    with cr:
        ranks_module.liderlik_tablosu_goster(supabase, current_user=u)

    st.markdown('</div>', unsafe_allow_html=True)
