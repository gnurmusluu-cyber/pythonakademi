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

# --- 1. SAYFA VE TASARIM AYARLARI ---
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
    
    /* SOL ÜST KİMLİK KARTI: Kontrast Mühürlendi */
    .user-header-box {
        background-color: #ffffff !important; border: 3px solid #3a7bd5 !important;
        border-radius: 20px !important; padding: 15px 25px !important; margin-bottom: 25px !important;
        box-shadow: 0 10px 25px rgba(58, 123, 213, 0.2) !important;
        display: flex !important; justify-content: space-between !important; align-items: center !important;
    }
    .info-label { color: #64748b !important; font-size: 0.8rem !important; font-weight: 800 !important; text-transform: uppercase; }
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
        position: relative; background: #ffffff; border: 3px solid #3a7bd5;
        border-radius: 25px; padding: 30px; color: #1e293b;
        font-weight: 500; font-size: 1.2rem; box-shadow: 10px 10px 30px rgba(58, 123, 213, 0.1);
        line-height: 1.8; text-align: left;
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

# --- 3. KESİN GIF ÇÖZÜMÜ: BASE64 + HTML RE-RENDER (ANIMASYON FIX) ---
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
        # Safari'de animasyon dondurmayı her renderda benzersiz ID ile çözüyoruz
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
                    st.markdown(f'''<div class="ranking-card"><div><b>{r["Öğrencinin Adı"]}</b><br><small>{r["Rütbe"]}</small></div><div style="color:#3a7bd5; font-weight:800;">{int(r["Puan"])}</div></div>''', unsafe_allow_html=True)
        with t2:
            for _, r in db_current.sort_values(by="Puan", ascending=False).head(10).iterrows():
                st.markdown(f'''<div class="ranking-card"><div><b>{r["Öğrencinin Adı"]}</b> ({r["Sınıf"]})<br><small>{r["Rütbe"]}</small></div><div style="color:#3a7bd5; font-weight:800;">{int(r["Puan"])}</div></div>''', unsafe_allow_html=True)

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

# --- 6. GİRİŞ VE MEZUNİYET ---
with col_main:
    if st.session_state.is_logged_in:
        current_rank = RUTBELER[min(sum(st.session_state.completed_modules), 8)]
        st.markdown(f'''<div class="user-header-box"><div><div class="info-label">ÖĞRENCİ</div><div class="info-value">👤 {st.session_state.student_name} ({st.session_state.student_class})</div></div><div style="text-align:center;"><div class="info-label">RÜTBE</div><div class="info-value">{current_rank}</div></div><div style="text-align:right;"><div class="info-label">TOPLAM PT</div><div class="score-badge">⭐ {st.session_state.total_score}</div></div></div>''', unsafe_allow_html=True)

    if not st.session_state.is_logged_in:
        c1, c2 = st.columns([1.6, 3.4])
        with c1: st.session_state.pito_emotion = "merhaba"; show_pito_gif(450)
        with c2:
            st.markdown('<div class="pito-bubble" style="margin-top: 60px;">Merhaba Geleceğin Yazılımcısı!<br><br>Ben <b>Pito</b>. Nusaybin laboratuvarında Python macerasına hazır mısın? Numaranı gir ve mühürlü dünyaya katıl!</div>', unsafe_allow_html=True)
            in_no = st.text_input("Okul Numaran:", key="login_f", placeholder="Numaranı mühürle...").strip()
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

    # --- 7. MUTLAK MÜFREDAT (8 MODÜL / 40 ADIM) ---
    training_data = [
        {"module_title": "1. İletişim: print() ve Metinler", "exercises": [
            {"msg": "**print():** Python'ın sesidir. Metinleri (String) mutlaka tırnak (' ') içine almalısın.", "task": "print('___')", "check": lambda c, o, i: "Merhaba Pito" in o, "solution": "print('Merhaba Pito')", "hint": "Tırnak koymayı unutma."},
            {"msg": "**Integers:** Sayılar tırnak gerektirmez. Tırnak koyarsan matematik yapamazsın.", "task": "print(___)", "check": lambda c, o, i: "100" in o, "solution": "print(100)", "hint": "Sadece 100 yaz."},
            {"msg": "**Virgül:** Farklı veri tiplerini aynı satırda otomatik boşlukla birleştirir.", "task": "print('PT:', ___)", "check": lambda c, o, i: "100" in o, "solution": "print('PT:', 100)", "hint": "100 yaz."},
            {"msg": "**# Yorum:** Bilgisayarın okumadığı, sadece bizim için olan notlardır.", "task": "___ bu nottur", "check": lambda c, o, i: "#" in c, "solution": "# bu nottur", "hint": "# koy."},
            {"msg": "**Newline:** `\\n` metni alt satıra fırlatır.", "task": "print('A' + '___' + 'B')", "check": lambda c, o, i: "A\nB" in o, "solution": "print('A\\nB')", "hint": "\\n yaz."}
        ]},
        {"module_title": "2. Hafıza: Değişkenler ve input()", "exercises": [
            {"msg": "**Değişkenler:** RAM'deki isimlendirilmiş kutulardır. `=` ile değer atanır.", "task": "yas = ___", "check": lambda c, o, i: "15" in str(i.get('yas', '')), "solution": "yas = 15", "hint": "15 yaz."},
            {"msg": "**input():** Kullanıcıdan bilgi bekler ve her zaman metin (String) getirir.", "task": "ad = ___('Ad: ')", "check": lambda c, o, i: "input" in c, "solution": "ad = input('Ad: ')", "hint": "input yaz."},
            {"msg": "**str():** Sayıları metne çevirip birleştirmek (Casting) için kullanılır.", "task": "print(___(10))", "check": lambda c, o, i: "str" in c, "solution": "print(str(10))", "hint": "str yaz."},
            {"msg": "**int():** input() metnini matematik için tam sayıya çevirir.", "task": "n = ___(___('S: '))", "check": lambda c, o, i: "int" in c and "input" in c, "solution": "n=int(input())", "hint": "int(input())."},
            {"msg": "**İsimlendirme:** Değişkenler rakamla başlayamaz ve boşluk içeremez.", "task": "isim = ___", "check": lambda c, o, i: "Pito" in str(i.get('isim', '')), "solution": "isim = 'Pito'", "hint": "'Pito'."}
        ]},
        {"module_title": "3. Mantık: Karar Yapıları (If-Else)", "exercises": [
            {"msg": "**Eşitlik:** Sorgulamada `=` değil, mutlaka `==` (çift eşittir) kullanılır.", "task": "if 10 ___ 10: print('OK')", "check": lambda c, o, i: "==" in c, "solution": "if 10 == 10:\n    print('OK')", "hint": "== koy."},
            {"msg": "**else:** Şart sağlanmadığında çalışan 'B Planı'dır.", "task": "if 1 > 5: pass\n___: print('H')", "check": lambda c, o, i: "else" in c, "solution": "else:", "hint": "else: yaz."},
            {"msg": "**elif:** Birden fazla farklı şartı denetlemek için kullanılır.", "task": "if p < 50: pass\n___ p > 50: pass", "check": lambda c, o, i: "elif" in c, "solution": "elif", "hint": "elif kullan."},
            {"msg": "**and:** İki tarafın da doğru olmasını bekleyen bağlaçtır.", "task": "if 1==1 ___ 2==2: pass", "check": lambda c, o, i: "and" in c, "solution": "and", "hint": "and yaz."},
            {"msg": "**!=:** 'Eşit değilse' anlamına gelen zıtlık operatörüdür.", "task": "if s ___ 0: pass", "check": lambda c, o, i: "!=" in c, "solution": "!=", "hint": "!= koy."}
        ]},
        {"module_title": "4. Otomasyon: For ve While Döngüleri", "exercises": [
            {"msg": "**range:** Belirtilen sayı kadar adım üretir.", "task": "for i in ___(5): pass", "check": lambda c, o, i: "range" in c, "solution": "range", "hint": "range yaz."},
            {"msg": "**While:** Şart 'True' olduğu sürece sonsuz dönebilir.", "task": "___ i < 5: pass", "check": lambda c, o, i: "while" in c, "solution": "while", "hint": "while yaz."},
            {"msg": "**break:** Döngüyü o an bitiren acil çıkış kapısıdır.", "task": "for i in R: if i==1: ___", "check": lambda c, o, i: "break" in c, "solution": "break", "hint": "break."},
            {"msg": "**continue:** O adımı pas geçip döngünün başına döner.", "task": "for i in R: if i==1: ___", "check": lambda c, o, i: "continue" in c, "solution": "continue", "hint": "continue."},
            {"msg": "**in:** Liste içinde gezinmeyi sağlayan aitlik kelimesidir.", "task": "for x ___ liste: pass", "check": lambda c, o, i: "in" in c, "solution": "in", "hint": "in yaz."}
        ]},
        {"module_title": "5. Gruplama: Listeler", "exercises": [
            {"msg": "**Listeler:** Birden fazla veriyi tek sepette tutar. `[]` ile kurulur.", "task": "L = [___, 20]", "check": lambda c, o, i: "10" in str(i.get('L','')), "solution": "10", "hint": "10 yaz."},
            {"msg": "**İndis:** İlk elemana ulaşmak için her zaman `0` kullanılır.", "task": "print(L[___])", "check": lambda c, o, i: "0" in c, "solution": "0", "hint": "0 yaz."},
            {"msg": "**.append():** Listenin sonuna yeni bir eleman mühürler.", "task": "L.___ (30)", "check": lambda c, o, i: "append" in c, "solution": "append", "hint": "append."},
            {"msg": "**len():** Listenin içindeki toplam eleman sayısını ölçer.", "task": "n = ___(L)", "check": lambda c, o, i: "len" in c, "solution": "len", "hint": "len yaz."},
            {"msg": "**.pop():** Son elemanı sepetten çıkarıp siler.", "task": "L.___()", "check": lambda c, o, i: "pop" in c, "solution": "pop", "hint": "pop."}
        ]},
        {"module_title": "6. Fonksiyonlar ve Sözlükler", "exercises": [
            {"msg": "**def:** Fonksiyon (kod paketi) tanımlamak için kullanılır.", "task": "___ pito(): pass", "check": lambda c, o, i: "def" in c, "solution": "def", "hint": "def yaz."},
            {"msg": "**Sözlük:** `{anahtar: değer}` yapısıyla çalışır.", "task": "d = {'ad': '___'}", "check": lambda c, o, i: "Pito" in str(i.get('d',{})), "solution": "Pito", "hint": "Pito."},
            {"msg": "**Tuple:** Değiştirilemeyen (mühürlü) listelerdir. `()` ile kurulur.", "task": "t = (___, 2)", "check": lambda c, o, i: "1" in str(i.get('t','')), "solution": "1", "hint": "1 yaz."},
            {"msg": "**.keys():** Sözlükteki tüm etiketleri (anahtarları) verir.", "task": "d.___()", "check": lambda c, o, i: "keys" in c, "solution": "keys", "hint": "keys."},
            {"msg": "**return:** Fonksiyonun sonucunu dışarıya fırlatır.", "task": "def f(): ___ 5", "check": lambda c, o, i: "return" in c, "solution": "return", "hint": "return."}
        ]},
        {"module_title": "7. Nesneler: OOP Dünyası", "exercises": [
            {"msg": "**class:** Nesne üretmek için kullanılan fabrikadır.", "task": "___ Robot: pass", "check": lambda c, o, i: "class" in c, "solution": "class", "hint": "class yaz."},
            {"msg": "**Robot():** Sınıftan canlı bir nesne üretir (Instance).", "task": "r = ___", "check": lambda c, o, i: "Robot" in str(i.get('r','')), "solution": "Robot()", "hint": "Robot()."},
            {"msg": "**Nokta (.):** Nesnenin özelliklerine nokta ile ulaşılır.", "task": "r.___ = 'Mavi'", "check": lambda c, o, i: "renk" in c, "solution": "renk", "hint": "renk."},
            {"msg": "**self:** Nesnenin kendisini temsil eden gizli parametredir.", "task": "def s(___): pass", "check": lambda c, o, i: "self" in c, "solution": "self", "hint": "self."},
            {"msg": "**Metot:** Nesneye bağlı çalışan fonksiyonlardır.", "task": "r.___()", "check": lambda c, o, i: "s()" in c, "solution": "s()", "hint": "s()."}
        ]},
        {"module_title": "8. Kalıcılık: Dosya Yönetimi", "exercises": [
            {"msg": "**open():** Dosyayı 'w' (yazma) modunda açar.", "task": "f = ___('a.txt', '___')", "check": lambda c, o, i: "open" in c and "w" in c, "solution": "open, w", "hint": "open ve w."},
            {"msg": "**.write():** Veriyi dosyaya kalıcı mühürler.", "task": "f.___('X')", "check": lambda c, o, i: "write" in c, "solution": "write", "hint": "write."},
            {"msg": "**'r':** Dosyayı sadece görmek için okuma modudur.", "task": "f = open('a.txt', '___')", "check": lambda c, o, i: "r" in c, "solution": "r", "hint": "r koy."},
            {"msg": "**.read():** Tüm içeriği belleğe çeker.", "task": "f.___()", "check": lambda c, o, i: "read" in c, "solution": "read", "hint": "read."},
            {"msg": "**.close():** Dosyayı kapatmak sistem sağlığı için hayatidir.", "task": "f.___()", "check": lambda c, o, i: "close" in c, "solution": "close", "hint": "close."}
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
    if not is_review_mode and st.session_state.fail_count < 4 and not st.session_state.exercise_passed:
        code = st_ace(value=curr_ex.get('task',''), language="python", theme="monokai", font_size=16, height=220)
        if st.button("🔍 Kodumu Kontrol Et"):
            # Kontrol Mantığı...
            old_stdout, new_stdout = sys.stdout, StringIO(); sys.stdout = new_stdout
            try:
                mock_env = {"print": print, "input": lambda x: "10", "int": int, "str": str, "yas": 15, "isim": "Pito"}
                exec(code, mock_env); out = new_stdout.getvalue(); sys.stdout = old_stdout
                if curr_ex.get('check', lambda c,o,i: True)(code, out, mock_env):
                    st.session_state.update({'feedback_msg': "✅ Mühürlendi!", 'exercise_passed': True, 'pito_emotion': 'mutlu'})
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
            st.session_state.update({'exercise_passed': False, 'fail_count': 0, 'current_potential_score': 20, 'pito_emotion': 'standart'}); st.rerun()
