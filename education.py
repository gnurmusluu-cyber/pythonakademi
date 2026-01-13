import streamlit as st
import random

def egitim_ekrani(u, mufredat, msgs, emotions_module, ranks_module, ilerleme_fonksiyonu, normalize_fonksiyonu, supabase):
    # --- 0. SİBER-ESTETİK (ICE-BLUE) UX CSS ---
    st.markdown("""
        <style>
        .stApp { background-color: #0e1117; }
        .kokpit-label { color: #00E5FF; font-family: 'Fira Code', monospace; font-size: 0.8rem; font-weight: bold; margin-bottom: 2px; }
        .stProgress > div > div > div > div { background-image: linear-gradient(to right, #00B8D4, #00E5FF) !important; }
        
        /* Modern Kart Yapısı */
        .cyber-card {
            background: rgba(0, 229, 255, 0.03);
            border: 1px solid rgba(0, 229, 255, 0.15);
            border-radius: 12px;
            padding: 15px; margin-bottom: 15px;
        }

        /* Neon Editör ve Yazılar */
        .stTextArea textarea {
            background-color: #161b22 !important;
            color: #00E5FF !important;
            border: 1px solid #00E5FF !important;
            border-radius: 10px !important;
            font-size: 1rem !important;
        }

        /* Sıfırla Butonu - Özel Tasarım */
        .stButton > button[kind="secondary"] {
            border: 2px solid #00E5FF !important;
            color: #00E5FF !important;
            background: rgba(0, 229, 255, 0.05) !important;
            border-radius: 10px !important;
            font-weight: bold !important;
            transition: 0.3s;
        }
        .stButton > button[kind="secondary"]:hover {
            box-shadow: 0 0 15px #00E5FF !important;
            background: rgba(0, 229, 255, 0.1) !important;
        }
        </style>
    """, unsafe_allow_html=True)

    # --- VERİ HAZIRLIĞI ---
    m_idx = int(u['mevcut_modul']) - 1
    total_m = len(mufredat)
    ad_k = u['ad_soyad'].split()[0]
    modul = mufredat[m_idx]
    egz = next((e for e in modul['egzersizler'] if e['id'] == str(u['mevcut_egzersiz'])), modul['egzersizler'][0])
    c_i, t_i = modul['egzersizler'].index(egz) + 1, len(modul['egzersizler'])

    # --- 1. ÜST PANEL: ÇİFTLİ İLERLEME GÖSTERGELERİ ---
    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown(f"<div class='kokpit-label'>🎓 AKADEMİ YOLCULUĞU (%{int((m_idx/total_m)*100)})</div>", unsafe_allow_html=True)
        st.progress(min((m_idx) / total_m, 1.0))
    with col_b:
        st.markdown(f"<div class='kokpit-label'>📍 MODÜL GÖREVİ ({c_i} / {t_i})</div>", unsafe_allow_html=True)
        st.progress(c_i / t_i)

    st.markdown("<br>", unsafe_allow_html=True)

    # --- 2. ANA DÜZEN (7:3) ---
    cl, cr = st.columns([7.2, 2.8])

    with cl:
        # Pito ve Durum Kartı
        p_xp = max(0, 20 - (st.session_state.error_count * 5))
        p_mod = emotions_module.pito_durum_belirle(st.session_state.error_count, st.session_state.cevap_dogru)
        
        c_pito, c_status = st.columns([1, 4])
        with c_pito: emotions_module.pito_goster(p_mod)
        with c_status:
            st.markdown(f"💎 **{p_xp} XP** | ⚠️ **Hata: {st.session_state.error_count}/4**")
            st.markdown(f"<div style='color:#00E5FF; font-style:italic;'>💬 {msgs['welcome'].format(ad_k)}</div>", unsafe_allow_html=True)

        # Konu Anlatımı ve Görev (Tek Kartta Kompakt)
        with st.expander(f"📖 {modul['modul_adi']}", expanded=True):
            st.markdown(modul.get('pito_anlatimi', '...'))
            st.markdown(f"<div class='cyber-card' style='margin-top:10px;'>🎯 <b>GÖREV:</b> {egz['yonerge']}</div>", unsafe_allow_html=True)

        # --- 3. KRİTİK ALAN: HATA MESAJI VE EDİTÖR ---
        if not st.session_state.cevap_dogru and st.session_state.error_count < 4:
            
            # Hata Mesajı Tam Editör Üstünde
            if st.session_state.error_count > 0:
                st.error(f"🚨 **Pito:** {random.choice(msgs['errors'][f'level_{min(st.session_state.error_count, 4)}']).format(ad_k)}")
                if st.session_state.error_count == 3:
                    st.warning(f"💡 **İPUCU:** {egz.get('ipucu', 'Kodu tekrar kontrol et!')}")

            # Editör
            if "reset_trigger" not in st.session_state: st.session_state.reset_trigger = 0
            user_code = st.text_area("Siber-Editor", value=egz['sablon'], height=160, 
                                     key=f"final_ux_{egz['id']}_{st.session_state.reset_trigger}", label_visibility="collapsed")

            b_check, b_reset = st.columns([4, 1.5])
            with b_check:
                if st.button("KODU KONTROL ET 🚀", use_container_width=True):
                    st.session_state.current_code = user_code
                    if normalize_fonksiyonu(user_code) == normalize_fonksiyonu(egz['dogru_cevap_kodu']):
                        st.session_state.cevap_dogru = True
                    else:
                        st.session_state.error_count += 1
                    st.rerun()
            with b_reset:
                if st.button("🔄 SIFIRLA", kind="secondary", use_container_width=True):
                    st.session_state.reset_trigger += 1
                    st.rerun()

        # Başarı ve Hata Akışları
        elif st.session_state.cevap_dogru:
            st.success(f"✅ Harika iş çıkardın {ad_k}!")
            if st.button("SONRAKİ GÖREVE GEÇ ➡️", use_container_width=True):
                s_idx = modul['egzersizler'].index(egz) + 1
                n_id, n_m = (modul['egzersizler'][s_idx]['id'], u['mevcut_modul']) if s_idx < len(modul['egzersizler']) else (f"{int(u['mevcut_modul'])+1}.1", int(u['mevcut_modul']) + 1)
                ilerleme_fonksiyonu(p_xp, st.session_state.current_code, egz['id'], n_id, n_m)
        
        elif st.session_state.error_count >= 4:
            st.warning("🚨 Limit doldu! Pito'nun çözümünü incele:")
            st.code(egz['cozum'], language="python")
            if st.button("ANLADIM, DEVAM ET ➡️", use_container_width=True):
                s_idx = modul['egzersizler'].index(egz) + 1
                n_id, n_m = (modul['egzersizler'][s_idx]['id'], u['mevcut_modul']) if s_idx < len(modul['egzersizler']) else (f"{int(u['mevcut_modul'])+1}.1", int(u['mevcut_modul']) + 1)
                ilerleme_fonksiyonu(0, "Çözüm İncelendi", egz['id'], n_id, n_m)

    with cr:
        # LİDERLİK TABLOSU (Sağda Sabit ve Neon Başlıklı)
        st.markdown("<div style='text-align:center; color:#00E5FF; font-weight:bold; font-size:1.1rem;'>🏆 ONUR KÜRSÜSÜ</div>", unsafe_allow_html=True)
        ranks_module.liderlik_tablosu_goster(supabase, current_user=u)
