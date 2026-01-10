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
RUTBELER = ["🥚 Yeni Başlayan", "🌱 Python Çırağı", "🪵 Kod Oduncusu", "🧱 Mantık Mimarı", "🌀 Döngü Ustası", "📋 Liste Uzmanı", "📦 Fonksiyon Kaptanı", "🤖 OOP Robotu", "🏆 Python Kahramanı"]

st.markdown("""
    <style>
    header {visibility: hidden;}
    .main .block-container {padding-top: 1rem; background-color: #f0f2f6;}
    .pito-bubble {
        position: relative; background: #ffffff; border: 2px solid #3a7bd5;
        border-radius: 15px; padding: 25px; margin-bottom: 20px; color: #1e1e1e;
        font-weight: 500; font-size: 1.1rem; box-shadow: 4px 4px 15px rgba(0,0,0,0.05);
        line-height: 1.7;
    }
    .pito-bubble:after {
        content: ''; position: absolute; bottom: -20px; left: 40px;
        border-width: 20px 20px 0; border-style: solid; border-color: #3a7bd5 transparent;
    }
    .solution-guide {
        background-color: #fef2f2 !important; border: 2px solid #ef4444 !important;
        border-radius: 12px; padding: 20px; margin: 15px 0; color: #1e1e1e !important;
    }
    .hint-guide {
        background-color: #fffbeb !important; border: 2px solid #f59e0b !important;
        border-radius: 12px; padding: 20px; margin: 15px 0; color: #1e1e1e !important;
    }
    .solution-header { color: #ef4444; font-weight: bold; font-size: 1.1rem; margin-bottom: 8px; }
    .hint-header { color: #f59e0b; font-weight: bold; font-size: 1.1rem; margin-bottom: 8px; }
    .leaderboard-card {
        background: linear-gradient(135deg, #1e1e1e, #2d2d2d);
        border: 1px solid #444; border-radius: 12px; padding: 10px; margin-bottom: 8px; color: white;
    }
    .stButton > button {
        width: 100%; border-radius: 12px; height: 3.5em;
        background: linear-gradient(45deg, #3a7bd5, #00d2ff) !important;
        color: white !important; font-weight: bold; border: none;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. VERİ TABANI ---
SHEET_URL = "https://docs.google.com/spreadsheets/d/1lat8rO2qm9QnzEUYlzC_fypG3cRkGlJfSfTtwNvs318/edit#gid=0"
conn = st.connection("gsheets", type=GSheetsConnection)

def get_db():
    try:
        df = conn.read(spreadsheet=SHEET_URL, ttl=0)
        df["Okul No"] = df["Okul No"].astype(str).str.split('.').str[0].str.strip()
        df["Puan"] = pd.to_numeric(df["Puan"], errors='coerce').fillna(0).astype(int)
        return df.dropna(subset=["Okul No"])
    except: return pd.DataFrame(columns=["Okul No", "Öğrencinin Adı", "Sınıf", "Puan", "Rütbe", "Tamamlanan Modüller", "Mevcut Modül", "Mevcut Egzersiz", "Tarih"])

def force_save():
    try:
        no = str(st.session_state.student_no).strip()
        df_all = get_db()
        df_clean = df_all[df_all["Okul No"] != no]
        prog = ",".join(["1" if m else "0" for m in st.session_state.completed_modules])
        rank = RUTBELER[min(sum(st.session_state.completed_modules), 8)]
        new_row = pd.DataFrame([[no, st.session_state.student_name, st.session_state.student_class, int(st.session_state.total_score), rank, prog, int(st.session_state.db_module), int(st.session_state.db_exercise), datetime.now().strftime("%H:%M:%S")]], columns=["Okul No", "Öğrencinin Adı", "Sınıf", "Puan", "Rütbe", "Tamamlanan Modüller", "Mevcut Modül", "Mevcut Egzersiz", "Tarih"])
        conn.update(spreadsheet=SHEET_URL, data=pd.concat([df_clean, new_row], ignore_index=True))
    except: pass

# --- 3. SESSION STATE ---
if 'is_logged_in' not in st.session_state:
    for k, v in {'student_name': "", 'student_no': "", 'student_class': "", 'completed_modules': [False]*8, 
                 'current_module': 0, 'current_exercise': 0, 'exercise_passed': False, 'total_score': 0, 
                 'scored_exercises': set(), 'db_module': 0, 'db_exercise': 0, 'is_logged_in': False, 
                 'current_potential_score': 20, 'celebrated': False, 'fail_count': 0, 
                 'feedback_msg': "", 'last_output': ""}.items():
        st.session_state[k] = v

PITO_IMG = "assets/pito.png"

# --- 4. GİRİŞ EKRANI ---
if not st.session_state.is_logged_in:
    _, col_mid, _ = st.columns([1, 2, 1])
    with col_mid:
        st.markdown('<div class="pito-bubble">Merhaba Geleceğin Yazılımcısı! Ben <b>Pito</b>. Bugün seninle Python dilini bir uzman gibi konuşmayı öğreneceğiz. Kod yazmak, bilgisayara emir vermenin en havalı yoludur!</div>', unsafe_allow_html=True)
        st.image(PITO_IMG if os.path.exists(PITO_IMG) else "https://img.icons8.com/fluency/180/robot-viewer.png", width=180)
        in_no = st.text_input("Okul Numaran:", key="login_field").strip()
        if in_no and in_no.isdigit():
            df = get_db()
            user_data = df[df["Okul No"] == in_no]
            if not user_data.empty:
                row = user_data.iloc[0]
                st.info(f"🔍 Hoş geldin **{row['Öğrencinin Adı']} ({row['Sınıf']})**.")
                if st.button("✅ Maceraya Başla"):
                    m_v, e_v = int(row['Mevcut Modül']), int(row['Mevcut Egzersiz'])
                    st.session_state.update({'student_no': in_no, 'student_name': row["Öğrencinin Adı"], 'student_class': row["Sınıf"], 'total_score': int(row["Puan"]), 'db_module': m_v, 'db_exercise': e_v, 'current_module': min(m_v, 7), 'current_exercise': min(e_v, 4), 'completed_modules': [True if x == "1" else False for x in str(row["Tamamlanan Modüller"]).split(",")], 'is_logged_in': True})
                    st.rerun()
            else:
                in_name = st.text_input("Adın Soyadın:")
                in_class = st.selectbox("Sınıfın:", SINIFLAR)
                if st.button("Kayıt Ol ve Başla ✨") and in_name:
                    st.session_state.update({'student_no': in_no, 'student_name': in_name, 'student_class': in_class, 'is_logged_in': True})
                    force_save(); st.rerun()
    st.stop()

# --- 5. ÖĞRETİCİ EĞİTMEN MÜFREDATI ---
training_data = [
    {"module_title": "1. İletişim: print() ve Çıktı", "exercises": [
        {"msg": "**Eğitmen Notu:** Bilgisayarlar aslında çok akıllıdır ama onlara ne yapacaklarını söylememiz gerekir. `print()` fonksiyonu, bilgisayarın bizimle konuşmasını sağlayan temel araçtır.\n\n**Görev:** Ekrana tam olarak **'Merhaba Pito'** yazdırmanı istiyorum.", "task": "print('___')", "check": lambda c, o, i: "Merhaba Pito" in o, "solution": "print('Merhaba Pito')", "hint": "Metinleri tırnak (' ') içine yazmalısın. Boşluğa tam olarak Merhaba Pito yaz!", "has_output": True},
        {"msg": "**Eğitmen Notu:** Programlamada 'Veri Türleri' vardır. Metinleri tırnakla yazarız ama sayılar (Integer) tırnak gerektirmez. Sayılarla doğrudan matematik yapabiliriz.\n\n**Görev:** Ekrana tırnak kullanmadan sadece sayısal olan **100** değerini bas.", "task": "print(___)", "check": lambda c, o, i: "100" in o, "solution": "print(100)", "hint": "Sayıları yazarken tırnak kullanma, sadece rakamları yaz!", "has_output": True},
        {"msg": "**Eğitmen Notu:** Bazen farklı şeyleri yan yana yazdırmak isteriz. Python'da virgül (`,`) farklı verileri birleştirmek için kullanılır ve araya otomatik bir boşluk koyar.\n\n**Görev:** Önce **'Puan:'** metnini, yanına ise **100** sayısını ekle.", "task": "print('Puan:', ___)", "check": lambda c, o, i: "100" in o, "solution": "print('Puan:', 100)", "hint": "Virgülden sonra sadece 100 yazmalısın.", "has_output": True},
        {"msg": "**Eğitmen Notu:** İyi yazılımcılar kodlarına notlar bırakır. `#` işareti 'yorum satırı' demektir. Bilgisayar bu satırı görmezden gelir, sadece biz insanlar içindir.\n\n**Görev:** Bir `#` işareti kullanarak bu satırı yorum satırına dönüştür.", "task": "___ bu bir yorumdur", "check": lambda c, o, i: "#" in c, "solution": "# bu bir yorumdur", "hint": "Satırın en başına kare (#) işaretini koymalısın.", "has_output": False},
        {"msg": "**Eğitmen Notu:** Metinleri alt alta yazmak için `\\n` (ters eğik çizgi n) karakteri kullanılır. Bu, 'new line' yani yeni satır demektir.\n\n**Görev:** Tek bir print içinde 'Üst' kelimesinden sonra alt satıra geçip 'Alt' yazmasını sağla.", "task": "print('Üst' + '___' + 'Alt')", "check": lambda c, o, i: "Üst\nAlt" in o, "solution": "print('Üst\\nAlt')", "hint": "Tırnak işaretleri içine ters eğik çizgi n (\\n) yazmalısın.", "has_output": True}
    ]},
    {"module_title": "2. Bellek Yönetimi: Değişkenler ve input()", "exercises": [
        {"msg": "**Eğitmen Notu:** Değişkenler, bilgisayarın hafızasındaki (RAM) isimlendirilmiş kutulardır. `=` işareti ile bu kutulara değer koyarız.\n\n**Görev:** **yas** ismindeki değişkene **15** değerini ata.", "task": "yas = ___\nprint(yas)", "check": lambda c, o, i: "15" in o, "solution": "yas = 15", "hint": "Eşittir işaretinden sonra sayısal olarak 15 yaz.", "has_output": True},
        {"msg": "**Eğitmen Notu:** Değişken isimleri anlamlı olmalıdır. Metinsel bir veriyi saklarken tırnak kullanmalısın. Unutma; isimlerde rakam olmaz!\n\n**Görev:** **isim** değişkenine **'Pito'** metnini ata.", "task": "isim = '___'\nprint(isim)", "check": lambda c, o, i: "Pito" in o, "solution": "isim = 'Pito'", "hint": "Tırnakların arasına Pito yazmalısın.", "has_output": True},
        {"msg": "**Eğitmen Notu:** Programlarımızı etkileşimli yapan şey `input()` fonksiyonudur. Kullanıcıdan bilgi almamızı sağlar.\n\n**Görev:** Kullanıcıya **'Adın: '** sorusunu soran girdi komutunu tamamla.", "task": "ad = ___('Adın: ')\nprint(ad)", "check": lambda c, o, i: "input" in c, "solution": "ad = input('Adın: ')", "hint": "Veri almak için 'input' fonksiyonunu kullan.", "has_output": True, "force_text": True},
        {"msg": "**Eğitmen Notu:** `str()` fonksiyonu sayıları metne çevirir. Bu işleme 'Veri Tipi Dönüşümü' denir. Metinlerle sayıları birleştirirken çok işe yarar.\n\n**Görev:** 10 sayısını metne çevirerek ekrana basılmasını sağla.", "task": "s = 10\nprint(___(s))", "check": lambda c, o, i: "str" in c, "solution": "s = 10\nprint(str(s))", "hint": "String kelimesinin kısaltması olan 'str' yazmalısın.", "has_output": True},
        {"msg": "**Eğitmen Notu:** `input()` ile gelen her şey Python için bir 'metin'dir. Eğer matematik yapmak istiyorsan onu `int()` ile tam sayıya çevirmelisin.\n\n**Görev:** Kullanıcıdan sayı al, sayıya çevir ve 1 ekleyip yazdır.", "task": "n = ___(___('S: '))\nprint(n + 1)", "check": lambda c, o, i: "int" in c and (str(int(i if i.isdigit() else 0) + 1) in o), "solution": "n = int(input('10'))", "hint": "Dıştaki boşluğa 'int', içteki boşluğa 'input' yaz.", "has_output": True}
    ]},
    {"module_title": "3. Karar Yapıları: Mantık ve Branching", "exercises": [
        {"msg": "**Eğitmen Notu:** Programların 'zekası' `if` yapısından gelir. Eğer bir şart doğruysa (`True`) o blok çalışır. Eşitlik kontrolü için `==` kullanırız.\n\n**Görev:** Sayı 10'a eşitse 'Buldun!' yazdır.", "task": "s = 10\nif s ___ 10: print('Buldun!')", "check": lambda c, o, i: "==" in c, "solution": "if s == 10:", "hint": "Eşitlik için çift eşittir (==) kullanmalısın.", "has_output": True},
        {"msg": "**Eğitmen Notu:** `else` bloğu, 'if' şartı gerçekleşmediğinde devreye giren 'B Planı'dır.\n\n**Görev:** Şart yanlışsa 'Hatalı' yazdıran bloğu tamamla.", "task": "if 5 > 10: pass\n___: print('Hatalı')", "check": lambda c, o, i: "else" in c, "solution": "else:", "hint": "Sadece else: yazman yeterli.", "has_output": True},
        {"msg": "**Eğitmen Notu:** `elif` (else if), birden fazla şartı sırayla kontrol etmemizi sağlar. 'Eğer o değilse buna bak' demektir.\n\n**Görev:** Puan 50'den büyükse 'Geçti' yazan şartı ekle.", "task": "p = 60\nif p < 50: pass\n___ p > 50: print('Geçti')", "check": lambda c, o, i: "elif" in c, "solution": "elif p > 50:", "hint": "Çoklu şart için elif kullanılır.", "has_output": True},
        {"msg": "**Eğitmen Notu:** Mantıksal bağlaçlar (`and`, `or`) şartları birleştirir. `and` kullanırsan her iki şartın da doğru olması gerekir.\n\n**Görev:** Her iki matematiksel şartın da doğru olduğunu kontrol eden bağlacı yaz.", "task": "if 1 == 1 ___ 2 == 2: print('Mükemmel')", "check": lambda c, o, i: "and" in c, "solution": "and", "hint": "Ve anlamına gelen and bağlacını yazmalısın.", "has_output": True},
        {"msg": "**Eğitmen Notu:** `!=` operatörü 'eşit değilse' demektir. Zıtlıkları kontrol ederken kullanılır.\n\n**Görev:** Sayı 0 değilse 'Var' yazdıran operatörü koy.", "task": "s = 5\nif s ___ 0: print('Var')", "check": lambda c, o, i: "!=" in c, "solution": "if s != 0:", "hint": "Eşit değildir operatörü != şeklindedir.", "has_output": True}
    ]},
    {"module_title": "4. Otomasyon: For ve While Döngüleri", "exercises": [
        {"msg": "**Eğitmen Notu:** Yazılımcılar hamallık yapmaz, döngü kurar! `for` döngüsü belirli bir sayıda tekrar yapmak için `range()` ile harika çalışır.\n\n**Görev:** Ekrana tam 5 kez tur sayısını yazdırmak için aralığı ayarla.", "task": "for i in ___(5): print(i)", "check": lambda c, o, i: "range" in c, "solution": "for i in range(5):", "hint": "Aralık üretici range() fonksiyonunu yaz.", "has_output": True},
        {"msg": "**Eğitmen Notu:** `while` döngüsü bir şart 'doğru' olduğu sürece döner. Sonsuz döngüye girmemek için şartı bozacak bir işlem yapmalısın.\n\n**Görev:** i sıfır olduğu sürece dönen döngüyü başlat.", "task": "i = 0\n___ i == 0: print('Dönüyor'); i += 1", "check": lambda c, o, i: "while" in c, "solution": "while i == 0:", "hint": "While döngüsünü başlatmalısın.", "has_output": True},
        {"msg": "**Eğitmen Notu:** `break` döngünün acil frenidir. Şart sağlandığı an döngüyü tamamen sonlandırır.\n\n**Görev:** i değeri 1 olduğunda döngüden çık.", "task": "for i in range(5):\n if i == 1: ___\n print(i)", "check": lambda c, o, i: "break" in c, "solution": "break", "hint": "Kırmak anlamına gelen break yaz.", "has_output": True},
        {"msg": "**Eğitmen Notu:** `continue` ise o anki adımı pas geçer ve döngünün başına döner. Sadece o turu atlar.\n\n**Görev:** 1 değerini atla.", "task": "for i in range(3):\n if i == 1: ___\n print(i)", "check": lambda c, o, i: "continue" in c, "solution": "continue", "hint": "Atlamak için continue yaz.", "has_output": True},
        {"msg": "**Eğitmen Notu:** Listeler üzerinde `in` anahtarı ile gezinmek çok yaygındır.\n\n**Görev:** Listedeki her harfi ekrana bas.", "task": "for x ___ ['A', 'B']: print(x)", "check": lambda c, o, i: "in" in c, "solution": "for x in", "hint": "İçinde anlamına gelen in kullan.", "has_output": True}
    ]},
    {"module_title": "5. Veri Sepeti: Listeler", "exercises": [
        {"msg": "**Eğitmen Notu:** Listeler birden fazla veriyi tek bir sepette tutar. Köşeli parantez `[]` ile tanımlanır.\n\n**Görev:** Boşluğa 10 değerini koyarak listeyi tamamla.", "task": "L = [___, 20]", "check": lambda c, o, i: "10" in c, "solution": "L = [10, 20]", "hint": "Sadece 10 yaz.", "has_output": False},
        {"msg": "**Eğitmen Notu:** Python'da saymaya her zaman 0'dan başlarız! İlk elemana ulaşmak için `[0]` indeksini kullanırız.\n\n**Görev:** Listenin ilk elemanına (50) ulaş.", "task": "L = [50, 60]\nprint(L[___])", "check": lambda c, o, i: "50" in o, "solution": "L[0]", "hint": "İlk indeks her zaman 0'dır.", "has_output": True},
        {"msg": "**Eğitmen Notu:** `.append()` metodu listenin sonuna yeni bir eleman 'mıknatıs gibi' çeker ve ekler.\n\n**Görev:** Listeye 30 ekle.", "task": "L = [10]\nL.___ (30)\nprint(L)", "check": lambda c, o, i: "append" in c, "solution": "L.append(30)", "hint": "Append metodunu yaz.", "has_output": True},
        {"msg": "**Eğitmen Notu:** `len()` fonksiyonu listenin içinde kaç tane eşya olduğunu sayar. (Length: Uzunluk)\n\n**Görev:** Listenin uzunluğunu bul.", "task": "L = [1, 2, 3]\nprint(___(L))", "check": lambda c, o, i: "3" in o, "solution": "len(L)", "hint": "Len fonksiyonunu kullan.", "has_output": True},
        {"msg": "**Eğitmen Notu:** `.pop()` metodu listenin en sonundaki elemanı çıkarır ve siler.\n\n**Görev:** Son elemanı sil.", "task": "L = [1, 2]\nL.___()\nprint(L)", "check": lambda c, o, i: "pop" in c, "solution": "L.pop()", "hint": "Pop metodunu yaz.", "has_output": True}
    ]},
    {"module_title": "6. Fonksiyonlar ve Veri Yapıları", "exercises": [
        {"msg": "**Eğitmen Notu:** Fonksiyonlar, bir işi bir kez tanımlayıp defalarca kullanmamızı sağlar. `def` (define: tanımla) ile başlar.\n\n**Görev:** 'pito' fonksiyonunu tanımlamaya başla.", "task": "___ pito(): print('Hi')", "check": lambda c, o, i: "def" in c, "solution": "def pito():", "hint": "Tanımlama için def yaz.", "has_output": False},
        {"msg": "**Eğitmen Notu:** Sözlükler (Dictionary) `{anahtar: değer}` mantığıyla çalışır. Gerçek bir sözlük gibi; kelimeyi verip anlamını alırsın.\n\n**Görev:** 'ad' anahtarına 'Pito' değerini ata.", "task": "d = {'ad': '___'}\nprint(d['ad'])", "check": lambda c, o, i: "Pito" in o, "solution": "d = {'ad': 'Pito'}", "hint": "Değer kısmına Pito yaz.", "has_output": True},
        {"msg": "**Eğitmen Notu:** Tuple (Demet), listeye benzer ama `()` ile kurulur ve içindekiler asla değiştirilemez. Mühürlü liste gibidir!\n\n**Görev:** (1, 2) demetini oluştur.", "task": "t = (___, 2)", "check": lambda c, o, i: "1" in c, "solution": "t = (1, 2)", "hint": "Boşluğa 1 yaz.", "has_output": False},
        {"msg": "**Eğitmen Notu:** Sözlükteki tüm etiketleri görmek için `.keys()` kullanılır.\n\n**Görev:** Anahtarları çağıran kodu tamamla.", "task": "d = {'a':1}\nprint(d.___())", "check": lambda c, o, i: "keys" in c, "solution": "d.keys()", "hint": "Keys metodunu yaz.", "has_output": True},
        {"msg": "**Eğitmen Notu:** `return` ifadesi fonksiyonun ürettiği sonucu dış dünyaya fırlatır. Fonksiyonun 'çıktı'sıdır.\n\n**Görev:** 5 döndüren fonksiyon yaz.", "task": "def f(): ___ 5", "check": lambda c, o, i: "return" in c, "solution": "return 5", "hint": "Döndürmek için return yaz.", "has_output": False}
    ]},
    {"module_title": "7. OOP: Nesne Tabanlı Programlama", "exercises": [
        {"msg": "**Eğitmen Notu:** `class` bir fabrikadır. Robot fabrikası kurarsan, ondan binlerce robot (nesne) üretebilirsin.\n\n**Görev:** Robot sınıfı tanımla.", "task": "___ Robot: pass", "check": lambda c, o, i: "class" in c, "solution": "class Robot:", "hint": "Sınıf için class yaz.", "has_output": False},
        {"msg": "**Eğitmen Notu:** Kalıptan nesne üretmek için sınıf ismini bir fonksiyon gibi çağırırız.\n\n**Görev:** r isminde bir Robot üret.", "task": "class Robot: pass\nr = ___()", "check": lambda c, o, i: "Robot()" in c, "solution": "r = Robot()", "hint": "Robot() yazmalısın.", "has_output": False},
        {"msg": "**Eğitmen Notu:** Nesnelerin özellikleri (nitelik) olabilir. Erişmek için nokta (`.`) operatörü kullanılır.\n\n**Görev:** Robotun rengini 'Mavi' yap.", "task": "class R: pass\nr = R()\nr.___ = 'Mavi'\nprint(r.renk)", "check": lambda c, o, i: "renk" in c, "solution": "r.renk = 'Mavi'", "hint": "Noktadan sonra renk yaz.", "has_output": True},
        {"msg": "**Eğitmen Notu:** `self` nesnenin kendisini temsil eder. Metotlarda parantez içine mutlaka yazılır.\n\n**Görev:** Metot tanımlarken self ekle.", "task": "class R:\n def ses(___): print('Bip')", "check": lambda c, o, i: "self" in c, "solution": "def ses(self):", "hint": "Parantez içine self yaz.", "has_output": False},
        {"msg": "**Eğitmen Notu:** Bir metodu çalıştırmak için nesne isminden sonra nokta koyup metot ismini yazarsın.\n\n**Görev:** r nesnesinin s() metodunu çalıştır.", "task": "class R:\n def s(self): print('X')\nr = R()\nr.___()", "check": lambda c, o, i: "s()" in c, "solution": "r.s()", "hint": "s() yazmalısın.", "has_output": True}
    ]},
    {"module_title": "8. Kalıcılık: Dosya Yönetimi", "exercises": [
        {"msg": "**Eğitmen Notu:** Program kapandığında verilerin silinmemesi için dosyaları kullanırız. `open()` ve **'w'** (yazma) moduyla dosya açılır.\n\n**Görev:** Dosyayı yazma modunda aç.", "task": "f = ___('test.txt', '___')", "check": lambda c, o, i: "open" in c and "w" in c, "solution": "open('test.txt', 'w')", "hint": "Açmak için open, mod için w kullan.", "has_output": False},
        {"msg": "**Eğitmen Notu:** `.write()` metodu veriyi dosyanın içine 'mühürler'.\n\n**Görev:** Dosyaya 'Pito' yaz.", "task": "f = open('t.txt', 'w')\nf.___('Pito')\nf.close()", "check": lambda c, o, i: "write" in c, "solution": "f.write('Pito')", "hint": "Write metodunu kullan.", "has_output": False},
        {"msg": "**Eğitmen Notu:** Dosyayı okumak için **'r'** (read) modu kullanılır.\n\n**Görev:** Okuma modunda dosya aç.", "task": "f = open('t.txt', '___')", "check": lambda c, o, i: "r" in c, "solution": "f = open('t.txt', 'r')", "hint": "Mod kısmına r yaz.", "has_output": False},
        {"msg": "**Eğitmen Notu:** `.read()` tüm içeriği bir kerede okuyup programa getirir.\n\n**Görev:** İçeriği ekrana bas.", "task": "f = open('t.txt', 'r')\nprint(f.___())", "check": lambda c, o, i: "read" in c, "solution": "f.read()", "hint": "Read metodunu yaz.", "has_output": True},
        {"msg": "**Eğitmen Notu:** İşlem bittiğinde `.close()` ile dosyayı kapatmak hayati önem taşır; kapatmazsan bellek yorulur.\n\n**Görev:** Dosyayı kapat.", "task": "f = open('t.txt', 'r')\nf.___()", "check": lambda c, o, i: "close" in c, "solution": "f.close()", "hint": "Close yazmalısın.", "has_output": False}
    ]}
]

# --- 6. ARA YÜZ DÜZENİ ---
col_main, col_side = st.columns([3, 1])
m_idx = max(0, min(st.session_state.current_module, 7))
curr_module_exercises = training_data[m_idx]["exercises"]
e_idx = max(0, min(st.session_state.current_exercise, len(curr_module_exercises) - 1))

with col_main:
    st.markdown(f"#### 👋 {RUTBELER[min(sum(st.session_state.completed_modules), 8)]} {st.session_state.student_name} ({st.session_state.student_class}) | ⭐ Puan: {int(st.session_state.total_score)}")
    
    if st.session_state.db_module >= 8:
        if not st.session_state.celebrated: st.balloons(); st.session_state.celebrated = True
        st.success(f"🎉 Tebrikler {st.session_state.student_name}! Tüm Python macerasını başarıyla tamamladın.")
        if st.button("🔄 Eğitimi Tekrar Al"):
            st.session_state.update({'db_module':0,'db_exercise':0,'total_score':0,'current_module':0,'current_exercise':0,'completed_modules':[False]*8,'scored_exercises':set(),'celebrated':False,'fail_count':0,'feedback_msg':"", 'last_output':""})
            force_save(); st.rerun()
        st.divider()

    module_labels = [f"{'✅' if st.session_state.completed_modules[i] else '📖'} Modül {i+1}: {training_data[i]['module_title']}" for i in range(len(training_data))]
    sel_mod_label = st.selectbox("Eğitim Modülü Seç:", module_labels, index=m_idx)
    new_m_idx = module_labels.index(sel_mod_label)
    if new_m_idx != st.session_state.current_module:
        st.session_state.update({'current_module': new_m_idx, 'current_exercise': 0, 'fail_count': 0, 'exercise_passed': False, 'current_potential_score': 20, 'feedback_msg': "", 'last_output': ""})
        st.rerun()

    st.divider()
    curr_ex = curr_module_exercises[e_idx]
    is_locked = (st.session_state.current_module < st.session_state.db_module) or (st.session_state.db_module >= 8)

    c_img, c_msg = st.columns([1, 4])
    with c_img: st.image(PITO_IMG if os.path.exists(PITO_IMG) else "https://img.icons8.com/fluency/200/robot-viewer.png", width=140)
    with c_msg:
        st.info(f"##### 🗣️ Pito'nun Eğitmen Notu:\n{curr_ex['msg']}")
        st.caption(f"Adım: {e_idx + 1}/5 | " + ("🔒 Arşiv" if is_locked else f"🎁 Puan: {st.session_state.current_potential_score} | ❌ Hata: {st.session_state.fail_count}/4"))

    # KADEMELİ HATA VE İPUCU SİSTEMİ
    if st.session_state.fail_count == 3 and not is_locked:
        st.markdown(f"""<div class="hint-guide"><div class="hint-header">💡 Pito'dan İpucu</div>{curr_ex['hint']}</div>""", unsafe_allow_html=True)
        st.warning("⚠️ Bu senin son deneme hakkın! Lütfen dikkat et.")
    elif st.session_state.fail_count >= 4 and not is_locked:
        st.error("❌ Maalesef bu adımdan puan alamadın. İşte öğrenmen için doğru çözüm:")
        st.markdown(f"""<div class="solution-guide"><div class="solution-header">✅ Doğru Çözüm Yolu</div></div>""", unsafe_allow_html=True)
        st.code(curr_ex['solution'], language="python")

    def run_pito_code(c, user_input="Pito"):
        if "___" in c: return "⚠️ Boşluk Hatası"
        old_stdout, new_stdout = sys.stdout, StringIO()
        sys.stdout = new_stdout
        try:
            mock_globals = {"input": lambda p: str(user_input), "print": print, "int": int, "str": str, "len": len, "open": open, "range": range, "s": 10, "L": [10], "d":{'ad':'Pito'}, "t":(1,2), "ad": "Pito"}
            exec(c, mock_globals)
            sys.stdout = old_stdout
            return new_stdout.getvalue()
        except Exception as e:
            sys.stdout = old_stdout
            return f"❌ Python Hatası: {e}"

    if is_locked:
        st.markdown(f'<div class="solution-guide"><div class="solution-header">📖 Çözüm Arşivi</div></div>', unsafe_allow_html=True)
        st.code(curr_ex['solution'], language="python")
    else:
        if st.session_state.fail_count < 4 and not st.session_state.exercise_passed:
            code = st_ace(value=curr_ex['task'], language="python", theme="dracula", font_size=14, height=200, key=f"ace_{st.session_state.current_module}_{e_idx}", auto_update=True)
            
            has_input = "input(" in code
            u_in = ""
            if has_input:
                st.markdown('<div style="border: 2px solid #3a7bd5; padding: 10px; border-radius: 10px; background-color: #e0f2fe; color: #0369a1; font-weight: bold;">⚡ Pito Bekliyor: Aşağıdaki kutuya bir veri yazmalısın!</div>', unsafe_allow_html=True)
                u_in = st.text_input("Giriş simülasyonu (Buraya yazınız):", key=f"term_{st.session_state.current_module}_{e_idx}")
            
            if st.button("🔍 Kodumu Kontrol Et", use_container_width=True):
                if "___" in code:
                    st.session_state.feedback_msg = "⚠️ Lütfen önce kodun içindeki '___' alanlarını doldur!"
                    st.rerun()
                elif has_input and not u_in.strip():
                    st.session_state.feedback_msg = "🔴 DUR! Giriş kutusuna veri yazmadan kontrol edemeyiz!"
                    st.rerun()
                elif curr_ex.get("force_text") and any(char.isdigit() for char in u_in):
                    st.session_state.feedback_msg = "🤔 İsimlerde rakam olmaz, lütfen sadece metin gir!"
                    st.rerun()
                else:
                    out = run_pito_code(code, u_in or "10")
                    if out.startswith("❌") or not curr_ex['check'](code, out, u_in or "10"):
                        st.session_state.fail_count += 1
                        st.session_state.current_potential_score = max(0, st.session_state.current_potential_score - 5)
                        if st.session_state.fail_count >= 4:
                            st.session_state.exercise_passed = True
                            if e_idx == 4: st.session_state.completed_modules[st.session_state.current_module] = True
                        else:
                            st.session_state.feedback_msg = f"❌ bu {st.session_state.fail_count}. hatan"
                        st.rerun()
                    else:
                        st.session_state.feedback_msg = "✅ Harika!"
                        st.session_state.last_output = out
                        st.session_state.exercise_passed = True
                        if f"{st.session_state.current_module}_{e_idx}" not in st.session_state.scored_exercises:
                            st.session_state.total_score += st.session_state.current_potential_score
                            st.session_state.scored_exercises.add(f"{st.session_state.current_module}_{e_idx}")
                            if st.session_state.db_exercise < 4: st.session_state.db_exercise += 1
                            else: st.session_state.db_module += 1; st.session_state.db_exercise = 0; st.session_state.completed_modules[st.session_state.current_module] = True
                            force_save()
                        st.rerun()

    if st.session_state.exercise_passed:
        if st.session_state.fail_count < 4:
            st.success(st.session_state.feedback_msg if st.session_state.feedback_msg else "✅ Görev tamamlandı.")
            if st.session_state.last_output:
                st.markdown("**Kod Çıktısı:**"); st.code(st.session_state.last_output)
        
        # NAVİGASYON (KESİN ÇÖZÜM)
        if e_idx < 4:
            if st.button("➡️ Sonraki Adım", use_container_width=True):
                st.session_state.update({'current_exercise': e_idx + 1, 'exercise_passed': False, 'fail_count': 0, 'current_potential_score': 20, 'feedback_msg': "", 'last_output': ""})
                st.rerun()
        elif st.session_state.current_module < 7:
            if st.button("🏆 Modülü Tamamla", use_container_width=True):
                st.session_state.update({'current_module': st.session_state.current_module + 1, 'current_exercise': 0, 'exercise_passed': False, 'fail_count': 0, 'current_potential_score': 20, 'feedback_msg': "", 'last_output': ""})
                st.rerun()
    elif st.session_state.feedback_msg:
        st.error(st.session_state.feedback_msg)

with col_side:
    df_lb = get_db()
    st.markdown("### 🏅 Şampiyon Sınıf")
    class_stats = df_lb.groupby("Sınıf")["Puan"].sum().reset_index()
    if not class_stats.empty:
        top_class = class_stats.sort_values(by="Puan", ascending=False).head(1).iloc[0]
        st.markdown(f'<div class="leaderboard-card" style="background: linear-gradient(135deg, #FFD700, #DAA520); color: black;"><b>Sınıf: {top_class["Sınıf"]}</b><br>Toplam: {int(top_class["Puan"])} Puan</div>', unsafe_allow_html=True)
    
    st.markdown("### 🏆 En İyi Kodlamacılar")
    tab_class, tab_school = st.tabs(["👥 Sınıfım", "🏫 Okul Geneli"])
    for t, d in zip([tab_class, tab_school], [df_lb[df_lb["Sınıf"] == st.session_state.student_class], df_lb]):
        with t:
            if not d.empty:
                for _, r in d.sort_values(by="Puan", ascending=False).head(10).iterrows():
                    st.markdown(f'<div class="leaderboard-card"><b>{r["Rütbe"]} {r["Öğrencinin Adı"]} ({r["Sınıf"]})</b><br>{int(r["Puan"])} Puan</div>', unsafe_allow_html=True)