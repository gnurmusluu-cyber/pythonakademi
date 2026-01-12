def ilerleme_kaydet(puan, kod, egz_id, n_id, n_m):
    try:
        # Veri tiplerini zorunlu olarak sayıya çeviriyoruz (Önemli!)
        ogrenci_no = int(st.session_state.user['ogrenci_no'])
        mevcut_xp = int(st.session_state.user['toplam_puan'])
        yeni_xp = mevcut_xp + puan
        yeni_modul = int(n_m)
        
        # Rütbe belirleme
        r = "🏆 Bilge" if yeni_xp >= 1000 else "🔥 Savaşçı" if yeni_xp >= 500 else "🐍 Pythonist" if yeni_xp >= 200 else "🥚 Çömez"
        
        # 1. KULLANICI GÜNCELLEME
        update_response = supabase.table("kullanicilar").update({
            "toplam_puan": yeni_xp, 
            "mevcut_egzersiz": str(n_id), 
            "mevcut_modul": yeni_modul, 
            "rutbe": r
        }).eq("ogrenci_no", ogrenci_no).execute()
        
        # 2. LOG KAYDI EKLEME
        insert_response = supabase.table("egzersiz_kayitlari").insert({
            "ogrenci_no": ogrenci_no, 
            "egz_id": str(egz_id),
            "alinan_puan": int(puan), 
            "basarili_kod": str(kod)
        }).execute()
        
        # Her şey tamamsa state güncelle ve yenile
        st.session_state.user.update({
            "toplam_puan": yeni_xp, 
            "mevcut_egzersiz": str(n_id), 
            "mevcut_modul": yeni_modul, 
            "rutbe": r
        })
        st.session_state.error_count, st.session_state.cevap_dogru, st.session_state.pito_mod = 0, False, "merhaba"
        st.success("✅ Veritabanı başarıyla güncellendi!")
        time.sleep(1)
        st.rerun()

    except Exception as e:
        # Hata varsa burada kırmızı kutu içinde görünecek
        st.error(f"❌ KAYIT HATASI: {str(e)}")
        st.write("Teknik Detay:", e)
