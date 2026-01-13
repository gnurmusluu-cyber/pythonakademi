import streamlit as st
import random

def login_ekrani(supabase, msgs, load_pito, liderlik_tablosu_fonksiyonu):
    col_in, col_tab = st.columns([2, 1], gap="large")
    
    with col_in:
        st.markdown('<div class="academy-title">Pito Python Akademi</div>', unsafe_allow_html=True)
        
        # --- GİRİŞ / KAYIT / ONAY MANTIĞI ---
        if not st.session_state.show_reg and st.session_state.temp_user is None:
            c1, c2 = st.columns([1, 2])
            with c1:
                load_pito("merhaba")
            with c2:
                st.markdown(f"<div class='pito-notu'>💬 <b>Pito:</b> {random.choice(msgs['login_welcome'])}</div>", unsafe_allow_html=True)
            
            num = st.number_input("Okul Numaranı Yaz Arkadaşım:", step=1, value=0)
            if num > 0 and st.button("Akademiye Gir 🚀"):
                res = supabase.table("kullanicilar").select("*").eq("ogrenci_no", int(num)).execute()
                if res.data:
                    st.session_state.temp_user = res.data[0]
                    st.rerun()
                else:
                    st.session_state.user_num = int(num)
                    st.session_state.show_reg = True
                    st.rerun()
        
        elif st.session_state.show_reg:
            st.markdown("<div class='pito-notu'>👋 Seni daha önce görmemiştim! Kaydını hemen yapalım genç yazılımcı.</div>", unsafe_allow_html=True)
            name = st.text_input("Adın Soyadın:")
            sinif = st.selectbox("Sınıfın:", ["9-A", "9-B", "10-A", "10-B", "11-A", "11-B", "12-A", "12-B"])
            if st.button("✨ Kaydı Tamamla ve Başla"):
                if name:
                    nu = {
                        "ogrenci_no": st.session_state.user_num, 
                        "ad_soyad": name, 
                        "sinif": sinif, 
                        "toplam_puan": 0, 
                        "mevcut_egzersiz": "1.1", 
                        "mevcut_modul": 1, 
                        "rutbe": "🥚 Çömez"
                    }
                    supabase.table("kullanicilar").insert(nu).execute()
                    st.session_state.user = nu
                    st.session_state.show_reg = False
                    st.rerun()
                else:
                    st.warning("Lütfen adını yaz arkadaşım!")

        elif st.session_state.temp_user:
            st.markdown(f"<div class='pito-notu'>👋 <b>Selam {st.session_state.temp_user['ad_soyad']}!</b> <br> Bu sen misin arkadaşım?</div>", unsafe_allow_html=True)
            c1, c2 = st.columns(2)
            if c1.button("✅ Evet, Benim!"):
                st.session_state.user = st.session_state.temp_user
                st.session_state.temp_user = None
                st.rerun()
            if c2.button("❌ Hayır, Değilim"):
                st.session_state.temp_user = None
                st.rerun()
    
    with col_tab:
        liderlik_tablosu_fonksiyonu()
