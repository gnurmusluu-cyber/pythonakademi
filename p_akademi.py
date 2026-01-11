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
    
    /* Quest Bar Tasarımı */
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

# Liderlik Tablosu Fonksiyonu (Sidebar için)
def draw_sidebar_rankings():
    df_lb = get_db()
    with st.sidebar:
        st.markdown("### 🏅 Şampiyon Sınıf")
        if not df_lb.empty:
            class_stats = df_lb.groupby("Sınıf")["Puan"].sum().reset_index()
            if not class_stats.empty:
                top_class = class_stats.sort_values(by="Puan", ascending=False).head(1).iloc[0]
                st.markdown(f"""<div class="leaderboard-card" style="background: linear-gradient(135deg, #FFD700, #DAA520); color: black;"><b>Sınıf: {top_class['Sınıf']}</b><br>Toplam: {int(top_class['Puan'])} Puan</div>""", unsafe_allow_html=True)
        
        st.markdown("---")
        t_c, t_s = st.tabs(["👥 Sınıfım", "🏫 Okul"])
        with t_c:
            if st.session_state.is_logged_in:
                my_c = df_lb[df_lb["Sınıf"] == st.session_state.student_class].sort_values(by="Puan", ascending=False).head(5)
                for _, r in my_c.iterrows():
                    st.markdown(f'<div class="leaderboard-card"><b>{r["Rütbe"]} {r["Öğrencinin Adı"]}</b><br>{int(r["Puan"])} Puan</div>', unsafe_allow_html=True)
            else: st.caption("Sınıfını görmek için giriş yap.")
        with t_s:
            if not df_lb.empty:
                for _, r in df_lb.sort_values(by="Puan", ascending=False).head(10).iterrows():
                    st.markdown(f'<div class="leaderboard-card"><b>{r["Rütbe"]} {r["Öğrencinin Adı"]} ({r["Sınıf"]})</b><br>{int(r["Puan"])} Puan</div>', unsafe_allow_html=True)

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

# Liderlik tablolarını her zaman sidebar'da çiz
draw_sidebar_rankings()

# --- 4. GİRİŞ EKRANI ---
if not st.session_state.is_logged_in:
    _, col_mid, _ = st.columns([1, 2, 1])
    with col_mid:
        st.markdown('<div class="pito-bubble">Merhaba Geleceğin Yazılımcısı! Ben <b>Pito</b>. Python dünyasında muhteşem bir keşfe çıkacağız. Hazır mısın?</div>', unsafe_allow_html=True)
        show_pito_img(180)
        
        if st.session_state.login_error:
            st.error(st.session_state.login_error)
            st.markdown('<style>[data-testid="stTextInput"] { border: 2px solid #ef4444 !important; }</style>', unsafe_allow_html=True)

        in_no = st.text_input("Okul Numaran:", key="login_field").strip()
        
        if in_no:
            if not in_no.isdigit():
                st.session_state.login_error = "⚠️ Okul numarası sadece rakamlardan oluşmalı!"; st.rerun()
            else:
                df = get_db()
                user_data = df[df["Okul No"] == in_no]
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
                            st.session_state.login_error = "🔴 Lütfen okul numaranı tekrar kontrol ederek gir!"; st.rerun()
                else:
                    st.info("🌟 Seni henüz tanımıyorum. Python macerasına katılmak için kendini tanıtır mısın?")
                    in_name = st.text_input("Adın Soyadın:")
                    in_class = st.selectbox("Sınıfın:", SINIFLAR)
                    if st.button("✨ Kayıt Ol ve Başla"):
                        if in_name:
                            st.session_state.update({'student_no': in_no, 'student_name': in_name, 'student_class': in_class, 'is_logged_in': True, 'current_potential_score': 20, 'login_error': ""})
                            force_save(); st.rerun()
                        else: st.error("🔴 Lütfen ismini gir!")
    st.stop()

