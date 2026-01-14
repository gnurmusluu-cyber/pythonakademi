import streamlit as st
import random
import os
import base64

def egitim_ekrani(u, mufredat, msgs, emotions_module, ranks_module, ilerleme_fonksiyonu, normalize_fonksiyonu, supabase):
    # --- 0. SİBER-GÖRSEL ZIRH (ANIMASYON, MOBİL UYUM VE OKUNABİLİRLİK) ---
    st.markdown('''
        <style>
        /* STREAMLIT STANDARTLARINI İMHA ET */
        header[data-testid="stHeader"], [data-testid="stDecoration"], footer { display: none !important; }
        .stApp { background-color: #0e1117 !important; }

        /* BAŞLIK GÖRÜNÜRLÜK GARANTİSİ (HUD ALTINDA KALMAYI ÖNLER) */
        [data-testid="stMainViewContainer"] { padding-top: 170px !important; }

        /* SABİT ÜST HUD BAR */
        .cyber-hud {
            position: fixed; top: 0; left: 0; right: 0;
            height: 110px; background-color: #0e1117 !important;
            border-bottom: 3px solid #00E5FF; z-index: 99999 !important;
            padding: 0 30px; display: flex; justify-content: space-between; align-items: center;
            box-shadow: 0 10px 30px #000000 !important;
        }

        /* PİTO KOKPİT GÖRSELİ */
        .hud-pito-gif img {
            width: 80px; height: 80px; border-radius: 50%; border: 3px solid #00E5FF;
            object-fit: cover; background: #000; margin-right: 15px;
            box-shadow: 0 0 15px #00E5FF;
        }

        /* --- SİBER-VURGU (DOUBLE PULSE PROTOKOLÜ) --- */
        @keyframes cyberPulse {
            0% { transform: scale(1); color: #00E5FF; text-shadow: none; }
            50% { transform: scale(1.8); color: #FF0000; text-shadow: 0 0 25px #FF0000, 0 0 50px #FF0000; }
            100% { transform: scale(1); color: #00E5FF; text-shadow: none; }
        }

        /* Wildcard selector: pulse-err- veya pulse-xp- ile başlayan her şeyi canlandır */
        [class^="pulse-err-"], [class^="pulse-xp-"] {
            display: inline-block;
            animation: cyberPulse 0.7s ease-in-out;
            font-weight: 950 !important;
        }

        /* MOBİL DÜZENLEME */
        @media (max-width: 768px) {
            .cyber-hud { height: 160px !important; flex-direction: column; justify-content: center; padding: 10px; }
            .hud-pito-gif img { width: 60px !important; height: 60px !important; margin-right: 0; margin-bottom: 5px; }
            .hud-item { font-size: 0.85rem !important; margin: 3px 5px !important; }
            [data-testid="stMainViewContainer"] { padding-top: 240px !important; } 
        }

        /* OKUNABİLİR BUTONLAR (SİYAH METİN) */
        div.stButton > button { background-color: #00E5FF !important; border: none !important; transition: 0.3s; }
        div.stButton > button p, div.stButton > button span { color: #000000 !important; font-weight: 900 !important; }
        div.stButton > button:hover { background-color: #ADFF2F !important; }

        .hud-item { color: #E0E0E0; font-family: 'Fira Code', monospace; font-size: 0.95rem; margin: 0 12px; }
        .hud-v { color: #00E5FF; font-weight: bold; text-shadow: 0 0 8px #00E5FF; }

        .console-box {
            background-color: #000 !important; color: #ADFF2F !important;
            border: 1px solid #333; border-radius: 10px;
            padding: 15px; font-family: 'Courier New', monospace; margin: 15px 0;
        }
        * :focus { outline: none !important; box-shadow: none !important; }
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

    # DİNAMİK ANİMASYON TETİKLEYİCİSİ (Her seferinde benzersiz class basarak animasyonu zorlar)
    e_count = st.session_state.error_count
    r_id = random.randint(0, 9999) # Her interaction'da animasyonu tazelemek için
    err_display = f'<span class="pulse-err-{e_count}-{r_id}">{e_count}</span>' if e_count > 0 else '0'
    xp_display = f'<span class="pulse-xp-{e_count}-{r_id}">{p_xp}</span>' if e_count > 0 else f'{p_xp}'

    # HUD HTML
    st.markdown(f'''
        <div class="cyber-hud">
            <div style="display: flex; align-items: center; flex-direction: inherit;">
                <div class="hud-pito-gif"><img src="{pito_gif_base64}"></div>
                <div class="hud-item">👤 <span class="hud-v">{u['ad_soyad']}</span></div>
            </div>
            <div style="display: flex; align-items: center; flex-wrap: wrap; justify-content: center;">
                <div class="hud-item">💎 Potansiyel: <span class="hud-v">{xp_display} XP</span></div>
                <div class="hud-item">⚠️ Hata: <span class="hud-v">{err_display}/4</span></div>
                <div class="hud-item">🏆 Toplam: <span class="hud-v">{int(u['toplam_puan'])} XP</span></div>
            </div>
        </div>
    ''', unsafe_allow_html=True)

    # --- 2. ANA BAŞLIK VE İLERLEME ---
    st.markdown(f"<h1 style='text-align:center; color:#00E5FF; text-shadow: 0 0 15px #00E5FF; margin-bottom:30px;'>🎓 PİTO PYTHON AKADEMİ</h1>", unsafe_allow_html=True)

    m_idx = int(u['mevcut_modul']) - 1
    total_m = 10 
    ad_k = u['ad_soyad'].split()[0]
    modul = mufredat[m_idx]
    egz = next((e for e in modul['egzersizler'] if e['id'] == str(u['mevcut_egzersiz'])), modul['egzersizler'][0])

    # TEK İLERLEME ÇUBUĞU (10 MODÜL)
    c_i = modul['egzersizler'].index(egz) + 1
    overall_progress = (m_idx + (c_i / len(modul['egzersizler']))) / total_m

    st.markdown(f'''
        <div style="display: flex; justify-content: space-between; color: #00E5FF; font-weight: bold; font-size: 0.9rem; margin-bottom: 5px;">
            <span>🚀 Akademi Yolculuğu (Toplam {total_m} Modül)</span>
            <span>📍 {m_idx + 1}. modülün {c_i}. görevi</span>
        </div>
    ''', unsafe_allow_html=True)
    st.progress(min(overall_progress, 1.0))

    st.markdown("<br>", unsafe_allow_html=True)
    cl, cr = st.columns([7.5, 2.5])
    
    with cl:
        c_nav = st.columns([0.4, 0.4, 0.2])
        with c_nav[0]: st.markdown(f"💬 *{msgs['welcome'].format(ad_k)}*")
        with c_nav[1]:
            if st.button("🔍 Geçmiş egzersizler", use_container_width=True, key="rev_edu"):
                st.session_state.in_review = True; st.rerun()
        with c_nav[2]:
            if st.button("🚪 Çıkış", use_container_width=True, key="exit_edu"):
                st.session_state.user = None; st.rerun()

        with st.expander(f"📖 {modul['modul_adi']}", expanded=True):
            st.markdown(f"<div style='background:rgba(0,229,255,0.03); padding:15px; border-radius:10px;'>{modul['pito_anlatimi']}</div>", unsafe_allow_html=True)
            st.markdown(f"### 🎯 GÖREV {egz['id']}")
            st.info(egz['yonerge'])

        # --- 3. EDİTÖR VE HATA MANTIĞI ---
        if not st.session_state.cevap_dogru and st.session_state.error_count < 4:
            if st.session_state.error_count > 0:
                lvl = f"level_{min(st.session_state.error_count, 4)}"
                st.error(f"🚨 **Pito:** {random.choice(msgs['errors'][lvl]).format(ad_k)}")
                if st.session_state.error_count == 3: st.warning(f"💡 **İpucu:** {egz.get('ipucu', '... ')}")

            if "reset_trigger" not in st.session_state: st.session_state.reset_trigger = 0
            user_code = st.text_area("Siber-Editor", value=egz['sablon'], height=180, key=f"ed_{egz['id']}_{st.session_state.reset_trigger}", label_visibility="collapsed")
            
            b_btns = st.columns([4, 1.2])
            with b_btns[0]:
                if st.button("KODU KONTROL ET 🚀", type="primary", use_container_width=True):
                    st.session_state.current_code = user_code
                    if normalize_fonksiyonu(user_code) == normalize_fonksiyonu(egz['dogru_cevap_kodu']):
                        st.session_state.cevap_dogru = True; st.balloons(); st.rerun()
                    else: st.session_state.error_count += 1; st.rerun()
            with b_btns[1]:
                if st.button("🔄 SIFIRLA", use_container_width=True):
                    st.session_state.reset_trigger += 1; st.rerun()

        elif st.session_state.cevap_dogru:
            st.markdown("💻 **Konsol Çıktısı:**")
            st.markdown(f"<div class='console-box'>{egz.get('beklenen_cikti', '...')}</div>", unsafe_allow_html=True)
            st.success(f"✅ Harika iş {ad_k}! (+{p_xp} XP)")
            if st.button("SIRADAKİ GÖREVE GEÇ ➡️", type="primary", use_container_width=True):
                s_idx = modul['egzersizler'].index(egz) + 1
                n_id, n_m = (modul['egzersizler'][s_idx]['id'], u['mevcut_modul']) if s_idx < len(modul['egzersizler']) else (f"{int(u['mevcut_modul'])+1}.1", int(u['mevcut_modul']) + 1)
                ilerleme_fonksiyonu(p_xp, st.session_state.current_code, egz['id'], n_id, n_m)

        elif st.session_state.error_count >= 4:
            # --- 4. HATA: ÖZEL MESAJ MÜHRÜ ---
            st.warning("🚨 Bu egzersizden puan alamadın çözümü incele ve devam et")
            st.code(egz['cozum'], language="python")
            st.markdown(f"<div class='console-box'>{egz.get('beklenen_cikti', '...')}</div>", unsafe_allow_html=True)
            if st.button("DEVAM ET ➡️", type="primary", use_container_width=True):
                s_idx = modul['egzersizler'].index(egz) + 1
                n_id, n_m = (modul['egzersizler'][s_idx]['id'], u['mevcut_modul']) if s_idx < len(modul['egzersizler']) else (f"{int(u['mevcut_modul'])+1}.1", int(u['mevcut_modul']) + 1)
                ilerleme_fonksiyonu(0, "Çözüm İncelendi", egz['id'], n_id, n_m)

    with cr:
        ranks_module.liderlik_tablosu_goster(supabase, current_user=u)
