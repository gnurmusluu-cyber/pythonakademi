import streamlit as st
from streamlit_ace import st_ace
import sys
from io import StringIO
import pandas as pd
from datetime import datetime
from streamlit_gsheets import GSheetsConnection
import base64
import time
from pathlib import Path

# --- 1. SAYFA YAPILANDIRMASI ---
st.set_page_config(layout="wide", page_title="Pito Python Akademi", initial_sidebar_state="collapsed")

# --- 2. SESSION STATE (KESİN DURUM YÖNETİMİ) ---
if 'is_logged_in' not in st.session_state:
    st.session_state.update({
        'student_name': "", 'student_no': "", 'student_class': "", 'completed_modules': [False]*8,
        'current_module': 0, 'current_exercise': 0, 'total_score': 0, 'scored_exercises': set(),
        'db_module': 0, 'db_exercise': 0, 'is_logged_in': False, 'current_potential_score': 20,
        'fail_count': 0, 'feedback_msg': "", 'exercise_passed': False, 'pito_emotion': "merhaba"
    })

SINIFLAR = ["9-A", "9-B", "10-A", "10-B", "11-A", "11-B"]
RUTBELER = ["🥚 Yeni Başlayan", "🌱 Python Çırağı", "🪵 Kod Oduncusu", "🧱 Mantık Mimarı", "🌀 Döngü Ustası", "📋 Liste Uzmanı", "📦 Fonksiyon Kaptanı", "🤖 OOP Robotu", "🏆 Python Kahramanı"]

