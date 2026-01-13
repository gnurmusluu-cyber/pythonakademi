import streamlit as st
import pandas as pd

def mezuniyet_ekrani(u, msgs, pito_goster, supabase):
    """Tüm modülleri bitiren öğrenci için mezuniyet törenini yönetir."""
    st.balloons() # Kutlama balonları!
    st.snow()     # Ve Nusaybin'e biraz kar yağdıralım :)
    
    st.markdown("<div class='academy-title'>🎓 PİTO PYHTON AKADEMİ MEZUNİYETİ</div>", unsafe_allow_html=True)
    
    c1, c2 = st.columns([1, 2])
    with c1:
        pito_goster("basari") # Mezuniyet için Pito çok mutlu!
    with c2:
        st.markdown(f"""
            <div class='pito-notu'>
                💬 <b>Pito:</b> {msgs['mezuniyet_mesaji'].format(u['ad_soyad'])}
            </div>
        """, unsafe_allow_html=True)

    st.markdown(f"""
        <div class='gorev-box' style='text-align:center; border: 2px solid #ADFF2F;'>
            <h2 style='color:#ADFF2F;'>📜 BAŞARI SERTİFİKASI</h2>
            <p>Sayın <b>{u['ad_soyad']}</b>,<br>
            Python dilinin temellerini başarıyla kavrayarak Pito Python Akademi'den 
            <b>{u['toplam_puan']} XP</b> ile mezun olmaya hak kazandınız.</p>
            <hr>
            <p><i>Nusaybin Süleyman Bölünmez Anadolu Lisesi - 2026</i></p>
        </div>
    """, unsafe_allow_html=True)
    
    if st.button("🔍 Eski Kodlarımı İncelemek İstiyorum"):
        st.session_state.in_review = True
        st.rerun()

def inceleme_modu_paneli(u, mufredat, pito_goster, supabase):
    """Öğrencinin geçmişte yazdığı başarılı kodları görmesini sağlar."""
    st.markdown("<h2 style='color:#ADFF2F;'>🔍 Geçmiş Görev İnceleme</h2>", unsafe_allow_html=True)
    
    if st.button("⬅️ Akademiye Dön"):
        st.session_state.in_review = False
        st.rerun()

    try:
        # AttributeError'u engellemek için doğrudan parametre olan supabase kullanıldı
        res = supabase.table("egzersiz_kayitlari").select("*").eq("ogrenci_no", int(u['ogrenci_no'])).execute()
        
        if res.data:
            df = pd.DataFrame(res.data)
            for item in res.data:
                with st.expander(f" Görev {item['egz_id']} | 💎 {item['alinan_puan']} XP"):
                    st.code(item['basarili_kod'], language="python")
                    st.info(f"Kayıt Tarihi: {item['created_at'][:10]}")
        else:
            st.info("Henüz kaydedilmiş bir görev çözümün bulunmuyor arkadaşım.")
            
    except Exception as e:
        st.error(f"Veriler çekilirken bir sorun oluştu: {e}")
