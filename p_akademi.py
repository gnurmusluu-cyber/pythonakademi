import streamlit as st
from streamlit_ace import st_ace
import sys
from io import StringIO
import pandas as pd
from datetime import datetime
from streamlit_gsheets import GSheetsConnection
import os
import base64

# --- 1. SAYFA VE CIHAZ AYARLARI ---
st.set_page_config(
    layout="wide", 
    page_title="Pito Python Akademi", 
    initial_sidebar_state="collapsed"
)

# --- 2. BEYAZ ZEMINE VE AÇILIR MENÜLERE UYGUN KESIN TASARIM (CSS) ---
st.markdown("""
    <style>
    /* 1. Uygulama Arka Planını Beyaz Yap */
    [data-testid="stAppViewContainer"], [data-testid="stHeader"], [data-testid="stToolbar"] {
        background-color: #FFFFFF !important;
    }
    header {visibility: hidden;}

    /* 2. Global Metin Rengi ve Görünürlük (Koyu Lacivert) */
    html, body, [class*="st-"] {
        color: #1E293B !important;
        font-family: 'Inter', sans-serif;
    }
    h1, h2, h3, h4, h5, h6, p, span, label, .stMarkdown {
        color: #1E293B !important;
    }

    /* 3. AÇILIR MENÜ (SELECTBOX) LİSTESİ İÇİN KESİN ÇÖZÜM */
    /* Menü kapalıyken görünüm */
    div[data-baseweb="select"] > div {
        background-color: #F8FAFC !important;
        color: #1E293B !important;
        border: 2px solid #E2E8F0 !important;
    }
    /* Menü AÇILDIĞINDA (Popover) arka planı beyaz yap */
    div[data-baseweb="popover"], div[data-baseweb="popover"] > div {
        background-color: #FFFFFF !important;
    }
    /* Menü içindeki seçeneklerin (li) görünümü */
    div[data-baseweb="popover"] li {
        color: #1E293B !important;
        background-color: #FFFFFF !important;
    }
    /* Seçeneklerin üzerine gelindiğinde (hover) rengi */
    div[data-baseweb="popover"] li:hover {
        background-color: #F1F5F9 !important;
    }

    /* 4. Giriş Kutuları */
    div[data-baseweb="base-input"] {
        background-color: #F8FAFC !important;
        border: 2px solid #E2E8F0 !important;
        border-radius: 8px !important;
    }
    input { color: #1E293B !important; }

    /* 5. Sekmelerin (Tabs) Görünürlüğü */
    button[data-baseweb="tab"] { color: #64748B !important; }
    button[data-baseweb="tab"][aria-selected="true"] {
        color: #3a7bd5 !important;
        border-bottom-color: #3a7bd5 !important;
    }

    /* 6. Pito Konuşma Balonu */
    .pito-bubble {
        position: relative; background: #F1F5F9; border: 2px solid #3a7bd5;
        border-radius: 20px; padding: 20px; margin: 0 auto 30px auto; 
        color: #1E293B !important; font-weight: 500; font-size: 1.1rem; 
        text-align: center; box-shadow: 0 10px 25px rgba(58, 123, 213, 0.08);
        max-width: 850px;
    }
    .pito-bubble:after {
        content: ''; position: absolute; bottom: -20px; left: 50%; transform: translateX(-50%);
        border-width: 20px 20px 0; border-style: solid; border-color: #3a7bd5 transparent;
    }

    /* 7. Liderlik Tablosu Kartları */
    .leaderboard-card { 
        background: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 12px; 
        padding: 12px; margin-bottom: 8px; color: #1E293B !important;
        box-shadow: 0 2px 4px rgba(0,0,0,0.02);
    }
    .leaderboard-card b { color: #3a7bd5 !important; }
    
    .champion-card { 
        background: linear-gradient(135deg, #FFD700, #F59E0B); 
        border-radius: 15px; padding: 15px; margin-top: 20px; 
        color: #FFFFFF !important; text-align: center; font-weight: bold;
    }

    /* 8. Buton Tasarımı */
    .stButton > button { 
        width: 100%; border-radius: 12px; height: 3.5em; 
        background: linear-gradient(45deg, #3a7bd5, #00d2ff) !important; 
        color: white !important; font-weight: 600; border: none;
    }
    
    /* 9. Mobil Uyumluluk */
    @media (max-width: 768px) {
        .main .block-container { padding: 1rem !important; }
        .pito-bubble { font-size: 1rem !important; }
        [data-testid="column"] { width: 100% !important; flex: 1 1 100% !important; }
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. TÜM HAFIZA DEĞİŞKENLERİNİ BAŞLAT ---
initial_states = {
    'is_logged_in': False, 'student_name': "", 'student_no': "", 'student_class': "",
    'completed_modules': [False]*8, 'current_module': 0, 'current_exercise': 0,
    'exercise_passed': False, 'total_score': 0, 'scored_exercises': set(),
    'db_module': 0, 'db_exercise': 0, 'current_potential_score': 20,
    'celebrated': False, 'rejected_user': False, 'pito_emotion': "pito_merhaba",
    'feedback_type': None, 'feedback_msg': ""
}
for key, value in initial_states.items():
    if key not in st.session_state:
        st.session_state[key] = value

# --- 4. GIF OYNATICI (BASE64) ---
def get_pito_gif(gif_name, width=280):
    gif_path = f"assets/{gif_name}.gif"
    if os.path.exists(gif_path):
        with open(gif_path, "rb") as f:
            data = f.read()
            encoded = base64.b64encode(data).decode()
        return f'<div style="text-align: center;"><img src="data:image/gif;base64,{encoded}" width="{width}" style="max-width: 100%;"></div>'
    return f'<div style="text-align: center;"><img src="https://img.icons8.com/fluency/200/robot-viewer.png" width="{width}"></div>'

# --- 5. VERİ TABANI ---
SHEET_URL = "https://docs.google.com/spreadsheets/d/1lat8rO2qm9QnzEUYlzC_fypG3cRkGlJfSfTtwNvs318/edit#gid=0"
conn = st.connection("gsheets", type=GSheetsConnection)

def get_db(use_cache=True):
    try:
        df = conn.read(spreadsheet=SHEET_URL, ttl=0 if not use_cache else 60)
        if df is None or df.empty: return pd.DataFrame(columns=["Okul No", "Öğrencinin Adı", "Sınıf", "Puan", "Rütbe", "Tamamlanan Modüller", "Mevcut Modül", "Mevcut Egzersiz", "Tarih"])
        df["Okul No"] = df["Okul No"].astype(str).str.split('.').str[0].str.strip()
        df["Puan"] = pd.to_numeric(df["Puan"], errors='coerce').fillna(0).astype(int)
        df["Mevcut Modül"] = pd.to_numeric(df["Mevcut Modül"], errors='coerce').fillna(0).astype(int)
        df["Mevcut Egzersiz"] = pd.to_numeric(df["Mevcut Egzersiz"], errors='coerce').fillna(0).astype(int)
        return df.dropna(subset=["Okul No"])
    except: return pd.DataFrame()

def force_save():
    try:
        no = str(st.session_state.student_no).strip()
        df_all = get_db(use_cache=False)
        df_clean = df_all[df_all["Okul No"] != no]
        progress = ",".join(["1" if m else "0" for m in st.session_state.completed_modules])
        rank = RUTBELER[sum(st.session_state.completed_modules)]
        new_row = pd.DataFrame([[no, st.session_state.student_name, st.session_state.student_class, int(st.session_state.total_score), rank, progress, int(st.session_state.db_module), int(st.session_state.db_exercise), datetime.now().strftime("%H:%M:%S")]], columns=["Okul No", "Öğrencinin Adı", "Sınıf", "Puan", "Rütbe", "Tamamlanan Modüller", "Mevcut Modül", "Mevcut Egzersiz", "Tarih"])
        conn.update(spreadsheet=SHEET_URL, data=pd.concat([df_clean, new_row], ignore_index=True))
    except: pass

SINIFLAR = ["9-A", "9-B", "10-A", "10-B", "11-A", "11-B"]
RUTBELER = ["🥚 Yeni Başlayan", "🌱 Python Çırağı", "🪵 Kod Oduncusu", "🧱 Mantık Mimarı", "🌀 Döngü Ustası", "📋 Liste Uzmanı", "📦 Fonksiyon Kaptanı", "🤖 OOP Robotu", "🏆 Python Kahramanı"]

# --- 6. GİRİŞ EKRANI ---
if not st.session_state.is_logged_in:
    _, col_mid, _ = st.columns([1, 2, 1])
    with col_mid:
        st.markdown('<div class="pito-bubble">Merhaba! Ben <b>Pito</b>.<br>Python Akademisi\'ne hoş geldin maceracı!</div>', unsafe_allow_html=True)
        st.markdown(get_pito_gif("pito_merhaba", width=300), unsafe_allow_html=True)
        if st.session_state.rejected_user: st.warning("⚠️ Lütfen kendi okul numaranı girerek devam et!")
        in_no_raw = st.text_input("Okul Numaran:", key="login_field").strip()
        if in_no_raw and in_no_raw.isdigit():
            if st.session_state.rejected_user: st.session_state.rejected_user = False
            df = get_db(use_cache=False)
            user_data = df[df["Okul No"] == in_no_raw] if not df.empty else pd.DataFrame()
            if not user_data.empty:
                row = user_data.iloc[0]
                st.info(f"🔍 Kayıtlarda bu numara **{row['Öğrencinin Adı']}** ismine ait görünüyor.")
                st.markdown("<h4 style='text-align: center;'>Bu sen misin? 🤔</h4>", unsafe_allow_html=True)
                c1, c2 = st.columns(2)
                with c1:
                    if st.button("✅ Evet, Benim"):
                        m_v, e_v = int(row['Mevcut Modül']), int(row['Mevcut Egzersiz'])
                        st.session_state.update({'student_no': in_no_raw, 'student_name': row["Öğrencinin Adı"], 'student_class': row["Sınıf"], 'total_score': int(row["Puan"]), 'db_module': m_v, 'db_exercise': e_v, 'current_module': min(m_v, 7), 'current_exercise': e_v if m_v < 8 else 0, 'completed_modules': [True if x == "1" else False for x in str(row["Tamamlanan Modüller"]).split(",")], 'is_logged_in': True, 'pito_emotion': "pito_dusunuyor" if m_v < 8 else "pito_mezun"})
                        st.rerun()
                with c2:
                    if st.button("❌ Hayır, Ben Değilim"):
                        st.session_state.rejected_user = True
                        if "login_field" in st.session_state: del st.session_state["login_field"]
                        st.rerun()
            else:
                st.info("Yeni bir maceracı! Kaydını yapalım:")
                in_name = st.text_input("Adın Soyadın:", key="new_name")
                in_class = st.selectbox("Sınıfın:", SINIFLAR, key="new_class")
                if st.button("Maceraya Başla! ✨") and in_name:
                    st.session_state.update({'student_no': in_no_raw, 'student_name': in_name, 'student_class': in_class, 'is_logged_in': True})
                    force_save(); st.rerun()
    st.stop()

# --- 7. MÜFREDAT KONU ANLATIMI VE EGZERSİZLER ---
training_data = [
    {"module_title": "1. Merhaba Dünya: Veri Çıkışı", "exercises": [
        {"msg": "Python'da ekrana yazı yazdırmak için **print()** fonksiyonu kullanılır. Metinler mutlaka **tırnak** (' ') içine alınmalıdır. \n\n**Hadi dene:** Ekrana **'Merhaba Pito'** yazdır.", "task": "print('___')", "check": lambda c, o: "Merhaba Pito" in o, "solution": "print('Merhaba Pito')"},
        {"msg": "Sayılar için tırnak gerekmez. Python sayıları matematiksel değer olarak tanır. \n\n**Hadi dene:** Ekrana sadece **100** sayısını yazdır.", "task": "print(___)", "check": lambda c, o: "100" in o, "solution": "print(100)"},
        {"msg": "Verileri yan yana yazdırmak için **virgül (,)** koyarız. \n\n**Hadi dene:** **'Puan:'** metni ile **100** sayısını yan yana yazdır.", "task": "print('Puan:', ___)", "check": lambda c, o: "100" in o, "solution": "print('Puan:', 100)"},
        {"msg": "**# (Diyez)** işaretiyle başlayan satırlar çalıştırılmaz (not). \n\n**Hadi dene:** Satırın başına **#** işaretini koy ve yanına **Not** yaz.", "task": "___ Bu bir not", "check": lambda c, o: "#" in c, "solution": "# Bu bir not"},
        {"msg": "Alt satıra geçmek için **'\\n'** kullanılır. \n\n**Hadi dene:** **'Üst'** ve **'Alt'** kelimelerini araya **\\n** koyarak yazdır.", "task": "print('Üst' + '___' + 'Alt')", "check": lambda c, o: "\n" in o, "solution": "print('Üst\\nAlt')"}
    ]},
    {"module_title": "2. Değişkenler: Bilgi Kutuları", "exercises": [
        {"msg": "Değişkenler verileri hafızada saklar. Atama operatörü **(=)** kullanılır. \n\n**Hadi dene:** **yas** adında bir değişken oluştur, içine **15** ata ve yazdır.", "task": "yas = ___\nprint(yas)", "check": lambda c, o: "15" in o, "solution": "yas = 15\nprint(yas)"},
        {"msg": "**isim** adında bir değişken oluştur, içine **'Pito'** ata ve yazdır.", "task": "isim = '___'\nprint(isim)", "check": lambda c, o: "Pito" in o, "solution": "isim = 'Pito'"},
        {"msg": "**input()** ile kullanıcıdan bilgi alırız. \n\n**Hadi dene:** **'Adın: '** sorusuyla bir girdi al, bunu **ad** değişkenine ata.", "task": "ad = ___('Adın: ')\nprint(ad)", "check": lambda c, o: "input" in c, "solution": "ad = input('Adın: ')"},
        {"msg": "Sayıları metne çevirmek için **str()** kullanılır. \n\n**Hadi dene:** **s = 10** sayısını metne çevirip yazdır.", "task": "s = 10\nprint(___(s))", "check": lambda c, o: "str" in c, "solution": "str(s)"},
        {"msg": "Girdileri sayıya çevirmek için **int()** kullanılır. \n\n**Hadi dene:** Gelen inputu **int**'e çevir ve üzerine 1 ekleyip yazdır.", "task": "n = ___(___('S: '))\nprint(n + 1)", "check": lambda c, o: "int" in c and "input" in c, "solution": "n = int(input('10'))"}
    ]},
    {"module_title": "3. Karar Yapıları: If-Else", "exercises": [{"msg": "Eşitlik için **çift eşittir (==)** kullanılır. \n\n**Hadi dene:** Eğer 10 sayısı **10'a eşitse** 'X' yazdır.", "task": "if 10 ___ 10: print('X')", "check": lambda c, o: "==" in c, "solution": "if 10 == 10: print('X')"}, {"msg": "Şart yanlışsa **else:** bloğu çalışır. \n\n**Hadi dene:** 5, 10'dan büyük değilse **'Y'** yazdıracak bir **else** kur.", "task": "if 5>10: pass\n___: print('Y')", "check": lambda c, o: "else" in c, "solution": "else"}, {"msg": "Büyük veya eşiti kontrol için **>=** kullanılır. \n\n**Hadi dene:** Eğer 5 sayısı **5'ten büyük veya eşitse** 'Z' yazdır.", "task": "if 5 ___ 5: print('Z')", "check": lambda c, o: ">=" in c, "solution": ">="}, {"msg": "**and** ile iki şartın da doğru olması istenir. \n\n**Hadi dene:** Eğer 1 eşit 1 **ve** 2 eşit 2 ise 'OK' yazdır.", "task": "if 1==1 ___ 2==2: print('OK')", "check": lambda c, o: "and" in c, "solution": "and"}, {"msg": "Birden fazla ihtimal için **elif** kullanılır. \n\n**Hadi dene:** İlk şart yanlış ama **5==5** doğruysa 'A' yazdır.", "task": "if 5>10: pass\n___ 5==5: print('A')", "check": lambda c, o: "elif" in c, "solution": "elif"}]},
    {"module_title": "4. Döngüler: Tekrarın Gücü", "exercises": [{"msg": "**for** ve **range(3)** ile 3 kez tekrar yap. \n\n**Hadi dene:** 3 kez 'X' yazdır.", "task": "for i in ___(3): print('X')", "check": lambda c, o: o.count("X")==3, "solution": "range"}, {"msg": "**while** şart doğruyken döner. \n\n**Hadi dene:** **i < 1** doğruyken 'Y' yazdıran döngü kur.", "task": "i=0\n___ i<1: print('Y'); i+=1", "check": lambda c, o: "while" in c, "solution": "while"}, {"msg": "**break** döngüyü bitirir. \n\n**Hadi dene:** i değeri 1 olduğunda döngüyü **bitir**.", "task": "for i in range(3):\n if i==1: ___\n print(i)", "check": lambda c, o: "break" in c, "solution": "break"}, {"msg": "**continue** adımı atlar. \n\n**Hadi dene:** i değeri 1 olduğunda o adımı **atla**.", "task": "for i in range(3):\n if i==1: ___\n print(i)", "check": lambda c, o: "continue" in c, "solution": "continue"}, {"msg": "**i** sayacı her turda değişir. \n\n**Hadi dene:** Döngü sayacı olan **i** değişkenini yazdır.", "task": "for i in range(2): print(___)", "check": lambda c, o: "1" in o, "solution": "i"}]},
    {"module_title": "5. Listeler: Veri Grupları", "exercises": [{"msg": "Listeler **[ ]** içine yazılır. \n\n**Hadi dene:** **10** ve **20** sayılarının olduğu bir liste oluştur.", "task": "L = [___, 20]", "check": lambda c, o: "10" in c, "solution": "L=[10, 20]"}, {"msg": "Sıralama **0**'dan başlar. \n\n**Hadi dene:** L listesinin **0. indeksindeki** elemanı yazdır.", "task": "L=[5,6]\nprint(L[___])", "check": lambda c, o: "5" in o, "solution": "0"}, {"msg": "**len()** eleman sayısını verir. \n\n**Hadi dene:** L listesinin boyutunu ekrana yazdır.", "task": "L=[1,2]\nprint(___(L))", "check": lambda c, o: "2" in o, "solution": "len"}, {"msg": "**append()** sona yeni eleman ekler. \n\n**Hadi dene:** Listeye **30** sayısını ekle.", "task": "L=[10]\nL.___(___)\nprint(L)", "check": lambda c, o: "30" in o, "solution": "append"}, {"msg": "**pop()** son elemanı siler. \n\n**Hadi dene:** Listeden son elemanı **çıkart**.", "task": "L=[1,2]\nL.___()\nprint(L)", "check": lambda c, o: "1" in o, "solution": "L=[1,2]\nL.pop()"}]},
    {"module_title": "6. Fonksiyonlar ve Türler", "exercises": [{"msg": "**def** ile f adında bir fonksiyon tanımla.", "task": "___ f(): print('X')", "check": lambda c, o: "def" in c, "solution": "def"}, {"msg": "**Tuple** (Demet) **( )** ile oluşturulur. Bir tane kur.", "task": "t = (___, 2)\nprint(t)", "check": lambda c, o: "1" in c, "solution": "1"}, {"msg": "**Sözlük** (Dict) anahtar:değer tutar. \n\n**Hadi dene:** **'ad'** anahtarına **'Pito'** ata.", "task": "d = {'ad': '___'}\nprint(d['ad'])", "check": lambda c, o: "Pito" in c, "solution": "Pito"}, {"msg": "**keys()** tüm etiketleri getirir. \n\n**Hadi dene:** Sözlükteki anahtarları yazdır.", "task": "d={'a':1}\nprint(d.___())", "check": lambda c, o: "keys" in c, "solution": "keys"}, {"msg": "**Set** (Küme) benzersiz veri tutar. \n\n**Hadi dene:** Tekrar eden sayıları teke düşüren bir küme oluştur.", "task": "s = {1, 2, ___}\nprint(s)", "check": lambda c, o: "1" in c, "solution": "s = {1, 2, 1}\nprint(s)"}]},
    {"module_title": "7. OOP: Nesne Tabanlı", "exercises": [{"msg": "**class** ile **Robot** sınıfı oluştur.", "task": "___ Robot: pass", "check": lambda c, o: "class" in c, "solution": "class"}, {"msg": "R sınıfından p nesnesi üret.", "task": "class R: pass\np = ___()", "check": lambda c, o: "R()" in c, "solution": "R"}, {"msg": "**renk** özelliği olarak **'Mavi'** ata.", "task": "class R: pass\np=R()\np.___ = 'Mavi'\nprint(p.renk)", "check": lambda c, o: "renk" in c, "solution": "renk"}, {"msg": "Metotlar için **self** kullanılır. **ses** metodu ekle.", "task": "class R:\n def ___(self):\n  print('Bip!')", "check": lambda c, o: "ses" in c, "solution": "ses"}, {"msg": "**r** nesnesinden **s** metodunu çağır.", "task": "class R:\n def s(self): print('X')\nr=R()\nr.___()", "check": lambda c, o: "s()" in c, "solution": "s"}]},
    {"module_title": "8. Dosya Yönetimi", "exercises": [{"msg": "**'w'** kipiyle dosya aç.", "task": "dosya = ___('n.txt', '___')", "check": lambda c, o: "open" in c, "solution": "w"}, {"msg": "**write()** ile 'Pito' yaz ve kapat.", "task": "f = open('t.txt', 'w'); f.___('Pito'); f.close()", "check": lambda c, o: "write" in c, "solution": "write"}, {"msg": "**'r'** kipiyle dosyayı okuma modunda aç.", "task": "f = open('t.txt', '___')", "check": lambda c, o: "'r'" in c, "solution": "r"}, {"msg": "**read()** ile içeriği yazdır.", "task": "f = open('t.txt', 'r')\nprint(f.___())\nf.close()", "check": lambda c, o: "read" in c, "solution": "read"}, {"msg": "**close()** ile dosyayı güvenle kapat.", "task": "f = open('t.txt', 'r')\nf.___()", "check": lambda c, o: "close" in c, "solution": "close"}]}
]

# --- 8. KOD CALISTIRICI ---
def run_pito_code(c, user_input="10"):
    old_stdout, new_stdout = sys.stdout, StringIO()
    sys.stdout = new_stdout
    if "input(" in c and not user_input: return "⚠️ Terminale veri girmelisin!"
    try:
        safe_code = c.replace("___", "None")
        exec(safe_code, {"input": lambda p: str(user_input), "print": print, "int": int, "str": str, "len": len, "open": open, "range": range})
        sys.stdout = old_stdout
        return new_stdout.getvalue()
    except Exception as e: 
        sys.stdout = old_stdout
        return f"Hata: {e}"

# --- 9. ANA ARAYÜZ (RESPONSIVE) ---
col_main, col_side = st.columns([3, 1])
student_rank = RUTBELER[sum(st.session_state.completed_modules)]

with col_main:
    st.markdown(f"#### 👋 {student_rank} {st.session_state.student_name} | ⭐ Puan: {int(st.session_state.total_score)}")
    
    if st.session_state.db_module >= 8:
        if not st.session_state.celebrated:
            st.balloons(); st.session_state.celebrated = True
            st.session_state.pito_emotion = "pito_mezun"
        st.success("### 🎉 Tebrikler! Python Kahramanı Oldun.")
        if st.button("🔄 Eğitimi Sıfırla"):
            st.session_state.update({'db_module': 0, 'db_exercise': 0, 'total_score': 0, 'current_module': 0, 'current_exercise': 0, 'completed_modules': [False]*8, 'scored_exercises': set(), 'celebrated': False, 'pito_emotion': "pito_dusunuyor", 'feedback_type': None})
            force_save(); st.rerun()

    # MODUL SECIMI (GORUNURLUK FIXLENMIS)
    st.markdown("**Ders Programı Seçimi:**")
    mod_titles = [f"{'✅' if st.session_state.completed_modules[i] else '📖'} Modül {i+1}" for i in range(8)]
    sel_mod = st.selectbox("mod_sel", mod_titles, index=st.session_state.current_module, label_visibility="collapsed")
    m_idx = mod_titles.index(sel_mod)
    if m_idx != st.session_state.current_module:
        st.session_state.update({'current_module': m_idx, 'current_exercise': 0, 'feedback_type': None})
        st.rerun()

    st.divider()
    e_idx = st.session_state.current_exercise
    curr_ex = training_data[m_idx]["exercises"][e_idx]
    is_locked = (m_idx < st.session_state.db_module)

    # Pito ve Mesaj
    c_p1, c_p2 = st.columns([1, 4])
    with c_p1: st.markdown(get_pito_gif(st.session_state.pito_emotion, width=180), unsafe_allow_html=True)
    with c_p2:
        st.info(f"##### 🗣️ Pito'nun Rehberliği:\n{curr_ex['msg']}")
        st.caption(f"Adım: {e_idx + 1}/5 | " + ("🔒 İnceleme Modu" if is_locked else f"🎁 Puan: {st.session_state.current_potential_score}"))

    # Editor
    code = st_ace(value=curr_ex['task'], language="python", theme="dracula", font_size=15, height=200, readonly=is_locked, key=f"ace_{m_idx}_{e_idx}", auto_update=True)

    # Geri Bildirim Alani (Dinamik ve Okunabilir)
    if st.session_state.feedback_type == "error":
        st.error(f"**❌ Hatalı Yanıt!** {st.session_state.feedback_msg}")
    elif st.session_state.feedback_type == "success":
        st.success(f"**✅ Tebrikler!** {st.session_state.feedback_msg}")

    if is_locked:
        st.success("**✅ Pito'nun Çözüm Örneği:**")
        st.code(curr_ex['solution'], language="python")
        sol_out = run_pito_code(curr_ex['solution'], "10") 
        st.markdown("**📟 Beklenen Çıktı:**")
        st.code(sol_out if sol_out else "Kod çalıştı.")
    else:
        u_in = st.text_input("👇 Terminal Girdisi:", key=f"t_{m_idx}_{e_idx}") if "input(" in code else ""
        if st.button("🔍 Kodumu Kontrol Et"):
            out = run_pito_code(code, u_in)
            if "⚠️" in out or "Hata" in out:
                st.session_state.update({'pito_emotion': "pito_hata", 'feedback_type': "error", 'feedback_msg': f"Bir hata çıktı: {out}"})
            elif curr_ex['check'](code, out) and "___" not in code:
                st.session_state.update({'exercise_passed': True, 'pito_emotion': "pito_basari", 'feedback_type': "success", 'feedback_msg': "Zorlu bir adımı geçtin! Sıradakine hazırsın."})
                if f"{m_idx}_{e_idx}" not in st.session_state.scored_exercises:
                    st.session_state.total_score += st.session_state.current_potential_score
                    st.session_state.scored_exercises.add(f"{m_idx}_{e_idx}")
                    if st.session_state.db_exercise < 4: st.session_state.db_exercise += 1
                    else:
                        st.session_state.db_module += 1; st.session_state.db_exercise = 0; st.session_state.completed_modules[m_idx] = True
                    force_save()
            else:
                st.session_state.update({'pito_emotion': "pito_hata", 'feedback_type': "error", 'feedback_msg': "Yanıtın eksik veya hatalı. Lütfen açıklamayı tekrar oku!"})
            st.rerun()

    if st.session_state.exercise_passed or is_locked:
        c_b1, c_b2 = st.columns(2)
        with c_b1:
            if e_idx > 0:
                if st.button("⬅️ Önceki Adım"): st.session_state.update({'current_exercise': e_idx - 1, 'feedback_type': None}); st.rerun()
        with c_b2:
            if e_idx < 4:
                if st.button("➡️ Sonraki Adım"): st.session_state.update({'current_exercise': e_idx + 1, 'exercise_passed': False, 'pito_emotion': "pito_dusunuyor", 'feedback_type': None}); st.rerun()
            elif m_idx < 7:
                if st.button("🏆 Modülü Bitir"): st.session_state.update({'current_module': m_idx + 1, 'current_exercise': 0, 'pito_emotion': "pito_dusunuyor", 'feedback_type': None}); st.rerun()

with col_side:
    st.markdown("### 🏆 Liderler Tablosu")
    df = get_db()
    t1, t2 = st.tabs(["👥 Sınıf", "🏫 Okul"])
    with t1:
        if not df.empty:
            df_c = df[df["Sınıf"] == st.session_state.student_class].sort_values("Puan", ascending=False).head(8)
            for _, r in df_c.iterrows(): st.markdown(f'<div class="leaderboard-card"><b>{r["Öğrencinin Adı"]}</b><br>{int(r["Puan"])} Puan</div>', unsafe_allow_html=True)
    with t2:
        if not df.empty:
            df_s = df.sort_values("Puan", ascending=False).head(8)
            for _, r in df_s.iterrows(): st.markdown(f'<div class="leaderboard-card"><b>{r["Öğrencinin Adı"]}</b><br>{int(r["Puan"])} Puan</div>', unsafe_allow_html=True)
    if not df.empty:
        sums = df.groupby("Sınıf")["Puan"].sum()
        if not sums.empty: st.markdown(f'<div class="champion-card">🏆 Şampiyon Sınıf<br>{sums.idxmax()}</div>', unsafe_allow_html=True)