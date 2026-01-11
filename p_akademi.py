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
        if df is None or df.empty: return pd.DataFrame(columns=["Okul No", "Öğrencinin Adı", "Sınıf", "Puan", "Rütbe", "Tamamlanan Modüller", "Mevcut Modül", "Mevcut Egzersiz", "Tarih"])
        df["Okul No"] = df["Okul No"].astype(str).str.split('.').str[0].str.strip()
        df["Puan"] = pd.to_numeric(df["Puan"], errors='coerce').fillna(0).astype(int)
        return df.dropna(subset=["Okul No"])
    except: return pd.DataFrame(columns=["Okul No", "Öğrencinin Adı", "Sınıf", "Puan", "Rütbe", "Tamamlanan Modüller", "Mevcut Modül", "Mevcut Egzersiz", "Tarih"])

def force_save():
    try:
        no = str(st.session_state.student_no).strip()
        df_all = get_db()
        if df_all.empty and st.session_state.is_logged_in: return # Veri Zırhı
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

PITO_IMG = "https://img.icons8.com/fluency/180/robot-viewer.png"

# --- 4. GİRİŞ EKRANI ---
if not st.session_state.is_logged_in:
    _, col_mid, _ = st.columns([1, 2, 1])
    with col_mid:
        st.markdown('<div class="pito-bubble">Merhaba Geleceğin Yazılımcısı! Ben <b>Pito</b>. Python dünyasında bir keşfe çıkacağız. Hazır mısın?</div>', unsafe_allow_html=True)
        in_no = st.text_input("Okul Numaran:", key="login_field").strip()
        if in_no and in_no.isdigit():
            df = get_db()
            user_data = df[df["Okul No"] == in_no]
            if not user_data.empty:
                row = user_data.iloc[0]
                st.info(f"Hoş geldin **{row['Öğrencinin Adı']} ({row['Sınıf']})**.")
                if st.button("✅ Maceraya Başla"):
                    m_v, e_v = int(row['Mevcut Modül']), int(row['Mevcut Egzersiz'])
                    st.session_state.update({'student_no': in_no, 'student_name': row["Öğrencinin Adı"], 'student_class': row["Sınıf"], 'total_score': int(row["Puan"]), 'db_module': m_v, 'db_exercise': e_v, 'current_module': m_v, 'current_exercise': e_v, 'completed_modules': [True if x == "1" else False for x in str(row["Tamamlanan Modüller"]).split(",")], 'is_logged_in': True, 'current_potential_score': 20})
                    st.rerun()
            else:
                in_name = st.text_input("Adın Soyadın:")
                in_class = st.selectbox("Sınıfın:", SINIFLAR)
                if st.button("Kayıt Ol ve Başla ✨") and in_name:
                    st.session_state.update({'student_no': in_no, 'student_name': in_name, 'student_class': in_class, 'is_logged_in': True, 'current_potential_score': 20})
                    force_save(); st.rerun()
    st.stop()

