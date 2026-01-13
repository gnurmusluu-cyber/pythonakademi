import streamlit as st
import random

def egitim_ekrani(u, mufredat, msgs, emotions_module, ranks_module, ilerleme_fonksiyonu, normalize_fonksiyonu, supabase):
    """
    Referans kod destekli eğitim motoru. 
    Öğrenci editörü bozsa bile görev kutusundaki kopyaya bakarak düzeltebilir.
    """
    
    m_idx = int(u['mevcut_modul']) - 1
    total_m = len(mufredat)
    ad_k = u['ad_soyad'].split()[0]

    # --- 1. ÜST PANEL (İLERLEME) ---
    st.markdown(f"<div class='progress-label'><span>🎓 Akademi Yolculuğu</span><span>Modül {m_idx + 1} / {total_m}</span></div>", unsafe_allow_html=True)
    st.progress(min((m_idx) / total_m, 1.0))

    modul = mufredat[m_idx]
    egz = next((e for e in modul['egzersizler'] if e['id'] == str(u['mevcut_egzersiz'])), modul['egzersizler'][0])
    
    cl, cr = st.columns([7, 3])
    with cl:
        # Pito ve Durum Bilgisi
        p_xp = max(0, 20 - (st.session_state.error_count * 5))
        p_mod = emotions_module.pito_durum_belirle(st.session_state.error_count, st.session_state.cevap_dogru)
        
        cp1, cp2 = st.columns([1, 3])
        with cp1: emotions_module.pito_goster(p_mod)
        with cp2:
            st.markdown(f"💎 **{p_xp} XP** | ⚠️ **Hata: {st.session_state.error_count}/4**")
            if st.session_state.error_count > 0:
                lvl = f"level_{min(st.session_state.error_count, 4)}"
                st.error(f"🚨 Pito: {random.choice(msgs['errors'][lvl]).format(ad_k)}")
            else:
                st.markdown(f"<div class='pito-notu'>💬 <b>Pito:</b> {msgs['welcome'].format(ad_k)}</div>", unsafe_allow_html=True)

        # --- 2. GÖREV VE REFERANS ALANI ---
        if not st.session_state.cevap_dogru and st.session_state.error_count < 4:
            with st.container():
                # Görev Yönergesi
                st.markdown(f"""
                    <div class='gorev-box'>
                        <span class='gorev-label'>📍 GÖREV {egz['id']}</span>
                        <div class='gorev-text'>{egz['yonerge']}</div>
                    </div>
                """, unsafe_allow_html=True)
                
                # YENİ: İskelet Referans Kutusu (Silinme riskine karşı sabit kopya)
                with st.expander("🔍 KOD İSKELETİNE BAK (REFERANS)", expanded=True):
                    st.info("Eğer aşağıdaki editörü yanlışlıkla bozarsan, buradaki kopyaya bakarak düzeltebilirsin.")
                    st.code(egz['sablon'], language="python")

            # --- 3. SERBEST EDİTÖR ---
            st.markdown("💻 **Senin Editörün (Hemen aşağıya kodla):**")
            
            # Hafıza yönetimi: Egzersiz değiştiğinde editörü sıfırla
            if "current_edit_val" not in st.session_state or st.session_state.get("last_egz_id") != egz['id']:
                st.session_state.current_edit_val = egz['sablon']
                st.session_state.last_egz_id = egz['id']

            user_code = st.text_area(
                "Editor",
                value=st.session_state.current_edit_val,
                height=180,
                key=f"edit_{egz['id']}",
                label_visibility="collapsed"
            )

            c_btn1, c_btn2 = st.columns([4, 1])
            with c_btn1:
                if st.button("Kodu Çalıştır ve Kontrol Et 🚀", use_container_width=True):
                    st.session_state.current_edit_val = user_code
                    if normalize_fonksiyonu(user_code) == normalize_fonksiyonu(egz['dogru_cevap_kodu']):
                        st.session_state.cevap_dogru = True
                    else:
                        st.session_state.error_count += 1
                    st.rerun()
            with c_btn2:
                if st.button("🔄 Sıfırla"):
                    st.session_state.current_edit_val = egz['sablon']
                    st.rerun()

        # --- BAŞARI VE HATA DURUMLARI (Standart Akış) ---
        elif st.session_state.cevap_dogru:
            st.success(f"✅ Müthişsin {ad_k}! Kodun onaylandı.")
            st.code(user_code if 'user_code' in locals() else st.session_state.current_edit_val, language="python")
            if st.button("Sonraki Göreve Geç ➡️", use_container_width=True):
                st.session_state.current_edit_val = None
                s_idx = modul['egzersizler'].index(egz) + 1
                n_id, n_m = (modul['egzersizler'][s_idx]['id'], u['mevcut_modul']) if s_idx < len(modul['egzersizler']) else (f"{int(u['mevcut_modul'])+1}.1", int(u['mevcut_modul']) + 1)
                ilerleme_fonksiyonu(p_xp, user_code if 'user_code' in locals() else st.session_state.current_edit_val, egz['id'], n_id, n_m)
        
        elif st.session_state.error_count >= 4:
            st.warning("🚨 Pito: 'Biraz takıldın sanki, sorun değil! İşte ideal çözüm:'")
            st.code(egz['cozum'], language="python")
            if st.button("Sıradaki Göreve Geç ➡️", use_container_width=True):
                st.session_state.current_edit_val = None
                s_idx = modul['egzersizler'].index(egz) + 1
                n_id, n_m = (modul['egzersizler'][s_idx]['id'], u['mevcut_modul']) if s_idx < len(modul['egzersizler']) else (f"{int(u['mevcut_modul'])+1}.1", int(u['mevcut_modul']) + 1)
                ilerleme_fonksiyonu(0, "Çözüm İncelendi", egz['id'], n_id, n_m)

    with cr:
        ranks_module.liderlik_tablosu_goster(supabase, current_user=u)
