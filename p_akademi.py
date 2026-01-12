# --- 1. SESSION STATE GÜNCELLEME (Bunu başlatma kısmına ekle) ---
if "adim_tamamlandi" not in st.session_state:
    st.session_state.adim_tamamlandi = False

# --- 2. GÜNCELLENMİŞ KONTROL FONKSİYONU ---
def kontrol_et(girilen_kod, dogru_kod, ipucu):
    # Boşlukları ve tırnak farklarını temizleyerek karşılaştır
    temiz_giris = girilen_kod.strip().replace('"', "'").replace(" ", "")
    temiz_cozum = dogru_kod.strip().replace('"', "'").replace(" ", "")
    
    if temiz_giris == temiz_cozum:
        st.session_state.adim_tamamlandi = True # Başarı bayrağını kaldır
        st.session_state.hata_sayisi = 0
    else:
        st.session_state.hata_sayisi += 1
        st.session_state.mevcut_puan = max(0, st.session_state.mevcut_puan - 5)
        st.error(f"Hatalı kod! Kalan Puan: {st.session_state.mevcut_puan}")
        
        if st.session_state.hata_sayisi == 3:
            st.warning(f"💡 İpucu: {ipucu}")
        
        if st.session_state.hata_sayisi >= 4:
            st.session_state.kilitli = True
            st.error(f"🛑 4. Hata! Editör kilitlendi. Doğru Çözüm:\n\n{dogru_kod}")

# --- 3. ANA EKRAN AKIŞINDAKİ BUTON YERLEŞİMİ ---
# Kodu Çalıştır butonu tıklandığında kontrolü yap
if not st.session_state.adim_tamamlandi:
    if st.button("Kodu Çalıştır", type="primary"):
        kontrol_et(user_code, adim_verisi['cozum'], adim_verisi['ipucu'])
        st.rerun() # Durumu güncellemek için sayfayı tazele

# Eğer adım doğruysa burası çalışır (Ayrı bir blok olarak)
if st.session_state.adim_tamamlandi:
    st.success(f"🎉 Harika! Bu adımdan {st.session_state.mevcut_puan} puan kazandın!")
    
    if st.button("Sonraki Adıma Geç ➡️"):
        # Puanı toplam puana ekle
        st.session_state.toplam_puan += st.session_state.mevcut_puan
        
        # İndeksleri güncelle (45 adım / 9 modül mantığı)
        if st.session_state.adim_idx < 4:
            st.session_state.adim_idx += 1
        else:
            st.session_state.adim_idx = 0
            st.session_state.modul_idx += 1
            
        # Değerleri bir sonraki adım için sıfırla
        st.session_state.adim_tamamlandi = False
        st.session_state.mevcut_puan = 20
        st.session_state.hata_sayisi = 0
        st.session_state.kilitli = False
        st.rerun() # Yeni soruya geçmek için sayfayı tazele
