import streamlit as st
import pandas as pd
import random

def mezuniyet_ekrani(u, msgs, pito_goster, supabase, ranks_module):
    """Mezuniyet töreni ve sadece animasyonlara özel görsel ayarlar."""
    
    # --- NOKTA ATIŞI SİBER-ÇERÇEVE SİLİCİ ---
    # Sadece balon ve kar tanesi animasyonlarını hedef alır, diğer elementlere dokunmaz.
    st.markdown("""
        <style>
        /* Sadece Streamlit animasyon katmanlarını ve içindeki spanları hedefle */
        .stBalloons, .stSnow, [data-testid="stBalloon"], [data-testid="stSnow"], 
        .stBalloons span, .stSnow span {
            outline: none !important;
            box-shadow: none !important;
            border: none !important;
            -webkit-tap-highlight-color: transparent !important;
        }
        
        /* Sertifika tasarımı (Siber-Buz) */
        .cyber-card {
            text-align:center; 
            border: 2px solid #00E5FF; 
            padding: 30px; 
            border-radius: 20px; 
            background: rgba(0, 229, 255, 0.05);
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
                st.session_state.in_review = True
                st.rerun()
        with col_btn2:
            if st.button("🚪 Çıkış Yap", help="Oturumu kapat ve başa dön", use_container_width=True, key="exit_btn_mezun"):
                st.session_state.user = None
                st.session_state.in_review = False
                st.rerun()

    with cr:
        ranks_module.liderlik_tablosu_goster(supabase, current_user=u)

def inceleme_modu(u, mufredat, supabase):
    """Bitmiş görevleri siber-arşivde ideal çözümlerle gösterir."""
    st.markdown("<h2 style='text-align:center; color:#00E5FF;'>🔍 SİBER-ARŞİV: GEÇMİŞ ÇÖZÜMLER</h2>", unsafe_allow_html=True)
    
    graduated = int(u['mevcut_modul']) > len(mufredat)
    geri_metni = "⬅️ Mezuniyet Ekranına Dön" if graduated else "⬅️ Eğitime Dön"
    
    if st.button(geri_metni, use_container_width=True, key="back_to_main"):
        st.session_state.in_review = False
        st.rerun()

    try:
        res = supabase.table("egzersiz_kayitlari").select("egz_id, alinan_puan").eq("ogrenci_no", int(u['ogrenci_no'])).execute()
        
        if res.data:
            biten_id_listesi = [str(item['egz_id']) for item in res.data]
            
            for m in mufredat:
                modulun_bitenleri = [e for e in m['egzersizler'] if str(e['id']) in biten_id_listesi]
                
                if modulun_bitenleri:
                    with st.expander(f"📦 {m['modul_adi']}", expanded=False):
                        for egz in modulun_bitenleri:
                            st.markdown(f"📍 **Görev {egz['id']}:** {egz.get('yonerge')}")
                            st.markdown("🤖 **Pito'nun İdeal Çözümü:**")
                            st.code(egz.get('cozum', '# Çözüm hazırlanıyor...'), language="python")
                            
                            st.markdown("💻 **Beklenen Çıktı:**")
                            st.markdown(f"<div class='console-box'>{egz.get('beklenen_cikti', 'Çıktı üretiliyor...')}</div>", unsafe_allow_html=True)
                            st.divider()
        else:
            st.info("Henüz tamamlanmış bir görevin bulunmuyor genç yazılımcı!")
    except Exception as e:
        st.error(f"Siber-arşiv hatası: {e}")
