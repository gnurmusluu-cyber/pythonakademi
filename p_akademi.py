import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
import base64

# --- GENEL AYARLAR ---
st.set_page_config(page_title="Pito Python Akademi", layout="wide")
SHEET_URL = "https://docs.google.com/spreadsheets/d/1lat8rO2qm9QnzEUYlzC_fypG3cRkGlJfSfTtwNvs318/edit?gid=0#gid=0"

# --- TASARIM (CSS) ---
st.markdown("""
    <style>
    .stButton>button { border-radius: 20px; height: 3.5em; font-weight: bold; background-color: #FF4B4B; color: white; border: none; }
    .stTextInput>div>div>input { border: 3px solid #FF4B4B !important; border-radius: 10px; font-size: 18px; }
    .pito-box { background-color: #ffffff; padding: 25px; border-radius: 20px; border-left: 10px solid #FF4B4B; box-shadow: 2px 2px 10px rgba(0,0,0,0.1); }
    </style>
    """, unsafe_allow_html=True)

# --- GIF YÜKLEME ---
def pito_render(gif_name):
    try:
        file_ = open(f"assets/{gif_name}", "rb")
        contents = file_.read()
        data_url = base64.b64encode(contents).decode("utf-8")
        file_.close()
        st.markdown(f'<div style="text-align:center;"><img src="data:image/gif;base64,{data_url}" width="220"></div>', unsafe_allow_html=True)
    except:
        st.info(f"🐍 Pito Görseli: {gif_name}")

