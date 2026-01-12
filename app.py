import streamlit as st
import pandas as pd
import time
import os
from streamlit_gsheets_connection import GSheetsConnection

# --- 1. SAYFA AYARLARI VE GÖRSEL TASARIM ---
st.set_page_config(page_title="Pito Python Akademi", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
    <style>
    .stApp { background-color: #f4f7f6; }
    .pito-note-box { 
        background-color: #ffffff; padding: 25px; border-radius: 20px; 
        border-left: 8px solid #FFD700; box-shadow: 0 4px 15px rgba(0,0,0,0.05);
        margin-bottom: 20px; color: #2c3e50; font-size: 1.1em; line-height: 1.6;
    }
    .leaderboard-card {
        background: white; padding: 12px; border-radius: 12px; 
        margin-bottom: 8px; border: 1px solid #e0e0e0;
    }
    .stButton>button { 
        width: 100%; border-radius: 12px; height: 3.5em; 
        font-weight: bold; font-size: 16px; background-color: #4CAF50; color: white;
    }
    .stTextInput>div>div>input { 
        border: 2px solid #4CAF50; border-radius: 10px; 
        font-family: 'Courier New', monospace; font-size: 18px; color: #1e1e1e;
    }
    .code-panel { 
        background-color: #1e1e1e; color: #dcdcdc; padding: 25px; 
        border-radius: 15px; font-family: 'Consolas', 'Monaco', monospace; 
        margin-bottom: 15px; border: 1px solid #333; font-size: 1.2em;
    }
    .highlight-input { border: 3px solid #FF4B4B !important; animation: blinker 1s linear infinite; }
    @keyframes blinker { 50% { opacity: 0.5; } }
    </style>
    """, unsafe_allow_html=True)

# --- 2. 8 MODÜL VE 40 ADIMLIK TAM MÜFREDAT ---
MUREDDAF = {
    1: {
        "baslik": "Modül 1: Python'un Sesi (Print)",
        "aciklama": "Python'da bilgisayarla konuşmanın yolu <b>print()</b> fonksiyonudur. Ekrana yazı yazdırmak için kelimelerimizi her zaman tırnak içine almalıyız.",
        "egzersizler": [
            {"yonerge": "Ekrana 'Merhaba Pito' yazdıralım. Boşluğu doldur.", "kod": "print(________)", "cevap": "'Merhaba Pito'", "ipucu": "Metinleri tırnak (' ') içine almalısın.", "cikti": "Merhaba Pito"},
            {"yonerge": "Kendi ismini (Örn: 'Ali') ekrana yazdır.", "kod": "print('________')", "cevap": "Ali", "ipucu": "Sadece tırnak içindeki boşluğu doldur.", "cikti": "Ali"},
            {"yonerge": "Sayıları tırnaksız yazdırabiliriz. 2026 yazdır.", "kod": "print(________)", "cevap": "2026", "ipucu": "Rakamlar tırnak gerektirmez.", "cikti": "2026"},
            {"yonerge": "İki veriyi virgül ile ayırırız. 'Puan:', 100 yazdır.", "kod": "print('Puan:' __ 100)", "cevap": ",", "ipucu": "Elemanları ayırmak için virgül (,) kullan.", "cikti": "Puan: 100"},
            {"yonerge": "Yazdırma fonksiyonunun ismini yaz.", "kod": "____('Derse Başlıyoruz')", "cevap": "print", "ipucu": "Ekrana basma komutu p ile başlar.", "cikti": "Derse Başlıyoruz"}
        ]
    },
    2: {
        "baslik": "Modül 2: Hafıza Kutuları (Değişkenler)",
        "aciklama": "Değişkenler, verileri sakladığımız kutulardır. Bir kutuya isim veririz ve <b>=</b> işareti ile içine bir değer koyarız.",
        "egzersizler": [
            {"yonerge": "ad isimli değişkene 'Pito' değerini ata.", "kod": "ad = ________", "cevap": "'Pito'", "ipucu": "Tırnak kullanmayı unutma.", "cikti": ""},
            {"yonerge": "yas değişkenine 15 sayısını ata.", "kod": "yas __ 15", "cevap": "=", "ipucu": "Atama operatörü eşittir (=) işaretidir.", "cikti": ""},
            {"yonerge": "puan değişkenini ekrana yazdır.", "kod": "print(________)", "cevap": "puan", "ipucu": "Değişkeni tırnaksız yazdır.", "cikti": "100"},
            {"yonerge": "okul_no değişkenine 123 değerini ver.", "kod": "okul____no = 123", "cevap": "_", "ipucu": "Değişken isimlerinde boşluk yerine alt tire (_) kullanılır.", "cikti": ""},
            {"yonerge": "sayi değişkenini 1 artırmak için sayi + 1 yaz.", "kod": "yeni_sayi = sayi __ 1", "cevap": "+", "ipucu": "Toplama sembolünü kullan.", "cikti": ""}
        ]
    },
    3: {
        "baslik": "Modül 3: Matematik Sihirbazı",
        "aciklama": "Python mükemmel bir hesap makinesidir. +, -, *, / ve tam bölme için // kullanır.",
        "egzersizler": [
            {"yonerge": "10 ile 5'i çarp.", "kod": "sonuc = 10 __ 5", "cevap": "*", "ipucu": "Çarpma için yıldız (*) kullanılır.", "cikti": "50"},
            {"yonerge": "20'yi 4'e böl.", "kod": "sonuc = 20 __ 4", "cevap": "/", "ipucu": "Bölme için taksim (/) kullanılır.", "cikti": "5.0"},
            {"yonerge": "Kalanı bulmak için % kullanılır. 10'un 3'e bölümünden kalan?", "kod": "kalan = 10 __ 3", "cevap": "%", "ipucu": "Mod alma sembolü yüzdedir.", "cikti": "1"},
            {"yonerge": "Üst almak için ** kullanılır. 2'nin 3. kuvveti?", "kod": "ust = 2 __ 3", "cevap": "**", "ipucu": "İki tane yıldız kullan.", "cikti": "8"},
            {"yonerge": "15'ten 7 çıkar.", "kod": "fark = 15 __ 7", "cevap": "-", "ipucu": "Eksi işaretini kullan.", "cikti": "8"}
        ]
    },
    4: {
        "baslik": "Modül 4: Etkileşim (Input)",
        "aciklama": "Kullanıcıdan bilgi almak için <b>input()</b> kullanırız. Sayı alırken bunu <b>int()</b> ile sarmalamalıyız.",
        "egzersizler": [
            {"yonerge": "Kullanıcıya adını sor.", "kod": "ad = ________('Adın ne?')", "cevap": "input", "ipucu": "Giriş fonksiyonu i ile başlar.", "cikti": ""},
            {"yonerge": "Alınan yaşı tam sayıya çevir.", "kod": "yas = ____(input('Yaşın?'))", "cevap": "int", "ipucu": "Integer kelimesinin kısaltması.", "cikti": ""},
            {"yonerge": "input parantezi içine mesaj yazılır.", "kod": "input(__Lütfen sayı girin__)", "cevap": "'Lütfen sayı girin'", "ipucu": "Mesajlar tırnak içinde olur.", "cikti": ""},
            {"yonerge": "Input ile alınan veriyi ekrana yazdır.", "kod": "x = input(); print(__)", "cevap": "x", "ipucu": "Değişken adını yaz.", "cikti": ""},
            {"yonerge": "input() her zaman metin (str) döndürür.", "kod": "tip = ____(input())", "cevap": "type", "ipucu": "Tür öğrenme fonksiyonu.", "cikti": "<class 'str'>"}
        ]
    },
    5: {
        "baslik": "Modül 5: Karar Odası (If-Else)",
        "aciklama": "Python'da kararlar <b>if</b> (eğer) ve <b>else</b> (değilse) ile verilir. Şartın sonuna iki nokta (:) koymayı unutma!",
        "egzersizler": [
            {"yonerge": "Eğer yaş 18'den büyükse:", "kod": "if yas __ 18:", "cevap": ">", "ipucu": "Büyüktür sembolü.", "cikti": ""},
            {"yonerge": "Şart sağlanmazsa çalışacak blok?", "kod": "____:", "cevap": "else", "ipucu": "Eğer değilse anlamına gelir.", "cikti": ""},
            {"yonerge": "Eşit mi kontrolü için == kullanılır.", "kod": "if sifre ____ '1234':", "cevap": "==", "ipucu": "İki tane eşittir koy.", "cikti": ""},
            {"yonerge": "İkinci bir şart eklemek için:", "kod": "______ yas == 18:", "cevap": "elif", "ipucu": "else ve if birleşimi.", "cikti": ""},
            {"yonerge": "Eşit değilse kontrolü:", "kod": "if ad __ 'Pito':", "cevap": "!=", "ipucu": "Ünlem ve eşittir.", "cikti": ""}
        ]
    },
    6: {
        "baslik": "Modül 6: Tekrar Makinesi (Loops)",
        "aciklama": "Bilgisayarlar yorulmaz! <b>for</b> döngüsü ile işlemleri belirli sayıda tekrar edebiliriz.",
        "egzersizler": [
            {"yonerge": "5 kez dönen bir döngü kur.", "kod": "for i in range(____):", "cevap": "5", "ipucu": "Parantez içine 5 yaz.", "cikti": "0, 1, 2, 3, 4"},
            {"yonerge": "Döngü başlatma komutu nedir?", "kod": "____ i in range(10):", "cevap": "for", "ipucu": "f ile başlayan döngü.", "cikti": ""},
            {"yonerge": "range içine (başlangıç, bitiş) yazılır.", "kod": "range(1, ____)", "cevap": "11", "ipucu": "10'a kadar gitmesi için 11 yazmalısın.", "cikti": ""},
            {"yonerge": "Şart doğru olduğu sürece dönen döngü?", "kod": "________ x < 5:", "cevap": "while", "ipucu": "w ile başlar.", "cikti": ""},
            {"yonerge": "Döngüyü aniden durdurmak için:", "kod": "if hata: ________", "cevap": "break", "ipucu": "Kırmak anlamına gelir.", "cikti": ""}
        ]
    },
    7: {
        "baslik": "Modül 7: Veri Sepetleri (Lists)",
        "aciklama": "Listeler birden fazla veriyi tek bir değişkende saklar. Köşeli parantez <b>[]</b> kullanılır.",
        "egzersizler": [
            {"yonerge": "Boş bir liste oluştur.", "kod": "liste = ____", "cevap": "[]", "ipucu": "Alt Gr + 8 ve 9 tuşları.", "cikti": "[]"},
            {"yonerge": "Listeye 'elma' ekle.", "kod": "meyveler.________('elma')", "cevap": "append", "ipucu": "Eklemek anlamına gelen metod.", "cikti": ""},
            {"yonerge": "Listenin ilk elemanına ulaş (indeks 0).", "kod": "print(liste[____])", "cevap": "0", "ipucu": "Sıfırıncı indeks.", "cikti": ""},
            {"yonerge": "Listenin kaç elemanlı olduğunu bul.", "kod": "____(liste)", "cevap": "len", "ipucu": "Length kısaltması.", "cikti": ""},
            {"yonerge": "Listeden eleman silmek için:", "kod": "liste.________('elma')", "cevap": "remove", "ipucu": "Kaldırmak anlamına gelir.", "cikti": ""}
        ]
    },
    8: {
        "baslik": "Modül 8: Python Kahramanı (Functions)",
        "aciklama": "Kendi özel komutlarını yaratmaya hazır mısın? <b>def</b> ile fonksiyon tanımlayıp her yerden çağırabilirsin.",
        "egzersizler": [
            {"yonerge": "selamla isminde bir fonksiyon tanımla.", "kod": "____ selamla():", "cevap": "def", "ipucu": "Define kısaltması.", "cikti": ""},
            {"yonerge": "Fonksiyondan veri döndürmek için:", "kod": "________ sonuc", "cevap": "return", "ipucu": "Geri döndür komutu.", "cikti": ""},
            {"yonerge": "Tanımlanan 'test' fonksiyonunu çağır.", "kod": "________()", "cevap": "test", "ipucu": "Fonksiyonun adını yaz.", "cikti": ""},
            {"yonerge": "Fonksiyon parantez içine ne alır?", "kod": "def topla(________):", "cevap": "sayi", "ipucu": "Parametre ismi.", "cikti": ""},
            {"yonerge": "Artık bir Python Kahramanısın! Son boşluğu 'Pito' ile doldur.", "kod": "hero = '________'", "cevap": "Pito", "ipucu": "Pito yazmalısın.", "cikti": "Pito"}
        ]
    }
}

RUTBELER = ["🥚 Yeni Başlayan", "🌱 Python Çırağı", "🪵 Kod Oduncusu", "🧱 Mantık Mimarı", "🌀 Döngü Ustası", "📋 Liste Uzmanı", "📦 Fonksiyon Kaptanı", "🤖 OOP Robotu", "🏆 Python Kahramanı"]

# --- 3. SESSION STATE (BELLEK) YÖNETİMİ ---
if 'init' not in st.session_state:
    st.session_state.update({
        'init': True, 'logged_in': False, 'user_data': None,
        'modul': 1, 'egzersiz': 1, 'total_puan': 0,
        'current_eg_puan': 20, 'hatalar': 0, 'finished': False,
        'review_mode': False, 'last_output': "", 'error_msg': ""
    })

# --- 4. YARDIMCI FONKSİYONLAR ---
def pito_gif(emotion):
    path = f"assets/pito_{emotion}.gif"
    if os.path.exists(path):
        st.image(path, width=250)
    else:
        st.info(f"🐍 Pito [{emotion}] (GIF Dosyası assets/ içinde bulunamadı)")

def get_rank(puan):
    idx = min(len(RUTBELER)-1, puan // 100)
    return RUTBELER[idx]

# --- 5. GİRİŞ VE KAYIT EKRANI ---
if not st.session_state.logged_in:
    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        pito_gif("merhaba")
        st.title("Pito Python Akademi")
        st.markdown("### Nusaybin Süleyman Bölünmez Anadolu Lisesi")
        
        okul_no = st.text_input("Okul Numaranı Gir", key="login_no", placeholder="Sadece sayı giriniz...")
        
        if okul_no:
            # Mock DB (Normalde Google Sheets'ten okunacak)
            if okul_no == "123": # Örnek kayıtlı kullanıcı
                st.info("Merhaba **Ahmet Yılmaz**! 1. Modül, 1. Egzersizdesin.")
                c1, c2 = st.columns(2)
                if c1.button("Evet, Benim! 👍"):
                    st.session_state.logged_in = True
                    st.session_state.user_data = {"ad": "Ahmet Yılmaz", "no": "123"}
                    st.rerun()
                if c2.button("Hayır, Ben Değilim ❌"):
                    st.session_state.login_no = ""
                    st.rerun()
            else:
                st.warning("Numara kayıtlı değil. Yeni profil oluştur!")
                with st.form("kayit"):
                    yeni_ad = st.text_input("Ad Soyad")
                    yeni_sinif = st.selectbox("Sınıf", ["9-A", "9-B", "10-A", "10-B", "11-A", "12-A"])
                    if st.form_submit_button("Kayıt Ol ve Başla 🚀"):
                        st.session_state.logged_in = True
                        st.session_state.user_data = {"ad": yeni_ad, "no": okul_no, "sinif": yeni_sinif}
                        st.rerun()

# --- 6. ANA AKADEMİ PANELİ ---
else:
    # Liderlik Tablosu (Sağ Sidebar)
    with st.sidebar:
        st.header("🏆 Liderlik Kürsüsü")
        st.markdown("### 🏫 Okul İlk 10")
        st.markdown("<div class='leaderboard-card'>🥇 105 - Elif - 🏆 Hero</div>", unsafe_allow_html=True)
        st.markdown("<div class='leaderboard-card'>🥈 123 - Ahmet - 📋 Uzman</div>", unsafe_allow_html=True)
        st.divider()
        st.markdown("### 🏁 Şampiyon Sınıf")
        st.success("🏆 9-A Sınıfı")

    # Üst Bölüm: İlerleme ve Rütbe
    curr_m = st.session_state.modul
    curr_e = st.session_state.egzersiz
    progress = ((curr_m - 1) * 5 + curr_e) / 40
    
    st.progress(progress)
    st.write(f"📊 İlerleme: %{int(progress*100)} | **Rütbe:** {get_rank(st.session_state.total_puan)} | **Puan:** {st.session_state.total_puan}")

    # Orta Bölüm: Pito ve İçerik
    col_pito, col_content = st.columns([1, 2.5])
    
    with col_pito:
        if st.session_state.finished: pito_gif("mezun")
        elif st.session_state.hatalar > 0: pito_gif("hata")
        else: pito_gif("dusunuyor")

    with col_content:
        st.markdown(f"<div class='pito-note-box'><h3>🐍 Pito'nun Notu</h3>{MUREDDAF[curr_m]['aciklama']}</div>", unsafe_allow_html=True)

    # Alt Bölüm: Egzersiz ve Kod Paneli
    st.divider()
    eg = MUREDDAF[curr_m]['egzersizler'][curr_e - 1]
    
    st.subheader(f"📝 Egzersiz {curr_e}: {eg['yonerge']}")
    
    # İnceleme Modu Kontrolü
    if st.session_state.review_mode:
        st.markdown(f"<div class='code-panel'>{eg['kod'].replace('________', '<span style=\"color:#FFD700\">'+eg['cevap']+'</span>')}</div>", unsafe_allow_html=True)
        if eg['cikti']: st.code(f"Çıktı: {eg['cikti']}")
        if st.button("Sonraki Adımı İncele ➡️"):
            if st.session_state.egzersiz < 5: st.session_state.egzersiz += 1
            elif st.session_state.modul < 8: st.session_state.modul += 1; st.session_state.egzersiz = 1
            st.rerun()
    else:
        st.markdown(f"<div class='code-panel'>{eg['kod']}</div>", unsafe_allow_html=True)
        
        user_input = st.text_input("Eksik kodu buraya yaz ve Enter'a bas:", key=f"inp_{curr_m}_{curr_e}")
        
        if st.button("Kontrol Et 🚀"):
            if not user_input:
                st.warning("⚠️ Pito: 'Lütfen boşluğu doldurmadan kontrol etme!'")
            else:
                if user_input.strip() == eg['cevap']:
                    st.session_state.total_puan += st.session_state.current_eg_puan
                    st.session_state.hatalar = 0
                    st.session_state.current_eg_puan = 20
                    st.success(f"🎊 Harika! Doğru cevap. +{st.session_state.total_puan} Puan kazandın!")
                    pito_gif("basari")
                    if eg['cikti']: st.code(f"Çıktı: {eg['cikti']}")
                    
                    time.sleep(1.5)
                    # İlerleme mantığı
                    if st.session_state.egzersiz < 5:
                        st.session_state.egzersiz += 1
                    else:
                        st.balloons()
                        if st.session_state.modul < 8:
                            st.session_state.modul += 1
                            st.session_state.egzersiz = 1
                        else:
                            st.session_state.finished = True
                    st.rerun()
                else:
                    st.session_state.hatalar += 1
                    st.session_state.current_eg_puan -= 5
                    
                    if st.session_state.hatalar < 3:
                        st.error(f"❌ Hatalı! Bu {st.session_state.hatalar}. denemen. Puanın 5 düştü! (Kalan: {st.session_state.current_eg_puan})")
                    elif st.session_state.hatalar == 3:
                        st.warning(f"💡 Pito'dan İpucu: {eg['ipucu']}")
                    else:
                        st.error("😔 4. hata! Bu sorudan puan alamadın. Hadi bir sonrakine geçelim.")
                        st.info(f"✅ Doğru Çözüm: {eg['cevap']}")
                        if st.button("Sonraki Soruya Geç ➡️"):
                            st.session_state.hatalar = 0
                            st.session_state.current_eg_puan = 20
                            if st.session_state.egzersiz < 5: st.session_state.egzersiz += 1
                            else: 
                                if st.session_state.modul < 8: st.session_state.modul += 1; st.session_state.egzersiz = 1
                            st.rerun()

# --- 7. MEZUNİYET EKRANI ---
if st.session_state.finished:
    st.balloons()
    st.markdown("## 🏆 TEBRİKLER PYTHON KAHRAMANI! 🏆")
    st.write("Eğitimi başarıyla tamamladın. Nusaybin'in en iyi kod yazarı olma yolunda dev bir adım attın!")
    
    col_fin1, col_fin2 = st.columns(2)
    with col_fin1:
        if st.button("Eğitimi Sıfırla ve Baştan Al 🔄"):
            st.session_state.update({'modul': 1, 'egzersiz': 1, 'total_puan': 0, 'finished': False, 'review_mode': False})
            st.rerun()
    with col_fin2:
        if st.button("İnceleme Moduna Geç 🔍"):
            st.session_state.review_mode = True
            st.session_state.modul = 1
            st.session_state.egzersiz = 1
            st.rerun()
