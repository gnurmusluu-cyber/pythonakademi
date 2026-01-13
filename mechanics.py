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
        # msgs.get kullanarak KeyError riskini sıfıra indiriyoruz
        raw_msg = msgs.get('mezuniyet_mesaji', "Tebrikler {}! Mezun oldun!")
        st.markdown(f"""
            <div class='pito-notu'>
                💬 <b>Pito:</b> {raw_msg.format(u['ad_soyad'])}
            </div>
        """, unsafe_allow_html=True)

    st.markdown(f"""
        <div class='gorev-box' style='text-align:center; border: 2px solid #ADFF2F;'>
            <h2 style='color:#ADFF2F;'>📜 BAŞARI SERTİFİKASI</h2>
            <p>Sayın <b>{u['ad_soyad']}</b>,<br>
            Python dilinin temellerini başarıyla kavrayarak Pito Python Akademi'den 
            <b>{int(u['toplam_puan'])} XP</b> ile mezun olmaya hak kazandınız.</p>
            <hr>
            <p><i>Nusaybin Süleyman Bölünmez Anadolu Lisesi - 2026</i></p>
        </div>
    """, unsafe_allow_html=True)
    
    if st.button("🔍 Eski Kodlarımı İncelemek İstiyorum"):
        st.session_state.in_review = True
        st.rerun()
