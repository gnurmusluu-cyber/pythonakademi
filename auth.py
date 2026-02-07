import streamlit as st
import random

def login_ekrani(supabase, msgs, load_pito, liderlik_tablosu_fonksiyonu):
    # --- 0. SİBER-GÖRSEL TASARIM (ÖNCEKİYLE AYNI) ---
    st.markdown('''
        <style>
        header[data-testid="stHeader"], [data-testid="stDecoration"], footer { display: none !important; }
        .stApp { background-color: #0e1117 !important; }
        .academy-title { color: #00E5FF; font-size: 2.3rem; font-weight: 950; text-align: center; font-family: 'Fira Code', monospace; }
        .pito-bubble { position: relative; background: #161b22; color: #ADFF2F; border: 2px solid #00E5FF; padding: 20px; border-radius: 20px; margin-left: 25px; }
        /* Butonun siyah metin kuralını koruyoruz */
        div.stButton > button p { color: #000 !important; font-weight: 900 !important; }
        </style>
    ''', unsafe_allow_html=True)

    col_in, col_tab = st.columns([1.8, 1.2], gap="large")
    
    with col_in:
        st.markdown('<div class="academy-title">🎓 PİTO PYTHON AKADEMİ</div>', unsafe_allow_html=True)
        
        if "login_step" not in st.session_state: st.session_state.login_step = "numara_girisi"

        # --- ADIM 1: OKUL NUMARASI SORGULAMA (FORM İLE FIX EDİLDİ) ---
        if st.session_state.login_step == "numara_girisi":
            st.markdown('<div class="pito-login-header">', unsafe_allow_html=True)
            c1, c2 = st.columns([1.2, 3])
            with c1: load_pito("merhaba")
            with c2:
                msg = random.choice(msgs.get('login_welcome', ["Hoş geldin!"]))
                st.markdown(f"<div class='pito-bubble'>💬 <b>Pito:</b> {msg}</div>", unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Donmayı engelleyen siber-form
            with st.form("numara_formu", clear_on_submit=False):
                num_input = st.text_input("Okul Numaran:", placeholder="Sayı giriniz...")
                submit = st.form_submit_button("SİBER-GEÇİDİ SORGULA 🔍")
                
                if submit:
                    if num_input.isdigit():
                        res = supabase.table("kullanicilar").select("*").eq("ogrenci_no", int(num_input)).execute()
                        if res.data:
                            user = res.data[0]
                            st.session_state.temp_num = int(num_input)
                            # Şifre kontrolü
                            if not user.get("sifre"):
                                st.session_state.login_step = "sifre_olustur"
                            else:
                                st.session_state.login_step = "sifre_giris"
                            st.rerun()
                        else:
                            st.error("🚨 Bu numara siber arşivde kayıtlı değil!")
                    else:
                        st.warning("Lütfen sadece sayı gir arkadaşım!")

        # --- ADIM 2: ŞİFRE OLUŞTURMA ---
        elif st.session_state.login_step == "sifre_olustur":
            with st.form("sifre_olustur_form"):
                st.info("✨ İlk girişin! 4 haneli siber-anahtarını belirle.")
                yeni_sifre = st.text_input("Yeni Şifren:", type="password")
                if st.form_submit_button("ANAHTARI MÜHÜRLE 🔐"):
                    if len(yeni_sifre) >= 2:
                        supabase.table("kullanicilar").update({"sifre": yeni_sifre}).eq("ogrenci_no", st.session_state.temp_num).execute()
                        st.session_state.login_step = "sifre_giris"
                        st.rerun()
                    else: st.error("Daha uzun bir şifre seç!")

        # --- ADIM 3: ŞİFRE GİRİŞİ ---
        elif st.session_state.login_step == "sifre_giris":
            with st.form("sifre_giris_form"):
                st.markdown("🔐 **Siber-Anahtarını Yaz**")
                girilen_sifre = st.text_input("Şifre:", type="password")
                if st.form_submit_button("BAĞLAN 🚀"):
                    res = supabase.table("kullanicilar").select("*").eq("ogrenci_no", st.session_state.temp_num).execute()
                    if res.data and str(res.data[0]["sifre"]) == str(girilen_sifre):
                        st.session_state.user = res.data[0]
                        st.rerun()
                    else: st.error("🚨 Yanlış anahtar!")
            
            if st.button("⬅️ NUMARAYI DEĞİŞTİR"):
                st.session_state.login_step = "numara_girisi"
                st.rerun()

    with col_tab:
        liderlik_tablosu_fonksiyonu()
