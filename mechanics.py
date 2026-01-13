import streamlit as st
import pandas as pd

def mezuniyet_ekrani(u, msgs, pito_goster, supabase, ranks_module):
    """Mezuniyet töreni, onur kürsüsü ve sıfırlama seçeneği."""
    st.balloons()
    st.snow()
    st.markdown("<div class='academy-title'>🎓 PİTO PYTHON AKADEMİ MEZUNİYETİ</div>", unsafe_allow_html=True)
    
    cl, cr = st.columns([7, 3])
    with cl:
        cp1, cp2 = st.columns([1, 2])
        with cp1: pito_goster("mezun")
        with cp2:
            raw_msg = msgs.get('mezuniyet_mesaji', "Tebrikler {}! Nusaybin'in tescilli Python savaşçısı oldun!")
            st.markdown(f"<div class='pito-notu'>💬 <b>Pito:</b> {raw_msg.format(u['ad_soyad'])}</div>", unsafe_allow_html=True)

        st.markdown(f"""
            <div class='gorev-box' style='text-align:center; border: 2px solid #ADFF2F;'>
                <h2 style='color:#ADFF2F;'>📜 BAŞARI SERTİFİKASI</h2>
                <p>Sayın <b>{u['ad_soyad']}</b>,<br>
                Python temellerini başarıyla kavrayarak Pito Python Akademi'den 
                <b>{int(u['toplam_puan'])} XP</b> ile mezun oldunuz.</p>
                <hr>
                <p><i>Nusaybin Süleyman Bölünmez Anadolu Lisesi - 2026</i></p>
            </div>
        """, unsafe_allow_html=True)
        
        st.markdown("### ⚙️ Sonraki Adımlar")
        col_btn1, col_btn2 = st.columns(2)
        with col_btn1:
            if st.button("🔍 Görev Çözümlerini İncele", use_container_width=True):
                st.session_state.in_review = True; st.rerun()
        with col_btn2:
            if st.button("🔄 Eğitimi Tekrar Al (Sıfırla)", use_container_width=True):
                supabase.table("kullanicilar").update({"toplam_puan": 0, "mevcut_egzersiz": "1.1", "mevcut_modul": 1, "rutbe": "🥚 Çömez"}).eq("ogrenci_no", int(u['ogrenci_no'])).execute()
                st.session_state.user = None; st.rerun()

    with cr:
        ranks_module.liderlik_tablosu_goster(supabase, current_user=u)

def inceleme_modu_paneli(u, mufredat, pito_goster, supabase):
    """Sadece müfredattaki ideal çözümleri gösteren gelişim paneli."""
    st.markdown("<h2 style='color:#ADFF2F;'>🔍 Görev Çözüm Kütüphanesi</h2>", unsafe_allow_html=True)
    st.markdown("Başarıyla tamamladığın görevlerin en ideal çözümlerini buradan inceleyebilirsin arkadaşım!")
    
    # --- DİNAMİK YÖNLENDİRME ZIRHI ---
    # Öğrencinin mevcut modülü müfredat sayısını geçtiyse mezun sayılır.
    is_graduated = int(u['mevcut_modul']) > len(mufredat)
    geri_butonu_metni = "⬅️ Mezuniyet Ekranına Dön" if is_graduated else "⬅️ Eğitime Dön"
    
    if st.button(geri_butonu_metni):
        st.session_state.in_review = False; st.rerun()
    # --------------------------------

    try:
        # Veritabanından sadece hangi görevlerin bittiğini çekiyoruz
        res = supabase.table("egzersiz_kayitlari").select("egz_id, alinan_puan").eq("ogrenci_no", int(u['ogrenci_no'])).execute()
        
        if res.data:
            # Bitirilen görevleri bir listeye alalım
            biten_id_listesi = [str(item['egz_id']) for item in res.data]
            
            # Müfredatı tarayarak sadece bitirilen görevlerin ideal çözümlerini göster
            for m in mufredat:
                # Bu modülde biten görev var mı kontrol et
                modulun_bitenleri = [e for e in m['egzersizler'] if str(e['id']) in biten_id_listesi]
                
                if modulun_bitenleri:
                    with st.expander(f"📦 {m['modul_adi']}"):
                        for egz in modulun_bitenleri:
                            st.markdown(f"📍 **Görev {egz['id']}:** {egz.get('yonerge')}")
                            st.markdown("🤖 **Pito'nun İdeal Çözümü:**")
                            st.code(egz.get('cozum', '# Çözüm hazırlanıyor...'), language="python")
                            st.divider()
        else:
            st.info("Henüz tamamlanmış bir görevin bulunmuyor genç yazılımcı. Önce biraz kod yazalım!")
    except Exception as e:
        st.error(f"Veri çekme hatası: {e}")
