import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
import time

# --- KONFİGÜRASYON ---
st.set_page_config(page_title="Pito Python Akademi", page_icon="🤖", layout="wide")

# --- CSS TASARIMI ---
st.markdown("""
    <style>
    .main { background-color: #f4f7f6; }
    .stButton>button { border-radius: 20px; font-weight: bold; background-color: #4CAF50; color: white; transition: 0.3s; }
    .stButton>button:hover { background-color: #45a049; transform: scale(1.05); }
    .pito-notu-box { background-color: #ffffff; padding: 20px; border-radius: 15px; border-left: 10px solid #2ecc71; box-shadow: 2px 2px 15px rgba(0,0,0,0.1); margin-bottom: 20px; }
    .pito-sozluk { background-color: #fff3e0; padding: 10px; border-radius: 8px; border: 1px dashed #ff9800; font-size: 0.9em; margin-top: 10px; }
    .input-vurgu { border: 2px solid #e74c3c !important; }
    </style>
""", unsafe_allow_html=True)

# --- VERİ BAĞLANTISI ---
# URL: https://docs.google.com/spreadsheets/d/1lat8rO2qm9QnzEUYlzC_fypG3cRkGlJfSfTtwNvs318/edit#gid=0
conn = st.connection("gsheets", type=GSheetsConnection)

RUTBELER = ["🥚 Yeni Başlayan", "🌱 Python Çırağı", "🪵 Kod Oduncusu", "🧱 Mantık Mimarı", 
            "🌀 Döngü Ustası", "📋 Liste Uzmanı", "📦 Fonksiyon Kaptanı", "🤖 OOP Robotu", "🏆 Python Kahramanı"]

