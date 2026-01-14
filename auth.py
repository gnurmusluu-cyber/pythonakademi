import streamlit as st
import random
import os
import base64

def login_ekrani(supabase, msgs, load_pito, liderlik_tablosu_fonksiyonu):
    # --- 0. SİBER-GÖRSEL TASARIM (120PX PİTO & SPACING MÜHRÜ) ---
    st.markdown('''
        <style>
        header[data-testid="stHeader"], [data-testid="stDecoration"], footer { display: none !important; }
        .stApp { background-color: #0e1117 !important; }

        [data-testid="stMainViewContainer"] {
            padding-top: 60px !important; 
        }

        .academy-title {
            color: #00E5FF;
            font-size: 2.3rem;
            font-weight: 950;
            text-align: center;
            text-shadow: 0 0 20px #00E5FF;
            font-family: 'Fira Code', monospace;
            margin-bottom: 5px;
        }

        /* --- SİBER KONUŞMA BALONU (KUYRUKLU & FERAH) --- */
        .pito-bubble {
            position: relative;
            background: #161b22;
            color: #ADFF2F;
            border: 2px solid #00E5FF;
            padding: 20px;
            border-radius: 20px;
            margin-left: 25px;
            margin-bottom: 30px !important; /* Altındaki bileşenlerle mesafe */
            font-family: 'Fira Code', monospace;
            font-size: 1.1rem;
            box-shadow: 0 10px 30px rgba(0,0,0,0.5);
        }

        .pito-bubble:after {
            content: '';
            position: absolute;
            left: -20px;
            top: 45px;
            width: 0;
            height: 0;
            border-top: 15px solid transparent;
            border-right: 20px solid #00E5FF;
            border-bottom: 15px solid transparent;
        }

        /* 120PX GÖRKEMLİ PİTO */
        .pito-login-img img {
            width: 120px !important;
            height: 120px !important;
            border-radius: 50%;
            border: 3px solid #00E5FF;
            box-shadow: 0 0 25px rgba(0, 229, 255, 0.5);
        }

        /* INPUT VE BUTON ARALARI */
        .auth-spacer {
            margin-bottom: 25px;
        }

        div[data-testid="stTextInput"] input {
            background-color: #000 !important;
            color: #ADFF2F !important;
            border: 1px solid #333 !important;
            text-align: center;
            font-size: 1.1rem !important;
        }
        
        div.stButton > button { background-color: #00E5FF !important; border: none !important; transition: 0.3s; width: 100%; }
        div.stButton > button p, div.stButton > button span { color: #000000 !important; font-weight: 900 !important; }

        /* MOBİL DÜZENLEME */
        @media (max-width: 768px) {
            .academy-title { font-size: 1.6rem !important; }
            .pito-login-header { 
                flex-direction: row !important; 
                display: flex !important; 
                align-items: center !important; 
                gap: 12px !important;
                margin-bottom: 30px !important;
            }
            .pito-login-img img { width: 85px !important; height: 85px !important; }
            .pito-bubble { font-size: 0.85rem !important; padding: 15px !important; margin-left: 10px !important; }
            .pito-bubble:after { top: 25px !important; left: -15px !important; }
            [data-testid="stMainViewContainer"] { padding-top: 30px !important; }
        }
        </style>
    ''', unsafe_allow_html=True)

    col_in, col_tab = st.columns([1.8, 1.2], gap="large")
    
    with col_in:
        st.markdown('<div class="academy-title">🎓 PİTO PYTHON AKADEMİ</div>', unsafe_allow_html=True)
        st.markdown('<p style="text-align:center; color:#555; margin-bottom:40px;">Nusaybin Süleyman Bölünmez Anadolu Lisesi</p>', unsafe_allow_html=True)
        
        # --- A. GİRİŞ VE SORGULAMA ---
        if not st.session_state.show_reg and st.session_state.temp_user is None:
            st.markdown('<div class="pito-login-header">', unsafe_allow_html=True)
            c1, c2 = st.columns([1.2, 3])
            with c1:
                st.markdown('<div class="pito-login-img">', unsafe_allow_html=True)
                load_pito("merhaba")
                st.markdown('</div>', unsafe_allow_html=True)
            with c2:
                msg = random.choice(msgs['login_welcome'])
                st.markdown(f"<div class='pito-bubble'>💬 <b>Pito:</b> {msg}</div>", unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
            
            num_input = st.text_input("Okul Numaran:", placeholder="Sayı giriniz...", help="Numaranı yazınca siber-geçit açılacak!")
            
            st.markdown('<div class="auth-spacer"></div>', unsafe_allow_html=True)
            if st.button("AKADEMİYE BAĞLAN 🚀"):
                if num_input.isdigit():
                    num = int(num_input)
                    res = supabase.table("kullanicilar").select("*").eq("ogrenci_no", num).execute()
                    if res.data:
                        st.session_state.temp_user = res.data[0]; st.rerun()
                    else:
                        st.session_state.user_num = num
                        st.session_state.show_reg = True; st.rerun()
                else:
                    st.warning("🚨 Lütfen sadece geçerli bir sayı gir arkadaşım!")

        # --- B. KAYIT DÖNGÜSÜ ---
        elif st.session_state.show_reg:
            st.markdown('<div class="pito-login-header">', unsafe_allow_html=True)
            c1, c2 = st.columns([1.2, 3])
            with c1: load_pito("dusunuyor")
            with c2: st.markdown(f"<div class='pito-bubble'>✨ <b>Yeni bir yetenek!</b> <br> {st.session_state.user_num} numarasını ilk kez görüyorum. Kaydını yapalım!</div>", unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
            
            name = st.text_input("Adın ve Soyadın:", placeholder="Örn: Ali Yılmaz")
            sinif = st.selectbox("Sınıfın:", ["9-A", "9-B", "10-A", "10-B", "11-A", "11-B", "12-A", "12-B"])
            
            st.markdown('<div class="auth-spacer"></div>', unsafe_allow_html=True)
            c_reg1, c_reg2 = st.columns(2)
            if c_reg1.button("✨ KAYDI TAMAMLA"):
                if name and len(name.split()) >= 2:
                    nu = {"ogrenci_no": st.session_state.user_num, "ad_soyad": name, "sinif": sinif, "toplam_puan": 0, "mevcut_egzersiz": "1.1", "mevcut_modul": 1, "rutbe": "🥚 Çömez"}
                    supabase.table("kullanicilar").insert(nu).execute()
                    st.session_state.user = nu; st.session_state.show_reg = False; st.rerun()
                else: st.error("Tam adını yazmalısın arkadaşım!")
            if c_reg2.button("⬅️ VAZGEÇ"):
                st.session_state.show_reg = False; st.rerun()

        # --- C. ONAY DÖNGÜSÜ ---
        elif st.session_state.temp_user:
            ad_k = st.session_state.temp_user['ad_soyad'].split()[0]
            st.markdown('<div class="pito-login-header">', unsafe_allow_html=True)
            c1, c2 = st.columns([1.2, 3])
            with c1: load_pito("basari")
            with c2: st.markdown(f"<div class='pito-bubble'>👋 <b>Selam {ad_k}!</b> <br> Hafızam seni tanıdı. Bu sen misin?</div>", unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Balon ile butonlar arasına boşluk mühürlendi
            st.markdown('<div class="auth-spacer"></div>', unsafe_allow_html=True)
            c_on1, c_on2 = st.columns(2)
            if c_on1.button("✅ EVET, BENİM!"):
                st.session_state.user = st.session_state.temp_user
                st.session_state.temp_user = None; st.rerun()
            if c_on2.button("❌ HAYIR, DEĞİLİM"):
                st.session_state.temp_user = None; st.rerun()

    with col_tab:
        liderlik_tablosu_fonksiyonu()