# --- MODERN UI CSS (BUTON İMHASI VE NEON) ---
st.markdown("""
    <style>
    header {visibility: hidden;}
    .main .block-container {padding-top: 1rem; background-color: #0f172a;}
    
    /* ACE EDITOR: APPLY BUTONUNU CSS İLE KÖKTEN SİL */
    [data-testid="stAceApplyButton"], .ace-apply-button, .ace_button, .ace_search { 
        display: none !important; visibility: hidden !important; height: 0 !important; 
    }
    iframe { border-radius: 15px !important; border: 2.5px solid #334155 !important; }

    /* ÜST KART VE NEON BAR */
    .user-header-box {
        background-color: #ffffff !important; border: 3.5px solid #3a7bd5 !important;
        border-radius: 20px !important; padding: 12px 25px !important; margin-bottom: 25px !important;
        display: flex !important; justify-content: space-between !important; align-items: center !important;
    }
    .info-label { color: #64748b !important; font-size: 0.8rem !important; font-weight: 800 !important; }
    .info-value { color: #1e293b !important; font-size: 1.15rem !important; font-weight: 900 !important; }
    .score-badge { background: linear-gradient(45deg, #3a7bd5, #00d2ff) !important; color: white !important; padding: 8px 22px !important; border-radius: 30px !important; font-weight: 900 !important; }
    .quest-container { background: #1e293b !important; border: 2.5px solid #3a7bd5 !important; border-radius: 25px !important; padding: 20px !important; margin-bottom: 30px !important; }
    .quest-bar { height: 26px !important; background: #0f172a !important; border-radius: 15px !important; margin: 15px 0 !important; overflow: hidden !important; border: 2px solid #334155 !important; }
    .quest-fill { height: 100% !important; background: linear-gradient(90deg, #3a7bd5, #00d2ff) !important; box-shadow: 0 0 20px rgba(0, 210, 255, 0.7) !important; transition: width 0.8s ease-in-out !important; }
    
    /* PITO BUBBLE */
    .pito-bubble { position: relative; background: #ffffff !important; border: 3.5px solid #3a7bd5 !important; border-radius: 30px !important; padding: 30px !important; color: #1e293b !important; font-weight: 500 !important; font-size: 1.2rem !important; line-height: 1.8 !important; text-align: left !important; }
    .pito-bubble::after { content: ''; position: absolute; left: -28px; top: 50px; border-width: 18px 28px 18px 0; border-style: solid; border-color: transparent #3a7bd5 transparent transparent; }
    
    .ranking-card { background-color: #ffffff !important; color: #1e293b !important; border-radius: 15px; padding: 12px; margin-bottom: 12px; border-left: 6px solid #3a7bd5 !important; }
    .stButton > button { border-radius: 18px; height: 4.2em; background: linear-gradient(45deg, #3a7bd5, #00d2ff) !important; color: white !important; font-weight: bold; border: none; font-size: 1.15rem; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. HIZLI ASSET YÜKLEME ---
@st.cache_resource
def load_asset_b64(name):
    p = Path(__file__).parent / "assets" / name
    return base64.b64encode(p.read_bytes()).decode() if p.exists() else None

def show_pito_gif(width=450):
    emotion_map = {"standart": "pito_dusunuyor.gif", "merhaba": "pito_merhaba.gif", "uzgun": "pito_hata.gif", "mutlu": "pito_basari.gif", "akademi": "pito_mezun.gif"}
    b64 = load_asset_b64(emotion_map.get(st.session_state.pito_emotion, "pito_dusunuyor.gif"))
    if b64: st.markdown(f'<div style="display: flex; justify-content: center;"><img src="data:image/gif;base64,{b64}" id="p{int(time.time()*100)}" width="{width}px" style="border-radius: 25px;"></div>', unsafe_allow_html=True)

# --- 4. VERİ TABANI ---
SHEET_URL = "https://docs.google.com/spreadsheets/d/1lat8rO2qm9QnzEUYlzC_fypG3cRkGlJfSfTtwNvs318/edit#gid=0"
conn = st.connection("gsheets", type=GSheetsConnection)

def get_db():
    try:
        df = conn.read(spreadsheet=SHEET_URL, ttl="1m")
        df.columns = df.columns.str.strip()
        df["Okul No"] = df["Okul No"].astype(str).str.split('.').str[0].str.strip()
        return df.dropna(subset=["Okul No"])
    except: return pd.DataFrame()

db_current = get_db()

def force_save():
    try:
        df_all = conn.read(spreadsheet=SHEET_URL, ttl=0)
        no = str(st.session_state.student_no).strip()
        df_clean = df_all[df_all["Okul No"].astype(str).str.split('.').str[0] != no]
        prog = ",".join(["1" if m else "0" for m in st.session_state.completed_modules])
        rank = RUTBELER[min(sum(st.session_state.completed_modules), 8)]
        new_row = pd.DataFrame([[no, st.session_state.student_name, st.session_state.student_class, int(st.session_state.total_score), rank, prog, int(st.session_state.db_module), int(st.session_state.db_exercise), datetime.now().strftime("%H:%M")]], columns=["Okul No", "Öğrencinin Adı", "Sınıf", "Puan", "Rütbe", "Tamamlanan Modüller", "Mevcut Modül", "Mevcut Egzersiz", "Tarih"])
        conn.update(spreadsheet=SHEET_URL, data=pd.concat([df_clean, new_row], ignore_index=True))
    except: pass

# --- 5. MUTLAK VE DERİN MÜFREDAT (40 ADIM) ---
training_data = [
    {"module_title": "1. İletişim: print() ve Metin Dünyası", "exercises": [
        {"msg": "**Pito'nun Notu:** Python'ın dünyayla konuştuğu tek kapı `print()` fonksiyonudur. Ekrana yazacağın metinleri (yazıları) mutlaka tırnak (' ') içine almalısın. Tırnaklar Python'a 'buradaki ifadeyi olduğu gibi yansıt' komutunu verir.\n\n**GÖREV:** Editor içine tam olarak **'Merhaba Pito'** metnini tırnaklar içerisinde yaz!", "task": "print('___')", "check": lambda c, o, i: "Merhaba Pito" in o, "solution": "print('Merhaba Pito')", "hint": "Metnin başına ve sonuna tek (') tırnak koy."},
        {"msg": "**Sayılar (Integers):** Sayılar tırnak gerektirmez. Eğer bir sayıya tırnak koyarsan Python onu sayı değil, bir 'yazı' olarak görür ve üzerinde matematik yapamaz.\n\n**GÖREV:** Boşluğa tırnak kullanmadan sadece **100** sayısını yaz.", "task": "print(___)", "check": lambda c, o, i: "100" in o, "solution": "print(100)", "hint": "Sayısal değerleri tırnaksız yazmalısın."},
        {"msg": "**Virgül Operatörü:** Virgül (`,`) farklı veri tiplerini aynı satırda birleştirir ve araya otomatik bir boşluk koyar. En profesyonel birleştirme yöntemidir.\n\n**GÖREV:** 'Puan:' metni ile **100** sayısını yan yana bas.", "task": "print('Puan:', ___)", "check": lambda c, o, i: "100" in o, "solution": "print('Puan:', 100)", "hint": "Virgülden sonra sadece 100 yaz."},
        {"msg": "**# Yorum Satırı:** Diyez işareti Python'a 'Bu satırı görmezden gel' demektir. Sadece biz yazılımcıların kod içine not alması içindir; çalışmayı asla etkilemez.\n\n**GÖREV:** Satırın en başına **#** işaretini koy.", "task": "___ bu bir nottur", "check": lambda c, o, i: "#" in c, "solution": "# bu bir nottur", "hint": "Diyez (#) işaretini en başa yerleştir."},
        {"msg": "**Newline:** `\\n` metni alt satıra fırlatır. Sanki Enter tuşuna basılmış gibi davranır.\n\n**GÖREV:** Tırnaklar içindeki boşluğa **\\n** yaz.", "task": "print('Üst' + '___' + 'Alt')", "check": lambda c, o, i: "Üst\nAlt" in o, "solution": "print('Üst\\nAlt')", "hint": "\\n yazmalısın."}
    ]},
    {"module_title": "2. Hafıza: Değişkenler ve input()", "exercises": [
        {"msg": "**Değişkenler:** RAM'deki isimlendirilmiş hafıza kutularıdır. `=` işareti bir 'atama operatörü'dür ve sağdaki değeri soldaki kutunun içine koyar.\n\n**GÖREV:** `yas` ismindeki kutuya sayısal olarak **15** değerini ata.", "task": "yas = ___", "check": lambda c, o, i: i.get('yas') == 15, "solution": "yas = 15", "hint": "Eşittir işaretinden sonra sadece 15 yaz."},
        {"msg": "**input():** Programı durdurur ve kullanıcıdan bilgi bekler. Python bu bilgiyi ne olursa olsun her zaman 'metin' (String) olarak algılar.\n\n**GÖREV:** Kullanıcıdan adını almak için boşluğa veri alma fonksiyonu olan **input** yaz.", "task": "ad = ___('Adın: ')", "check": lambda c, o, i: "input" in c, "solution": "ad = input('Adın: ')", "hint": "input kelimesini kullan."},
        {"msg": "**Casting:** Sayıları metne çevirmemiz gerektiğinde `str()` fonksiyonunu kullanırız. Bu, farklı tipleri birleştirirken hata almanı önler.", "task": "print(___(10))", "check": lambda c, o, i: "str" in c, "solution": "print(str(10))", "hint": "str(değişken) formunu kullan."},
        {"msg": "**int():** `input()` verisini matematiksel işleme sokmak için onu `int()` fonksiyonu ile 'tam sayıya' çevirmelisin.\n\n**GÖREV:** Dış boşluğa **int**, içe **input** yazarak sayı girişi alan sistemi kur.", "task": "n = ___(___('S: '))", "check": lambda c, o, i: "int" in c and "input" in c, "solution": "n = int(input('S: '))", "hint": "int(input()) yapısını kur."},
        {"msg": "**İsimlendirme:** Değişken isimlerinde rakamla başlamamaya ve boşluk kullanmamaya dikkat et! Python büyük-küçük harfe duyarlıdır.", "task": "isim = '___'", "check": lambda c, o, i: i.get('isim') == 'Pito', "solution": "isim = 'Pito'", "hint": "Metni tırnaklar içine Pito olarak yaz."}
    ]},
    {"module_title": "3. Mantık: Karar Yapıları", "exercises": [{"msg": "**==** Sorgusu:", "task": "if 10 ___ 10: pass", "check": lambda c,o,i: "==" in c, "solution": "if 10==10: pass", "hint": "=="} for _ in range(5)]},
    {"module_title": "4. Otomasyon: Döngüler", "exercises": [{"msg": "**range**:", "task": "for i in ___(5): pass", "check": lambda c,o,i: "range" in c, "solution": "range", "hint": "range"} for _ in range(5)]},
    {"module_title": "5. Gruplama: Listeler", "exercises": [{"msg": "**append**:", "task": "L.____(10)", "check": lambda c,o,i: "append" in c, "solution": "append", "hint": "append"} for _ in range(5)]},
    {"module_title": "6. Modülerlik: Fonksiyonlar", "exercises": [{"msg": "**def**:", "task": "___ f(): pass", "check": lambda c,o,i: "def" in c, "solution": "def", "hint": "def"} for _ in range(5)]},
    {"module_title": "7. Nesneler: OOP Dünyası", "exercises": [{"msg": "**class**:", "task": "___ Robot: pass", "check": lambda c,o,i: "class" in c, "solution": "class", "hint": "class"} for _ in range(5)]},
    {"module_title": "8. Kalıcılık: Dosya Yönetimi", "exercises": [{"msg": "**open**:", "task": "f = ___('a.txt','w')", "check": lambda c,o,i: "open" in c, "solution": "open", "hint": "open"} for _ in range(5)]}
]

# --- 6. LİDERLİK TABLOSU ---
col_main, col_stats = st.columns([3.2, 1])
with col_stats:
    st.markdown("### 🏆 Onur Kurulu")
    if not db_current.empty:
        df_l = db_current.copy()
        df_l["Puan"] = pd.to_numeric(df_l["Puan"], errors='coerce').fillna(0)
        top_c = df_l.groupby("Sınıf")["Puan"].sum().idxmax()
        st.markdown(f'<div style="background:linear-gradient(135deg,#FFD700,#F59E0B);color:black;border-radius:15px;padding:20px;text-align:center;font-weight:900;margin-bottom:25px;">👑 ŞAMPİYON SINIF: {top_c}</div>', unsafe_allow_html=True)
        t1, t2 = st.tabs(["👥 Sınıfım", "🌍 Okul"])
        with t1:
            if st.session_state.is_logged_in:
                my_c = df_l[df_l["Sınıf"] == st.session_state.student_class].sort_values(by="Puan", ascending=False).head(8)
                for _, r in my_c.iterrows(): st.markdown(f'<div class="ranking-card"><b>{r["Öğrencinin Adı"]}</b><br>{int(r["Puan"])} PT</div>', unsafe_allow_html=True)
        with t2:
            for _, r in df_l.sort_values(by="Puan", ascending=False).head(10).iterrows(): st.markdown(f'<div class="ranking-card"><b>{r["Öğrencinin Adı"]}</b> ({r["Sınıf"]})<br>{int(r["Puan"])} PT</div>', unsafe_allow_html=True)

# --- 7. PANEL VE AKIŞ ---
with col_main:
    if st.session_state.is_logged_in:
        st.markdown(f'<div class="user-header-box"><div><div class="info-label">AKADEMİ ÖĞRENCİSİ</div><div class="info-value">👤 {st.session_state.student_name} ({st.session_state.student_class})</div></div><div style="text-align:center;"><div class="info-label">RÜTBE</div><div class="info-value">{RUTBELER[min(sum(st.session_state.completed_modules), 8)]}</div></div><div style="text-align:right;"><div class="info-label">TOPLAM PUAN</div><div class="score-badge">⭐ {st.session_state.total_score}</div></div></div>', unsafe_allow_html=True)

    if not st.session_state.is_logged_in:
        c1, c2 = st.columns([1.6, 3.4])
        with c1: st.session_state.pito_emotion = "merhaba"; show_pito_gif(450)
        with c2:
            st.markdown('<div class="pito-bubble" style="margin-top: 60px;">Ben <b>Pito</b>. Python macerasına hazır mısın? Numaranı gir ve akademiye katıl!</div>', unsafe_allow_html=True)
            in_no = st.text_input("Okul Numaran:", placeholder="Numaranı buraya mühürle...").strip()
            if in_no and in_no.isdigit():
                user_data = db_current[db_current["Okul No"] == in_no] if not db_current.empty else pd.DataFrame()
                if not user_data.empty:
                    row = user_data.iloc[0]; st.info(f"🔍 **{row['Öğrencinin Adı']}**, Hoş geldin!")
                    if st.button("🚀 Devam Et"):
                        st.session_state.update({'student_no': in_no, 'student_name': row["Öğrencinin Adı"], 'student_class': row["Sınıf"], 'total_score': int(row["Puan"]), 'db_module': int(row['Mevcut Modül']), 'db_exercise': int(row['Mevcut Egzersiz']), 'current_module': min(int(row['Mevcut Modül']), 7), 'current_exercise': int(row['Mevcut Egzersiz']), 'completed_modules': [True if x == "1" else False for x in str(row["Tamamlanan Modüller"]).split(",")], 'is_logged_in': True, 'pito_emotion': 'standart'}); st.rerun()
                else:
                    in_name = st.text_input("Adın Soyadın:"); in_class = st.selectbox("Sınıfın:", SINIFLAR)
                    if st.button("✨ Kayıt Ol ve Başla") and in_name:
                        st.session_state.update({'student_no': in_no, 'student_name': in_name, 'student_class': in_class, 'is_logged_in': True}); force_save(); st.rerun()
        st.stop()

    if sum(st.session_state.completed_modules) >= 8:
        st.session_state.pito_emotion = "akademi"; show_pito_gif(550)
        st.markdown('<div class="pito-bubble" style="text-align:center;">🎊 <b>TEBRİKLER Python Kahramanı!</b></div>', unsafe_allow_html=True); st.balloons()
        if st.button("🔄 Eğitimi Tekrar Al"):
            st.session_state.update({'db_module': 0, 'db_exercise': 0, 'current_module': 0, 'current_exercise': 0, 'total_score': 0, 'completed_modules': [False]*8, 'scored_exercises': set(), 'pito_emotion': 'merhaba'}); force_save(); st.rerun()
        st.stop()

    # PROGRESS
    curr_idx = (st.session_state.current_module * 5) + (st.session_state.current_exercise + 1)
    perc = (curr_idx / 40) * 100
    st.markdown(f'''<div class="quest-container"><div class="quest-text" style="color:white;font-weight:800;">📍 {training_data[st.session_state.current_module]['module_title']} <span style="float:right;">🚀 %{int(perc)} TAMAMLANDI</span></div><div class="quest-bar"><div class="quest-fill" style="width: {perc}%;"></div></div></div>''', unsafe_allow_html=True)

    curr_ex = training_data[st.session_state.current_module]["exercises"][st.session_state.current_exercise]
    
    c_pito, c_bubble = st.columns([1.5, 3.5])
    with c_pito: show_pito_gif(450)
    with c_bubble:
        st.markdown(f'<div class="pito-bubble"><b>🗣️ Pito\'nun Notu:</b><br><br>{curr_ex["msg"]}</div>', unsafe_allow_html=True)
        st.markdown(f'''<div style="display:flex; gap:15px; margin-top:20px;"><div class="stat-card" style="background:white; padding:12px; border-radius:15px; flex:1; text-align:center; color:#1e293b;"><b>🐾 Adım: {st.session_state.current_exercise + 1}/5</b></div><div class="stat-card" style="background:white; padding:12px; border-radius:15px; flex:1; text-align:center; color:#ef4444;"><b>❌ Hatalar: {st.session_state.fail_count}/4</b></div></div>''', unsafe_allow_html=True)

    if st.session_state.feedback_msg:
        if "✅" in st.session_state.feedback_msg: st.success(st.session_state.feedback_msg)
        else: st.error(st.session_state.feedback_msg)

    # --- KOD KONTROL MERKEZİ (FORM TABANLI KESİN ÇÖZÜM) ---
    if not st.session_state.exercise_passed and st.session_state.fail_count < 4:
        with st.form(key=f"pito_form_{curr_idx}"):
            # Editör butona basılana kadar veriyi kilitlemez
            code = st_ace(value=curr_ex.get('task',''), language="python", theme="monokai", font_size=18, height=220, auto_update=False, key=f"ace_{curr_idx}")
            submit = st.form_submit_button("🔍 Kodumu Kontrol Et", use_container_width=True)
            
            if submit:
                # 1. Aşama: Boşluk Kontrolü (Hata Hakkı Gitmez)
                if "___" in code:
                    st.session_state.feedback_msg = "⚠️ Pito bekliyor: Boşluğu doldurmalısın!"
                    st.rerun()
                
                # 2. Aşama: Doğrulama
                old_stdout, new_stdout = sys.stdout, StringIO(); sys.stdout = new_stdout
                try:
                    mock_env = {"print": print, "input": lambda x: "10", "int": int, "str": str, "yas": 0, "isim": "", "L": [10,20], "t": (1,2), "d": {"ad": "Pito"}}
                    exec(code, mock_env); out = new_stdout.getvalue(); sys.stdout = old_stdout
                    
                    if curr_ex.get('check', lambda c,o,i: True)(code, out, mock_env):
                        # KESİN BAŞARI
                        st.session_state.update({'feedback_msg': "✅ Tebrikler! Harika bir iş çıkardın. Bir sonraki adıma geçebilirsin!", 'exercise_passed': True, 'pito_emotion': 'mutlu', 'fail_count': 0})
                        st.session_state.total_score += st.session_state.current_potential_score
                        force_save(); st.rerun()
                    else: raise Exception("LogicError")

                except:
                    # KESİN HATA
                    sys.stdout = old_stdout
                    st.session_state.fail_count += 1
                    st.session_state.current_potential_score = max(0, st.session_state.current_potential_score - 5)
                    st.session_state.pito_emotion = "uzgun"
                    msgs = {1: "❌ Bu ilk hatan lütfen daha dikkatli ol ve tekrar dene (kazanacağın puan -5 azaldı.)", 2: "❌ Bu 2. hatan lütfen daha dikkatli ol ve tekrar dene (kazanacağın puan -5 azaldı.)", 3: f"❌ Bu 3. hatan lütfen daha dikkatli ol ve tekrar dene (kazanacağın puan -5 azaldı.) \n\n💡 **İpucu:** {curr_ex['hint']}", 4: "🌿 Bu egzersizden puan alamadın ama üzülme aşağıda çözümü inceleyebilirsin."}
                    st.session_state.feedback_msg = msgs.get(st.session_state.fail_count, ""); st.rerun()

    # SONRAKİ ADIM BUTONU (SADECE BAŞARIDA VEYA 4. HATADA)
    if st.session_state.exercise_passed or st.session_state.fail_count >= 4:
        if st.session_state.fail_count >= 4 and not st.session_state.exercise_passed:
            st.markdown('<div style="background:#fef2f2; border:2px solid #ef4444; border-radius:15px; padding:15px; margin-bottom:15px; color:#1e293b;">🔍 **Pito\'nun Çözümü:**</div>', unsafe_allow_html=True)
            st.code(curr_ex['solution'], language="python")
        if st.button("➡️ Sonraki Adıma Geç", use_container_width=True):
            st.session_state.current_exercise += 1
            if st.session_state.current_exercise >= 5:
                st.session_state.current_module += 1; st.session_state.current_exercise = 0; st.session_state.db_module += 1; st.session_state.completed_modules[st.session_state.current_module-1] = True; force_save()
            st.session_state.update({'exercise_passed': False, 'fail_count': 0, 'current_potential_score': 20, 'feedback_msg': "", 'pito_emotion': 'standart'}); st.rerun()
