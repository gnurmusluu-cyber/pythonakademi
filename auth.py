import streamlit as st
import random
import os
import base64

def login_ekrani(supabase, msgs, load_pito, liderlik_tablosu_fonksiyonu):
    # --- 0. SİBER-GÖRSEL TASARIM (DOSYANDAKİ ORİJİNAL YAPI) ---
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
        }

        .auth-spacer { height: 30px; }
        </style>
    ''', unsafe_allow_html=True)

    st.markdown('<div class="academy-title">PİTO PYTHON AKADEMİ</div>', unsafe_allow_html=True)

    # --- 1. PİTO KARŞILAMA VE GİRİŞ ALANI ---
    # Not: Onay ve Kayıt state'lerini tamamen devre dışı bırakıyoruz
    st.markdown('<div class="pito-login-header">', unsafe_allow_html=True)
    c1, c2 = st.columns([1.2, 3])
    with c1:
        load_pito("merhaba")
    with c2:
        welcome_msg = random.choice(msgs.get('login_welcome', ["Siber dünyaya hoş geldin!"]))
        st.markdown(f'<div class="pito-bubble"><b>Pito:</b><br>{welcome_msg}</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="auth-spacer"></div>', unsafe_allow_html=True)

    # --- 2. GİRİŞ KONTROLÜ (DOĞRUDAN GEÇİŞ) ---
    numara = st.text_input("OKUL NUMARANI GİR VE BAŞLA", placeholder="Örn: 123", key="login_input")
    
    if numara:
        try:
            # Okul numarasını veritabanında ara
            res = supabase.table("kullanicilar").select("*").eq("ogrenci_no", int(numara)).execute()
            
            if res.data:
                # EŞLEŞME VAR: Kullanıcıyı state'e al ve temizlik yap
                user_data = res.data[0]
                st.session_state.user = user_data
                
                # Geçişi garantilemek için geçici state'leri temizliyoruz
                st.session_state.temp_user = None
                st.session_state.show_reg = False
                
                st.success(f"Bağlantı Kuruldu! Hoş geldin, {user_data['ad_soyad']}!")
                st.rerun() # p_akademi.py bu noktada education.egitim_ekrani'nı tetikleyecektir
            else:
                # EŞLEŞME YOK: Yeni kayıt sistemini kaldırdığımız için sadece hata veriyoruz
                st.error("🚨 ERİŞİM REDDEDİLDİ: Bu numara siber arşivde kayıtlı değil. Lütfen öğretmenine danış!")
        except ValueError:
            st.error("Lütfen sadece sayılardan oluşan bir numara gir!")

    # --- 3. LİDERLİK TABLOSU (ORİJİNAL YERİNDE) ---
    st.markdown('<div class="auth-spacer"></div>', unsafe_allow_html=True)
    liderlik_tablosu_fonksiyonu()
