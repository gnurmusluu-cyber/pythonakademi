import streamlit as st
from streamlit_ace import st_ace
import sys
from io import StringIO
import pandas as pd
from datetime import datetime
from streamlit_gsheets import GSheetsConnection
import os

# --- 1. TASARIM VE SAYFA AYARLARI ---
st.set_page_config(layout="wide", page_title="Pito Python Akademi", initial_sidebar_state="collapsed")

SINIFLAR = ["9-A", "9-B", "10-A", "10-B", "11-A", "11-B"]

RUTBELER = [
    "🥚 Yeni Başlayan", "🌱 Python Çırağı", "🪵 Kod Oduncusu", "🧱 Mantık Mimarı", 
    "🌀 Döngü Ustası", "📋 Liste Uzmanı", "📦 Fonksiyon Kaptanı", "🤖 OOP Robotu", "🏆 Python Kahramanı"
]

st.markdown("""
    <style>
    header {visibility: hidden;}
    .main .block-container {padding-top: 1rem;}
    .pito-bubble {
        position: relative; background: #f0f2f6; border: 2px solid #3a7bd5;
        border-radius: 15px; padding: 20px; margin-bottom: 20px; color: #1e1e1e;
        font-weight: 500; font-size: 1.1rem; box-shadow: 4px 4px 15px rgba(0,0,0,0.1);
    }
    .pito-bubble:after {
        content: ''; position: absolute; bottom: -20px; left: 40px;
        border-width: 20px 20px 0; border-style: solid; border-color: #3a7bd5 transparent;
    }
    .leaderboard-card {
        background: linear-gradient(135deg, #1e1e1e, #2d2d2d);
        border: 1px solid #444; border-radius: 12px; padding: 10px; margin-bottom: 8px; color: white;
    }
    .champion-card {
        background: linear-gradient(135deg, #FFD700, #FFA500);
        border: 2px solid #FFF; border-radius: 15px; padding: 15px; margin-top: 20px; color: #1e1e1e;
        text-align: center; font-weight: bold; box-shadow: 0 4px 15px rgba(255, 215, 0, 0.4);
    }
    .stButton > button {
        width: 100%; border-radius: 12px; height: 3.5em;
        background: linear-gradient(45deg, #3a7bd5, #00d2ff) !important;
        color: white !important; font-weight: bold; border: none;
    }
    .restart-btn > button { background: linear-gradient(45deg, #e53935, #e35d5b) !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. VERİ TABANI YÖNETİMİ ---
SHEET_URL = "https://docs.google.com/spreadsheets/d/1lat8rO2qm9QnzEUYlzC_fypG3cRkGlJfSfTtwNvs318/edit#gid=0"
conn = st.connection("gsheets", type=GSheetsConnection)

def get_db(use_cache=True):
    try:
        df = conn.read(spreadsheet=SHEET_URL, ttl=60 if use_cache else 0)
        if df is None or df.empty:
            return pd.DataFrame(columns=["Okul No", "Öğrencinin Adı", "Sınıf", "Puan", "Rütbe", "Tamamlanan Modüller", "Mevcut Modül", "Mevcut Egzersiz", "Tarih"])
        df["Okul No"] = df["Okul No"].astype(str).str.split('.').str[0].str.strip()
        df = df[df["Okul No"].str.isdigit()] 
        df["Puan"] = pd.to_numeric(df["Puan"], errors='coerce').fillna(0).astype(int)
        return df.dropna(subset=["Okul No"])
    except:
        return pd.DataFrame(columns=["Okul No", "Öğrencinin Adı", "Sınıf", "Puan", "Rütbe", "Tamamlanan Modüller", "Mevcut Modül", "Mevcut Egzersiz", "Tarih"])

def force_save():
    try:
        no = str(st.session_state.student_no).strip()
        score = int(st.session_state.total_score)
        df_all = get_db(use_cache=False)
        if df_all.empty and st.session_state.db_module > 0: return 
        df_clean = df_all[df_all["Okul No"] != no]
        progress = ",".join(["1" if m else "0" for m in st.session_state.completed_modules])
        rank = RUTBELER[sum(st.session_state.completed_modules)]
        new_row = pd.DataFrame([[no, st.session_state.student_name, st.session_state.student_class, score, rank, progress, st.session_state.db_module, st.session_state.db_exercise, datetime.now().strftime("%H:%M:%S")]], 
                               columns=["Okul No", "Öğrencinin Adı", "Sınıf", "Puan", "Rütbe", "Tamamlanan Modüller", "Mevcut Modül", "Mevcut Egzersiz", "Tarih"])
        conn.update(spreadsheet=SHEET_URL, data=pd.concat([df_clean, new_row], ignore_index=True))
    except: pass

# --- 3. SESSION STATE ---
if 'is_logged_in' not in st.session_state:
    for k, v in {'student_name': "", 'student_no': "", 'student_class': "", 'completed_modules': [False]*8, 
                  'current_module': 0, 'current_exercise': 0, 'exercise_passed': False, 'total_score': 0, 
                  'scored_exercises': set(), 'db_module': 0, 'db_exercise': 0, 'is_logged_in': False, 
                  'current_potential_score': 20, 'celebrated': False, 'rejected_user': False}.items():
        st.session_state[k] = v

PITO_IMG = "assets/pito.png"

# --- 4. GİRİŞ EKRANI ---
if not st.session_state.is_logged_in:
    st.markdown("<br>", unsafe_allow_html=True)
    _, col_mid, _ = st.columns([1, 2, 1])
    with col_mid:
        st.markdown('<div class="pito-bubble">Merhaba! Ben <b>Pito</b>. Python Dünyası\'na hoş geldin.</div>', unsafe_allow_html=True)
        st.image(PITO_IMG if os.path.exists(PITO_IMG) else "https://img.icons8.com/fluency/180/robot-viewer.png", width=180)
        
        if st.session_state.rejected_user:
            st.warning("⚠️ O halde kendi okul numaranı gir!")

        in_no_raw = st.text_input("Okul Numaran (Sadece Rakam):", key="login_field").strip()
        
        if in_no_raw and not in_no_raw.isdigit():
            st.error("⚠️ Hata: Okul numarası sadece rakamlardan oluşmalıdır!")
        elif in_no_raw:
            if st.session_state.rejected_user:
                st.session_state.rejected_user = False
                
            df = get_db(use_cache=False)
            user_data = df[df["Okul No"] == in_no_raw]
            
            if not user_data.empty:
                row = user_data.iloc[0]
                st.info(f"🔍 Bu numara **{row['Öğrencinin Adı']}** adına kayıtlı.")
                st.markdown("### Sen bu kişi misin? 🤔")
                
                c1, c2 = st.columns(2)
                with c1:
                    if st.button("✅ Evet, Benim"):
                        m_v, e_v = int(row['Mevcut Modül']), int(row['Mevcut Egzersiz'])
                        st.session_state.update({'student_no': str(row["Okul No"]), 'student_name': row["Öğrencinin Adı"], 'student_class': row["Sınıf"], 'total_score': int(row["Puan"]), 'db_module': m_v, 'db_exercise': e_v, 'current_module': min(m_v, 7), 'current_exercise': e_v, 'completed_modules': [True if x == "1" else False for x in str(row["Tamamlanan Modüller"]).split(",")], 'is_logged_in': True})
                        st.rerun()
                with c2:
                    if st.button("❌ Hayır, Ben Değilim"):
                        st.session_state.rejected_user = True
                        if "login_field" in st.session_state:
                            del st.session_state["login_field"]
                        st.rerun()
            else:
                st.info("Yeni bir maceracı! Bilgilerini tamamla:")
                in_name = st.text_input("Adın Soyadın:", key="new_name")
                in_class = st.selectbox("Sınıfın:", SINIFLAR, key="new_class")
                if st.button("Maceraya Başla! ✨"):
                    if in_name.strip():
                        st.session_state.update({'student_no': in_no_raw, 'student_name': in_name.strip(), 'student_class': in_class, 'is_logged_in': True})
                        force_save(); st.rerun()
    st.stop()

# --- 5. ZENGİNLEŞTİRİLMİŞ EĞİTİCİ MÜFREDAT ---
training_data = [
    {"module_title": "1. Giriş ve Çıktı İşlemleri", "exercises": [
        {"msg": "Python ile program yazarken bilgisayarın bize cevap vermesini sağlamak için **print()** fonksiyonunu kullanırız. Parantez içine yazdığımız metinsel ifadeleri Python'ın anlayabilmesi için mutlaka **tek tırnak (' ')** veya **çift tırnak (\" \")** içine almalısın. Hadi dene: Ekrana **'Merhaba Pito'** yazdır.", "task": "print('___')", "check": lambda c, o: "Merhaba Pito" in o, "solution": "print('Merhaba Pito')"},
        {"msg": "Python'da matematiksel değer olan sayıları ekrana yazdırırken tırnak işareti kullanmamıza gerek yoktur. Çünkü Python sayıları doğrudan bir değer olarak tanır. Şimdi tırnak kullanmadan sadece **100** sayısını ekrana yazdır.", "task": "print(___)", "check": lambda c, o: "100" in o, "solution": "print(100)"},
        {"msg": "Aynı `print()` fonksiyonu içinde farklı türdeki verileri yan yana yazdırmak için aralarına **virgül (,)** koyarız. Virgül, Python'a 'bu başka bir veri' der ve araya otomatik olarak bir boşluk bırakır. Hadi dene: **'Puan:'** metni ile **100** sayısını virgül kullanarak yan yana yazdır.", "task": "print('Puan:', ___)", "check": lambda c, o: "100" in o, "solution": "print('Puan:', 100)"},
        {"msg": "Kod yazarken kendimize veya diğer programcılara notlar bırakmak isteriz. **# (Diyez)** işaretiyle başlayan satırlar Python tarafından 'yorum' olarak kabul edilir ve asla çalıştırılmaz. Hadi dene: Satırın başına diyez koyarak bir **yorum satırı** oluştur.", "task": "___ Bu bir yorumdur", "check": lambda c, o: "#" in c, "solution": "# Kodlarımı buraya yazıyorum"},
        {"msg": "Yazıları alt alta yazdırmak için metin içine **'\\n'** kaçış karakterini ekleriz. Bu, klavyede Enter'a basmakla aynı etkiyi yaratır. Hadi dene: Tek print içinde **'Üst'** ve **'Alt'** kelimelerini araya **\\n** koyarak farklı satırlarda yazdır.", "task": "print('Üst' + '___' + 'Alt')", "check": lambda c, o: "\n" in o, "solution": "print('Üst' + '\\n' + 'Alt')"}
    ]},
    {"module_title": "2. Değişkenler: Bilgi Depolama", "exercises": [
        {"msg": "Değişkenler, bilgileri daha sonra kullanmak üzere sakladığımız isimli kutular gibidir. `=` işareti bir atama operatörüdür; sağdaki değeri soldaki ismin içine koyar. Hadi dene: **yas** adında bir kutu oluştur ve içine **15** değerini koyup ekrana yazdır.", "task": "yas = ___\nprint(yas)", "check": lambda c, o: "15" in o, "solution": "yas = 15\nprint(yas)"},
        {"msg": "Değişkenlere sadece sayı değil, metin de atayabiliriz. Metin atarken tırnak işaretlerini asla unutmamalıyız. Hadi dene: **isim** adında bir değişken oluştur, içine **'Pito'** değerini ata ve ekrana yazdır.", "task": "isim = '___'\nprint(isim)", "check": lambda c, o: "Pito" in o, "solution": "isim = 'Pito'\nprint(isim)"},
        {"msg": "**input()** fonksiyonu programı durdurur ve kullanıcıdan bir bilgi yazmasını bekler. Kullanıcı Enter'a bastığında yazılan bilgi bir değişkene aktarılır. Hadi dene: **'Adın: '** sorusuyla kullanıcıdan ismini al ve ekrana yazdır.", "task": "ad = ___('Adın: ')\nprint(ad)", "check": lambda c, o: "input" in c, "solution": "ad = input('Adın: ')\nprint(ad)"},
        {"msg": "Bazen sayıları metne dönüştürerek bir yazı içinde kullanmak isteriz. **str()** fonksiyonu sayısal veriyi metne (string) çevirir. Hadi dene: **s = 10** sayı değişkenini metne çevirip print ile ekrana yazdır.", "task": "s = 10\nprint(___(s))", "check": lambda c, o: "str" in c, "solution": "s = 10\nprint(str(s))"},
        {"msg": "Kullanıcıdan gelen her bilgi Python tarafından metin olarak görülür. Matematiksel bir işlem (toplama gibi) yapacaksan onu **int()** ile tam sayıya çevirmelisin. Hadi dene: **n** değişkenine bir girdi al ve bunu tam sayıya çevirip üzerine 1 ekle.", "task": "n = ___(___('S: '))\nprint(n + 1)", "check": lambda c, o: "int" in c and "input" in c, "solution": "n = int(input('10'))\nprint(n + 1)"}
    ]},
    {"module_title": "3. Karar Yapıları: Programın Düşünmesi", "exercises": [
        {"msg": "Programın bir koşula göre karar vermesini istiyorsak `if` (eğer) yapısını kullanırız. İki değerin eşit olup olmadığını kontrol etmek için **'=='** (çift eşittir) operatörü kullanılır. Hadi dene: Eğer 10 sayısı **10'a eşitse** ekrana 'X' yazdır.", "task": "if 10 ___ 10: print('X')", "check": lambda c, o: "==" in c, "solution": "if 10 == 10: print('X')"},
        {"msg": "Eğer `if` içindeki şart gerçekleşmiyorsa, program otomatik olarak **'else:'** (değilse) bloğuna gider. Hadi dene: 5 sayısı 10'dan büyük değilse ekrana **'Y'** yazdıracak bir `else` bloğu kur.", "task": "if 5>10: pass\n___: print('Y')", "check": lambda c, o: "else" in c, "solution": "if 5>10: pass\nelse: print('Y')"},
        {"msg": "Büyük veya eşittir durumunu kontrol etmek için **'>='** operatörü kullanılır. Hadi dene: Eğer 5 sayısı **5'ten büyük veya eşitse** ekrana 'Z' yazdır.", "task": "if 5 ___ 5: print('Z')", "check": lambda c, o: ">=" in c, "solution": "if 5 >= 5: print('Z')"},
        {"msg": "**'and'** (ve) anahtar kelimesi ile iki farklı koşulun da aynı anda doğru olması istenir. Hadi dene: Eğer 1 eşit 1 **ve** 2 eşit 2 ise ekrana 'OK' yazdır.", "task": "if 1==1 ___ 2==2: print('OK')", "check": lambda c, o: "and" in c, "solution": "if 1==1 and 2==2: print('OK')"},
        {"msg": "**'elif'**, ilk şart yanlışsa devreye giren 'diğer eğer' şartıdır. Hadi dene: İlk şart yanlış olsa bile **5==5 ise** ekrana 'A' yazdır.", "task": "if 5>10: pass\n___ 5==5: print('A')", "check": lambda c, o: "elif" in c, "solution": "if 5>10: pass\nelif 5==5: print('A')"}
    ]},
    {"module_title": "4. Döngüler: Tekrarlanan İşler", "exercises": [
        {"msg": "**'for'** döngüsü ve **range()** fonksiyonu bir işlemi belirli sayıda tekrarlatır. `range(3)` ifadesi döngünün 3 tur dönmesini sağlar. Hadi dene: 3 kez ekrana 'X' yazdıran döngüyü kur.", "task": "for i in ___(3): print('X')", "check": lambda c, o: o.count("X")==3, "solution": "for i in range(3): print('X')"},
        {"msg": "**'while'** döngüsü, yanındaki koşul 'True' (doğru) olduğu sürece durmadan çalışır. Hadi dene: **i<1** şartı doğruyken ekrana 'Y' yazdıran ve sayacı artıran döngüyü kur.", "task": "i=0\n___ i<1: print('Y'); i+=1", "check": lambda c, o: "while" in c, "solution": "i=0\nwhile i<1: print('Y'); i+=1"},
        {"msg": "**'break'** komutu bir döngüyü aniden bitirmek (kırmak) için kullanılır. Hadi dene: Döngü dönerken i değeri 1 olduğunda döngüyü **bitir**.", "task": "for i in range(3):\n if i==1: ___\n print(i)", "check": lambda c, o: "break" in c, "solution": "for i in range(3):\n    if i==1: break\n    print(i)"},
        {"msg": "**'continue'** o anki adımı pas geçer ve döngünün en başına döner. Hadi dene: i değeri 1 olduğunda o adımı **atla**.", "task": "for i in range(3):\n if i==1: ___\n print(i)", "check": lambda c, o: "continue" in c, "solution": "for i in range(3):\n    if i==1: continue\n    print(i)"},
        {"msg": "Döngü sayacı olan **i** değişkeni her turda güncellenir (0, 1, 2...). Bu sayacı ekrana yazdırarak tur numarasını görebilirsin. Hadi dene: Sayacı ekrana yazdır.", "task": "for i in range(2): print(___)", "check": lambda c, o: "1" in o, "solution": "for i in range(2): print(i)"}
    ]},
    {"module_title": "5. Listeler: Veri Grupları", "exercises": [
        {"msg": "Listeler birden fazla veriyi tek bir paket içinde saklar ve `[]` parantezleriyle oluşturulur. Hadi dene: İçinde **10** ve **20** sayıları olan bir liste oluştur.", "task": "L = [___, 20]", "check": lambda c, o: "10" in c, "solution": "L=[10, 20]\nprint(L)"},
        {"msg": "Python'da liste sayımı **0'dan başlar!** Listenin ilk elemanına ulaşmak için `[0]` indeksini kullanırız. Hadi dene: **L** listesinin **ilk elemanına** eriş ve yazdır.", "task": "L=[5,6]\nprint(L[___])", "check": lambda c, o: "5" in o, "solution": "L=[5,6]\nprint(L[0])"},
        {"msg": "**len()** fonksiyonu listenin boyunu, yani içinde kaç tane eleman olduğunu söyler. Hadi dene: L listesinin eleman sayısını ekrana yazdır.", "task": "L=[1,2]\nprint(___(L))", "check": lambda c, o: "2" in o, "solution": "L=[1,2]\nprint(len(L))"},
        {"msg": "**append()** metodu listenin sonuna yeni bir vagon ekler. Hadi dene: Mevcut listeye **30** sayısını eklemek için boşluğu doldur.", "task": "L=[10]\nL.___(___)\nprint(L)", "check": lambda c, o: "30" in o, "solution": "L=[10]\nL.append(30)\nprint(L)"},
        {"msg": "**pop()** metodu listenin en sonundaki elemanı tutup dışarı atar (siler). Hadi dene: Listeden son elemanı **sil**.", "task": "L=[1,2]\nL.___()\nprint(L)", "check": lambda c, o: "1" in o, "solution": "L=[1,2]\nL.pop()\nprint(L)"}
    ]},
    {"module_title": "6. Fonksiyonlar ve Veri Türleri", "exercises": [
        {"msg": "**Fonksiyonlar**, karmaşık bir işi bir isim altında toplayıp tekrar tekrar kullanmamızı sağlar. 'def' kelimesiyle tanımlanır. Hadi dene: **f** isminde bir fonksiyon tanımla.", "task": "___ f(): print('X')", "check": lambda c, o: "def" in c, "solution": "def f(): print('X')"},
        {"msg": "**Tuple (Demet)** listelere benzer ama bir kez oluşturulduktan sonra **değiştirilemez**. Listelerde `[]`, demetlerde **`()`** kullanılır. Hadi dene: Bir demet oluştur.", "task": "t = (___, 2)\nprint(t)", "check": lambda c, o: "1" in c, "solution": "t = (1, 2)\nprint(t)"},
        {"msg": "**Sözlükler (Dict)** 'Anahtar: Değer' ikilisiyle çalışır (örneğin kelime ve anlamı gibi). Hadi dene: **'ad'** anahtarına **'Pito'** değerini ata.", "task": "d = {'ad': '___'}\nprint(d['ad'])", "check": lambda c, o: "Pito" in c, "solution": "d = {'ad': 'Pito'}\nprint(d['ad'])"},
        {"msg": "**keys()** metodu sözlükteki tüm anahtar etiketlerini bize getirir. Hadi dene: d sözlüğündeki anahtarları yazdır.", "task": "d={'a':1}\nprint(d.___())", "check": lambda c, o: "keys" in c, "solution": "d={'a':1}\nprint(d.keys())"},
        {"msg": "**Set (Küme)** her elemandan sadece bir tane barındırır, tekrar edenleri siler. Hadi dene: Tekrarlayan sayıları olan bir küme oluştur.", "task": "s = {1, 2, ___}\nprint(s)", "check": lambda c, o: "1" in c, "solution": "s = {1, 2, 1}\nprint(s)"}
    ]},
    {"module_title": "7. Nesne Tabanlı Programlama (OOP)", "exercises": [
        {"msg": "**Sınıf (Class)**, nesnelerin nasıl olacağını belirleyen bir taslak veya fabrika kalıbıdır. **class** yazarak **Robot** sınıfını oluştur.", "task": "___ Robot: pass", "check": lambda c, o: "class" in c, "solution": "class Robot: pass"},
        {"msg": "**Nesne (Object)**, sınıftan (taslaktan) üretilen gerçek ve canlı örnektir. **R** sınıfını kullanarak **p** adında gerçek bir nesne üret.", "task": "class R: pass\np = ___()", "check": lambda c, o: "R()" in c, "solution": "class R: pass\np = R()"},
        {"msg": "Nitelik (Attribute), nesnenin rengi veya hızı gibi sahip olduğu bilgilerdir. Robota **renk** niteliği olarak **'Mavi'** ata.", "task": "class R: pass\np=R()\np.___ = 'Mavi'\nprint(p.renk)", "check": lambda c, o: "renk" in c, "solution": "class R: pass\np=R()\np.renk = 'Mavi'\nprint(p.renk)"},
        {"msg": "**Metot**, bir sınıfın içindeki fonksiyonlara denir. İlk parametresi her zaman **self** (kendisi) olmalıdır. Robota **ses** metodu ekle.", "task": "class R:\n def ___(self):\n  print('Bip!')", "check": lambda c, o: "ses" in c, "solution": "class R:\n    def ses(self):\n        print('Bip!')"},
        {"msg": "Bir metodu çalıştırmak için **nesne.metot()** kuralı uygulanır. r nesnesi üzerinden **s** metodunu çağır (çalıştır).", "task": "class R:\n def s(self): print('X')\nr=R()\nr.___()", "check": lambda c, o: "s()" in c, "solution": "class R:\n    def s(self):\n        print('X')\nr=R()\nr.s()"}
    ]},
    {"module_title": "8. Dosya Yönetimi: Kalıcılık", "exercises": [
        {"msg": "**open()** ile dosya açılır. **'w'** (write) kipi dosyanın içine yazı yazmak içindir; dosya yoksa oluşturur.", "task": "dosya = ___('n.txt', '___')", "check": lambda c, o: "open" in c and "'w'" in c, "solution": "dosya = open('n.txt', 'w')\nprint('Açıldı.')"},
        {"msg": "**write()** komutuyla dosyanın içine yazı yazılır. Hadi dene: Dosyaya **'Pito'** yazdır ve dosyayı kapatmayı unutma.", "task": "f = open('t.txt', 'w'); f.___('Pito'); f.close()", "check": lambda c, o: "write" in c, "solution": "f = open('t.txt', 'w'); f.write('Pito'); f.close()"},
        {"msg": "**'r'** (read) kipi dosyadaki bilgileri sadece **okumak** için kullanılır. t.txt dosyasını okuma modunda aç.", "task": "f = open('t.txt', '___')", "check": lambda c, o: "'r'" in c, "solution": "f = open('t.txt', 'r'); f.close()"},
        {"msg": "**read()** komutu dosyadaki tüm metni tek parça halinde okur. Hadi dene: Dosyayı oku ve print ile ekrana yazdır.", "task": "f = open('t.txt', 'r')\nprint(f.___())\nf.close()", "check": lambda c, o: "read" in c, "solution": "f = open('t.txt', 'w'); f.write('Pito Akademi'); f.close(); f = open('t.txt', 'r'); print(f.read()); f.close()"},
        {"msg": "Açılan dosyalar bilgisayarın hafızasında yer tutar. İş bitince mutlaka **close()** ile kapatılmalıdır. Hadi dene: Dosyayı kapat.", "task": "f = open('t.txt', 'r')\nf.___()", "check": lambda c, o: "close" in c, "solution": "f = open('t.txt', 'r'); f.close()"}
    ]}
]

# --- 6. ARA YÜZ DÜZENİ ---
col_main, col_side = st.columns([3, 1])

completed_count = sum(st.session_state.completed_modules)
student_rank = RUTBELER[completed_count]

with col_main:
    st.markdown(f"#### 👋 {student_rank} {st.session_state.student_name} | ⭐ Puan: {int(st.session_state.total_score)}")
    
    if st.session_state.db_module >= 8:
        if not st.session_state.celebrated:
            st.balloons(); st.session_state.celebrated = True
        st.success("### 🎉 Tebrikler! Eğitimi Başarıyla Tamamladın.")
        st.markdown('<div class="pito-bubble">Python yolculuğunu bitirdin! Aşağıdan modülleri inceleyebilir veya baştan başlayabilirsin.</div>', unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        with c1:
            if st.button("🔄 Eğitimi Tekrar Al (Sıfırla)"):
                st.session_state.update({'db_module': 0, 'db_exercise': 0, 'total_score': 0, 'current_module': 0, 'current_exercise': 0, 'completed_modules': [False]*8, 'scored_exercises': set(), 'celebrated': False})
                force_save(); st.rerun()
        with c2: st.info("Başarın kaydedildi.")
        st.divider(); st.subheader("📖 İnceleme Modu")

    mod_titles = [f"{'✅' if st.session_state.completed_modules[i] else '📖'} Modül {i+1}" for i in range(8)]
    if st.session_state.current_module != st.session_state.db_module and st.session_state.db_module < 8:
        if st.button(f"🔙 Güncel Görevime Dön (Modül {st.session_state.db_module + 1})", use_container_width=True):
            st.session_state.current_module, st.session_state.current_exercise = st.session_state.db_module, st.session_state.db_exercise
            st.rerun()

    sel_mod = st.selectbox("Modül Seç:", mod_titles, index=st.session_state.current_module)
    m_idx = mod_titles.index(sel_mod)
    if m_idx != st.session_state.current_module:
        st.session_state.current_module, st.session_state.current_exercise = m_idx, 0
        st.rerun()

    st.divider()
    e_idx = st.session_state.current_exercise
    curr_ex = training_data[m_idx]["exercises"][e_idx]
    is_locked = (m_idx < st.session_state.db_module) or (st.session_state.db_module >= 8)

    c_img, c_msg = st.columns([1, 4])
    with c_img: st.image(PITO_IMG if os.path.exists(PITO_IMG) else "https://img.icons8.com/fluency/200/robot-viewer.png", width=140)
    with c_msg:
        st.info(f"##### 🗣️ Pito:\n{curr_ex['msg']}")
        st.caption(f"Adım: {e_idx + 1}/5 " + ("🔒 İnceleme Modu" if is_locked else f"🎁 Puan: {st.session_state.current_potential_score}"))

    code = st_ace(value=curr_ex['task'], language="python", theme="dracula", font_size=14, height=200, readonly=is_locked, key=f"ace_{m_idx}_{e_idx}", auto_update=True)

    def run_pito_code(c, user_input=""):
        old_stdout, new_stdout = sys.stdout, StringIO()
        sys.stdout = new_stdout
        if "input(" in c and not user_input:
            sys.stdout = old_stdout
            return "⚠️ Pito Terminali boş! Lütfen terminale bir değer yazıp tekrar deneyin."
        def mocked_input(prompt=""): return str(user_input)
        try:
            safe_code = c.replace("___", "None")
            exec_globals = {"input": mocked_input, "print": print, "int": int, "str": str, "len": len, "open": open}
            exec(safe_code, exec_globals)
            sys.stdout = old_stdout
            return new_stdout.getvalue()
        except ValueError:
            sys.stdout = old_stdout
            return "Hata: Sayı beklenirken hatalı veri girildi veya fonksiyonlar yanlış sırada kullanıldı."
        except Exception as e:
            sys.stdout = old_stdout
            return f"Hata: {e}"

    u_in = ""
    if "input(" in code and not is_locked:
        st.warning("👇 **Pito Terminali:** Aşağıya bir değer yaz ve 'Kontrol Et' butonuna bas!")
        u_in = st.text_input("Giriş yap:", key=f"term_{m_idx}_{e_idx}")

    if is_locked:
        st.subheader("📟 Sonuç (İnceleme Modu)")
        st.code(run_pito_code(curr_ex['solution'], "Örnek Veri") if curr_ex['solution'] else "Hazır.")
    else:
        if st.button("🔍 Kontrol Et", use_container_width=True):
            out = run_pito_code(code, u_in)
            if out.startswith("⚠️") or out.startswith("Hata:"):
                st.error(out)
                if out.startswith("Hata:"): st.session_state.current_potential_score = max(5, st.session_state.current_potential_score - 5)
            else:
                st.subheader("📟 Çıktı")
                st.code(out if out else "Kod çalıştı!")
                if curr_ex['check'](code, out) and "___" not in code:
                    st.session_state.exercise_passed = True
                    if f"{m_idx}_{e_idx}" not in st.session_state.scored_exercises:
                        st.session_state.total_score += st.session_state.current_potential_score
                        st.session_state.scored_exercises.add(f"{m_idx}_{e_idx}")
                        if st.session_state.db_exercise < 4: st.session_state.db_exercise += 1
                        else:
                            st.session_state.db_module += 1; st.session_state.db_exercise = 0
                            st.session_state.completed_modules[m_idx] = True
                        force_save()
                    st.success("Tebrikler! ✅")
                else:
                    st.session_state.current_potential_score = max(5, st.session_state.current_potential_score - 5)
                    st.warning("Hatalı!")

    c_back, c_next = st.columns(2)
    with c_back:
        if is_locked and e_idx > 0:
            if st.button("⬅️ Önceki Adım"): st.session_state.current_exercise -= 1; st.rerun()
    with c_next:
        if st.session_state.exercise_passed or is_locked:
            if e_idx < 4:
                if st.button("➡️ Sonraki Adıma Geç"):
                    st.session_state.current_exercise += 1; st.session_state.exercise_passed = False; st.rerun()
            else:
                if st.button("🏆 Modülü Bitir"):
                    if st.session_state.current_module < 7:
                        st.session_state.current_module += 1; st.session_state.current_exercise = 0; st.rerun()
                    else:
                        st.session_state.db_module = 8; st.session_state.completed_modules[7] = True
                        force_save(); st.rerun()

with col_side:
    st.markdown(f"### 🏆 Liderlik Tablosu")
    df_lb = get_db(use_cache=True)
    tab_class, tab_school = st.tabs(["👥 Sınıfım", "🏫 Okul"])
    with tab_class:
        df_class_lb = df_lb[df_lb["Sınıf"] == st.session_state.student_class]
        if not df_class_lb.empty:
            df_sort = df_class_lb.sort_values(by="Puan", ascending=False).drop_duplicates(subset=["Okul No"]).head(10)
            for i, (_, r) in enumerate(df_sort.iterrows()):
                medal = "🥇" if i == 0 else "🥈" if i == 1 else "🥉" if i == 2 else "⭐"
                st.markdown(f'<div class="leaderboard-card"><b>{medal} {r["Rütbe"]} {r["Öğrencinin Adı"]} ({r["Sınıf"]})</b><br>{int(r["Puan"])} Puan</div>', unsafe_allow_html=True)
        else: st.info("Henüz veri yok...")
    with tab_school:
        if not df_lb.empty:
            df_school_sort = df_lb.sort_values(by="Puan", ascending=False).drop_duplicates(subset=["Okul No"]).head(10)
            for i, (_, r) in enumerate(df_school_sort.iterrows()):
                medal = "🏆" if i == 0 else "🥈" if i == 1 else "🥉" if i == 2 else "⭐"
                st.markdown(f'<div class="leaderboard-card"><b>{medal} {r["Rütbe"]} {r["Öğrencinin Adı"]} ({r["Sınıf"]})</b><br>{int(r["Puan"])} Puan</div>', unsafe_allow_html=True)
    if not df_lb.empty:
        class_sums = df_lb.groupby("Sınıf")["Puan"].sum()
        if not class_sums.empty:
            champ_class = class_sums.idxmax(); champ_puan = int(class_sums.max())
            st.markdown(f"""
                <div class="champion-card">
                    <span style="font-size: 1.4rem;">🏆 Şampiyon Sınıf</span><br>
                    <span style="font-size: 1.1rem;">{champ_class}</span><br>
                    <span style="font-size: 0.9rem;">Toplam: {champ_puan} Puan</span>
                </div>
            """, unsafe_allow_html=True)