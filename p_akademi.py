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

# --- MODERN UI CSS (KESİN GÖRÜNÜRLÜK VE NEON ÇUBUK) ---
st.markdown("""
    <style>
    header {visibility: hidden;}
    .main .block-container {padding-top: 1rem; background-color: #0f172a;}
    
    /* SOL ÜST KİMLİK KARTI */
    .user-header-box {
        background-color: #ffffff !important; border: 3px solid #3a7bd5 !important;
        border-radius: 20px !important; padding: 15px 25px !important; margin-bottom: 25px !important;
        box-shadow: 0 10px 25px rgba(58, 123, 213, 0.2) !important;
        display: flex !important; justify-content: space-between !important; align-items: center !important;
    }
    .info-label { color: #64748b !important; font-size: 0.8rem !important; font-weight: 800 !important; }
    .info-value { color: #1e293b !important; font-size: 1.1rem !important; font-weight: 900 !important; }
    .score-badge { 
        background: linear-gradient(45deg, #3a7bd5, #00d2ff) !important; color: white !important;
        padding: 8px 20px !important; border-radius: 30px !important; font-weight: 900 !important;
    }

    /* NEON İLERLEME ÇUBUĞU */
    .quest-container {
        background: #1e293b !important; border: 2px solid #3a7bd5 !important;
        border-radius: 25px !important; padding: 25px !important; margin-bottom: 30px !important;
    }
    .quest-bar { 
        height: 24px !important; background: #0f172a !important; 
        border-radius: 15px !important; margin: 15px 0 !important; overflow: hidden !important; 
        border: 1px solid #334155 !important;
    }
    .quest-fill { 
        height: 100% !important; background: linear-gradient(90deg, #3a7bd5, #00d2ff) !important; 
        box-shadow: 0 0 15px rgba(0, 210, 255, 0.5) !important; transition: width 0.8s ease-in-out !important; 
    }
    .quest-text { color: #f8fafc !important; font-weight: 800 !important; font-size: 1.1rem !important; }

    /* PİTO KONUŞMA BALONU */
    .pito-bubble {
        position: relative; background: #ffffff !important; border: 3px solid #3a7bd5 !important;
        border-radius: 25px !important; padding: 30px !important; color: #1e293b !important;
        font-weight: 500 !important; font-size: 1.15rem !important; box-shadow: 10px 10px 30px rgba(58, 123, 213, 0.1) !important;
        line-height: 1.7 !important; text-align: left !important;
    }
    .pito-bubble::after {
        content: ''; position: absolute; left: -25px; top: 50px;
        border-width: 15px 25px 15px 0; border-style: solid; border-color: transparent #3a7bd5 transparent transparent;
    }

    /* LİDERLİK KARTLARI */
    .ranking-card {
        background-color: #ffffff !important; color: #1e293b !important;
        border-radius: 12px; padding: 12px; margin-bottom: 10px;
        display: flex; justify-content: space-between; align-items: center;
        border-left: 5px solid #3a7bd5;
    }
    .ranking-card b { color: #1e293b !important; }
    
    .stButton > button {
        border-radius: 15px; height: 4em; background: linear-gradient(45deg, #3a7bd5, #00d2ff) !important;
        color: white !important; font-weight: bold; border: none; font-size: 1.1rem;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. KESİN GIF ÇÖZÜMÜ ---
def get_base64_gif(file_name):
    base_path = Path(__file__).parent.absolute()
    asset_path = base_path / "assets" / file_name
    if asset_path.exists():
        with open(asset_path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    return None

def show_pito_gif(width=450):
    emotion_map = {
        "standart": "pito_dusunuyor.gif", "merhaba": "pito_merhaba.gif",
        "uzgun": "pito_hata.gif", "mutlu": "pito_basari.gif", "akademi": "pito_mezun.gif"
    }
    gif_file = emotion_map.get(st.session_state.pito_emotion, "pito_dusunuyor.gif")
    b64 = get_base64_gif(gif_file)
    if b64:
        uid = f"pito_{int(time.time() * 1000)}"
        st.markdown(f'<div style="display: flex; justify-content: center;"><img src="data:image/gif;base64,{b64}" id="{uid}" width="{width}px" style="border-radius: 20px;"></div>', unsafe_allow_html=True)
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

# --- 5. LİDERLİK TABLOSU ---
col_main, col_stats = st.columns([3.2, 1])
with col_stats:
    st.markdown("### 🏆 Onur Kurulu")
    if db_current is not None and not db_current.empty:
        class_stats = db_current.groupby("Sınıf")["Puan"].sum().reset_index()
        top_class = class_stats.sort_values(by="Puan", ascending=False).head(1).iloc[0]
        st.markdown(f'''<div style="background: linear-gradient(135deg, #FFD700 0%, #F59E0B 100%); color: black; border-radius: 15px; padding: 20px; text-align: center; font-weight: bold; margin-bottom: 20px;">👑 <b>ŞAMPİYON: {top_class["Sınıf"]}</b><br>{int(top_class["Puan"])} PT</div>''', unsafe_allow_html=True)
        t1, t2 = st.tabs(["👥 Sınıfım", "🌍 Okul"])
        with t1:
            if st.session_state.is_logged_in:
                my_c = db_current[db_current["Sınıf"] == st.session_state.student_class].sort_values(by="Puan", ascending=False).head(8)
                for _, r in my_c.iterrows():
                    st.markdown(f'''<div class="ranking-card"><div><b>{r["Öğrencinin Adı"]}</b><br><small>{r["Rütbe"]}</small></div><div style="color:#3a7bd5; font-weight:800;">{int(r["Puan"])} PT</div></div>''', unsafe_allow_html=True)
        with t2:
            for _, r in db_current.sort_values(by="Puan", ascending=False).head(10).iterrows():
                st.markdown(f'''<div class="ranking-card"><div><b>{r["Öğrencinin Adı"]}</b> ({r["Sınıf"]})<br><small>{r["Rütbe"]}</small></div><div style="color:#3a7bd5; font-weight:800;">{int(r["Puan"])} PT</div></div>''', unsafe_allow_html=True)

def force_save():
    try:
        no = str(st.session_state.student_no).strip()
        df_all = get_db()
        df_clean = df_all[df_all["Okul No"] != no]
        prog = ",".join(["1" if m else "0" for m in st.session_state.completed_modules])
        rank = RUTBELER[min(sum(st.session_state.completed_modules), 8)]
        new_row = pd.DataFrame([[no, st.session_state.student_name, st.session_state.student_class, int(st.session_state.total_score), rank, prog, int(st.session_state.db_module), int(st.session_state.db_exercise), datetime.now().strftime("%H:%M")]], columns=["Okul No", "Öğrencinin Adı", "Sınıf", "Puan", "Rütbe", "Tamamlanan Modüller", "Mevcut Modül", "Mevcut Egzersiz", "Tarih"])
        conn.update(spreadsheet=SHEET_URL, data=pd.concat([df_clean, new_row], ignore_index=True))
    except: pass

# --- 6. GİRİŞ VE MÜFREDAT AKIŞI ---
with col_main:
    if st.session_state.is_logged_in:
        current_rank = RUTBELER[min(sum(st.session_state.completed_modules), 8)]
        st.markdown(f'''<div class="user-header-box"><div><div class="info-label">AKADEMİ ÖĞRENCİSİ</div><div class="info-value">👤 {st.session_state.student_name} ({st.session_state.student_class})</div></div><div style="text-align:center;"><div class="info-label">RÜTBE</div><div class="info-value">{current_rank}</div></div><div style="text-align:right;"><div class="info-label">MÜHÜRLÜ PUAN</div><div class="score-badge">⭐ {st.session_state.total_score}</div></div></div>''', unsafe_allow_html=True)

    if not st.session_state.is_logged_in:
        c1, c2 = st.columns([1.6, 3.4])
        with c1: st.session_state.pito_emotion = "merhaba"; show_pito_gif(450)
        with c2:
            st.markdown('<div class="pito-bubble" style="margin-top: 50px;">Merhaba Geleceğin Yazılımcısı!<br><br>Ben <b>Pito</b>. Nusaybin laboratuvarında Python macerasına hazır mısın? Numaranı gir ve mühürlü dünyaya katıl!</div>', unsafe_allow_html=True)
            in_no = st.text_input("Okul Numaran:", key="login_f", placeholder="Örn: 123").strip()
            if in_no and in_no.isdigit():
                user_data = db_current[db_current["Okul No"] == in_no] if db_current is not None else pd.DataFrame()
                if not user_data.empty:
                    row = user_data.iloc[0]
                    m_v = int(row['Mevcut Modül'])
                    st.info(f"🔍 **{row['Öğrencinin Adı']}**, Hoş geldin! {'🎓 Mezuniyet mühürlendi.' if m_v >= 8 else f'En son {m_v+1}. Modülde kalmıştın.'}")
                    if st.button("✅ Devam Et"):
                        st.session_state.update({'student_no': in_no, 'student_name': row["Öğrencinin Adı"], 'student_class': row["Sınıf"], 'total_score': int(row["Puan"]), 'db_module': m_v, 'db_exercise': int(row['Mevcut Egzersiz']), 'current_module': min(m_v, 7), 'current_exercise': int(row['Mevcut Egzersiz']), 'completed_modules': [True if x == "1" else False for x in str(row["Tamamlanan Modüller"]).split(",")], 'is_logged_in': True, 'graduation_view': (m_v >= 8), 'pito_emotion': 'standart'}); st.rerun()
                else:
                    in_name = st.text_input("Adın Soyadın:", key="reg_name")
                    in_class = st.selectbox("Sınıfın:", SINIFLAR, key="reg_class")
                    if st.button("✨ Kayıt Ol ve Başla") and in_name:
                        st.session_state.update({'student_no': in_no, 'student_name': in_name, 'student_class': in_class, 'is_logged_in': True, 'pito_emotion': 'standart'})
                        force_save(); st.rerun()
        st.stop()

    if st.session_state.graduation_view:
        st.session_state.pito_emotion = "akademi"; show_pito_gif(550)
        st.markdown('<div class="pito-bubble" style="text-align:center;">🎊 <b>TEBRİKLER Python Kahramanı!</b><br>Nusaybin laboratuvarının gururusun. Tüm akademi mühürlendi!</div>', unsafe_allow_html=True)
        st.balloons()
        if st.button("🔄 Eğitimi Tekrar Al (Sıfırla)"):
            st.session_state.update({'db_module': 0, 'db_exercise': 0, 'current_module': 0, 'current_exercise': 0, 'total_score': 0, 'completed_modules': [False]*8, 'graduation_view': False, 'scored_exercises': set(), 'pito_emotion': 'merhaba'}); force_save(); st.rerun()
        if st.button("🔍 İnceleme Modu"): st.session_state.graduation_view = False; st.rerun()
        st.stop()

    # --- 7. MUTLAK MÜFREDAT: 8 MODÜL / 40 DERİN EGZERSİZ ---
    training_data = [
        {"module_title": "1. İletişim: print() ve Metin Dünyası", "exercises": [
            {"msg": "**Pito'nun Notu:** Python'ın dünyayla konuştuğu tek kapı `print()` fonksiyonudur. Ekrana yazacağın metinleri mutlaka tırnak (' ') içine almalısın. Tırnaklar bilgisayara 'bu bir yazı dizisidir' mesajını verir.\n\n**GÖREV:** Editor içine tam olarak **'Merhaba Pito'** metnini tırnaklar içerisinde yaz ve kontrol et!", "task": "print('___')", "check": lambda c, o, i: "Merhaba Pito" in o, "solution": "print('Merhaba Pito')", "hint": "Metnin başına ve sonuna tek (') tırnak koy."},
            {"msg": "**Sayılar (Integers):** Sayılar tırnak gerektirmezler. Eğer bir sayıya tırnak koyarsan Python onu sayı değil, bir 'yazı' olarak görür ve üzerinde toplama gibi işlemler yapamaz.\n\n**GÖREV:** Boşluğa tırnak kullanmadan sadece **100** sayısını yaz.", "task": "print(___)", "check": lambda c, o, i: "100" in o, "solution": "print(100)", "hint": "Rakamları tırnaksız yazmalısın."},
            {"msg": "**Virgül Operatörü:** Virgül (`,`) farklı veri tiplerini aynı satırda birleştirir ve araya otomatik bir boşluk koyar. Bu, değişkenleri ve mesajları birleştirmek için en profesyonel yöntemdir.\n\n**GÖREV:** 'Puan:' metni ile **100** sayısını yan yana basmak için virgülden sonraki boşluğa sadece **100** yaz.", "task": "print('Puan:', ___)", "check": lambda c, o, i: "100" in o, "solution": "print('Puan:', 100)", "hint": "Virgülden sonra 100 yaz."},
            {"msg": "**# Yorum Satırı:** Diyez işareti Python'a 'Bu satırı görmezden gel' demektir. Sadece biz yazılımcıların kod içine not alması içindir; kodun çalışmasını asla etkilemez.\n\n**GÖREV:** Satırın en başına **#** işaretini koyarak bu satırı etkisiz bir nota dönüştür.", "task": "___ bu bir nottur", "check": lambda c, o, i: "#" in c, "solution": "# bu bir nottur", "hint": "Klavyeden diyez (#) işaretini en başa yerleştir."},
            {"msg": "**Newline:** `\\n` (new line) kaçış karakteri metni alt satıra böler. Sanki klavyede Enter tuşuna basılmış gibi davranır.\n\n**GÖREV:** 'Üst' ve 'Alt' kelimelerini alt alta getirmek için tırnaklar içindeki boşluğa **\\n** yaz.", "task": "print('Üst' + '___' + 'Alt')", "check": lambda c, o, i: "Üst\nAlt" in o, "solution": "print('Üst\\nAlt')", "hint": "Ters eğik çizgi ve n harfi (\\n)."}
        ]},
        {"module_title": "2. Hafıza: Değişkenler ve input()", "exercises": [
            {"msg": "**Değişkenler:** RAM'deki isimlendirilmiş kutulardır. `=` işareti bir 'atama operatörü'dür ve sağdaki değeri soldaki kutunun içine koyar.\n\n**GÖREV:** `yas` ismindeki hafıza kutusuna sayısal olarak **15** değerini ata.", "task": "yas = ___", "check": lambda c, o, i: "15" in str(i.get('yas', '')), "solution": "yas = 15", "hint": "Eşittir işaretinden sonra sadece 15 yaz."},
            {"msg": "**input():** Programı durdurur ve kullanıcıdan bir bilgi bekler. Python bu bilgiyi ne olursa olsun her zaman 'String' (metin) olarak algılar.\n\n**GÖREV:** Kullanıcıdan adını almak için boşluğa veri alma fonksiyonu olan **input** yaz.", "task": "ad = ___('Adın: ')", "check": lambda c, o, i: "input" in c, "solution": "ad = input('Adın: ')", "hint": "input kelimesini kullan."},
            {"msg": "**Casting:** Sayıları metne çevirmemiz gerektiğinde (Buna 'Casting' diyoruz) `str()` fonksiyonunu kullanırız. Bu, farklı tipleri birleştirirken hata almanı önler.\n\n**GÖREV:** 10 sayısını metne çeviren **str** fonksiyonunu boşluğa yerleştir.", "task": "print(___(10))", "check": lambda c, o, i: "str" in c, "solution": "print(str(10))", "hint": "str(değişken) formunu kullan."},
            {"msg": "**int():** `input()` verisini matematiksel işleme sokmak için onu `int()` fonksiyonu ile 'tam sayıya' çevirmelisin.\n\n**GÖREV:** Dış boşluğa **int**, içe **input** yazarak sayı girişi alan sistemi kur.", "task": "n = ___(___('S: '))", "check": lambda c, o, i: "int" in c and "input" in c, "solution": "n = int(input('S: '))", "hint": "int(input()) yapısını kur."},
            {"msg": "**İsimlendirme:** Değişken isimlerinde rakamla başlamamaya ve boşluk kullanmamaya dikkat et!\n\n**GÖREV:** `isim` değişkenine **'Pito'** metnini ata.", "task": "isim = '___'", "check": lambda c, o, i: "Pito" in str(i.get('isim', '')), "solution": "isim = 'Pito'", "hint": "Tırnaklar içine Pito yaz."}
        ]},
        {"module_title": "3. Mantık: Karar Yapıları (If-Else)", "exercises": [
            {"msg": "**Eşitlik:** Karar yapılarında `=` (atama) ile `==` (eşitlik sorgusu) çok farklıdır. Sorgularken mutlaka çift eşittir kullanmalısın.", "task": "if 10 ___ 10: print('Tamam')", "check": lambda c, o, i: "==" in c, "solution": "if 10 == 10:\n    print('Tamam')", "hint": "== operatörünü kullan."},
            {"msg": "**B Planı:** `else:` şart sağlanmadığında devreye giren yoldur. Şart sağlanmadığında ne yapılacağını belirler.", "task": "if 5 > 10: pass\n___: print('Hata')", "check": lambda c, o, i: "else" in c, "solution": "if 5 > 10: pass\nelse:\n    print('Hata')", "hint": "Sadece else: yaz."},
            {"msg": "**elif:** Birden fazla şartı denetlemek için kullanılır. Şartlar yukarıdan aşağıya taranır.\n\n**GÖREV:** Puan 50'den büyükse kontrolü için boşluğa **elif** yaz.", "task": "p = 60\nif p < 50: pass\n___ p > 50: print('Geçti')", "check": lambda c, o, i: "elif" in c, "solution": "if p < 50: pass\nelif p > 50:\n    print('Geçti')", "hint": "elif komutunu kullan."},
            {"msg": "**and:** Bu bağlaç iki tarafın da doğru (True) olmasını bekler. Biri bile yanlışsa blok çalışmaz.", "task": "if 1==1 ___ 2==2: print('OK')", "check": lambda c, o, i: "and" in c, "solution": "if 1==1 and 2==2:\n    print('OK')", "hint": "and anahtarını yerleştir."},
            {"msg": "**!=:** 'eşit değilse' anlamına gelir. Şartın gerçekleşmediği durumları denetler.", "task": "s = 5\nif s ___ 0: print('Var')", "check": lambda c, o, i: "!=" in c, "solution": "if s != 0:\n    print('Var')", "hint": "!= operatörünü kullan."}
        ]},
        {"module_title": "4. Otomasyon: For ve While Döngüleri", "exercises": [
            {"msg": "**range:** `range(5)` komutu 0'dan 4'e kadar 5 sayı üretir. `for` bu sayılarda adım adım ilerler.", "task": "for i in ___(5): print(i)", "check": lambda c, o, i: "range" in c, "solution": "for i in range(5):\n    print(i)", "hint": "range yaz."},
            {"msg": "**While:** Şart 'True' olduğu sürece çalışmaya devam eder. Sonsuz döngüden kaçmak için içeride şartı bozmalısın.", "task": "i = 0\n___ i == 0: print('D'); i += 1", "check": lambda c, o, i: "while" in c, "solution": "i = 0\nwhile i == 0:\n    print('D')\n    i += 1", "hint": "while yaz."},
            {"msg": "**break:** Döngüyü anında sonlandırır. Şart sağlandığı an 'acil çıkış kapısıdır'.", "task": "for i in range(5):\n if i == 1: ___", "check": lambda c, o, i: "break" in c, "solution": "for i in range(5):\n    if i == 1: break\n    print(i)", "hint": "break kullan."},
            {"msg": "**continue:** O anki adımı pas geçer ve döngünün en başına geri döner. Altındaki kodları o tur için okumaz.", "task": "for i in range(3):\n if i == 1: ___", "check": lambda c, o, i: "continue" in c, "solution": "for i in range(3):\n    if i == 1: continue\n    print(i)", "hint": "continue yaz."},
            {"msg": "**in:** Listelerde gezinmek için kullanılır. Her bir elemanı sırayla değişkenimize atar.", "task": "for x ___ ['A']: print(x)", "check": lambda c, o, i: "in" in c, "solution": "for x in ['A']:\n    print(x)", "hint": "in anahtarını yaz."}
        ]},
        {"module_title": "5. Gruplama: Listeler (Veri Sepeti)", "exercises": [
            {"msg": "**Listeler:** Birden fazla veriyi tek kutuda tutar. Python'da saymaya her zaman 0'dan başlarız!", "task": "L = [___, 20]", "check": lambda c, o, i: "10" in str(i.get('L','')), "solution": "L = [10, 20]", "hint": "10 yaz."},
            {"msg": "**İndeksleme:** Listenin ilk elemanına `[0]` indeksiyle ulaşılır. Bu kurala 'İndisleme' denir.", "task": "L = [50, 60]\nprint(L[___])", "check": lambda c, o, i: "50" in o, "solution": "L = [50, 60]\nprint(L[0])", "hint": "0 yaz."},
            {"msg": "**.append():** Listenin sonuna yeni bir eleman ekler. Listeni dinamik olarak büyütür.", "task": "L = [10]\nL.___ (30)", "check": lambda c, o, i: "append" in c, "solution": "L.append(30)", "hint": "append metodu."},
            {"msg": "**len():** Listenin içindeki toplam eleman sayısını (uzunluğu) verir.", "task": "L = [1, 2, 3]\nprint(___(L))", "check": lambda c, o, i: "3" in o, "solution": "print(len(L))", "hint": "len yaz."},
            {"msg": "**.pop():** Listenin en sonundaki elemanı sepetten çıkarır ve siler.", "task": "L = [1, 2]\nL.___()", "check": lambda c, o, i: "pop" in c, "solution": "L.pop()", "hint": "pop metodu."}
        ]},
        {"module_title": "6. Modülerlik: Fonksiyonlar ve Sözlükler", "exercises": [
            {"msg": "**def:** Tekrar eden kodları paketlemek (Define) için kullanılır. Fonksiyonu bir kez yazıp her yerde çağırırsın.", "task": "___ pito(): print('Hi')", "check": lambda c, o, i: "def" in c, "solution": "def pito():\n    print('Hi')", "hint": "def yaz."},
            {"msg": "**Sözlük:** `{anahtar: değer}` çiftleriyle çalışır. Rehberdeki isim ve numara mantığıdır.", "task": "d = {'ad': '___'}", "check": lambda c, o, i: "Pito" in str(i.get('d', {})), "solution": "d = {'ad': 'Pito'}", "hint": "Pito yaz."},
            {"msg": "**Tuple:** Listeye benzer ama parantez `()` ile kurulur ve içeriği asla değiştirilemez.", "task": "t = (___, 2)", "check": lambda c, o, i: "1" in str(i.get('t', '')), "solution": "t = (1, 2)", "hint": "1 yaz."},
            {"msg": "**.keys():** Sözlükteki tüm etiketleri (anahtarları) liste halinde bize sunar.", "task": "d = {'a':1}\nprint(d.___())", "check": lambda c, o, i: "keys" in c, "solution": "d.keys()", "hint": "keys metodu."},
            {"msg": "**return:** Fonksiyonun ürettiği sonucu dışarıya 'fırlatır'. Bu değer artık başka bir değişkene atanabilir.", "task": "def f(): ___ 5", "check": lambda c, o, i: "return" in c, "solution": "return 5", "hint": "return kullan."}
        ]},
        {"module_title": "7. Nesneler: OOP Dünyası", "exercises": [
            {"msg": "**class:** Bir taslaktır. Ondan 'Nesneler' (Object) üretiriz. Sınıf fabrikayken, nesne o fabrikadan çıkan üründür.", "task": "___ Robot: pass", "check": lambda c, o, i: "class" in c, "solution": "class Robot:\n    pass", "hint": "class yaz."},
            {"msg": "**Robot():** Kalıptan nesne üretmek için sınıf ismini parantezlerle çağırırız. (Örnekleme)", "task": "class Robot: pass\nr = ___", "check": lambda c, o, i: "Robot" in str(i.get('r','')), "solution": "r = Robot()", "hint": "Robot() yaz."},
            {"msg": "**Özellikler:** Nesnelerin özellikleri nokta (`.`) yardımıyla atanır. Rengi, hızı, adı gibi kimlik bilgileridir.", "task": "r.___ = 'Mavi'", "check": lambda c, o, i: "renk" in c, "solution": "r.renk = 'Mavi'", "hint": "renk yaz."},
            {"msg": "**self:** Nesnenin kendisini temsil eden gizli parametredir. Metotlarda (Sınıf içi fonksiyonlar) ilk sıradadır.", "task": "class R:\n def ses(___): print('Bip')", "check": lambda c, o, i: "self" in c, "solution": "self", "hint": "self yaz."},
            {"msg": "**Method:** Nesnenin bir eylemini çalıştırmak için nokta ve metod ismi kullanılır.", "task": "r.___()", "check": lambda c, o, i: "s()" in c, "solution": "r.s()", "hint": "s() yaz."}
        ]},
        {"module_title": "8. Kalıcılık: Dosya Yönetimi", "exercises": [
            {"msg": "**open():** Kaydetmek için kullanılır. **'w'** (write) yazma modudur. Dosya yoksa oluşturur.", "task": "f = ___('a.txt', '___')", "check": lambda c, o, i: "open" in c and "w" in c, "solution": "f = open('a.txt', 'w')", "hint": "open ve w."},
            {"msg": "**.write():** Veriyi dosyanın içine kalıcı olarak mühürler.", "task": "f.___('X')", "check": lambda c, o, i: "write" in c, "solution": "f.write('X')", "hint": "write metodu."},
            {"msg": "**'r':** Okuma modudur. Dosyayı sadece görmemizi sağlar, değiştirmemizi engeller.", "task": "f = open('t.txt', '___')", "check": lambda c, o, i: "r" in c, "solution": "r", "hint": "r koy."},
            {"msg": "**.read():** Dosyanın tüm içeriğini bir metin olarak belleğe çeker.", "task": "print(f.___())", "check": lambda c, o, i: "read" in c, "solution": "read", "hint": "read yaz."},
            {"msg": "**.close():** Dosyayı kapatmak hayatidir! Kapatılmazsa veri kaybı veya sistem hatası olabilir.", "task": "f.___()", "check": lambda c, o, i: "close" in c, "solution": "f.close()", "hint": "close kullan."}
        ]}
    ]

    # --- 8. NEON İLERLEME PANELİ ---
    total_steps = 40
    curr_t_idx = (st.session_state.current_module * 5) + (st.session_state.current_exercise + 1)
    progress_perc = (curr_t_idx / total_steps) * 100
    st.markdown(f'''<div class="quest-container"><div class="quest-text">📍 {training_data[st.session_state.current_module]['module_title']} <span style="float:right;">🐍 %{int(progress_perc)} TAMAMLANDI</span></div><div class="quest-bar"><div class="quest-fill" style="width: {progress_perc}%;"></div></div></div>''', unsafe_allow_html=True)

    st.divider()
    curr_ex = training_data[st.session_state.current_module]["exercises"][st.session_state.current_exercise]
    is_review_mode = (st.session_state.current_module < st.session_state.db_module)

    c_pito, c_bubble = st.columns([1.5, 3.5])
    with c_pito: show_pito_gif(450)
    with c_bubble:
        st.markdown(f'''<div class="pito-bubble"><b>🗣️ Pito'nun Notu:</b><br><br>{curr_ex["msg"]}</div>''', unsafe_allow_html=True)
        st.markdown(f'''<div style="display:flex; gap:15px; margin-top:20px;"><div class="stat-card">👣 Adım: {st.session_state.current_exercise + 1}/5</div><div class="stat-card">🎁 Potansiyel: {st.session_state.current_potential_score} PT</div><div class="stat-card" style="color:#ef4444">❌ Hata: {st.session_state.fail_count}/4</div></div>''', unsafe_allow_html=True)

    # --- 9. KOD PANELİ VE KONTROL ---
    if st.session_state.feedback_msg:
        if "✅" in st.session_state.feedback_msg: st.success(st.session_state.feedback_msg)
        else: st.error(st.session_state.feedback_msg)

    if not is_review_mode and st.session_state.fail_count < 4 and not st.session_state.exercise_passed:
        custom_input = ""
        if "input" in curr_ex['solution']: custom_input = st.text_input("📝 Girdi Kutusu:", key=f"inp_{st.session_state.current_module}_{st.session_state.current_exercise}").strip()
        
        code = st_ace(value=curr_ex.get('task',''), language="python", theme="monokai", font_size=16, height=220)
        
        if st.button("🔍 Kodumu Kontrol Et", use_container_width=True):
            if "___" in code: st.session_state.feedback_msg = "⚠️ Boşluğu doldurmalısın!"; st.rerun()
            else:
                old_stdout, new_stdout = sys.stdout, StringIO(); sys.stdout = new_stdout
                try:
                    mock_env = {"print": print, "input": lambda x: custom_input or "10", "int": int, "str": str, "yas": 15, "isim": "Pito"}
                    exec(code, mock_env); out = new_stdout.getvalue(); sys.stdout = old_stdout
                    if curr_ex.get('check', lambda c,o,i: True)(code, out, mock_env):
                        st.session_state.update({'feedback_msg': "✅ Mühürlendi! Harika gidiyorsun.", 'exercise_passed': True, 'pito_emotion': 'mutlu'})
                        st.session_state.total_score += st.session_state.current_potential_score; force_save(); st.rerun()
                    else: raise Exception()
                except:
                    sys.stdout = old_stdout; st.session_state.fail_count += 1
                    st.session_state.current_potential_score = max(0, st.session_state.current_potential_score - 5)
                    st.session_state.pito_emotion = "uzgun"; st.rerun()
    
    if st.session_state.exercise_passed or is_review_mode or st.session_state.fail_count >= 4:
        if st.session_state.fail_count >= 4 or is_review_mode: st.code(curr_ex['solution'])
        if st.button("➡️ Sonraki Adıma Geç"):
            st.session_state.current_exercise += 1
            if st.session_state.current_exercise >= 5: 
                st.session_state.current_module += 1; st.session_state.current_exercise = 0; st.session_state.db_module += 1; force_save()
            st.session_state.update({'exercise_passed': False, 'fail_count': 0, 'current_potential_score': 20, 'feedback_msg': "", 'pito_emotion': 'standart'}); st.rerun()
