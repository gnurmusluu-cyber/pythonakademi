import streamlit as st
import pandas as pd
import base64

# --- 1. SAYFA AYARLARI ---
st.set_page_config(page_title="Pito Python Akademi", layout="wide")

# --- 2. GELİŞMİŞ CSS: GÖRSEL KARARLILIK VE OKUNABİLİRLİK ---
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
        font-size: 1.1rem;
    }
    .editor-container {
        background-color: #1E1E1E;
        border-radius: 10px 10px 0 0;
        border: 1px solid #333;
        margin-top: 15px;
    }
    .editor-header {
        background-color: #2D2D2D;
        color: #D4D4D4;
        padding: 10px 20px;
        border-radius: 10px 10px 0 0;
        font-family: 'Consolas', monospace;
        font-size: 13px;
        border-bottom: 1px solid #3F3F3F;
    }
    .editor-tab {
        background-color: #1E1E1E;
        padding: 8px 25px;
        display: inline-block;
        color: #FFF;
        border-right: 1px solid #333;
        font-weight: bold;
    }
    /* Kod Giriş Alanı */
    .stTextArea textarea {
        background-color: #1E1E1E !important;
        color: #D4D4D4 !important;
        font-family: 'Consolas', monospace !important;
        font-size: 17px !important;
        border-radius: 0 0 10px 10px !important;
        border: 1px solid #333 !important;
        padding: 20px !important;
    }
    /* Doğru Cevap Sonrası Okunabilirlik */
    .stTextArea textarea:disabled {
        color: #A6E22E !important;
        -webkit-text-fill-color: #A6E22E !important;
        opacity: 1 !important;
        background-color: #1A1A1A !important;
    }
    .leaderboard-card {
        background-color: #FFFFFF;
        padding: 12px;
        border-radius: 10px;
        border-left: 5px solid #FFD700;
        margin-bottom: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. YARDIMCI FONKSİYONLAR ---
SHEET_URL = "https://docs.google.com/spreadsheets/d/1lat8rO2qm9QnzEUYlzC_fypG3cRkGlJfSfTtwNvs318/export?format=csv"

def get_rank(points):
    """Puan bazlı rütbe hiyerarşisi"""
    ranks = [(800, "🏆 Python Kahramanı"), (700, "🤖 OOP Robotu"), (600, "📦 Fonksiyon Kaptanı"), (500, "📋 Liste Uzmanı"), (400, "🌀 Döngü Ustası"), (300, "🧱 Mantık Mimarı"), (200, "🪵 Kod Oduncusu"), (100, "🌱 Python Çırağı"), (0, "🥚 Yeni Başlayan")]
    for limit, label in ranks:
        if points >= limit: return label
    return "🥚 Yeni Başlayan"

def render_gif(name):
    """GIF'leri base64 ile render eder"""
    try:
        with open(f"assets/{name}.gif", "rb") as f:
            data = f.read()
            url = base64.b64encode(data).decode()
            st.markdown(f'<img src="data:image/gif;base64,{url}" width="280">', unsafe_allow_html=True)
    except:
        st.info(f"[{name}.gif yüklenemedi]")

# --- 4. EKSİKSİZ 40 ADIMLIK MÜFREDAT ---
# Not: Egzersizlerin tamamı 'print()' varlığına göre çıktı verecek şekilde kurgulanmıştır.
training_data = [
    {"module_title": "1. İletişim: print() ve Çıktı Dünyası", "exercises": [
        {"msg": "Python'da ekrana mesaj yazdırmak için `print()` fonksiyonunu kullanırız. Bilgisayara bir metin yazdırmak için o metni mutlaka tırnak (' ') içine almalısın.\n\n**Görev:** Ekrana tam olarak **'Merhaba Pito'** yazdır.", "task": "print('___')", "solution": "print('Merhaba Pito')", "hint": "Metni tırnak içine al."},
        {"msg": "Sayılar (Integer) metinlerden farklıdır; tırnak gerektirmezler.\n\n**Görev:** Boşluğa tırnak kullanmadan sadece **100** sayısını yaz.", "task": "print(___)", "solution": "print(100)", "hint": "Tırnak kullanma!"},
        {"msg": "Virgül (`,`) farklı veri tiplerini aynı satırda birleştirir.\n\n**Görev:** 'Puan:' metni ile **100** sayısını yanyana bas.", "task": "print('Puan:', ___)", "solution": "print('Puan:', 100)", "hint": "Sayıyı tırnaksız yaz."},
        {"msg": "`#` işareti Python'da yorum satırıdır. Bilgisayar bu satırı okumaz.\n\n**Görev:** Satırın en başına **#** işaretini koy.", "task": "___ bu bir yoldur", "solution": "# bu bir yoldur", "hint": "Kare (diyez) işaretini koy."},
        {"msg": "`\\n` kaçış karakteri metni alt satıra böler.\n\n**Görev:** Boşluğa **\\n** yaz.", "task": "print('Üst' + '___' + 'Alt')", "solution": "print('Üst\\nAlt')", "hint": "Alt satıra geçme komutunu yaz."}
    ]},
    {"module_title": "2. Hafıza: Değişkenler ve input()", "exercises": [
        {"msg": "Değişkenler hafızadaki kutulardır. `=` işareti atama yapar.\n\n**Görev:** `yas` değişkenine **15** değerini ata.", "task": "yas = ___", "solution": "yas = 15", "hint": "Sadece 15 yaz."},
        {"msg": "Metin atarken tırnak şarttır.\n\n**Görev:** `isim` değişkenine **'Pito'** değerini ata.", "task": "isim = '___'", "solution": "isim = 'Pito'", "hint": "Tırnak içine Pito yaz."},
        {"msg": "`input()` kullanıcıdan bilgi bekler.\n\n**Görev:** Boşluğa **input** fonksiyonunu yaz.", "task": "ad = ___('Adın: ')", "solution": "ad = input('Adın: ')", "hint": "input yaz."},
        {"msg": "`str()` sayıları metne çevirir.\n\n**Görev:** 10 sayısını metne çeviren **str** fonksiyonunu yaz.", "task": "print(___(10))", "solution": "print(str(10))", "hint": "str yazmalısın."},
        {"msg": "`int()` metni sayıya çevirir. Matematik için şarttır.\n\n**Görev:** Dış boşluğa **int**, içe **input** yaz.", "task": "n = ___(___('S: '))", "solution": "n = int(input('S: '))", "hint": "int(input()) yapısını kur."}
    ]},
    {"module_title": "3. Karar Yapıları: If-Else Dünyası", "exercises": [
        {"msg": "Eşitlik kontrolü için `==` kullanılır.\n\n**Görev:** Sayı 10'a eşitse kontrolü için **==** yaz.", "task": "if 10 ___ 10: print('OK')", "solution": "if 10 == 10: print('OK')", "hint": "Çift eşittir koy."},
        {"msg": "Şart yanlışsa `else:` bloğu çalışır.\n\n**Görev:** Boşluğa **else** yaz.", "task": "if 5 > 10: pass\n___: print('Hata')", "solution": "else: print('Hata')", "hint": "else: yaz."},
        {"msg": "`elif` birden fazla şartı denetler.\n\n**Görev:** Boşluğa **elif** yaz.", "task": "p = 60\nif p < 50: pass\n___ p > 50: print('Geçti')", "solution": "elif p > 50: print('Geçti')", "hint": "elif kullan."},
        {"msg": "`and` (ve) iki tarafın da doğru olmasını bekler.\n\n**Görev:** Boşluğa **and** yaz.", "task": "if 1 == 1 ___ 2 == 2: print('OK')", "solution": "if 1 == 1 and 2 == 2: print('OK')", "hint": "and yaz."},
        {"msg": "`!=` eşit değilse demektir.\n\n**Görev:** s değişkeni 0'a eşit değilse kontrolü için **!=** yaz.", "task": "s = 5\nif s ___ 0: print('Var')", "solution": "if s != 0: print('Var')", "hint": "!= operatörünü koy."}
    ]},
    {"module_title": "4. Otomasyon: For ve While Döngüleri", "exercises": [
        {"msg": "`for` döngüsü tekrar yapar. `range(5)` sayıları üretir.\n\n**Görev:** Boşluğa **range** yaz.", "task": "for i in ___(5): print(i)", "solution": "for i in range(5): print(i)", "hint": "range yaz."},
        {"msg": "`while` şart doğru oldukça döner.\n\n**Görev:** Boşluğa **while** yaz.", "task": "i = 0\n___ i == 0: print('Dönüyor'); i += 1", "solution": "while i == 0: print('Dönüyor')", "hint": "while ile başlat."},
        {"msg": "`break` döngüyü bitirir.\n\n**Görev:** Boşluğa **break** yaz.", "task": "for i in range(5):\n if i == 1: ___\n print(i)", "solution": "break", "hint": "break yaz."},
        {"msg": "`continue` o adımı atlar.\n\n**Görev:** Boşluğa **continue** yaz.", "task": "for i in range(3):\n if i == 1: ___\n print(i)", "solution": "continue", "hint": "continue yaz."},
        {"msg": "Listede gezinmek için `in` kullanılır.\n\n**Görev:** Boşluğa **in** yaz.", "task": "for x ___ ['A', 'B']: print(x)", "solution": "for x in ['A', 'B']: print(x)", "hint": "in kullan."}
    ]},
    {"module_title": "5. Gruplama: Listeler", "exercises": [
        {"msg": "Listeler `[]` içine yazılır.\n\n**Görev:** Boşluğa **10** yazarak listeyi kur.", "task": "L = [___, 20]", "solution": "L = [10, 20]", "hint": "10 yaz."},
        {"msg": "Saymaya 0'dan başlarız! İlk elemana erişmek için **0** yaz.\n\n**Görev:** Boşluğa **0** yaz.", "task": "L = [50, 60]\nprint(L[___])", "solution": "print(L[0])", "hint": "0 yaz."},
        {"msg": "`.append()` sonuna eleman ekler.\n\n**Görev:** Boşluğa **append** yaz.", "task": "L = [10]\nL.___ (30)\nprint(L)", "solution": "L.append(30)", "hint": "append yaz."},
        {"msg": "`len()` boyut ölçer.\n\n**Görev:** Boşluğa **len** yaz.", "task": "L = [1, 2, 3]\nprint(___(L))", "solution": "print(len(L))", "hint": "len yaz."},
        {"msg": "`.pop()` son elemanı atar.\n\n**Görev:** Boşluğa **pop** yaz.", "task": "L = [1, 2]\nL.___()", "solution": "L.pop()", "hint": "pop yaz."}
    ]},
    {"module_title": "6. Modülerlik: Fonksiyonlar ve Sözlükler", "exercises": [
        {"msg": "`def` fonksiyon tanımlar.\n\n**Görev:** Boşluğa **def** yaz.", "task": "___ pito(): print('Hi')", "solution": "def pito(): print('Hi')", "hint": "def yaz."},
        {"msg": "Sözlükler `{anahtar: değer}` tutar.\n\n**Görev:** Boşluğa **'Pito'** yaz.", "task": "d = {'ad': '___'}", "solution": "d = {'ad': 'Pito'}", "hint": "Pito yaz."},
        {"msg": "Tuple `()` ile kurulur ve değiştirilemez.\n\n**Görev:** Boşluğa sadece **1** yaz.", "task": "t = (___, 2)", "solution": "t = (1, 2)", "hint": "1 yaz."},
        {"msg": "`.keys()` tüm anahtarları listeler.\n\n**Görev:** Boşluğa **keys** yaz.", "task": "d = {'a':1}\nprint(d.___())", "solution": "print(d.keys())", "hint": "keys yaz."},
        {"msg": "`return` sonucu dışarı fırlatır.\n\n**Görev:** Boşluğa **return** yaz.", "task": "def f(): ___ 5", "solution": "return 5", "hint": "return yaz."}
    ]},
    {"module_title": "7. OOP: Nesne Tabanlı Dünya", "exercises": [
        {"msg": "`class` bir kalıptır.\n\n**Görev:** Boşluğa **class** yaz.", "task": "___ Robot: pass", "solution": "class Robot: pass", "hint": "class yaz."},
        {"msg": "Nesne üretmek için Robot() yazılır.\n\n**Görev:** Boşluğa **Robot()** yaz.", "task": "class Robot: pass\nr = ___", "solution": "r = Robot()", "hint": "Robot() yaz."},
        {"msg": "Özellikler nokta ile atanır.\n\n**Görev:** Boşluğa **renk** yaz.", "task": "class R: pass\nr = R()\nr.___ = 'Mavi'", "solution": "r.renk = 'Mavi'", "hint": "renk yaz."},
        {"msg": "`self` nesnenin kendisidir.\n\n**Görev:** Parantez içine **self** yaz.", "task": "class R:\n def ses(___): print('Bip')", "solution": "def ses(self):", "hint": "self yaz."},
        {"msg": "Metodu çalıştırmak için nesne isminden sonra nokta koyarız.\n\n**Görev:** Boşluğa **s()** yaz.", "task": "class R:\n def s(self): print('X')\nr = R()\nr.___()", "solution": "r.s()", "hint": "s() yaz."}
    ]},
    {"module_title": "8. Kalıcılık: Dosya Yönetimi", "exercises": [
        {"msg": "Açmak için `open()` kullanılır.\n\n**Görev:** Boşluklara **open** ve **'w'** yaz.", "task": "f = ___('n.txt', '___')", "solution": "open('n.txt', 'w')", "hint": "open ve w kullan."},
        {"msg": "`.write()` veriyi yazar.\n\n**Görev:** Boşluğa **write** yaz.", "task": "f = open('t.txt', 'w')\nf.___('X')\nf.close()", "solution": "f.write('X')", "hint": "write yaz."},
        {"msg": "Okuma için **'r'** kullanılır.\n\n**Görev:** Boşluğa **r** yaz.", "task": "f = open('t.txt', '___')", "solution": "f = open('t.txt', 'r')", "hint": "r yaz."},
        {"msg": "`.read()` içeriği çeker.\n\n**Görev:** Boşluğa **read** yaz.", "task": "f = open('t.txt', 'r')\nprint(f.___())", "solution": "print(f.read())", "hint": "read yaz."},
        {"msg": "`.close()` dosyayı kapatır.\n\n**Görev:** Boşluğa **close** yaz.", "task": "f = open('t.txt', 'r')\nf.___()", "solution": "f.close()", "hint": "close yaz."}
    ]}
]

# --- 5. DURUM YÖNETİMİ ---
if 'user' not in st.session_state:
    st.session_state.user, st.session_state.errors, st.session_state.score_pool = None, 0, 20
    st.session_state.is_completed, st.session_state.feedback_msg, st.session_state.feedback_type = False, "", ""

# --- 6. GİRİŞ VE ANA PANEL ---
if st.session_state.user is None:
    cl, cr = st.columns([2, 1])
    with cl:
        render_gif("pito_merhaba")
        st.title("Pito Python Akademi")
        okul_no = st.text_input("Okul Numaranı Gir:")
        if okul_no:
            st.session_state.user = {"Okul No": okul_no, "Ad": "Öğrenci", "Mevcut Modül": 1, "Mevcut Egzersiz": 1, "Puan": 0}
            st.rerun()
else:
    u = st.session_state.user
    m_idx, e_idx = int(u["Mevcut Modül"]) - 1, int(u["Mevcut Egzersiz"]) - 1
    if m_idx >= len(training_data):
        render_gif("pito_mezun"); st.balloons(); st.title("🎓 Mezun Oldun!"); st.stop()
    
    curr_ex = training_data[m_idx]["exercises"][e_idx]
    st.progress(((m_idx * 5) + e_idx) / 40)

    mc, sc = st.columns([2.5, 1])
    with mc:
        # Pito GIF
        if st.session_state.is_completed:
            render_gif("pito_dusunuyor" if st.session_state.errors >= 4 else "pito_basari")
        elif st.session_state.errors > 0: render_gif("pito_hata")
        else: render_gif("pito_dusunuyor")

        st.markdown(f'<div class="pito-note"><b>🐍 Pito\'nun Notu:</b><br>{curr_ex["msg"]}</div>', unsafe_allow_html=True)
        
        if st.session_state.feedback_msg:
            if st.session_state.feedback_type == "error": st.error(st.session_state.feedback_msg)
            elif st.session_state.feedback_type == "warning": st.warning(st.session_state.feedback_msg)

        # CODESIGNAL PANELİ
        st.markdown('<div class="editor-container"><div class="editor-header"><div class="editor-tab">solution.py</div></div></div>', unsafe_allow_html=True)
        ans = st.text_area("Kod Girişi:", value=curr_ex['task'], height=130, key=f"e_{m_idx}_{e_idx}", disabled=st.session_state.is_completed, label_visibility="collapsed")

        if not st.session_state.is_completed:
            if st.button("Kontrol Et"):
                # Karşılaştırma Mantığı
                ans_clean = ans.strip().replace(" ","").replace("'","").replace('"',"")
                sol_clean = curr_ex["solution"].replace(" ","").replace("'","").replace('"',"")
                
                if ans_clean == sol_clean:
                    st.session_state.is_completed = True
                    st.session_state.feedback_msg = ""
                    u["Puan"] += st.session_state.score_pool
                    st.rerun()
                else:
                    st.session_state.errors += 1
                    st.session_state.score_pool -= 5
                    if st.session_state.errors < 3:
                        st.session_state.feedback_msg = f"❌ Yanlış! {st.session_state.errors}. hatan. -5 Puan."
                        st.session_state.feedback_type = "error"
                    elif st.session_state.errors == 3:
                        st.session_state.feedback_msg = f"💡 İpucu: {curr_ex['hint']}"
                        st.session_state.feedback_type = "warning"
                    elif st.session_state.errors >= 4:
                        st.session_state.is_completed = True
                        st.session_state.feedback_msg = "🚨 4 hata! Puan kazanamadın. Çözümü incele."
                        st.session_state.feedback_type = "error"
                    st.rerun()

        if st.session_state.is_completed:
            st.divider()
            if st.session_state.errors >= 4:
                st.info(f"✅ Doğru Çözüm: `{curr_ex['solution']}`")
            else:
                st.success("✨ Tebrikler! Doğru cevap.")
                
                # --- ÇIKTI KONTROLÜ (Yalnızca print içerenler) ---
                if "print(" in curr_ex["solution"]:
                    # SyntaxError Giderme: replace işlemini f-string dışında yap
                    clean_out = curr_ex['solution'].split('print(')[1].rsplit(')', 1)[0].replace("'", "").replace('"', "")
                    st.code(f"Kod Çıktısı:\n{clean_out}")

            if st.button("Sonraki Adıma Geç ➡️"):
                if e_idx < 4: u["Mevcut Egzersiz"] += 1
                else: u["Mevcut Modül"] += 1; u["Mevcut Egzersiz"] = 1
                st.session_state.is_completed, st.session_state.errors, st.session_state.score_pool, st.session_state.feedback_msg = False, 0, 20, ""
                st.rerun()

    with sc:
        st.subheader(f"👤 {u['Ad']}")
        st.metric("Puan", u["Puan"]); st.write(f"**Rütbe:** {get_rank(u['Puan'])}")