# --- 5. EKSİKSİZ UZMAN EĞİTMEN MÜFREDATI ---
training_data = [
    {"module_title": "1. İletişim: print() ve Çıktı Dünyası", "exercises": [
        {"msg": "**Eğitmen Notu:** Bilgisayarlar aslında sadece elektrikle çalışır ama onlara ne yapacaklarını biz söyleriz. `print()` fonksiyonu, Python'ın dünyayla konuşma yoludur. Parantez içine yazdığın metinler ekranda belirir.\n\n**Görev:** Ekrana tam olarak **'Merhaba Pito'** yazdırmanı istiyorum. Boşluğa bu metni yaz!", "task": "print('___')", "check": lambda c, o, i: "Merhaba Pito" in o, "solution": "print('Merhaba Pito')", "hint": "Metinleri mutlaka tırnak işaretleri arasına yazmalısın."},
        {"msg": "**Eğitmen Notu:** Sayılar (Integer), metinlerden farklıdır; tırnak gerektirmezler. Doğrudan matematiksel işlemler yapabiliriz.\n\n**Görev:** Boşluğa tırnak kullanmadan sadece **100** sayısını yaz ve ekrana basılmasını sağla.", "task": "print(___)", "check": lambda c, o, i: "100" in o, "solution": "print(100)", "hint": "Sayıları yazarken tırnak kullanma!"},
        {"msg": "**Eğitmen Notu:** Virgül (`,`) farklı veri tiplerini (metin ve sayı gibi) aynı satırda birleştirir ve araya otomatik bir boşluk koyar.\n\n**Görev:** Önce **'Puan:'** metnini yaz ve yanına sayısal olarak **100** değerini eklemek için boşluğa 100 yaz.", "task": "print('Puan:', ___)", "check": lambda c, o, i: "100" in o, "solution": "print('Puan:', 100)", "hint": "Virgülden sonra tırnaksız şekilde 100 yazmalısın."},
        {"msg": "**Eğitmen Notu:** `#` işareti Python'a 'Bu satırı görmezden gel' demektir. Sadece kod yazanlara not bırakmak içindir.\n\n**Görev:** Satırın en başına **#** işaretini koyarak bu satırı yoruma dönüştür.", "task": "___ bu bir yorumdur", "check": lambda c, o, i: "#" in c, "solution": "# bu bir yorumdur", "hint": "Kare (diyez) işaretini en başa yerleştir."},
        {"msg": "**Eğitmen Notu:** Metinleri alt alta yazmak için `\\n` (new line) kaçış karakterini kullanırız.\n\n**Görev:** Boşluğa **\\n** yazarak 'Üst' ve 'Alt' kelimelerinin alt alta gelmesini sağla.", "task": "print('Üst' + '___' + 'Alt')", "check": lambda c, o, i: "Üst\nAlt" in o, "solution": "print('Üst\\nAlt')", "hint": "Tırnakların arasına sadece \\n yazmalısın."}
    ]},
    {"module_title": "2. Hafıza: Değişkenler ve input()", "exercises": [
        {"msg": "**Eğitmen Notu:** Değişkenler hafızadaki kutulardır. `=` işareti atama yapar, yani kutunun içine bir değer koyar.\n\n**Görev:** **yas** ismindeki kutuya sayısal olarak **15** değerini ata.", "task": "yas = ___\nprint(yas)", "check": lambda c, o, i: "15" in o, "solution": "yas = 15", "hint": "Eşittir işaretinden sonra 15 yaz."},
        {"msg": "**Eğitmen Notu:** Metin atarken tırnak şarttır. İsimlerde rakam kullanmamalıyız.\n\n**Görev:** **isim** kutusuna **'Pito'** metnini ata.", "task": "isim = '___'\nprint(isim)", "check": lambda c, o, i: "Pito" in o, "solution": "isim = 'Pito'", "hint": "Tırnaklar arasına Pito yaz."},
        {"msg": "**Eğitmen Notu:** `input()` programı durdurur ve kullanıcıdan veri bekler. Kullanıcıyla etkileşime girmenin ana yoludur.\n\n**Görev:** Kullanıcıya **'Adın: '** sorusunu soran girdi komutunu tamamla. Boşluğa **input** yaz.", "task": "ad = ___('Adın: ')\nprint(ad)", "check": lambda c, o, i: "input" in c, "solution": "ad = input('Adın: ')", "hint": "input fonksiyonunu kullanmalısın."},
        {"msg": "**Eğitmen Notu:** `str()` fonksiyonu sayıları metne çevirir (Casting). Metin birleştirme işlemlerinde hayati önem taşır.\n\n**Görev:** 10 sayısını metne çevirerek ekrana basılmasını sağlamak için boşluğa **str** yaz.", "task": "s = 10\nprint(___(s))", "check": lambda c, o, i: "str" in c, "solution": "s = 10\nprint(str(s))", "hint": "str yazmalısın."},
        {"msg": "**Eğitmen Notu:** `input()` verisi her zaman 'metin'dir. Matematik yapmak için onu `int()` ile tam sayıya çevirmelisin.\n\n**Görev:** Kullanıcıdan sayı al, sayıya çevir ve 1 ekleyip yazdır. Dıştaki boşluğa **int**, içe **input** yaz.", "task": "n = ___(___('S: '))\nprint(n + 1)", "check": lambda c, o, i: "int" in c and (str(int(i if i.isdigit() else 0) + 1) in o), "solution": "n = int(input('10'))", "hint": "Dıştaki boşluğa int, içteki boşluğa input yaz."}
    ]},
    {"module_title": "3. Karar Yapıları: If-Else Mantığı", "exercises": [
        {"msg": "**Eğitmen Notu:** Programların 'zekası' `if` yapısından gelir. Eğer bir şart doğruysa o blok çalışır. Eşitlik kontrolü için `==` kullanırız.\n\n**Görev:** Sayı 10'a eşitse 'Buldun!' yazdıracak operatörü (**==**) boşluğa yaz.", "task": "s = 10\nif s ___ 10: print('Buldun!')", "check": lambda c, o, i: "==" in c, "solution": "if s == 10:", "hint": "Eşitlik için çift eşittir (==) kullanılır."},
        {"msg": "**Eğitmen Notu:** `else` bloğu, 'if' şartı gerçekleşmediğinde devreye giren alternatiftir.\n\n**Görev:** Şart yanlışsa 'Hata' yazdıran bloğu tamamla. Boşluğa **else** yaz.", "task": "if 5 > 10: pass\n___: print('Hata')", "check": lambda c, o, i: "else" in c, "solution": "else:", "hint": "Sadece else: yazman yeterli."},
        {"msg": "**Eğitmen Notu:** `elif` (else if), birden fazla şartı sırayla denetler.\n\n**Görev:** Puan 50'den büyükse 'Geçti' yazan şartı eklemek için boşluğa **elif** yaz.", "task": "p = 60\nif p < 50: pass\n___ p > 50: print('Geçti')", "check": lambda c, o, i: "elif" in c, "solution": "elif p > 50:", "hint": "elif kullanmalısın."},
        {"msg": "**Eğitmen Notu:** `and` her iki şartın da doğru olmasını bekler. `or` ise sadece birinin.\n\n**Görev:** Her iki şartın da doğru olduğunu kontrol eden bağlacı (**and**) yaz.", "task": "if 1 == 1 ___ 2 == 2: print('OK')", "check": lambda c, o, i: "and" in c, "solution": "and", "hint": "ve anlamına gelen and yaz."},
        {"msg": "**Eğitmen Notu:** `!=` operatörü 'eşit değilse' demektir.\n\n**Görev:** Sayı 0 değilse 'Var' yazdıran operatörü (**!=**) boşluğa koy.", "task": "s = 5\nif s ___ 0: print('Var')", "check": lambda c, o, i: "!=" in c, "solution": "if s != 0:", "hint": "!= operatörünü koy."}
    ]},
    {"module_title": "4. Otomasyon: For ve While Döngüleri", "exercises": [
        {"msg": "**Eğitmen Notu:** Yazılımcılar hamallık yapmaz! `for` döngüsü belirli bir sayıda tekrar yapmak için `range()` ile çalışır.\n\n**Görev:** Döngüyü 5 kez döndürmek için boşluğa **range** yaz.", "task": "for i in ___(5): print(i)", "check": lambda c, o, i: "range" in c, "solution": "for i in range(5):", "hint": "range() fonksiyonunu kullan."},
        {"msg": "**Eğitmen Notu:** `while` döngüsü bir şart 'doğru' olduğu sürece döner.\n\n**Görev:** i sıfır olduğu sürece dönen döngüyü başlatmak için boşluğa **while** yaz.", "task": "i = 0\n___ i == 0: print('Dönüyor'); i += 1", "check": lambda c, o, i: "while" in c, "solution": "while i == 0:", "hint": "while ile başlat."},
        {"msg": "**Eğitmen Notu:** `break` döngünün acil frenidir. Şart sağlandığı an döngüyü tamamen sonlandırır.\n\n**Görev:** i değeri 1 olduğunda döngüyü bitiren **break** komutunu yaz.", "task": "for i in range(5):\n if i == 1: ___\n print(i)", "check": lambda c, o, i: "break" in c, "solution": "break", "hint": "break yaz."},
        {"msg": "**Eğitmen Notu:** `continue` ise o anki adımı pas geçer.\n\n**Görev:** 1 değerini atlayan **continue** komutunu yaz.", "task": "for i in range(3):\n if i == 1: ___\n print(i)", "check": lambda c, o, i: "continue" in c, "solution": "continue", "hint": "continue yaz."},
        {"msg": "**Eğitmen Notu:** Listeler üzerinde `in` anahtarı ile gezinmek yaygındır.\n\n**Görev:** Listedeki her harfi basmak için boşluğa **in** yaz.", "task": "for x ___ ['A', 'B']: print(x)", "check": lambda c, o, i: "in" in c, "solution": "for x in", "hint": "in kullan."}
    ]},
    {"module_title": "5. Gruplama: Listeler (Veri Sepeti)", "exercises": [
        {"msg": "**Eğitmen Notu:** Listeler birden fazla veriyi tek sepette tutar. Köşeli parantez `[]` kullanılır.\n\n**Görev:** Boşluğa sayısal olarak **10** değerini koyarak listeyi tamamla.", "task": "L = [___, 20]", "check": lambda c, o, i: "10" in c, "solution": "L = [10, 20]", "hint": "Sadece 10 yaz."},
        {"msg": "**Eğitmen Notu:** Python'da saymaya her zaman 0'dan başlarız! İlk eleman `[0]` indeksindedir.\n\n**Görev:** İlk elemana (50) ulaşmak için boşluğa **0** yaz.", "task": "L = [50, 60]\nprint(L[___])", "check": lambda c, o, i: "50" in o, "solution": "L[0]", "hint": "İlk indeks 0'dır."},
        {"msg": "**Eğitmen Notu:** `.append()` metodu listenin sonuna yeni bir eleman ekler.\n\n**Görev:** Listeye 30 değerini ekleyen metot olan **append** kelimesini yaz.", "task": "L = [10]\nL.___ (30)\nprint(L)", "check": lambda c, o, i: "append" in c, "solution": "L.append(30)", "hint": "append metodunu yaz."},
        {"msg": "**Eğitmen Notu:** `len()` fonksiyonu boyut (eleman sayısı) ölçer.\n\n**Görev:** Boşluğa **len** yazarak listenin toplam boyutunu bul.", "task": "L = [1, 2, 3]\nprint(___(L))", "check": lambda c, o, i: "3" in o, "solution": "len(L)", "hint": "len kullan."},
        {"msg": "**Eğitmen Notu:** `.pop()` metodu listenin sonundaki elemanı atar.\n\n**Görev:** Son elemanı silen metot olan **pop** kelimesini boşluğa yaz.", "task": "L = [1, 2]\nL.___()\nprint(L)", "check": lambda c, o, i: "pop" in c, "solution": "L.pop()", "hint": "pop yaz."}
    ]},
    {"module_title": "6. Modülerlik: Fonksiyonlar ve Sözlükler", "exercises": [
        {"msg": "**Eğitmen Notu:** Fonksiyonlar tekrarı önler. `def` (define: tanımla) ile başlar.\n\n**Görev:** 'pito' isimli fonksiyonu tanımlamaya başlayan **def** kelimesini boşluğa yaz.", "task": "___ pito(): print('Hi')", "check": lambda c, o, i: "def" in c, "solution": "def pito():", "hint": "def yaz."},
        {"msg": "**Eğitmen Notu:** **Sözlükler (Dictionary)**, veri çiftlerini `{anahtar: değer}` mantığıyla tutar. 'ad' anahtardır (key), 'Pito' ise değerdir (value).\n\n**Görev:** 'ad' anahtarına karşılık gelen değer boşluğuna tırnaklar içinde **'Pito'** yaz.", "task": "d = {'ad': '___'}\nprint(d['ad'])", "check": lambda c, o, i: "Pito" in o, "solution": "d = {'ad': 'Pito'}", "hint": "Pito yaz."},
        {"msg": "**Eğitmen Notu:** **Tuple (Demet)** listelere benzer ama `()` ile kurulur ve değiştirilemez.\n\n**Görev:** Boşluğa sayısal olarak **1** yazarak (1, 2) demetini oluştur.", "task": "t = (___, 2)\nprint(t)", "check": lambda c, o, i: "1" in c, "solution": "t = (1, 2)", "hint": "Boşluğa 1 yaz."},
        {"msg": "**Eğitmen Notu:** Bir sözlükteki sadece etiketleri (anahtarları) çekmek için `.keys()` kullanılır.\n\n**Görev:** Boşluğa **keys** yazarak anahtarları çekmeyi sağla.", "task": "d = {'a':1}\nprint(d.___())", "check": lambda c, o, i: "keys" in c, "solution": "d.keys()", "hint": "keys yaz."},
        {"msg": "**Eğitmen Notu:** `return` ifadesi fonksiyonun ürettiği sonucu dışarı fırlatır.\n\n**Görev:** 5 değerini döndüren (return) fonksiyonu tamamlamak için boşluğa **return** yaz.", "task": "def f(): ___ 5", "check": lambda c, o, i: "return" in c, "solution": "return 5", "hint": "return kullan."}
    ]},
    {"module_title": "7. OOP: Nesne Tabanlı Dünya", "exercises": [
        {"msg": "**Eğitmen Notu:** `class` bir fabrikadır (kalıptır). Ondan binlerce nesne (object) üretebiliriz.\n\n**Görev:** 'Robot' isminde bir kalıp oluşturmak için boşluğa **class** anahtar kelimesini yaz.", "task": "___ Robot: pass", "check": lambda c, o, i: "class" in c, "solution": "class Robot:", "hint": "Kalıp için class yazılır."},
        {"msg": "**Eğitmen Notu:** Kalıptan nesne üretmek için sınıf ismini fonksiyon gibi parantezlerle `()` çağırırız.\n\n**Görev:** Robot kalıbından r isminde bir ürün almak için boşluğa **Robot()** yaz.", "task": "class Robot: pass\nr = ___", "check": lambda c, o, i: "Robot()" in c, "solution": "r = Robot()", "hint": "Robot() yazmalısın."},
        {"msg": "**Eğitmen Notu:** Nesnelerin özellikleri (nitelik) olabilir. Nokta (`.`) operatörüyle erişilir.\n\n**Görev:** r nesnesinin **renk** özelliğini 'Mavi' yapmak için boşluğa **renk** kelimesini yaz.", "task": "class R: pass\nr = R()\nr.___ = 'Mavi'\nprint(r.renk)", "check": lambda c, o, i: "renk" in c, "solution": "r.renk = 'Mavi'", "hint": "renk yaz."},
        {"msg": "**Eğitmen Notu:** `self` nesnenin kendisidir ve metodların parantezinde bulunmalıdır.\n\n**Görev:** Metod parantezi içine **self** anahtarını yazarak nesnenin kendine erişmesini sağla.", "task": "class R:\n def ses(___): print('Bip')", "check": lambda c, o, i: "self" in c, "solution": "def ses(self):", "hint": "self yaz."},
        {"msg": "**Eğitmen Notu:** Nesnenin bir eylemini (metodunu) çalıştırmak için nesne isminden sonra nokta koyup metod ismini yazarız.\n\n**Görev:** r nesnesinin s() metodunu çalıştırmak için boşluğa parantezleri ile beraber **s()** yaz.", "task": "class R:\n def s(self): print('X')\nr = R()\nr.___()", "check": lambda c, o, i: "s()" in c, "solution": "r.s()", "hint": "s() yazmalısın."}
    ]},
    {"module_title": "8. Kalıcılık: Dosya Yönetimi", "exercises": [
        {"msg": "**Eğitmen Notu:** Program kapanınca veriler silinir. Saklamak için `open()` fonksiyonuyla dosya açarız. **'w'** (write) kipi yazmak içindir.\n\n**Görev:** n.txt dosyasını yazma modunda açmak için ilk boşluğa **open**, mod için ikinci boşluğa **w** yaz.", "task": "f = ___('n.txt', '___')", "check": lambda c, o, i: "open" in c and "w" in c, "solution": "open('n.txt', 'w')", "hint": "open ve w kullan."},
        {"msg": "**Eğitmen Notu:** `.write()` metodu veriyi dosyanın içine kalıcı olarak 'mühürler'.\n\n**Görev:** Dosyaya 'X' yazmak için ilgili boşluğa **write** metodunu yaz.", "task": "f = open('t.txt', 'w')\nf.___('X')\nf.close()", "check": lambda c, o, i: "write" in c, "solution": "f.write('X')", "hint": "write yaz."},
        {"msg": "**Eğitmen Notu:** Okuma için **'r'** (read) modu kullanılır.\n\n**Görev:** Dosyayı okuma modunda açmak için boşluğa **r** harfini koy.", "task": "f = open('t.txt', '___')", "check": lambda c, o, i: "r" in c, "solution": "f = open('t.txt', 'r')", "hint": "r yaz."},
        {"msg": "**Eğitmen Notu:** `.read()` metodu dosyanın tüm içeriğini programa getirir.\n\n**Görev:** İçeriği almak için boşluğa **read** metodunu yaz.", "task": "f = open('t.txt', 'r')\nprint(f.___())", "check": lambda c, o, i: "read" in c, "solution": "f.read()", "hint": "read yaz."},
        {"msg": "**Eğitmen Notu:** `.close()` hayati önem taşır; kapatılmayan dosyalar hafızayı meşgul eder.\n\n**Görev:** Dosyayı kapatmak için boşluğa **close** kelimesini yaz.", "task": "f = open('t.txt', 'r')\nf.___()", "check": lambda c, o, i: "close" in c, "solution": "f.close()", "hint": "close yaz."}
    ]}
]

