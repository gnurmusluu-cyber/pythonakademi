import streamlit as st
import random
import os
import base64

def login_ekrani(supabase, msgs, load_pito, liderlik_tablosu_fonksiyonu):
    # --- 0. SİBER-GÖRSEL TASARIM (ORİJİNAL KORUNDU & DASHBOARD DÜZENİ) ---
    st.markdown('''
        <style>
        header[data-testid="stHeader"], [data-testid="stDecoration"], footer { display: none !important; }
        .stApp { background-color: #0e1117 !important; }

        [data-testid="stMainViewContainer"] {
            padding-top: 40px !important; 
        }

        .academy-title {
            color: #00E5FF;
            font-size: 2.5rem;
            font-weight: 950;
            text-align: center;
            text-shadow: 0 0 20px #00E5FF;
            font-family: 'Fira Code', monospace;
            margin-bottom: 30px;
        }

        .pito-bubble {
            position: relative;
            background: #161b22;
            color: #ADFF2F;
            border: 2px solid #00E5FF;
            padding: 20px;
            border-radius: 15px;
            font-size: 1.1rem;
            line-height: 1.4;
            box-shadow: 0 4px 15px rgba(0,229,255,0.2);
            margin-bottom: 20px;
        }

        /* Giriş kutusu stili */
        div[data-testid="stTextInput"] label {
            color: #00E5FF !important;
            font-weight: bold;
            letter-spacing: 1px;
        }
        
        .auth-spacer { height: 20px; }
        </style>
    ''', unsafe_allow_html=True)

    st.markdown('<div class="academy-title">PİTO PYTHON AKADEMİ</div>', unsafe_allow_html=True)

    # --- 1. DASHBOARD YAPISI (SOL: GİRİŞ, SAĞ: LİDERLİK) ---
    col_left, col_right = st.columns([1.5, 1], gap="large")

    with col_left:
        # Pito Karşılama Alanı
        st.markdown('<div class="pito-login-header">', unsafe_allow_html=True)
        c1, c2 = st.columns([1, 2.5])
        with c1:
            load_pito("merhaba", size=150)
        with c2:
            welcome_msg = random.choice(msgs.get('login_welcome', ["Siber dünyaya hoş geldin!"]))
            st.markdown(f'<div class="pito-bubble"><b>Pito:</b><br>{welcome_msg}</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="auth-spacer"></div>', unsafe_allow_html=True)

        # Giriş Formu
        numara = st.text_input("SİSTEME ERİŞİM İÇİN OKUL NUMARANI GİR", placeholder="Örn: 123", key="login_input")
        
        if numara:
            try:
                res = supabase.table("kullanicilar").select("*").eq("ogrenci_no", int(numara)).execute()
                
                if res.data:
                    user_data = res.data[0]
                    # Temizlik ve Geçiş
                    st.session_state.user = user_data
                    st.session_state.temp_user = None
                    st.session_state.show_reg = False
                    
                    st.success(f"🔓 Erişim Onaylandı: {user_data['ad_soyad']}")
                    st.rerun()
                else:
                    st.error("🚨 SİSTEM HATASI: Numara bulunamadı. Lütfen öğretmenine başvur.")
            except ValueError:
                st.error("Lütfen sadece sayısal bir değer gir!")

    with col_right:
        # Sağ taraf Liderlik Tablosu için ayrıldı
        st.markdown('<div style="text-align:center; color:#ADFF2F; font-weight:bold; margin-bottom:10px;">🏆 EN İYİ SAVAŞÇILAR</div>', unsafe_allow_html=True)
        liderlik_tablosu_fonksiyonu()
