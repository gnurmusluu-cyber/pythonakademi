import streamlit as st
import random

def login_ekrani(supabase, msgs, load_pito, liderlik_tablosu_fonksiyonu):
    # --- 0. SİBER-GÖRSEL TASARIM ---
    st.markdown('''
        <style>
        header[data-testid="stHeader"], [data-testid="stDecoration"], footer { display: none !important; }
        .stApp { background-color: #0e1117 !important; }
        [data-testid="stMainViewContainer"] { padding-top: 60px !important; }
        .pito-bubble {
            position: relative; background: #161b22; color: #ADFF2F;
            border: 2px solid #00E5FF; padding: 20px; border-radius: 15px;
            font-size: 1.1rem; line-height: 1.4; box-shadow: 0 4px 15px rgba(0,229,255,0.2);
        }
        .auth-spacer { height: 30px; }
        </style>
    ''', unsafe_allow_html=True)

    st.markdown('<h1 style="text-align:center; color:#00E5FF; font-family:monospace;">💎 PİTO PYTHON AKADEMİ</h1>', unsafe_allow_html=True)

    # --- 1. PİTO KARŞILAMA ALANI ---
    st.markdown('<div class="pito-login-header">', unsafe_allow_html=True)
    c1, c2 = st.columns([1.2, 3])
    with c1:
        load_pito("merhaba")
    with c2:
        welcome_msg = random.choice(msgs.get('login_welcome', ["Siber dünyaya hoş geldin!"]))
        st.markdown(f'<div class="pito-bubble"><b>Pito:</b><br>{welcome_msg}</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="auth-spacer"></div>', unsafe_allow_html=True)

    # --- 2. KESİN GİRİŞ KONTROLÜ ---
    numara = st.text_input("OKUL NUMARANI GİR VE BAŞLA", placeholder="Örn: 123", key="login_input")
    
    if numara:
        try:
            # Sadece mevcut kullanıcıyı sorgula
            res = supabase.table("kullanicilar").select("*").eq("ogrenci_no", int(numara)).execute()
            
            if res.data:
                # EŞLEŞME VAR: Doğrudan giriş yap
                user_data = res.data[0]
                st.session_state.user = user_data
                st.success(f"Bağlantı Kuruldu! Hoş geldin, {user_data['ad_soyad']}!")
                st.rerun()
            else:
                # EŞLEŞME YOK: Erişim engellendi
                st.error("🚨 ERİŞİM REDDEDİLDİ: Bu numara siber arşivde kayıtlı değil. Lütfen öğretmenine danış!")
        except ValueError:
            st.error("Geçerli bir numara girmelisin genç yazılımcı!")

    # --- 3. LİDERLİK TABLOSU ---
    st.markdown('<div class="auth-spacer"></div>', unsafe_allow_html=True)
    liderlik_tablosu_fonksiyonu()