# --- 6. ARA YÜZ DÜZENİ ---
col_main, col_side = st.columns([3, 1])

# SIRALI İLERLEME VE KİLİT SİSTEMİ
# Sadece db_module değerine kadar olan (açılmış) modülleri göster
selectable_indices = list(range(min(st.session_state.db_module + 1, 8)))
module_labels = [f"{'✅' if i < st.session_state.db_module else '📖'} Modül {i+1}: {training_data[i]['module_title']}" for i in selectable_indices]

with col_main:
    st.markdown(f"#### 👋 {RUTBELER[min(sum(st.session_state.completed_modules), 8)]} {st.session_state.student_name} ({st.session_state.student_class}) | ⭐ Puan: {int(st.session_state.total_score)}")
    
    if st.session_state.db_module >= 8:
        if not st.session_state.celebrated: st.balloons(); st.session_state.celebrated = True
        st.success("🎉 Tebrikler! Tüm macerayı bitirdin.")
    
    sel_mod_label = st.selectbox("Modül Seç:", module_labels, index=min(st.session_state.current_module, len(module_labels)-1))
    new_m_idx = selectable_indices[module_labels.index(sel_mod_label)]
    
    if new_m_idx != st.session_state.current_module:
        st.session_state.update({'current_module': new_m_idx, 'current_exercise': 0, 'fail_count': 0, 'exercise_passed': False, 'current_potential_score': 20, 'feedback_msg': "", 'last_output': ""})
        st.rerun()

    st.divider()
    curr_ex = training_data[st.session_state.current_module]["exercises"][st.session_state.current_exercise]
    is_review_mode = (st.session_state.current_module < st.session_state.db_module)

    c_img, c_msg = st.columns([1, 4])
    with c_img: st.image(PITO_IMG, width=140)
    with c_msg:
        st.info(f"##### 🗣️ Pito'nun Notu:\n{curr_ex['msg']}")
        status = "🔒 İnceleme Modu (Arşiv)" if is_review_mode else f"🎁 Puan: {st.session_state.current_potential_score} | ❌ Hata: {st.session_state.fail_count}/4"
        st.caption(f"Adım: {st.session_state.current_exercise + 1}/5 | {status}")

    def run_pito_code(c):
        if "___" in c: return "⚠️ Boşluk Hatası"
        old_stdout, new_stdout = sys.stdout, StringIO()
        sys.stdout = new_stdout
        try:
            # Akıllı Simülasyon
            exec(c, {"print": print, "input": lambda x: "10", "range": range, "s": 10, "L": [10, 20], "d":{'ad':'Pito', 'yas':15, 'a':1}, "t":(1,2), "Robot": lambda: None, "R": lambda: None})
            sys.stdout = old_stdout
            return new_stdout.getvalue()
        except Exception as e:
            sys.stdout = old_stdout
            return f"❌ Hata: {e}"

    if is_review_mode:
        st.markdown('<div class="solution-guide"><div class="solution-header">📖 Arşiv Kaydı (Soru ve Çözüm)</div></div>', unsafe_allow_html=True)
        st.code(curr_ex['solution'], language="python")
    else:
        if st.session_state.fail_count < 4 and not st.session_state.exercise_passed:
            code = st_ace(value=curr_ex['task'], language="python", theme="dracula", font_size=14, height=180, key=f"ace_{st.session_state.current_module}_{st.session_state.current_exercise}")
            if st.button("🔍 Kodumu Kontrol Et"):
                if "___" in code: st.session_state.feedback_msg = "⚠️ Önce boşluğu doldur!"; st.rerun()
                else:
                    out = run_pito_code(code)
                    if out.startswith("❌") or not curr_ex.get('check', lambda c, o, i: True)(code, out, ""):
                        st.session_state.fail_count += 1
                        st.session_state.current_potential_score = max(0, st.session_state.current_potential_score - 5)
                        if st.session_state.fail_count >= 4: st.session_state.exercise_passed = True
                        st.rerun()
                    else:
                        st.session_state.feedback_msg = "✅ Harika!"
                        st.session_state.last_output = out
                        st.session_state.exercise_passed = True
                        ex_key = f"{st.session_state.current_module}_{st.session_state.current_exercise}"
                        if ex_key not in st.session_state.scored_exercises:
                            st.session_state.total_score += st.session_state.current_potential_score
                            st.session_state.scored_exercises.add(ex_key)
                            force_save()
                        st.rerun()
        
        if st.session_state.fail_count == 3:
            st.markdown(f'<div class="hint-guide"><div class="hint-header">💡 İpucu</div>{curr_ex["hint']}</div>', unsafe_allow_html=True)
        elif st.session_state.fail_count >= 4:
            st.error("❌ Puan alamadın. İşte doğru çözüm:")
            st.markdown(f'<div class="solution-guide"><div class="solution-header">✅ Doğru Çözüm</div></div>', unsafe_allow_html=True)
            st.code(curr_ex['solution'], language="python")

    if st.session_state.exercise_passed or is_review_mode or st.session_state.fail_count >= 4:
        if not is_review_mode and st.session_state.fail_count < 4:
            st.success(st.session_state.feedback_msg)
            if st.session_state.last_output: st.code(st.session_state.last_output)
        
        col_p, col_n = st.columns(2)
        with col_p:
            if st.session_state.current_exercise > 0:
                if st.button("⬅️ Önceki Adım"):
                    st.session_state.update({'current_exercise': st.session_state.current_exercise - 1, 'exercise_passed': False, 'fail_count': 0, 'current_potential_score': 20, 'feedback_msg': "", 'last_output': ""})
                    st.rerun()
        with col_n:
            if st.session_state.current_exercise < 4:
                if st.button("➡️ Sonraki Adım"):
                    st.session_state.update({'current_exercise': st.session_state.current_exercise + 1, 'exercise_passed': False, 'fail_count': 0, 'current_potential_score': 20, 'feedback_msg': "", 'last_output': ""})
                    st.rerun()
            elif st.session_state.current_module < 7:
                if st.button("🏆 Modülü Bitir ve Devam Et"):
                    if not is_review_mode:
                        st.session_state.db_module += 1; st.session_state.db_exercise = 0
                        st.session_state.completed_modules[st.session_state.current_module] = True
                        force_save()
                    st.session_state.update({'current_module': st.session_state.current_module + 1, 'current_exercise': 0, 'exercise_passed': False, 'fail_count': 0, 'current_potential_score': 20})
                    st.rerun()

