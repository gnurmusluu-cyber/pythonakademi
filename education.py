import streamlit as st
import random

def egitim_ekrani(u, mufredat, msgs, emotions_module, ranks_module, ilerleme_fonksiyonu, normalize_fonksiyonu, supabase):
    # --- 0. SİBER-BUZ (ELECTRIC BLUE) KOKPİT CSS ---
    st.markdown('''
        <style>
        .stApp { background-color: #0e1117; }
        
        /* Akademi Başlığı */
        .academy-header {
            text-align: center; color: #00E5FF; font-family: 'Fira Code', monospace;
            font-size: 2.2rem; font-weight: bold; letter-spacing: 2px;
            text-shadow: 0 0 20px rgba(0, 229, 255, 0.4);
            margin-bottom: 20px; border-bottom: 2px solid rgba(0, 229, 255, 0.2);
            padding-bottom: 10px;
        }

        /* Kokpit Göstergeleri */
        .kokpit-label { color: #00E5FF; font-family: 'Fira Code', monospace; font-size: 0.85rem; font-weight: bold; margin-bottom: 5px; }
        .stProgress > div > div > div > div { background-image: linear-gradient(to right, #00B8D4, #00E5FF) !important; }
        
        /* Modern Siber Kartlar */
        .cyber-card {
            background: rgba(0, 229, 255, 0.03);
            border: 1px solid rgba(0, 229, 255, 0.2);
            border-radius: 15px; padding: 20px; margin-bottom: 15px;
        }

        /* Siyah Konsol Kutusu */
        .console-box {
            background-color: #000000 !important;
            color: #00E5FF !important;
            border: 1px solid #333;
            border-radius: 8px;
            padding: 15px;
            font-family: 'Courier New', monospace;
            margin: 10px 0;
        }

        /* Neon Editör */
        .stTextArea textarea {
            background-color: #161b22 !important;
            color: #00E5FF !important;
            border: 1px solid #00E5FF !important;
            border-radius: 12px !important;
            font-family: 'Fira Code', monospace !important;
            font-size: 1.05rem !important;
            box-shadow: inset 0 0 15px rgba(0, 229, 255, 0.1) !important;
        }

        /* Siber-Punk Sıfırla Butonu */
        button[kind="secondary"] {
            border: 2px solid #00E5FF !important;
            color: #00E5FF !important;
            background: rgba(0, 229, 255, 0.05) !important;
            border-radius: 10px !important;
            font-weight: bold !important;
            transition: 0.3s;
        }
        button[kind="secondary"]:hover {
            box-shadow: 0 0 20px #00E5FF !important;
            background: rgba(0, 229, 255, 0.15) !important;
        }
        </style>
    ''', unsafe_allow_html=True)

    # --- 1. AKADEMİ BAŞLIĞI ---
    st.markdown("<div class='academy-header'>🎓 PİTO PYTHON AKADEMİ</div>", unsafe_allow_html=True)

    # --- VERİ VE KONUM HAZIRLIĞI ---
    m_idx = int(u['mevcut_modul']) - 1
    total_m = len(mufredat)
    ad_k = u['ad_soyad'].split()[0]
    modul = mufredat[m_idx]
    egz = next((e for e in modul['egzersizler'] if e['id'] == str(u['mevcut_egzersiz'])), modul['egzersizler'][0])
    c_i, t_i = modul['egzersizler'].index(egz) + 1, len(modul['egzersizler'])

    # --- 2. ÜST PANEL: İLERLEME GÖSTERGELERİ ---
    col_acad, col_mod = st.columns(2)
    with col_acad:
        st.markdown(f"<div class='kokpit-label'>🚀 AKADEMİ YOLCULUĞU (%{int((m_idx/total_m)*100)})</div>", unsafe_allow_html=True)
        st.progress(min((m_idx) / total_m, 1.0))
    with col_mod:
        # Netleştirilmiş Modül ve Görev Takibi
        st.markdown(f"<div class='kokpit-label'>📍 MODÜL {m_idx + 1} - GÖREV {c_i} / {t_i}</div>", unsafe_allow_html=True)
        st.progress(c_i / t_i)

    st.markdown("<br>", unsafe_allow_html=True)

    # --- 3. ANA DÜZEN (7:3) ---
    main_col, side_col = st.columns([7.2, 2.8])
    
    with main_col:
        # Pito Bilgi Paneli
        p_xp = max(0, 20 - (st.session_state.error_count * 5))
        p_mod = emotions_module.pito_durum_belirle(st.session_state.error_count, st.session_state.cevap_dogru)
        
        c_pito, c_info = st.columns([1, 4])
        with c_pito: emotions_module.pito_goster(p_mod)
        with c_info:
            st.markdown(f"💎 **{p_xp} XP** | ⚠️ **Hata: {st.session_state.error_count}/4**")
            st.markdown(f"<div style='color:#00E5FF; font-style:italic;'>💬 {msgs['welcome'].format(ad_k)}</div>", unsafe_allow_html=True)

        # Konu Anlatımı ve Görev Alanı
        with st.expander(f"📖 {modul['modul_adi']}", expanded=True):
            st.markdown(f"<div class='cyber-card'>{modul['pito_anlatimi']}</div>", unsafe_allow_html=True)
            st.markdown(f"### 🎯 GÖREV {egz['id']}")
            st.info(egz['yonerge'])

        # --- 4. EDİTÖR VE KONSOL AKIŞI ---
        if not st.session_state.cevap_dogru and st.session_state.error_count < 4:
            # Hata ve İpucu (Tam Editör Üzerinde)
            if st.session_state.error_count > 0:
                st.error(f"🚨 **Pito:** {random.choice(msgs['errors'][f'level_{min(st.session_state.error_count, 4)}']).format(ad_k)}")
                if st.session_state.error_count == 3:
                    st.warning(f"💡 **İPUCU:** {egz.get('ipucu', 'Kodu tekrar kontrol et!')}")

            # Editör Alanı
            if "reset_trigger" not in st.session_state: st.session_state.reset_trigger = 0
            user_code = st.text_area("Siber-Editor", value=egz['sablon'], height=180, 
                                     key=f"final_ux_{egz['id']}_{st.session_state.reset_trigger}", label_visibility="collapsed")

            b_run, b_res = st.columns([4, 1.5])
            with b_run:
                if st.button("KODU KONTROL ET 🚀", type="primary", use_container_width=True):
                    st.session_state.current_code = user_code
                    if normalize_fonksiyonu(user_code) == normalize_fonksiyonu(egz['dogru_cevap_kodu']):
                        st.session_state.cevap_dogru = True
                        st.balloons() # Kutlama balonları sadece "başarı anında" uçar
                    else:
                        st.session_state.error_count += 1
                    st.rerun()
            with b_res:
                if st.button("🔄 SIFIRLA", type="secondary", use_container_width=True):
                    st.session_state.reset_trigger += 1; st.rerun()

        # BAŞARI DURUMU: Konsol çıktısı ve devam butonu
        elif st.session_state.cevap_dogru:
            st.markdown("💻 **Konsol Çıktısı:**")
            st.markdown(f"<div class='console-box'>{egz.get('beklenen_cikti', 'Kod başarıyla çalıştırıldı...')}</div>", unsafe_allow_html=True)
            st.success(f"✅ Harika iş çıkardın {ad_k}! Kodun siber-onay aldı.")
            if st.button("SIRADAKİ GÖREVE GEÇ ➡️", type="primary", use_container_width=True):
                s_idx = modul['egzersizler'].index(egz) + 1
                n_id, n_m = (modul['egzersizler'][s_idx]['id'], u['mevcut_modul']) if s_idx < len(modul['egzersizler']) else (f"{int(u['mevcut_modul'])+1}.1", int(u['mevcut_modul']) + 1)
                ilerleme_fonksiyonu(p_xp, st.session_state.current_code, egz['id'], n_id, n_m)

        # HATA SINIRI: Kesin çözüm ve Konsol çıktısı
        elif st.session_state.error_count >= 4:
            st.warning("🚨 Limit doldu! Pito'nun ideal çözümü ve çıktısı:")
            st.code(egz['cozum'], language="python")
            st.markdown("💻 **Kodun Çıktısı:**")
            st.markdown(f"<div class='console-box'>{egz.get('beklenen_cikti', 'Çıktı üretiliyor...')}</div>", unsafe_allow_html=True)
            if st.button("ANLADIM, DEVAM ET ➡️", type="primary", use_container_width=True):
                s_idx = modul['egzersizler'].index(egz) + 1
                n_id, n_m = (modul['egzersizler'][s_idx]['id'], u['mevcut_modul']) if s_idx < len(modul['egzersizler']) else (f"{int(u['mevcut_modul'])+1}.1", int(u['mevcut_modul']) + 1)
                ilerleme_fonksiyonu(0, "Çözüm İncelendi", egz['id'], n_id, n_m)

    with side_col:
        # LİDERLİK TABLOSU (Sağ Kanatta Sabit)
        st.markdown("<div style='text-align:center; color:#00E5FF; font-weight:bold; font-size:1.1rem;'>🏆 ONUR KÜRSÜSÜ</div>", unsafe_allow_html=True)
        ranks_module.liderlik_tablosu_goster(supabase, current_user=u)
