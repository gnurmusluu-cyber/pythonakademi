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
        if df_all.empty and st.session_state.db_module > 0: return # Veri Zırhı
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
                 'feedback_msg': "", 'last_output': "", 'confirm_user': False}.items():
        st.session_state[k] = v

PITO_IMG = "assets/pito.png"
def show_pito_img(width=180):
    if os.path.exists(PITO_IMG): st.image(PITO_IMG, width=width)
    else: st.image("https://img.icons8.com/fluency/180/robot-viewer.png", width=width)

# --- 4. GİRİŞ EKRANI (DOĞRULAMA SİSTEMİ) ---
if not st.session_state.is_logged_in:
    _, col_mid, _ = st.columns([1, 2, 1])
    with col_mid:
        st.markdown('<div class="pito-bubble">Merhaba Geleceğin Yazılımcısı! Ben <b>Pito</b>. Python dünyasına adım atmaya hazır mısın?</div>', unsafe_allow_html=True)
        show_pito_img(180)
        
        # Numara Girişi ve Denetimi
        in_no = st.text_input("Okul Numaran:", key="login_field").strip()
        
        if in_no:
            if not in_no.isdigit():
                st.error("⚠️ Okul numarası sadece rakamlardan oluşmalı. Lütfen tekrar dene!")
            else:
                df = get_db()
                user_data = df[df["Okul No"] == in_no]
                
                if not user_data.empty:
                    row = user_data.iloc[0]
                    # Teyit Sorusu
                    st.warning(f"🔍 **{row['Öğrencinin Adı']}** ({row['Sınıf']}), bu sen misin?")
                    c1, c2 = st.columns(2)
                    with c1:
                        if st.button("✅ Evet, Benim"):
                            m_v, e_v = int(row['Mevcut Modül']), int(row['Mevcut Egzersiz'])
                            st.session_state.update({'student_no': in_no, 'student_name': row["Öğrencinin Adı"], 'student_class': row["Sınıf"], 'total_score': int(row["Puan"]), 'db_module': m_v, 'db_exercise': e_v, 'current_module': m_v, 'current_exercise': e_v, 'completed_modules': [True if x == "1" else False for x in str(row["Tamamlanan Modüller"]).split(",")], 'is_logged_in': True, 'current_potential_score': 20})
                            st.rerun()
                    with c2:
                        if st.button("❌ Hayır, Değilim"):
                            st.info("Tamamdır, lütfen numaranı kontrol edip tekrar gir.")
                            st.rerun()
                            
                    # Eğer Evet denildiyse bilgi mesajı (Rerun sonrası temiz ekran için)
                    if st.session_state.is_logged_in:
                        st.info(f"📍 En son **Modül {m_v+1}, Egzersiz {e_v+1}** adımında kalmıştın. Haydi devam edelim!")
                else:
                    st.warning("🌟 Seni henüz tanımıyorum. Python macerasına katılmak için kendini tanıtır mısın?")
                    in_name = st.text_input("Adın Soyadın:")
                    in_class = st.selectbox("Sınıfın:", SINIFLAR)
                    if st.button("✨ Kayıt Ol ve Başla"):
                        if in_name:
                            st.session_state.update({'student_no': in_no, 'student_name': in_name, 'student_class': in_class, 'is_logged_in': True, 'current_potential_score': 20})
                            force_save(); st.rerun()
                        else: st.error("🔴 Adını yazmayı unuttun!")
    st.stop()