# --- MÜFREDAT SÖZLÜĞÜ (8 MODÜL x 5 EGZERSİZ) ---
ACADEMY_DATA = {
    1: {"baslik": "Python'ın Sesi", "konu": "Python dünyasına hoş geldin! Bilgisayara bir şeyler söyletmek için 'print' fonksiyonunu kullanırız. Metinleri tırnak (' ') içinde yazmalısın.", 
        "egz": [
            {"q": "Ekrana Merhaba yazdır: ____(\"Merhaba\")", "a": "print", "h": "Konuşma komutu!", "out": "Merhaba"},
            {"q": "Tırnağı tamamla: print(__Selam\")", "a": "\"", "h": "Metinler neyin içine yazılır?", "out": "Selam"},
            {"q": "Parantezi kapat: print(\"Kod\"__", "a": ")", "h": "Fonksiyonlar parantezle biter.", "out": "Kod"},
            {"q": "Sayı yazdır: print(__10__)", "a": "10", "h": "Sayılar tırnaksız da yazılabilir.", "out": "10"},
            {"q": "Ekrana çıktı: ____(\"Pito\")", "a": "print", "h": "Yazdır komutu.", "out": "Pito"}]},
    2: {"baslik": "Hafıza Kutuları", "konu": "Değişkenler verileri saklar. 'ad = \"Pito\"' gibi. '=' işareti ile atama yaparız.", 
        "egz": [
            {"q": "Değişken tanımla: x __ 5", "a": "=", "h": "Eşittir işaretini kullan.", "out": ""},
            {"q": "İsimlendir: ____ = \"Mardin\"", "a": "sehir", "h": "Bir değişken ismi ver (örn: sehir).", "out": ""},
            {"q": "Yazdır: print(__)", "a": "x", "h": "Değişkeni tırnaksız çağır.", "out": "5"},
            {"q": "Yeni değer: puan = __", "a": "100", "h": "Bir sayı gir.", "out": ""},
            {"q": "Birleştir: a=2, b=a, print(__)", "a": "b", "h": "b değişkenini yazdır.", "out": "2"}]},
    3: {"baslik": "Veri Tipleri", "konu": "Sayılar (int), metinler (str) ve ondalıklılar (float) vardır. type() ile tipi kontrol ederiz.", 
        "egz": [
            {"q": "Tam sayı yap: ____(\"5\")", "a": "int", "h": "Integer kısaltması.", "out": "5"},
            {"q": "Metin yap: ____(10)", "a": "str", "h": "String kısaltması.", "out": "'10'"},
            {"q": "Tipi öğren: ____(3.14)", "a": "type", "h": "Tip kontrol komutu.", "out": "<class 'float'>"},
            {"q": "Ondalıklı: pi = 3.__", "a": "14", "h": "Virgül yerine nokta!", "out": ""},
            {"q": "Tırnaklı tip: type(\"A\") = ____", "a": "str", "h": "Metin tipinin adı.", "out": ""}]},
    4: {"baslik": "Matematiksel Güç", "konu": "Python bir hesap makinesidir! +, -, *, / dışında % kalan, ** üs alma demektir.", 
        "egz": [
            {"q": "Kalanı bul: 10 __ 3 = 1", "a": "%", "h": "Modül (kalan) operatörü.", "out": "1"},
            {"q": "Üs al: 2 __ 3 = 8", "a": "**", "h": "İki tane yıldız.", "out": "8"},
            {"q": "Tam bölme: 7 ____ 2 = 3", "a": "//", "h": "Çift bölü işareti.", "out": "3"},
            {"q": "Topla: 5 __ 5 = 10", "a": "+", "h": "Artı işareti.", "out": "10"},
            {"q": "Çarp: 4 __ 2 = 8", "a": "*", "h": "Yıldız işareti.", "out": "8"}]},
    5: {"baslik": "input() Sohbetleri", "konu": "input() ile kullanıcıdan veri alırız. Gelen veri her zaman metindir (str).", 
        "egz": [
            {"q": "Veri iste: ad = ____(\"Adın?\")", "a": "input", "h": "Giriş komutu.", "out": ""},
            {"q": "Sayıya çevir: yas = int(____())", "a": "input", "h": "Kullanıcıdan alıyoruz.", "out": ""},
            {"q": "Selamla: print(f\"Selam {____}\")", "a": "ad", "h": "Değişkeni süslü paranteze koy.", "out": ""},
            {"q": "Metin girişi: x = input(\"____ gir:\")", "a": "Sayı", "h": "Bir kelime yaz.", "out": ""},
            {"q": "Değişken: ____ = input()", "a": "yanit", "h": "Bir isim seç.", "out": ""}]},
    6: {"baslik": "Yol Ayrımı: if-else", "konu": "Şartlar sağlandığında 'if', sağlanmadığında 'else' çalışır. Blok sonuna ':' eklenir.", 
        "egz": [
            {"q": "Eşit mi: if x ____ 5:", "a": "==", "h": "Çift eşittir kullan.", "out": ""},
            {"q": "Aksi halde: ____:", "a": "else", "h": "Şart dışı durum.", "out": ""},
            {"q": "Noktala: if x > 0__", "a": ":", "h": "Satır sonu işareti.", "out": ""},
            {"q": "Küçük mü: if a ____ b:", "a": "<", "h": "Küçüktür işareti.", "out": ""},
            {"q": "Veya: ____ puan > 50:", "a": "elif", "h": "Else-if kısaltması.", "out": ""}]},
    7: {"baslik": "Döngüler", "konu": "Tekrar eden işler için döngü kullanırız. range(5) ile 0'dan 4'e kadar sayarız.", 
        "egz": [
            {"q": "Döngü kur: ____ i in range(3):", "a": "for", "h": "Tekrarlama komutu.", "out": "0 1 2"},
            {"q": "Sayı aralığı: range(____)", "a": "5", "h": "5 kere dönsün.", "out": ""},
            {"q": "Şartlı döngü: ____ x < 10:", "a": "while", "h": "Olduğu sürece...", "out": ""},
            {"q": "Durdur: if x == 5: ____", "a": "break", "h": "Kırma komutu.", "out": ""},
            {"q": "Sıralama: for x in [1, 2__ 3]:", "a": ",", "h": "Virgül ile ayır.", "out": ""}]},
    8: {"baslik": "Listeler", "konu": "Listeler birden fazla veriyi [ ] içinde tutar. Saymaya her zaman 0'dan başlanır.", 
        "egz": [
            {"q": "Liste yap: meyveler = [____]", "a": "\"elma\"", "h": "Tırnaklı bir veri yaz.", "out": ""},
            {"q": "Sona ekle: meyveler.____(\"muz\")", "a": "append", "h": "Ekleme metodu.", "out": ""},
            {"q": "İlk eleman: print(liste[____])", "a": "0", "h": "Başlangıç indeksi.", "out": ""},
            {"q": "Sil: liste.____(\"elma\")", "a": "remove", "h": "Kaldırma komutu.", "out": ""},
            {"q": "Boyut: ____(liste)", "a": "len", "h": "Uzunluk ölçer.", "out": ""}]}
}

RUTBELER = ["🥚 Yeni Başlayan", "🌱 Python Çırağı", "🪵 Kod Oduncusu", "🧱 Mantık Mimarı", "🌀 Döngü Ustası", "📋 Liste Uzmanı", "📦 Fonksiyon Kaptanı", "🤖 OOP Robotu", "🏆 Python Kahramanı"]

# --- VERİ BAĞLANTISI ---
conn = st.connection("gsheets", type=GSheetsConnection)

def get_data():
    return conn.read(spreadsheet=SHEET_URL)

def update_user(df, user_no, mod, egz, puan):
    # Bu kısım Sheet update yetkisi gerektirir
    st.toast(f"Puanın kaydedildi: {puan}!", icon="🎯")

