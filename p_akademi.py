import streamlit as st
import pandas as pd
import base64
import re

# --- 1. SAYFA AYARLARI VE CSS ---
st.set_page_config(page_title="Pito Python Akademi", layout="wide")

st.markdown("""
    <style>
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
    .stTextArea textarea {
        background-color: #1E1E1E !important;
        color: #D4D4D4 !important;
        font-family: 'Consolas', monospace !important;
        font-size: 17px !important;
        border-radius: 0 0 10px 10px !important;
        padding: 20px !important;
    }
    /* Disabled durumunda metin okunabilirliği */
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
            st.markdown(f'<img src="data:image/gif;base64,{url}" width="280">', unsafe_allow_html=True)
    except: st.info(f"[{name}.gif Hazırlanıyor...]")

# --- 3. 8 MODÜL VE 40 ADIMLIK EKSİKSİZ MÜFREDAT ---
# Müfredat: Bilgisayar Bilimi Kur 1 - 2. Bölüm standartlarına göre oluşturulmuştur[cite: 2, 4, 5].
training_data = [
    {
        "module_title": "1. Merhaba Python: Giriş ve Çıktı",
        "intro": "Python dünyasına hoş geldin! Bu bölümde bilgisayarla iletişim kurmanın en temel yolu olan ekrana yazdırmayı öğreneceğiz.",
        "exercises": [
            {"task": "print('___')", "solution": "print('Merhaba Pito')", "msg": "Ekrana tam olarak **'Merhaba Pito'** yazdır.", "hint": "Metinleri tırnak (' ') içine almalısın.", "output": "Merhaba Pito"},
            {"task": "print(10 + ___)", "solution": "print(10 + 20)", "msg": "Ekrana 10 ve 20'nin toplamını yazdır.", "hint": "Sadece 20 yaz.", "output": "30"},
            {"task": "___('Pito Python Akademi')", "solution": "print('Pito Python Akademi')", "msg": "Yazdırma komutu olan **print** fonksiyonunu kullan.", "hint": "Parantezden önce print yaz.", "output": "Pito Python Akademi"},
            {"task": "print('Mardin', '___')", "solution": "print('Mardin', 'Nusaybin')", "hint": "Tırnak içinde Nusaybin yaz.", "msg": "Mardin ve Nusaybin kelimelerini virgül kullanarak yanyana yazdır.", "output": "Mardin Nusaybin"},
            {"task": "# ___ satırı", "solution": "# Yorum satırı", "msg": "Python'ın görmezden gelmesi için bir yorum satırı oluştur.", "hint": "Diyez (#) işaretinden sonra 'Yorum' yaz.", "output": None}
        ]
    },
    {
        "module_title": "2. Veri Tipleri ve Değişkenler",
        "intro": "Değişkenler, bilgileri sakladığımız hafıza kutularıdır. Python'da her verinin bir tipi (int, str, float) vardır.",
        "exercises": [
            {"task": "puan = ___", "solution": "puan = 100", "msg": "**puan** değişkenine 100 değerini ata.", "hint": "Eşittir'den sonra 100 yaz.", "output": None},
            {"task": "isim = '___'", "solution": "isim = 'Pito'", "msg": "**isim** değişkenine 'Pito' metnini ata.", "hint": "Tırnaklar arasına Pito yaz.", "output": None},
            {"task": "print(type(___))", "solution": "print(type(5.5))", "msg": "Ondalıklı bir sayının (örn: 5.5) tipini ekrana yazdır.", "hint": "Parantez içine 5.5 yaz.", "output": "<class 'float'>"},
            {"task": "sayi = ___('50')", "solution": "sayi = int('50')", "msg": "Metin halindeki '50'yi tam sayıya (integer) çevir.", "hint": "Dönüştürme komutu int() kullan.", "output": None},
            {"task": "print(len('___'))", "solution": "print(len('Pito'))", "msg": "'Pito' kelimesinin kaç karakterden oluştuğunu bul.", "hint": "Tırnaklar içine Pito yaz.", "output": "4"}
        ]
    },
    {
        "module_title": "3. Matematiksel Operatörler",
        "intro": "Python güçlü bir hesap makinesidir! Toplama (+), çıkarma (-), çarpma (*) ve bölme (/) işlemlerini yapabiliriz.",
        "exercises": [
            {"task": "print(10 ___ 2)", "solution": "print(10 * 2)", "msg": "10 ile 2'yi çarpan operatörü yaz.", "hint": "Yıldız (*) işaretini kullan.", "output": "20"},
            {"task": "print(15 ___ 4)", "solution": "print(15 // 4)", "msg": "15'in 4'e bölümünden sadece tam kısmı (taban bölme) al.", "hint": "Çift eğik çizgi (//) kullan.", "output": "3"},
            {"task": "print(10 ___ 3)", "solution": "print(10 % 3)", "msg": "10'un 3'e bölümünden kalanı (mod) bul.", "hint": "Yüzde (%) işaretini kullan.", "output": "1"},
            {"task": "print(2 ___ 3)", "solution": "print(2 ** 3)", "msg": "2'nin 3. kuvvetini (üssünü) hesapla.", "hint": "Çift yıldız (**) kullan.", "output": "8"},
            {"task": "print( (5+5) ___ 2 )", "solution": "print( (5+5) * 2 )", "msg": "Önce parantez içini toplayıp sonra 2 ile çarpan kodu tamamla.", "hint": "Yıldız (*) işaretini koy.", "output": "20"}
        ]
    },
    {
        "module_title": "4. Karar Yapıları: if-else",
        "intro": "Programlarımızın karar vermesini sağlarız. 'Eğer hava yağmurluysa şemsiye al' mantığı burada çalışır.",
        "exercises": [
            {"task": "if 10 ___ 10: print('Eşit')", "solution": "if 10 == 10: print('Eşit')", "msg": "Eşitlik kontrolü için gereken operatörü yaz.", "hint": "İki tane eşittir (==) kullan.", "output": "Eşit"},
            {"task": "if 5 > 3: ___('Büyük')", "solution": "if 5 > 3: print('Büyük')", "msg": "Şart doğruysa ekrana 'Büyük' yazdır.", "hint": "print fonksiyonunu ekle.", "output": "Büyük"},
            {"task": "if 10 < 5: pass\n___: print('Küçük değil')", "solution": "else: print('Küçük değil')", "msg": "Şart yanlışsa (else) çalışacak bloğu tamamla.", "hint": "else: yazmalısın.", "output": "Küçük değil"},
            {"task": "notu = 60\nif notu < 50: pass\n___ notu > 50: print('Geçti')", "solution": "elif notu > 50: print('Geçti')", "msg": "Birden fazla şartı kontrol etmek için **elif** kullan.", "hint": "elif yaz ve şartı tamamla.", "output": "Geçti"},
            {"task": "if 1==1 ___ 2==2: print('Ok')", "solution": "if 1==1 and 2==2: print('Ok')", "msg": "İki şartın da doğru olmasını bekleyen mantıksal operatörü yaz.", "hint": "and (ve) operatörünü kullan.", "output": "Ok"}
        ]
    },
    {
        "module_title": "5. Listeler: Veri Gruplama",
        "intro": "Listeler, birden fazla veriyi tek bir sepette tutmamıza yarar. Saymaya her zaman 0'dan başlarız!",
        "exercises": [
            {"task": "meyveler = [___, 'Elma']", "solution": "meyveler = ['Muz', 'Elma']", "msg": "Listenin ilk elemanına 'Muz' ekle.", "hint": "Tırnak içinde Muz yaz.", "output": None},
            {"task": "print(meyveler[___])", "solution": "print(meyveler[0])", "msg": "Listenin ilk elemanına (0. indeks) eriş.", "hint": "Sadece 0 yaz.", "output": "Muz"},
            {"task": "meyveler.___('Çilek')", "solution": "meyveler.append('Çilek')", "msg": "Listeye yeni bir eleman ekleme metodunu yaz.", "hint": "append metodunu kullan.", "output": None},
            {"task": "meyveler.pop(___)", "solution": "meyveler.pop(0)", "msg": "Listenin ilk elemanını sil.", "hint": "Parantez içine 0 yaz.", "output": None},
            {"task": "print(___(meyveler))", "solution": "print(len(meyveler))", "msg": "Listenin toplam kaç elemanlı olduğunu bul.", "hint": "len() fonksiyonunu kullan.", "output": "2"}
        ]
    },
    {
        "module_title": "6. Döngüler: for",
        "intro": "Döngüler, aynı işlemi defalarca yapmamızı sağlayan otomasyon araçlarıdır.",
        "exercises": [
            {"task": "for i in ___(5): print(i)", "solution": "for i in range(5): print(i)", "msg": "0'dan 4'e kadar sayı üreten fonksiyonu yaz.", "hint": "range kullanmalısın.", "output": "0\n1\n2\n3\n4"},
            {"task": "for harf ___ 'Pito': print(harf)", "solution": "for harf in 'Pito': print(harf)", "msg": "Kelimedeki harfleri gezen döngüdeki eksik kelimeyi yaz.", "hint": "in kelimesini ekle.", "output": "P\ni\nt\no"},
            {"task": "for i in range(3): ___('Pito')", "solution": "for i in range(3): print('Pito')", "msg": "Ekrana 3 kez 'Pito' yazdır.", "hint": "print fonksiyonunu ekle.", "output": "Pito\nPito\nPito"},
            {"task": "sayilar = [1, 2]\nfor x in sayilar: print(x ___ 10)", "solution": "for x in sayilar: print(x * 10)", "msg": "Listedeki her sayıyı 10 ile çarparak yazdır.", "hint": "Çarpma (*) operatörünü koy.", "output": "10\n20"},
            {"task": "for i in range(5):\n if i == 2: ___\n print(i)", "solution": "if i == 2: break", "msg": "Döngü i değeri 2 olduğunda tamamen dursun.", "hint": "break komutunu kullan.", "output": "0\n1"}
        ]
    },
    {
        "module_title": "7. Döngüler: while",
        "intro": "While döngüsü, bir şart doğru olduğu sürece çalışmaya devam eder.",
        "exercises": [
            {"task": "sayac = 0\n___ sayac < 3:\n print(sayac)\n sayac += 1", "solution": "while sayac < 3:", "msg": "Sayaç 3'ten küçük olduğu sürece dönen döngüyü başlat.", "hint": "while kelimesini yaz.", "output": "0\n1\n2"},
            {"task": "while True:\n print('Tek sefer')\n ___", "solution": "break", "msg": "Sonsuz döngüyü tek seferde durdur.", "hint": "break yaz.", "output": "Tek sefer"},
            {"task": "i = 0\nwhile i < 2:\n ___ += 1", "solution": "i += 1", "msg": "Döngünün sonsuza girmemesi için **i** değişkenini artır.", "hint": "i harfini yaz.", "output": None},
            {"task": "while 1 ___ 2: print('Asla çalışmaz'); break", "solution": "while 1 == 2:", "msg": "Döngü şartını '1 eşit değildir 2' yerine '1 eşittir 2' yaparak hiç çalışmamasını sağla.", "hint": "== operatörünü koy.", "output": None},
            {"task": "i = 0\nwhile i < 3:\n i += 1\n if i == 1: ___\n print(i)", "solution": "continue", "msg": "i değeri 1 olduğunda yazdırmayı atlayıp döngü başına dön.", "hint": "continue komutunu kullan.", "output": "2\n3"}
        ]
    },
    {
        "module_title": "8. Fonksiyonlar ve Final",
        "intro": "Fonksiyonlar, karmaşık işlemleri bir isim altında toplayıp ihtiyaç duyduğumuzda çağırmamızı sağlar.",
        "exercises": [
            {"task": "___ selamla(): print('Merhaba')", "solution": "def selamla(): print('Merhaba')", "msg": "Bir fonksiyon tanımlamak için gereken kelimeyi yaz.", "hint": "def yazmalısın.", "output": None},
            {"task": "def topla(a, b):\n ___ a + b", "solution": "return a + b", "msg": "Fonksiyonun sonucunu dışarıya aktar.", "hint": "return kelimesini kullan.", "output": None},
            {"task": "def hi(): print('Selam')\n___()", "solution": "hi()", "msg": "Tanımlanan 'hi' fonksiyonunu çalıştır (çağır).", "hint": "Fonksiyon ismini ve parantezleri yaz.", "output": "Selam"},
            {"task": "import ___", "solution": "import math", "msg": "Matematik kütüphanesini (math) projene dahil et.", "hint": "math yaz.", "output": None},
            {"task": "print(math.sqrt(___))", "solution": "print(math.sqrt(16))", "msg": "16 sayısının karekökünü hesapla.", "hint": "Parantez içine 16 yaz.", "output": "4.0"}
        ]
    }
]

# --- 4. SESSION STATE YÖNETİMİ ---
if 'user' not in st.session_state:
    st.session_state.user = None
    st.session_state.errors = 0
    st.session_state.score_pool = 20
    st.session_state.is_completed = False
    st.session_state.feedback_msg = ""
    st.session_state.feedback_type = ""

# --- 5. LİDERLİK TABLOSU ---
def show_leaderboard():
    try:
        df = pd.read_csv("https://docs.google.com/spreadsheets/d/1lat8rO2qm9QnzEUYlzC_fypG3cRkGlJfSfTtwNvs318/export?format=csv")
        st.sidebar.markdown("### 🏆 Okul Liderliği")
        for _, row in df.sort_values(by="Puan", ascending=False).head(10).iterrows():
            st.sidebar.markdown(f'<div class="leaderboard-card"><b>{row["Öğrencinin Adı"]}</b><br>{row["Rütbe"]} | {row["Puan"]} P</div>', unsafe_allow_html=True)
    except: st.sidebar.info("Sıralama yükleniyor...")

# --- 6. GİRİŞ EKRANI ---
if st.session_state.user is None:
    c1, c2 = st.columns([2, 1])
    with c1:
        render_gif("pito_merhaba")
        st.title("Pito Python Akademi")
        okul_no = st.text_input("Okul Numaranı Gir:", placeholder="Örn: 123")
        if okul_no:
            # Okul numarası kontrolü ve kayıt mantığı buraya gelir
            st.session_state.user = {"Okul No": okul_no, "Ad": "Genç Yazılımcı", "Modül": 1, "Egzersiz": 1, "Puan": 0}
            st.rerun()
    with c2: show_leaderboard()

# --- 7. AKADEMİ PANELİ ---
else:
    u = st.session_state.user
    m_idx, e_idx = int(u["Modül"]) - 1, int(u["Egzersiz"]) - 1
    curr_ex = training_data[m_idx]["exercises"][e_idx]
    
    st.progress(((m_idx * 5) + e_idx) / 40)

    mc, sc = st.columns([2.5, 1])
    with mc:
        # Pito Duygu Durumu
        if st.session_state.is_completed:
            render_gif("pito_dusunuyor" if st.session_state.errors >= 4 else "pito_basari")
        elif st.session_state.errors > 0: render_gif("pito_hata")
        else: render_gif("pito_dusunuyor")

        st.markdown(f'<div class="pito-note"><b>🐍 Pito\'nun Notu:</b><br>{curr_ex["msg"]}</div>', unsafe_allow_html=True)
        
        # Geri bildirim mesajları
        if st.session_state.feedback_msg:
            if st.session_state.feedback_type == "error": st.error(st.session_state.feedback_msg)
            elif st.session_state.feedback_type == "warning": st.warning(st.session_state.feedback_msg)

        # CODESIGNAL PANELİ
        st.markdown('<div class="editor-container"><div class="editor-header"><div class="editor-tab">solution.py</div></div></div>', unsafe_allow_html=True)
        ans = st.text_area("Kod Girişi:", value=curr_ex['task'], height=130, key=f"ex_{m_idx}_{e_idx}", disabled=st.session_state.is_completed, label_visibility="collapsed")

        if not st.session_state.is_completed:
            if st.button("Kontrol Et"):
                # Karşılaştırma Mantığı
                clean_ans = re.sub(r"\s+", "", ans).replace("'", '"')
                clean_sol = re.sub(r"\s+", "", curr_ex["solution"]).replace("'", '"')
                
                if clean_ans == clean_sol:
                    st.session_state.is_completed, st.session_state.feedback_msg = True, ""
                    u["Puan"] += st.session_state.score_pool
                    st.rerun()
                else:
                    st.session_state.errors += 1
                    st.session_state.score_pool = max(0, st.session_state.score_pool - 5)
                    if st.session_state.errors < 3:
                        st.session_state.feedback_msg, st.session_state.feedback_type = f"❌ Yanlış! {st.session_state.errors}. hatan. -5 Puan.", "error"
                    elif st.session_state.errors == 3:
                        st.session_state.feedback_msg, st.session_state.feedback_type = f"💡 İpucu: {curr_ex['hint']}", "warning"
                    elif st.session_state.errors >= 4:
                        st.session_state.is_completed, st.session_state.feedback_msg, st.session_state.feedback_type = True, "🚨 4 hata yaptın. Çözümü incele!", "error"
                    st.rerun()

        if st.session_state.is_completed:
            st.divider()
            if st.session_state.errors >= 4:
                st.info(f"✅ Doğru Çözüm: `{curr_ex['solution']}`")
            else:
                st.success("✨ Tebrikler! Doğru cevap.")
                # ÇIKTI KONTROLÜ: Sadece print içerenler çıktı verir
                if curr_ex["output"]:
                    st.code(f"Kod Çıktısı:\n{curr_ex['output']}")

            if st.button("Sonraki Adıma Geç ➡️"):
                if e_idx < 4: u["Egzersiz"] += 1
                else: u["Modül"] += 1; u["Egzersiz"] = 1
                st.session_state.is_completed, st.session_state.errors, st.session_state.score_pool, st.session_state.feedback_msg = False, 0, 20, ""
                st.rerun()

    with sc:
        st.subheader(f"👤 {u['Ad']}")
        st.metric("Puan", u["Puan"]); st.write(f"**Rütbe:** {get_rank(u['Puan'])}")
        st.divider(); show_leaderboard()