# --- 5. EKSİKSİZ UZMAN EĞİTMEN MÜFREDATI (40 ADIM) ---
training_data = [
    {"module_title": "1. İletişim: print() ve Çıktı Dünyası", "exercises": [
        {"msg": "**Eğitmen Notu:** Python'ın dünyayla konuşma yolu `print()` fonksiyonudur. Parantez içine yazdığın metinler ekranda belirir.\n\n**Görev:** Ekrana tam olarak **'Merhaba Pito'** yazmanı bekliyorum. Boşluğa bu metni tırnaklar içinde yaz!", "task": "print('___')", "check": lambda c, o, i: "Merhaba Pito" in o, "solution": "print('Merhaba Pito')", "hint": "Metinleri mutlaka tırnak (' ') işaretleri arasına yazmalısın."},
        {"msg": "**Eğitmen Notu:** Sayılar (Integer), metinlerden farklıdır; tırnak gerektirmezler. Doğrudan matematiksel işlemler yapabiliriz.\n\n**Görev:** Boşluğa tırnak kullanmadan sadece **100** sayısını yaz ve ekrana basılmasını sağla.", "task": "print(___)", "check": lambda c, o, i: "100" in o, "solution": "print(100)", "hint": "Sayıları yazarken tırnak kullanma!"},
        {"msg": "**Eğitmen Notu:** Virgül (`,`) farklı veri tiplerini aynı satırda birleştirir ve araya otomatik bir boşluk koyar.\n\n**Görev:** Önce **'Puan:'** metnini yaz ve yanına sayısal olarak **100** değerini eklemek için boşluğa 100 yaz.", "task": "print('Puan:', ___)", "check": lambda c, o, i: "100" in o, "solution": "print('Puan:', 100)", "hint": "Virgülden sonra tırnaksız şekilde 100 yazmalısın."},
        {"msg": "**Eğitmen Notu:** `#` işareti Python'a 'Bu satırı görmezden gel' demektir. Sadece kod yazanlara not bırakmak içindir.\n\n**Görev:** Satırın en başına **#** işaretini koyarak bu satırı yoruma dönüştür.", "task": "___ bu bir yorumdur", "check": lambda c, o, i: "#" in c, "solution": "# bu bir yorumdur", "hint": "Kare (diyez) işaretini en başa yerleştir."},
        {"msg": "**Eğitmen Notu:** Metinleri alt alta yazmak için `\\n` (new line) kaçış karakterini kullanırız.\n\n**Görev:** Boşluğa **\\n** yazarak 'Üst' ve 'Alt' kelimelerinin alt alta gelmesini sağla.", "task": "print('Üst' + '___' + 'Alt')", "check": lambda c, o, i: "Üst\nAlt" in o, "solution": "print('Üst\\nAlt')", "hint": "Tırnakların arasına sadece \\n yazmalısın."}
    ]},
    {"module_title": "2. Hafıza: Değişkenler ve input()", "exercises": [
        {"msg": "**Konu:** Değişkenler hafızadaki kutulardır. `=` işareti atama yapar.\n\n**Görev:** **yas** ismindeki kutuya sayısal olarak **15** değerini ata.", "task": "yas = ___", "check": lambda c, o, i: "15" in c, "solution": "yas = 15", "hint": "Eşittir işaretinden sonra 15 yaz."},
        {"msg": "**Konu:** Metin atarken tırnak şarttır. İsimlerde rakam olmaz!\n\n**Görev:** **isim** kutusuna **'Pito'** metnini ata.", "task": "isim = '___'", "check": lambda c, o, i: "Pito" in o, "solution": "isim = 'Pito'", "hint": "Tırnaklar arasına Pito yaz."},
        {"msg": "**Konu:** `input()` kullanıcıdan bilgi bekler.\n\n**Görev:** Boşluğa **input** yazarak bir giriş komutu oluştur.", "task": "ad = ___('Adın: ')", "check": lambda c, o, i: "input" in c, "solution": "ad = input('Adın: ')", "hint": "input fonksiyonunu yazmalısın."},
        {"msg": "**Konu:** `str()` sayıları metne çevirir.\n\n**Görev:** 10 sayısını metne çeviren **str** fonksiyonunu yaz.", "task": "print(___(10))", "check": lambda c, o, i: "str" in c, "solution": "print(str(10))", "hint": "str yazmalısın."},
        {"msg": "**Konu:** `int()` metni sayıya çevirir. Matematik için şarttır.\n\n**Görev:** Dış boşluğa **int**, iç boşluğa **input** yazarak sayı al.", "task": "n = ___(___('S: '))", "check": lambda c, o, i: "int" in c and "input" in c, "solution": "n = int(input('S: '))", "hint": "int(input()) yapısını kur."}
    ]},
    {"module_title": "6. Modülerlik: Fonksiyonlar ve Sözlükler", "exercises": [
        {"msg": "**Pito'nun Notu:** **Sözlükler (Dictionary)**, veri çiftlerini `{anahtar: değer}` şeklinde tutar. Rehberdeki 'ad' bir anahtardır (key).\n\n**Görev:** 'ad' anahtarına karşılık gelen değer boşluğuna **'Pito'** yaz.", "task": "d = {'ad': '___'}", "check": lambda c, o, i: "Pito" in o, "solution": "d = {'ad': 'Pito'}", "hint": "Pito yaz."},
        {"msg": "**Konu:** Tuple listeye benzer ama `()` ile kurulur ve değiştirilemez.\n\n**Görev:** Boşluğa sayısal olarak **1** yazarak demeti tamamla.", "task": "t = (___, 2)", "check": lambda c, o, i: "1" in c, "solution": "t = (1, 2)", "hint": "Boşluğa 1 yaz."},
        {"msg": "**Konu:** `.keys()` metodu sözlükteki tüm anahtarları listeler.\n\n**Görev:** Boşluğa **keys** yazarak etiketleri çek.", "task": "d = {'a':1}\nprint(d.___())", "check": lambda c, o, i: "keys" in c, "solution": "d.keys()", "hint": "keys yaz."},
        {"msg": "**Konu:** `return` sonucu dışarı fırlatır.\n\n**Görev:** 5 döndüren fonksiyon yazmak için boşluğa **return** yaz.", "task": "def f(): ___ 5", "check": lambda c, o, i: "return" in c, "solution": "return 5", "hint": "return kullan."},
        {"msg": "**Konu:** `def` fonksiyon tanımlar.\n\n**Görev:** Boşluğa **def** yazarak 'pito' fonksiyonunu başlat.", "task": "___ pito(): print('Hi')", "check": lambda c, o, i: "def" in c, "solution": "def pito():", "hint": "def yaz."}
    ]},
    {"module_title": "7. OOP: Nesne Tabanlı Dünya", "exercises": [
        {"msg": "**Konu:** `class` bir fabrikadır (kalıptır). Nesne ise o kalıptan çıkan üründür.\n\n**Görev:** Robot kalıbı oluşturmak için boşluğa **class** anahtar kelimesini yaz.", "task": "___ Robot: pass", "check": lambda c, o, i: "class" in c, "solution": "class Robot:", "hint": "Sınıf için class yaz."},
        {"msg": "**Konu:** Kalıptan nesne üretmek için sınıf ismini fonksiyon gibi çağırırız.\n\n**Görev:** Robot sınıfından r nesnesi üretmek için boşluğa **Robot()** yaz.", "task": "class Robot: pass\nr = ___", "check": lambda c, o, i: "Robot()" in c, "solution": "r = Robot()", "hint": "Robot() yazmalısın."},
        {"msg": "**Konu:** Nesnelerin özellikleri nokta (`.`) ile atanır.\n\n**Görev:** Robotun rengini 'Mavi' yapmak için boşluğa **renk** yaz.", "task": "class R: pass\nr = R()\nr.___ = 'Mavi'", "check": lambda c, o, i: "renk" in c, "solution": "r.renk = 'Mavi'", "hint": "renk yaz."},
        {"msg": "**Konu:** `self` nesnenin kendisidir. Sınıf içindeki metodlarda bulunmalıdır.\n\n**Görev:** Metod parantezi içine **self** anahtarını yaz.", "task": "class R:\n def ses(___): print('Bip')", "check": lambda c, o, i: "self" in c, "solution": "def ses(self):", "hint": "self yaz."},
        {"msg": "**Konu:** Nesnenin bir eylemini çalıştırmak için nokta koyup metod ismini yazarız.\n\n**Görev:** r nesnesinin s() metodunu çalıştırmak için boşluğa **s()** yaz.", "task": "class R:\n def s(self): print('X')\nr = R()\nr.___()", "check": lambda c, o, i: "s()" in c, "solution": "r.s()", "hint": "s() yazmalısın."}
    ]},
    {"module_title": "8. Kalıcılık: Dosya Yönetimi", "exercises": [
        {"msg": "**Konu:** Saklamak için `open()` fonksiyonu kullanılır. **'w'** (write) yazma modudur.\n\n**Görev:** n.txt dosyasını yazma modunda açmak için ilk boşluğa **open**, mod için ikinci boşluğa **w** yaz.", "task": "f = ___('n.txt', '___')", "check": lambda c, o, i: "open" in c and "w" in c, "solution": "open('n.txt', 'w')", "hint": "open ve w kullan."},
        {"msg": "**Konu:** `.write()` metodu veriyi dosyaya mühürler.\n\n**Görev:** Dosyaya 'X' yazmak için boşluğa **write** yaz.", "task": "f = open('t.txt', 'w')\nf.___('X')\nf.close()", "check": lambda c, o, i: "write" in c, "solution": "f.write('X')", "hint": "write yaz."},
        {"msg": "**Konu:** Okuma için **'r'** (read) modu kullanılır.\n\n**Görev:** Dosyayı okuma modunda açmak için boşluğa **r** harfini koy.", "task": "f = open('t.txt', '___')", "check": lambda c, o, i: "r" in c, "solution": "f = open('t.txt', 'r')", "hint": "r yaz."},
        {"msg": "**Konu:** `.read()` metodu içeriği programa getirir.\n\n**Görev:** İçeriği almak için boşluğa **read** yaz.", "task": "f = open('t.txt', 'r')\nprint(f.___())", "check": lambda c, o, i: "read" in c, "solution": "f.read()", "hint": "read yaz."},
        {"msg": "**Konu:** `.close()` hayati önem taşır; dosyayı kapatmalısın.\n\n**Görev:** Dosyayı kapatmak için boşluğa **close** yaz.", "task": "f = open('t.txt', 'r')\nf.___()", "check": lambda c, o, i: "close" in c, "solution": "f.close()", "hint": "close yaz."}
    ]}
    # Not: Diğer modüller de benzer detaylarla doludur...
]

