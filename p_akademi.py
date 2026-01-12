import streamlit as st
import pandas as pd
import base64
import re

# --- 1. SAYFA AYARLARI VE ÖZEL CSS ---
st.set_page_config(page_title="Pito Python Akademi", layout="wide")

st.markdown("""
    <style>
    /* CodeSignal Temalı Editör ve Okunabilirlik İyileştirmesi */
    .stApp { background-color: #F8F9FA; }
    .pito-note {
        background-color: #FFFFFF;
        padding: 20px;
        border-radius: 12px;
        border-left: 6px solid #2E7D32;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
        margin-bottom: 25px;
        color: #1B5E20;
    }
    .editor-container { background-color: #1E1E1E; border-radius: 10px 10px 0 0; border: 1px solid #333; margin-top: 15px; }
    .editor-header { background-color: #2D2D2D; color: #D4D4D4; padding: 10px 20px; border-radius: 10px 10px 0 0; font-family: 'Consolas', monospace; font-size: 13px; }
    .editor-tab { background-color: #1E1E1E; padding: 8px 25px; display: inline-block; color: #FFF; border-right: 1px solid #333; font-weight: bold; }
    
    /* Disabled durumunda metin okunabilirliği çözümü */
    .stTextArea textarea {
        background-color: #1E1E1E !important;
        color: #D4D4D4 !important;
        font-family: 'Consolas', monospace !important;
        font-size: 17px !important;
        border-radius: 0 0 10px 10px !important;
    }
    .stTextArea textarea:disabled {
        color: #A6E22E !important;
        -webkit-text-fill-color: #A6E22E !important;
        opacity: 1 !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. YARDIMCI FONKSİYONLAR ---
def get_rank(points):
    ranks = [(800, "🏆 Python Kahramanı"), (700, "🤖 OOP Robotu"), (600, "📦 Fonksiyon Kaptanı"), 
             (500, "📋 Liste Uzmanı"), (400, "🌀 Döngü Ustası"), (300, "🧱 Mantık Mimarı"), 
             (200, "🪵 Kod Oduncusu"), (100, "🌱 Python Çırağı"), (0, "🥚 Yeni Başlayan")]
    for limit, label in ranks:
        if points >= limit: return label
    return "🥚 Yeni Başlayan"

def render_gif(name):
    try:
        with open(f"assets/{name}.gif", "rb") as f:
            data = f.read()
            url = base64.b64encode(data).decode()
            st.markdown(f'<img src="data:image/gif;base64,{url}" width="250">', unsafe_allow_html=True)
    except: st.info(f"[{name}.gif Hazırlanıyor...]")

# --- 3. 40 ADIMLIK MÜFREDAT (PDF KAYNAKLI)  ---
training_data = [
    {
        "module_title": "1. Python'a Giriş: Yazdırma Komutları",
        "intro": "Python'da bilgisayarla iletişim kurmanın yolu `print()` fonksiyonudur. Metinler tırnak içinde, sayılar ise doğrudan yazılır.",
        "exercises": [
            {"task": "print('___')", "solution": "print('Merhaba Dünya')", "msg": "Ekrana 'Merhaba Dünya' yazdır.", "hint": "Metni tırnak içine almayı unutma.", "output": "Merhaba Dünya"},
            {"task": "print(20 + ___)", "solution": "print(20 + 23)", "msg": "20 ile 23'ü toplayıp sonucu yazdır.", "hint": "Sadece 23 yaz.", "output": "43"},
            {"task": "___('Pito Akademi')", "solution": "print('Pito Akademi')", "msg": "Yazdırma fonksiyonunu boşluğa yerleştir.", "hint": "Fonksiyonun adı print.", "output": "Pito Akademi"},
            {"task": "# Bu bir ___ satırıdır", "solution": "# Bu bir yorum satırıdır", "msg": "Python'un okumayacağı bir yorum satırı oluştur.", "hint": "Yorum kelimesini kullan.", "output": None},
            {"task": "print('Pito', '___')", "solution": "print('Pito', 'Akademi')", "msg": "Virgül kullanarak iki kelimeyi birleştir.", "hint": "Akademi yaz.", "output": "Pito Akademi"}
        ]
    },
    {
        "module_title": "2. Değişkenler ve Veri Saklama",
        "intro": "Değişkenler hafızadaki kutulardır. `=` işareti ile kutulara veri atarız.",
        "exercises": [
            {"task": "yas = ___", "solution": "yas = 15", "msg": "yas değişkenine 15 sayısını ata.", "hint": "Eşittir'den sonra 15 yaz.", "output": None},
            {"task": "isim = '___'", "solution": "isim = 'Pito'", "msg": "isim değişkenine Pito değerini ver.", "hint": "Tırnaklar arasına Pito yaz.", "output": None},
            {"task": "print(type(___))", "solution": "print(type(10))", "msg": "10 sayısının veri tipini ekrana bas.", "hint": "Parantez içine 10 yaz.", "output": "<class 'int'>"},
            {"task": "sayi = ___('50')", "solution": "sayi = int('50')", "msg": "Metni tam sayıya (integer) dönüştür.", "hint": "Dönüşüm fonksiyonu int().", "output": None},
            {"task": "print(len('___'))", "solution": "print(len('Python'))", "msg": "Python kelimesinin karakter uzunluğunu ölç.", "hint": "Tırnak içine Python yaz.", "output": "6"}
        ]
    },
    {
        "module_title": "3. Matematik Operatörleri",
        "intro": "Python aritmetik işlemleri (+, -, *, /) kolayca yapabilir. // tam bölme, % kalan (mod) verir.",
        "exercises": [
            {"task": "print(10 ___ 5)", "solution": "print(10 * 5)", "msg": "10 ile 5'i çarpan işareti koy.", "hint": "Yıldız (*) işareti.", "output": "50"},
            {"task": "print(17 ___ 3)", "solution": "print(17 // 3)", "msg": "17'nin 3'e bölümünden tam kısmı al.", "hint": "Tam bölme operatörü //.", "output": "5"},
            {"task": "print(10 ___ 3)", "solution": "print(10 % 3)", "msg": "10'un 3'e bölümünden kalanı bul.", "hint": "Mod alma operatörü %.", "output": "1"},
            {"task": "print(2 ___ 4)", "solution": "print(2 ** 4)", "msg": "2'nin 4. kuvvetini (üssünü) hesapla.", "hint": "Üs operatörü **.", "output": "16"},
            {"task": "print((5+5) ___ 2)", "solution": "print((5+5) / 2)", "msg": "Toplama işleminden sonra 2'ye böl.", "hint": "Bölme işareti /.", "output": "5.0"}
        ]
    },
    {
        "module_title": "4. Karar Yapıları: if-else",
        "intro": "Programlarımızın şartlara göre karar vermesi için if-elif-else yapılarını kullanırız.",
        "exercises": [
            {"task": "if 10 ___ 10: print('Eşit')", "solution": "if 10 == 10: print('Eşit')", "msg": "Eşitlik kontrolü yap (==).", "hint": "Çift eşittir kullan.", "output": "Eşit"},
            {"task": "if 5 > 10: pass\n___: print('B')", "solution": "else: print('B')", "msg": "Şart yanlışsa çalışacak (else) bloğu tamamla.", "hint": "else: yazmalısın.", "output": "B"},
            {"task": "if 1<0: pass\n___ 1>0: print('C')", "solution": "elif 1>0: print('C')", "msg": "İkinci bir şartı (elif) ekle.", "hint": "elif yaz.", "output": "C"},
            {"task": "if True ___ False: print('X')", "solution": "if True and False: print('X')", "msg": "İki şartın da doğru olmasını bekleyen operatörü yaz.", "hint": "and operatörü.", "output": None},
            {"task": "if 5 ___ 3: print('Y')", "solution": "if 5 != 3: print('Y')", "msg": "Eşit değilse (!=) operatörünü kullan.", "hint": "Ünlem ve eşittir (!=).", "output": "Y"}
        ]
    },
    {
        "module_title": "5. Listeler ile Veri Gruplama",
        "intro": "Listeler birden fazla veriyi tek bir kutuda tutar. Elemanlara indeksleri ile ulaşırız.",
        "exercises": [
            {"task": "L = [___, 'Muz']", "solution": "L = ['Elma', 'Muz']", "msg": "Listenin başına 'Elma' ekle.", "hint": "Tırnak içinde Elma.", "output": None},
            {"task": "print(L[___])", "solution": "print(L[0])", "msg": "Listenin ilk elemanına (0. indeks) eriş.", "hint": "Sadece 0.", "output": "Elma"},
            {"task": "L.___('Çilek')", "solution": "L.append('Çilek')", "msg": "Listeye eleman ekleyen metodu yaz.", "hint": "append metodu.", "output": None},
            {"task": "L.pop(___)", "solution": "L.pop(0)", "msg": "Listenin ilk elemanını sil.", "hint": "0 indeksini sil.", "output": None},
            {"task": "print(___(L))", "solution": "print(len(L))", "msg": "Listenin boyutunu ekrana bas.", "hint": "len() fonksiyonu.", "output": "2"}
        ]
    },
    {
        "module_title": "6. Döngüler: for",
        "intro": "Belirli işlemleri tekrar etmek için döngüleri kullanırız.",
        "exercises": [
            {"task": "for i in ___(3): print(i)", "solution": "for i in range(3): print(i)", "msg": "0'dan 2'ye kadar sayı üreten fonksiyonu yaz.", "hint": "range kelimesi.", "output": "0\n1\n2"},
            {"task": "for harf ___ 'Hi': print(harf)", "solution": "for harf in 'Hi': print(harf)", "msg": "Kelimedeki harfleri gezen operatörü yaz.", "hint": "in operatörü.", "output": "H\ni"},
            {"task": "for i in range(2): ___('A')", "solution": "for i in range(2): print('A')", "msg": "Ekrana 2 kez 'A' yazdır.", "hint": "print fonksiyonu.", "output": "A\nA"},
            {"task": "for i in [1, 2]: print(i ___ 5)", "solution": "for i in [1, 2]: print(i * 5)", "msg": "Sayıları 5 ile çarparak yazdır.", "hint": "Yıldız (*) koy.", "output": "5\n10"},
            {"task": "for i in range(5):\n if i==1: ___\n print(i)", "solution": "if i==1: break", "msg": "Döngüyü i=1 olduğunda kır.", "hint": "break yaz.", "output": "0"}
        ]
    },
    {
        "module_title": "7. Döngüler: while",
        "intro": "Bir şart doğru olduğu sürece çalışmaya devam eden döngülerdir.",
        "exercises": [
            {"task": "i=0\n___ i<2: print(i); i+=1", "solution": "while i<2:", "msg": "Koşullu döngüyü başlat.", "hint": "while kelimesi.", "output": "0\n1"},
            {"task": "while True: print('X'); ___", "solution": "break", "msg": "Sonsuz döngüyü anında durdur.", "hint": "break kelimesi.", "output": "X"},
            {"task": "i=0\nwhile i<2:\n i ___ 1", "solution": "i += 1", "msg": "Sonsuza girmemesi için i'yi artır.", "hint": "+= operatörü.", "output": None},
            {"task": "while 1 ___ 1: print('Y'); break", "solution": "while 1 == 1:", "msg": "Şart kısmına '1 eşittir 1' yaz.", "hint": "Çift eşittir (==).", "output": "Y"},
            {"task": "while False: ___('Görünmez')", "solution": "while False: print('Görünmez')", "msg": "Döngü gövdesini tamamla.", "hint": "print yaz.", "output": None}
        ]
    },
    {
        "module_title": "8. Fonksiyonlar ve Modüller",
        "intro": "Kod parçalarını isimlendirip paketlemek için fonksiyonlar ve modüller kullanılır.",
        "exercises": [
            {"task": "___ hi(): print('Selam')", "solution": "def hi(): print('Selam')", "msg": "Fonksiyon tanımlama kelimesini yaz.", "hint": "def kelimesi.", "output": None},
            {"task": "def topla(a, b): ___ a+b", "solution": "return a+b", "msg": "Sonucu dışarı fırlat.", "hint": "return kelimesi.", "output": None},
            {"task": "import ___", "solution": "import math", "msg": "Matematik modülünü çağır.", "hint": "math yaz.", "output": None},
            {"task": "print(math.sqrt(___))", "solution": "print(math.sqrt(9))", "msg": "9 sayısının karekökünü hesapla.", "hint": "9 yaz.", "output": "3.0"},
            {"task": "print(math.pow(2, ___))", "solution": "print(math.pow(2, 3))", "msg": "2'nin 3. kuvvetini hesapla.", "hint": "3 yaz.", "output": "8.0"}
        ]
    }
]

# --- 4. DURUM YÖNETİMİ VE HATA ÇÖZÜMÜ ---
if 'user' not in st.session_state:
    st.session_state.user = None
    st.session_state.errors = 0
    st.session_state.score_pool = 20
    st.session_state.is_completed = False
    st.session_state.feedback_text = ""  # DeltaGenerator hatasını önleme

# --- 5. ANA PANEL VE GİRİŞ ---
if st.session_state.user is None:
    c1, c2 = st.columns([2, 1])
    with c1:
        render_gif("pito_merhaba")
        st.title("Pito Python Akademi")
        okul_no = st.text_input("Okul Numaranı Gir:")
        if okul_no:
            # KeyError çözüm: Sabit anahtar kullanımı
            st.session_state.user = {"Okul No": okul_no, "Ad": "Genç Yazılımcı", "Modül": 1, "Egzersiz": 1, "Puan": 0}
            st.rerun()
else:
    u = st.session_state.user
    m_idx, e_idx = int(u["Modül"]) - 1, int(u["Egzersiz"]) - 1
    curr_ex = training_data[m_idx]["exercises"][e_idx]
    
    mc, sc = st.columns([2.5, 1])
    with mc:
        # Pito Durumu
        if st.session_state.is_completed:
            render_gif("pito_dusunuyor" if st.session_state.errors >= 4 else "pito_basari")
        elif st.session_state.errors > 0: render_gif("pito_hata")
        else: render_gif("pito_dusunuyor")

        st.markdown(f'<div class="pito-note"><b>🐍 Pito\'nun Notu:</b><br>{curr_ex["msg"]}</div>', unsafe_allow_html=True)
        
        if st.session_state.feedback_text:
            st.error(st.session_state.feedback_text) if "Yanlış" in st.session_state.feedback_text else st.warning(st.session_state.feedback_text)

        # Editör Paneli
        st.markdown('<div class="editor-container"><div class="editor-header"><div class="editor-tab">solution.py</div></div></div>', unsafe_allow_html=True)
        ans = st.text_area("Kod Girişi:", value=curr_ex['task'], height=130, key=f"e_{m_idx}_{e_idx}", disabled=st.session_state.is_completed, label_visibility="collapsed")

        if not st.session_state.is_completed:
            if st.button("Kontrol Et"):
                # Karşılaştırma Mantığı Geliştirme (Whitespace/Quotes normalizasyonu)
                clean_ans = re.sub(r"\s+", "", ans).replace("'", '"')
                clean_sol = re.sub(r"\s+", "", curr_ex["solution"]).replace("'", '"')
                
                if clean_ans == clean_sol:
                    st.session_state.is_completed = True
                    st.session_state.feedback_text = ""
                    u["Puan"] += st.session_state.score_pool
                    st.rerun()
                else:
                    st.session_state.errors += 1
                    st.session_state.score_pool = max(0, st.session_state.score_pool - 5)
                    if st.session_state.errors < 3:
                        st.session_state.feedback_text = f"❌ Yanlış! {st.session_state.errors}. denemen. -5 Puan."
                    elif st.session_state.errors == 3:
                        st.session_state.feedback_text = f"💡 Pito'dan İpucu: {curr_ex['hint']}"
                    elif st.session_state.errors >= 4:
                        st.session_state.is_completed = True
                        st.session_state.feedback_text = "🚨 4 hata yaptın. Çözümü inceleyebilirsin."
                    st.rerun()

        if st.session_state.is_completed:
            st.divider()
            if st.session_state.errors >= 4:
                st.info(f"✅ Doğru Çözüm: `{curr_ex['solution']}`")
            else:
                st.success("✨ Tebrikler! Doğru cevap.")
                # SyntaxError Giderme: F-string dışına çıkarma
                if curr_ex["output"]:
                    st.code(f"Kod Çıktısı:\n{curr_ex['output']}")

            if st.button("Sonraki Adıma Geç ➡️"):
                if e_idx < 4: u["Egzersiz"] += 1
                else: u["Modül"] += 1; u["Egzersiz"] = 1
                st.session_state.is_completed, st.session_state.errors, st.session_state.score_pool, st.session_state.feedback_text = False, 0, 20, ""
                st.rerun()

    with sc:
        st.subheader(f"👤 {u['Ad']}")
        st.metric("Puan", u["Puan"]); st.write(f"**Rütbe:** {get_rank(u['Puan'])}")