with col_side:
    df_lb = get_db()
    st.markdown("### 🏅 Şampiyon Sınıf")
    if not df_lb.empty:
        class_stats = df_lb.groupby("Sınıf")["Puan"].sum().reset_index()
        top_class = class_stats.sort_values(by="Puan", ascending=False).head(1).iloc[0]
        st.markdown(f'<div class="leaderboard-card" style="background: linear-gradient(135deg, #FFD700, #DAA520); color: black;"><b>Sınıf: {top_class["Sınıf"]}</b><br>Toplam: {int(top_class["Puan"])} Puan</div>', unsafe_allow_html=True)
    
    st.markdown("### 🏆 En İyi Kodlamacılar")
    tab_c, tab_s = st.tabs(["👥 Sınıfım", "🏫 Okul Geneli"])
    for t, d in zip([tab_c, tab_s], [df_lb[df_lb["Sınıf"] == st.session_state.student_class], df_lb]):
        with t:
            if not d.empty:
                for _, r in d.sort_values(by="Puan", ascending=False).head(10).iterrows():
                    st.markdown(f'<div class="leaderboard-card"><b>{r["Rütbe"]} {r["Öğrencinin Adı"]} ({r["Sınıf"]})</b><br>{int(r["Puan"])} Puan</div>', unsafe_allow_html=True)