import streamlit as st
import os
import base64

def pito_durum_belirle(error_count, cevap_dogru):
    """
    Hata sayısına ve başarı durumuna göre Pito'nun modunu döner.
    Giriş ve çalışma anı: merhaba
    1, 2, 3. hata: hata
    4. hata: dusunuyor
    Başarı: basari
    """
    if cevap_dogru:
        return "basari"
    elif error_count in [1, 2, 3]:
        return "hata"
    elif error_count >= 4:
        return "dusunuyor"
    else:
        return "merhaba"

def pito_goster(mod, size=180):
    """Assets klasöründeki GIF'i Base64 ile ekrana basar."""
    path = os.path.join(os.path.dirname(__file__), "assets", f"pito_{mod}.gif")
    if os.path.exists(path):
        with open(path, "rb") as f:
            encoded = base64.b64encode(f.read()).decode()
        st.markdown(
            f'<img src="data:image/gif;base64,{encoded}" width="{size}" style="border-radius: 20px; border: 2px solid #ADFF2F;">', 
            unsafe_allow_html=True
        )
    else:
        st.warning(f"GIF bulunamadı: pito_{mod}")