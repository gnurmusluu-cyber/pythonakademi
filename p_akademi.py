import streamlit as st
from streamlit_ace import st_ace
import sys
from io import StringIO
import pandas as pd
from datetime import datetime
from streamlit_gsheets import GSheetsConnection
import os
import base64
from pathlib import Path

# --- 1. TASARIM VE SAYFA AYARLARI ---
st.set_page_config(layout="wide", page_title="Pito Python Akademi", initial_sidebar_state="collapsed")

# --- 2. SESSION STATE (SİSTEM ANAYASASI) ---
if 'is_logged_in' not in st.session_state:
    for k, v in {
        'student_name': "", 'student_no': "", 'student_class': "", 'completed_modules': [False]*8,
        'current_module': 0, 'current_exercise': 0, 'exercise_passed': False, 'total_score': 0,
        'scored_exercises': set(), 'db_module': 0, 'db_exercise': 0, 'is_logged_in': False,
        'current_potential_score': 20, 'fail_count': 0, 'feedback_msg': "", 'last_output': "",
        'login_error': "", 'graduation_view': False, 'no_input_error': False,
        'pito_emotion': "merhaba"
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
    .quest-bar { height: 16px; background: #e2e8f0; border-radius: 10px; margin: 10px 0; overflow: hidden; position: relative; }
    .quest-fill { height: 100%; background: linear-gradient(90deg, #3a7bd5, #00d2ff); transition: width 0.6s ease-in-out; }
    .pito-bubble {
        position: relative; background: #ffffff; border: 2.5px solid #3a7bd5;
        border-radius: 20px; padding: 25px; margin-bottom: 20px; color: #1e1e1e;
        font-weight: 500; font-size: 1.15rem; box-shadow: 6px 6px 20px rgba(0,0,0,0.06); line-height: 1.7;
    }
    .pito-bubble:after { content: ''; position: absolute; bottom: -20px; left: 50px; border-width: 20px 20px 0; border-style: solid; border-color: #3a7bd5 transparent; }
    .solution-guide { background-color: #fef2f2 !important; border: 2px solid #ef4444 !important; border-radius: 12px; padding: 20px; margin: 15px 0; color: #1e1e1e !important; }
    .hint-guide { background-color: #fffbeb !important; border: 2px solid #f59e0b !important; border-radius: 12px; padding: 20px; margin: 15px 0; color: #1e1e1e !important; }
    .leaderboard-card { background: linear-gradient(135deg, #1e1e1e, #2d2d2d); border: 1px solid #444; border-radius: 12px; padding: 10px; margin-bottom: 8px; color: white; }
    .stButton > button { width: 100%; border-radius: 12px; height: 3.8em; background: linear-gradient(45deg, #3a7bd5, #00d2ff) !important; color: white !important; font-weight: bold; border: none; font-size: 1.1rem; }
    [data-testid="stTextInput"] { border: 2.5px solid #3a7bd5 !important; border-radius: 12px; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. KESİN ÇÖZÜM: GIF YOLU VE BASE64 (MACBOOK UYUMLU) ---
def get_base64_gif(gif_name):
    # Scriptin çalıştığı klasörü bul ve assets klasörüyle birleştir
    base_path = Path(__file__).parent if "__file__" in locals() else Path.cwd()
    asset_path = base_path / "assets" / gif_name
    
    if asset_path.exists():
        with open(asset_path, "rb") as f:
            data = f.read()
            return base64.b64encode(data).decode()
    return None

def show_pito_gif(width=300):
    emotion_map = {
        "standart": "pito_dusunuyor.gif",
        "merhaba": "pito_merhaba.gif",
        "uzgun": "pito_hata.gif",
        "mutlu": "pito_basari.gif",
        "akademi": "pito_mezun.gif"
    }
    gif_file = emotion_map.get(st.session_state.pito_emotion, "pito_dusunuyor.gif")
    base64_data = get_base64_gif(gif_file)
    
    if base64_data:
        st.markdown(f'<div style="display: flex; justify-content: center; margin-bottom: 10px;"><img src="data:image/gif;base64,{base64_data}" width="{width}"></div>', unsafe_allow_html=True)
    else:
        # Yedek simge (Assets klasörü hatalıysa)
        st.image("https://img.icons8.com/fluency/250/robot-viewer.png", width=width)

# --- 4. VERİ TABANI ---
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
    except: return None

db_current = get_db()
if db_current is None: db_current = pd.DataFrame(columns=["Okul No", "Öğrencinin Adı", "Sınıf", "Puan", "Rütbe", "Tamamlanan Modüller", "Mevcut Modül", "Mevcut Egzersiz", "Tarih"])

# --- 5. LİDERLİK TABLOSU (MÜHÜRLÜ - EN ÜSTTE) ---
col_app, col_ranking = st.columns([3, 1])

with col_ranking:
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
            my_c = db_current[db_current["Sınıf"] == st.session_state.student_class].sort_values(by="Puan", ascending=False).head(10)
            for _, r in my_c.iterrows(): st.markdown(f'<div class="leaderboard-card"><b>{r["Rütbe"]} {r["Öğrencinin Adı"]}</b><br>{int(r["Puan"])} Puan</div>', unsafe_allow_html=True)
        else: st.caption("Giriş yapmalısın.")
    with tab_s:
        for _, r in db_current.sort_values(by="Puan", ascending=False).head(10).iterrows():
            st.markdown(f'<div class="leaderboard-card"><b>{r["Rütbe"]} {r["Öğrencinin Adı"]} ({r["Sınıf"]})</b><br>{int(r["Puan"])} Puan</div>', unsafe_allow_html=True)

def force_save():
    try:
        no = str(st.session_state.student_no).strip()
        df_all = get_db()
        if df_all is None: return
        df_clean = df_all[df_all["Okul No"] != no]
        prog = ",".join(["1" if m else "0" for m in st.session_state.completed_modules])
        rank = RUTBELER[min(sum(st.session_state.completed_modules), 8)]
        new_row = pd.DataFrame([[no, st.session_state.student_name, st.session_state.student_class, int(st.session_state.total_score), rank, prog, int(st.session_state.db_module), int(st.session_state.db_exercise), datetime.now().strftime("%H:%M:%S")]], columns=["Okul No", "Öğrencinin Adı", "Sınıf", "Puan", "Rütbe", "Tamamlanan Modüller", "Mevcut Modül", "Mevcut Egzersiz", "Tarih"])
        conn.update(spreadsheet=SHEET_URL, data=pd.concat([df_clean, new_row], ignore_index=True))
    except: pass

# --- 6. GİRİŞ VE MEZUNİYET SİSTEMİ ---
with col_app:
    if not st.session_state.is_logged_in:
        st.markdown('<div class="pito-bubble">Merhaba! Ben <b>Pito</b>. Python dünyasına adım atmaya hazır mısın?</div>', unsafe_allow_html=True)
        st.session_state.pito_emotion = "merhaba"
        show_pito_gif(300)
        in_no = st.text_input("Okul Numaran:", key="login_f", placeholder="Sayısal okul numaranı gir...").strip()
        if in_no:
            if not in_no.isdigit(): st.error("⚠️ Sadece rakam giriniz!")
            else:
                user_data = db_current[db_current["Okul No"] == in_no]
                if not user_data.empty:
                    row = user_data.iloc[0]
                    m_v, e_v = int(row['Mevcut Modül']), int(row['Mevcut Egzersiz'])
                    st.info(f"🔍 **{row['Öğrencinin Adı']}** ({row['Sınıf']}), Hoş geldin! En son **{m_v+1}. Modül {e_v+1}. Egzersizde** kalmıştın. Bu sen misin?")
                    c1, c2 = st.columns(2)
                    with c1:
                        if st.button("✅ Evet, Benim"):
                            st.session_state.update({'student_no': in_no, 'student_name': row["Öğrencinin Adı"], 'student_class': row["Sınıf"], 'total_score': int(row["Puan"]), 'db_module': m_v, 'db_exercise': e_v, 'current_module': min(m_v, 7), 'current_exercise': e_v, 'completed_modules': [True if x == "1" else False for x in str(row["Tamamlanan Modüller"]).split(",")], 'is_logged_in': True, 'graduation_view': (m_v >= 8), 'pito_emotion': 'standart'})
                            st.rerun()
                    with c2:
                        if st.button("❌ Hayır, Değilim"): st.rerun()
                else:
                    st.warning("🌟 Seni henüz tanımıyorum. Python macerasına katılmak için yeni kayıt oluştur!")
                    in_name = st.text_input("Adın Soyadın:")
                    in_class = st.selectbox("Sınıfın:", SINIFLAR)
                    if st.button("✨ Kayıt Ol ve Başla"):
                        if in_name:
                            st.session_state.update({'student_no': in_no, 'student_name': in_name, 'student_class': in_class, 'is_logged_in': True, 'pito_emotion': 'standart'})
                            force_save(); st.rerun()
        st.stop()

    if st.session_state.graduation_view:
        st.session_state.pito_emotion = "akademi"
        st.markdown('<div class="pito-bubble">🎊 <b>TEBRİKLER Python Kahramanı!</b> Tüm akademiyi başarıyla tamamladın.</div>', unsafe_allow_html=True)
        st.balloons(); show_pito_gif(380)
        st.success(f"Nusaybin'in gururu oldun! Toplam Puanın: {st.session_state.total_score}")
        c1, c2 = st.columns(2)
        with c1:
            if st.button("🔄 Eğitimi Tekrar Al (Puan Sıfırlanır)"):
                st.session_state.update({'db_module': 0, 'db_exercise': 0, 'current_module': 0, 'current_exercise': 0, 'total_score': 0, 'completed_modules': [False]*8, 'graduation_view': False, 'scored_exercises': set(), 'last_output': "", 'feedback_msg': "", 'pito_emotion': 'merhaba'})
                force_save(); st.rerun()
        with c2:
            if st.button("🔒 İnceleme Modu ve Liderlikte Kal"):
                st.session_state.update({'current_module': 0, 'current_exercise': 0, 'graduation_view': False, 'pito_emotion': 'standart'}); st.rerun()
        st.stop()

    # --- 7. MÜHÜRLÜ MÜFREDAT (40 ADIM) ---
    training_data = [
        {"module_title": "1. İletişim: print() ve Metin Dünyası", "exercises": [
            {"msg": "**Pito'nun Notu:** Python'ın dünyayla konuşma yolu `print()` fonksiyonudur. Ekrana yazacağın metinleri mutlaka tırnak (' ') içine almalısın. Tırnaklar Python'a 'buradaki ifadeyi olduğu gibi yansıt' komutunu verir. Unutma, bilgisayar senin ne yazmak istediğini tırnaklar olmazsa anlayamaz.", "task": "print('___')", "check": lambda c, o, i: "Merhaba Pito" in o, "solution": "print('Merhaba Pito')", "hint": "Metnin başına ve sonuna tek (') tırnak koyduğundan emin ol."},
            {"msg": "**Pito'un Notu:** Sayılar (Integer), metinlerden farklıdır; tırnak gerektirmezler. Eğer bir sayıya tırnak koyarsan Python onu sayı değil, bir 'yazı' olarak görür ve üzerinde toplama/çıkarma gibi matematiksel işlemler yapamaz.", "task": "print(___)", "check": lambda c, o, i: "100" in o, "solution": "print(100)", "hint": "Rakamları tırnaksız yazmalısın. Eğer '100' yazarsan bu bir metin (String) olur!"},
            {"msg": "**Pito'nun Notu:** Virgül (`,`) farklı veri tiplerini (örneğin bir metin ve bir sayı) aynı satırda birleştirir ve araya otomatik bir boşluk koyar. Bu, değişkenleri ve mesajları birleştirmek için en profesyonel yöntemdir.", "task": "print('Puan:', ___)", "check": lambda c, o, i: "100" in o, "solution": "print('Puan:', 100)", "hint": "Virgülden sonra sadece sayısal değeri (100) yazmalısın."},
            {"msg": "**Pito'nun Notu:** `#` işareti Python'a 'Bu satırı görmezden gel' demektir. Buna 'Yorum Satırı' diyoruz. Sadece biz yazılımcıların kod içine not alması içindir; kodun çalışmasını asla etkilemez.", "task": "___ bu bir nottur", "check": lambda c, o, i: "#" in c, "solution": "# bu bir nottur", "hint": "Klavyeden diyez (#) işaretini satırın en başına yerleştir."},
            {"msg": "**Pito'nun Notu:** `\\n` (new line) kaçış karakteri metni alt satıra böler. Sanki klavyede Enter tuşuna basılmış gibi davranır. Bu karakter metinlerin içinde gizli bir alt satıra geçiş komutudur.", "task": "print('Üst' + '___' + 'Alt')", "check": lambda c, o, i: "Üst\nAlt" in o, "solution": "print('Üst\\nAlt')", "hint": "Tırnaklar içerisine ters eğik çizgi (\\) ve n harfini birleşik yaz: \\n"}
        ]},
        {"module_title": "2. Hafıza: Değişkenler ve input()", "exercises": [
            {"msg": "**Pito'nun Notu:** Değişkenler bellekteki (RAM) kutulardır. `=` işareti bir 'atama operatörü'dür ve sağdaki değeri soldaki kutunun içine koyar. Artık o kutuya ismiyle seslendiğinde içindeki değeri sana verir.", "task": "yas = ___", "check": lambda c, o, i: "15" in str(i.get('yas', '')), "solution": "yas = 15", "hint": "Eşittir işaretinden sonra sadece değeri (15) yazmalısın."},
            {"msg": "**Pito'nun Notu:** Metin (String) verilerini hafızaya alırken tırnak şarttır. Değişken isimlerinde rakamla başlamamaya ve boşluk kullanmamaya dikkat etmelisin. Python büyük-küçük harfe duyarlıdır!", "task": "isim = '___'", "check": lambda c, o, i: "Pito" in str(i.get('isim', '')), "solution": "isim = 'Pito'", "hint": "Metni tırnaklar içerisine tam olarak Pito şeklinde yaz."},
            {"msg": "**Pito'nun Notu:** `input()` programı durdurur ve kullanıcıdan bir bilgi bekler. Python bu bilgiyi ne olursa olsun her zaman 'metin' (String) olarak algılar. Eğer sayı gerekiyorsa onu dönüştürmen gerekecek.", "task": "ad = ___('Adın: ')", "check": lambda c, o, i: "input" in c, "solution": "ad = input('Adın: ')", "hint": "Veri alma komutu olan input kelimesini kullan."},
            {"msg": "**Pito'nun Notu:** Sayıları metne çevirmemiz gerektiğinde (Buna 'Casting' diyoruz) `str()` fonksiyonunu kullanırız. Bu, sayıları ve metinleri `+` operatörüyle birleştirirken hata almanı önler.", "task": "print(___(10))", "check": lambda c, o, i: "str" in c, "solution": "print(str(10))", "hint": "String'in kısaltması olan str fonksiyonunu yerleştir."},
            {"msg": "**Pito'nun Notu:** Matematik yapabilmek için `input()` ile gelen metni `int()` fonksiyonu ile 'tam sayıya' çevirmelisin. Aksi takdirde Python onları toplamaz, yan yana dizer.", "task": "n = ___(___('S: '))", "check": lambda c, o, i: "int" in c and "input" in c, "solution": "n = int(input('S: '))", "hint": "Fonksiyonları iç içe kullanmalısın: int(input())"}
        ]},
        {"module_title": "3. Mantık: Karar Yapıları (If-Else)", "exercises": [
            {"msg": "**Karar:** Programların beyni `if` bloğudur. Karşılaştırmada `=` değil, mutlaka `==` (çift eşittir) kullanmalısın.", "task": "if 10 ___ 10: print('OK')", "check": lambda c, o, i: "==" in c, "solution": "if 10 == 10:\n    print('OK')", "hint": "Eşitlik kontrolü için == kullan."},
            {"msg": "**B Planı:** `else:` şart sağlanmadığında devreye giren 'B Planı'dır.", "task": "if 5 > 10: pass\n___: print('Hata')", "check": lambda c, o, i: "else" in c, "solution": "if 5 > 10: pass\nelse:\n    print('Hata')", "hint": "Sadece else: yaz."},
            {"msg": "**elif:** Birden fazla şartı denetlemek için kullanılır. Şartlar yukarıdan aşağıya okunur.", "task": "p = 60\nif p < 50: pass\n___ p > 50: print('Geçti')", "check": lambda c, o, i: "elif" in c, "solution": "if p < 50: pass\nelif p > 50:\n    print('Geçti')", "hint": "elif komutunu kullan."},
            {"msg": "**Bağlaç:** `and` (ve) iki tarafın da doğru olmasını bekler. İki şarttan biri bile yanlışsa blok çalışmaz.", "task": "if 1==1 ___ 2==2: print('OK')", "check": lambda c, o, i: "and" in c, "solution": "if 1==1 and 2==2:\n    print('OK')", "hint": "and yaz."},
            {"msg": "**Zıtlık:** `!=` 'eşit değilse' anlamına gelir.", "task": "s = 5\nif s ___ 0: print('Var')", "check": lambda c, o, i: "!=" in c, "solution": "if s != 0:\n    print('Var')", "hint": "!= kullan."}
        ]},
        {"module_title": "4. Otomasyon: For ve While Döngüleri", "exercises": [
            {"msg": "**range:** `range(5)` komutu 0'dan 4'e kadar 5 sayı üretir. `for` döngüsü bu sayılar üzerinde adım adım ilerler.", "task": "for i in ___(5): print(i)", "check": lambda c, o, i: "range" in c, "solution": "for i in range(5):\n    print(i)", "hint": "range yaz."},
            {"msg": "**While:** Şart 'True' olduğu sürece çalışmaya devam eder.", "task": "i = 0\n___ i == 0: print('D'); i += 1", "check": lambda c, o, i: "while" in c, "solution": "i = 0\nwhile i == 0:\n    print('D')\n    i += 1", "hint": "while yaz."},
            {"msg": "**break:** Döngüyü anında sonlandırır. Şart sağlandığı an acil çıkış kapısıdır.", "task": "for i in range(5):\n if i == 1: ___", "check": lambda c, o, i: "break" in c, "solution": "for i in range(5):\n    if i == 1: break\n    print(i)", "hint": "break kullan."},
            {"msg": "**continue:** O anki adımı 'pas geçer' ve döngünün en başına geri döner.", "task": "for i in range(3):\n if i == 1: ___", "check": lambda c, o, i: "continue" in c, "solution": "for i in range(3):\n    if i == 1: continue\n    print(i)", "hint": "continue yaz."},
            {"msg": "**in:** Listelerde gezinmek için kullanılır.", "task": "for x ___ ['A']: print(x)", "check": lambda c, o, i: "in" in c, "solution": "for x in ['A']:\n    print(x)", "hint": "in yaz."}
        ]},
        {"module_title": "5. Gruplama: Listeler (Veri Sepeti)", "exercises": [
            {"msg": "**Listeler:** Birden fazla veriyi tek kutuda tutar. Python'da saymaya 0'dan başlarız!", "task": "L = [___, 20]", "check": lambda c, o, i: "10" in str(i.get('L', '')), "solution": "L = [10, 20]", "hint": "10 yaz."},
            {"msg": "**İndeks:** Listenin ilk elemanına `[0]` indeksiyle ulaşılır. Buna 'İndisleme' denir.", "task": "L = [50, 60]\nprint(L[___])", "check": lambda c, o, i: "50" in o, "solution": "L = [50, 60]\nprint(L[0])", "hint": "0 yaz."},
            {"msg": "**.append():** Listenin sonuna yeni bir eleman ekler.", "task": "L = [10]\nL.___ (30)", "check": lambda c, o, i: "append" in c, "solution": "L = [10]\nL.append(30)", "hint": "append kullan."},
            {"msg": "**len():** Listenin içindeki toplam eleman sayısını verir.", "task": "L = [1, 2, 3]\nprint(___(L))", "check": lambda c, o, i: "3" in o, "solution": "L = [1, 2, 3]\nprint(len(L))", "hint": "len yaz."},
            {"msg": "**.pop():** Listenin en sonundaki elemanı sepetten çıkarır.", "task": "L = [1, 2]\nL.___()", "check": lambda c, o, i: "pop" in c, "solution": "L = [1, 2]\nL.pop()", "hint": "pop yazmalısın."}
        ]},
        {"module_title": "6. Modülerlik: Fonksiyonlar ve Sözlükler", "exercises": [
            {"msg": "**def:** Tekrar eden kodları paketlemek için kullanırız.", "task": "___ pito(): print('Hi')", "check": lambda c, o, i: "def" in c, "solution": "def pito():\n    print('Hi')", "hint": "def yaz."},
            {"msg": "**Sözlük:** `{anahtar: değer}` çiftleriyle çalışır. Rehber mantığıdır.", "task": "d = {'ad': '___'}", "check": lambda c, o, i: "Pito" in str(i.get('d', {})), "solution": "d = {'ad': 'Pito'}", "hint": "Pito yaz."},
            {"msg": "**Tuple:** Listeye benzer ama parantez `()` ile kurulur ve değiştirilemez.", "task": "t = (___, 2)", "check": lambda c, o, i: "1" in str(i.get('t', '')), "solution": "t = (1, 2)", "hint": "1 yaz."},
            {"msg": "**.keys():** Sözlükteki tüm etiketleri liste halinde verir.", "task": "d = {'a':1}\nprint(d.___())", "check": lambda c, o, i: "keys" in c, "solution": "d = {'a':1}\nprint(d.keys())", "hint": "keys yaz."},
            {"msg": "**return:** Fonksiyonun ürettiği sonucu dışarıya 'fırlatır'.", "task": "def f(): ___ 5", "check": lambda c, o, i: "return" in c, "solution": "def f():\n    return 5", "hint": "return kullan."}
        ]},
        {"module_title": "7. Nesneler: OOP Dünyası", "exercises": [
            {"msg": "**class:** Bir taslaktır. Ondan 'Nesneler' üretiriz. Sınıf bir fabrikadır.", "task": "___ Robot: pass", "check": lambda c, o, i: "class" in c, "solution": "class Robot:\n    pass", "hint": "class yaz."},
            {"msg": "**Robot():** Kalıptan nesne üretmek için sınıf ismini parantezlerle `()` çağırırız.", "task": "class Robot: pass\nr = ___", "check": lambda c, o, i: "Robot" in str(i.get('r', '')), "solution": "class Robot: pass\nr = Robot()", "hint": "Robot() yaz."},
            {"msg": "**Özellikler:** Nesnelerin kimlik bilgileridir, nokta (`.`) yardımıyla atanır.", "task": "class R: pass\nr = R()\nr.___ = 'Mavi'", "check": lambda c, o, i: "renk" in c, "solution": "class R: pass\nr = R()\nr.renk = 'Mavi'", "hint": "renk yaz."},
            {"msg": "**self:** Nesnenin kendisini temsil eden parametredir. Metotlarda ilk sırada olmalıdır.", "task": "class R:\n def ses(___): print('Bip')", "check": lambda c, o, i: "self" in c, "solution": "class R:\n    def ses(self):\n        print('Bip')", "hint": "self yaz."},
            {"msg": "**Method:** r nesnesinin **s()** metodunu çalıştır.", "task": "class R:\n def s(self): pass\nr = R()\nr.___()", "check": lambda c, o, i: "s()" in c, "solution": "class R:\n    def s(self):\n        pass\nr = R()\nr.s()", "hint": "s() yaz."}
        ]},
        {"module_title": "8. Kalıcılık: Dosya Yönetimi", "exercises": [
            {"msg": "**open():** Bilgileri saklamak için kullanılır. **'w'** (write) yazma modudur.", "task": "f = ___('n.txt', '___')", "check": lambda c, o, i: "open" in c and "w" in c, "solution": "f = open('n.txt', 'w')", "hint": "open ve w yaz."},
            {"msg": "**.write():** Veriyi dosyanın içine kalıcı olarak mühürler.", "task": "f = open('t.txt', 'w')\nf.___('X')", "check": lambda c, o, i: "write" in c, "solution": "f = open('t.txt', 'w')\nf.write('X')\nf.close()", "hint": "write yaz."},
            {"msg": "**'r':** Okuma modudur. Dosyayı sadece görmemizi sağlar.", "task": "f = open('t.txt', '___')", "check": lambda c, o, i: "r" in c, "solution": "f = open('t.txt', 'r')", "hint": "r koy."},
            {"msg": "**.read():** Dosyanın tüm içeriğini belleğe getirir.", "task": "f = open('t.txt', 'r')\nprint(f.___())", "check": lambda c, o, i: "read" in c, "solution": "f = open('t.txt', 'r')\nprint(f.read())", "hint": "read yaz."},
            {"msg": "**.close():** Dosyayı mutlaka kapatmalısın!", "task": "f = open('t.txt', 'r')\nf.___()", "check": lambda c, o, i: "close" in c, "solution": "f = open('t.txt', 'r')\nf.close()", "hint": "close kullan."}
        ]}
    ]

    # --- 8. QUEST BAR ---
    total_steps = 40
    curr_total = (st.session_state.current_module * 5) + (st.session_state.current_exercise + 1)
    progress_perc = (curr_total / total_steps) * 100
    st.markdown(f"""<div class="quest-container"><div style="display: flex; justify-content: space-between; font-weight: bold; color: #3a7bd5; margin-bottom: 5px;"><span>📍 {training_data[st.session_state.current_module]['module_title']}</span><span>🐍 %{int(progress_perc)} İlerleme</span><span>🏆 {RUTBELER[min(sum(st.session_state.completed_modules), 8)]}</span></div><div class="quest-bar"><div class="quest-fill" style="width: {progress_perc}%;"></div></div></div>""", unsafe_allow_html=True)

    module_labels = [f"{'✅' if i < st.session_state.db_module else '📖'} Modül {i+1}" for i in range(min(st.session_state.db_module + 1, 8))]
    sel_mod_label = st.selectbox("Seviye Seç:", module_labels, index=min(st.session_state.current_module, len(module_labels)-1))
    new_m_idx = module_labels.index(sel_mod_label)
    if new_m_idx != st.session_state.current_module:
        st.session_state.update({'current_module': new_m_idx, 'current_exercise': 0, 'fail_count': 0, 'exercise_passed': False, 'current_potential_score': 20, 'feedback_msg': "", 'last_output': "", 'pito_emotion': 'standart'}); st.rerun()

    st.divider()
    curr_ex = training_data[st.session_state.current_module]["exercises"][st.session_state.current_exercise]
    is_review_mode = (st.session_state.current_module < st.session_state.db_module)

    # GÖRSEL MİMARİ: Pito'ya daha fazla alan (1.3)
    c_box_i, c_box_m = st.columns([1.3, 3.7])
    with c_box_i: show_pito_gif(300)
    with c_box_m:
        st.info(f"##### 🗣️ Pito'nun Notu:\n{curr_ex['msg']}")
        st.caption(f"Adım: {st.session_state.current_exercise + 1}/5 | {'🔒 İnceleme Modu' if is_review_mode else f'🎁 Potansiyel: {st.session_state.current_potential_score} | ❌ Hata: {st.session_state.fail_count}/4'}")

    # --- 9. FEEDBACK VE ÇIKTI PANELİ ---
    if st.session_state.feedback_msg:
        if "✅" in st.session_state.feedback_msg:
            st.success(st.session_state.feedback_msg)
            if st.session_state.last_output:
                st.markdown("##### 🖥️ Kod Çıktısı (Konsol):")
                st.code(st.session_state.last_output, language="text")
        else: st.error(st.session_state.feedback_msg)

    if not st.session_state.exercise_passed and st.session_state.fail_count == 3:
        st.markdown(f'<div class="hint-guide">💡 <b>Pito\'dan Destek: İpucu</b><br>{curr_ex["hint"]}</div>', unsafe_allow_html=True)
    
    if st.session_state.fail_count >= 4 or is_review_mode:
        st.markdown('<div class="solution-guide">🔍 <b>Aşağıdaki Doğru Çözüm Yolunu İncele</b></div>', unsafe_allow_html=True)
        st.code(curr_ex['solution'], language="python")

    # KOD PANELİ
    if not is_review_mode and st.session_state.fail_count < 4 and not st.session_state.exercise_passed:
        custom_input = ""
        if "input" in curr_ex['solution']:
            st.markdown("👇 **Kullanıcıdan veri bekleniyor! Lütfen kutuya değer giriniz:**")
            custom_input = st.text_input("📝 Girdi Kutusu:", placeholder="Değer yaz...", key=f"inp_{st.session_state.current_module}_{st.session_state.current_exercise}").strip()
            if st.session_state.no_input_error: st.warning("⚠️ Pito: Lütfen önce kutuya bir veri girişi yap!")

        code = st_ace(value=curr_ex['task'], language="python", theme="dracula", font_size=14, height=180, key=f"ace_{st.session_state.current_module}_{st.session_state.current_exercise}", auto_update=True)
        
        if st.button("🔍 Kodumu Kontrol Et", use_container_width=True):
            if "___" in code: st.session_state.feedback_msg = "⚠️ Pito bekliyor: Lütfen önce boşluğu doldur!"; st.rerun()
            elif "input" in curr_ex['solution'] and not custom_input:
                st.session_state.no_input_error = True; st.rerun()
            else:
                st.session_state.no_input_error = False
                old_stdout, new_stdout = sys.stdout, StringIO(); sys.stdout = new_stdout
                try:
                    mock_env = {"print": print, "input": lambda x: custom_input or "10", "int": int, "str": str, "yas": 15, "isim": "Pito", "ad": "Pito"}
                    exec(code, mock_env); out = new_stdout.getvalue(); sys.stdout = old_stdout
                    if curr_ex.get('check', lambda c, o, i: True)(code, out, mock_env):
                        st.session_state.update({'feedback_msg': "✅ Harika! Görevi başarıyla mühürledin.", 'last_output': out, 'exercise_passed': True, 'pito_emotion': 'mutlu'})
                        ex_key = f"{st.session_state.current_module}_{st.session_state.current_exercise}"
                        if ex_key not in st.session_state.scored_exercises: st.session_state.total_score += st.session_state.current_potential_score; st.session_state.scored_exercises.add(ex_key); force_save()
                    else: raise Exception()
                except:
                    sys.stdout = old_stdout; st.session_state.fail_count += 1
                    st.session_state.current_potential_score = max(0, st.session_state.current_potential_score - 5)
                    st.session_state.pito_emotion = "uzgun"
                    if st.session_state.fail_count < 4:
                        st.session_state.feedback_msg = f"❌ {st.session_state.fail_count}. Hatayı yaptın! 5 Puan Kaybettin. Tekrar dene!"
                    else:
                        st.session_state.feedback_msg = "🌿 4 kez hata yaptığın için bu sorudan puan alamadın. Aşağıdaki çözüm yolunu inceleyip sonraki soruya geçelim."
                st.rerun()

    # --- 10. NAVİGASYON ---
    if st.session_state.exercise_passed or is_review_mode or st.session_state.fail_count >= 4:
        cp, cn = st.columns(2)
        with cp:
            if is_review_mode and st.session_state.current_exercise > 0:
                if st.button("⬅️ Önceki"): 
                    st.session_state.update({'current_exercise': st.session_state.current_exercise - 1, 'exercise_passed': False, 'fail_count': 0, 'current_potential_score': 20, 'feedback_msg': "", 'last_output': "", 'pito_emotion': 'standart'}); st.rerun()
        with cn:
            if st.session_state.current_exercise < 4:
                if st.button("➡️ Sonraki"): 
                    st.session_state.update({'current_exercise': st.session_state.current_exercise + 1, 'exercise_passed': False, 'fail_count': 0, 'current_potential_score': 20, 'feedback_msg': "", 'last_output': "", 'pito_emotion': 'standart'}); st.rerun()
            elif st.session_state.current_module < 7:
                if st.button("🏆 Modülü Bitir"):
                    st.balloons()
                    if not is_review_mode:
                        st.session_state.db_module += 1; st.session_state.db_exercise = 0; st.session_state.completed_modules[st.session_state.current_module] = True; force_save()
                    st.session_state.update({'current_module': st.session_state.current_module + 1, 'current_exercise': 0, 'exercise_passed': False, 'fail_count': 0, 'current_potential_score': 20, 'feedback_msg': "", 'last_output': "", 'pito_emotion': 'standart'}); st.rerun()
            elif st.session_state.current_module == 7:
                if st.button("🏁 Akademiyi Tamamla"):
                    st.session_state.completed_modules[7] = True; st.session_state.db_module = 8; force_save(); st.session_state.graduation_view = True; st.rerun()