# --- 8 MODÜL VE 40 EGZERSİZLİK TAM MÜFREDAT ---
# Not: Her modül Python ile Programlamanın Temelleri ünitesinden (Bölüm 2) beslenmiştir[cite: 4, 5].
MÜFREDAT = {
    1: {
        "baslik": "Python'a Merhaba",
        "egzersizler": {
            1: {"soru": "Ekrana 'Merhaba Pito' yazdır.", "cevap": "print('Merhaba Pito')", "not": "Python'da dış dünyaya veri göndermek için **print()** fonksiyonunu kullanırız.", "sozluk": "**Fonksiyon:** Belirli bir görevi yapan komut grubu.", "ipucu": "Parantez ve tırnakları unutma!"},
            2: {"soru": "Bir satırda 10, alt satırda 20 yazdır.", "cevap": "print(10)\nprint(20)", "not": "Her print komutu yeni bir satır başlatır.", "sozluk": "**Integer:** Tam sayı veri tipi.", "ipucu": "İki ayrı print kullan."},
            3: {"soru": "30 ve 40 sayılarını tek print içinde virgülle ayırarak yazdır.", "cevap": "print(30, 40)", "not": "Virgül, ekrana yazarken araya boşluk bırakır.", "sozluk": "**Argüman:** Fonksiyona gönderilen veri.", "ipucu": "print(x, y) yapısını kullan."},
            4: {"soru": "Adını kullanıcıdan alıp 'ad' değişkenine ata.", "cevap": "ad = input()", "not": "Kullanıcıdan bilgi almak için **input()** kullanılır.", "sozluk": "**Değişken:** Veri saklayan isimlendirilmiş hafıza alanı.", "ipucu": "ad = ... şeklinde başla.", "input": True},
            5: {"soru": "Ekrana 'Python Öğreniyorum' yazdır.", "cevap": "print('Python Öğreniyorum')", "not": "Metinler (String) mutlaka tırnak içinde olmalı.", "sozluk": "**String:** Metinsel veri dizisi.", "ipucu": "Tırnaklara dikkat!"}
        }
    },
    2: {
        "baslik": "Değişkenlerin Gücü",
        "egzersizler": {
            1: {"soru": "x değişkenine 5, y değişkenine 10 ata.", "cevap": "x = 5\ny = 10", "not": "Atama operatörü '=' sembolüdür.", "sozluk": "**Operatör:** İşlem yapmamızı sağlayan simge.", "ipucu": "Her atama yeni satırda olsun."},
            2: {"soru": "x ve y'nin toplamını ekrana yazdır.", "cevap": "print(x + y)", "not": "Değişken adları tırnak içine alınmaz.", "sozluk": "**İfade (Expression):** Bir değer üreten kod parçası.", "ipucu": "Tırnak kullanma!"},
            3: {"soru": "Kullanıcıdan yaşını alıp tam sayıya çevir.", "cevap": "yas = int(input())", "not": "input() her şeyi metin alır, sayı için **int()** lazımdır.", "sozluk": "**Tip Dönüşümü:** Verinin türünü değiştirme.", "ipucu": "int(input()) yapısını dene.", "input": True},
            4: {"soru": "İsim ve soyisim değişkenlerini birleştir.", "cevap": "print(isim + soyisim)", "not": "Artı (+) metinleri yan yana yapıştırır.", "sozluk": "**Birleştirme (Concatenation):** Stringleri ekleme.", "ipucu": "+ kullan."},
            5: {"soru": "Pi sayısını 3.14 olarak ata.", "cevap": "pi = 3.14", "not": "Ondalıklı sayılar 'float' olarak adlandırılır.", "sozluk": "**Float:** Ondalıklı sayı tipi.", "ipucu": "Nokta kullanmalısın."}
        }
    },
    3: {
        "baslik": "Matematiksel İşlemler",
        "egzersizler": {
            1: {"soru": "10'un 3'e bölümünden kalanı bul.", "cevap": "print(10 % 3)", "not": "Mod operatörü (%) kalanı verir.", "sozluk": "**Modülo:** Kalanı bulma operatörü.", "ipucu": "% sembolünü kullan."},
            2: {"soru": "2'nin 5. kuvvetini hesapla.", "cevap": "print(2 ** 5)", "not": "Üs almak için iki yıldız (**) kullanılır.", "sozluk": "**Üs:** Bir sayının kuvveti.", "ipucu": "** kullan."},
            3: {"soru": "7'yi 2'ye tam böl (ondalıksız).", "cevap": "print(7 // 2)", "not": "Taban bölme (//) tam kısmı verir.", "sozluk": "**Integer Division:** Ondalıksız bölme.", "ipucu": "// kullan."},
            4: {"soru": "Sayi değişkenini 1 artır.", "cevap": "sayi += 1", "not": "Artırma operatörü += kısayoldur.", "sozluk": "**Artırma (Increment):** Değeri yükseltme.", "ipucu": "+= kullan."},
            5: {"soru": "(5+5)*2 işlemini yap.", "cevap": "print((5 + 5) * 2)", "not": "İşlem önceliği için parantez şarttır.", "sozluk": "**Öncelik:** İşlem sırası.", "ipucu": "Parantez kullan."}
        }
    },
    4: {
        "baslik": "Karar Mekanizmaları",
        "egzersizler": {
            1: {"soru": "x, 10'dan büyükse 'Büyük' yazdır.", "cevap": "if x > 10:\n    print('Büyük')", "not": "Koşul sonuna iki nokta (:) konur.", "sozluk": "**Blok:** Girintili kod alanı.", "ipucu": "Girintiye (Tab) dikkat!"},
            2: {"soru": "Hava yağmurluysa 'Şemsiye al' değilse 'Güneş gözlüğü al' yaz.", "cevap": "if hava == 'yagmurlu':\n    print('Şemsiye al')\nelse:\n    print('Güneş gözlüğü al')", "not": "Aksi durumlar için **else** kullanılır.", "sozluk": "**Dallanma:** Kodun farklı yollara ayrılması.", "ipucu": "else'den sonra : unutma."},
            3: {"soru": "Not 85'ten büyükse 'A', 70'ten büyükse 'B' yazdır.", "cevap": "if not > 85:\n    print('A')\nelif not > 70:\n    print('B')", "not": "Birden fazla koşul için **elif** kullanılır.", "sozluk": "**Else If:** Alternatif koşul.", "ipucu": "elif kullan."},
            4: {"soru": "x ve y eşit mi kontrol et.", "cevap": "if x == y:", "not": "Eşitlik kontrolü çift eşittir (==) ile yapılır.", "sozluk": "**Karşılaştırma:** Değerleri kıyaslama.", "ipucu": "== kullan."},
            5: {"soru": "Yaş 18'den büyük VE ehliyet varsa 'Geç' yaz.", "cevap": "if yas > 18 and ehliyet == True:\n    print('Geç')", "not": "İki koşulun da doğruluğu için **and** kullanılır.", "sozluk": "**Mantıksal Operatör:** Koşulları bağlama.", "ipucu": "and kullan."}
        }
    },
    5: {
        "baslik": "Listelerle Düzen",
        "egzersizler": {
            1: {"soru": "1, 2, 3 sayılarından oluşan bir liste yap.", "cevap": "liste = [1, 2, 3]", "not": "Listeler köşeli parantez [] ile tanımlanır.", "sozluk": "**Liste (List):** Sıralı veri topluluğu.", "ipucu": "[] kullan."},
            2: {"soru": "Listenin ilk elemanına ulaş.", "cevap": "print(liste[0])", "not": "Saymaya her zaman 0'dan başlarız.", "sozluk": "**İndis (Index):** Elemanın konum numarası.", "ipucu": "[0] kullan."},
            3: {"soru": "Listeye 'elma' elemanını ekle.", "cevap": "liste.append('elma')", "not": "Sona eleman eklemek için **append()** metodu kullanılır.", "sozluk": "**Metot:** Bir nesneye ait özel fonksiyon.", "ipucu": ".append() yaz."},
            4: {"soru": "Listenin uzunluğunu bul.", "cevap": "print(len(liste))", "not": "Eleman sayısını **len()** verir.", "sozluk": "**Length:** Uzunluk.", "ipucu": "len() kullan."},
            5: {"soru": "Listenin son elemanını sil.", "cevap": "liste.pop()", "not": "Son elemanı atmak için **pop()** kullanılır.", "sozluk": "**Silme:** Veriyi listeden çıkarma.", "ipucu": ".pop() kullan."}
        }
    },
    6: {
        "baslik": "Döngülerin Sihri",
        "egzersizler": {
            1: {"soru": "1'den 5'e kadar (5 hariç) saydır.", "cevap": "for i in range(1, 5):\n    print(i)", "not": "**range()** sayı dizisi oluşturur.", "sozluk": "**Iterasyon:** Tekrarlı işlem.", "ipucu": "for ve range kullan."},
            2: {"soru": "'Merhaba' kelimesini 3 kez yazdır.", "cevap": "for i in range(3):\n    print('Merhaba')", "not": "Tekrar sayısı için range idealdir.", "sozluk": "**Döngü (Loop):** Tekrarlanan yapı.", "ipucu": "range(3) kullan."},
            3: {"soru": "Listenin tüm elemanlarını yazdır.", "cevap": "for eleman in liste:\n    print(eleman)", "not": "Listenin içinde gezmek Python'da çok kolaydır.", "sozluk": "**Traversal:** Üzerinde gezinme.", "ipucu": "for ... in ..."},
            4: {"soru": "Sonsuz döngü başlat (while True).", "cevap": "while True:\n    print('Hi')", "not": "Koşul doğru olduğu sürece çalışan döngüdür.", "sozluk": "**While:** 'İken' anlamına gelen döngü.", "ipucu": "while True:"},
            5: {"soru": "Döngüyü zorla durdur.", "cevap": "break", "not": "**break** komutu döngüyü anında bitirir.", "sozluk": "**Break:** Kırma/Durdurma komutu.", "ipucu": "break yaz."}
        }
    },
    7: {
        "baslik": "Fonksiyon Kaptanlığı",
        "egzersizler": {
            1: {"soru": "'selam' adında bir fonksiyon tanımla.", "cevap": "def selam():\n    print('Merhaba')", "not": "**def** anahtar kelimesiyle tanımlanır.", "sozluk": "**Tanımlama:** Fonksiyonu oluşturma.", "ipucu": "def selam():"},
            2: {"soru": "Parametre alan bir toplama fonksiyonu yap.", "cevap": "def topla(a, b):\n    print(a + b)", "not": "Parantez içi veriye parametre denir.", "sozluk": "**Parametre:** Fonksiyona giren değişken.", "ipucu": "topla(a, b):"},
            3: {"soru": "Bir değer döndüren fonksiyon yaz.", "cevap": "def dondur():\n    return 5", "not": "**return** sonucu çağıran yere geri gönderir.", "sozluk": "**Geri Dönüş (Return):** Çıktı üretme.", "ipucu": "return kullan."},
            4: {"soru": "Daha önce yazdığın 'selam' fonksiyonunu çağır.", "cevap": "selam()", "not": "Fonksiyonu çalıştırmak için adını ve parantezini yazarız.", "sozluk": "**Çağırma (Call):** Çalıştırma.", "ipucu": "selam()"},
            5: {"soru": "İsim parametresi alan ve 'Selam isim' yazan fonksiyon yap.", "cevap": "def selam(isim):\n    print('Selam', isim)", "not": "Parametreler fonksiyonu dinamik yapar.", "sozluk": "**Dinamik:** Değişken veriyle çalışma.", "ipucu": "print('Selam', isim)"}
        }
    },
    8: {
        "baslik": "OOP: Robot Fabrikası",
        "egzersizler": {
            1: {"soru": "'Robot' isminde boş bir sınıf oluştur.", "cevap": "class Robot:\n    pass", "not": "Sınıflar nesne taslaklarıdır.", "sozluk": "**Sınıf (Class):** Taslak/Şablon.", "ipucu": "class Robot:"},
            2: {"soru": "Sınıfın başlangıç (init) metodunu yaz.", "cevap": "def __init__(self):", "not": "**__init__** nesne oluşurken ilk çalışan metottur.", "sozluk": "**Constructor:** Yapıcı metot.", "ipucu": "self parametresini unutma."},
            3: {"soru": "Robot sınıfından 'pito' adında bir nesne üret.", "cevap": "pito = Robot()", "not": "Taslaktan gerçek bir örnek yapmaktır.", "sozluk": "**Nesne (Object):** Sınıf örneği.", "ipucu": "Robot()"},
            4: {"soru": "Nesneye 'enerji' özelliği ekle.", "cevap": "self.enerji = 100", "not": "**self** o anki nesneyi temsil eder.", "sozluk": "**Öznitelik (Attribute):** Nesnenin verisi.", "ipucu": "self.enerji"},
            5: {"soru": "Robotu hareket ettiren 'git' metodu yaz.", "cevap": "def git(self):\n    print('Gidiyorum')", "not": "Sınıf içindeki fonksiyonlara metot denir.", "sozluk": "**Davranış:** Nesnenin yapabildikleri.", "ipucu": "def git(self):"}
        }
    }
}

