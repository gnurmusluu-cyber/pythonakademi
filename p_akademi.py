import streamlit as st
import pandas as pd
import base64

# --- 1. SAYFA AYARLARI ---
st.set_page_config(page_title="Pito Python Akademi", layout="wide")

# --- 2. GELİŞMİŞ CSS: CODESIGNAL PANEL VE OKUNABİLİRLİK İYİLEŞTİRMESİ ---
st.markdown("""
    <style>
    .stApp { background-color: #F8F9FA; }
    
    /* Pito Notu Alanı */
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

    /* CodeSignal Tarzı Komut Paneli */
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

    /* Kod Giriş Alanı ve Disabled Renk İyileştirmesi */
    .stTextArea textarea {
        background-color: #1E1E1E !important;
        color: #D4D4D4 !important; /* Normal metin rengi */
        font-family: 'Consolas', 'Monaco', 'Courier New', monospace !important;
        font-size: 17px !important;
        border-radius: 0 0 10px 10px !important;
        border: 1px solid #333 !important;
        padding: 20px !important;
        line-height: 1.5 !important;
    }

    /* Kilitlendiğinde (Doğru Cevap) Metin Rengini Koruma */
    .stTextArea textarea:disabled {
        color: #A6E22E !important; /* Doğru cevapta metin yeşilimsi tonda kalır */
        -webkit-text-fill-color: #A6E22E !important;
        opacity: 1 !important;
        background-color: #1A1A1A !important;
    }

    /* Liderlik Kartları */
    .leaderboard-card {
        background-color: #FFFFFF;
        padding: 12px;
        border-radius: 10px;
        border-left: 5px solid #FFD700;
        margin-bottom: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. VERİ VE RÜTBE SİSTEMİ ---
SHEET_URL = "https://docs.google.com/spreadsheets/d/1lat8rO2qm9QnzEUYlzC_fypG3cRkGlJfSfTtwNvs318/export?format=csv"

def get_rank(points):
    """Puan bazlı rütbe hiyerarşisi"""
    ranks = [
        (800, "🏆 Python Kahramanı"), (700, "🤖 OOP Robotu"), (600, "📦 Fonksiyon Kaptanı"),
        (500, "📋 Liste Uzmanı"), (400, "🌀 Döngü Ustası"), (300, "🧱 Mantık Mimarı"),
        (200, "🪵 Kod Oduncusu"), (100, "🌱 Python Çırağı"), (0, "🥚 Yeni Başlayan")
    ]
    for limit, label in ranks:
        if points >= limit: return label
    return "🥚 Yeni Başlayan"

def render_gif(name):
    """GIF'leri base64 ile render ederek donmayı engeller"""
    try:
        with open(f"assets/{name}.gif", "rb") as f:
            data = f.read()
            url = base64.b64encode(data).decode()
            st.markdown(f'<img src="data:image/gif;base64,{url}" width="280">', unsafe_allow_html=True)
    except:
        st.info(f"[{name}.gif yüklenemedi]")

# --- 4. EKSİKSİZ 40 ADIMLIK MÜFREDAT ---
training_data = [
    {"module_title": "1. İletişim: print() ve Çıktı Dünyası", "exercises": [
        {"msg": "Python'da ekrana mesaj yazdırmak için `print()` fonksiyonunu kullanırız. Metinleri tırnak (' ') içine almalısın.", "task": "print('___')", "solution": "print('Merhaba Pito')", "hint": "Metinleri tırnak işaretleri arasına yazmalısın."},
        {"msg": "Sayılar tırnak gerektirmez. Boşluğa sadece **100** yaz.", "task": "print(___)", "solution": "print(100)", "hint": "Sayıları yazarken tırnak kullanma!"},
        {"msg": "Virgül (`,`) farklı verileri birleştirir. 'Puan:' metni ile **100** sayısını yanyana bas.", "task": "print('Puan:', ___)", "solution": "print('Puan:', 100)", "hint": "Virgülden sonra tırnaksız 100 yaz."},
        {"msg": "`#` işareti yorum satırıdır. Başına **#** işaretini koy.", "task": "___ bu bir yoldur", "solution": "# bu bir yoldur", "hint": "Kare (diyez) işaretini en başa koy."},
        {"msg": "`\\n` karakteri metni alt satıra böler. Boşluğa **\\n** yaz.", "task": "print('Üst' + '___' + 'Alt')", "solution": "print('Üst\\nAlt')", "hint": "Tırnaklar içine \\n yazmalısın."}
    ]},
    {"module_title": "2. Hafıza: Değişkenler ve input()", "exercises": [
        {"msg": "Değişkenler hafızadaki kutulardır. `yas` değişkenine **15** değerini ata.", "task": "yas = ___", "solution": "yas = 15", "hint": "yas = 15 şeklinde yaz."},
        {"msg": "Metin atarken tırnak şarttır. `isim` değişkenine **'Pito'** değerini ata.", "task": "isim = '___'", "solution": "isim = 'Pito'", "hint": "Tırnaklar arasına Pito yaz."},
        {"msg": "`input()` kullanıcıdan bilgi bekler. Boşluğa **input** fonksiyonunu yaz.", "task": "ad = ___('Adın: ')", "solution": "ad = input('Adın: ')", "hint": "Veri alma komutu olan input yaz."},
        {"msg": "`str()` sayıları metne çevirir. Boşluğa **str** yaz.", "task": "print(___(10))", "solution": "print(str(10))", "hint": "str yazmalısın."},
        {"msg": "`int()` metni sayıya çevirir. Boşluklara **int** ve **input** yaz.", "task": "n = ___(___('S: '))", "solution": "n = int(input('S: '))", "hint": "int(input()) yapısını kur."}
    ]},
    {"module_title": "3. Karar Yapıları: If-Else Dünyası", "exercises": [
        {"msg": "Eşitlik için `==` kullanılır. Sayı 10'a eşitse kontrolü için **==** yaz.", "task": "if 10 ___ 10: print('OK')", "solution": "if 10 == 10:", "hint": "Çift eşittir kullan."},
        {"msg": "Şart yanlışsa `else:` çalışır. Boşluğa **else** yaz.", "task": "if 5 > 10: pass\n___: print('Hata')", "solution": "else:", "hint": "Sadece else: yaz."},
        {"msg": "`elif` birden fazla şartı denetler. Boşluğa **elif** yaz.", "task": "p = 60\nif p < 50: pass\n___ p > 50: print('Pass')", "solution": "elif p > 50:", "hint": "elif kullanmalısın."},
        {"msg": "`and` iki tarafın da doğru olmasını bekler. Boşluğa **and** yaz.", "task": "if 1 == 1 ___ 2 == 2: print('OK')", "solution": "and", "hint": "ve anlamına gelen and yaz."},
        {"msg": "`!=` eşit değilse demektir. Boşluğa **!=** yaz.", "task": "s = 5\nif s ___ 0: print('Var')", "solution": "if s != 0:", "hint": "!= operatörünü koy."}
    ]},
    {"module_title": "4. Otomasyon: For ve While Döngüleri", "exercises": [
        {"msg": "`for` döngüsü tekrar yapar. Boşluğa **range** yaz.", "task": "for i in ___(5): print(i)", "solution": "for i in range(5):", "hint": "range yaz."},
        {"msg": "`while` şart doğru oldukça döner. Boşluğa **while** yaz.", "task": "i = 0\n___ i == 0: print('Dönüyor'); i += 1", "solution": "while i == 0:", "hint": "while ile başlat."},
        {"msg": "`break` döngüyü bitirir. Boşluğa **break** yaz.", "task": "for i in range(5):\n if i == 1: ___\n print(i)", "solution": "break", "hint": "break yaz."},
        {"msg": "`continue` o adımı atlar. Boşluğa **continue** yaz.", "task": "for i in range(3):\n if i == 1: ___\n print(i)", "solution": "continue", "hint": "continue yaz."},
        {"msg": "Listede gezinmek için `in` kullanılır. Boşluğa **in** yaz.", "task": "for x ___ ['A', 'B']: print(x)", "solution": "for x in", "hint": "in kullan."}
    ]},
    {"module_title": "5. Gruplama: Listeler", "exercises": [
        {"msg": "Listeler `[]` içine yazılır. Boşluğa **10** yaz.", "task": "L = [___, 20]", "solution": "L = [10, 20]", "hint": "Sadece 10 yaz."},
        {"msg": "Saymaya 0'dan başlarız! İlk elemana erişmek için **0** yaz.", "task": "L = [50, 60]\nprint(L[___])", "solution": "L[0]", "hint": "İlk indeks 0'dır."},
        {"msg": "`.append()` sonuna eleman ekler. Boşluğa **append** yaz.", "task": "L = [10]\nL.___ (30)\nprint(L)", "solution": "L.append(30)", "hint": "append yaz."},
        {"msg": "`len()` boyut ölçer. Boşluğa **len** yaz.", "task": "L = [1, 2, 3]\nprint(___(L))", "solution": "len(L)", "hint": "len kullan."},
        {"msg": "`.pop()` son elemanı atar. Boşluğa **pop** yaz.", "task": "L = [1, 2]\nL.___()", "solution": "L.pop()", "hint": "pop yaz."}
    ]},
    {"module_title": "6. Modülerlik: Fonksiyonlar ve Sözlükler", "exercises": [
        {"msg": "`def` fonksiyon tanımlar. Boşluğa **def** yaz.", "task": "___ pito(): print('Hi')", "solution": "def pito():", "hint": "def yaz."},
        {"msg": "Sözlükler `{anahtar: değer}` tutar. Boşluğa **'Pito'** yaz.", "task": "d = {'ad': '___'}", "solution": "d = {'ad': 'Pito'}", "hint": "Pito yaz."},
        {"msg": "Tuple `()` ile kurulur. Boşluğa sadece **1** yaz.", "task": "t = (___, 2)", "solution": "t = (1, 2)", "hint": "Boşluğa 1 yaz."},
        {"msg": "`.keys()` tüm anahtarları listeler. Boşluğa **keys** yaz.", "task": "d = {'a':1}\nprint(d.___())", "solution": "d.keys()", "hint": "keys yaz."},
        {"msg": "`return` sonucu dışarı fırlatır. Boşluğa **return** yaz.", "task": "def f(): ___ 5", "solution": "return 5", "hint": "return kullan."}
    ]},
    {"module_title": "7. OOP: Nesne Tabanlı Dünya", "exercises": [
        {"msg": "`class` bir kalıptır. Boşluğa **class** yaz.", "task": "___ Robot: pass", "solution": "class Robot:", "hint": "class yaz."},
        {"msg": "Nesne üretmek için Robot() yazılır. Boşluğa **Robot()** yaz.", "task": "class Robot: pass\nr = ___", "solution": "r = Robot()", "hint": "Robot() yazmalısın."},
        {"msg": "Özellikler nokta ile atanır. Boşluğa **renk** yaz.", "task": "class R: pass\nr = R()\nr.___ = 'Mavi'", "solution": "r.renk = 'Mavi'", "hint": "renk yaz."},
        {"msg": "`self` nesnenin kendisidir. Boşluğa **self** yaz.", "task": "class R:\n def ses(___): print('Bip')", "solution": "def ses(self):", "hint": "self yaz."},
        {"msg": "Metodu çalıştırmak için boşluğa **s()** yaz.", "task": "class R:\n def s(self): print('X')\nr = R()\nr.___()", "solution": "r.s()", "hint": "s() yazmalısın."}
    ]},
    {"module_title": "8. Kalıcılık: Dosya Yönetimi", "exercises": [
        {"msg": "`open()` ile dosya açılır. Boşluklara **open** ve **'w'** yaz.", "task": "f = ___('n.txt', '___')", "solution": "open('n.txt', 'w')", "hint": "open ve w kullan."},
        {"msg": "`.write()` veriyi yazar. Boşluğa **write** yaz.", "task": "f = open('t.txt', 'w')\nf.___('X')\nf.close()", "solution": "f.write('X')", "hint": "write yaz."},
        {"msg": "Okuma için **'r'** kullanılır. Boşluğa **r** yaz.", "task": "f = open('t.txt', '___')", "solution": "f = open('t.txt', 'r')", "hint": "r yaz."},
        {"msg": "`.read()` içeriği çeker. Boşluğa **read** yaz.", "task": "f = open('t.txt', 'r')\nprint(f.___())", "solution": "f.read()", "hint": "read yaz."},
        {"msg": "`.close()` dosyayı kapatır. Boşluğa **close** yaz.", "task": "f = open('t.txt', 'r')\nf.___()", "solution": "f.close()", "hint": "close yaz."}
    ]}
]

# --- 5. DURUM YÖNETİMİ (SESSION STATE) ---
if 'user' not in st.session_state:
    st.session_state.user = None
    st.session_state.errors = 0
    st.session_state.score_pool = 20
    st.session_state.is_completed = False
    st.session_state.feedback_msg = ""
    st.session_state.feedback_type = ""

def show_side_leaderboard():
    try:
        df = pd.read_csv(SHEET_URL)
        st.sidebar.markdown("### 🏆 Okul Liderliği")
        for _, row in df.sort_values(by="Puan", ascending=False).head(10).iterrows():
            st.sidebar.markdown(f'<div class="leaderboard-card"><b>{row["Öğrencinin Adı"]}</b><br>{row["Rütbe"]} | {row["Puan"]} P</div>', unsafe_allow_html=True)
    except:
        st.sidebar.info("Liderlik tablosu yükleniyor...")

# --- 6. GİRİŞ VE ANA PANEL ---
if st.session_state.user is None:
    cl, cr = st.columns([2, 1])
    with cl:
        render_gif("pito_merhaba")
        st.title("Pito Python Akademi")
        okul_no = st.text_input("Okul Numaranı Gir:", placeholder="Örn: 12")
        if okul_no:
            # Başlangıç verisi
            st.session_state.user = {"Okul No": okul_no, "Ad": "Öğrenci", "Mevcut Modül": 1, "Mevcut Egzersiz": 1, "Puan": 0}
            st.rerun()
    with cr: show_side_leaderboard()

else:
    u = st.session_state.user
    m_idx, e_idx = int(u["Mevcut Modül"]) - 1, int(u["Mevcut Egzersiz"]) - 1
    
    if m_idx >= len(training_data):
        render_gif("pito_mezun"); st.balloons(); st.title("🎓 Python Kahramanı Oldun!"); st.stop()

    curr_ex = training_data[m_idx]["exercises"][e_idx]
    st.progress(((m_idx * 5) + e_idx) / 40)

    mc, sc = st.columns([2.5, 1])

    with mc:
        # Pito GIF Durum Yönetimi
        if st.session_state.is_completed:
            render_gif("pito_dusunuyor" if st.session_state.errors >= 4 else "pito_basari")
        elif st.session_state.errors > 0: render_gif("pito_hata")
        else: render_gif("pito_dusunuyor")

        st.markdown(f'<div class="pito-note"><b>🐍 Pito\'nun Notu:</b><br>{curr_ex["msg"]}</div>', unsafe_allow_html=True)
        
        # Geri bildirimlerin (feedback) metin olarak görüntülenmesi
        if st.session_state.feedback_msg:
            if st.session_state.feedback_type == "error": st.error(st.session_state.feedback_msg)
            elif st.session_state.feedback_type == "warning": st.warning(st.session_state.feedback_msg)

        # CODESIGNAL PANELİ
        st.markdown('<div class="editor-container"><div class="editor-header"><div class="editor-tab">solution.py</div></div></div>', unsafe_allow_html=True)
        ans = st.text_area("Kod Girişi:", value=curr_ex['task'], height=130, key=f"e_{m_idx}_{e_idx}", disabled=st.session_state.is_completed, label_visibility="collapsed")

        if not st.session_state.is_completed:
            if st.button("Kontrol Et"):
                if not ans or "___" in ans:
                    st.warning("⚠️ Lütfen boşluğu doldur!")
                else:
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
                st.success("✨ Harika! Doğru cevap.")
                # f-string hatasını önlemek için değişkeni dışarıda işle
                output_val = curr_ex['solution'].replace('print(', '').replace(')', '').replace("'", "").replace('"', "")
                st.code(f"Kod Çıktısı:\n{output_val}")

            if st.button("Sonraki Adıma Geç ➡️"):
                if e_idx < 4: u["Mevcut Egzersiz"] += 1
                else: u["Mevcut Modül"] += 1; u["Mevcut Egzersiz"] = 1
                st.session_state.is_completed = False; st.session_state.errors = 0; st.session_state.score_pool = 20; st.session_state.feedback_msg = ""; st.rerun()

    with sc:
        st.subheader(f"👤 {u['Ad']}")
        st.metric("Puan", u["Puan"]); st.write(f"**Rütbe:** {get_rank(u['Puan'])}")
        st.divider(); show_side_leaderboard()
