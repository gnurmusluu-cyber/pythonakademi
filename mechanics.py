import streamlit as st
import pandas as pd
import random

def mezuniyet_ekrani(u, msgs, pito_goster, supabase, ranks_module):
    """Mezuniyet töreni ve animasyonlar için kesin görsel çözüm."""
    
    # --- NOKTA ATIŞI SİBER-KALKAN (HAYALET MODU) ---
    st.markdown("""
        <style>
        /* Balon ve Kar Tanelerini tamamen etkileşimsiz yap (Mavi Çerçeve İlacı) */
        [data-testid="stBalloons"], [data-testid="stSnow"], 
        [data-testid="stBalloons"] *, [data-testid="stSnow"] * {
            pointer-events: none !important; /* Tıklanmayı engelle */
            outline: none !important;       /* Çerçeveyi yok et */
            box-shadow: none !important;    /* Gölgeyi sil */
            border: none !important;        /* Kenarlığı kaldır */
        }
        
        .cyber-card {
            text-align:center; border: 2px solid #00E5FF; padding: 30px; 
            border-radius: 20px; background: rgba(0, 229, 255, 0.05);
            box-shadow: 0 0 25px rgba(0, 229, 255, 0.2);
        }
        </style>
    """, unsafe_allow_html=True)

    # Efektleri tetikle
    st.balloons()
    st.snow()
    
    st.markdown("<div class='academy-header'>🎓 PİTO PYTHON AKADEMİ MEZUNİYETİ</div>", unsafe_allow_html=True)
    
    cl, cr = st.columns([7, 3])
    with cl:
        cp1, cp2 = st.columns([1, 2])
        with cp1: pito_goster("mezun")
        with cp2:
            raw_msg = msgs.get('mezuniyet_mesaji', "Tebrikler {}! Nusaybin'in tescilli Python savaşçısı oldun!")
            st.markdown(f"<div class='pito-notu'>💬 <b>Pito:</b> {raw_msg.format(u['ad_soyad'])}</div>", unsafe_allow_html=True)

        # Siber Sertifika
        st.markdown(f"""
            <div class='cyber-card'>
                <h2 style='color:#00E5FF; margin-top: 0;'>📜 BAŞARI SERTİFİKASI</h2>
                <hr style='border-color: #00E5FF; opacity: 0.3;'>
                <p style='font-size: 1.2rem;'>Sayın <b>{u['ad_soyad']}</b>,</p>
                <p>Python temellerini başarıyla kavrayarak Pito Python Akademi'den 
                <b style='color:#ADFF2F;'>{int(u['toplam_puan'])} XP</b> ile mezun oldunuz.</p>
                <p style='font-size:0.8rem; color:#888; margin-top: 20px;'>
                    Sertifika No: PPA-{u['ogrenci_no']}-{random.randint(1000,9999)} <br>
                    Nusaybin Süleyman Bölünmez Anadolu Lisesi Laboratuvarı - 2026
                </p>
            </div>
        """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # NAVİGASYON BUTONLARI
        col_btn1, col_btn2 = st.columns(2)
        with col_btn1:
            if st.button("🔍 Geçmiş egzersizler", use_container_width=True, key="rev_btn_mezun"):
                st.session_state.in_review = True; st.rerun()
        with col_btn2:
            if st.button("🚪 Çıkış Yap", help="Oturumu kapat ve başa dön", use_container_width=True, key="exit_btn_mezun"):
                st.session_state.user = None
                st.session_state.in_review = False; st.rerun()

    with cr:
        ranks_module.liderlik_tablosu_goster(supabase, current_user=u)

def inceleme_modu(u, mufredat, supabase):
    # (Bu kısım aynı kalabilir, herhangi bir siber-hata yok)
    ...
