import streamlit as st
import random
import os
import base64

def login_ekrani(supabase, msgs, load_pito, liderlik_tablosu_fonksiyonu):
    # --- 0. SİBER-KONUŞMA BALONU VE TEMİZLİK CSS ---
    st.markdown('''
        <style>
        /* STANDARTLARI İMHA ET */
        header[data-testid="stHeader"], [data-testid="stDecoration"], footer { display: none !important; }
        .stApp { background-color: #0e1117 !important; }

        /* ANA KONTEYNER (SADE VE FERAH) */
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

        /* --- SİBER KONUŞMA BALONU (KUYRUKLU) --- */
        .pito-bubble {
            position: relative;
            background: #161b22;
            color: #ADFF2F; /* Siber-Yeşil yazı */
            border: 1px solid #00E5FF;
            padding: 18px;
            border-radius: 15px;
            margin-left: 20px;
            font-family: 'Fira Code', monospace;
            font-size: 1.05rem;
            box-shadow: 0 5px 15px rgba(0,0,0,0.3);
        }

        /* Konuşma Balonu Kuyruğu */
        .pito-bubble:after {
            content: '';
            position: absolute;
            left: -15px;
            top: 25px;
            width: 0;
            height: 0;
            border-top: 10px solid transparent;
            border-right: 15px solid #00E5FF;
            border-bottom: 10px solid transparent;
        }

        /* 75PX PİTO MÜHRÜ */
        .pito-login-img img {
            width: 75px !important;
            height: 75px !important;
            border-radius: 50%;
            border: 2px solid #00E5FF;
            box-shadow: 0 0 15px rgba(0, 229, 255, 0.4);
        }

        /* OKUNABİLİR BUTONLAR (SİYAH METİN) */
        div.stButton > button { background-color: #00E5FF !important; border: none !important; transition: 0.3s; width: 100%; }
        div.stButton > button p, div.stButton > button span { color: #000000 !important; font-weight: 900 !important; }
        div.stButton > button:hover { background-color: #ADFF2F !important; box-shadow: 0 0 20px #ADFF2F; }

        /* MOBİL DÜZENLEME (YAN YANA MÜHRÜ) */
        @media (max-width: 768px) {
            .academy-title { font-size: 1.7rem !important; }
            .pito-login-header { 
                flex-direction: row !important; 
                display: flex !important; 
                align-items: center !important; 
                gap: 10px !important;
                margin-bottom: 20px !important;
            }
            .pito-bubble { font-size: 0.9rem !important; padding: 12px !important; margin-left: 10px !important; }
            .pito-bubble:after { top: 15px !important; }
            .pito-login-img img { width: 65px !important; height: 65px !important; }
            [data-testid="stMainViewContainer"] { padding-top: 30px !important; }
        }
        </style>
    ''', unsafe_allow_html=True)

    # --- 1. SAYFA DÜZENİ ---
    col_in, col_tab = st.columns([1.8, 1.2], gap="large")
    
    with col_in:
        st.markdown('<div class="academy-title">🎓 PİTO PYTHON AKADEMİ</div>', unsafe_allow_html=True)
        st.markdown('<p style="text-align:center; color:#555; margin-bottom:30px;">Nusaybin Süleyman Bölünmez Anadolu Lisesi</p>', unsafe_allow_html=True)
        
        # --- A. GİRİŞ VE SORGULAMA ---
        if not st.session_state.show_reg and st.session_state.temp_user is None:
            st.markdown('<div class="pito-login-header">', unsafe_allow_html=True)
            c1, c2 = st.columns([1, 4])
            with c1:
                st.markdown('<div class="pito-login-img">', unsafe_allow_html=True)
                load_pito("merhaba")
                st.markdown('</div>', unsafe_allow_html=True)
            with c2:
                msg = random.choice(msgs['login_welcome'])
                # Kullanıcının istediği o özel vurguyu yapıyoruz
                st.markdown(f"<div class='pito-bubble'>💬 <b>Pito:</b> {msg}</div>", unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
            
            num = st.number_input("Okul Numaranı Yaz Arkadaşım:", step=1, value=0)
            
            if st.button("AKADEMİYE BAĞLAN 🚀"):
                if num > 0:
                    res = supabase.table("kullanicilar").select("*").eq("ogrenci_no", int(num)).execute()
                    if res.data:
                        st.session_state.temp_user = res.data[0]; st.rerun()
                    else:
                        st.session_state.user_num = int(num)
                        st.session_state.show_reg = True; st.rerun()
                else:
                    st.warning("Numaranı yazmadan geçit açılmaz!")

        # --- B. KAYIT DÖNGÜSÜ ---
        elif st.session_state.show_reg:
            st.markdown(f"<div class='pito-bubble'>✨ <b>Yeni bir yetenek!</b> <br> {st.session_state.user_num} numarasını ilk kez görüyorum. Kaydını yapalım!</div>", unsafe_allow_html=True)
            name = st.text_input("Adın ve Soyadın:", placeholder="Örn: Ali Yılmaz")
            sinif = st.selectbox("Sınıfın:", ["9-A", "9-B", "10-A", "10-B", "11-A", "11-B", "12-A", "12-B"])
            
            c_reg1, c_reg2 = st.columns(2)
            if c_reg1.button("✨ KAYDI TAMAMLA"):
                if name and len(name.split()) >= 2:
                    nu = {"ogrenci_no": st.session_state.user_num, "ad_soyad": name, "sinif": sinif, "toplam_puan": 0, "mevcut_egzersiz": "1.1", "mevcut_modul": 1, "rutbe": "🥚 Çömez"}
                    supabase.table("kullanicilar").insert(nu).execute()
                    st.session_state.user = nu; st.session_state.show_reg = False; st.rerun()
                else: st.error("Lütfen tam adını yaz arkadaşım!")
            if c_r2.button("⬅️ VAZGEÇ"):
                st.session_state.show_reg = False; st.rerun()

        # --- C. ONAY DÖNGÜSÜ ---
        elif st.session_state.temp_user:
            ad_k = st.session_state.temp_user['ad_soyad'].split()[0]
            st.markdown(f"<div class='pito-bubble'>👋 <b>Selam {ad_k}!</b> <br> Hafızam seni tanıdı. Bu sen misin?</div>", unsafe_allow_html=True)
            c_on1, c_on2 = st.columns(2)
            if c_on1.button("✅ EVET, BENİM!"):
                st.session_state.user = st.session_state.temp_user
                st.session_state.temp_user = None; st.rerun()
            if c_on2.button("❌ HAYIR, DEĞİLİM"):
                st.session_state.temp_user = None; st.rerun()

    with col_tab:
        # Ranks.py zaten kendi başlığını (Onur Kürsüsü) basıyor, biz sadece çağırıyoruz.
        liderlik_tablosu_fonksiyonu()
