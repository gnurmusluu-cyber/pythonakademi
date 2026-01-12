import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
import base64

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="Pito Python Akademi", layout="wide")

# --- CSS: ÖĞRENCİ DOSTU ARAYÜZ ---
st.markdown("""
    <style>
    .stButton>button { border-radius: 20px; height: 3.5em; font-weight: bold; background-color: #FF4B4B; color: white; border: none; }
    .stTextInput>div>div>input { border: 3px solid #FF4B4B !important; border-radius: 10px; padding: 10px; font-size: 18px; }
    .pito-box { background-color: #ffffff; padding: 20px; border-radius: 15px; border-left: 10px solid #FF4B4B; box-shadow: 2px 2px 10px rgba(0,0,0,0.1); margin-bottom: 20px; }
    .leaderboard-text { font-size: 14px; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# --- GIF FONKSİYONU ---
def pito_gif(gif_name):
    try:
        file_ = open(f"assets/{gif_name}", "rb")
        contents = file_.read()
        data_url = base64.b64encode(contents).decode("utf-8")
        file_.close()
        st.markdown(f'<div style="text-align:center;"><img src="data:image/gif;base64,{data_url}" width="220"></div>', unsafe_allow_html=True)
    except:
        st.warning(f"🐍 Pito ({gif_name}) dosyası assets klasöründe bulunamadı.")

# --- MÜFREDAT: 8 MODÜL x 5 EGZERSİZ ---
MUREDDTAT = {
    1: {"baslik": "Python'ın Sesi", "not": "Python dünyasına hoş geldin! Bilgisayara bir şeyler söyletmek için 'print' fonksiyonunu kullanırız. Metinleri her zaman tırnak (' ') içinde yazmalısın.", 
        "egz": [
            {"q": "Ekrana Merhaba yazdır: ____(\"Merhaba\")", "a": "print", "h": "Konuşma komutunu hatırla!", "out": "Merhaba"},
            {"q": "Tırnağı tamamla: print(__Selam\")", "a": "\"", "h": "Metinler neyin içine yazılır?", "out": "Selam"},
            {"q": "Parantezi kapat: print(\"Nusaybin\"__", "a": ")", "h": "Her fonksiyon parantezle biter.", "out": "Nusaybin"},
            {"q": "Kendi ismini yazdır: print(\"____\")", "a": "Pito", "h": "Herhangi bir isim yazabilirsin.", "out": "Pito"},
            {"q": "Çıktı komutu: ____(\"Kodluyorum\")", "a": "print", "h": "Yazdır komutu.", "out": "Kodluyorum"}]},
    2: {"baslik": "Hafıza Kutuları", "not": "Değişkenler verileri saklar. 'ad = \"Pito\"' gibi. 'ad' anahtar, 'Pito' ise nesnedir.", 
        "egz": [
            {"q": "Değişken tanımla: x __ 5", "a": "=", "h": "Atama işareti nedir?", "out": ""},
            {"q": "Kutuyu isimlendir: ____ = \"Mardin\"", "a": "sehir", "h": "Bir isim ver (örn: sehir).", "out": ""},
            {"q": "Değişkeni yazdır: print(__)", "a": "x", "h": "Tırnak kullanma!", "out": "5"},
            {"q": "Sayıyı sakla: yas = __", "a": "16", "h": "Bir sayı gir.", "out": ""},
            {"q": "Topla: a=2, b=3, print(a__b)", "a": "+", "h": "Toplama işareti.", "out": "5"}]},
    3: {"baslik": "Veri Tipleri", "not": "Python'da sayılar (int), metinler (str) ve ondalıklılar (float) vardır. type() ile tipi öğrenebiliriz.", 
        "egz": [
            {"q": "Sayıya çevir: ____(\"10\")", "a": "int", "h": "Integer kısaltması.", "out": "10"},
            {"q": "Metne çevir: ____(5)", "a": "str", "h": "String kısaltması.", "out": "'5'"},
            {"q": "Tipi bul: ____(3.14)", "a": "type", "h": "Tip öğrenme komutu.", "out": "<class 'float'>"},
            {"q": "Float tanımla: boy = 1.__", "a": "75", "h": "Ondalık değer yaz.", "out": ""},
            {"q": "Hangi tip: type(\"A\") = ____", "a": "str", "h": "Metin tipi nedir?", "out": ""}]},
    4: {"baslik": "Matematiksel Güç", "not": "Python ile hesap yapmak çok kolay! +, -, *, / dışında % kalan, ** üs alma demektir.", 
        "egz": [
            {"q": "Kalanı bul (7 % 2): ____", "a": "1", "h": "7'nin 2'ye bölümünden kalan.", "out": "1"},
            {"q": "Üs al (2'nin küpü): 2 __ 3", "a": "**", "h": "Üs alma işareti.", "out": "8"},
            {"q": "Tam bölme (9 // 4): ____", "a": "2", "h": "9'da 4 kaç kere tam var?", "out": "2"},
            {"q": "Çarp: 5 __ 4 = 20", "a": "*", "h": "Çarpma işareti.", "out": "20"},
            {"q": "Böl: 10 __ 2 = 5.0", "a": "/", "h": "Bölme işareti.", "out": "5.0"}]},
    5: {"baslik": "input() ile Sohbet", "not": "input() kullanıcıdan veri alır. Gelen her veri 'str' (metin) tipindedir.", 
        "egz": [
            {"q": "Veri al: ad = ____(\"Adın?\")", "a": "input", "h": "Giriş komutu.", "out": ""},
            {"q": "Sayı al: yas = ____(input())", "a": "int", "h": "Girdiyi sayıya çevir.", "out": ""},
            {"q": "Mesaj: print(f\"Selam {____}\")", "a": "ad", "h": "Değişkeni yaz.", "out": "Selam ..."},
            {"q": "Giriş: input(\"____ gir:\")", "a": "Sayı", "h": "Herhangi bir kelime.", "out": ""},
            {"q": "Değişken: ____ = input()", "a": "cevap", "h": "Bir isim seç.", "out": ""}]},
    6: {"baslik": "Yol Ayrımı: if-else", "not": "Şartlar sağlandığında 'if', sağlanmadığında 'else' bloğu çalışır. İki nokta (:) unutulmamalı!", 
        "egz": [
            {"q": "Eşit mi: if x ____ 10:", "a": "==", "h": "Çift eşittir kullan.", "out": ""},
            {"q": "Değilse: ____:", "a": "else", "h": "Diğer durum komutu.", "out": ""},
            {"q": "Nokta ekle: if x > 5__", "a": ":", "h": "Blok sonu işareti.", "out": ""},
            {"q": "Küçükse: if yas ____ 18:", "a": "<", "h": "Küçüktür işareti.", "out": ""},
            {"q": "Veya: ____ x == 5:", "a": "elif", "h": "Else-if kısaltması.", "out": ""}]},
    7: {"baslik": "Döngü Döngüsü", "not": "Döngüler işleri tekrar eder. 'for' belirli sayıda, 'while' ise şart sürdükçe çalışır.", 
        "egz": [
            {"q": "Döngü: ____ i in range(3):", "a": "for", "h": "Tekrarlama komutu.", "out": "0 1 2"},
            {"q": "Sınır: range(____)", "a": "5", "h": "3 kere dönmesi için?", "out": ""},
            {"q": "Şartlı: ____ x < 10:", "a": "while", "h": "Sürece komutu.", "out": ""},
            {"q": "Durdur: if x==2: ____", "a": "break", "h": "Kırma komutu.", "out": ""},
            {"q": "Sayıcı: i = i __ 1", "a": "+", "h": "Artırma işareti.", "out": ""}]},
    8: {"baslik": "Veri Listeleri", "not": "Listeler birden fazla veriyi tutar. [ ] içinde yazılır ve saymaya 0'dan başlanır.", 
        "egz": [
            {"q": "Liste: renk = [____]", "a": "\"al\"", "h": "Tırnaklı bir renk.", "out": ""},
            {"q": "Ekle: renk.____(\"ak\")", "a": "append", "h": "Sona ekleme metodu.", "out": ""},
            {"q": "İlk eleman: print(renk[____])", "a": "0", "h": "Başlangıç indeksi.", "out": ""},
            {"q": "Sil: renk.____(\"al\")", "a": "remove", "h": "Silme metodu.", "out": ""},
            {"q": "Uzunluk: ____(renk)", "a": "len", "h": "Sayma fonksiyonu.", "out": ""}]}
}

# --- VERİ İŞLEME ---
conn = st.connection("gsheets", type=GSheetsConnection)

def get_data():
    return conn.read(spreadsheet=SHEET_URL)

# --- SİDEBAR: LİDERLİK TABLOLARI ---
def render_sidebar(df):
    with st.sidebar:
        st.markdown("### 🏆 Okul Liderlik")
        top_school = df.nlargest(10, 'Puan')[['Öğrencinin Adı', 'Rütbe', 'Puan']]
        st.dataframe(top_school, hide_index=True)
        
        if 'user' in st.session_state:
            sinif = st.session_state.user['Sınıf']
            st.markdown(f"### 🥇 {sinif} Liderleri")
            top_class = df[df['Sınıf'] == sinif].nlargest(10, 'Puan')[['Öğrencinin Adı', 'Puan']]
            st.dataframe(top_class, hide_index=True)

# --- ANA AKIŞ ---
def main():
    df = get_data()
    render_sidebar(df)

    if 'is_logged_in' not in st.session_state:
        # GİRİŞ EKRANI
        pito_gif("pito_merhaba.gif")
        st.title("Pito Python Akademi")
        st.info("Selam! Ben Pito. Nusaybin Süleyman Bölünmez Anadolu Lisesi Python yolculuğuna hazır mısın?")
        
        okul_no = st.text_input("Okul Numaranı Gir (Örn: 12)", key="login_box")
        if okul_no:
            if okul_no.isdigit():
                user_row = df[df['Okul No'] == int(okul_no)]
                if not user_row.empty:
                    user = user_row.iloc[0].to_dict()
                    # HATAYI ÖNLEYEN KRİTİK KISIM:
                    mod = int(user.get('Mevcut Modül', 1)) if pd.notna(user.get('Mevcut Modül')) else 1
                    egz = int(user.get('Mevcut Egzersiz', 1)) if pd.notna(user.get('Mevcut Egzersiz')) else 1
                    
                    st.success(f"Hoş geldin **{user['Öğrencinin Adı']}**! Şu an {mod}. Modül, {egz}. Adımdasın.")
                    col1, col2 = st.columns(2)
                    if col1.button("Evet, Benim!"):
                        st.session_state.user = user
                        st.session_state.is_logged_in = True
                        st.session_state.hata = 0
                        st.session_state.puan = 20
                        st.rerun()
                    if col2.button("Hayır, Ben Değilim"): st.rerun()
                else:
                    st.warning("Kayıt bulunamadı. Lütfen yeni kayıt oluştur!")
                    # Kayıt formu buraya gelebilir
            else: st.error("Lütfen sadece sayı gir!")
    else:
        # EĞİTİM EKRANI
        u = st.session_state.user
        # Sayısal değerleri güvenli al
        m_id = int(u.get('Mevcut Modül', 1)) if pd.notna(u.get('Mevcut Modül')) else 1
        e_id = int(u.get('Mevcut Egzersiz', 1)) if pd.notna(u.get('Mevcut Egzersiz')) else 1
        
        # İlerleme Çubuğu
        progress = ((m_id - 1) * 5 + (e_id - 1)) / 40
        st.progress(progress)
        
        col_gif, col_not = st.columns([1, 2])
        with col_gif:
            if 'success' in st.session_state: pito_gif("pito_basari.gif")
            elif st.session_state.hata > 0: pito_gif("pito_hata.gif")
            else: pito_gif("pito_dusunuyor.gif")
            
        with col_not:
            st.markdown(f'<div class="pito-box"><b>Pito\'nun Notu (Modül {m_id}):</b><br>{MUREDDTAT[m_id]["not"]}</div>', unsafe_allow_html=True)

        # Egzersiz Paneli
        egz_data = MUREDDTAT[m_id]["egz"][e_id-1]
        st.subheader(f"📍 Adım {e_id}")
        st.code(egz_data["q"], language="python")
        
        ans = st.text_input("Kodunu buraya yaz:", key=f"ans_{m_id}_{e_id}")
        
        if st.button("Kontrol Et"):
            if not ans:
                st.warning("Pito veri girmelisin diyor! 🐍")
            elif ans.strip() == egz_data["a"]:
                st.balloons()
                st.session_state.success = True
                st.success(f"Tebrikler {u['Öğrencinin Adı']}! Doğru cevap.")
                if egz_data["out"]: st.info(f"Kod Çıktısı: {egz_data['out']}")
                # G Sheets Güncelleme ve st.rerun()
            else:
                st.session_state.hata += 1
                st.session_state.puan -= 5
                st.error(f"Hata {st.session_state.hata}/4! Puanın: {st.session_state.puan}")
                if st.session_state.hata == 3: st.warning(f"💡 İpucu: {egz_data['h']}")
                if st.session_state.hata >= 4:
                    st.error(f"4 hata yaptın. Doğru çözüm: {egz_data['a']}")
                    if st.button("Devam Et"): st.rerun()

if __name__ == "__main__":
    main()
