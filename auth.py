import streamlit as st
import random
import os
import base64

def login_ekrani(supabase, msgs, load_pito, liderlik_tablosu_fonksiyonu):
    # --- 0. SİBER-ESTETİK CSS (GİRİŞ ÖZEL) ---
    st.markdown('''
        <style>
        /* STANDARTLARI GİZLE */
        header[data-testid="stHeader"], [data-testid="stDecoration"], footer { display: none !important; }
        .stApp { background-color: #0e1117 !important; }

        /* MERKEZİ KONTEYNER */
        .auth-card {
            background: rgba(0, 229, 255, 0.03);
            border: 2px solid #00E5FF;
            border-radius: 20px;
            padding: 30px;
            box-shadow: 0 0 30px rgba(0, 229, 255, 0.1);
            margin-bottom: 20px;
        }

        .academy-title {
            color: #00E5FF;
            font-size: 2.5rem;
            font-weight: 900;
            text-align: center;
            text-shadow: 0 0 20px #00E5FF;
            margin-bottom: 10px;
            font-family: 'Fira Code', monospace;
        }

        /* PİTO KONUŞMA BALONU */
        .pito-bubble {
            background: #161b22;
            color: #E0E0E0;
            border-left: 5px solid #00E5FF;
            padding: 15px;
            border-radius: 10px;
            margin-bottom: 20px;
            font-style: italic;
        }

        /* BUTON STANDARTLARI (SİYAH METİN) */
        div.stButton > button { background-color: #00E5FF !important; border: none !important; transition: 0.3s; width: 100%; }
        div.stButton > button p, div.stButton > button span { color: #000000 !important; font-weight: 900 !important; }
        div.stButton > button:hover { background-color: #ADFF2F !important; box-shadow: 0 0 15px #ADFF2F; }

        /* INPUT ALANLARI */
        .stNumberInput input, .stTextInput input {
            background-color: #000 !important;
            color: #ADFF2F !important;
            border: 1px solid #333 !important;
        }
        </style>
    ''', unsafe_allow_html=True)

    # --- 1. SAYFA DÜZENİ ---
    col_in, col_tab = st.columns([1.8, 1.2], gap="large")
    
    with col_in:
        st.markdown('<div class="academy-title">🎓 PİTO PYTHON AKADEMİ</div>', unsafe_allow_html=True)
        st.markdown('<p style="text-align:center; color:#888;">Nusaybin Süleyman Bölünmez Anadolu Lisesi</p>', unsafe_allow_html=True)
        
        st.markdown('<div class="auth-card">', unsafe_allow_html=True)
        
        # --- A. VARSAYILAN GİRİŞ DURUMU ---
        if not st.session_state.show_reg and st.session_state.temp_user is None:
            c1, c2 = st.columns([1, 2.5])
            with c1:
                # Giriş ekranında Pito biraz daha görkemli (100px)
                load_pito("merhaba") 
            with c2:
                msg = random.choice(msgs['login_welcome'])
                st.markdown(f"<div class='pito-bubble'>💬 <b>Pito:</b> {msg}</div>", unsafe_allow_html=True)
            
            num = st.number_input("Okul Numaranı Yaz Arkadaşım:", step=1, value=0, help="Sana özel siber-kimliğine ulaşmam için numaran şart!")
            
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
                    st.warning("Numaranı yazmadan siber-geçitten geçemezsin!")

        # --- B. KAYIT DURUMU (YENİ SİBER-YAZILIMCI) ---
        elif st.session_state.show_reg:
            st.markdown(f"<div class='pito-bubble'>✨ <b>Yeni bir yetenek!</b> <br> {st.session_state.user_num} numarasını ilk kez görüyorum. Hadi seni sisteme kaydedelim!</div>", unsafe_allow_html=True)
            
            name = st.text_input("Adın ve Soyadın:", placeholder="Örn: Ali Yılmaz")
            sinif = st.selectbox("Sınıfın:", ["9-A", "9-B", "10-A", "10-B", "11-A", "11-B", "12-A", "12-B"])
            
            c_reg1, c_reg2 = st.columns(2)
            with c_reg1:
                if st.button("✨ KAYDI TAMAMLA"):
                    if name and len(name.split()) >= 2:
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
                        st.success("Siber-Kimlik Oluşturuldu! Giriş yapılıyor...")
                        st.rerun()
                    else:
                        st.error("Lütfen tam adını ve soyadını yaz arkadaşım!")
            with c_reg2:
                if st.button("⬅️ VAZGEÇ"):
                    st.session_state.show_reg = False
                    st.rerun()

        # --- C. ONAY DURUMU (ESKİ DOST) ---
        elif st.session_state.temp_user:
            st.markdown(f"<div class='pito-bubble'>👋 <b>Selam {st.session_state.temp_user['ad_soyad'].split()[0]}!</b> <br> Siber-hafızamda bu numara kayıtlı. Bu sen misin?</div>", unsafe_allow_html=True)
            
            c_on1, c_on2 = st.columns(2)
            with c_on1:
                if st.button("✅ EVET, BENİM!"):
                    st.session_state.user = st.session_state.temp_user
                    st.session_state.temp_user = None
                    st.rerun()
            with c_on2:
                if st.button("❌ HAYIR, DEĞİLİM"):
                    st.session_state.temp_user = None
                    st.rerun()

        st.markdown('</div>', unsafe_allow_html=True)

    with col_tab:
        # Sağ panelde liderlik tablosu parlasın
        st.markdown('<h3 style="text-align:center; color:#00E5FF;">🏆 EN İYİLER</h3>', unsafe_allow_html=True)
        liderlik_tablosu_fonksiyonu(supabase)
