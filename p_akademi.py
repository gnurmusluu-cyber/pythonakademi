import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
import base64

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="Pito Python Akademi", layout="wide")

# --- CSS: PİTO TASARIMI ---
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stButton>button { border-radius: 12px; height: 3em; font-weight: bold; }
    .pito-box { background-color: #ffffff; padding: 25px; border-radius: 20px; border-left: 8px solid #FF4B4B; box-shadow: 2px 2px 15px rgba(0,0,0,0.1); }
    .stTextInput>div>div>input { border: 2px solid #FF4B4B !important; }
    </style>
    """, unsafe_allow_html=True)

# --- GIF YÖNETİMİ ---
def render_pito_gif(gif_name):
    try:
        file_ = open(f"assets/{gif_name}", "rb")
        contents = file_.read()
        data_url = base64.b64encode(contents).decode("utf-8")
        file_.close()
        st.markdown(f'<div style="text-align:center;"><img src="data:image/gif;base64,{data_url}" width="200"></div>', unsafe_allow_html=True)
    except:
        st.info(f"🐍 Pito ({gif_name})")

# --- MÜFREDAT VERİSİ (8 Modül / 40 Egzersiz) ---
MUREDDTAT = {
    1: {
        "baslik": "Python'ın Sesi: print()",
        "not": "Python dünyasına hoş geldin! Bilgisayara bir şeyler söyletmek için 'print' fonksiyonunu kullanırız. Metinleri tırnak (' ') içinde yazmalısın.",
        "egz": [
            {"q": "Ekrana Merhaba yazdır: ____(\"Merhaba\")", "a": "print", "h": "Pito'nun konuşma komutunu hatırla!", "out": "Merhaba"},
            {"q": "Tırnağı tamamla: print(__Selam\")", "a": "\"", "h": "Metinler neyin içinde olmalıydı?", "out": "Selam"},
            {"q": "Parantezi kapat: print(\"Nusaybin\"__", "a": ")", "h": "Fonksiyonlar parantezle açılır ve kapanır.", "out": "Nusaybin"},
            {"q": "Tek tırnak kullan: print(__Selam')", "a": "'", "h": "Çift tırnak yerine tek tırnak da olur.", "out": "Selam"},
            {"q": "Komutu yaz: ____(\"Pito\")", "a": "print", "h": "Ekrana çıktı komutu.", "out": "Pito"}
        ]
    },
    2: {
        "baslik": "Hafıza Kutuları: Değişkenler",
        "not": "Değişkenler, verileri sakladığımız kutulardır. 'ad = \"Pito\"' yazdığımızda 'ad' isimli kutuya 'Pito' değerini koyarız.",
        "egz": [
            {"q": "Değişken tanımla: x __ 10", "a": "=", "h": "Atama yapmak için hangi işaret kullanılır?", "out": ""},
            {"q": "Kutuyu isimlendir: ____ = \"Python\"", "a": "dil", "h": "Herhangi bir isim yazabilirsin (Örn: dil).", "out": ""},
            {"q": "Değişkeni yazdır: print(__)", "a": "x", "h": "Tırnak kullanma!", "out": "10"},
            {"q": "Sayıyı sakla: yas = __", "a": "15", "h": "Herhangi bir sayı gir.", "out": ""},
            {"q": "Boşluğu doldur: a=5, b=a, print(__)", "a": "b", "h": "b'nin içindeki değeri görmek istiyoruz.", "out": "5"}
        ]
    },
    3: {
        "baslik": "Veri Tiplerinin Gizemi",
        "not": "Python'da sayılar (int), metinler (str) ve ondalıklı sayılar (float) vardır. Bir tipi diğerine dönüştürebiliriz.",
        "egz": [
            {"q": "Tam sayıya dönüştür: ____(\"5\")", "a": "int", "h": "Integer'ın kısaltması.", "out": "5"},
            {"q": "Metne dönüştür: ____(10)", "a": "str", "h": "String'in kısaltması.", "out": "'10'"},
            {"q": "Tipi kontrol et: ____(5.5)", "a": "type", "h": "Nesnenin tipini ne söyler?", "out": "<class 'float'>"},
            {"q": "Float tanımla: pi = 3.__", "a": "14", "h": "Ondalıklı kısım.", "out": ""},
            {"q": "Hangi tip: type(\"A\") = ____", "a": "str", "h": "Tırnak içindeki veri tipi.", "out": ""}
        ]
    },
    4: {
        "baslik": "Matematiksel Dans",
        "not": "Python bir hesap makinesidir! +, -, *, / dışında % (kalan) ve ** (üs alma) operatörlerini de kullanırız.",
        "egz": [
            {"q": "Kalanı bul (10 % 3): ____", "a": "1", "h": "10'un 3'e bölümünden kalan kaçtır?", "out": "1"},
            {"q": "Üs al (5'in karesi): 5 __ 2", "a": "**", "h": "Çarpma işaretini iki kere kullan.", "out": "25"},
            {"q": "Tam bölme (7 // 2): ____", "a": "3", "h": "7'de 2 kaç kere tam var?", "out": "3"},
            {"q": "Topla: 10 __ 5 = 15", "a": "+", "h": "Artı işareti.", "out": "15"},
            {"q": "Çarp: 4 __ 2 = 8", "a": "*", "h": "Yıldız işareti.", "out": "8"}
        ]
    },
    5: {
        "baslik": "Kullanıcı ile Sohbet: input()",
        "not": "input() ile kullanıcıdan veri alırız. Unutma, input() her zaman bir metin (str) döndürür!",
        "egz": [
            {"q": "Veri al: ad = ____(\"Adın?\")", "a": "input", "h": "Giriş alma komutu.", "out": ""},
            {"q": "Sayısal girdi: yas = ____(input())", "a": "int", "h": "Girdiyi sayıya dönüştür.", "out": ""},
            {"q": "Yazdır: print(f\"Merhaba {____}\")", "a": "ad", "h": "Değişken adını yaz.", "out": "Merhaba ..."},
            {"q": "Mesaj ekle: input(\"____\")", "a": "Sayı gir", "h": "Herhangi bir mesaj yaz.", "out": ""},
            {"q": "Tamamla: ____ = input()", "a": "sehir", "h": "Bir değişken ismi seç.", "out": ""}
        ]
    },
    6: {
        "baslik": "Karar Anı: If-Else",
        "not": "Koşullara göre farklı yollar seçeriz. 'if' doğruysa çalışır, değilse 'else' kısmına bakar.",
        "egz": [
            {"q": "Eşit mi kontrolü: if x ____ 5:", "a": "==", "h": "Karşılaştırma için çift eşittir.", "out": ""},
            {"q": "Değilse: ____:", "a": "else", "h": "Koşul sağlanmazsa ne olur?", "out": ""},
            {"q": "İki nokta ekle: if x > 0__", "a": ":", "h": "Satır sonu işareti.", "out": ""},
            {"q": "Büyükse: if yas ____ 18:", "a": ">", "h": "Büyüktür işareti.", "out": ""},
            {"q": "Aksi halde (else if): ____ x < 10:", "a": "elif", "h": "Diğer koşul kısaltması.", "out": ""}
        ]
    },
    7: {
        "baslik": "Döngü Zamanı: For ve While",
        "not": "Tekrar eden işler için döngü kullanırız. 'range(5)' ile 0'dan 4'e kadar sayabiliriz.",
        "egz": [
            {"q": "Döngüyü başlat: ____ i in range(5):", "a": "for", "h": "Tekrarlama komutu.", "out": "0 1 2 3 4"},
            {"q": "Sınırı belirle: range(____)", "a": "10", "h": "Kaça kadar gitsin?", "out": ""},
            {"q": "Şartlı döngü: ____ x < 5:", "a": "while", "h": "Olduğu sürece çalış.", "out": ""},
            {"q": "Durdur: if x==5: ____", "a": "break", "h": "Döngüyü kırma komutu.", "out": ""},
            {"q": "Devam et: ____", "a": "continue", "h": "Sıradakine geç komutu.", "out": ""}
        ]
    },
    8: {
        "baslik": "Takım Çantası: Listeler",
        "not": "Listeler birçok veriyi tek bir kutuda tutar. Elemanlara 0'dan başlayarak ulaşırız.",
        "egz": [
            {"q": "Liste oluştur: meyve = [__]", "a": "\"elma\"", "h": "Tırnak içinde bir meyve yaz.", "out": ""},
            {"q": "Eleman ekle: meyve.____(\"muz\")", "a": "append", "h": "Sona ekleme metodu.", "out": ""},
            {"q": "İlk eleman: print(meyve[____])", "a": "0", "h": "Python saymaya kaçtan başlar?", "out": ""},
            {"q": "Sil: meyve.____(\"elma\")", "a": "remove", "h": "Çıkarma metodu.", "out": ""},
            {"q": "Uzunluk: ____(meyve)", "a": "len", "h": "Length (Uzunluk) kısaltması.", "out": ""}
        ]
    }
}

# --- RÜTBELER VE LİDERLİK ---
RUTBELER = ["🥚 Yeni Başlayan", "🌱 Python Çırağı", "🪵 Kod Oduncusu", "🧱 Mantık Mimarı", 
            "🌀 Döngü Ustası", "📋 Liste Uzmanı", "📦 Fonksiyon Kaptanı", "🤖 OOP Robotu", "🏆 Python Kahramanı"]

# --- VERİTABANI VE STATE ---
conn = st.connection("gsheets", type=GSheetsConnection)

def verileri_al():
    return conn.read(spreadsheet="https://docs.google.com/spreadsheets/d/1lat8rO2qm9QnzEUYlzC_fypG3cRkGlJfSfTtwNvs318/edit?gid=0#gid=0")

def sidebar_render(df):
    with st.sidebar:
        st.title("🏆 Şampiyonlar")
        st.subheader("🏫 Okul Top 10")
        st.table(df.nlargest(10, 'Puan')[['Öğrencinin Adı', 'Puan', 'Rütbe']])
        if 'user' in st.session_state:
            sinif = st.session_state.user['Sınıf']
            st.subheader(f"🥇 {sinif} Liderleri")
            st.table(df[df['Sınıf'] == sinif].nlargest(10, 'Puan')[['Öğrencinin Adı', 'Puan']])

# --- ANA PROGRAM ---
def main():
    df = verileri_al()
    sidebar_render(df)

    if 'is_logged_in' not in st.session_state:
        # GİRİŞ EKRANI
        render_pito_gif("pito_merhaba.gif")
        st.title("Pito Python Akademi")
        st.write("Nusaybin Süleyman Bölünmez Anadolu Lisesi'ne hoş geldin!")
        
        okul_no = st.text_input("Okul Numaranı Gir:", key="login_input")
        if okul_no:
            if not okul_no.isdigit():
                st.error("Sadece sayı girmelisin!")
            else:
                user_row = df[df['Okul No'] == int(okul_no)]
                if not user_row.empty:
                    user = user_row.iloc[0].to_dict()
                    st.success(f"Hoş geldin {user['Öğrencinin Adı']}!")
                    col1, col2 = st.columns(2)
                    if col1.button("✅ Evet, Benim! Devam"):
                        st.session_state.is_logged_in = True
                        st.session_state.user = user
                        st.session_state.hata = 0
                        st.session_state.temp_puan = 20
                        st.rerun()
                    if col2.button("❌ Ben Değilim"):
                        st.rerun()
                else:
                    st.warning("Kayıt bulunamadı. Yeni profil oluştur!")
                    with st.form("kayit"):
                        ad = st.text_input("Ad Soyad")
                        sinif = st.selectbox("Sınıf", ["9-A", "9-B", "10-A", "10-B"])
                        if st.form_submit_button("Kayıt Ol"):
                            # GSheets append logic buraya gelecek
                            st.rerun()
    else:
        # EĞİTİM EKRANI
        u = st.session_state.user
        mod_id = int(u['Mevcut Modül'])
        egz_id = int(u['Mevcut Egzersiz'])
        
        # İlerleme Çubuğu
        progress = ((mod_id - 1) * 5 + (egz_id - 1)) / 40
        st.progress(progress)
        
        # Pito ve Notu
        col_img, col_txt = st.columns([1, 2])
        with col_img:
            render_pito_gif("pito_dusunuyor.gif")
        with col_txt:
            st.markdown(f"""<div class="pito-box">
                <b>Pito'nun Notu (Modül {mod_id}):</b><br>{MUREDDTAT[mod_id]['not']}
            </div>""", unsafe_allow_html=True)

        # Egzersiz
        egz = MUREDDTAT[mod_id]['egz'][egz_id-1]
        st.subheader(f"📝 Adım {egz_id}")
        st.code(egz['q'], language="python")
        
        user_ans = st.text_input("Boşluğu Doldur:", key=f"ans_{mod_id}_{egz_id}")
        
        if st.button("Kontrol Et"):
            if not user_ans:
                st.warning("Pito veri bekliyor, boş bırakma!")
            elif user_ans.strip() == egz['a']:
                st.session_state.hata = 0
                st.balloons()
                render_pito_gif("pito_basari.gif")
                st.success("Tebrikler! Doğru cevap.")
                if egz['out']: st.info(f"Kod Çıktısı: {egz['out']}")
                # İlerleme ve Veritabanı Update (conn.update)
            else:
                st.session_state.hata += 1
                st.session_state.temp_puan -= 5
                render_pito_gif("pito_hata.gif")
                st.error(f"{st.session_state.hata}. hatan! 5 puan düştü. Puan: {st.session_state.temp_puan}")
                
                if st.session_state.hata == 3:
                    st.warning(f"💡 İpucu: {egz['h']}")
                if st.session_state.hata >= 4:
                    st.error("4 hata yaptın, puan alamadın. Çözüm aşağıda.")
                    st.info(f"Çözüm: {egz['a']}")

if __name__ == "__main__":
    main()
