import streamlit as st
from streamlit_ace import st_ace
import sys
from io import StringIO
import pandas as pd
from datetime import datetime
from streamlit_gsheets import GSheetsConnection
import os
import base64
import time
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
        'graduation_view': False, 'no_input_error': False, 'pito_emotion': "merhaba"
    }.items():
        st.session_state[k] = v

SINIFLAR = ["9-A", "9-B", "10-A", "10-B", "11-A", "11-B"]
RUTBELER = ["🥚 Yeni Başlayan", "🌱 Python Çırağı", "🪵 Kod Oduncusu", "🧱 Mantık Mimarı", "🌀 Döngü Ustası", "📋 Liste Uzmanı", "📦 Fonksiyon Kaptanı", "🤖 OOP Robotu", "🏆 Python Kahramanı"]

# --- MODERN UI CSS ---
st.markdown("""
    <style>
    header {visibility: hidden;}
    .main .block-container {padding-top: 1.5rem; background-color: #f8fafc;}
    
    /* İlerleme Çubuğu Konteynırı */
    .quest-container {
        background: white; padding: 20px; border-radius: 20px;
        box-shadow: 0 10px 15px -3px rgba(0,0,0,0.1); margin-bottom: 30px;
        border-top: 5px solid #3a7bd5;
    }
    .quest-bar { height: 14px; background: #f1f5f9; border-radius: 20px; margin: 10px 0; overflow: hidden; }
    .quest-fill { height: 100%; background: linear-gradient(90deg, #3a7bd5, #00d2ff); transition: width 0.8s ease-out; }

    /* Konuşma Balonu */
    .pito-bubble {
        position: relative; background: #ffffff; border: 3px solid #3a7bd5;
        border-radius: 30px; padding: 30px; color: #1e293b;
        font-weight: 500; font-size: 1.2rem; box-shadow: 10px 10px 30px rgba(58, 123, 213, 0.1);
        line-height: 1.7; height: 100%; display: flex; align-items: center;
    }
    .pito-bubble::after {
        content: ''; position: absolute; left: -25px; top: 50px;
        border-width: 15px 25px 15px 0; border-style: solid; border-color: transparent #3a7bd5 transparent transparent;
    }

    /* Bilgi Kartları (Stats) */
    .stat-card {
        background: #fdfdfd; border: 1px solid #e2e8f0; border-radius: 12px;
        padding: 10px 15px; text-align: center; color: #64748b; font-weight: bold; font-size: 0.9rem;
    }

    /* Liderlik Kartları */
    .leaderboard-card {
        background: linear-gradient(135deg, #1e293b, #334155); border-radius: 15px;
        padding: 12px; margin-bottom: 10px; color: white; border-left: 4px solid #00d2ff;
    }

    /* Modern Butonlar */
    .stButton > button {
        width: 100%; border-radius: 15px; height: 3.5em; 
        background: linear-gradient(45deg, #3a7bd5, #00d2ff) !important;
        color: white !important; font-weight: bold; border: none; font-size: 1.1rem;
        transition: transform 0.2s;
    }
    .stButton > button:hover { transform: scale(1.02); }
    
    /* Editor ve Giriş Kutusu */
    [data-testid="stTextInput"] { border: 2px solid #e2e8f0; border-radius: 15px; }
    [data-testid="stTextInput"]:focus-within { border-color: #3a7bd5; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. KESİN GIF ÇÖZÜMÜ: BASE64 & HTML INJECTION ---
def show_pito_gif(width=450):
    emotion_map = {
        "standart": "pito_dusunuyor.gif", "merhaba": "pito_merhaba.gif",
        "uzgun": "pito_hata.gif", "mutlu": "pito_basari.gif", "akademi": "pito_mezun.gif"
    }
    gif_file = emotion_map.get(st.session_state.pito_emotion, "pito_dusunuyor.gif")
    base_path = Path(__file__).parent if "__file__" in locals() else Path.cwd()
    gif_path = base_path / "assets" / gif_file
    
    if gif_path.exists():
        with open(gif_path, "rb") as f:
            b64 = base64.b64encode(f.read()).decode()
        st.markdown(f'''
            <div style="display: flex; justify-content: center; align-items: center; width: 100%;">
                <img src="data:image/gif;base64,{b64}" width="{width}px" style="object-fit: contain;">
            </div>
            ''', unsafe_allow_html=True)
    else:
        st.image("https://img.icons8.com/fluency/450/robot-viewer.png", width=width)

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

# --- 5. LİDERLİK TABLOSU (SAĞ PANEL - MÜHÜRLÜ) ---
col_main, col_leader = st.columns([3.3, 1])

with col_leader:
    st.markdown("### 🏆 Onur Kurulu")
    if not db_current.empty:
        class_stats = db_current.groupby("Sınıf")["Puan"].sum().reset_index()
        if not class_stats.empty:
            top_class = class_stats.sort_values(by="Puan", ascending=False).head(1).iloc[0]
            st.markdown(f'<div class="leaderboard-card" style="background: linear-gradient(135deg, #FFD700, #DAA520); color: black; border-left: 4px solid #B8860B;">🥇 <b>Zirve Sınıf: {top_class["Sınıf"]}</b><br>Skor: {int(top_class["Puan"])} Puan</div>', unsafe_allow_html=True)
    
    st.divider()
    t1, t2 = st.tabs(["👥 Sınıfım", "🏫 Okul"])
    with t1:
        if st.session_state.is_logged_in:
            my_c = db_current[db_current["Sınıf"] == st.session_state.student_class].sort_values(by="Puan", ascending=False).head(10)
            for _, r in my_c.iterrows(): st.markdown(f'<div class="leaderboard-card"><b>{r["Rütbe"]} {r["Öğrencinin Adı"]}</b><br>{int(r["Puan"])} Puan</div>', unsafe_allow_html=True)
        else: st.caption("Liderliği görmek için giriş yapmalısın.")
    with t2:
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

# --- 6. GİRİŞ EKRANI VE MEZUNİYET ---
with col_main:
    if not st.session_state.is_logged_in:
        c1, c2 = st.columns([1.5, 2.5])
        with c1:
            st.session_state.pito_emotion = "merhaba"
            show_pito_gif(450)
        with c2:
            st.markdown('<div class="pito-bubble">Selam! Ben <b>Pito</b>. Nusaybin laboratuvarında Python macerasına adım atmaya hazır mısın? Numaranı gir ve mühürlü dünyaya katıl!</div>', unsafe_allow_html=True)
            in_no = st.text_input("Okul Numaran:", key="log_f", placeholder="Sayısal okul numaranı yaz...").strip()
            if in_no:
                if not in_no.isdigit(): st.error("⚠️ Sadece rakam giriniz!")
                else:
                    user_data = db_current[db_current["Okul No"] == in_no]
                    if not user_data.empty:
                        row = user_data.iloc[0]
                        m_v, e_v = int(row['Mevcut Modül']), int(row['Mevcut Egzersiz'])
                        st.info(f"🔍 **{row['Öğrencinin Adı']}** ({row['Sınıf']}), Hoş geldin! En son **{m_v+1}. Modül {e_v+1}. Egzersizde** mühürlenmiştin. Devam edelim mi?")
                        ca, cb = st.columns(2)
                        with ca:
                            if st.button("✅ Evet, Benim"):
                                st.session_state.update({'student_no': in_no, 'student_name': row["Öğrencinin Adı"], 'student_class': row["Sınıf"], 'total_score': int(row["Puan"]), 'db_module': m_v, 'db_exercise': e_v, 'current_module': min(m_v, 7), 'current_exercise': e_v, 'completed_modules': [True if x == "1" else False for x in str(row["Tamamlanan Modüller"]).split(",")], 'is_logged_in': True, 'graduation_view': (m_v >= 8), 'pito_emotion': 'standart'})
                                st.rerun()
                        with cb:
                            if st.button("❌ Hayır, Değilim"): st.rerun()
                    else:
                        st.warning("🌟 Yeni bir akademi kaydı oluştur!")
                        in_name = st.text_input("Adın Soyadın:", key="new_n")
                        in_class = st.selectbox("Sınıfın:", SINIFLAR, key="new_c")
                        if st.button("✨ Kayıt Ol ve Başla"):
                            if in_name:
                                st.session_state.update({'student_no': in_no, 'student_name': in_name, 'student_class': in_class, 'is_logged_in': True, 'pito_emotion': 'standart'})
                                force_save(); st.rerun()
        st.stop()

    if st.session_state.graduation_view:
        st.session_state.pito_emotion = "akademi"
        show_pito_gif(550)
        st.markdown('<div class="pito-bubble" style="text-align:center;">🎊 <b>TEBRİKLER Python Kahramanı!</b> Tüm akademiyi başarıyla tamamlayarak mezun oldun. Nusaybin laboratuvarının gururusun!</div>', unsafe_allow_html=True)
        st.balloons()
        st.success(f"Nihai Skorun: {st.session_state.total_score}")
        c1, c2 = st.columns(2)
        with c1:
            if st.button("🔄 Eğitimi Tekrar Al (Puan Sıfırlanır)"):
                st.session_state.update({'db_module': 0, 'db_exercise': 0, 'current_module': 0, 'current_exercise': 0, 'total_score': 0, 'completed_modules': [False]*8, 'graduation_view': False, 'scored_exercises': set(), 'pito_emotion': 'merhaba'})
                force_save(); st.rerun()
        with c2:
            if st.button("🔍 İnceleme Modu ve Liderlikte Kal"):
                st.session_state.update({'current_module': 0, 'current_exercise': 0, 'graduation_view': False, 'pito_emotion': 'standart'}); st.rerun()
        st.stop()

    # --- 7. MÜHÜRLÜ MÜFREDAT (40 DERİN ADIM) ---
    training_data = [
        {"module_title": "1. İletişim: print() ve Metin Dünyası", "exercises": [
            {"msg": "**Pito'nun Notu:** Python'ın dünyayla konuşma yolu `print()` fonksiyonudur. Ekrana yazacağın metinleri mutlaka tırnak (' ') içine almalısın. Tırnaklar Python'a 'buradaki ifadeyi olduğu gibi yansıt' komutunu verir.\n\n**GÖREV:** Editor içine tam olarak **'Merhaba Pito'** yaz!", "task": "print('___')", "check": lambda c, o, i: "Merhaba Pito" in o, "solution": "print('Merhaba Pito')", "hint": "Metnin başına ve sonuna tek (') tırnak koy."},
            {"msg": "**Pito'un Notu:** Sayılar (Integer), metinlerden farklıdır; tırnak gerektirmezler. Eğer bir sayıya tırnak koyarsan Python onu sayı değil, bir 'yazı' olarak görür.\n\n**GÖREV:** Boşluğa tırnak kullanmadan sadece **100** sayısını yaz.", "task": "print(___)", "check": lambda c, o, i: "100" in o, "solution": "print(100)", "hint": "Sayısal değerleri tırnaksız yazmalısın."},
            {"msg": "**Virgül Operatörü:** Farklı veri tiplerini (metin ve sayı gibi) aynı satırda birleştirirken otomatik bir boşluk koyar.\n\n**GÖREV:** 'Puan:' metni ile **100** sayısını yan yana bas.", "task": "print('Puan:', ___)", "check": lambda c, o, i: "100" in o, "solution": "print('Puan:', 100)", "hint": "Virgülden sonra 100 yaz."},
            {"msg": "**Yorum Satırı:** `#` işareti Python'a 'Bu satırı okuma' demektir. Sadece geliştiricilerin not alması içindir.\n\n**GÖREV:** Satırın en başına **#** işaretini koy.", "task": "___ bu bir nottur", "check": lambda c, o, i: "#" in c, "solution": "# bu bir nottur", "hint": "Klavyeden diyez (#) işaretini kullan."},
            {"msg": "**Kaçış Karakteri:** `\\n` metni alt satıra böler. Sanki Enter tuşuna basılmış gibi davranır.\n\n**GÖREV:** Boşluğa **\\n** yazarak kelimeleri alt alta getir.", "task": "print('Üst' + '___' + 'Alt')", "check": lambda c, o, i: "Üst\nAlt" in o, "solution": "print('Üst\\nAlt')", "hint": "Ters eğik çizgi ve n harfi."}
        ]},
        {"module_title": "2. Hafıza: Değişkenler ve Atama", "exercises": [
            {"msg": "**Değişkenler:** Bellekteki (RAM) kutulardır. `=` işareti sağdaki değeri soldaki kutunun içine koyar (Atama).\n\n**GÖREV:** `yas` kutusuna sayısal olarak **15** değerini ata.", "task": "yas = ___", "check": lambda c, o, i: "15" in str(i.get('yas', '')), "solution": "yas = 15", "hint": "Sadece 15 yaz."},
            {"msg": "**Metin Atama:** Değişken isimlerinde rakamla başlamamaya ve boşluk kullanmamaya dikkat et!\n\n**GÖREV:** `isim` değişkenine **'Pito'** metnini ata.", "task": "isim = '___'", "check": lambda c, o, i: "Pito" in str(i.get('isim', '')), "solution": "isim = 'Pito'", "hint": "Metni tırnaklar içine yaz."},
            {"msg": "**input():** Programı durdurur ve kullanıcıdan bir bilgi bekler. Python bu bilgiyi her zaman 'String' (metin) olarak algılar.\n\n**GÖREV:** Kullanıcıdan adını almak için boşluğa **input** yaz.", "task": "ad = ___('Adın: ')", "check": lambda c, o, i: "input" in c, "solution": "ad = input('Adın: ')", "hint": "Veri girişi fonksiyonunu kullan."},
            {"msg": "**Casting (Dönüşüm):** Sayıları metne çevirip birleştirmek için `str()` fonksiyonunu kullanırız.\n\n**GÖREV:** 10 sayısını metne çeviren **str** komutunu yerleştir.", "task": "print(___(10))", "check": lambda c, o, i: "str" in c, "solution": "print(str(10))", "hint": "str(sayı) yapısını kullan."},
            {"msg": "**Matematik Dönüşümü:** `input()` ile gelen veriyi `int()` ile tam sayıya çevirmelisin.\n\n**GÖREV:** Dışa **int**, içe **input** yazarak sayı girişi alan sistemi kur.", "task": "n = ___(___('S: '))", "check": lambda c, o, i: "int" in c and "input" in c, "solution": "n = int(input('S: '))", "hint": "int(input()) yapısını kur."}
        ]},
        {"module_title": "3. Mantık: Karar Yapıları (If-Else)", "exercises": [
            {"msg": "**Karar:** Programların beyni `if` bloğudur. Karşılaştırmada `=` değil, mutlaka `==` kullanmalısın.", "task": "if 10 ___ 10: print('OK')", "check": lambda c, o, i: "==" in c, "solution": "if 10 == 10:\n    print('OK')", "hint": "Eşitlik için == koy."},
            {"msg": "**B Planı:** `else:` şart sağlanmadığında devreye girer.\n\n**GÖREV:** Şart sağlanmazsa 'Hata' yazdıran yolu tamamlamak için boşluğa **else** yaz.", "task": "if 5 > 10: pass\n___: print('Hata')", "check": lambda c, o, i: "else" in c, "solution": "if 5 > 10: pass\nelse:\n    print('Hata')", "hint": "Sadece else: yaz."},
            {"msg": "**elif:** Birden fazla şartı (A, B, C planı) denetlemek için kullanılır.", "task": "p = 60\nif p < 50: pass\n___ p > 50: print('G')", "check": lambda c, o, i: "elif" in c, "solution": "if p < 50: pass\nelif p > 50:\n    print('G')", "hint": "elif kullan."},
            {"msg": "**and Operatörü:** İki tarafın da doğru olmasını bekler.\n\n**GÖREV:** İki tarafın doğruluğunu denetleyen bağlacı (**and**) boşluğa yaz.", "task": "if 1==1 ___ 2==2: print('OK')", "check": lambda c, o, i: "and" in c, "solution": "if 1==1 and 2==2:\n    print('OK')", "hint": "and yaz."},
            {"msg": "**!=:** 'eşit değilse' anlamına gelir.\n\n**GÖREV:** Sayı 0'a eşit değilse 'Var' yazdıran operatörü (**!=**) koy.", "task": "s = 5\nif s ___ 0: print('Var')", "check": lambda c, o, i: "!=" in c, "solution": "if s != 0:\n    print('Var')", "hint": "!= kullan."}
        ]},
        {"module_title": "4. Otomasyon: For ve While Döngüleri", "exercises": [
            {"msg": "**range:** `range(5)` komutu 0'dan 4'e kadar 5 sayı üretir. `for` bu sayılarda adım adım ilerler.", "task": "for i in ___(5): print(i)", "check": lambda c, o, i: "range" in c, "solution": "for i in range(5):\n    print(i)", "hint": "range yaz."},
            {"msg": "**While:** Şart 'True' olduğu sürece çalışmaya devam eder.", "task": "i = 0\n___ i == 0: print('D'); i += 1", "check": lambda c, o, i: "while" in c, "solution": "i = 0\nwhile i == 0:\n    print('D')\n    i += 1", "hint": "while yaz."},
            {"msg": "**break:** Döngüyü anında sonlandırır. Acil çıkış kapısıdır.", "task": "for i in range(5):\n if i == 1: ___", "check": lambda c, o, i: "break" in c, "solution": "for i in range(5):\n    if i == 1: break\n    print(i)", "hint": "break kullan."},
            {"msg": "**continue:** O anki adımı pas geçer ve başa döner.", "task": "for i in range(3):\n if i == 1: ___", "check": lambda c, o, i: "continue" in c, "solution": "for i in range(3):\n    if i == 1: continue\n    print(i)", "hint": "continue yaz."},
            {"msg": "**in Operatörü:** Listelerde gezinmek için kullanılır.", "task": "for x ___ ['A']: print(x)", "check": lambda c, o, i: "in" in c, "solution": "for x in ['A']:\n    print(x)", "hint": "in anahtarı."}
        ]},
        {"module_title": "5. Gruplama: Listeler", "exercises": [
            {"msg": "**Listeler:** Birden fazla veriyi tek kutuda tutar. Saymaya her zaman 0'dan başlarız!", "task": "L = [___, 20]", "check": lambda c, o, i: "10" in str(i.get('L', '')), "solution": "L = [10, 20]", "hint": "10 yaz."},
            {"msg": "**İndisleme:** Listenin ilk elemanına `[0]` indeksiyle ulaşılır. Buna 'İndisleme' denir.", "task": "L = [50, 60]\nprint(L[___])", "check": lambda c, o, i: "50" in o, "solution": "L = [50, 60]\nprint(L[0])", "hint": "Sıfır indisi."},
            {"msg": "**.append():** Listenin sonuna yeni bir eleman ekler.", "task": "L = [10]\nL.___ (30)", "check": lambda c, o, i: "append" in c, "solution": "L = [10]\nL.append(30)", "hint": "append metodu."},
            {"msg": "**len():** Listenin içindeki toplam eleman sayısını verir.", "task": "L = [1, 2, 3]\nprint(___(L))", "check": lambda c, o, i: "3" in o, "solution": "L = [1, 2, 3]\nprint(len(L))", "hint": "len yaz."},
            {"msg": "**.pop():** Listenin en sonundaki elemanı sepetten çıkarır ve siler.", "task": "L = [1, 2]\nL.___()", "check": lambda c, o, i: "pop" in c, "solution": "L = [1, 2]\nL.pop()", "hint": "pop metodu."}
        ]},
        {"module_title": "6. Modülerlik: Fonksiyonlar ve Sözlükler", "exercises": [
            {"msg": "**def:** Fonksiyon tanımlama anahtarıdır. Tekrar eden kodları paketler.", "task": "___ pito(): print('Hi')", "check": lambda c, o, i: "def" in c, "solution": "def pito():\n    print('Hi')", "hint": "def yaz."},
            {"msg": "**Sözlük:** `{anahtar: değer}` çiftleriyle çalışır. Rehber mantığıdır.", "task": "d = {'ad': '___'}", "check": lambda c, o, i: "Pito" in str(i.get('d', {})), "solution": "d = {'ad': 'Pito'}", "hint": "Pito yaz."},
            {"msg": "**Tuple:** Listeye benzer ama parantez `()` ile kurulur ve içeriği asla değiştirilemez.", "task": "t = (___, 2)", "check": lambda c, o, i: "1" in str(i.get('t', '')), "solution": "t = (1, 2)", "hint": "1 yaz."},
            {"msg": "**.keys():** Sözlükteki tüm etiketleri liste halinde sunar.", "task": "d = {'a':1}\nprint(d.___())", "check": lambda c, o, i: "keys" in c, "solution": "d = {'a':1}\nprint(d.keys())", "hint": "keys metodu."},
            {"msg": "**return:** Fonksiyonun ürettiği sonucu dışarıya 'fırlatır'.", "task": "def f(): ___ 5", "check": lambda c, o, i: "return" in c, "solution": "def f():\n    return 5", "hint": "return kullan."}
        ]},
        {"module_title": "7. Nesneler: OOP Dünyası", "exercises": [
            {"msg": "**class:** Bir taslaktır. Ondan 'Nesneler' (Object) üretiriz. Sınıf bir fabrikadır.", "task": "___ Robot: pass", "check": lambda c, o, i: "class" in c, "solution": "class Robot:\n    pass", "hint": "class yaz."},
            {"msg": "**Robot():** Kalıptan nesne üretmek için sınıf ismini parantezlerle `()` çağırırız.", "task": "class Robot: pass\nr = ___", "check": lambda c, o, i: "Robot" in str(i.get('r', '')), "solution": "class Robot: pass\nr = Robot()", "hint": "Robot() yaz."},
            {"msg": "**Özellikler:** Nesnelerin özellikleri nokta (`.`) yardımıyla atanır.", "task": "class R: pass\nr = R()\nr.___ = 'Mavi'", "check": lambda c, o, i: "renk" in c, "solution": "class R: pass\nr = R()\nr.renk = 'Mavi'", "hint": "renk yaz."},
            {"msg": "**self:** Nesnenin kendisini temsil eden parametredir. Metotlarda ilk sırada olmalıdır.", "task": "class R:\n def ses(___): print('Bip')", "check": lambda c, o, i: "self" in c, "solution": "class R:\n    def ses(self):\n        print('Bip')", "hint": "self yaz."},
            {"msg": "**Method:** r nesnesinin **s()** metodunu çalıştır.", "task": "class R:\n def s(self): pass\nr = R()\nr.___()", "check": lambda c, o, i: "s()" in c, "solution": "class R:\n    def s(self):\n        pass\nr = R()\nr.s()", "hint": "s() yaz."}
        ]},
        {"module_title": "8. Kalıcılık: Dosya Yönetimi", "exercises": [
            {"msg": "**open():** Kaydetmek için kullanılır. **'w'** (write) yazma modudur.", "task": "f = ___('n.txt', '___')", "check": lambda c, o, i: "open" in c and "w" in c, "solution": "f = open('n.txt', 'w')", "hint": "open ve w yaz."},
            {"msg": "**.write():** Veriyi dosyaya kalıcı olarak mühürler.", "task": "f = open('t.txt', 'w')\nf.___('X')", "check": lambda c, o, i: "write" in c, "solution": "f = open('t.txt', 'w')\nf.write('X')\nf.close()", "hint": "write yaz."},
            {"msg": "**'r':** Okuma modudur. Dosyayı sadece görmemizi sağlar.", "task": "f = open('t.txt', '___')", "check": lambda c, o, i: "r" in c, "solution": "f = open('t.txt', 'r')", "hint": "r koy."},
            {"msg": "**.read():** Dosyanın tüm içeriğini belleğe getirir.", "task": "f = open('t.txt', 'r')\nprint(f.___())", "check": lambda c, o, i: "read" in c, "solution": "f = open('t.txt', 'r')\nprint(f.read())", "hint": "read yaz."},
            {"msg": "**.close():** Dosyayı kapatmak hayatidir! Kapatılmazsa veri kaybı olabilir.", "task": "f = open('t.txt', 'r')\nf.___()", "check": lambda c, o, i: "close" in c, "solution": "f = open('t.txt', 'r')\nf.close()", "hint": "close kullan."}
        ]}
    ]

    # --- 8. QUEST BAR ---
    total_steps = 40
    curr_t_idx = (st.session_state.current_module * 5) + (st.session_state.current_exercise + 1)
    progress_perc = (curr_t_idx / total_steps) * 100
    st.markdown(f'''<div class="quest-container">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <span style="font-weight: bold; color: #3a7bd5;">📍 {training_data[st.session_state.current_module]['module_title']}</span>
            <span style="background: #e0f2fe; color: #0369a1; padding: 4px 12px; border-radius: 20px; font-size: 0.8rem; font-weight: bold;">🐍 %{int(progress_perc)} Tamamlandı</span>
            <span style="font-weight: bold; color: #0f172a;">🏆 {RUTBELER[min(sum(st.session_state.completed_modules), 8)]}</span>
        </div>
        <div class="quest-bar"><div class="quest-fill" style="width: {progress_perc}%;"></div></div>
    </div>''', unsafe_allow_html=True)

    module_labels = [f"{'✅' if i < st.session_state.db_module else '📖'} Modül {i+1}" for i in range(min(st.session_state.db_module + 1, 8))]
    sel_mod_label = st.selectbox("📖 Seviye Seç:", module_labels, index=min(st.session_state.current_module, len(module_labels)-1))
    new_m_idx = module_labels.index(sel_mod_label)
    if new_m_idx != st.session_state.current_module:
        st.session_state.update({'current_module': new_m_idx, 'current_exercise': 0, 'fail_count': 0, 'exercise_passed': False, 'current_potential_score': 20, 'feedback_msg': "", 'last_output': "", 'pito_emotion': 'standart'}); st.rerun()

    st.divider()
    curr_ex = training_data[st.session_state.current_module]["exercises"][st.session_state.current_exercise]
    is_review_mode = (st.session_state.current_module < st.session_state.db_module)

    # --- HERO SECTION: PITO + BUBBLE ---
    c_pito, c_bubble = st.columns([1.6, 3.4])
    with c_pito:
        show_pito_gif(450)
    with c_bubble:
        st.markdown(f'<div class="pito-bubble">##### 🗣️ Pito\'nun Notu:<br>{curr_ex["msg"]}</div>', unsafe_allow_html=True)
        # Dashboard Alt Bilgi Barı
        st.markdown(f'''<div style="display: flex; gap: 10px; margin-top: 15px;">
            <div class="stat-card">👣 Adım: {st.session_state.current_exercise + 1}/5</div>
            <div class="stat-card">🎁 Potansiyel: {st.session_state.current_potential_score} Puan</div>
            <div class="stat-card">❌ Hatalar: {st.session_state.fail_count}/4</div>
        </div>''', unsafe_allow_html=True)

    # --- 9. FEEDBACK VE ÇIKTI ---
    if st.session_state.feedback_msg:
        if "✅" in st.session_state.feedback_msg:
            st.success(st.session_state.feedback_msg)
            if st.session_state.last_output:
                st.markdown("##### 🖥️ Kod Çıktısı (Konsol):")
                st.code(st.session_state.last_output, language="text")
        else: st.error(st.session_state.feedback_msg)

    if not st.session_state.exercise_passed and st.session_state.fail_count == 3:
        st.markdown(f'<div class="hint-guide">💡 <b>Pito\'dan İpucu:</b> {curr_ex["hint"]}</div>', unsafe_allow_html=True)
    
    if st.session_state.fail_count >= 4 or is_review_mode:
        st.markdown('<div class="solution-guide">🔍 <b>Mühürlü Çözüm Yolu (Tam Kod)</b></div>', unsafe_allow_html=True)
        st.code(curr_ex['solution'], language="python")

    # KOD PANELİ
    if not is_review_mode and st.session_state.fail_count < 4 and not st.session_state.exercise_passed:
        custom_input = ""
        if "input" in curr_ex['solution']:
            st.markdown("👇 **Veri Girişi Bekleniyor:**")
            custom_input = st.text_input("📝 Buraya yaz:", placeholder="Örn: 10", key=f"inp_{st.session_state.current_module}_{st.session_state.current_exercise}").strip()
            if st.session_state.no_input_error: st.warning("⚠️ Önce kutuya veri girmelisin!")

        code = st_ace(value=curr_ex['task'], language="python", theme="monokai", font_size=16, height=200, key=f"ace_{st.session_state.current_module}_{st.session_state.current_exercise}", auto_update=True)
        
        if st.button("🔍 Kodumu Kontrol Et", use_container_width=True):
            if "___" in code: st.session_state.feedback_msg = "⚠️ Pito bekliyor: Boşluğu doldurmalısın!"; st.rerun()
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
                        st.session_state.feedback_msg = f"❌ {st.session_state.fail_count}. Hata! -5 Puan Kaybettin."
                    else:
                        st.session_state.feedback_msg = "🌿 4 kez hata yaptığın için puan alamadın. Aşağıdaki çözümü incele."
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
                if st.button("🏁 Mezun Ol"):
                    st.session_state.completed_modules[7] = True; st.session_state.db_module = 8; force_save(); st.session_state.graduation_view = True; st.rerun()