# --- FONKSİYONLAR ---
def veri_oku():
    try:
        return conn.read(ttl="0")
    except:
        st.error("Veri tabanı okuma hatası! Lütfen sayfayı yenile.")
        return pd.DataFrame()

def ogrenci_kaydet(no, ad, sinif):
    df = veri_oku()
    if int(no) in df['Okul No'].values: return
    yeni = {"Okul No": int(no), "Öğrencinin Adı": ad, "Sınıf": sinif, "Puan": 0, "Rütbe": RUTBELER[0], "Tamamlanan Modüller": 0, "Mevcut Modül": 1, "Mevcut Egzesiz": 1, "Tarih": time.strftime("%d-%m-%Y")}
    df = pd.concat([df, pd.DataFrame([yeni])], ignore_index=True)
    conn.update(data=df)
    return yeni

def ilerleme_kaydet(u):
    df = veri_oku()
    idx = df[df['Okul No'] == u['Okul No']].index[0]
    for k, v in u.items(): df.at[idx, k] = v
    conn.update(data=df)

# --- SESSION STATE ---
if 'user' not in st.session_state: st.session_state.user = None
if 'hata' not in st.session_state: st.session_state.hata = 0
if 'cevap_verildi' not in st.session_state: st.session_state.cevap_verildi = False

