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

# --- 2. BEYAZ ZEMINE VE TÜM CİHAZLARA UYGUN TASARIM (CSS) ---
st.markdown("""
    <style>
    /* Uygulama Arka Planını Beyaz Yap */
    [data-testid="stAppViewContainer"], [data-testid="stHeader"], [data-testid="stToolbar"] {
        background-color: #FFFFFF !important;
    }
    header {visibility: hidden;}

    /* Global Metin Rengi (Koyu Lacivert) */
    html, body, [class*="st-"] { color: #1E293B !important; font-family: 'Inter', sans-serif; }
    h1, h2, h3, h4, h5, h6, p, span, label, .stMarkdown { color: #1E293B !important; }

    /* Açılır Menü ve Giriş Kutuları Görünürlüğü */
    div[data-baseweb="select"] > div {
        background-color: #F8FAFC !important;
        color: #1E293B !important;
        border: 2px solid #E2E8F0 !important;
    }
    div[data-baseweb="popover"], div[data-baseweb="popover"] > div { background-color: #FFFFFF !important; }
    div[data-baseweb="popover"] li { color: #1E293B !important; background-color: #FFFFFF !important; }
    div[data-baseweb="popover"] li:hover { background-color: #F1F5F9 !important; }
    
    div[data-baseweb="base-input"] { background-color: #F8FAFC !important; border: 2px solid #E2E8F0 !important; border-radius: 10px !important; }
    input { color: #1E293B !important; }

    /* Pito Konuşma Balonu */
    .pito-bubble {
        position: relative; background: #F1F5F9; border: 2px solid #3a7bd5;
        border-radius: 20px; padding: 25px; margin: 0 auto 20px auto; 
        color: #1E293B !important; font-weight: 500; font-size: 1.15rem; 
        text-align: center; box-shadow: 0 10px 25px rgba(58, 123, 213, 0.08);
        max-width: 850px;
    }
    .pito-bubble:after {
        content: ''; position: absolute; bottom: -20px; left: 50%; transform: translateX(-50%);
        border-width: 20px 20px 0; border-style: solid; border-color: #3a7bd5 transparent;
    }

    /* Oyunlaştırma Kartları */
    .rank-badge {
        display: inline-block; background: #3a7bd5; color: white !important;
        padding: 4px 12px; border-radius: 20px; font-size: 0.9rem; font-weight: bold;
    }
    .leaderboard-card { 
        background: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 12px; 
        padding: 12px; margin-bottom: 8px; color: #1E293B !important;
        box-shadow: 0 2px 4px rgba(0,0,0,0.02);
    }
    .champion-card { 
        background: linear-gradient(135deg, #FFD700, #F59E0B); 
        border-radius: 15px; padding: 15px; margin-top: 20px; 
        color: #FFFFFF !important; text-align: center; font-weight: bold;
    }

    /* Buton Tasarımı */
    .stButton > button { 
        width: 100%; border-radius: 12px; height: 3.5em; 
        background: linear-gradient(45deg, #3a7bd5, #00d2ff) !important; 
        color: white !important; font-weight: 600; border: none;
    }

    /* Mobil Uyumluluk */
    @media (max-width: 768px) {
        .main .block-container { padding: 1rem !important; }
        [data-testid="column"] { width: 100% !important; flex: 1 1 100% !important; }
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. VERİLER VE HAFIZA ---
SINIFLAR = ["9-A", "9-B", "10-A", "10-B", "11-A", "11-B"]
RUTBELER = [
    "🥚 Yumurta", "🌱 Filiz", "🪵 Oduncu", "🧱 Mimar", 
    "🌀 Usta", "📋 Uzman", "📦 Kaptan", "🤖 Robot", "🏆 Kahraman"
]

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

def get_pito_gif(gif_name, width=280):
    gif_path = f"assets/{gif_name}.gif"
    if os.path.exists(gif_path):
        with open(gif_path, "rb") as f:
            encoded = base64.b64encode(f.read()).decode()
        return f'<div style="text-align: center;"><img src="data:image/gif;base64,{encoded}" width="{width}" style="max-width: 100%;"></div>'
    return f'<div style="text-align: center;"><img src="https://img.icons8.com/fluency/200/robot-viewer.png" width="{width}"></div>'

# --- 4. VERİ TABANI ---
SHEET_URL = "https://docs.google.com/spreadsheets/d/1lat8rO2qm9QnzEUYlzC_fypG3cRkGlJfSfTtwNvs318/edit#gid=0"
conn = st.connection("gsheets", type=GSheetsConnection)

def get_db():
    try:
        df = conn.read(spreadsheet=SHEET_URL, ttl=0)
        df["Okul No"] = df["Okul No"].astype(str).str.split('.').str[0].str.strip()
        for col in ["Puan", "Mevcut Modül", "Mevcut Egzersiz"]:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype(int)
        return df.dropna(subset=["Okul No"])
    except: return pd.DataFrame()

def force_save():
    try:
        no = str(st.session_state.student_no).strip()
        df_all = get_db()
        df_clean = df_all[df_all["Okul No"] != no]
        progress_str = ",".join(["1" if m else "0" for m in st.session_state.completed_modules])
        rank = RUTBELER[sum(st.session_state.completed_modules)]
        new_row = pd.DataFrame([[no, st.session_state.student_name, st.session_state.student_class, int(st.session_state.total_score), rank, progress_str, int(st.session_state.db_module), int(st.session_state.db_exercise), datetime.now().strftime("%H:%M:%S")]], columns=["Okul No", "Öğrencinin Adı", "Sınıf", "Puan", "Rütbe", "Tamamlanan Modüller", "Mevcut Modül", "Mevcut Egzersiz", "Tarih"])
        conn.update(spreadsheet=SHEET_URL, data=pd.concat([df_clean, new_row], ignore_index=True))
    except: pass

# --- 5. GİRİŞ EKRANI ---
if not st.session_state.is_logged_in:
    _, col_mid, _ = st.columns([1, 2, 1])
    with col_mid:
        st.markdown('<div class="pito-bubble">Merhaba! Ben <b>Pito</b>.<br>Python Akademisi macerasına hoş geldin!</div>', unsafe_allow_html=True)
        st.markdown(get_pito_gif("pito_merhaba", width=300), unsafe_allow_html=True)
        if st.session_state.rejected_user: st.warning("⚠️ Lütfen kendi okul numaranı gir!")
        in_no = st.text_input("Okul Numaran:", key="login_field").strip()
        if in_no and in_no.isdigit():
            df = get_db()
            user_data = df[df["Okul No"] == in_no] if not df.empty else pd.DataFrame()
            if not user_data.empty:
                row = user_data.iloc[0]
                st.info(f"🔍 Bu numara **{row['Öğrencinin Adı']}** ismine kayıtlı.")
                st.markdown("<h4 style='text-align: center;'>Bu sen misin?</h4>", unsafe_allow_html=True)
                c1, c2 = st.columns(2)
                with c1:
                    if st.button("✅ Evet"):
                        mv, ev = int(row['Mevcut Modül']), int(row['Mevcut Egzersiz'])
                        st.session_state.update({'student_no': in_no, 'student_name': row["Öğrencinin Adı"], 'student_class': row["Sınıf"], 'total_score': int(row["Puan"]), 'db_module': mv, 'db_exercise': ev, 'current_module': min(mv, 7), 'current_exercise': ev if mv < 8 else 0, 'completed_modules': [True if x == "1" else False for x in str(row["Tamamlanan Modüller"]).split(",")], 'is_logged_in': True, 'pito_emotion': "pito_dusunuyor" if mv < 8 else "pito_mezun"})
                        st.rerun()
                with c2:
                    if st.button("❌ Hayır"):
                        st.session_state.rejected_user = True
                        if "login_field" in st.session_state: del st.session_state["login_field"]
                        st.rerun()
            else:
                in_name = st.text_input("Adın Soyadın:", key="new_name")
                in_class = st.selectbox("Sınıfın:", SINIFLAR, key="new_class")
                if st.button("Maceraya Başla! ✨") and in_name:
                    st.session_state.update({'student_no': in_no, 'student_name': in_name, 'student_class': in_class, 'is_logged_in': True})
                    force_save(); st.rerun()
    st.stop()

# --- 6. MÜFREDAT ---
training_data = [
    {"module_title": "1. Veri Çıkışı: print()", "exercises": [
        {"msg": "Ekrana bir yazı yazdırmak için **print()** kullanılır. Metinleri tırnak (' ') içine almalısın. \n\n**Hadi dene:** Ekrana **'Merhaba Pito'** yazdır.", "task": "print('___')", "check": lambda c, o: "Merhaba Pito" in o, "solution": "print('Merhaba Pito')"},
        {"msg": "Sayılar için tırnak gerekmez. Python bunları matematiksel değer olarak tanır. \n\n**Hadi dene:** Ekrana sadece **100** sayısını yazdır.", "task": "print(___)", "check": lambda c, o: "100" in o, "solution": "print(100)"},
        {"msg": "Verileri yan yana yazdırmak için **virgül (,)** kullanılır. \n\n**Hadi dene:** **'Puan:'** metni ile **100** sayısını yan yana yazdır.", "task": "print('Puan:', ___)", "check": lambda c, o: "100" in o, "solution": "print('Puan:', 100)"},
        {"msg": "**# (Diyez)** işaretiyle başlayan satırlar çalıştırılmaz (not). \n\n**Hadi dene:** Satırın başına **#** işaretini koy ve yanına **Not** yaz.", "task": "___ Bu bir not", "check": lambda c, o: "#" in c, "solution": "# Not"},
        {"msg": "Alt satıra geçmek için **'\\n'** kullanılır. \n\n**Hadi dene:** Tek print içinde **'Üst'** ve **'Alt'** kelimelerini alt alta yazdır.", "task": "print('Üst' + '___' + 'Alt')", "check": lambda c, o: "\n" in o, "solution": "print('Üst\\nAlt')"}
    ]},
    {"module_title": "2. Değişkenler: Bilgi Saklama", "exercises": [
        {"msg": "Değişkenler bilgileri hafızada tutar. **(=)** ile atama yapılır. \n\n**Hadi dene:** **yas** değişkenine **15** ata ve yazdır.", "task": "yas = ___\nprint(yas)", "check": lambda c, o: "15" in o, "solution": "yas = 15"},
        {"msg": "**isim** değişkenine **'Pito'** ata ve yazdır.", "task": "isim = '___'\nprint(isim)", "check": lambda c, o: "Pito" in o, "solution": "isim = 'Pito'"},
        {"msg": "**input()** ile kullanıcıdan bilgi alırız. \n\n**Hadi dene:** **'Adın: '** sorusuyla bir girdi al, bunu **ad** değişkenine ata.", "task": "ad = ___('Adın: ')\nprint(ad)", "check": lambda c, o: "input" in c, "solution": "ad = input('Adın: ')"},
        {"msg": "Sayıları metne çevirmek için **str()** kullanılır. \n\n**Hadi dene:** **s = 10** sayısını metne çevirip yazdır.", "task": "s = 10\nprint(___(s))", "check": lambda c, o: "str" in c, "solution": "str(s)"},
        {"msg": "Girdileri sayıya çevirmek için **int()** kullanılır. \n\n**Hadi dene:** Gelen inputu **int**'e çevir ve üzerine 1 ekle.", "task": "n = ___(___('S: '))\nprint(n + 1)", "check": lambda c, o: "int" in c and "input" in c, "solution": "n = int(input('10'))"}
    ]},
    {"module_title": "3. Karar Yapıları", "exercises": [{"msg": "Eşitlik için **(==)** kullanılır. \n\n**Hadi dene:** Eğer 10 sayısı **10'a eşitse** 'X' yazdır.", "task": "if 10 ___ 10: print('X')", "check": lambda c, o: "==" in c, "solution": "if 10 == 10: print('X')"}, {"msg": "Şart yanlışsa **else:** bloğu çalışır. \n\n**Hadi dene:** 5, 10'dan büyük değilse **'Y'** yazdıran bir **else** kur.", "task": "if 5>10: pass\n___: print('Y')", "check": lambda c, o: "else" in c, "solution": "else"}, {"msg": "Büyük veya eşiti kontrol için **>=** kullanılır. \n\n**Hadi dene:** Eğer 5, **5'ten büyük veya eşitse** 'Z' yazdır.", "task": "if 5 ___ 5: print('Z')", "check": lambda c, o: ">=" in c, "solution": ">="}, {"msg": "**and** ile iki şartın da doğruluğu istenir. \n\n**Hadi dene:** Eğer 1==1 **ve** 2==2 ise 'OK' yazdır.", "task": "if 1==1 ___ 2==2: print('OK')", "check": lambda c, o: "and" in c, "solution": "and"}, {"msg": "**elif** alternatif şarttır. \n\n**Hadi dene:** İlk şart yanlış ama **5==5** doğruysa 'A' yazdır.", "task": "if 5>10: pass\n___ 5==5: print('A')", "check": lambda c, o: "elif" in c, "solution": "elif"}]},
    {"module_title": "4. Döngüler: Tekrarın Gücü", "exercises": [{"msg": "**for** ve **range(3)** ile 3 kez tekrar yap.", "task": "for i in ___(3): print('X')", "check": lambda c, o: o.count("X")==3, "solution": "range"}, {"msg": "**while** şart doğruyken döner. \n\n**Hadi dene:** **i < 1** doğruyken 'Y' yazdıran döngü kur.", "task": "i=0\n___ i<1: print('Y'); i+=1", "check": lambda c, o: "while" in c, "solution": "while"}, {"msg": "**break** döngüyü bitirir.", "task": "for i in range(3):\n if i==1: ___\n print(i)", "check": lambda c, o: "break" in n, "solution": "break"}, {"msg": "**continue** adımı atlar.", "task": "for i in range(3):\n if i==1: ___\n print(i)", "check": lambda c, o: "continue" in n, "solution": "continue"}, {"msg": "**i** sayacını yazdır.", "task": "for i in range(2): print(___)", "check": lambda c, o: "1" in o, "solution": "i"}]},
    {"module_title": "5. Listeler", "exercises": [{"msg": "Liste **[ ]** içine yazılır. \n\n**Hadi dene:** **10** ve **20** olan bir liste oluştur.", "task": "L = [___, 20]", "check": lambda c, o: "10" in c, "solution": "L=[10, 20]"}, {"msg": "İlk eleman **0.** indekstir. \n\n**Hadi dene:** L listesinin **0. indeksini** yazdır.", "task": "L=[5,6]\nprint(L[___])", "check": lambda c, o: "5" in o, "solution": "0"}, {"msg": "**len()** boyutu ölçer.", "task": "L=[1,2]\nprint(___(L))", "check": lambda c, o: "2" in o, "solution": "len"}, {"msg": "**append()** veri ekler. 30 ekle.", "task": "L=[10]\nL.___(___)\nprint(L)", "check": lambda c, o: "30" in o, "solution": "append"}, {"msg": "**pop()** veri siler. Sonuncuyu sil.", "task": "L=[1,2]\nL.___()\nprint(L)", "check": lambda c, o: "1" in o, "solution": "pop"}]},
    {"module_title": "6. Fonksiyonlar ve Türler", "exercises": [{"msg": "**def** ile f tanımla.", "task": "___ f(): print('X')", "check": lambda c, o: "def" in c, "solution": "def"}, {"msg": "**Tuple** (Demet) **( )** ile oluşturulur.", "task": "t = (___, 2)\nprint(t)", "check": lambda c, o: "1" in c, "solution": "1"}, {"msg": "**Sözlük** (Dict) anahtar:değer tutar.", "task": "d = {'ad': '___'}\nprint(d['ad'])", "check": lambda c, o: "Pito" in c, "solution": "Pito"}, {"msg": "**keys()** anahtarları getirir.", "task": "d={'a':1}\nprint(d.___())", "check": lambda c, o: "keys" in c, "solution": "keys"}, {"msg": "**Set** (Küme) benzersiz veri tutar.", "task": "s = {1, 2, ___}\nprint(s)", "check": lambda c, o: "1" in c, "solution": "1"}]},
    {"module_title": "7. OOP: Nesne Tabanlı", "exercises": [{"msg": "**class** ile Robot sınıfı oluştur.", "task": "___ Robot: pass", "check": lambda c, o: "class" in c, "solution": "class"}, {"msg": "R'den p nesnesi üret.", "task": "class R: pass\np = ___()", "check": lambda c, o: "R()" in c, "solution": "R"}, {"msg": "**renk** özelliği ata.", "task": "class R: pass\np=R()\np.___ = 'Mavi'\nprint(p.renk)", "check": lambda c, o: "renk" in c, "solution": "renk"}, {"msg": "Metotlar için **self** kullanılır.", "task": "class R:\n def ___(self):\n  print('Bip!')", "check": lambda c, o: "ses" in c, "solution": "ses"}, {"msg": "**r**'den **s** metodunu çağır.", "task": "class R:\n def s(self): print('X')\nr=R()\nr.___()", "check": lambda c, o: "s()" in c, "solution": "s"}]},
    {"module_title": "8. Dosya Yönetimi", "exercises": [{"msg": "**'w'** kipiyle dosya aç.", "task": "dosya = ___('n.txt', '___')", "check": lambda c, o: "open" in c, "solution": "w"}, {"msg": "**write()** ile 'Pito' yaz ve kapat.", "task": "f = open('t.txt', 'w'); f.___('Pito'); f.close()", "check": lambda c, o: "write" in c, "solution": "write"}, {"msg": "**'r'** kipiyle oku.", "task": "f = open('t.txt', '___')", "check": lambda c, o: "'r'" in c, "solution": "r"}, {"msg": "**read()** ile içeriği yazdır.", "task": "f = open('t.txt', 'r')\nprint(f.___())\nf.close()", "check": lambda c, o: "read" in c, "solution": "read"}, {"msg": "**close()** ile dosyayı kapat.", "task": "f = open('t.txt', 'r')\nf.___()", "check": lambda c, o: "close" in c, "solution": "close"}]}
]

# --- 8. OYUNLASTIRMA VE ARA YÜZ ---
col_main, col_side = st.columns([3, 1])
rank_idx = sum(st.session_state.completed_modules)
student_rank = RUTBELER[rank_idx]

with col_main:
    # Üst Bilgi ve Rütbe Rozeti
    st.markdown(f"#### 👋 {st.session_state.student_name} | <span class='rank-badge'>{student_rank}</span> | ⭐ Puan: {int(st.session_state.total_score)}", unsafe_allow_html=True)
    
    # İlerleme Çubuğu
    total_prog = (rank_idx * 5 + st.session_state.current_exercise) / 40
    st.progress(total_prog, text=f"Akademi İlerlemesi: %{int(total_prog*100)}")

    if st.session_state.db_module >= 8:
        if not st.session_state.celebrated:
            st.balloons(); st.session_state.celebrated = True
            st.session_state.pito_emotion = "pito_mezun"
        st.success("🎉 Tebrikler! Akademiden Mezun Oldun.")
        if st.button("🔄 Eğitimi Sıfırla"):
            st.session_state.update({'db_module': 0, 'db_exercise': 0, 'total_score': 0, 'current_module': 0, 'current_exercise': 0, 'completed_modules': [False]*8, 'scored_exercises': set(), 'celebrated': False, 'pito_emotion': "pito_dusunuyor", 'feedback_type': None})
            force_save(); st.rerun()

    # Modül Seçimi
    st.markdown("**📌 Mevcut Dersin:**")
    mod_titles = [f"{'✅' if st.session_state.completed_modules[i] else '📖'} Modül {i+1}" for i in range(8)]
    sel_mod = st.selectbox("mod_sel", mod_titles, index=st.session_state.current_module, label_visibility="collapsed")
    m_idx = mod_titles.index(sel_mod)
    if m_idx != st.session_state.current_module:
        st.session_state.update({'current_module': m_idx, 'current_exercise': 0, 'feedback_type': None})
        st.rerun()

    st.divider()
    curr_ex = training_data[m_idx]["exercises"][st.session_state.current_exercise]
    is_locked = (m_idx < st.session_state.db_module)

    # Pito ve Rehberlik
    c1, c2 = st.columns([1, 4])
    with c1: st.markdown(get_pito_gif(st.session_state.pito_emotion, width=180), unsafe_allow_html=True)
    with c2:
        st.info(f"##### 🗣️ Pito:\n{curr_ex['msg']}")
        st.caption(f"Adım: {st.session_state.current_exercise + 1}/5 | Puan Değeri: {st.session_state.current_potential_score}")

    code = st_ace(value=curr_ex['task'], language="python", theme="dracula", font_size=15, height=200, readonly=is_locked, key=f"ace_{m_idx}_{st.session_state.current_exercise}", auto_update=True)

    # Geri Bildirim ve İnceleme Modu
    if st.session_state.feedback_type:
        if st.session_state.feedback_type == "error": st.error(f"❌ {st.session_state.feedback_msg}")
        else: st.success(f"✅ {st.session_state.feedback_msg}")

    if is_locked:
        st.success("**✅ Çözüm Örneği:**")
        st.code(curr_ex['solution'])
    else:
        u_in = st.text_input("👇 Terminal:", key=f"t_{m_idx}") if "input(" in code else ""
        if st.button("🔍 Kontrol Et"):
            old_stdout, new_stdout = sys.stdout, StringIO()
            sys.stdout = new_stdout
            try:
                exec(code.replace("___", "None"), {"input": lambda p: str(u_in or "10"), "print": print, "int": int, "str": str, "len": len, "open": open, "range": range})
                out = new_stdout.getvalue()
                if curr_ex['check'](code, out) and "___" not in code:
                    st.session_state.update({'exercise_passed': True, 'pito_emotion': "pito_basari", 'feedback_type': "success", 'feedback_msg': "Harika! Bir adım daha yaklaştın."})
                    if f"{m_idx}_{st.session_state.current_exercise}" not in st.session_state.scored_exercises:
                        st.session_state.total_score += st.session_state.current_potential_score
                        st.session_state.scored_exercises.add(f"{m_idx}_{st.session_state.current_exercise}")
                        if st.session_state.db_exercise < 4: st.session_state.db_exercise += 1
                        else: st.session_state.db_module += 1; st.session_state.db_exercise = 0; st.session_state.completed_modules[m_idx] = True
                        force_save()
                else: st.session_state.update({'pito_emotion': "pito_hata", 'feedback_type': "error", 'feedback_msg': "Hatalı yanıt, yönergeyi tekrar oku!"})
            except Exception as e: st.session_state.update({'pito_emotion': "pito_hata", 'feedback_type': "error", 'feedback_msg': f"Kod hatası: {e}"})
            st.rerun()

    # Navigasyon
    if st.session_state.exercise_passed or is_locked:
        nb1, nb2 = st.columns(2)
        with nb1:
            if st.session_state.current_exercise > 0:
                if st.button("⬅️ Önceki"): st.session_state.update({'current_exercise': st.session_state.current_exercise - 1, 'feedback_type': None}); st.rerun()
        with nb2:
            if st.session_state.current_exercise < 4:
                if st.button("➡️ Sonraki"): st.session_state.update({'current_exercise': st.session_state.current_exercise + 1, 'exercise_passed': False, 'pito_emotion': "pito_dusunuyor", 'feedback_type': None}); st.rerun()
            elif m_idx < 7:
                if st.button("🏆 Modülü Bitir"): st.session_state.update({'current_module': m_idx + 1, 'current_exercise': 0, 'pito_emotion': "pito_dusunuyor", 'feedback_type': None}); st.rerun()

with col_side:
    st.markdown("### 🏆 Sıralama")
    df = get_db()
    t1, t2 = st.tabs(["👥 Sınıf", "🏫 Okul"])
    with t1:
        if not df.empty:
            for _, r in df[df["Sınıf"] == st.session_state.student_class].sort_values("Puan", ascending=False).head(8).iterrows():
                st.markdown(f'<div class="leaderboard-card"><b>{r["Öğrencinin Adı"]}</b><br>{int(r["Puan"])} Puan</div>', unsafe_allow_html=True)
    with t2:
        if not df.empty:
            for _, r in df.sort_values("Puan", ascending=False).head(8).iterrows():
                st.markdown(f'<div class="leaderboard-card"><b>{r["Öğrencinin Adı"]}</b><br>{int(r["Puan"])} Puan</div>', unsafe_allow_html=True)
    if not df.empty:
        sums = df.groupby("Sınıf")["Puan"].sum()
        if not sums.empty: st.markdown(f'<div class="champion-card">🏆 Lider Sınıf<br>{sums.idxmax()}</div>', unsafe_allow_html=True)