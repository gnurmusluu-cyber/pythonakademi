import streamlit as st
import pandas as pd

def mezuniyet_ekrani(u, msgs, pito_goster, supabase, ranks_module):
    """Mezuniyet töreni ve sıfırlama seçeneği."""
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
            if st.button("🔍 Eski Kodlarımı İncele", use_container_width=True):
                st.session_state.in_review = True; st.rerun()
        with col_btn2:
            if st.button("🔄 Eğitimi Tekrar Al (Sıfırla)", use_container_width=True):
                supabase.table("kullanicilar").update({"toplam_puan": 0, "mevcut_egzersiz": "1.1", "mevcut_modul": 1, "rutbe": "🥚 Çömez"}).eq("ogrenci_no", int(u['ogrenci_no'])).execute()
                st.session_state.user = None; st.rerun()

    with cr:
        ranks_module.liderlik_tablosu_goster(supabase, current_user=u)

def inceleme_modu_paneli(u, mufredat, pito_goster, supabase):
    """Öğrencinin geçmiş başarılarını modül isimleriyle birlikte gösterir."""
    st.markdown("<h2 style='color:#ADFF2F;'>🔍 Geçmiş Görev İnceleme</h2>", unsafe_allow_html=True)
    
    if st.button("⬅️ Geri Dön"):
        st.session_state.in_review = False; st.rerun()

    try:
        # Veritabanından kayıtları çek
        res = supabase.table("egzersiz_kayitlari").select("*").eq("ogrenci_no", int(u['ogrenci_no'])).order("created_at", desc=True).execute()
        
        if res.data:
            for item in res.data:
                egz_id = item.get('egz_id')
                # MÜFREDATTAN MODÜL İSMİNİ BULMA (Akıllı Arama)
                modul_adi = "Diğer Görevler"
                for m in mufredat:
                    if any(e['id'] == str(egz_id) for e in m['egzersizler']):
                        modul_adi = m['modul_adi']
                        break
                
                tarih = item.get('created_at', 'Tarih Belirsiz')[:10]
                xp = item.get('alinan_puan', 0)
                
                # Expand başlığında Modül İsmi ve Görev ID birlikte
                with st.expander(f"📦 {modul_adi} | 📍 Görev {egz_id} | 💎 {xp} XP"):
                    # Veritabanındaki sütun isminin 'basarili_kod' olduğundan eminiz
                    kod_icerigi = item.get('basarili_kod', '')
                    
                    if kod_icerigi and kod_icerigi.strip():
                        st.code(kod_icerigi, language="python")
                    else:
                        st.warning("⚠️ Bu görev için kayıtlı bir kod bulunamadı (Çözüm izlenmiş olabilir).")
                    
                    st.caption(f"📅 Kayıt Tarihi: {tarih}")
        else:
            st.info("Henüz kaydedilmiş bir çözümün bulunmuyor genç yazılımcı.")
    except Exception as e:
        st.error(f"Veri çekilirken bir sorun oluştu: {e}")
