import streamlit as st
import pandas as pd
import random

def mezuniyet_ekrani(u, msgs, pito_goster, supabase, ranks_module):
    """Mezuniyet töreni, onur kürsüsü ve sıfırlama seçeneği."""
    
    # --- AGRESİF SİBER-ÇERÇEVE SİLİCİ CSS ---
    # Sayfadaki her şeyin (butonlar, yazılar, animasyonlar) mavi çerçevesini kökten keser.
    st.markdown("""
        <style>
        /* Tüm tarayıcı odak çerçevelerini (focus ring) yok et */
        * :focus {
            outline: none !important;
            box-shadow: none !important;
        }
        * :focus-visible {
            outline: none !important;
        }
        /* Streamlit özel buton ve yazı odaklarını temizle */
        div[data-testid="stMarkdownContainer"] :focus {
            outline: none !important;
        }
        button:focus {
            outline: none !important;
            box-shadow: none !important;
        }
        </style>
    """, unsafe_allow_html=True)

    # Kutlama efektleri
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

        # Siber Sertifika Alanı
        st.markdown(f"""
            <div class='cyber-card' style='text-align:center; border: 2px solid #00E5FF; padding: 25px; border-radius: 15px; background: rgba(0, 229, 255, 0.05);'>
                <h2 style='color:#00E5FF; margin-top: 0;'>📜 BAŞARI SERTİFİKASI</h2>
                <hr style='border-color: #00E5FF; opacity: 0.3;'>
                <p style='font-size: 1.2rem;'>Sayın <b>{u['ad_soyad']}</b>,</p>
                <p>Python temellerini başarıyla kavrayarak Pito Python Akademi'den 
                <b style='color:#ADFF2F;'>{int(u['toplam_puan'])} XP</b> ile mezun oldunuz.</p>
                <p style='font-size:0.8rem; color:#888; margin-top: 20px;'>
                    Sertifika No: PPA-{u['ogrenci_no']}-{random.randint(1000,9999)} <br>
                    Nusaybin Süleyman Bölünmez Anadolu Lisesi Laboratuvarı
                </p>
            </div>
        """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Sıfırlama ve İnceleme Seçenekleri
        col_b1, col_b2 = st.columns(2)
        with col_b1:
            if st.button("🔍 Geçmiş egzersizler", use_container_width=True, key="rev_btn_mezun"):
                st.session_state.in_review = True; st.rerun()
        with col_b2:
            if st.button("🚪 Çıkış", help="Ana sayfaya dön", use_container_width=True, key="exit_btn_mezun"):
                st.session_state.user = None
                st.session_state.in_review = False; st.rerun()

    with cr:
        ranks_module.liderlik_tablosu_goster(supabase, current_user=u)

def inceleme_modu(u, mufredat, supabase):
    """Öğrencinin bitirdiği tüm görevleri modül bazlı gösteren siber-arşiv."""
    st.markdown("<h2 style='text-align:center; color:#00E5FF;'>🔍 SİBER-ARŞİV: GEÇMİŞ ÇÖZÜMLER</h2>", unsafe_allow_html=True)
    
    graduated = u.get('mevcut_modul') == 11
    geri_metni = "⬅️ Ana Sayfaya Dön" if graduated else "⬅️ Eğitime Dön"
    
    if st.button(geri_metni, use_container_width=True, key="back_to_edu"):
        st.session_state.in_review = False; st.rerun()

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
                            
                            st.markdown("💻 **Konsol Çıktısı:**")
                            st.markdown(f"<div class='console-box'>{egz.get('beklenen_cikti', 'Çıktı üretiliyor...')}</div>", unsafe_allow_html=True)
        else:
            st.info("Henüz tamamladığın bir egzersiz bulunmuyor arkadaşım. Kod yazmaya başla!")
    except Exception as e:
        st.error(f"⚠️ Arşiv verisi yüklenirken bir hata oluştu: {e}")
