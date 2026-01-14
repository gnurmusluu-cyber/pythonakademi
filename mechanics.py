import streamlit as st
import pandas as pd
import random

def mezuniyet_ekrani(u, msgs, pito_goster, supabase, ranks_module):
    """Mezuniyet töreni, onur kürsüsü ve tam sistem sıfırlama seçeneği."""
    
    # --- 0. SİBER-GÖRSEL ZIRH (OKUNABİLİRLİK VE ÇERÇEVE İMHASI) ---
    st.markdown("""
        <style>
        /* 1. Mavi çerçeve imha edici (Pointer-Events Protokolü) */
        [data-testid='stBalloons'], [data-testid='stSnow'], 
        [data-testid='stBalloons'] *, [data-testid='stSnow'] * {
            pointer-events: none !important;
            outline: none !important;
            box-shadow: none !important;
            border: none !important;
        }
        
        /* 2. BUTON METİNLERİNİ SİYAH YAPMA (KESİN OKUNABİLİRLİK) */
        div.stButton > button {
            background-color: #00E5FF !important;
            border: 2px solid #00E5FF !important;
            transition: 0.3s !important;
        }
        /* Butonun içindeki metni (p etiketi dahil) siyaha zorla */
        div.stButton > button p, div.stButton > button span {
            color: #000000 !important;
            font-weight: 900 !important;
            font-size: 1rem !important;
        }
        div.stButton > button:hover {
            background-color: #ADFF2F !important;
            border-color: #ADFF2F !important;
        }

        .cyber-card {
            text-align:center; border: 2px solid #00E5FF; padding: 30px; 
            border-radius: 20px; background: rgba(0, 229, 255, 0.05);
            box-shadow: 0 0 25px rgba(0, 229, 255, 0.2);
            margin-bottom: 25px;
        }
        </style>
    """, unsafe_allow_html=True)

    # --- 1. EFEKT KONTROLÜ (SIFIRLAMA ANINDA BALONLARI SUSTUR) ---
    if not st.session_state.get('reset_active', False):
        st.balloons()
        st.snow()
    
    st.markdown("<div class='academy-header'>🎓 PİTO PYTHON AKADEMİ MEZUNİYETİ</div>", unsafe_allow_html=True)
    
    cl, cr = st.columns([7.5, 2.5])
    with cl:
        cp1, cp2 = st.columns([1, 2])
        with cp1: pito_goster('mezun')
        with cp2:
            raw_msg = msgs.get('mezuniyet_mesaji', "Tebrikler {}! Nusaybin'in tescilli Python savaşçısı oldun!")
            st.markdown(f"<div class='pito-notu'>💬 <b>Pito:</b> {raw_msg.format(u['ad_soyad'])}</div>", unsafe_allow_html=True)

        # Siber Sertifika Alanı
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
        
        # --- KUMANDA PANELİ (OKUNAKLI BUTONLAR) ---
        st.markdown("### ⚙️ Kumanda Paneli")
        b1, b2, b3 = st.columns(3)
        
        with b1:
            if st.button("🔍 Geçmiş egzersizler", use_container_width=True, key='rev_btn_master'):
                st.session_state.in_review = True; st.rerun()
        
        with b2:
            if st.button("🚪 Çıkış Yap", help='Oturumu kapat', use_container_width=True, key='exit_btn_master'):
                st.session_state.user = None
                st.session_state.in_review = False; st.rerun()
                
        with b3:
            # EĞİTİMİ TEKRAR AL (SIFIRLAMA) PROTOKOLÜ
            if st.button("🔄 Eğitimi Tekrar Al", help='Puanları sil ve 1. Modülden başla', use_container_width=True, key='reset_btn_master'):
                st.session_state.reset_active = True # Balonları durdur
                
                # Supabase Güncelleme: 0 Puan, 1. Modül, 1.1 Egzersiz
                supabase.table('kullanicilar').update({
                    'toplam_puan': 0, 
                    'mevcut_egzersiz': '1.1', 
                    'mevcut_modul': 1, 
                    'rutbe': '🥚 Çömez',
                }).eq('ogrenci_no', int(u['ogrenci_no'])).execute()
                
                # Tüm geçmiş egzersiz kayıtlarını sil
                supabase.table('egzersiz_kayitlari').delete().eq('ogrenci_no', int(u['ogrenci_no'])).execute()
                
                st.session_state.user = None
                st.session_state.in_review = False
                st.session_state.reset_active = False # Bir sonraki giriş için temizle
                st.rerun()

    with cr:
        ranks_module.liderlik_tablosu_goster(supabase, current_user=u)

def inceleme_modu_paneli(u, mufredat, pito_goster, supabase):
    """Bitmiş görevleri siber-arşivde siyah metinli butonlarla gösterir."""
    st.markdown("""<style>div.stButton > button p, div.stButton > button span { color: #000 !important; font-weight: 900 !important; }</style>""", unsafe_allow_html=True)
    st.markdown("<h2 style='text-align:center; color:#00E5FF;'>🔍 SİBER-ARŞİV: GEÇMİŞ ÇÖZÜMLER</h2>", unsafe_allow_html=True)
    
    is_graduated = int(u['mevcut_modul']) > len(mufredat)
    geri_metni = "⬅️ Mezuniyet Ekranına Dön" if is_graduated else "⬅️ Eğitime Dön"
    
    if st.button(geri_metni, use_container_width=True, key='back_btn_archive'):
        st.session_state.in_review = False; st.rerun()

    try:
        res = supabase.table('egzersiz_kayitlari').select('egz_id').eq('ogrenci_no', int(u['ogrenci_no'])).execute()
        if res.data:
            biten_id_listesi = [str(item['egz_id']) for item in res.data]
            for m in mufredat:
                modulun_bitenleri = [e for e in m['egzersizler'] if str(e['id']) in biten_id_listesi]
                if modulun_bitenleri:
                    with st.expander(f"📦 {m['modul_adi']}", expanded=False):
                        for egz in modulun_bitenleri:
                            st.markdown(f"📍 **Görev {egz['id']}:** {egz.get('yonerge')}")
                            st.markdown("🤖 **Pito'nun İdeal Çözümü:**")
                            st.code(egz.get('cozum', '# Çözüm hazırlanıyor...'), language='python')
                            st.markdown(f"<div class='console-box'>{egz.get('beklenen_cikti', '...')}</div>", unsafe_allow_html=True)
                            st.divider()
        else:
            st.info("Henüz tamamlanmış bir görevin bulunmuyor genç yazılımcı!")
    except Exception as e:
        st.error(f"Siber-arşiv hatası: {e}")