# --- 5. EKSİKSİZ UZMAN EĞİTMEN MÜFREDATI ---
training_data = [
    {"module_title": "1. İletişim: print() ve Çıktı Dünyası", "exercises": [
        {"msg": "**Eğitmen Notu:** Python'da ekrana mesaj basmak için `print()` kullanılır. Metinleri mutlaka tırnak (' ') içine almalısın.\n\n**Görev:** Ekrana tam olarak **'Merhaba Pito'** yazdır.", "task": "print('___')", "check": lambda c, o, i: "Merhaba Pito" in o, "solution": "print('Merhaba Pito')", "hint": "Metni tırnak içine almayı unutma."},
        {"msg": "**Eğitmen Notu:** Sayılar tırnak gerektirmez. Onlarla matematik yapabiliriz.\n\n**Görev:** Ekrana tırnaksız şekilde sadece **100** sayısını yaz.", "task": "print(___)", "check": lambda c, o, i: "100" in o, "solution": "print(100)", "hint": "Sayıları yazarken tırnak kullanma!"},
        {"msg": "**Eğitmen Notu:** Virgül (`,`) farklı verileri birleştirir.\n\n**Görev:** 'Puan:' metni ile **100** sayısını yanyana bas.", "task": "print('Puan:', ___)", "check": lambda c, o, i: "100" in o, "solution": "print('Puan:', 100)", "hint": "Virgülden sonra 100 yaz."},
        {"msg": "**Eğitmen Notu:** `#` işareti 'yorum satırı' demektir. Bilgisayar bu satırı okumaz.\n\n**Görev:** Satırın en başına **#** işaretini koy.", "task": "___ bu bir nottur", "check": lambda c, o, i: "#" in c, "solution": "# bu bir nottur", "hint": "Sadece diyez (#) işareti koy."},
        {"msg": "**Eğitmen Notu:** `\\n` metni alt satıra böler.\n\n**Görev:** Boşluğa **\\n** yazarak kelimeleri alt alta getir.", "task": "print('Üst' + '___' + 'Alt')", "check": lambda c, o, i: "Üst\nAlt" in o, "solution": "print('Üst\\nAlt')", "hint": "Tırnaklar içine \\n yazmalısın."}
    ]},
    {"module_title": "2. Hafıza: Değişkenler ve input()", "exercises": [
        {"msg": "**Pito'nun Notu:** Değişkenler hafızadaki kutulardır. `=` işareti ile kutuya değer koyarız.\n\n**Görev:** `yas` değişkenine sayısal olarak **15** değerini ata.", "task": "yas = ___", "check": lambda c, o, i: "15" in c, "solution": "yas = 15", "hint": "Eşittir işaretinden sonra 15 yaz."},
        {"msg": "**Pito'nun Notu:** Metin atarken tırnak şarttır.\n\n**Görev:** `isim` kutusuna **'Pito'** metnini ata.", "task": "isim = '___'", "check": lambda c, o, i: "Pito" in o, "solution": "isim = 'Pito'", "hint": "Tırnaklar arasına Pito yaz."},
        {"msg": "**Pito'nun Notu:** `input()` kullanıcıdan bilgi bekler.\n\n**Görev:** Boşluğa **input** yazarak giriş komutu oluştur.", "task": "ad = ___('Adın: ')", "check": lambda c, o, i: "input" in c, "solution": "ad = input('Adın: ')", "hint": "input kelimesini kullan."},
        {"msg": "**Pito'nun Notu:** `str()` sayıları metne çevirir.\n\n**Görev:** 10 sayısını metne çeviren **str** fonksiyonunu yaz.", "task": "print(___(10))", "check": lambda c, o, i: "str" in c, "solution": "print(str(10))", "hint": "str yazmalısın."},
        {"msg": "**Pito'nun Notu:** `int()` metni sayıya çevirir. Matematik için şarttır.\n\n**Görev:** Dış boşluğa **int**, içe **input** yazarak bir sayı girişi al.", "task": "n = ___(___('S: '))", "check": lambda c, o, i: "int" in c and "input" in c, "solution": "n = int(input('S: '))", "hint": "int(input()) yapısını kur."}
    ]},
    {"module_title": "3. Karar Yapıları: If-Else Mantığı", "exercises": [
        {"msg": "**Konu:** `if` (eğer) şart kontrolüdür. Eşitlik için `==` kullanılır.\n\n**Görev:** Sayı 10'a eşitse 'OK' yazdıracak operatörü (**==**) boşluğa yaz.", "task": "if 10 ___ 10: print('OK')", "check": lambda c, o, i: "==" in c, "solution": "if 10 == 10:", "hint": "Çift eşittir kullan."},
        {"msg": "**Konu:** Şart yanlışsa `else:` bloğu çalışır.\n\n**Görev:** Boşluğa **else** yazarak alternatif yolu tamamla.", "task": "if 5 > 10: pass\n___: print('Hata')", "check": lambda c, o, i: "else" in c, "solution": "else:", "hint": "Sadece else: yaz."},
        {"msg": "**Konu:** `elif` birden fazla şartı denetler.\n\n**Görev:** Puan 50'den büyükse 'Geçti' yazacak şartı eklemek için boşluğa **elif** yaz.", "task": "p = 60\nif p < 50: pass\n___ p > 50: print('Geçti')", "check": lambda c, o, i: "elif" in c, "solution": "elif p > 50:", "hint": "elif kullanmalısın."},
        {"msg": "**Konu:** `and` (ve) iki tarafın da doğru olmasını bekler.\n\n**Görev:** Boşluğa **and** yazarak iki şartı birleştir.", "task": "if 1 == 1 ___ 2 == 2: print('OK')", "check": lambda c, o, i: "and" in c, "solution": "and", "hint": "ve anlamına gelen and yaz."},
        {"msg": "**Konu:** `!=` eşit değilse demektir.\n\n**Görev:** s değişkeni 0'a eşit değilse 'Var' yazdıracak operatörü (**!=**) boşluğa koy.", "task": "s = 5\nif s ___ 0: print('Var')", "check": lambda c, o, i: "!=" in c, "solution": "if s != 0:", "hint": "!= operatörünü koy."}
    ]},
    {"module_title": "4. Otomasyon: For ve While Döngüleri", "exercises": [
        {"msg": "**Konu:** `for` döngüsü tekrar yapar. `range(5)` sayıları üretir.\n\n**Görev:** Boşluğa **range** yazarak döngüyü kur.", "task": "for i in ___(5): print(i)", "check": lambda c, o, i: "range" in c, "solution": "for i in range(5):", "hint": "range yaz."},
        {"msg": "**Konu:** `while` şart doğru oldukça döner.\n\n**Görev:** Boşluğa **while** yazarak döngüyü başlat.", "task": "i = 0\n___ i == 0: print('Dönüyor'); i += 1", "check": lambda c, o, i: "while" in c, "solution": "while i == 0:", "hint": "while ile başlat."},
        {"msg": "**Konu:** `break` döngüyü bitirir.\n\n**Görev:** i değeri 1 olduğunda döngüyü bitiren **break** komutunu yaz.", "task": "for i in range(5):\n if i == 1: ___\n print(i)", "check": lambda c, o, i: "break" in c, "solution": "break", "hint": "break yaz."},
        {"msg": "**Konu:** `continue` o adımı atlar.\n\n**Görev:** 1 değerini atlayan **continue** komutunu yaz.", "task": "for i in range(3):\n if i == 1: ___\n print(i)", "check": lambda c, o, i: "continue" in c, "solution": "continue", "hint": "continue yaz."},
        {"msg": "**Konu:** Listede gezinmek için `in` kullanılır.\n\n**Görev:** Listedeki her harfi basmak için **in** anahtarını yaz.", "task": "for x ___ ['A', 'B']: print(x)", "check": lambda c, o, i: "in" in c, "solution": "for x in", "hint": "in kullan."}
    ]},
    {"module_title": "5. Veri Sepeti: Listeler", "exercises": [
        {"msg": "**Konu:** Listeler `[]` içine yazılır.\n\n**Görev:** Boşluğa **10** yazarak listeyi kur.", "task": "L = [___, 20]", "check": lambda c, o, i: "10" in c, "solution": "L = [10, 20]", "hint": "Sadece 10 yaz."},
        {"msg": "**Konu:** Saymaya 0'dan başlarız! `[0]` ilk elemanı verir.\n\n**Görev:** İlk elemana (50) erişmek için **0** yaz.", "task": "L = [50, 60]\nprint(L[___])", "check": lambda c, o, i: "50" in o, "solution": "L[0]", "hint": "İlk indeks 0'dır."},
        {"msg": "**Konu:** `.append()` sonuna yeni eleman ekler.\n\n**Görev:** Boşluğa **append** yazarak listeyi büyüt.", "task": "L = [10]\nL.___ (30)", "check": lambda c, o, i: "append" in c, "solution": "L.append(30)", "hint": "append yaz."},
        {"msg": "**Konu:** `len()` boyut ölçer.\n\n**Görev:** Boşluğa **len** yazarak eleman sayısını bul.", "task": "L = [1, 2, 3]\nprint(___(L))", "check": lambda c, o, i: "3" in o, "solution": "len(L)", "hint": "len kullan."},
        {"msg": "**Konu:** `.pop()` son elemanı atar.\n\n**Görev:** Boşluğa **pop** yazarak son elemanı sil.", "task": "L = [1, 2]\nL.___()", "check": lambda c, o, i: "pop" in c, "solution": "L.pop()", "hint": "pop yaz."}
    ]},
    {"module_title": "6. Modülerlik: Fonksiyonlar ve Sözlükler", "exercises": [
        {"msg": "**Pito'nun Notu:** **Sözlükler (Dictionary)**, veri çiftlerini `{anahtar: değer}` şeklinde tutar.\n\n**Görev:** 'ad' anahtarına karşılık gelen değer boşluğuna **'Pito'** yaz.", "task": "d = {'ad': '___'}", "check": lambda c, o, i: "Pito" in o, "solution": "d = {'ad': 'Pito'}", "hint": "Pito yaz."},
        {"msg": "**Konu:** **Tuple**, listeye benzer ama `()` ile kurulur ve değiştirilemez!\n\n**Görev:** Boşluğa sadece **1** yaz.", "task": "t = (___, 2)", "check": lambda c, o, i: "1" in c, "solution": "t = (1, 2)", "hint": "Boşluğa 1 yaz."},
        {"msg": "**Konu:** `.keys()` metodu sözlükteki tüm anahtarları listeler.\n\n**Görev:** Boşluğa **keys** yaz.", "task": "d = {'a':1}\nprint(d.___())", "check": lambda c, o, i: "keys" in c, "solution": "d.keys()", "hint": "keys yaz."},
        {"msg": "**Konu:** `return` sonucu dışarı fırlatır.\n\n**Görev:** Boşluğa **return** yaz.", "task": "def f(): ___ 5", "check": lambda c, o, i: "return" in c, "solution": "return 5", "hint": "return kullan."},
        {"msg": "**Konu:** `def` fonksiyon tanımlar.\n\n**Görev:** Boşluğa **def** yazarak 'pito' fonksiyonunu başlat.", "task": "___ pito(): print('Hi')", "check": lambda c, o, i: "def" in c, "solution": "def pito():", "hint": "def yaz."}
    ]},
    {"module_title": "7. OOP: Nesne Tabanlı Dünya", "exercises": [
        {"msg": "**Pito'nun Notu:** `class` bir fabrikadır (kalıptır). Nesne ise o fabrikadan çıkan üründür.\n\n**Görev:** Bir Robot kalıbı oluşturmak için boşluğa **class** anahtar kelimesini yaz.", "task": "___ Robot: pass", "check": lambda c, o, i: "class" in c, "solution": "class Robot:", "hint": "Sınıf için class yaz."},
        {"msg": "**Konu:** Kalıptan nesne üretmek için sınıf ismini fonksiyon gibi çağırırız.\n\n**Görev:** Robot kalıbından r isminde bir ürün almak için boşluğa **Robot()** yaz.", "task": "class Robot: pass\nr = ___", "check": lambda c, o, i: "Robot()" in c, "solution": "r = Robot()", "hint": "Robot() yazmalısın."},
        {"msg": "**Konu:** Nesnelerin özellikleri nokta (`.`) ile atanır.\n\n**Görev:** r nesnesinin **renk** özelliğini 'Mavi' yapmak için boşluğa **renk** yaz.", "task": "class R: pass\nr = R()\nr.___ = 'Mavi'\nprint(r.renk)", "check": lambda c, o, i: "renk" in c, "solution": "r.renk = 'Mavi'", "hint": "Noktadan sonra renk yaz."},
        {"msg": "**Pito'nun Notu:** `self` nesnenin kendisidir. Sınıf içindeki metodlarda mutlaka bulunmalıdır.\n\n**Görev:** Metod parantezi içine **self** anahtarını yaz.", "task": "class R:\n def ses(___): print('Bip')", "check": lambda c, o, i: "self" in c, "solution": "def ses(self):", "hint": "self yaz."},
        {"msg": "**Konu:** Nesnenin bir metodunu çalıştırmak için nesne isminden sonra nokta koyup metod ismini yazarız.\n\n**Görev:** r nesnesinin s() metodunu çalıştırmak için boşluğa **s()** yaz.", "task": "class R:\n def s(self): print('X')\nr = R()\nr.___()", "check": lambda c, o, i: "s()" in c, "solution": "r.s()", "hint": "Metot ismi s()."}
    ]},
    {"module_title": "8. Kalıcılık: Dosya Yönetimi", "exercises": [
        {"msg": "**Konu:** Program kapanınca veriler silinir. Saklamak için `open()` fonksiyonuyla dosya açarız. **'w'** (write) kipi yazmak içindir.\n\n**Görev:** n.txt dosyasını yazma modunda açmak için ilk boşluğa **open**, mod için ikinci boşluğa **w** yaz.", "task": "f = ___('n.txt', '___')", "check": lambda c, o, i: "open" in c and "w" in c, "solution": "open('n.txt', 'w')", "hint": "open ve w kullan."},
        {"msg": "**Konu:** `.write()` metodu veriyi dosyaya mühürler.\n\n**Görev:** Dosyaya 'X' yazmak için boşluğa **write** yaz.", "task": "f = open('t.txt', 'w')\nf.___('X')\nf.close()", "check": lambda c, o, i: "write" in c, "solution": "f.write('X')", "hint": "write yaz."},
        {"msg": "**Konu:** Okuma için **'r'** (read) modu kullanılır.\n\n**Görev:** Dosyayı okuma modunda açmak için boşluğa **r** harfini koy.", "task": "f = open('t.txt', '___')", "check": lambda c, o, i: "r" in c, "solution": "f = open('t.txt', 'r')", "hint": "r yaz."},
        {"msg": "**Konu:** `.read()` metodu içeriği çeker.\n\n**Görev:** İçeriği almak için boşluğa **read** yaz.", "task": "f = open('t.txt', 'r')\nprint(f.___())", "check": lambda c, o, i: "read" in c, "solution": "f.read()", "hint": "read yaz."},
        {"msg": "**Konu:** `.close()` hayati önem taşır; dosyayı kapatmalısın.\n\n**Görev:** Dosyayı kapatmak için boşluğa **close** yaz.", "task": "f = open('t.txt', 'r')\nf.___()", "check": lambda c, o, i: "close" in c, "solution": "f.close()", "hint": "close yaz."}
    ]}
]