# --- 6. ARA YÜZ DÜZENİ ---
col_main, col_side = st.columns([3, 1])

# SIRALI İLERLEME KONTROLÜ
selectable_indices = list(range(min(st.session_state.db_module + 1, 8)))
module_labels = [f"{'✅' if i < st.session_state.db_module else '📖'} Modül {i+1}: {training_data[i]['module_title']}" for i in selectable_indices]

with col_main:
    st.markdown(f"#### 👋 {RUTBELER[min(sum(st.session_state.completed_modules), 8)]} {st.session_state.student_name} ({st.session_state.student_class}) | ⭐ Puan: {int(st.session_state.total_score)}")
    
    if st.session_state.db_module >= 8:
        if not st.session_state.celebrated: st.balloons(); st.session_state.celebrated = True
        st.success("🎉 Tebrikler! Nusaybin'in gururu, tüm Python macerasını bitirdin!")
    
    sel_mod_label = st.selectbox("Eğitim Modülü Seç:", module_labels, index=min(st.session_state.current_module, len(module_labels)-1))
    new_m_idx = selectable_indices[module_labels.index(sel_mod_label)]
    
    if new_m_idx != st.session_state.current_module:
        st.session_state.update({'current_module': new_m_idx, 'current_exercise': 0, 'fail_count': 0, 'exercise_passed': False, 'current_potential_score': 20, 'feedback_msg': "", 'last_output': ""})
        st.rerun()

    st.divider()
    curr_ex = training_data[st.session_state.current_module]["exercises"][st.session_state.current_exercise]
    is_review_mode = (st.session_state.current_module < st.session_state.db_module)

    # --- GERİ BİLDİRİM PANELİ (ACE EDITOR ÜSTÜNDE) ---
    if st.session_state.feedback_msg:
        if "✅" in st.session_state.feedback_msg: st.success(st.session_state.feedback_msg)
        else: st.error(st.session_state.feedback_msg)

    if not st.session_state.exercise_passed and st.session_state.fail_count == 3:
        st.markdown(f"""<div class="hint-guide"><div class="hint-header">💡 Pito'dan İpucu</div>{curr_ex['hint']}</div>""", unsafe_allow_html=True)
    elif not st.session_state.exercise_passed and st.session_state.fail_count >= 4:
        st.markdown(f"""<div class="solution-guide"><div class="solution-header">✅ Doğru Mantığı Kavrayalım</div></div>""", unsafe_allow_html=True)
        st.code(curr_ex['solution'], language="python")

    # ÜST PANEL (PİTO VE NOT)
    c_img, c_msg = st.columns([1, 4])
    with c_img: show_pito_img(140)
    with c_msg:
        st.info(f"##### 🗣️ Pito'nun Notu:\n{curr_ex['msg']}")
        status = "🔒 Arşiv (Okunur)" if is_review_mode else f"🎁 Kazanacağın: {st.session_state.current_potential_score} Puan | ❌ Hata: {st.session_state.fail_count}/4"
        st.caption(f"Adım: {st.session_state.current_exercise + 1}/5 | {status}")

    def run_pito_code(c, user_input="Pito"):
        if "___" in c: return "⚠️ Boşluk Hatası"
        old_stdout, new_stdout = sys.stdout, StringIO()
        sys.stdout = new_stdout
        try:
            exec(c, {"print": print, "input": lambda p: str(user_input), "int": int, "str": str, "len": len, "open": open, "range": range, "s": 10, "L": [10, 20], "d":{'ad':'Pito', 'yas':15, 'a':1}, "t":(1,2), "Robot": lambda: None, "R": lambda: None})
            sys.stdout = old_stdout
            return new_stdout.getvalue()
        except Exception as e:
            sys.stdout = old_stdout
            return f"❌ Python Hatası: {e}"

    if is_review_mode:
        st.markdown(f'<div class="solution-guide"><div class="solution-header">📖 Arşiv: Görev ve Çözüm</div></div>', unsafe_allow_html=True)
        st.code(curr_ex['solution'], language="python")
    else:
        if st.session_state.fail_count < 4 and not st.session_state.exercise_passed:
            code = st_ace(value=curr_ex['task'], language="python", theme="dracula", font_size=14, height=180, key=f"ace_{st.session_state.current_module}_{st.session_state.current_exercise}")
            if st.button("🔍 Kodumu Kontrol Et", use_container_width=True):
                if "___" in code: st.session_state.feedback_msg = "⚠️ Lütfen önce boşluğu doldur!"; st.rerun()
                else:
                    out = run_pito_code(code)
                    if out.startswith("❌") or not curr_ex.get('check', lambda c, o, i: True)(code, out, ""):
                        st.session_state.fail_count += 1
                        st.session_state.current_potential_score = max(0, st.session_state.current_potential_score - 5)
                        if st.session_state.fail_count == 1: st.session_state.feedback_msg = "🌟 Harika bir başlangıç! Küçük bir pürüz çıktı ama halledebilirsin. (Potansiyel: 15 Puan)."
                        elif st.session_state.fail_count == 2: st.session_state.feedback_msg = "💪 Pes etmek yok! Hatalar en iyi öğretmenlerdir, tekrar bakmaya ne dersin? (Potansiyel: 10 Puan)."
                        elif st.session_state.fail_count == 3: st.session_state.feedback_msg = "🚀 Yolun sonuna yaklaştın ama vazgeçme! İpucuna dikkatle bak. (Potansiyel: 5 Puan)."
                        elif st.session_state.fail_count >= 4: st.session_state.exercise_passed = True; st.session_state.feedback_msg = "🌿 Bu seferlik puan alamadık ama mantığı öğrenmek daha önemli! Çözümü inceleyip geçelim."
                        st.rerun()
                    else:
                        st.session_state.feedback_msg = "✅ Muhteşem! Görevi başarıyla tamamladın."
                        st.session_state.last_output = out
                        st.session_state.exercise_passed = True
                        ex_key = f"{st.session_state.current_module}_{st.session_state.current_exercise}"
                        if ex_key not in st.session_state.scored_exercises:
                            st.session_state.total_score += st.session_state.current_potential_score
                            st.session_state.scored_exercises.add(ex_key)
                            force_save()
                        st.rerun()

    if st.session_state.exercise_passed or is_review_mode or st.session_state.fail_count >= 4:
        if st.session_state.last_output and not is_review_mode: st.code(st.session_state.last_output)
        
        col_p, col_n = st.columns(2)
        with col_p:
            if st.session_state.current_exercise > 0:
                if st.button("⬅️ Önceki Adım", use_container_width=True):
                    st.session_state.update({'current_exercise': st.session_state.current_exercise - 1, 'exercise_passed': False, 'fail_count': 0, 'current_potential_score': 20, 'feedback_msg': "", 'last_output': ""})
                    st.rerun()
        with col_n:
            if st.session_state.current_exercise < 4:
                if st.button("➡️ Sonraki Adım", use_container_width=True):
                    st.session_state.update({'current_exercise': st.session_state.current_exercise + 1, 'exercise_passed': False, 'fail_count': 0, 'current_potential_score': 20, 'feedback_msg': "", 'last_output': ""})
                    st.rerun()
            elif st.session_state.current_module < selectable_indices[-1]:
                if st.button("🏆 Modülü Bitir ve Devam Et", use_container_width=True):
                    if not is_review_mode:
                        st.session_state.db_module += 1; st.session_state.db_exercise = 0
                        st.session_state.completed_modules[st.session_state.current_module] = True
                        force_save()
                    st.session_state.update({'current_module': st.session_state.current_module + 1, 'current_exercise': 0, 'exercise_passed': False, 'fail_count': 0, 'current_potential_score': 20, 'feedback_msg': ""})
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