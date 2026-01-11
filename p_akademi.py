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

# --- 2. SESSION STATE (HATA VE VERİ KORUMA ZIRHI) ---
if 'is_logged_in' not in st.session_state:
    for k, v in {
        'student_name': "", 'student_no': "", 'student_class': "", 'completed_modules': [False]*8, 
        'current_module': 0, 'current_exercise': 0, 'exercise_passed': False, 'total_score': 0, 
        'scored_exercises': set(), 'db_module': 0, 'db_exercise': 0, 'is_logged_in': False, 
        'current_potential_score': 20, 'fail_count': 0, 'feedback_msg': "", 'last_output': "", 
        'login_error': ""
    }.items():
        st.session_state[k] = v

SINIFLAR = ["9-A", "9-B", "10-A", "10-B", "11-A", "11-B"]
RUTBELER = ["🥚 Yeni Başlayan", "🌱 Python Çırağı", "🪵 Kod Oduncusu", "🧱 Mantık Mimarı", "🌀 Döngü Ustası", "📋 Liste Uzmanı", "📦 Fonksiyon Kaptanı", "🤖 OOP Robotu", "🏆 Python Kahramanı"]

st.markdown("""
    <style>
    header {visibility: hidden;}
    .main .block-container {padding-top: 1rem; background-color: #f0f2f6;}
    .quest-container {
        background: white; padding: 15px; border-radius: 15px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1); margin-bottom: 20px;
        border-bottom: 4px solid #3a7bd5; text-align: center;
    }
    .quest-bar { height: 14px; background: #e2e8f0; border-radius: 10px; margin: 10px 0; overflow: hidden; position: relative; }
    .quest-fill { height: 100%; background: linear-gradient(90deg, #3a7bd5, #00d2ff); transition: width 0.6s ease-in-out; }
    .pito-bubble {
        position: relative; background: #ffffff; border: 2px solid #3a7bd5;
        border-radius: 15px; padding: 25px; margin-bottom: 20px; color: #1e1e1e;
        font-weight: 500; font-size: 1.1rem; box-shadow: 4px 4px 15px rgba(0,0,0,0.05); line-height: 1.7;
    }
    .pito-bubble:after { content: ''; position: absolute; bottom: -20px; left: 40px; border-width: 20px 20px 0; border-style: solid; border-color: #3a7bd5 transparent; }
    .solution-guide { background-color: #fef2f2 !important; border: 2px solid #ef4444 !important; border-radius: 12px; padding: 20px; margin: 15px 0; color: #1e1e1e !important; }
    .hint-guide { background-color: #fffbeb !important; border: 2px solid #f59e0b !important; border-radius: 12px; padding: 20px; margin: 15px 0; color: #1e1e1e !important; }
    .leaderboard-card { background: linear-gradient(135deg, #1e1e1e, #2d2d2d); border: 1px solid #444; border-radius: 12px; padding: 10px; margin-bottom: 8px; color: white; }
    .stButton > button { width: 100%; border-radius: 12px; height: 3.5em; background: linear-gradient(45deg, #3a7bd5, #00d2ff) !important; color: white !important; font-weight: bold; border: none; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. VERİ TABANI ---
SHEET_URL = "https://docs.google.com/spreadsheets/d/1lat8rO2qm9QnzEUYlzC_fypG3cRkGlJfSfTtwNvs318/edit#gid=0"
conn = st.connection("gsheets", type=GSheetsConnection)

def get_db():
    try:
        df = conn.read(spreadsheet=SHEET_URL, ttl=0)
        if df is None or df.empty: return pd.DataFrame(columns=["Okul No", "Öğrencinin Adı", "Sınıf", "Puan", "Rütbe", "Tamamlanan Modüller", "Mevcut Modül", "Mevcut Egzersiz", "Tarih"])
        df.columns = df.columns.str.strip()
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

PITO_IMG = "assets/pito.png"
def show_pito_img(width=180):
    if os.path.exists(PITO_IMG): st.image(PITO_IMG, width=width)
    else: st.image("https://img.icons8.com/fluency/180/robot-viewer.png", width=width)

# --- 4. SIDEBAR LİDERLİK TABLOSU ---
db_current = get_db()
with st.sidebar:
    st.markdown("### 🏅 Şampiyon Sınıf")
    if not db_current.empty:
        class_stats = db_current.groupby("Sınıf")["Puan"].sum().reset_index()
        if not class_stats.empty:
            top_class = class_stats.sort_values(by="Puan", ascending=False).head(1).iloc[0]
            st.markdown(f'<div class="leaderboard-card" style="background: linear-gradient(135deg, #FFD700, #DAA520); color: black;"><b>Sınıf: {top_class["Sınıf"]}</b><br>Toplam: {int(top_class["Puan"])} Puan</div>', unsafe_allow_html=True)
    st.markdown("---")
    tab_c, tab_s = st.tabs(["👥 Sınıfım", "🏫 Okul"])
    with tab_c:
        if st.session_state.is_logged_in:
            my_c = db_current[db_current["Sınıf"] == st.session_state.student_class].sort_values(by="Puan", ascending=False).head(5)
            for _, r in my_c.iterrows(): st.markdown(f'<div class="leaderboard-card"><b>{r["Rütbe"]} {r["Öğrencinin Adı"]}</b><br>{int(r["Puan"])} Puan</div>', unsafe_allow_html=True)
        else: st.caption("Giriş yapmalısın.")
    with tab_s:
        for _, r in db_current.sort_values(by="Puan", ascending=False).head(10).iterrows():
            st.markdown(f'<div class="leaderboard-card"><b>{r["Rütbe"]} {r["Öğrencinin Adı"]} ({r["Sınıf"]})</b><br>{int(r["Puan"])} Puan</div>', unsafe_allow_html=True)

# --- 5. GİRİŞ EKRANI ---
col_app, _ = st.columns([3, 0.01])
with col_app:
    if not st.session_state.is_logged_in:
        _, col_mid, _ = st.columns([1, 4, 1])
        with col_mid:
            st.markdown('<div class="pito-bubble">Selam geleceğin yazılımcı dostu! Ben <b>Pito</b>. Nusaybin laboratuvarında Python macerasına hazır mısın?</div>', unsafe_allow_html=True)
            show_pito_img(180)
            in_no = st.text_input("Okul Numaran:", key="login_field").strip()
            if in_no:
                if not in_no.isdigit(): st.error("⚠️ Sadece rakam giriniz!")
                else:
                    user_data = db_current[db_current["Okul No"] == in_no]
                    if not user_data.empty:
                        row = user_data.iloc[0]
                        st.warning(f"🔍 **{row['Öğrencinin Adı']}** ({row['Sınıf']}), bu sen misin?")
                        if st.button("✅ Evet, Benim"):
                            st.session_state.update({'student_no': in_no, 'student_name': row["Öğrencinin Adı"], 'student_class': row["Sınıf"], 'total_score': int(row["Puan"]), 'db_module': int(row['Mevcut Modül']), 'db_exercise': int(row['Mevcut Egzersiz']), 'current_module': int(row['Mevcut Modül']), 'current_exercise': int(row['Mevcut Egzersiz']), 'completed_modules': [True if x == "1" else False for x in str(row["Tamamlanan Modüller"]).split(",")], 'is_logged_in': True})
                            st.rerun()
                    else:
                        st.info("🌟 Seni henüz tanımıyorum. Lütfen kayıt ol!")
                        in_name = st.text_input("Adın Soyadın:")
                        in_class = st.selectbox("Sınıfın:", SINIFLAR)
                        if st.button("✨ Kayıt Ol"):
                            if in_name:
                                st.session_state.update({'student_no': in_no, 'student_name': in_name, 'student_class': in_class, 'is_logged_in': True})
                                force_save(); st.rerun()
        st.stop()

    # --- 6. EKSİKSİZ VE MÜHÜRLÜ PEDAGOJİK MÜFREDAT (40 ADIM) ---
    training_data = [
        {"module_title": "1. İletişim: print() ve Metin Dünyası", "exercises": [
            {"msg": "**Pito'nun Notu:** Python'ın dış dünyayla konuşma yolu `print()` fonksiyonudur. Ekrana yazacağın metinleri mutlaka tırnak (' ') içine almalısın. Tırnaklar Python'a 'buradaki her şeyi olduğu gibi yansıt' der.", "task": "print('___')", "check": lambda c, o, i: "Merhaba Pito" in o, "solution": "print('Merhaba Pito')", "hint": "Metnin her iki yanına da tek (') veya çift (\") tırnak koymayı unutma."},
            {"msg": "**Pito'nun Notu:** Sayılar (Integer), metinlerden farklıdır. Tırnak gerektirmezler. Eğer tırnak koyarsan Python onu sayı değil, yazı olarak görür ve üzerinde matematik yapamaz.", "task": "print(___)", "check": lambda c, o, i: "100" in o, "solution": "print(100)", "hint": "Sayısal değer olan 100'ü doğrudan tırnaksız yazmalısın."},
            {"msg": "**Pito'nun Notu:** Virgül (`,`) farklı veri tiplerini aynı satırda birleştirirken araya otomatik bir boşluk koyar. Bu, değişkenleri ve mesajları birleştirmek için çok profesyonel bir yoldur.", "task": "print('Puan:', ___)", "check": lambda c, o, i: "100" in o, "solution": "print('Puan:', 100)", "hint": "Virgülden sonra sadece sayısal değer olan 100'ü yaz."},
            {"msg": "**Pito'nun Notu:** `#` işareti Python'a 'Bu satırı görmezden gel' demektir. Buna 'Yorum Satırı' diyoruz. Sadece biz yazılımcıların not alması içindir.", "task": "___ bu bir nottur", "check": lambda c, o, i: "#" in c, "solution": "# bu bir nottur", "hint": "Klavyeden diyez (#) işaretini satırın en başına yerleştir."},
            {"msg": "**Pito'nun Notu:** `\\n` (new line) kaçış karakteri metni alt satıra böler. Sanki klavyede 'Enter' tuşuna basılmış gibi davranır.", "task": "print('Üst' + '___' + 'Alt')", "check": lambda c, o, i: "Üst\nAlt" in o, "solution": "print('Üst\\nAlt')", "hint": "Tırnaklar içerisine ters eğik çizgi (\\) ve n harfini birleşik yaz: \\n"}
        ]},
        {"module_title": "2. Hafıza: Değişkenler ve input()", "exercises": [
            {"msg": "**Pito'nun Notu:** Değişkenler bellekteki kutulardır. `=` işareti bir 'atama operatörü'dür ve sağdaki değeri soldaki kutunun içine koyar.", "task": "yas = ___", "check": lambda c, o, i: "15" in c, "solution": "yas = 15", "hint": "Eşittir işaretinden sonra sadece değeri (15) yazmalısın."},
            {"msg": "**Pito'nun Notu:** `input()` programı durdurur ve kullanıcıdan bir bilgi bekler. Python bu bilgiyi her zaman 'String' (metin) olarak belleğe kaydeder.", "task": "ad = ___('Adın: ')", "check": lambda c, o, i: "input" in c, "solution": "ad = input('Adın: ')", "hint": "Girdi alma fonksiyonu olan 'input' kelimesini kullan."},
            {"msg": "**Pito'nun Notu:** Sayıları metne çevirmemiz gerektiğinde (Casting) `str()` fonksiyonunu kullanırız. Bu, metinleri birleştirirken hayati önem taşır.", "task": "print(___(10))", "check": lambda c, o, i: "str" in c, "solution": "print(str(10))", "hint": "String'in kısaltması olan 'str' fonksiyonunu yerleştir."},
            {"msg": "**Pito'nun Notu:** Matematik yapabilmek için `input()` ile gelen metni `int()` fonksiyonu ile 'tam sayıya' çevirmelisin. Buna tip dönüşümü denir.", "task": "n = ___(___('S: '))", "check": lambda c, o, i: "int" in c and "input" in c, "solution": "n = int(input('S: '))", "hint": "Fonksiyonları iç içe kullanmalısın: int(input())"},
            {"msg": "**Pito'nun Notu:** Değişken isimlerinde Pito ismini sakla. Metin verilerini tırnakla atamayı unutma; yoksa Python onu bir komut sanabilir.", "task": "isim = '___'", "check": lambda c, o, i: "Pito" in o, "solution": "isim = 'Pito'", "hint": "Tırnaklar arasına tam olarak Pito yaz."}
        ]},
        {"module_title": "3. Karar Yapıları: If-Else Mantığı", "exercises": [
            {"msg": "**Pito'nun Notu:** Programların karar verme yeteneği `if` bloğuyla başlar. Eşitlik sorgusu yaparken `=` değil, mutlaka `==` (çift eşittir) kullanmalısın.", "task": "if 10 ___ 10: print('OK')", "check": lambda c, o, i: "==" in c, "solution": "if 10 == 10:\n    print('OK')", "hint": "Mantıksal karşılaştırma için çift eşittir (==) mühürdür."},
            {"msg": "**Pito'nun Notu:** `else:` bloğu, 'if' şartı 'False' (yanlış) olduğunda devreye giren otomatik plandır. Asla tek başına kullanılamaz.", "task": "if 5 > 10: pass\n___: print('Hata')", "check": lambda c, o, i: "else" in c, "solution": "if 5 > 10: pass\nelse:\n    print('Hata')", "hint": "Sadece else kelimesini ve iki noktayı (else:) düşün."},
            {"msg": "**Pito'nun Notu:** Birden fazla şartı sırayla denetlemek için `elif` (else if) kullanırız. Şartlardan biri doğru çıktığında altındakiler okunmaz.", "task": "p = 60\nif p < 50: pass\n___ p > 50: print('Geçti')", "check": lambda c, o, i: "elif" in c, "solution": "if p < 50: pass\nelif p > 50:\n    print('Geçti')", "hint": "İkinci bir şart kontrolü için elif komutunu kullan."},
            {"msg": "**Pito'nun Notu:** `and` (ve) bağlacı, her iki tarafındaki şartın da doğru olmasını bekler. `or` ise sadece birinin doğru olmasıyla yetinir.", "task": "if 1 == 1 ___ 2 == 2: print('OK')", "check": lambda c, o, i: "and" in c, "solution": "if 1 == 1 and 2 == 2:\n    print('OK')", "hint": "İngilizcede 've' anlamına gelen and kelimesini yerleştir."},
            {"msg": "**Pito'nun Notu:** `!=` operatörü 'eşit değilse' anlamına gelir. Şartın gerçekleşmediği durumları kontrol etmek için çok güçlü bir araçtır.", "task": "s = 5\nif s ___ 0: print('Var')", "check": lambda c, o, i: "!=" in c, "solution": "if s != 0:\n    print('Var')", "hint": "Ünlem ve eşittir işaretlerini birleştir: !="}
        ]},
        {"module_title": "4. Otomasyon: For ve While Döngüleri", "exercises": [
            {"msg": "**Pito'un Notu:** `for` döngüsü bir liste veya sayı aralığında (range) adım adım ilerler. `range(5)` komutu 0'dan 4'e kadar sayı üretir.", "task": "for i in ___(5): print(i)", "check": lambda c, o, i: "range" in c, "solution": "for i in range(5):\n    print(i)", "hint": "Sayı üreticisi olan range() fonksiyonunu kullanmalısın."},
            {"msg": "**Pito'un Notu:** `while` döngüsü bir şart 'True' olduğu sürece çalışır. Döngünün içinde o şartı bir noktada bozmalısın yoksa sonsuz döngü olur.", "task": "i = 0\n___ i == 0: print('Dönüyor'); i += 1", "check": lambda c, o, i: "while" in c, "solution": "i = 0\nwhile i == 0:\n    print('Dönüyor')\n    i += 1", "hint": "Şartlı döngü komutu olan while kelimesini yerleştir."},
            {"msg": "**Pito'un Notu:** `break` komutu döngünün 'acil çıkış' kapısıdır. Şart sağlandığı an döngüyü tamamen sonlandırır ve program devam eder.", "task": "for i in range(5):\n if i == 1: ___\n print(i)", "check": lambda c, o, i: "break" in c, "solution": "for i in range(5):\n    if i == 1: break\n    print(i)", "hint": "Döngüyü kırmak için break anahtar kelimesini kullan."},
            {"msg": "**Pito'un Notu:** `continue` o anki adımı 'pas geçer' ve döngünün en başına geri döner. Bir sonraki turdan devam eder.", "task": "for i in range(3):\n if i == 1: ___\n print(i)", "check": lambda c, o, i: "continue" in c, "solution": "for i in range(3):\n    if i == 1: continue\n    print(i)", "hint": "Atlamak anlamına gelen continue kelimesini kullan."},
            {"msg": "**Pito'un Notu:** Listelerde gezinmek için `in` anahtar kelimesini kullanırız. Bu, her bir elemanı sırayla değişkenimize atar.", "task": "for x ___ ['A', 'B']: print(x)", "check": lambda c, o, i: "in" in c, "solution": "for x in ['A', 'B']:\n    print(x)", "hint": "Aitlik ve üyelik bildiren in kelimesini yerleştir."}
        ]},
        {"module_title": "5. Gruplama: Listeler (Veri Sepeti)", "exercises": [
            {"msg": "**Pito'un Notu:** Listeler birden fazla veriyi tek bir kutuda saklamamızı sağlar. Köşeli parantez `[]` ile tanımlanır.", "task": "L = [___, 20]", "check": lambda c, o, i: "10" in c, "solution": "L = [10, 20]", "hint": "Listenin ilk elemanı için sadece 10 rakamını yaz."},
            {"msg": "**Pito'un Notu:** Python'da saymaya her zaman 0'dan başlarız. Listenin ilk elemanına `[0]` indeksini kullanarak ulaşırız.", "task": "L = [50, 60]\nprint(L[___])", "check": lambda c, o, i: "50" in o, "solution": "L = [50, 60]\nprint(L[0])", "hint": "Python'da indekslerin başlangıç sayısı olan 0'ı düşün."},
            {"msg": "**Pito'un Notu:** `.append()` metodu listenin sonuna yeni bir eleman ekler ve sepeti büyütür.", "task": "L = [10]\nL.___ (30)", "check": lambda c, o, i: "append" in c, "solution": "L = [10]\nL.append(30)", "hint": "Noktadan sonra ekleme metodu olan append kelimesini kullan."},
            {"msg": "**Pito'un Notu:** `len()` fonksiyonu 'length' (uzunluk) kelimesinden gelir ve listenin içindeki eleman sayısını bize verir.", "task": "L = [1, 2, 3]\nprint(___(L))", "check": lambda c, o, i: "3" in o, "solution": "L = [1, 2, 3]\nprint(len(L))", "hint": "Eleman sayısını ölçen len fonksiyonunu yaz."},
            {"msg": "**Pito'un Notu:** `.pop()` metodu listenin en sonundaki elemanı sepetten çıkarır ve bize geri verir.", "task": "L = [1, 2]\nL.___()", "check": lambda c, o, i: "pop" in c, "solution": "L = [1, 2]\nL.pop()", "hint": "Parantezlerin önüne pop kelimesini yazmalısın."}
        ]},
        {"module_title": "6. Modülerlik: Fonksiyonlar ve Sözlükler", "exercises": [
            {"msg": "**Pito'un Notu:** Fonksiyonlar tekrar eden kodları bir 'iş paketi'ne dönüştürür. `def` (define: tanımla) kelimesi ile kurulur.", "task": "___ pito(): print('Hi')", "check": lambda c, o, i: "def" in c, "solution": "def pito():\n    print('Hi')", "hint": "Fonksiyon tanımlama anahtarı olan def'i düşün."},
            {"msg": "**Pito'un Notu:** **Sözlükler (Dictionary)**, `{anahtar: değer}` çiftleriyle çalışır. Tıpkı rehberdeki bir isim ve ona ait numara gibi.", "task": "d = {'ad': '___'}", "check": lambda c, o, i: "Pito" in o, "solution": "d = {'ad': 'Pito'}", "hint": "Metni tırnaklar içerisine tam olarak Pito şeklinde yaz."},
            {"msg": "**Pito'un Notu:** **Tuple (Demet)**, listeye benzer ama içeriğinin asla değiştirilemez (immutable) olmasıyla ayrılır.", "task": "t = (___, 2)", "check": lambda c, o, i: "1" in c, "solution": "t = (1, 2)", "hint": "Sadece eksik olan 1 rakamını koyman yeterli."},
            {"msg": "**Pito'un Notu:** `.keys()` metodu bir sözlükteki tüm etiketleri (anahtarları) bize bir liste halinde sunar.", "task": "d = {'a':1}\nprint(d.___())", "check": lambda c, o, i: "keys" in c, "solution": "d = {'a':1}\nprint(d.keys())", "hint": "Anahtar kelimesinin İngilizcesini düşün: keys."},
            {"msg": "**Pito'un Notu:** `return` ifadesi fonksiyonun ürettiği sonucu dışarıya 'fırlatır'. Bu değer değişkene atanabilir.", "task": "def f(): ___ 5", "check": lambda c, o, i: "return" in c, "solution": "def f():\n    return 5", "hint": "Geri döndürme komutu olan return kelimesini kullan."}
        ]},
        {"module_title": "7. OOP: Nesne Tabanlı Dünya", "exercises": [
            {"msg": "**OOP:** `class` (Sınıf) bir taslaktır. Ondan kopyalar yani 'Nesneler' (Object) üretiriz. Sınıf fabrika, nesne üründür.", "task": "___ Robot: pass", "check": lambda c, o, i: "class" in c, "solution": "class Robot:\n    pass", "hint": "Sınıf tanımlama anahtarı olan class kelimesini yaz."},
            {"msg": "**OOP:** Kalıptan nesne üretmek için sınıf ismini parantezlerle `()` çağırırız. Buna 'Instance' oluşturma denir.", "task": "class Robot: pass\nr = ___", "check": lambda c, o, i: "Robot()" in c, "solution": "class Robot: pass\nr = Robot()", "hint": "Sınıf isminin sonuna parantezleri eklemelisin."},
            {"msg": "**OOP:** Nesnelerin özellikleri (Attribute) nokta (`.`) yardımıyla atanır. Bu nesnenin kimlik bilgisidir.", "task": "class R: pass\nr = R()\nr.___ = 'Mavi'", "check": lambda c, o, i: "renk" in c, "solution": "class R: pass\nr = R()\nr.renk = 'Mavi'", "hint": "Noktadan hemen sonra özellik ismini (renk) yerleştir."},
            {"msg": "**OOP:** `self` nesnenin kendisini temsil eden bir parametredir. Metotlarda ilk sırada mutlaka olmalıdır.", "task": "class R:\n def ses(___): print('Bip')", "check": lambda c, o, i: "self" in c, "solution": "class R:\n    def ses(self):\n        print('Bip')", "hint": "Kendi anlamına gelen self kelimesini kullan."},
            {"msg": "**OOP:** Nesnenin bir eylemini (Metot) çalıştırmak için nokta koyup metod ismini parantezleri ile yazarız.", "task": "class R:\n def s(self): pass\nr = R()\nr.___()", "check": lambda c, o, i: "s()" in c, "solution": "class R:\n    def s(self): pass\nr = R()\nr.s()", "hint": "Çağırılacak metot ismi s() fonksiyonudur."}
        ]},
        {"module_title": "8. Kalıcılık: Dosya Yönetimi", "exercises": [
            {"msg": "**Dosya:** Kaydetmek için `open()` kullanırız. **'w'** (write) yazma, **'r'** (read) okuma modudur.", "task": "f = ___('n.txt', '___')", "check": lambda c, o, i: "open" in c and "w" in c, "solution": "f = open('n.txt', 'w')", "hint": "Dosya açma fonksiyonu ve mod ismini düşün."},
            {"msg": "**Dosya:** `.write()` metodu içeriği dosyaya mühürler. Önceki içeriği siler.", "task": "f = open('t.txt', 'w')\nf.___('X')\nf.close()", "check": lambda c, o, i: "write" in c, "solution": "f = open('t.txt', 'w')\nf.write('X')\nf.close()", "hint": "write metodunu yerleştir."},
            {"msg": "**Dosya:** Okuma modunda dosyayı açmak için **'r'** kullanılır. Dosyayı sadece görmemizi sağlar.", "task": "f = open('t.txt', '___')", "check": lambda c, o, i: "r" in c, "solution": "f = open('t.txt', 'r')", "hint": "r harfini koy."},
            {"msg": "**Dosya:** `.read()` metodu dosyanın tüm içeriğini belleğe getirir.", "task": "f = open('t.txt', 'r')\nprint(f.___())", "check": lambda c, o, i: "read" in c, "solution": "f = open('t.txt', 'r')\nprint(f.read())", "hint": "read yazmalısın."},
            {"msg": "**Dosya:** `.close()` hayati önem taşır; dosyayı mutlaka kapatmalısın!", "task": "f = open('t.txt', 'r')\nf.___()", "check": lambda c, o, i: "close" in c, "solution": "f = open('t.txt', 'r')\nf.close()", "hint": "close kullan."}
        ]}
    ]

    # --- 7. QUEST BAR VE İLERLEME ---
    total_steps = 40
    curr_t_idx = (st.session_state.current_module * 5) + (st.session_state.current_exercise + 1)
    progress_perc = (curr_t_idx / total_steps) * 100
    st.markdown(f"""<div class="quest-container"><div style="display: flex; justify-content: space-between; font-weight: bold; color: #3a7bd5;"><span>📍 {training_data[st.session_state.current_module]['module_title']}</span><span>🐍 %{int(progress_perc)} İlerleme</span><span>🏆 {RUTBELER[min(sum(st.session_state.completed_modules), 8)]}</span></div><div class="quest-bar"><div class="quest-fill" style="width: {progress_perc}%;"></div></div></div>""", unsafe_allow_html=True)

    module_labels = [f"{'✅' if i < st.session_state.db_module else '📖'} Modül {i+1}" for i in range(min(st.session_state.db_module + 1, 8))]
    sel_mod_label = st.selectbox("Seviye Seç:", module_labels, index=min(st.session_state.current_module, len(module_labels)-1))
    new_m_idx = module_labels.index(sel_mod_label)
    if new_m_idx != st.session_state.current_module:
        st.session_state.update({'current_module': new_m_idx, 'current_exercise': 0, 'fail_count': 0, 'exercise_passed': False, 'current_potential_score': 20, 'feedback_msg': "", 'last_output': ""}); st.rerun()

    st.divider()
    curr_ex = training_data[st.session_state.current_module]["exercises"][st.session_state.current_exercise]
    is_review_mode = (st.session_state.current_module < st.session_state.db_module)

    c_box_i, c_box_m = st.columns([1, 4])
    with c_box_i: show_pito_img(140)
    with c_box_m:
        st.info(f"##### 🗣️ Pito'nun Notu:\n{curr_ex['msg']}")
        st.caption(f"Adım: {st.session_state.current_exercise + 1}/5 | {'🔒 İnceleme' if is_review_mode else f'🎁 Potansiyel: {st.session_state.current_potential_score} | ❌ Hata: {st.session_state.fail_count}/4'}")

    # --- 8. FEEDBACK VE ÇÖZÜM BLOĞU (PEDAGOJİK MÜHÜR) ---
    if st.session_state.feedback_msg:
        if "✅" in st.session_state.feedback_msg: st.success(st.session_state.feedback_msg)
        else: st.error(st.session_state.feedback_msg)

    # 3. Hatada ipucu (Yellow Box)
    if not st.session_state.exercise_passed and st.session_state.fail_count == 3:
        st.markdown(f'<div class="hint-guide"><div class="hint-header">💡 Pito\'dan Destek: İpucu</div>{curr_ex["hint"]}</div>', unsafe_allow_html=True)
    
    # 4. Hata veya İnceleme: TAM ÇÖZÜM (Red Box)
    if st.session_state.fail_count >= 4 or is_review_mode:
        st.markdown('<div class="solution-guide"><div class="solution-header">🔍 Doğru Çözüm Yolu (Tam Kod)</div></div>', unsafe_allow_html=True)
        st.code(curr_ex['solution'], language="python")

    # KOD PANELİ
    if not is_review_mode and st.session_state.fail_count < 4 and not st.session_state.exercise_passed:
        code = st_ace(value=curr_ex['task'], language="python", theme="dracula", font_size=14, height=180, key=f"ace_{st.session_state.current_module}_{st.session_state.current_exercise}", auto_update=True)
        if st.button("🔍 Kodumu Kontrol Et", use_container_width=True):
            if "___" in code: st.session_state.feedback_msg = "⚠️ Pito bekliyor: Lütfen önce boşluğu doldur!"; st.rerun()
            else:
                old_stdout, new_stdout = sys.stdout, StringIO(); sys.stdout = new_stdout
                try:
                    mock_env = {"print": print, "input": lambda x: "10", "int": int, "str": str, "len": len, "open": open, "range": range, "s": 10, "L": [10, 20], "d":{'ad':'Pito'}, "t":(1,2), "Robot": lambda: None, "R": lambda: None, "yas": 15, "isim": "Pito", "ad": "Pito"}
                    exec(code, mock_env); out = new_stdout.getvalue(); sys.stdout = old_stdout
                    if curr_ex.get('check', lambda c, o, i: True)(code, out, ""):
                        st.session_state.update({'feedback_msg': "✅ Muhteşem! Bu görevi başarıyla tamamladın.", 'last_output': out, 'exercise_passed': True})
                        ex_key = f"{st.session_state.current_module}_{st.session_state.current_exercise}"
                        if ex_key not in st.session_state.scored_exercises: st.session_state.total_score += st.session_state.current_potential_score; st.session_state.scored_exercises.add(ex_key); force_save()
                    else: raise Exception()
                except:
                    sys.stdout = old_stdout; st.session_state.fail_count += 1
                    st.session_state.current_potential_score = max(0, st.session_state.current_potential_score - 5)
                    if st.session_state.fail_count < 4:
                        st.session_state.feedback_msg = f"❌ 5 Puan Kaybettin! Küçük bir pürüz çıktı ama halledebilirsin. Kalan Ödül: {st.session_state.current_potential_score} Puan. Tekrar dene!"
                    else:
                        st.session_state.feedback_msg = "🌿 Bu seferlik puan kazanamadın ama tecrübe kazandın! Doğru çözümü yukarıdan inceleyip bir sonraki adıma geçelim."
                st.rerun()

    # --- 9. NAVİGASYON ---
    if st.session_state.exercise_passed or is_review_mode or st.session_state.fail_count >= 4:
        if st.session_state.last_output and not is_review_mode and st.session_state.fail_count < 4: st.code(st.session_state.last_output)
        cp, cn = st.columns(2)
        with cp:
            if st.session_state.current_exercise > 0:
                if st.button("⬅️ Önceki Adım"): st.session_state.update({'current_exercise': st.session_state.current_exercise - 1, 'exercise_passed': False, 'fail_count': 0, 'current_potential_score': 20, 'feedback_msg': "", 'last_output': ""}); st.rerun()
        with cn:
            if st.session_state.current_exercise < 4:
                if st.button("➡️ Sonraki Adım"): st.session_state.update({'current_exercise': st.session_state.current_exercise + 1, 'exercise_passed': False, 'fail_count': 0, 'current_potential_score': 20, 'feedback_msg': "", 'last_output': ""}); st.rerun()
            elif st.session_state.current_module < 7:
                if st.button("🏆 Modülü Bitir ve Devam Et"):
                    if not is_review_mode:
                        st.session_state.db_module += 1; st.session_state.db_exercise = 0; st.session_state.completed_modules[st.session_state.current_module] = True; force_save()
                    st.session_state.update({'current_module': st.session_state.current_module + 1, 'current_exercise': 0, 'exercise_passed': False, 'fail_count': 0, 'current_potential_score': 20, 'feedback_msg': ""}); st.rerun()