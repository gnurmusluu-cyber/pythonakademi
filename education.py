import streamlit as st
import random

def egitim_ekrani(u, mufredat, msgs, emotions_module, ranks_module, ilerleme_fonksiyonu, normalize_fonksiyonu, supabase):
    # --- 0. SİBER-ESTETİK (ICE-BLUE) CSS MÜHRÜ ---
    st.markdown("""
        <style>
        .stApp { background-color: #0e1117; }
        
        /* Kokpit Göstergeleri */
        .kokpit-label { color: #00E5FF; font-family: 'Fira Code', monospace; font-size: 0.85rem; font-weight: bold; margin-bottom: 2px; }
        .stProgress > div > div > div > div { background-image: linear-gradient(to right, #00B8D4, #00E5FF) !important; }
        
        /* Modern Kart Yapısı */
        .cyber-card {
            background: rgba(0, 229, 255, 0.03);
            border: 1px solid rgba(0, 229, 255, 0.2);
            border-radius: 15px;
            padding: 20px;
            margin-bottom: 15px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.3);
        }
        
        /* Neon Editör */
        .stTextArea textarea {
            background-color: #161b22 !important;
            color: #00E5FF !important;
            border: 1px solid #00E5FF !important;
            border-radius: 12px !important;
            font-size: 1rem !important;
            line-height: 1.6 !important;
            box-shadow: inset 0 0 10px rgba(0, 229, 255, 0.1) !important;
        }

        /* Özel Vurgular */
        .status-text { font-size: 0.9rem; color: #E0E0E0; }
        .blue-highlight { color: #00E5FF; font-weight: bold; }
        </style>
    """, unsafe_allow_html=True)

    m_idx = int(u['mevcut_modul']) - 1
    total_m = len(mufredat)
    ad_k = u['ad_soyad'].split()[0]
    modul = mufredat[m_idx]
    egz = next((e for e in modul['egzersizler'] if e['id'] == str(u['mevcut_egzersiz'])), modul['egzersizler'][0])
    c_i, t_i = modul['egzersizler'].index(egz) + 1, len(modul['egzersizler'])

    # --- 1. ÜST KOKPİT (İLERLEME ÇUBUKLARI) ---
    col_acad, col_mod = st.columns(2)
    with col_acad:
        st.markdown(f"<div class='kokpit-label'>🎓 AKADEMİ YOLCULUĞU (%{int((m_idx/total_m)*100)})</div>", unsafe_allow_html=True)
        st.progress(min((m_idx) / total_m, 1.0))
    with col_mod:
        st.markdown(f"<div class='kokpit-label'>🗺️ MODÜL GÖREVİ ({c_i} / {t_i})</div>", unsafe_allow_html=True)
        st.progress(c_i / t_i)

    st.markdown("<br>", unsafe_allow_html=True)

    # --- 2. ANA PANEL DÜZENİ ---
    main_col, side_col = st.columns([7, 3])
    
    with main_col:
        # Pito Durum ve XP Kartı
        p_xp = max(0, 20 - (st.session_state.error_count * 5))
        p_mod = emotions_module.pito_durum_belirle(st.session_state.error_count, st.session_state.cevap_dogru)
        
        with st.container():
            c_pito, c_info = st.columns([1, 4])
            with c_pito: emotions_module.pito_goster(p_mod)
            with c_info:
                st.markdown(f"""
                    <div style='margin-top: 10px;'>
                        <span class='status-text'>💎 Kazanç: <span class='blue-highlight'>{p_xp} XP</span></span> | 
                        <span class='status-text'>⚠️ Hata: <span class='blue-highlight'>{st.session_state.error_count}/4</span></span>
                    </div>
                """, unsafe_allow_html=True)
                if st.session_state.error_count > 0:
                    st.error(f"**Pito:** {random.choice(msgs['errors'][f'level_{min(st.session_state.error_count, 4)}']).format(ad_k)}")
                else:
                    st.markdown(f"<div style='color:#00E5FF; font-style: italic;'>💬 {msgs['welcome'].format(ad_k)}</div>", unsafe_allow_html=True)

        # Görev ve Editör Alanı
        if not st.session_state.cevap_dogru and st.session_state.error_count < 4:
            st.markdown(f"### 📍 GÖREV {egz['id']}")
            
            # Konu Anlatımı ve Yönerge (Kompakt Kart İçinde)
            with st.container():
                st.markdown(f"""<div class='cyber-card'>
                    <b style='color:#00E5FF;'>KONU:</b> {modul['pito_anlatimi']}<br><br>
                    <b style='color:#00E5FF;'>GÖREV:</b> {egz['yonerge']}
                </div>""", unsafe_allow_html=True)
            
            # Editör Sıfırlama Mekanizması
            if "reset_trigger" not in st.session_state: st.session_state.reset_trigger = 0

            user_code = st.text_area(
                "Siber Editör", 
                value=egz['sablon'], 
                height=180, 
                key=f"pro_ed_{egz['id']}_{st.session_state.reset_trigger}", 
                label_visibility="collapsed"
            )

            # Komut Butonları
            b_run, b_reset = st.columns([4, 1])
            with b_run:
                if st.button("KODU MÜHÜRLE VE GÖNDER 🚀", use_container_width=True):
                    st.session_state.current_code = user_code
                    if normalize_fonksiyonu(user_code) == normalize_fonksiyonu(egz['dogru_cevap_kodu']):
                        st.session_state.cevap_dogru = True
                    else:
                        st.session_state.error_count += 1
                    st.rerun()
            with b_reset:
                if st.button("🔄", help="Kod Şablonuna Geri Dön", use_container_width=True):
                    st.session_state.reset_trigger += 1
                    st.rerun()

        # Başarı Ekranı
        elif st.session_state.cevap_dogru:
            st.balloons()
            st.success(f"✅ Harika iş çıkardın {ad_k}! Kodun siber-onay aldı.")
            if st.button("SIRADAKİ GÖREVE ATLA ➡️", use_container_width=True):
                s_idx = modul['egzersizler'].index(egz) + 1
                n_id, n_m = (modul['egzersizler'][s_idx]['id'], u['mevcut_modul']) if s_idx < len(modul['egzersizler']) else (f"{int(u['mevcut_modul'])+1}.1", int(u['mevcut_modul']) + 1)
                ilerleme_fonksiyonu(p_xp, st.session_state.current_code, egz['id'], n_id, n_m)

        # 4 Hata - Çözüm Ekranı
        elif st.session_state.error_count >= 4:
            st.warning("🚨 Biraz zorlandın ama sorun değil! İşte Pito'nun ideal çözümü:")
            st.code(egz['cozum'], language="python")
            if st.button("ÇÖZÜMÜ ANLADIM, DEVAM ET ➡️", use_container_width=True):
                s_idx = modul['egzersizler'].index(egz) + 1
                n_id, n_m = (modul['egzersizler'][s_idx]['id'], u['mevcut_modul']) if s_idx < len(modul['egzersizler']) else (f"{int(u['mevcut_modul'])+1}.1", int(u['mevcut_modul']) + 1)
                ilerleme_fonksiyonu(0, "Çözüm İncelendi", egz['id'], n_id, n_m)

    # --- 3. SAĞ KANAT (LİDERLİK TABLOSU) ---
    with side_col:
        st.markdown("<div style='text-align:center; color:#00E5FF; font-weight:bold; margin-bottom:10px;'>🏆 ONUR KÜRSÜSÜ</div>", unsafe_allow_html=True)
        ranks_module.liderlik_tablosu_goster(supabase, current_user=u)
