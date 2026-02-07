import streamlit as st
import random
import os
import base64

def login_ekrani(supabase, msgs, load_pito, liderlik_tablosu_fonksiyonu):
    # --- 0. SİBER-GÖRSEL TASARIM (DASHBOARD & ŞİFRE PANELİ) ---
    st.markdown('''
        <style>
        header[data-testid="stHeader"], [data-testid="stDecoration"], footer { display: none !important; }
        .stApp { background-color: #0e1117 !important; }
        [data-testid="stMainViewContainer"] { padding-top: 60px !important; }
        .academy-title {
            color: #00E5FF; font-size: 2.3rem; font-weight: 950; text-align: center;
            text-shadow: 0 0 20px #00E5FF; font-family: 'Fira Code', monospace; margin-bottom: 5px;
        }
        .pito-bubble {
            position: relative; background: #161b22; color: #ADFF2F;
            border: 2px solid #00E5FF; padding: 20px; border-radius: 20px;
            margin-left: 25px; margin-bottom: 30px !important; 
            font-family: 'Fira Code', monospace; font-size: 1.1rem;
            box-shadow: 0 10px 30px rgba(0,0,0,0.5);
        }
        .pito-bubble:after {
            content: ''; position: absolute; left: -20px; top: 45px;
            width: 0; height: 0; border-top: 15px solid transparent;
            border-right: 20px solid #00E5FF; border-bottom: 15px solid transparent;
        }
        .pito-login-img img {
            width: 120px !important; height: 120px !important;
            border-radius: 50%; border: 3px solid #00E5FF;
            box-shadow: 0 0 25px rgba(0, 229, 255, 0.5);
        }
        div[data-testid="stTextInput"] input {
            background-color: #000 !important; color: #ADFF2F !important;
            border: 1px solid #333 !important; text-align: center; font-size: 1.1rem !important;
        }
        div.stButton > button { background-color: #00E5FF !important; border: none !important; width: 100%; }
        div.stButton > button p { color: #000 !important; font-weight: 900 !important; }
        </style>
    ''', unsafe_allow_html=True)

    col_in, col_tab = st.columns([1.8, 1.2], gap="large")
    
    with col_in:
        st.markdown('<div class="academy-title">🎓 PİTO PYTHON AKADEMİ</div>', unsafe_allow_html=True)
        st.markdown('<p style="text-align:center; color:#888; margin-bottom:40px;">Nusaybin Süleyman Bölünmez Anadolu Lisesi</p>', unsafe_allow_html=True)
        
        # --- 1. OTURUM DURUMU KONTROLÜ ---
        if "login_step" not in st.session_state: st.session_state.login_step = "numara_girisi"
        if "temp_num" not in st.session_state: st.session_state.temp_num = None

        # --- ADIM 1: OKUL NUMARASI SORGULAMA ---
        if st.session_state.login_step == "numara_girisi":
            st.markdown('<div class="pito-login-header">', unsafe_allow_html=True)
            c1, c2 = st.columns([1.2, 3])
            with c1: load_pito("merhaba")
            with c2:
                msg = random.choice(msgs.get('login_welcome', ["Hoş geldin!"]))
                st.markdown(f"<div class='pito-bubble'>💬 <b>Pito:</b> {msg}</div>", unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
            
            num_input = st.text_input("Okul Numaran:", placeholder="Sayı giriniz...", key="n_in")
            if st.button("SİBER-GEÇİDİ SORGULA 🔍"):
                if num_input.isdigit():
                    res = supabase.table("kullanicilar").select("*").eq("ogrenci_no", int(num_input)).execute()
                    if res.data:
                        user = res.data[0]
                        st.session_state.temp_num = int(num_input)
                        # Şifre daha önce oluşturulmuş mu? (Veritabanında 'sifre' sütunu olmalı)
                        if user.get("sifre") is None or user.get("sifre") == "":
                            st.session_state.login_step = "sifre_olustur"
                        else:
                            st.session_state.login_step = "sifre_giris"
                        st.rerun()
                    else:
                        st.error("🚨 Bu numara siber arşivde kayıtlı değil!")
                else:
                    st.warning("Lütfen geçerli bir numara yaz!")

        # --- ADIM 2: İLK GİRİŞ - ŞİFRE OLUŞTURMA ---
        elif st.session_state.login_step == "sifre_olustur":
            st.markdown('<div class="pito-login-header">', unsafe_allow_html=True)
            c1, c2 = st.columns([1.2, 3])
            with c1: load_pito("basari")
            with c2: st.markdown("<div class='pito-bubble'>✨ <b>İlk kez mi geliyorsun?</b><br>Güvenliğin için kendine 4 haneli bir siber-anahtar belirle!</div>", unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
            
            yeni_sifre = st.text_input("Yeni Şifren:", type="password", help="Sadece rakam öneririm!")
            if st.button("ANAHTARI MÜHÜRLE 🔐"):
                if len(yeni_sifre) >= 2:
                    supabase.table("kullanicilar").update({"sifre": yeni_sifre}).eq("ogrenci_no", st.session_state.temp_num).execute()
                    st.success("Şifren kaydedildi! Şimdi giriş yapabilirsin.")
                    st.session_state.login_step = "sifre_giris"
                    st.rerun()
                else: st.error("Daha güvenli bir şifre seçmelisin!")

        # --- ADIM 3: SONRAKİ GİRİŞLER - ŞİFRE DOĞRULAMA ---
        elif st.session_state.login_step == "sifre_giris":
            st.markdown('<div class="pito-login-header">', unsafe_allow_html=True)
            c1, c2 = st.columns([1.2, 3])
            with c1: load_pito("merhaba")
            with c2: st.markdown("<div class='pito-bubble'>🔐 <b>Siber-Anahtar Gerekli</b><br>Hafızamdaki şifrenle eşleşecek anahtarı gir arkadaşım.</div>", unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
            
            girilen_sifre = st.text_input("Şifreni Yaz:", type="password")
            c_btn1, c_btn2 = st.columns(2)
            if c_btn1.button("BAĞLAN 🚀"):
                res = supabase.table("kullanicilar").select("*").eq("ogrenci_no", st.session_state.temp_num).execute()
                if res.data and str(res.data[0]["sifre"]) == str(girilen_sifre):
                    st.session_state.user = res.data[0]
                    st.rerun()
                else:
                    st.error("🚨 Yanlış anahtar! Tekrar dene.")
            if c_btn2.button("⬅️ NUMARAYI DEĞİŞTİR"):
                st.session_state.login_step = "numara_girisi"
                st.rerun()

    with col_tab:
        liderlik_tablosu_fonksiyonu()