# --- LİDERLİK TABLOSU ---
def liderlik_sidebar():
    df = veri_oku()
    with st.sidebar:
        st.markdown("### 🏆 Şampiyonlar")
        # Okul Liderlik
        st.markdown("**🏫 Okul Top 10**")
        st.dataframe(df.nlargest(10, 'Puan')[['Öğrencinin Adı', 'Puan', 'Rütbe']], hide_index=True)
        # Sınıf Liderlik
        if st.session_state.user:
            s = st.session_state.user['Sınıf']
            st.markdown(f"**🌟 {s} Sınıf Liderleri**")
            st.dataframe(df[df['Sınıf'] == s].nlargest(5, 'Puan')[['Öğrencinin Adı', 'Puan']], hide_index=True)
            if st.button("Çıkış Yap"):
                st.session_state.user = None
                st.rerun()

liderlik_sidebar()

# --- GİRİŞ EKRANI ---
if st.session_state.user is None:
    st.image("assets/pito_merhaba.gif", width=300)
    st.title("Pito Python Akademi")
    okul_no = st.text_input("Okul Numaranı Yaz:", placeholder="Sadece sayı giriniz...")
    
    if okul_no:
        if not okul_no.isdigit():
            st.error("Lütfen sadece sayı gir!")
        else:
            df = veri_oku()
            user_data = df[df['Okul No'] == int(okul_no)]
            if not user_data.empty:
                u = user_data.iloc[0]
                st.success(f"Merhaba {u['Öğrencinin Adı']}! {u['Mevcut Modül']}. Modülde kalmıştın.")
                col1, col2 = st.columns(2)
                if col1.button("Evet, Benim! Devam Et"):
                    st.session_state.user = u.to_dict()
                    st.rerun()
                if col2.button("Hayır, Ben Değilim"): st.rerun()
            else:
                st.warning("Kaydın bulunamadı. Hemen oluşturalım!")
                with st.form("yeni_kayit"):
                    ad = st.text_input("Ad Soyad:")
                    sinif = st.selectbox("Sınıf:", ["9-A", "9-B", "10-A", "10-B"])
                    if st.form_submit_button("Akademiye Katıl"):
                        st.session_state.user = ogrenci_kaydet(okul_no, ad, sinif)
                        st.rerun()

