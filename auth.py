import streamlit as st
import random
import os
import base64

def login_ekrani(supabase, msgs, load_pito, liderlik_tablosu_fonksiyonu):
    # --- 0. SİBER-GÖRSEL TASARIM ---
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

    # --- 1. DASHBOARD YAPISI ---
    col_in, col_tab = st.columns([1.8, 1.2], gap="large")
    
    with col_in:
        st.markdown('<div class="academy-title">🎓 PİTO PYTHON AKADEMİ</div>', unsafe_allow_html=True)
        st.markdown('<p style="text-align:center; color:#888; margin-bottom:40px;">Nusaybin Süleyman Bölünmez Anadolu Lisesi</p>', unsafe_allow_html=True)
        
        if "login_step" not in st.session_state: st.session_state.login_step = "numara_girisi"
        if "temp_num" not in st.session_state: st.session_state.temp_num = None

        # --- ADIM 1: OKUL NUMARASI VE GİZLİ GEÇİT SORGULAMA ---
        if st.session_state.login_step == "numara_girisi":
            st.markdown('<div class="pito-login-header">', unsafe_allow_html=True)
            c1, c2 = st.columns([1.2, 3])
            with c1: load_pito("merhaba")
            with c2:
                msg = random.choice(msgs.get('login_welcome', ["Hoş geldin!"]))
                st.markdown(f"<div class='pito-bubble'>💬 <b>Pito:</b> {msg}</div>", unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
            
            with st.form("numara_sorgu_formu"):
                num_input = st.text_input("Giriş Anahtarı:", placeholder="Okul numaranı yaz...")
                submit = st.form_submit_button("SİBER-GEÇİDİ SORGULA 🔍")
                
                if submit:
                    # GİZLİ ÖĞRETMEN PANELİ ANAHTARI
                    if num_input == "5520161990":
                        st.session_state.login_step = "ogretmen_paneli"
                        st.rerun()
                    
                    elif num_input.isdigit():
                        num = int(num_input)
                        res = supabase.table("kullanicilar").select("*").eq("ogrenci_no", num).execute()
                        
                        if res.data:
                            user = res.data[0]
                            # SINIF KİLİT KONTROLÜ
                            kilit_res = supabase.table("ayarlar").select("deger").eq("anahtar", "aktif_sinif").execute()
                            aktif_sinif = kilit_res.data[0]['deger'] if kilit_res.data else "KAPALI"
                            
                            if aktif_sinif != "KAPALI" and user['sinif'] == aktif_sinif:
                                st.session_state.temp_num = num
                                if not user.get("sifre"):
                                    st.session_state.login_step = "sifre_olustur"
                                else:
                                    st.session_state.login_step = "sifre_giris"
                                st.rerun()
                            else:
                                st.error(f"🚫 ERİŞİM ENGELLENDİ: Şu an sadece {aktif_sinif} sınıfı derstedir.")
                        else:
                            st.error("🚨 Bu numara siber arşivde kayıtlı değil!")

        # --- ADIM 2: ÖĞRETMEN YÖNETİM PANELİ ---
        elif st.session_state.login_step == "ogretmen_paneli":
            st.markdown("### 🔐 SİBER-GEÇİT YÖNETİMİ")
            res = supabase.table("ayarlar").select("deger").eq("anahtar", "aktif_sinif").execute()
            su_anki = res.data[0]['deger'] if res.data else "KAPALI"
            
            st.info(f"Şu an erişim açık olan grup: **{su_anki}**")
            
            siniflar = ["KAPALI", "9-A", "9-B", "10-A", "10-B", "11-A", "11-B", "12-A", "12-B"]
            yeni_sinif = st.selectbox("Erişimi açılacak sınıfı seç:", siniflar)
            
            if st.button("KİLİDİ GÜNCELLE 🔑"):
                supabase.table("ayarlar").update({"deger": yeni_sinif}).eq("anahtar", "aktif_sinif").execute()
                st.success(f"Erişim {yeni_sinif} için mühürlendi!")
                st.rerun()
                
            if st.button("⬅️ GİRİŞ EKRANINA DÖN"):
                st.session_state.login_step = "numara_girisi"
                st.rerun()

        # --- ADIM 3: İLK GİRİŞ - ŞİFRE OLUŞTURMA ---
        elif st.session_state.login_step == "sifre_olustur":
            with st.form("sifre_ol_form"):
                st.info("✨ İlk girişin! Kendine 4 haneli bir siber-anahtar belirle.")
                yeni = st.text_input("Yeni Şifre:", type="password")
                if st.form_submit_button("ANAHTARI MÜHÜRLE 🔐"):
                    if len(yeni) >= 2:
                        supabase.table("kullanicilar").update({"sifre": yeni}).eq("ogrenci_no", st.session_state.temp_num).execute()
                        st.session_state.login_step = "sifre_giris"
                        st.rerun()

        # --- ADIM 4: ŞİFRE DOĞRULAMA ---
        elif st.session_state.login_step == "sifre_giris":
            with st.form("sifre_gir_form"):
                st.markdown("🔐 **Siber-Anahtar Gerekli**")
                girilen = st.text_input("Şifre:", type="password")
                if st.form_submit_button("BAĞLAN 🚀"):
                    res = supabase.table("kullanicilar").select("*").eq("ogrenci_no", st.session_state.temp_num).execute()
                    if res.data and str(res.data[0]["sifre"]) == str(girilen):
                        st.session_state.user = res.data[0]
                        st.rerun()
                    else: st.error("🚨 Yanlış anahtar!")
            
            if st.button("⬅️ NUMARAYI DEĞİŞTİR"):
                st.session_state.login_step = "numara_girisi"
                st.rerun()

    with col_tab:
        liderlik_tablosu_fonksiyonu()
