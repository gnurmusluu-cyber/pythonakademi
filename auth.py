import streamlit as st
import random
import os
import base64

def login_ekrani(supabase, msgs, load_pito, liderlik_tablosu_fonksiyonu):
    # --- 0. SİBER-GÖRSEL TASARIM (75PX & MOBİL YAN YANA MÜHRÜ) ---
    st.markdown('''
        <style>
        /* STANDARTLARI GİZLE */
        header[data-testid="stHeader"], [data-testid="stDecoration"], footer { display: none !important; }
        .stApp { background-color: #0e1117 !important; }

        /* ANA KONTEYNER BOŞLUĞU */
        [data-testid="stMainViewContainer"] {
            padding-top: 100px !important; 
        }

        .auth-card {
            background: rgba(0, 229, 255, 0.03);
            border: 2px solid #00E5FF;
            border-radius: 20px;
            padding: 25px;
            box-shadow: 0 0 30px rgba(0, 229, 255, 0.1);
        }

        .academy-title {
            color: #00E5FF;
            font-size: 2.2rem;
            font-weight: 900;
            text-align: center;
            text-shadow: 0 0 15px #00E5FF;
            font-family: 'Fira Code', monospace;
            margin-bottom: 5px;
        }

        /* PİTO KONUŞMA BALONU */
        .pito-bubble {
            background: #161b22;
            color: #E0E0E0;
            border-left: 5px solid #00E5FF;
            padding: 12px;
            border-radius: 10px;
            margin-bottom: 15px;
            font-size: 0.95rem;
            font-style: italic;
        }

        /* 75PX PİTO MÜHRÜ */
        .pito-login-img img {
            width: 75px !important;
            height: 75px !important;
            border-radius: 50%;
            border: 2px solid #00E5FF;
            box-shadow: 0 0 10px #00E5FF;
        }

        /* BUTON STANDARTLARI (SİYAH METİN) */
        div.stButton > button { background-color: #00E5FF !important; border: none !important; transition: 0.3s; width: 100%; }
        div.stButton > button p, div.stButton > button span { color: #000000 !important; font-weight: 900 !important; }
        div.stButton > button:hover { background-color: #ADFF2F !important; box-shadow: 0 0 15px #ADFF2F; }

        /* MOBİL DÜZENLEME (PİTO VE İSİM YAN YANA) */
        @media (max-width: 768px) {
            .academy-title { font-size: 1.6rem !important; }
            .pito-login-header { 
                flex-direction: row !important; 
                display: flex !important; 
                align-items: center !important; 
                gap: 15px !important;
                margin-bottom: 15px !important;
            }
            .pito-login-img img {
                width: 60px !important;
                height: 60px !important;
            }
            [data-testid="stMainViewContainer"] { padding-top: 50px !important; }
        }
        </style>
    ''', unsafe_allow_html=True)

    # --- 1. SAYFA DÜZENİ ---
    col_in, col_tab = st.columns([1.8, 1.2], gap="large")
    
    with col_in:
        st.markdown('<div class="academy-title">🎓 PİTO PYTHON AKADEMİ</div>', unsafe_allow_html=True)
        st.markdown('<p style="text-align:center; color:#555; margin-bottom:20px;">Nusaybin Süleyman Bölünmez Anadolu Lisesi</p>', unsafe_allow_html=True)
        
        st.markdown('<div class="auth-card">', unsafe_allow_html=True)
        
        # --- A. GİRİŞ VE SORGULAMA ---
        if not st.session_state.show_reg and st.session_state.temp_user is None:
            # Mobilde yan yana görünüm için özel wrapper class (pito-login-header)
            st.markdown('<div class="pito-login-header">', unsafe_allow_html=True)
            c1, c2 = st.columns([1, 3])
            with c1:
                st.markdown('<div class="pito-login-img">', unsafe_allow_html=True)
                load_pito("merhaba")
                st.markdown('</div>', unsafe_allow_html=True)
            with c2:
                msg = random.choice(msgs['login_welcome'])
                st.markdown(f"<div class='pito-bubble'>💬 <b>Pito:</b> {msg}</div>", unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
            
            num = st.number_input("Okul Numaranı Yaz Arkadaşım:", step=1, value=0)
            
            if st.button("AKADEMİYE BAĞLAN 🚀"):
                if num > 0:
                    res = supabase.table("kullanicilar").select("*").eq("ogrenci_no", int(num)).execute()
                    if res.data:
                        st.session_state.temp_user = res.data[0]
                        st.rerun()
                    else:
                        st.session_state.user_num = int(num)
                        st.session_state.show_reg = True
                        st.rerun()
                else:
                    st.warning("Numaranı yazmadan siber-geçit açılmaz!")

        # --- B. KAYIT VE ONAY AKIŞLARI (Aynı Görsel Standartla) ---
        elif st.session_state.show_reg:
            st.markdown(f"<div class='pito-bubble'>✨ <b>Yeni yetenek!</b> <br> {st.session_state.user_num} numarasını ilk kez görüyorum. Kaydını yapalım!</div>", unsafe_allow_html=True)
            name = st.text_input("Adın ve Soyadın:", placeholder="Örn: Ali Yılmaz")
            sinif = st.selectbox("Sınıfın:", ["9-A", "9-B", "10-A", "10-B", "11-A", "11-B", "12-A", "12-B"])
            
            c_r1, c_r2 = st.columns(2)
            with c_r1:
                if st.button("✨ KAYDI TAMAMLA"):
                    if name and len(name.split()) >= 2:
                        nu = {"ogrenci_no": st.session_state.user_num, "ad_soyad": name, "sinif": sinif, "toplam_puan": 0, "mevcut_egzersiz": "1.1", "mevcut_modul": 1, "rutbe": "🥚 Çömez"}
                        supabase.table("kullanicilar").insert(nu).execute()
                        st.session_state.user = nu
                        st.session_state.show_reg = False
                        st.rerun()
                    else:
                        st.error("Lütfen tam adını yaz arkadaşım!")
            with c_r2:
                if st.button("⬅️ VAZGEÇ"):
                    st.session_state.show_reg = False; st.rerun()

        elif st.session_state.temp_user:
            ad_k = st.session_state.temp_user['ad_soyad'].split()[0]
            st.markdown(f"<div class='pito-bubble'>👋 <b>Selam {ad_k}!</b> <br> Siber-hafızamda bu numara sana ait görünüyor. Bu sen misin?</div>", unsafe_allow_html=True)
            c_o1, c_o2 = st.columns(2)
            with c_o1:
                if st.button("✅ EVET, BENİM!"):
                    st.session_state.user = st.session_state.temp_user
                    st.session_state.temp_user = None; st.rerun()
            with c_o2:
                if st.button("❌ HAYIR, DEĞİLİM"):
                    st.session_state.temp_user = None; st.rerun()

        st.markdown('</div>', unsafe_allow_html=True)

    with col_tab:
        st.markdown('<h3 style="text-align:center; color:#00E5FF;">🏆 EN İYİLER</h3>', unsafe_allow_html=True)
        # Ranks.py içerisindeki fonksiyonu doğru parametreyle çağırıyoruz
        liderlik_tablosu_fonksiyonu(supabase)