# --- 6. QUEST BAR (ÜST PANEL) ---
total_steps = 40
current_step_count = (st.session_state.current_module * 5) + (st.session_state.current_exercise + 1)
progress_perc = (current_step_count / total_steps) * 100
st.markdown(f"""<div class="quest-container"><div style="display: flex; justify-content: space-between; font-weight: bold; color: #3a7bd5;"><span>📍 {training_data[st.session_state.current_module]['module_title']}</span><span>🐍 %{int(progress_perc)} Tamamlandı</span><span>🏆 {RUTBELER[min(sum(st.session_state.completed_modules), 8)]}</span></div><div class="quest-bar"><div class="quest-fill" style="width: {progress_perc}%;"></div></div></div>""", unsafe_allow_html=True)

# --- 7. ANA ARAYÜZ ---
col_main, _ = st.columns([1, 0.01]) # Sidebar kullanıldığı için sağ sütun daraltıldı

selectable_indices = list(range(min(st.session_state.db_module + 1, 8)))
module_labels = [f"{'✅' if i < st.session_state.db_module else '📖'} Modül {i+1}" for i in selectable_indices]

with col_main:
    st.markdown(f"#### 👋 Hoş geldin **{st.session_state.student_name}** | ⭐ Toplam Puan: {int(st.session_state.total_score)}")
    
    sel_mod_label = st.selectbox("Seviye Seç:", module_labels, index=min(st.session_state.current_module, len(module_labels)-1))
    new_m_idx = selectable_indices[module_labels.index(sel_mod_label)]
    
    if new_m_idx != st.session_state.current_module:
        st.session_state.update({'current_module': new_m_idx, 'current_exercise': 0, 'fail_count': 0, 'exercise_passed': False, 'current_potential_score': 20, 'feedback_msg': "", 'last_output': ""}); st.rerun()

    st.divider()
    curr_ex = training_data[st.session_state.current_module]["exercises"][st.session_state.current_exercise]
    is_review_mode = (st.session_state.current_module < st.session_state.db_module)

    # 1. BÖLÜM: PİTO NOTU
    c_img, c_msg = st.columns([1, 4])
    with c_img: show_pito_img(140)
    with c_msg:
        st.info(f"##### 🗣️ Pito'nun Notu:\n{curr_ex['msg']}")
        st.caption(f"Adım: {st.session_state.current_exercise + 1}/5 | {'🔒 Arşiv Modu' if is_review_mode else f'🎁 Kazanacağın: {st.session_state.current_potential_score} Puan | ❌ Hata: {st.session_state.fail_count}/4'}")

    # 2. BÖLÜM: FEEDBACK PANELİ (ACE EDITOR ÜSTÜ)
    if st.session_state.feedback_msg:
        if "✅" in st.session_state.feedback_msg: st.success(st.session_state.feedback_msg)
        else: st.error(st.session_state.feedback_msg)

    if not st.session_state.exercise_passed and st.session_state.fail_count == 3:
        st.markdown(f'<div class="hint-guide"><div class="hint-header">💡 Pito\'dan Destek: İpucu</div>{curr_ex["hint"]}</div>', unsafe_allow_html=True)
    elif not st.session_state.exercise_passed and st.session_state.fail_count >= 4:
        st.markdown('<div class="solution-guide"><div class="solution-header">🔍 Mantığı Birlikte Kavrayalım</div></div>', unsafe_allow_html=True); st.code(curr_ex['solution'], language="python")

    # 3. BÖLÜM: KOD PANELİ
    if is_review_mode:
        st.markdown('<div class="solution-guide"><div class="solution-header">📖 Arşiv: Soru ve Çözüm</div></div>', unsafe_allow_html=True); st.code(curr_ex['solution'], language="python")
    else:
        if st.session_state.fail_count < 4 and not st.session_state.exercise_passed:
            code = st_ace(value=curr_ex['task'], language="python", theme="dracula", font_size=14, height=180, key=f"ace_{st.session_state.current_module}_{st.session_state.current_exercise}")
            if st.button("🔍 Kodumu Kontrol Et"):
                if "___" in code: st.session_state.feedback_msg = "⚠️ Pito bekliyor: Lütfen boşluğu doldur!"; st.rerun()
                else:
                    old_stdout, new_stdout = sys.stdout, StringIO(); sys.stdout = new_stdout
                    try:
                        exec(code, {"print": print, "input": lambda x: "10", "range": range, "s": 10, "L": [10, 20], "d":{'ad':'Pito'}})
                        out = new_stdout.getvalue(); sys.stdout = old_stdout
                        if curr_ex.get('check', lambda c, o, i: True)(code, out, ""):
                            st.session_state.update({'feedback_msg': "✅ Muhteşem! Görevi başarıyla tamamladın.", 'last_output': out, 'exercise_passed': True})
                            ex_key = f"{st.session_state.current_module}_{st.session_state.current_exercise}"
                            if ex_key not in st.session_state.scored_exercises: st.session_state.total_score += st.session_state.current_potential_score; st.session_state.scored_exercises.add(ex_key); force_save()
                        else: raise Exception()
                    except:
                        sys.stdout = old_stdout; st.session_state.fail_count += 1; st.session_state.current_potential_score = max(0, st.session_state.current_potential_score - 5)
                        msgs = ["🌟 Harika bir deneme! Küçük bir pürüz çıktı ama halledebilirsin.", "💪 Pes etmek yok! Hatalar en iyi öğretmenlerdir.", "🚀 Yolun sonuna yaklaştın ama vazgeçme! İpucuna bak."]
                        st.session_state.feedback_msg = msgs[min(st.session_state.fail_count-1, 2)]
                        if st.session_state.fail_count >= 4: st.session_state.exercise_passed = True
                    st.rerun()

    # 4. BÖLÜM: NAVİGASYON
    if st.session_state.exercise_passed or is_review_mode:
        if st.session_state.last_output and not is_review_mode: st.code(st.session_state.last_output)
        cp, cn = st.columns(2)
        with cp:
            if st.session_state.current_exercise > 0:
                if st.button("⬅️ Önceki Adım"): st.session_state.update({'current_exercise': st.session_state.current_exercise - 1, 'exercise_passed': False, 'fail_count': 0, 'current_potential_score': 20, 'feedback_msg': "", 'last_output': ""}); st.rerun()
        with cn:
            if st.session_state.current_exercise < 4:
                if st.button("➡️ Sonraki Adım"): st.session_state.update({'current_exercise': st.session_state.current_exercise + 1, 'exercise_passed': False, 'fail_count': 0, 'current_potential_score': 20, 'feedback_msg': "", 'last_output': ""}); st.rerun()
            elif st.session_state.current_module < 7:
                if st.button("🏆 Modülü Bitir ve Devam Et"):
                    if not is_review_mode: st.session_state.db_module += 1; st.session_state.db_exercise = 0; st.session_state.completed_modules[st.session_state.current_module] = True; force_save()
                    st.session_state.update({'current_module': st.session_state.current_module + 1, 'current_exercise': 0, 'exercise_passed': False, 'fail_count': 0, 'current_potential_score': 20, 'feedback_msg': ""}); st.rerun()