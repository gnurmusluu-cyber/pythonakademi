import streamlit as st
import random

def egitim_ekrani(u, mufredat, msgs, emotions_module, ranks_module, ilerleme_fonksiyonu, normalize_fonksiyonu, supabase):
    """Satır bazlı korumalı kod editörü motoru."""
    
    m_idx = int(u['mevcut_modul']) - 1
    total_m = len(mufredat)
    ad_k = u['ad_soyad'].split()[0]

    # --- 1. ÜST PANEL ---
    st.markdown(f"<div class='progress-label'><span>🎓 Akademi</span><span>Modül {m_idx + 1} / {total_m}</span></div>", unsafe_allow_html=True)
    st.progress(min((m_idx) / total_m, 1.0))

    modul = mufredat[m_idx]
    egz = next((e for e in modul['egzersizler'] if e['id'] == str(u['mevcut_egzersiz'])), modul['egzersizler'][0])
    
    cl, cr = st.columns([7, 3])
    with cl:
        rn, rc = ranks_module.rütbe_ata(u['toplam_puan'])
        st.markdown(f"<div class='hero-panel'><h3>🚀 {modul['modul_adi']}</h3><p>{ad_k} | <span class='rank-badge' style='background:black; color:#ADFF2F;'>{rn}</span></p></div>", unsafe_allow_html=True)
        
        # Pito Mesajı ve XP Durumu
        p_xp = max(0, 20 - (st.session_state.error_count * 5))
        p_mod = emotions_module.pito_durum_belirle(st.session_state.error_count, st.session_state.cevap_dogru)
        
        cp1, cp2 = st.columns([1, 2])
        with cp1: emotions_module.pito_goster(p_mod, size=140)
        with cp2:
            st.markdown(f"💎 **{p_xp} XP** | ⚠️ **Hata: {st.session_state.error_count}/4**")
            if st.session_state.error_count > 0:
                st.error(f"🚨 {random.choice(msgs['errors'][f'level_{min(st.session_state.error_count, 4)}']).format(ad_k)}")
            else:
                st.markdown(f"<div class='pito-notu'>💬 {msgs['welcome'].format(ad_k)}</div>", unsafe_allow_html=True)

        # --- 2. SATIR BAZLI AKILLI EDİTÖR ---
        if not st.session_state.cevap_dogru and st.session_state.error_count < 4:
            st.markdown(f"<div class='gorev-box'><span class='gorev-label'>📍 GÖREV {egz['id']}</span><div class='gorev-text'>{egz['yonerge']}</div></div>", unsafe_allow_html=True)
            
            sablon_satirlari = egz.get('sablon', '').split('\n')
            cevap_inputlari = {}

            st.markdown("💻 **Kod Defteri (Boşlukları Doldur):**")
            
            for idx, satir in enumerate(sablon_satirlari):
                if "___" in satir:
                    # İçinde boşluk olan satır için giriş kutusu aç
                    # Satırın başındaki boşlukları (indentation) korumak için placeholder kullanıyoruz
                    indent = len(satir) - len(satir.lstrip())
                    label = " " * indent + "📝 Satır " + str(idx + 1)
                    
                    user_val = st.text_input(
                        label, 
                        key=f"ln_{egz['id']}_{idx}", 
                        placeholder=satir.strip(),
                        help="Bu satırdaki ___ kısmını doldur."
                    )
                    cevap_inputlari[idx] = user_val
                else:
                    # Sabit satırları direkt kod olarak göster (silemezler)
                    st.code(satir if satir.strip() else " ", language="python")

            if st.button("Kodu Çalıştır 🚀", use_container_width=True):
                # Satırları birleştirerek nihai kodu oluştur
                final_kod_listesi = []
                for idx, satir in enumerate(sablon_satirlari):
                    if idx in cevap_inputlari:
                        # Boşluklu satırı öğrencinin girdisiyle oluştur
                        # Eğer öğrenci satırı tamamen yazdıysa onu al, sadece ___ kısmını yazdıysa replace et
                        girdi = cevap_inputlari[idx]
                        if "___" in satir and girdi:
                            final_kod_listesi.append(satir.replace("___", girdi))
                        else:
                            final_kod_listesi.append(girdi if girdi else satir)
                    else:
                        final_kod_listesi.append(satir)
                
                final_code = "\n".join(final_kod_listesi)
                st.session_state.current_code = final_code
                
                if normalize_fonksiyonu(final_code) == normalize_fonksiyonu(egz['dogru_cevap_kodu']):
                    st.session_state.cevap_dogru = True
                else:
                    st.session_state.error_count += 1
                st.rerun()

        # --- 3. BAŞARI / HATA DURUMLARI ---
        elif st.session_state.cevap_dogru:
            st.success(f"✅ Harika iş çıkardın {ad_k}!")
            st.code(st.session_state.current_code, language="python")
            if st.button("Sonraki Göreve Geç ➡️", use_container_width=True):
                s_idx = modul['egzersizler'].index(egz) + 1
                n_id, n_m = (modul['egzersizler'][s_idx]['id'], u['mevcut_modul']) if s_idx < len(modul['egzersizler']) else (f"{int(u['mevcut_modul'])+1}.1", int(u['mevcut_modul']) + 1)
                ilerleme_fonksiyonu(p_xp, st.session_state.current_code, egz['id'], n_id, n_m)
        
        elif st.session_state.error_count >= 4:
            st.warning("🚨 Pito: 'Bu biraz zordu ama üzülme, işte doğrusu!'")
            st.code(egz['cozum'], language="python")
            if st.button("Sıradaki Göreve Geç ➡️", use_container_width=True):
                s_idx = modul['egzersizler'].index(egz) + 1
                n_id, n_m = (modul['egzersizler'][s_idx]['id'], u['mevcut_modul']) if s_idx < len(modul['egzersizler']) else (f"{int(u['mevcut_modul'])+1}.1", int(u['mevcut_modul']) + 1)
                ilerleme_fonksiyonu(0, "Çözüm İncelendi", egz['id'], n_id, n_m)

    with cr:
        ranks_module.liderlik_tablosu_goster(supabase, current_user=u)