# --- LİDERLİK TABLOSU ---
def show_leaderboard(df):
    with st.sidebar:
        st.header("🏆 Şampiyonlar")
        st.subheader("🏫 Okul Top 10")
        st.dataframe(df.nlargest(10, 'Puan')[['Öğrencinin Adı', 'Rütbe', 'Puan']], hide_index=True)
        if 'user' in st.session_state:
            sinif = st.session_state.user['Sınıf']
            st.subheader(f"🥇 {sinif} Liderleri")
            st.dataframe(df[df['Sınıf'] == sinif].nlargest(10, 'Puan')[['Öğrencinin Adı', 'Puan']], hide_index=True)

# --- ANA PROGRAM ---
def main():
    df = get_data()
    show_leaderboard(df)

    if 'is_logged_in' not in st.session_state:
        # GİRİŞ EKRANI
        pito_render("pito_merhaba.gif")
        st.title("Pito Python Akademi")
        st.info("Selam! Ben Pito. Nusaybin Süleyman Bölünmez Anadolu Lisesi için hazır mısın?")
        
        okul_no = st.text_input("Okul Numaranı Gir:", key="login_box")
        if okul_no:
            if okul_no.isdigit():
                user_row = df[df['Okul No'] == int(okul_no)]
                if not user_row.empty:
                    user = user_row.iloc[0].to_dict()
                    # HATA GİDERME: Boş değerleri 1'e sabitle
                    m = int(user.get('Mevcut Modül', 1)) if pd.notna(user.get('Mevcut Modül')) else 1
                    e = int(user.get('Mevcut Egzersiz', 1)) if pd.notna(user.get('Mevcut Egzersiz')) else 1
                    
                    st.success(f"Hoş geldin **{user['Öğrencinin Adı']}**! {m}. Modül, {e}. Adımdasın.")
                    col1, col2 = st.columns(2)
                    if col1.button("✅ Evet, Benim!"):
                        st.session_state.user = user
                        st.session_state.is_logged_in = True
                        st.session_state.hata = 0
                        st.session_state.kazanc = 20
                        st.rerun()
                    if col2.button("❌ Hayır, Değilim"): st.rerun()
                else:
                    st.warning("Numaran kayıtlı değil! Kayıt için öğretmenine danış.")
            else: st.error("Lütfen sadece sayı gir!")
    else:
        # EĞİTİM EKRANI
        u = st.session_state.user
        m_id = int(u.get('Mevcut Modül', 1)) if pd.notna(u.get('Mevcut Modül')) else 1
        e_id = int(u.get('Mevcut Egzersiz', 1)) if pd.notna(u.get('Mevcut Egzersiz')) else 1
        
        # İlerleme Çubuğu
        progress = ((m_id - 1) * 5 + (e_id - 1)) / 40
        st.progress(progress)
        
        col_img, col_note = st.columns([1, 2])
        with col_img:
            if 'success' in st.session_state: pito_render("pito_basari.gif")
            elif st.session_state.hata > 0: pito_render("pito_hata.gif")
            else: pito_render("pito_dusunuyor.gif")
            
        with col_note:
            st.markdown(f'<div class="pito-box"><b>Pito\'nun Notu (Modül {m_id}):</b><br>{ACADEMY_DATA[m_id]["konu"]}</div>', unsafe_allow_html=True)

        # Egzersiz Paneli
        egz = ACADEMY_DATA[m_id]["egz"][e_id-1]
        st.subheader(f"📍 Adım {e_id}")
        st.code(egz["q"], language="python")
        
        user_ans = st.text_input("Kodunu buraya yaz:", key=f"ans_{m_id}_{e_id}")
        
        if st.button("Kontrol Et"):
            if not user_ans:
                st.warning("Pito veri girmelisin diyor! 🐍")
            elif user_ans.strip() == egz["a"]:
                st.balloons()
                st.session_state.success = True
                st.success(f"Harika! Doğru cevap.")
                if egz["out"]: st.info(f"Kod Çıktısı: {egz['out']}")
                # Burada veritabanı güncelleme çağrılabilir
            else:
                st.session_state.hata += 1
                st.session_state.kazanc -= 5
                st.error(f"{st.session_state.hata}. hata! Puanın: {st.session_state.kazanc}")
                if st.session_state.hata == 3: st.warning(f"💡 İpucu: {egz['h']}")
                if st.session_state.hata >= 4:
                    st.error(f"Üzgünüm, 4 hata oldu. Doğru cevap: {egz['a']}")
                    if st.button("Sıradakine Geç"): st.rerun()

if __name__ == "__main__":
    main()
