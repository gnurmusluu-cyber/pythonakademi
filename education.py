import streamlit as st
import random

def egitim_ekrani(u, mufredat, msgs, emotions_module, ranks_module, ilerleme_fonksiyonu, normalize_fonksiyonu, supabase):
    """Canlı Önizleme ve Dinamik Boşluk Doldurma Motoru."""
    
    m_idx = int(u['mevcut_modul']) - 1
    total_m = len(mufredat)
    ad_k = u['ad_soyad'].split()[0]

    # --- ÜST İLERLEME ---
    st.markdown(f"<div class='progress-label'><span>🎓 Akademi Yolculuğu</span><span>Modül {m_idx + 1} / {total_m}</span></div>", unsafe_allow_html=True)
    st.progress(min((m_idx) / total_m, 1.0))

    modul = mufredat[m_idx]
    egz = next((e for e in modul['egzersizler'] if e['id'] == str(u['mevcut_egzersiz'])), modul['egzersizler'][0])
    
    cl, cr = st.columns([7, 3])
    with cl:
        rn, rc = ranks_module.rütbe_ata(u['toplam_puan'])
        st.markdown(f"<div class='hero-panel'><h3>🚀 {modul['modul_adi']}</h3><p>{u['ad_soyad']} | <span class='rank-badge' style='background:black; color:#ADFF2F;'>{rn}</span></p></div>", unsafe_allow_html=True)
        
        with st.expander("📖 KONU ANLATIMI", expanded=True):
            st.markdown(f"<div style='background:#000; padding:15px; border-radius:10px; border-left: 4px solid #ADFF2F;'>{modul.get('pito_anlatimi', '...')}</div>", unsafe_allow_html=True)
        
        # XP Formülü: $XP = \max(0, 20 - (\text{Hata} \times 5))$
        p_xp = max(0, 20 - (st.session_state.error_count * 5))
        st.markdown(f'<div style="background:#161b22; padding:12px; border-radius:12px; border:1px solid #ADFF2F; color:#ADFF2F; font-weight:bold; text-align:center;">💎 Kazanılacak: {p_xp} XP | ⚠️ Hatalar: {st.session_state.error_count}/4</div>', unsafe_allow_html=True)
        
        # Pito Etkileşim
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

        # --- CANLI ÖNİZLEME EDİTÖRÜ ---
        if not st.session_state.cevap_dogru and st.session_state.error_count < 4:
            st.markdown(f"<div class='gorev-box'><span class='gorev-label'>📍 GÖREV {egz['id']}</span><div class='gorev-text'>{egz['yonerge']}</div></div>", unsafe_allow_html=True)
            
            sablon = egz.get('sablon', '')
            blanks_count = sablon.count("___")
            
            st.info("💡 Yukarıdaki kod iskeletine göre boşlukları doldur.")
            
            # 1. Aşama: İskeleti Göster (Salt Okunur)
            st.markdown("📑 **Kod İskeleti:**")
            st.code(sablon, language="python")
            
            # 2. Aşama: Giriş Alanları
            user_inputs = []
            cols = st.columns(blanks_count if blanks_count > 0 else 1)
            for i in range(blanks_count):
                with cols[i]:
                    ans = st.text_input(f"Boşluk {i+1}", key=f"inp_{egz['id']}_{i}", placeholder="...")
                    user_inputs.append(ans)
            
            # 3. Aşama: Canlı Birleştirme ve Önizleme
            final_code = sablon
            for val in user_inputs:
                final_code = final_code.replace("___", val if val else "___", 1)
            
            st.markdown("💻 **Senin Oluşturduğun Kod:**")
            st.code(final_code, language="python")
            
            if st.button("Kodu Çalıştır ve Kontrol Et 🔍", use_container_width=True):
                st.session_state.current_code = final_code
                if normalize_fonksiyonu(final_code) == normalize_fonksiyonu(egz['dogru_cevap_kodu']):
                    st.session_state.cevap_dogru = True
                else:
                    st.session_state.error_count += 1
                st.rerun()

        # Başarı ve Hata durumları (Mevcut yapı korunur...)
        elif st.session_state.cevap_dogru:
            st.success(f"✅ Harika! Kod tıkır tıkır çalışıyor.")
            if st.button("Sonraki Göreve Geç ➡️", use_container_width=True):
                s_idx = modul['egzersizler'].index(egz) + 1
                n_id, n_m = (modul['egzersizler'][s_idx]['id'], u['mevcut_modul']) if s_idx < len(modul['egzersizler']) else (f"{int(u['mevcut_modul'])+1}.1", int(u['mevcut_modul']) + 1)
                ilerleme_fonksiyonu(p_xp, st.session_state.current_code, egz['id'], n_id, n_m)
        
        elif st.session_state.error_count >= 4:
            st.warning("🚨 Çok zorlandın, Pito senin için çözümü hazırladı.")
            st.code(egz['cozum'], language="python")
            if st.button("Sıradaki Göreve Geç ➡️", use_container_width=True):
                s_idx = modul['egzersizler'].index(egz) + 1
                n_id, n_m = (modul['egzersizler'][s_idx]['id'], u['mevcut_modul']) if s_idx < len(modul['egzersizler']) else (f"{int(u['mevcut_modul'])+1}.1", int(u['mevcut_modul']) + 1)
                ilerleme_fonksiyonu(0, "Çözüm İncelendi", egz['id'], n_id, n_m)

    with cr:
        ranks_module.liderlik_tablosu_goster(supabase, current_user=u)
