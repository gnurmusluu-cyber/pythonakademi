import streamlit as st
import random
import os
import base64

def login_ekrani(supabase, msgs, load_pito, liderlik_tablosu_fonksiyonu):
    # --- 0. SİBER-GÖRSEL TASARIM (DASHBOARD MÜHRÜ) ---
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

        /* --- SİBER KONUŞMA BALONU --- */
        .pito-bubble {
            position: relative;
            background: #161b22;
            color: #ADFF2F;
            border: 2px solid #00E5FF;
            padding: 20px;
            border-radius: 20px;
            margin-left: 25px;
            margin-bottom: 30px !important; 
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

        .pito-login-img img {
            width: 120px !important;
            height: 120px !important;
            border-radius: 50%;
            border: 3px solid #00E5FF;
            box-shadow: 0 0 25px rgba(0, 229, 255, 0.5);
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
        }
        </style>
    ''', unsafe_allow_html=True)

    # --- 1. SAYFA DÜZENİ (SOL: GİRİŞ, SAĞ: LİDERLİK) ---
    col_in, col_tab = st.columns([1.8, 1.2], gap="large")
    
    with col_in:
        st.markdown('<div class="academy-title">🎓 PİTO PYTHON AKADEMİ</div>', unsafe_allow_html=True)
        st.markdown('<p style="text-align:center; color:#888; margin-bottom:40px;">Nusaybin Süleyman Bölünmez Anadolu Lisesi</p>', unsafe_allow_html=True)
        
        # Pito Karşılama Alanı
        st.markdown('<div class="pito-login-header">', unsafe_allow_html=True)
        c1, c2 = st.columns([1.2, 3])
        with c1:
            st.markdown('<div class="pito-login-img">', unsafe_allow_html=True)
            load_pito("merhaba")
            st.markdown('</div>', unsafe_allow_html=True)
        with c2:
            # messages.json'dan rastgele bir karşılama mesajı
            msg = random.choice(msgs.get('login_welcome', ["Hoş geldin genç yazılımcı!"]))
            st.markdown(f"<div class='pito-bubble'>💬 <b>Pito:</b> {msg}</div>", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Giriş Alanı
        num_input = st.text_input("Okul Numaranı Yaz ve Siber-Geçidi Aç:", placeholder="Örn: 123", key="login_input")
        
        st.markdown('<div style="margin-bottom: 20px;"></div>', unsafe_allow_html=True)
        
        if st.button("AKADEMİYE BAĞLAN 🚀"):
            if num_input.isdigit():
                num = int(num_input)
                # Veritabanında (Supabase) öğrenci numarasını sorgula
                res = supabase.table("kullanicilar").select("*").eq("ogrenci_no", num).execute()
                
                if res.data:
                    # EŞLEŞME VAR: Doğrudan giriş yap ve state'leri temizle
                    st.session_state.user = res.data[0]
                    st.session_state.temp_user = None
                    st.session_state.show_reg = False
                    st.success(f"🔓 Erişim Onaylandı: {res.data[0]['ad_soyad']}")
                    st.rerun()
                else:
                    # EŞLEŞME YOK: Erişim reddedildi
                    st.error("🚨 ERİŞİM REDDEDİLDİ: Bu numara siber arşivde bulunamadı. Lütfen öğretmenine danış!")
            else:
                st.warning("🚨 Lütfen sadece geçerli bir sayı gir genç yazılımcı!")

    with col_tab:
        # Sağ tarafa Liderlik Tablosu (ranks.py üzerinden gelen fonksiyon)
        st.markdown('<div style="text-align:center; color:#00E5FF; font-weight:bold; margin-bottom:15px; font-family:monospace;">🏆 SİBER LİDERLER</div>', unsafe_allow_html=True)
        liderlik_tablosu_fonksiyonu()