# --- EĞİTİM EKRANI ---
else:
    u = st.session_state.user
    mod_no = int(u['Mevcut Modül'])
    egz_no = int(u['Mevcut Egzesiz'])
    
    # Mezuniyet
    if mod_no > 8:
        st.image("assets/pito_mezun.gif", width=400)
        st.balloons()
        st.title("🎓 TEBRİKLER KAHRAMAN!")
        st.success(f"Eğitimi başarıyla tamamladın! Toplam Puanın: {u['Puan']}")
        if st.button("Eğitimi Sıfırla (Puanın silinir!)"):
            u.update({"Mevcut Modül": 1, "Mevcut Egzesiz": 1, "Puan": 0, "Rütbe": RUTBELER[0]})
            ilerleme_kaydet(u); st.rerun()
        st.stop()

    # İlerleme Çubuğu
    st.progress(((mod_no-1)*5 + (egz_no-1)) / 40)
    
    # Pito Görseli ve Notu
    col_l, col_r = st.columns([3, 1])
    with col_r:
        if st.session_state.hata > 0: st.image("assets/pito_hata.gif")
        else: st.image("assets/pito_dusunuyor.gif")
        st.metric("Puan", u['Puan'])
        st.caption(f"Rütbe: {u['Rütbe']}")

    with col_l:
        data = MÜFREDAT[mod_no]['egzersizler'][egz_no]
        st.markdown(f"""<div class="pito-notu-box">
            <h3>🤖 Pito'nun Notu: {MÜFREDAT[mod_no]['baslik']}</h3>
            <p>{data['not']}</p>
            <div class="pito-sozluk">{data['sozluk']}</div>
        </div>""", unsafe_allow_html=True)
        
        st.subheader(f"Görev {egz_no}: {data['soru']}")
        
        kod = st.text_area("Kodunu Yaz:", height=100)
        user_input = ""
        if data.get("input"):
            user_input = st.text_input("Giriş Verisi (Input):", help="Pito için veri gir!", placeholder="Buraya yaz...")
        
        if st.button("KONTROL ET"):
            if not kod or (data.get("input") and not user_input):
                st.warning("Kod alanı veya giriş verisi boş olamaz!")
            else:
                if kod.strip().replace(" ", "") == data['cevap'].strip().replace(" ", ""):
                    st.image("assets/pito_basari.gif", width=150)
                    st.success("Tebrikler! Bir sonraki adıma geçebilirsin.")
                    # Puan Güncelleme
                    u['Puan'] += (20 - (st.session_state.hata * 5))
                    # İlerleme
                    if egz_no < 5: u['Mevcut Egzesiz'] += 1
                    else:
                        u['Mevcut Modül'] += 1; u['Mevcut Egzesiz'] = 1
                        st.balloons()
                    u['Rütbe'] = RUTBELER[min(int(u['Mevcut Modül']), 8)]
                    st.session_state.hata = 0
                    ilerleme_kaydet(u)
                    time.sleep(2)
                    st.rerun()
                else:
                    st.session_state.hata += 1
                    if st.session_state.hata < 3:
                        st.error(f"Yanlış! Bu {st.session_state.hata}. hatan. Puanın düşüyor...")
                    elif st.session_state.hata == 3:
                        st.warning(f"💡 İPUCU: {data['ipucu']}")
                    else:
                        st.error("4. Hata! Bu sorudan puan alamadın. İşte çözüm:")
                        st.code(data['cevap'])
                        if st.button("Sonraki Soruya Geç"):
                            st.session_state.hata = 0
                            if egz_no < 5: u['Mevcut Egzesiz'] += 1
                            else: u['Mevcut Modül'] += 1; u['Mevcut Egzesiz'] = 1
                            ilerleme_kaydet(u); st.rerun()
