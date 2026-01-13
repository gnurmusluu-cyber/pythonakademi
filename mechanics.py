import streamlit as st
import pandas as pd

def mezuniyet_ekrani(u, msgs, pito_goster, supabase):
    """Tüm modülleri bitiren öğrenci için mezuniyet törenini yönetir."""
    st.balloons()
    st.snow()
    
    st.markdown("<div class='academy-title'>🎓 PİTO PYTHON AKADEMİ MEZUNİYETİ</div>", unsafe_allow_html=True)
    
    c1, c2 = st.columns([1, 2])
    with c1:
        pito_goster("basari")
    with c2:
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
    
    if st.button("🔍 Eski Kodlarımı İncele"):
        st.session_state.in_review = True
        st.rerun()

def inceleme_modu_paneli(u, mufredat, pito_goster, supabase):
    """Öğrencinin geçmiş başarılarını görmesini sağlar."""
    st.markdown("<h2 style='color:#ADFF2F;'>🔍 Geçmiş Görev İnceleme</h2>", unsafe_allow_html=True)
    
    if st.button("⬅️ Akademiye Dön"):
        st.session_state.in_review = False
        st.rerun()

    try:
        # AttributeError riskine karşı doğrudan iletilen 'supabase' kullanılır
        res = supabase.table("egzersiz_kayitlari").select("*").eq("ogrenci_no", int(u['ogrenci_no'])).execute()
        
        if res.data:
            for item in res.data:
                with st.expander(f"📍 Görev {item['egz_id']} | 💎 {item['alinan_puan']} XP"):
                    st.code(item['basarili_kod'], language="python")
                    st.info(f"Kayıt Tarihi: {item['created_at'][:10]}")
        else:
            st.info("Henüz kaydedilmiş bir çözümün bulunmuyor genç yazılımcı.")
    except Exception as e:
        st.error(f"Veri çekme hatası: {e}")
