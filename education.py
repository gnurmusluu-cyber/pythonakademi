import streamlit as st
import random

def egitim_ekrani(u, mufredat, msgs, emotions_module, ranks_module, ilerleme_fonksiyonu, normalize_fonksiyonu, supabase):
    """
    Referans kod destekli ve sıfırlama özellikli eğitim motoru.
    Öğrenci editörü bozsa bile yukarıdaki kopyaya bakabilir veya tek tuşla sıfırlayabilir.
    """
    
    # --- 0. SİBER-EDİTÖR CSS ZIRHI ---
    st.markdown("""
        <style>
        /* Textarea'yı gerçek bir siber-editör gibi göster */
        div[data-testid="stTextArea"] textarea {
            background-color: #0e1117 !important;
            color: #ADFF2F !important;
            font-family: 'Courier New', Courier, monospace !important;
            border: 1px solid #ADFF2F !important;
            border-radius: 10px !important;
            padding: 15px !important;
            line-height: 1.5 !important;
        }
        /* Odaklandığında parlasın */
        div[data-testid="stTextArea"] textarea:focus {
            border-color: #ffffff !important;
            box-shadow: 0 0 10px #ADFF2F !important;
        }
        </style>
    """, unsafe_allow_html=True)

    m_idx = int(u['mevcut_modul']) - 1
    total_m = len(mufredat)
    ad_k = u['ad_soyad'].split()[0]

    # --- 1. ÜST İLERLEME GÖSTERGELERİ ---
    st.markdown(f"<div class='progress-label'><span>🎓 Akademi Yolculuğu</span><span>Modül {m_idx + 1} / {total_m}</span></div>", unsafe_allow_html=True)
    st.progress(min((m_idx) / total_m, 1.0))

    modul = mufredat[m_idx]
    egz = next((e for e in modul['egzersizler'] if e['id'] == str(u['mevcut_egzersiz'])), modul['egzersizler'][0])
    c_i, t_i = modul['egzersizler'].index(egz) + 1, len(modul['egzersizler'])
    
    st.markdown(f"<div class='progress-label'><span>🗺️ Modül Görevleri</span><span>{c_i} / {t_i} Görev</span></div>", unsafe_allow_html=True)
    st.progress(c_i / t_i)

    # --- 2. ANA EĞİTİM ALANI ---
    cl, cr = st.columns([7, 3])
    with cl:
        # Hero Panel: Öğrenci Bilgisi
        rn, rc = ranks_module.rütbe_ata(u['toplam_puan'])
        st.markdown(f"<div class='hero-panel'><h3>🚀 {modul['modul_adi']}</h3><p>{u['ad_soyad']} | <span class='rank-badge' style='background:black; color:#ADFF2F;'>{rn}</span></p></div>", unsafe_allow_html=True)
        
        with st.expander("📖 KONU ANLATIMI", expanded=True):
            st.markdown(f"<div style='background:#000; padding:15px; border-radius:10px; border-left: 4px solid #ADFF2F;'>{modul.get('pito_anlatimi', '...')}</div>", unsafe_allow_html=True)
        
        # XP ve Hata Paneli
        p_xp = max(0, 20 - (st.session_state.error_count * 5))
        st.markdown(f'<div style="background:#161b22; padding:12px; border-radius:12px; border:1px solid #ADFF2F; color:#ADFF2F; font-weight:bold; text-align:center;">💎 Kazanılacak: {p_xp} XP | ⚠️ Hatalar: {st.session_state.error_count}/4</div>', unsafe_allow_html=True)
        
        # Pito Duygu Motoru
        p_mod = emotions_module.pito_durum_belirle(st.session_state.error_count, st.session_state.cevap_dogru)
        cp1, cp2 = st.columns([1, 2])
        with cp1: emotions_module.pito_goster(p_mod)
        with cp2:
            if st.session_state.error_count > 0:
                lvl = f"level_{min(st.session_state.error_count, 4)}"
                msg = random.choice(msgs['errors'][lvl]).format(ad_k)
                st.error(f"🚨 Pito: {msg}")
                if st.session_state.error_count == 3: st.warning(f"💡 İpucu: {egz['ipucu']}")
            else:
                st.markdown(f"<div class='pito-notu'>💬 <b>Pito:</b> {msgs['welcome'].format(ad_k)}</div>", unsafe_allow_html=True)

        # --- 3. GÖREV VE AKILLI EDİTÖR ---
        if not st.session_state.cevap_dogru and st.session_state.error_count < 4:
            # Görev Yönergesi
            st.markdown(f"<div class='gorev-box'><span class='gorev-label'>📍 GÖREV {egz['id']}</span><div class='gorev-text'>{egz['yonerge']}</div></div>", unsafe_allow_html=True)
            
            # REFERANS KUTUSU (Silinme riskine karşı beton iskelet)
            with st.expander("🔍 Orijinal Kod Şablonu (Referans)", expanded=False):
                st.info("Eğer editörü bozarsan buradaki kopyaya bakarak düzeltebilirsin.")
                st.code(egz['sablon'], language="python")
            
            # SIFIRLAMA MEKANİZMASI
            if "reset_trigger" not in st.session_state:
                st.session_state.reset_trigger = 0

            st.markdown("💻 **Senin Editörün:**")
            user_code = st.text_area(
                "Editor", 
                value=egz['sablon'], 
                height=180, 
                key=f"editor_{egz['id']}_{st.session_state.reset_trigger}", 
                label_visibility="collapsed"
            )

            # KOMUT PANELİ
            col_btn1, col_btn2 = st.columns([4, 1])
            with col_btn1:
                if st.button("Kodu Kontrol Et 🔍", use_container_width=True):
                    st.session_state.current_code = user_code
                    if normalize_fonksiyonu(user_code) == normalize_fonksiyonu(egz['dogru_cevap_kodu']):
                        st.session_state.cevap_dogru = True
                    else:
                        st.session_state.error_count += 1
                    st.rerun()
            with col_btn2:
                if st.button("🔄 Sıfırla", use_container_width=True, help="Kod alanını orijinal şablona döndür"):
                    st.session_state.reset_trigger += 1
                    st.rerun()
        
        # BAŞARI DURUMU
        elif st.session_state.cevap_dogru:
            st.success(f"✅ Harika iş çıkardın {ad_k}! Kodun siber-onay aldı.")
            if st.button("Sonraki Göreve Geç ➡️", use_container_width=True):
                s_idx = modul['egzersizler'].index(egz) + 1
                n_id, n_m = (modul['egzersizler'][s_idx]['id'], u['mevcut_modul']) if s_idx < len(modul['egzersizler']) else (f"{int(u['mevcut_modul'])+1}.1", int(u['mevcut_modul']) + 1)
                ilerleme_fonksiyonu(p_xp, st.session_state.current_code, egz['id'], n_id, n_m)
        
        # 4 HATA DURUMU
        elif st.session_state.error_count >= 4:
            st.warning("🚨 Biraz takıldın, ama sorun değil. İşte Pito'nun çözüm yolu:")
            with st.expander("📖 PİTO'NUN KESİN ÇÖZÜMÜ", expanded=True):
                st.code(egz['cozum'], language="python")
            if st.button("Sıradaki Göreve Geç (0 XP) ➡️", use_container_width=True):
                s_idx = modul['egzersizler'].index(egz) + 1
                n_id, n_m = (modul['egzersizler'][s_idx]['id'], u['mevcut_modul']) if s_idx < len(modul['egzersizler']) else (f"{int(u['mevcut_modul'])+1}.1", int(u['mevcut_modul']) + 1)
                ilerleme_fonksiyonu(0, "Çözüm İncelendi", egz['id'], n_id, n_m)

    with cr:
        ranks_module.liderlik_tablosu_goster(supabase, current_user=u)
