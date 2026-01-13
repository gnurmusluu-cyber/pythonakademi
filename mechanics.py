import streamlit as st
import pandas as pd

def mezuniyet_ekrani(u, msgs, pito_goster, supabase, ranks_module):
    """Mezuniyet töreni, onur kürsüsü ve sıfırlama seçeneği."""
    st.balloons()
    st.snow()
    
    st.markdown("<div class='academy-title'>🎓 PİTO PYTHON AKADEMİ MEZUNİYETİ</div>", unsafe_allow_html=True)
    
    # Ana ekranı ikiye bölüyoruz: Sol (Mezuniyet), Sağ (Liderlik)
    cl, cr = st.columns([7, 3])
    
    with cl:
        cp1, cp2 = st.columns([1, 2])
        with cp1:
            pito_goster("mezun") # Mezuniyet GIF'i
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
        
        # Seçenekler Paneli
        st.markdown("### ⚙️ Sonraki Adımlar")
        col_btn1, col_btn2 = st.columns(2)
        
        with col_btn1:
            if st.button("🔍 Eski Kodlarımı İncele", use_container_width=True):
                st.session_state.in_review = True
                st.rerun()
        
        with col_btn2:
            # SIFIRLAMA MEKANİZMASI
            if st.button("🔄 Eğitimi Tekrar Al (XP Sıfırlanır!)", use_container_width=True):
                try:
                    # Veritabanını başlangıç ayarlarına döndür
                    supabase.table("kullanicilar").update({
                        "toplam_puan": 0,
                        "mevcut_egzersiz": "1.1",
                        "mevcut_modul": 1,
                        "rutbe": "🥚 Çömez"
                    }).eq("ogrenci_no", int(u['ogrenci_no'])).execute()
                    
                    # Local state'i temizle ve yeniden başlat
                    st.session_state.user = None
                    st.success("Yolculuk en baştan başlıyor... Hazırlan arkadaşım!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Sıfırlama sırasında bir hata oluştu: {e}")

    with cr:
        # Mezuniyet anında onur kürsüsünü gösteriyoruz
        ranks_module.liderlik_tablosu_goster(supabase, current_user=u)

def inceleme_modu_paneli(u, mufredat, pito_goster, supabase):
    """Öğrencinin geçmiş kodlarını incelediği panel."""
    st.markdown("<h2 style='color:#ADFF2F;'>🔍 Geçmiş Görev İnceleme</h2>", unsafe_allow_html=True)
    
    if st.button("⬅️ Mezuniyet Ekranına Dön"):
        st.session_state.in_review = False
        st.rerun()

    try:
        res = supabase.table("egzersiz_kayitlari").select("*").eq("ogrenci_no", int(u['ogrenci_no'])).execute()
        if res.data:
            for item in res.data:
                tarih = item.get('created_at', 'Tarih Belirsiz')
                tarih_formatli = tarih[:10] if tarih != 'Tarih Belirsiz' else tarih
                with st.expander(f"📍 Görev {item.get('egz_id', '?')} | 💎 {item.get('alinan_puan', 0)} XP"):
                    st.code(item.get('basarili_kod', '# Kod bulunamadı'), language="python")
                    st.info(f"Kayıt Tarihi: {tarih_formatli}")
        else:
            st.info("Henüz kaydedilmiş bir çözümün bulunmuyor.")
    except Exception as e:
        st.error(f"Veri çekme hatası: {e}")
