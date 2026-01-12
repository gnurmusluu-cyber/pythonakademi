# --- EĞİTİM PANELİ (DÜZELTİLMİŞ) ---

with col2:
    puan_pot = max(0, 20 - (st.session_state.error_count * 5))
    st.write(f"🎯 Kazanılacak: **{puan_pot} XP**")

    # DURUM 1: DENEME ANI
    if not st.session_state.cevap_dogru and st.session_state.error_count < 4:
        # text_area'ya bir 'key' atayarak veriyi otomatik session_state'e alıyoruz
        kod_input = st.text_area("Kodunu Yaz:", value=egz['sablon'], height=200, key="mevcut_kod_girdisi")
        
        if st.button("Kontrol Et"):
            # Yazılan kodu hemen kalıcı hafızaya alalım
            st.session_state.last_code = kod_input 
            
            if kod_input.strip() == egz['dogru_cevap_kodu'].strip():
                st.session_state.cevap_dogru, st.session_state.pito_mod = True, "basari"
                st.rerun()
            else:
                st.session_state.error_count += 1
                st.session_state.pito_mod = "hata" if st.session_state.error_count < 4 else "dusunuyor"
                st.rerun()

    # DURUM 2: BAŞARI (HATANIN ÇÖZÜLDÜĞÜ YER)
    elif st.session_state.cevap_dogru:
        st.success("🌟 Harika! Pito seninle gurur duyuyor.")
        
        # Bir sonraki egzersiz hesaplamaları...
        idx = modul['egzersizler'].index(egz)
        if idx + 1 < len(modul['egzersizler']):
            n_id, n_m = modul['egzersizler'][idx+1]['id'], u['mevcut_modul']
        else:
            n_id, n_m = f"{int(float(u['mevcut_modul'])) + 1}.1", int(float(u['mevcut_modul'])) + 1

        # KRİTİK DÜZELTME: 'kod_input' yerine 'st.session_state.last_code' kullanıyoruz
        if st.button("Sonraki Göreve Geç ➡️"):
            ilerleme_kaydet(puan_pot, st.session_state.last_code, egz['id'], u['mevcut_modul'], n_id, n_m)

    # DURUM 3: KİLİT (4 HATA)
    elif st.session_state.error_count >= 4:
        st.error("🚫 Kilitlendi. Çözümü incele.")
        with st.expander("📖 Çözüm"): st.code(egz['cozum'])
        
        idx = modul['egzersizler'].index(egz)
        n_id, n_m = (modul['egzersizler'][idx+1]['id'], u['mevcut_modul']) if idx+1 < len(modul['egzersizler']) else (f"{int(float(u['mevcut_modul'])) + 1}.1", int(float(u['mevcut_modul'])) + 1)
        
        if st.button("Anladım, Sıradaki Göreve Geç ➡️"):
            # Çözüm incelendiğinde kod yerine sabit bir metin gönderiyoruz
            ilerleme_kaydet(0, "Çözüm İncelendi", egz['id'], u['mevcut_modul'], n_id, n_m)
