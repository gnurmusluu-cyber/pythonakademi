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
        font-weight: 500; font-size: 1.1rem; box-shadow: 4px 4px 15px rgba(0,0,0,0.05);
        line-height: 1.7;
    }
    .pito-bubble:after { content: ''; position: absolute; bottom: -20px; left: 40px; border-width: 20px 20px 0; border-style: solid; border-color: #3a7bd5 transparent; }
    .solution-guide { background-color: #fef2f2 !important; border: 2px solid #ef4444 !important; border-radius: 12px; padding: 20px; margin: 15px 0; color: #1e1e1e !important; }
    .hint-guide { background-color: #fffbeb !important; border: 2px solid #f59e0b !important; border-radius: 12px; padding: 20px; margin: 15px 0; color: #1e1e1e !important; }
    .leaderboard-card { background: linear-gradient(135deg, #1e1e1e, #2d2d2d); border: 1px solid #444; border-radius: 12px; padding: 10px; margin-bottom: 8px; color: white; }
    .stButton > button { width: 100%; border-radius: 12px; height: 3.5em; background: linear-gradient(45deg, #3a7bd5, #00d2ff) !important; color: white !important; font-weight: bold; border: none; }
    [data-testid="stTextInput"] { border: 2px solid transparent; transition: 0.3s; }
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

# --- 3. SESSION STATE ---
if 'is_logged_in' not in st.session_state:
    for k, v in {'student_name': "", 'student_no': "", 'student_class': "", 'completed_modules': [False]*8, 
                 'current_module': 0, 'current_exercise': 0, 'exercise_passed': False, 'total_score': 0, 
                 'scored_exercises': set(), 'db_module': 0, 'db_exercise': 0, 'is_logged_in': False, 
                 'current_potential_score': 20, 'celebrated': False, 'fail_count': 0, 
                 'feedback_msg': "", 'last_output': "", 'login_error': ""}.items():
        st.session_state[k] = v

def force_save():
    try:
        no = str(st.session_state.student_no).strip()
        df_all = get_db()
        if df_all.empty and st.session_state.db_module > 0: return 
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

# --- 4. LAYOUT TANIMLAMA (LİDERLİK TABLOSU SAĞDA) ---
col_main_app, col_sidebar_rank = st.columns([3, 1])

with col_sidebar_rank:
    db_data = get_db()
    st.markdown("### 🏅 Şampiyon Sınıf")
    if not db_data.empty:
        class_stats = db_data.groupby("Sınıf")["Puan"].sum().reset_index()
        if not class_stats.empty:
            top_class = class_stats.sort_values(by="Puan", ascending=False).head(1).iloc[0]
            st.markdown(f'<div class="leaderboard-card" style="background: linear-gradient(135deg, #FFD700, #DAA520); color: black;"><b>Sınıf: {top_class["Sınıf"]}</b><br>Toplam: {int(top_class["Puan"])} Puan</div>', unsafe_allow_html=True)
    st.markdown("---")
    tab_c, tab_s = st.tabs(["👥 Sınıfım", "🏫 Okul Geneli"])
    with tab_c:
        if st.session_state.is_logged_in:
            my_c_df = db_data[db_data["Sınıf"] == st.session_state.student_class].sort_values(by="Puan", ascending=False).head(5)
            for _, r in my_c_df.iterrows():
                st.markdown(f'<div class="leaderboard-card"><b>{r["Rütbe"]} {r["Öğrencinin Adı"]}</b><br>{int(r["Puan"])} Puan</div>', unsafe_allow_html=True)
        else: st.caption("Sınıfını görmek için giriş yapmalısın.")
    with tab_s:
        if not db_data.empty:
            for _, r in db_data.sort_values(by="Puan", ascending=False).head(10).iterrows():
                st.markdown(f'<div class="leaderboard-card"><b>{r["Rütbe"]} {r["Öğrencinin Adı"]} ({r["Sınıf"]})</b><br>{int(r["Puan"])} Puan</div>', unsafe_allow_html=True)

# --- 5. GİRİŞ EKRANI (SOL KOLONDA) ---
with col_main_app:
    if not st.session_state.is_logged_in:
        _, col_mid, _ = st.columns([1, 4, 1])
        with col_mid:
            st.markdown('<div class="pito-bubble">Merhaba Geleceğin Yazılımcısı! Ben <b>Pito</b>. Python dünyasına adım atmaya hazır mısın?</div>', unsafe_allow_html=True)
            show_pito_img(180)
            if st.session_state.login_error:
                st.error(st.session_state.login_error)
                st.markdown('<style>[data-testid="stTextInput"] { border: 2px solid #ef4444 !important; }</style>', unsafe_allow_html=True)
            in_no = st.text_input("Okul Numaran:", key="login_field").strip()
            if in_no:
                if not in_no.isdigit():
                    st.session_state.login_error = "⚠️ Okul numarası sadece rakamlardan oluşmalı!"; st.rerun()
                else:
                    user_data = db_data[db_data["Okul No"] == in_no]
                    if not user_data.empty:
                        row = user_data.iloc[0]
                        st.warning(f"🔍 **{row['Öğrencinin Adı']}** ({row['Sınıf']}), bu sen misin?")
                        c1, c2 = st.columns(2)
                        with c1:
                            if st.button("✅ Evet, Benim"):
                                m_v, e_v = int(row['Mevcut Modül']), int(row['Mevcut Egzersiz'])
                                st.session_state.update({'student_no': in_no, 'student_name': row["Öğrencinin Adı"], 'student_class': row["Sınıf"], 'total_score': int(row["Puan"]), 'db_module': m_v, 'db_exercise': e_v, 'current_module': m_v, 'current_exercise': e_v, 'completed_modules': [True if x == "1" else False for x in str(row["Tamamlanan Modüller"]).split(",")], 'is_logged_in': True, 'current_potential_score': 20, 'login_error': ""})
                                st.rerun()
                        with c2:
                            if st.button("❌ Hayır, Değilim"):
                                st.session_state.login_error = "🔴 Lütfen okul numaranı kontrol ederek tekrar gir!"; st.rerun()
                    else:
                        st.info("🌟 Seni henüz tanımıyorum. Python macerasına katılmak için kendini tanıtmalısın.")
                        in_name = st.text_input("Adın Soyadın:")
                        in_class = st.selectbox("Sınıfın:", SINIFLAR)
                        if st.button("✨ Kayıt Ol ve Başla"):
                            if in_name:
                                st.session_state.update({'student_no': in_no, 'student_name': in_name, 'student_class': in_class, 'is_logged_in': True, 'current_potential_score': 20, 'login_error': ""})
                                force_save(); st.rerun()
                            else: st.error("🔴 Lütfen ismini gir!")
        st.stop()

    # --- 6. EKSİKSİZ UZMAN EĞİTMEN MÜFREDATI (40 ADIM) ---
    training_data = [
        {"module_title": "1. print() ve Metin Dünyası", "exercises": [
            {"msg": "**Pito'nun Notu:** Python'da ekrana mesaj basmak için `print()` fonksiyonunu kullanırız. Yazdığın metinler tırnaklar (' ') arasında olmalıdır. Bu tırnaklar bilgisayara 'buradaki ifadeyi olduğu gibi ekrana yansıt' mesajını verir.\n\n**Görev:** Ekrana tam olarak **'Merhaba Pito'** yazmanı bekliyorum.", "task": "print('___')", "check": lambda c, o, i: "Merhaba Pito" in o, "solution": "print('Merhaba Pito')", "hint": "Metnin her iki tarafına da tek (') veya çift (\") tırnak koyduğundan emin ol."},
            {"msg": "**Pito'nun Notu:** Sayılar (Integer), metinlerden farklıdır; tırnak gerektirmezler. Eğer tırnak koyarsan Python onu sayı değil, bir metin olarak görür ve matematiksel işlem yapamaz.\n\n**Görev:** Boşluğa tırnak kullanmadan sadece **100** sayısını yaz.", "task": "print(___)", "check": lambda c, o, i: "100" in o, "solution": "print(100)", "hint": "Rakamları tırnaksız yazmalısın. Eğer '100' yazarsan bu bir sayı değil metin olur!"},
            {"msg": "**Pito'nun Notu:** Virgül (`,`) farklı veri tiplerini aynı satırda birleştirir ve araya otomatik bir boşluk koyar. Değişkenleri cümle içinde kullanmak için harika bir yoldur.\n\n**Görev:** 'Puan:' metni ile **100** sayısını yan yana bas.", "task": "print('Puan:', ___)", "check": lambda c, o, i: "100" in o, "solution": "print('Puan:', 100)", "hint": "Virgülden sonra sadece sayısal değeri yazmalısın."},
            {"msg": "**Pito'nun Notu:** `#` işareti Python'a 'Bu satırı görmezden gel' demektir. Buna 'Yorum Satırı' diyoruz. Sadece biz yazılımcıların not alması içindir.\n\n**Görev:** Satırın en başına **#** işaretini koyarak bu satırı etkisiz hale getir.", "task": "___ bu bir nottur", "check": lambda c, o, i: "#" in c, "solution": "# bu bir nottur", "hint": "Klavyeden diyez (#) işaretini satırın en başına yerleştir."},
            {"msg": "**Pito'nun Notu:** `\\n` (new line) kaçış karakteri metni alt satıra böler. Bu karakter Python'a 'burada satır başı yap' emri verir.\n\n**Görev:** 'Üst' ve 'Alt' kelimelerini alt alta getirmek için boşluğa **\\n** yaz.", "task": "print('Üst' + '___' + 'Alt')", "check": lambda c, o, i: "Üst\nAlt" in o, "solution": "print('Üst\\nAlt')", "hint": "Tırnaklar içerisine ters eğik çizgi (\\) ve n harfini birleşik yaz: \\n"}
        ]},
        {"module_title": "2. Hafıza: Değişkenler ve input()", "exercises": [
            {"msg": "**Pito'nun Notu:** Değişkenler hafızadaki kutulardır. `=` işareti bir 'atama operatörü'dür ve sağdaki değeri soldaki kutunun içine koyar.\n\n**Görev:** `yas` değişkenine sayısal olarak **15** değerini ata.", "task": "yas = ___", "check": lambda c, o, i: "15" in c, "solution": "yas = 15", "hint": "Eşittir işaretinden sonra sadece 15 yazmalısın."},
            {"msg": "**Pito'nun Notu:** Metin (String) verilerini saklarken tırnak şarttır. İsimlerde rakamla başlamamaya ve boşluk kullanmamaya dikkat etmelisin.\n\n**Görev:** `isim` değişkenine **'Pito'** metnini ata.", "task": "isim = '___'", "check": lambda c, o, i: "Pito" in o, "solution": "isim = 'Pito'", "hint": "Metni tırnaklar içerisine tam olarak Pito şeklinde yaz."},
            {"msg": "**Pito'nun Notu:** `input()` programı durdurur ve kullanıcıdan bir bilgi bekler. Python bu bilgiyi her zaman 'metin' (String) olarak algılar.\n\n**Görev:** Kullanıcıdan adını almak için boşluğa **input** fonksiyonunu yaz.", "task": "ad = ___('Adın: ')", "check": lambda c, o, i: "input" in c, "solution": "ad = input('Adın: ')", "hint": "Veri alma komutu olan input kelimesini kullan."},
            {"msg": "**Pito'nun Notu:** Sayıları metne çevirmemiz gerektiğinde (Casting) `str()` fonksiyonunu kullanırız. Bu, metinleri birleştirirken çok işe yarar.\n\n**Görev:** 10 sayısını metne çeviren **str** fonksiyonunu yaz.", "task": "print(___(10))", "check": lambda c, o, i: "str" in c, "solution": "print(str(10))", "hint": "String'in kısaltması olan str fonksiyonunu yerleştir."},
            {"msg": "**Pito'nun Notu:** Matematik yapabilmek için `input()` ile gelen metni `int()` fonksiyonu ile 'tam sayıya' çevirmelisin.\n\n**Görev:** Dış boşluğa **int**, içe **input** yazarak bir sayı girişi al.", "task": "n = ___(___('S: '))", "check": lambda c, o, i: "int" in c and "input" in c, "solution": "n = int(input('S: '))", "hint": "Fonksiyonları iç içe kullanmalısın: int(input())"}
        ]},
        {"module_title": "3. Karar Yapıları: If-Else Mantığı", "exercises": [
            {"msg": "**Pito'nun Notu:** `if` bloğu Python'ın beynidir. Eşitlik sorgusu yaparken `=` değil, mutlaka `==` kullanmalısın.\n\n**Görev:** Sayı 10'a eşitse 'OK' yazdıracak operatörü (**==**) yaz.", "task": "if 10 ___ 10: print('OK')", "check": lambda c, o, i: "==" in c, "solution": "if 10 == 10:", "hint": "Mantıksal kontrol için çift eşittir koy."},
            {"msg": "**Pito'nun Notu:** `else:` bloğu, 'if' şartı sağlanmadığında devreye giren son çaredir.\n\n**Görev:** Şart sağlanmazsa 'Hata' yazdıran bloğu tamamla. Boşluğa **else** yaz.", "task": "if 5 > 10: pass\n___: print('Hata')", "check": lambda c, o, i: "else" in c, "solution": "else:", "hint": "Sadece else: yazman yeterli."},
            {"msg": "**Pito'nun Notu:** Birden fazla ihtimal varsa `elif` kullanılır. Şartlar yukarıdan aşağıya doğru sırayla denetlenir.\n\n**Görev:** Puan 50'den büyükse 'Geçti' yazacak şartı eklemek için boşluğa **elif** yaz.", "task": "p = 60\nif p < 50: pass\n___ p > 50: print('Geçti')", "check": lambda c, o, i: "elif" in c, "solution": "elif p > 50:", "hint": "İkinci şart için elif komutunu kullan."},
            {"msg": "**Pito'nun Notu:** `and` (ve) her iki tarafın da doğru olmasını ister. `or` ise bir tanesinin doğru olmasıyla yetinir.\n\n**Görev:** İki tarafın da doğru olduğunu kontrol eden bağlacı (**and**) yaz.", "task": "if 1 == 1 ___ 2 == 2: print('OK')", "check": lambda c, o, i: "and" in c, "solution": "and", "hint": "İngilizcede ve anlamına gelen kelimeyi yaz."},
            {"msg": "**Pito'nun Notu:** `!=` operatörü 'eşit değilse' anlamına gelir.\n\n**Görev:** Sayı 0'a eşit değilse 'Var' yazdıran operatörü (**!=**) boşluğa koy.", "task": "s = 5\nif s ___ 0: print('Var')", "check": lambda c, o, i: "!=" in c, "solution": "if s != 0:", "hint": "Ünlem ve eşittiri birleştir: !="}
        ]},
        {"module_title": "4. Otomasyon: For ve While Döngüleri", "exercises": [
            {"msg": "**Pito'un Notu:** `for` döngüsü bir sayı aralığında adım adım ilerler. `range(5)` komutu 0'dan 4'e kadar sayı üretir.\n\n**Görev:** Döngüyü 5 kez döndürmek için boşluğa **range** yaz.", "task": "for i in ___(5): print(i)", "check": lambda c, o, i: "range" in c, "solution": "for i in range(5):", "hint": "Sayı üreticisi olan range() fonksiyonunu kullan."},
            {"msg": "**Pito'un Notu:** `while` döngüsü şart 'True' olduğu sürece döner. Sonsuz döngüye dikkat!\n\n**Görev:** i sıfır oldukça dönen döngüyü başlatmak için boşluğa **while** yaz.", "task": "i = 0\n___ i == 0: print('D'); i += 1", "check": lambda c, o, i: "while" in c, "solution": "while i == 0:", "hint": "Şartlı döngü komutu olan while kelimesini yaz."},
            {"msg": "**Pito'un Notu:** `break` döngünün 'acil çıkış' kapısıdır. Şart sağlandığı an döngüyü bitirir.\n\n**Görev:** i değeri 1 olduğunda döngüyü bitiren **break** komutunu yaz.", "task": "for i in range(5):\n if i == 1: ___\n print(i)", "check": lambda c, o, i: "break" in c, "solution": "break", "hint": "Döngüyü kırmak için break anahtar kelimesini kullan."},
            {"msg": "**Pito'un Notu:** `continue` ise o anki adımı pas geçer ve döngünün başına geri döner.\n\n**Görev:** 1 değerini atlamak için boşluğa **continue** yaz.", "task": "for i in range(3):\n if i == 1: ___\n print(i)", "check": lambda c, o, i: "continue" in c, "solution": "continue", "hint": "Atlamak için continue kelimesini kullan."},
            {"msg": "**Pito'un Notu:** Listelerde gezinmek için `in` anahtar kelimesini kullanırız.\n\n**Görev:** Listedeki her harfi çekmek için boşluğa **in** anahtarını yaz.", "task": "for x ___ ['A', 'B']: print(x)", "check": lambda c, o, i: "in" in c, "solution": "for x in", "hint": "Aitlik bildiren in kelimesini yerleştir."}
        ]},
        {"module_title": "5. Gruplama: Listeler (Veri Sepeti)", "exercises": [
            {"msg": "**Pito'nun Notu:** Listeler birden fazla veriyi tek kutuda tutar ve `[]` ile tanımlanır. Python'da saymaya her zaman 0'dan başlarız!\n\n**Görev:** Boşluğa sayısal olarak **10** değerini koyarak listeyi tamamla.", "task": "L = [___, 20]", "check": lambda c, o, i: "10" in c, "solution": "L = [10, 20]", "hint": "Listenin ilk elemanı için sadece 10 yaz."},
            {"msg": "**Pito'nun Notu:** İlk elemana ulaşmak için `[0]` indeksini kullanırız.\n\n**Görev:** İlk elemana (50) ulaşmak için boşluğa **0** yaz.", "task": "L = [50, 60]\nprint(L[___])", "check": lambda c, o, i: "50" in o, "solution": "L[0]", "hint": "İlk indeks her zaman 0'dır."},
            {"msg": "**Pito'nun Notu:** `.append()` metodu listenin sonuna yeni bir eleman ekler.\n\n**Görev:** Listeye 30 ekleyen **append** metodunu boşluğa yaz.", "task": "L = [10]\nL.___ (30)", "check": lambda c, o, i: "append" in c, "solution": "L.append(30)", "hint": "Ekleme metodu olan append kelimesini kullan."},
            {"msg": "**Pito'nun Notu:** `len()` fonksiyonu listenin içindeki eleman sayısını bize verir.\n\n**Görev:** Boşluğa **len** yazarak listenin boyutunu ekrana bas.", "task": "L = [1, 2, 3]\nprint(___(L))", "check": lambda c, o, i: "3" in o, "solution": "len(L)", "hint": "Eleman sayısını ölçen len fonksiyonunu yaz."},
            {"msg": "**Pito'nun Notu:** `.pop()` metodu listenin en sonundaki elemanı sepetten çıkarır.\n\n**Görev:** Son elemanı silen **pop** metodunu boşluğa yerleştir.", "task": "L = [1, 2]\nL.___()", "check": lambda c, o, i: "pop" in c, "solution": "L.pop()", "hint": "Pop kelimesini yazmalısın."}
        ]},
        {"module_title": "6. Fonksiyonlar ve Sözlükler", "exercises": [
            {"msg": "**Pito'un Notu:** Fonksiyonlar tekrarı önler. `def` (tanımla) kelimesi ile kurulur.\n\n**Görev:** 'pito' fonksiyonunu tanımlayan **def** kelimesini boşluğa yaz.", "task": "___ pito(): print('Hi')", "check": lambda c, o, i: "def" in c, "solution": "def pito():", "hint": "Fonksiyon anahtarı def kelimesidir."},
            {"msg": "**Pito'un Notu:** **Sözlükler (Dictionary)**, `{anahtar: değer}` çiftleriyle çalışır.\n\n**Görev:** 'ad' anahtarına karşılık gelen değer boşluğuna **'Pito'** yaz.", "task": "d = {'ad': '___'}", "check": lambda c, o, i: "Pito" in o, "solution": "d = {'ad': 'Pito'}", "hint": "Tırnaklar içine Pito yaz."},
            {"msg": "**Pito'un Notu:** **Tuple**, listeye benzer ama içeriği değiştirilemez. `()` ile kurulur.\n\n**Görev:** Boşluğa sayısal olarak **1** yazarak demeti oluştur.", "task": "t = (___, 2)", "check": lambda c, o, i: "1" in c, "solution": "t = (1, 2)", "hint": "Eksik olan 1 rakamını koy."},
            {"msg": "**Pito'un Notu:** `.keys()` metodu sözlükteki tüm etiketleri bir liste halinde bize sunar.\n\n**Görev:** Boşluğa **keys** yazarak anahtarları çek.", "task": "d = {'a':1}\nprint(d.___())", "check": lambda c, o, i: "keys" in c, "solution": "d.keys()", "hint": "Keys kelimesini düşün."},
            {"msg": "**Pito'un Notu:** `return` ifadesi fonksiyonun ürettiği sonucu dışarıya fırlatır.\n\n**Görev:** 5 sonucunu döndüren fonksiyon için boşluğa **return** yaz.", "task": "def f(): ___ 5", "check": lambda c, o, i: "return" in c, "solution": "return 5", "hint": "Geri döndürme komutu return'dür."}
        ]},
        {"module_title": "7. OOP: Nesne Tabanlı Dünya", "exercises": [
            {"msg": "**Pito'un Notu:** `class` bir taslaktır. Ondan kopyalar yani 'Nesneler' (Object) üretiriz.\n\n**Görev:** 'Robot' isminde bir kalıp oluşturmak için boşluğa **class** yaz.", "task": "___ Robot: pass", "check": lambda c, o, i: "class" in c, "solution": "class Robot:", "hint": "Kalıp tanımlamak için class yazmalısın."},
            {"msg": "**Pito'un Notu:** Kalıptan nesne üretmek için sınıf ismini parantezlerle `()` çağırırız.\n\n**Görev:** Robot kalıbından r nesnesi üretmek için boşluğa **Robot()** yaz.", "task": "class Robot: pass\nr = ___", "check": lambda c, o, i: "Robot()" in c, "solution": "r = Robot()", "hint": "Sınıf isminin sonuna parantezleri ekle."},
            {"msg": "**Pito'un Notu:** Nesnelerin özellikleri nokta (`.`) yardımıyla atanır.\n\n**Görev:** r nesnesinin **renk** özelliğini 'Mavi' yapmak için boşluğa **renk** yaz.", "task": "class R: pass\nr = R()\nr.___ = 'Mavi'", "check": lambda c, o, i: "renk" in c, "solution": "r.renk = 'Mavi'", "hint": "Noktadan sonra renk özelliğini yaz."},
            {"msg": "**Pito'un Notu:** `self` nesnenin kendisini temsil eder. Metotlarda ilk sırada olmalıdır.\n\n**Görev:** Metod parantezi içine **self** anahtarını yaz.", "task": "class R:\n def ses(___): print('Bip')", "check": lambda c, o, i: "self" in c, "solution": "def ses(self):", "hint": "Self kelimesini yerleştir."},
            {"msg": "**Pito'un Notu:** Nesnenin bir eylemini çalıştırmak için nokta koyup metod ismini yazarız.\n\n**Görev:** r nesnesinin s() metodunu çalıştırmak için boşluğa **s()** yaz.", "task": "class R:\n def s(self): pass\nr = R()\nr.___()", "check": lambda c, o, i: "s()" in c, "solution": "r.s()", "hint": "Metot ismi s() fonksiyonudur."}
        ]},
        {"module_title": "8. Kalıcılık: Dosya Yönetimi", "exercises": [
            {"msg": "**Pito'un Notu:** Program kapandığında veriler silinir. Saklamak için `open()` kullanırız. **'w'** (write) modu yazmak içindir.\n\n**Görev:** n.txt dosyasını yazma modunda açmak için boşluklara **open** ve **w** yaz.", "task": "f = ___('n.txt', '___')", "check": lambda c, o, i: "open" in c and "w" in c, "solution": "open('n.txt', 'w')", "hint": "Fonksiyon open, mod ise w olmalı."},
            {"msg": "**Pito'un Notu:** `.write()` metodu veriyi dosyanın içine kalıcı olarak mühürler.\n\n**Görev:** Dosyaya 'X' yazmak için ilgili boşluğa **write** metodunu yaz.", "task": "f = open('t.txt', 'w')\nf.___('X')\nf.close()", "check": lambda c, o, i: "write" in c, "solution": "f.write('X')", "hint": "Write metodunu yerleştir."},
            {"msg": "**Pito'un Notu:** Kayıtlı verileri okumak için **'r'** (read) modu kullanılır.\n\n**Görev:** Dosyayı okuma modunda açmak için boşluğa **r** harfini koy.", "task": "f = open('t.txt', '___')", "check": lambda c, o, i: "r" in c, "solution": "f = open('t.txt', 'r')", "hint": "Okuma modu r harfidir."},
            {"msg": "**Pito'un Notu:** `.read()` metodu dosyanın içeriğini belleğe getirir.\n\n**Görev:** İçeriği ekrana basmak için boşluğa **read** metodunu yaz.", "task": "f = open('t.txt', 'r')\nprint(f.___())", "check": lambda c, o, i: "read" in c, "solution": "f.read()", "hint": "Read metodunu kullan."},
            {"msg": "**Pito'un Notu:** `.close()` hayati önem taşır; dosyayı mutlaka kapatmalısın.\n\n**Görev:** Dosyayı kapatmak için boşluğa **close** komutunu yaz.", "task": "f = open('t.txt', 'r')\nf.___()", "check": lambda c, o, i: "close" in c, "solution": "f.close()", "hint": "Kapatma komutu close'dur."}
        ]}
    ]

    # --- 7. QUEST BAR (ÜST PANEL) ---
    total_steps = 40
    current_step_count = (st.session_state.current_module * 5) + (st.session_state.current_exercise + 1)
    progress_perc = (current_step_count / total_steps) * 100
    st.markdown(f"""<div class="quest-container"><div style="display: flex; justify-content: space-between; font-weight: bold; color: #3a7bd5; margin-bottom: 5px;"><span>📍 {training_data[st.session_state.current_module]['module_title']}</span><span>🐍 Python Macerası: %{int(progress_perc)}</span><span>🏆 {RUTBELER[min(sum(st.session_state.completed_modules), 8)]}</span></div><div class="quest-bar"><div class="quest-fill" style="width: {progress_perc}%;"></div></div></div>""", unsafe_allow_html=True)

    # --- 8. ANA ARAYÜZ ---
    selectable_indices = list(range(min(st.session_state.db_module + 1, 8)))
    module_labels = [f"{'✅' if i < st.session_state.db_module else '📖'} Modül {i+1}" for i in selectable_indices]

    st.markdown(f"#### 👋 Hoş geldin **{st.session_state.student_name}** | ⭐ Toplam Puan: {int(st.session_state.total_score)}")
    sel_mod_label = st.selectbox("Seviye Seç:", module_labels, index=min(st.session_state.current_module, len(module_labels)-1))
    new_m_idx = selectable_indices[module_labels.index(sel_mod_label)]
    if new_m_idx != st.session_state.current_module:
        st.session_state.update({'current_module': new_m_idx, 'current_exercise': 0, 'fail_count': 0, 'exercise_passed': False, 'current_potential_score': 20, 'feedback_msg': "", 'last_output': ""}); st.rerun()

    st.divider()
    curr_ex = training_data[st.session_state.current_module]["exercises"][st.session_state.current_exercise]
    is_review_mode = (st.session_state.current_module < st.session_state.db_module)

    # PİTO PANELİ
    c_img_not, c_msg_not = st.columns([1, 4])
    with c_img_not: show_pito_img(140)
    with c_msg_not:
        st.info(f"##### 🗣️ Pito'nun Notu:\n{curr_ex['msg']}")
        st.caption(f"Adım: {st.session_state.current_exercise + 1}/5 | {'🔒 Arşiv Modu' if is_review_mode else f'🎁 Kazanacağın: {st.session_state.current_potential_score} Puan | ❌ Hata: {st.session_state.fail_count}/4'}")

    # --- FEEDBACK PANELİ (ACE EDITOR ÜSTÜ) ---
    if st.session_state.feedback_msg:
        if "✅" in st.session_state.feedback_msg: st.success(st.session_state.feedback_msg)
        else: st.error(st.session_state.feedback_msg)

    # 4. HATA VEYA İNCELEME MODU: İpucu kalkar, çözüm kutusu gelir.
    if not st.session_state.exercise_passed and st.session_state.fail_count == 3:
        st.markdown(f'<div class="hint-guide"><div class="hint-header">💡 Pito\'dan Destek: İpucu</div>{curr_ex["hint"]}</div>', unsafe_allow_html=True)
    elif (not st.session_state.exercise_passed and st.session_state.fail_count >= 4) or is_review_mode:
        st.markdown('<div class="solution-guide"><div class="solution-header">🔍 Doğru Çözüm Yolu</div></div>', unsafe_allow_html=True); st.code(curr_ex['solution'], language="python")

    # KOD PANELİ
    if is_review_mode:
        pass # Çözüm yukarıda sergilendi
    else:
        if st.session_state.fail_count < 4 and not st.session_state.exercise_passed:
            code = st_ace(value=curr_ex['task'], language="python", theme="dracula", font_size=14, height=180, key=f"ace_{st.session_state.current_module}_{st.session_state.current_exercise}", auto_update=True)
            if st.button("🔍 Kodumu Kontrol Et", use_container_width=True):
                if "___" in code: st.session_state.feedback_msg = "⚠️ Pito bekliyor: Lütfen önce boşluğu doldur!"; st.rerun()
                else:
                    old_stdout, new_stdout = sys.stdout, StringIO(); sys.stdout = new_stdout
                    try:
                        exec(code, {"print": print, "input": lambda x: "10", "range": range, "s": 10, "L": [50, 60], "d":{'ad':'Pito'}, "t":(1,2), "Robot": lambda: None, "R": lambda: None})
                        out = new_stdout.getvalue(); sys.stdout = old_stdout
                        if curr_ex.get('check', lambda c, o, i: True)(code, out, ""):
                            st.session_state.update({'feedback_msg': "✅ Muhteşem! Görevi başarıyla tamamladın.", 'last_output': out, 'exercise_passed': True})
                            ex_key = f"{st.session_state.current_module}_{st.session_state.current_exercise}"
                            if ex_key not in st.session_state.scored_exercises: st.session_state.total_score += st.session_state.current_potential_score; st.session_state.scored_exercises.add(ex_key); force_save()
                        else: raise Exception()
                    except:
                        sys.stdout = old_stdout; st.session_state.fail_count += 1; st.session_state.current_potential_score = max(0, st.session_state.current_potential_score - 5)
                        if st.session_state.fail_count == 1: st.session_state.feedback_msg = "🌟 Harika bir başlangıç! Küçük bir pürüz çıktı. (Potansiyel: 15 Puan)."
                        elif st.session_state.fail_count == 2: st.session_state.feedback_msg = "💪 Pes etmek yok! Hatalar en iyi öğretmenlerdir. (Potansiyel: 10 Puan)."
                        elif st.session_state.fail_count == 3: st.session_state.feedback_msg = "🚀 Yolun sonuna yaklaştın! İpucuna bakarak son şansını kullanabilirsin. (Potansiyel: 5 Puan)."
                        elif st.session_state.fail_count >= 4: st.session_state.exercise_passed = True; st.session_state.feedback_msg = "🌿 Bu seferlik puan kazanamadın ama tecrübe kazandın! Doğru çözümü inceleyip geçelim."
                    st.rerun()

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