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

# --- 2. SESSION STATE (HATA ZIRHI - EN ÜSTTE) ---
if 'is_logged_in' not in st.session_state:
    for k, v in {
        'student_name': "", 'student_no': "", 'student_class': "", 'completed_modules': [False]*8, 
        'current_module': 0, 'current_exercise': 0, 'exercise_passed': False, 'total_score': 0, 
        'scored_exercises': set(), 'db_module': 0, 'db_exercise': 0, 'is_logged_in': False, 
        'current_potential_score': 20, 'fail_count': 0, 'feedback_msg': "", 'last_output': "", 
        'login_error': "", 'graduation_view': False
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
    .quest-bar { height: 14px; background: #e2e8f0; border-radius: 10px; margin: 10px 0; overflow: hidden; position: relative; }
    .quest-fill { height: 100%; background: linear-gradient(90deg, #3a7bd5, #00d2ff); transition: width 0.6s ease-in-out; }
    .pito-bubble {
        position: relative; background: #ffffff; border: 2px solid #3a7bd5;
        border-radius: 15px; padding: 25px; margin-bottom: 20px; color: #1e1e1e;
        font-weight: 500; font-size: 1.1rem; box-shadow: 4px 4px 15px rgba(0,0,0,0.05); line-height: 1.7;
    }
    .pito-bubble:after { content: ''; position: absolute; bottom: -20px; left: 40px; border-width: 20px 20px 0; border-style: solid; border-color: #3a7bd5 transparent; }
    .solution-guide { background-color: #fef2f2 !important; border: 2px solid #ef4444 !important; border-radius: 12px; padding: 20px; margin: 15px 0; color: #1e1e1e !important; }
    .hint-guide { background-color: #fffbeb !important; border: 2px solid #f59e0b !important; border-radius: 12px; padding: 20px; margin: 15px 0; color: #1e1e1e !important; }
    .leaderboard-card { background: linear-gradient(135deg, #1e1e1e, #2d2d2d); border: 1px solid #444; border-radius: 12px; padding: 10px; margin-bottom: 8px; color: white; }
    .stButton > button { width: 100%; border-radius: 12px; height: 3.5em; background: linear-gradient(45deg, #3a7bd5, #00d2ff) !important; color: white !important; font-weight: bold; border: none; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. VERİ TABANI VE LİDERLİK TABLOSU (MÜHÜRLÜ - EN ÜSTTE) ---
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
    except: return pd.DataFrame(columns=["Okul No", "Öğrencinin Adı", "Sınıf", "Puan", "Rütbe", "Tamamlanan Modüller", "Mevcut Modül", "Mevcut Egzersiz", "Tarih"])

db_current = get_db()

with st.sidebar:
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
            my_c = db_current[db_current["Sınıf"] == st.session_state.student_class].sort_values(by="Puan", ascending=False).head(5)
            for _, r in my_c.iterrows(): st.markdown(f'<div class="leaderboard-card"><b>{r["Rütbe"]} {r["Öğrencinin Adı"]}</b><br>{int(r["Puan"])} Puan</div>', unsafe_allow_html=True)
        else: st.caption("Giriş yapmalısın.")
    with tab_s:
        for _, r in db_current.sort_values(by="Puan", ascending=False).head(10).iterrows():
            st.markdown(f'<div class="leaderboard-card"><b>{r["Rütbe"]} {r["Öğrencinin Adı"]} ({r["Sınıf"]})</b><br>{int(r["Puan"])} Puan</div>', unsafe_allow_html=True)

def force_save():
    try:
        no = str(st.session_state.student_no).strip()
        df_all = get_db()
        df_clean = df_all[df_all["Okul No"] != no]
        prog = ",".join(["1" if m else "0" for m in st.session_state.completed_modules])
        rank = RUTBELER[min(sum(st.session_state.completed_modules), 8)]
        new_row = pd.DataFrame([[no, st.session_state.student_name, st.session_state.student_class, int(st.session_state.total_score), rank, prog, int(st.session_state.db_module), int(st.session_state.db_exercise), datetime.now().strftime("%H:%M:%S")]], columns=["Okul No", "Öğrencinin Adı", "Sınıf", "Puan", "Rütbe", "Tamamlanan Modüller", "Mevcut Modül", "Mevcut Egzersiz", "Tarih"])
        conn.update(spreadsheet=SHEET_URL, data=pd.concat([df_clean, new_row], ignore_index=True))
    except: pass

def show_pito_img(width=180):
    if os.path.exists("assets/pito.png"): st.image("assets/pito.png", width=width)
    else: st.image("https://img.icons8.com/fluency/180/robot-viewer.png", width=width)

# --- 4. GİRİŞ EKRANI ---
col_app, _ = st.columns([3, 0.01])
with col_app:
    if not st.session_state.is_logged_in:
        _, col_mid, _ = st.columns([1, 4, 1])
        with col_mid:
            st.markdown('<div class="pito-bubble">Merhaba! Ben <b>Pito</b>. Nusaybin laboratuvarında Python dünyasına adım atmaya hazır mısın?</div>', unsafe_allow_html=True)
            show_pito_img(180)
            in_no = st.text_input("Okul Numaran:", key="login_f").strip()
            if in_no:
                if not in_no.isdigit(): st.error("⚠️ Sadece rakam giriniz!")
                else:
                    user_data = db_current[db_current["Okul No"] == in_no]
                    if not user_data.empty:
                        row = user_data.iloc[0]
                        st.warning(f"🔍 **{row['Öğrencinin Adı']}** ({row['Sınıf']}), bu sen misin?")
                        if st.button("✅ Evet, Benim"):
                            m_v = int(row['Mevcut Modül'])
                            st.session_state.update({'student_no': in_no, 'student_name': row["Öğrencinin Adı"], 'student_class': row["Sınıf"], 'total_score': int(row["Puan"]), 'db_module': m_v, 'db_exercise': int(row['Mevcut Egzersiz']), 'current_module': min(m_v, 7), 'current_exercise': int(row['Mevcut Egzersiz']), 'completed_modules': [True if x == "1" else False for x in str(row["Tamamlanan Modüller"]).split(",")], 'is_logged_in': True, 'graduation_view': (m_v >= 8)})
                            st.rerun()
                    else:
                        st.info("🌟 Seni henüz tanımıyorum. Python macerasına katılmak için kendini tanıtmalısın.")
                        in_name = st.text_input("Adın Soyadın:")
                        in_class = st.selectbox("Sınıfın:", SINIFLAR)
                        if st.button("✨ Kayıt Ol ve Başla"):
                            if in_name:
                                st.session_state.update({'student_no': in_no, 'student_name': in_name, 'student_class': in_class, 'is_logged_in': True})
                                force_save(); st.rerun()
        st.stop()

    # MEZUNİYET EKRANI (RESTART FIX)
    if st.session_state.graduation_view:
        st.markdown('<div class="pito-bubble">🎊 <b>TEBRİKLER Python Kahramanı!</b> Nusaybin laboratuvarının en başarılı yazılımcısı oldun!</div>', unsafe_allow_html=True)
        st.snow()
        show_pito_img(250)
        st.success(f"Tüm akademiyi başarıyla tamamladın. Toplam Puanın: {st.session_state.total_score}")
        c1, c2 = st.columns(2)
        with c1:
            if st.button("🔄 Eğitimi Tekrar Al (Puan Sıfırlanır)"):
                # TÜM VERİYİ SIFIRLIYORUZ (DB_MODULE DAHİL)
                st.session_state.update({
                    'db_module': 0, 'db_exercise': 0, 'current_module': 0, 
                    'current_exercise': 0, 'total_score': 0, 'completed_modules': [False]*8, 
                    'graduation_view': False, 'scored_exercises': set(), 'exercise_passed': False
                })
                force_save() # Sıfırlama bilgisini DB'ye mühürle
                st.rerun()
        with c2:
            if st.button("🔒 İnceleme Moduna Geç"):
                st.session_state.update({'current_module': 0, 'current_exercise': 0, 'graduation_view': False})
                st.rerun()
        st.stop()

    # --- 5. EKSİKSİZ VE BOL AÇIKLAMALI PEDAGOJİK MÜFREDAT (40 ADIM) ---
    training_data = [
        {"module_title": "1. print() ve Metin Dünyası", "exercises": [
            {"msg": "**Pito'nun Notu:** Python'ın dünyayla konuşma yolu `print()` fonksiyonudur. Ekrana yazacağın metinleri mutlaka tırnak (' ') içine almalısın. Tırnaklar Python'a 'buradaki ifadeyi olduğu gibi yansıt' komutunu verir.\n\n**GÖREV:** Editor içindeki boşluğa tam olarak **'Merhaba Pito'** metnini tırnaklar içerisinde yaz ve kontrol et!", "task": "print('___')", "check": lambda c, o, i: "Merhaba Pito" in o, "solution": "print('Merhaba Pito')", "hint": "Metnin hem başına hem sonuna tek (') veya çift (\") tırnak koyduğundan emin ol."},
            {"msg": "**Pito'nun Notu:** Sayılar (Integer), metinlerden farklıdır; tırnak gerektirmezler. Eğer tırnak koyarsan Python onu sayı değil, bir metin olarak görür ve üzerinde matematiksel işlemler yapamaz.\n\n**GÖREV:** Boşluğa tırnak kullanmadan sadece **100** sayısını yaz. Bu sayede Python onun bir sayı olduğunu anlayacak ve ileride onunla matematiksel toplama yapabileceksin.", "task": "print(___)", "check": lambda c, o, i: "100" in o, "solution": "print(100)", "hint": "Rakamları tırnaksız yazmalısın. Eğer '100' yazarsan bu bir metin olur!"},
            {"msg": "**Pito'nun Notu:** Virgül (`,`) farklı veri tiplerini (örneğin bir metin ve bir sayı) aynı satırda birleştirir ve araya otomatik bir boşluk koyar. Bu, değişkenleri ve mesajları birleştirmek için en profesyonel yoldur.\n\n**GÖREV:** 'Puan:' metni ile **100** sayısını yan yana basmak için virgülden sonraki boşluğa sadece **100** yaz.", "task": "print('Puan:', ___)", "check": lambda c, o, i: "100" in o, "solution": "print('Puan:', 100)", "hint": "Virgülden sonra sadece sayısal değeri yazmalısın."},
            {"msg": "**Pito'nun Notu:** `#` işareti Python'a 'Bu satırı görmezden gel' demektir. Buna 'Yorum Satırı' diyoruz. Sadece biz yazılımcıların not alması içindir; kodun çalışmasını etkilemez.\n\n**GÖREV:** Satırın en başına **#** işaretini koyarak bu satırı etkisiz bir nota dönüştür.", "task": "___ bu bir nottur", "check": lambda c, o, i: "#" in c, "solution": "# bu bir nottur", "hint": "Klavyeden diyez (#) işaretini satırın en başına yerleştir."},
            {"msg": "**Pito'nun Notu:** `\\n` (new line) kaçış karakteri metni alt satıra böler. Sanki klavyede 'Enter' tuşuna basılmış gibi davranır.\n\n**GÖREV:** 'Üst' ve 'Alt' kelimelerini alt alta getirmek için tırnaklar içindeki boşluğa **\\n** yaz.", "task": "print('Üst' + '___' + 'Alt')", "check": lambda c, o, i: "Üst\nAlt" in o, "solution": "print('Üst\\nAlt')", "hint": "Tırnaklar içerisine ters eğik çizgi (\\) ve n harfini birleşik yaz: \\n"}
        ]},
        {"module_title": "2. Hafıza: Değişkenler ve Atama", "exercises": [
            {"msg": "**Pito'nun Notu:** Değişkenler bellekteki (RAM) isimlendirilmiş kutulardır. `=` işareti bir 'atama operatörü'dür ve sağdaki değeri soldaki kutunun içine koyar.\n\n**GÖREV:** `yas` ismindeki hafıza kutusuna sayısal olarak **15** değerini ata ve Python'ın onu saklamasını sağla.", "task": "yas = ___", "check": lambda c, o, i: "15" in c, "solution": "yas = 15", "hint": "Eşittir işaretinden sonra sadece değeri (15) yazmalısın."},
            {"msg": "**Pito'nun Notu:** Metin (String) verilerini saklarken tırnak şarttır. İsimlerde boşluk kullanamazsın ve rakamla başlayamazsın.\n\n**GÖREV:** `isim` değişkenine **'Pito'** metnini ata. Metni tırnak içinde yazmayı unutma!", "task": "isim = '___'", "check": lambda c, o, i: "Pito" in o, "solution": "isim = 'Pito'", "hint": "Metni tırnaklar içerisine tam olarak Pito şeklinde yaz."},
            {"msg": "**Pito'nun Notu:** `input()` programı durdurur ve kullanıcıdan bir bilgi bekler. Python bu bilgiyi her zaman 'metin' (String) olarak belleğe kaydeder.\n\n**GÖREV:** Kullanıcıdan adını almak için boşluğa veri alma fonksiyonu olan **input** yaz.", "task": "ad = ___('Adın: ')", "check": lambda c, o, i: "input" in c, "solution": "ad = input('Adın: ')", "hint": "Veri alma komutu olan input kelimesini kullan."},
            {"msg": "**Pito'nun Notu:** Sayıları metne çevirmemiz gerektiğinde (Buna 'Casting' diyoruz) `str()` fonksiyonunu kullanırız. Bu, metinleri birleştirirken hayati önem taşır.\n\n**GÖREV:** 10 sayısını metne çeviren **str** fonksiyonunu boşluğa yerleştir.", "task": "print(___(10))", "check": lambda c, o, i: "str" in c, "solution": "print(str(10))", "hint": "String'in kısaltması olan str fonksiyonunu yerleştir."},
            {"msg": "**Pito'nun Notu:** Matematik yapabilmek için `input()` ile gelen metni `int()` fonksiyonu ile 'tam sayıya' çevirmelisin. Buna tip dönüşümü denir.\n\n**GÖREV:** Dış boşluğa **int**, içe **input** yazarak kullanıcıdan sayı girişi alan sistemi kur.", "task": "n = ___(___('S: '))", "check": lambda c, o, i: "int" in c and "input" in c, "solution": "n = int(input('S: '))", "hint": "Fonksiyonları iç içe kullanmalısın: int(input())"}
        ]},
        {"module_title": "3. Karar Yapıları: If-Else Mantığı", "exercises": [
            {"msg": "**Pito'un Notu:** Programların karar verme yeteneği `if` bloğuyla başlar. Koşul doğruysa kod içeri girer. Eşitlik sorgusunda tek eşittir atama yapar, karşılaştırma için mutlaka `==` (çift eşittir) kullanmalısın.\n\n**GÖREV:** Sayı 10'a eşitse kontrolü için boşluğa çift eşittir (**==**) operatörünü koy.", "task": "if 10 ___ 10: print('OK')", "check": lambda c, o, i: "==" in c, "solution": "if 10 == 10:\n    print('OK')", "hint": "Mantıksal karşılaştırma için == koy."},
            {"msg": "**Pito'un Notu:** `else:` bloğu, 'if' şartı sağlanmadığında devreye giren son çaredir. Python'da 'değilse' anlamına gelir.\n\n**GÖREV:** Şart sağlanmazsa 'Hata' yazdıran yolu tamamla. Boşluğa **else** yaz.", "task": "if 5 > 10: pass\n___: print('Hata')", "check": lambda c, o, i: "else" in c, "solution": "if 5 > 10: pass\nelse:\n    print('Hata')", "hint": "else: yazman yeterli."},
            {"msg": "**Pito'un Notu:** Birden fazla şartı sırayla denetlemek için `elif` kullanılır. Şartlar yukarıdan aşağıya okunur, biri doğruysa diğerlerine bakılmaz.\n\n**GÖREV:** Puan 50'den büyükse kontrolü için boşluğa **elif** anahtarını yaz.", "task": "p = 60\nif p < 50: pass\n___ p > 50: print('Geçti')", "check": lambda c, o, i: "elif" in c, "solution": "if p < 50: pass\nelif p > 50:\n    print('Geçti')", "hint": "İkinci bir şart kontrolü için elif komutunu kullan."},
            {"msg": "**Pito'un Notu:** `and` (ve) bağlacı, her iki tarafındaki şartın da doğru olmasını bekler. İki şarttan biri yanlışsa tüm blok iptal olur.\n\n**GÖREV:** İki tarafın da doğru olduğunu kontrol eden bağlacı (**and**) boşluğa yaz.", "task": "if 1 == 1 ___ 2 == 2: print('OK')", "check": lambda c, o, i: "and" in c, "solution": "if 1 == 1 and 2 == 2:\n    print('OK')", "hint": "and anahtarını yerleştir."},
            {"msg": "**Pito'un Notu:** `!=` operatörü 'eşit değilse' anlamına gelir. Şartın gerçekleşmediği durumları denetlemek için kullanılır.\n\n**GÖREV:** Sayı 0'a eşit değilse 'Var' yazdıran operatörü (**!=**) boşluğa koy.", "task": "s = 5\nif s ___ 0: print('Var')", "check": lambda c, o, i: "!=" in c, "solution": "if s != 0:\n    print('Var')", "hint": "!= kullan."}
        ]},
        {"module_title": "4. Otomasyon: For ve While Döngüleri", "exercises": [
            {"msg": "**Pito'un Notu:** `range(5)` komutu 0'dan 4'e kadar 5 adet sayı üretir. `for` döngüsü bu sayılar üzerinde adım adım ilerleyerek işlemleri tekrarlar.\n\n**GÖREV:** Döngüyü 5 kez döndürmek için boşluğa sayı üretici olan **range** yaz.", "task": "for i in ___(5): print(i)", "check": lambda c, o, i: "range" in c, "solution": "for i in range(5):\n    print(i)", "hint": "range yaz."},
            {"msg": "**Pito'un Notu:** `while` döngüsü bir şart 'True' olduğu sürece çalışmaya devam eder. Döngünün içinde şartı bozacak bir işlem yapmalısın yoksa sonsuz döngü oluşur.\n\n**GÖREV:** i sıfır olduğu sürece dönen döngüyü başlatmak için boşluğa **while** yaz.", "task": "i = 0\n___ i == 0: print('Dönüyor'); i += 1", "check": lambda c, o, i: "while" in c, "solution": "i = 0\nwhile i == 0:\n    print('Dönüyor')\n    i += 1", "hint": "while yaz."},
            {"msg": "**Pito'un Notu:** `break` komutu döngünün 'acil çıkış' kapısıdır. Şart sağlandığı an döngüyü tamamen sonlandırır ve bir sonraki kod satırına geçer.\n\n**GÖREV:** i değeri 1 olduğunda döngüyü bitiren **break** komutunu boşluğa yaz.", "task": "for i in range(5):\n if i == 1: ___", "check": lambda c, o, i: "break" in c, "solution": "for i in range(5):\n    if i == 1: break\n    print(i)", "hint": "break kullan."},
            {"msg": "**Pito'un Notu:** `continue` ise o anki adımı 'pas geçer' ve döngünün en başına geri döner. Altındaki kodları o tur için okumaz.\n\n**GÖREV:** 1 değerini atlayıp devam etmek için boşluğa **continue** yaz.", "task": "for i in range(3):\n if i == 1: ___", "check": lambda c, o, i: "continue" in c, "solution": "for i in range(3):\n    if i == 1: continue\n    print(i)", "hint": "continue yaz."},
            {"msg": "**Pito'un Notu:** Listelerde gezinmek için `in` anahtar kelimesini kullanırız. Bu, her bir elemanı sırayla değişkenimize atar.\n\n**GÖREV:** Listedeki her harfi çekmek için boşluğa aitlik bildiren **in** anahtarını yaz.", "task": "for x ___ ['A', 'B']: print(x)", "check": lambda c, o, i: "in" in c, "solution": "for x in ['A', 'B']:\n    print(x)", "hint": "in anahtarını koy."}
        ]},
        {"module_title": "5. Gruplama: Listeler (Veri Sepeti)", "exercises": [
            {"msg": "**Pito'un Notu:** Listeler birden fazla veriyi tek kutuda tutar ve `[]` ile tanımlanır. Python'da saymaya her zaman 0'dan başlarız!\n\n**GÖREV:** Boşluğa sayısal olarak **10** değerini koyarak listeyi tamamla.", "task": "L = [___, 20]", "check": lambda c, o, i: "10" in c, "solution": "L = [10, 20]", "hint": "10 yaz."},
            {"msg": "**Pito'un Notu:** Python'da saymaya her zaman 0'dan başlarız. Listenin ilk elemanına `[0]` indeksiyle ulaşılır. Bu kurala 'İndisleme' denir.\n\n**GÖREV:** İlk elemana (50) ulaşmak için boşluğa başlangıç indisi olan **0** yaz.", "task": "L = [50, 60]\nprint(L[___])", "check": lambda c, o, i: "50" in o, "solution": "L = [50, 60]\nprint(L[0])", "hint": "0 yaz."},
            {"msg": "**Pito'un Notu:** `.append()` metodu listenin sonuna yeni bir eleman ekler. Bu sayede listeyi dinamik olarak büyütebilirsin.\n\n**GÖREV:** Listeye 30 ekleyen ekleme metodu **append** kelimesini boşluğa yaz.", "task": "L = [10]\nL.___ (30)", "check": lambda c, o, i: "append" in c, "solution": "L = [10]\nL.append(30)", "hint": "append kullan."},
            {"msg": "**Pito'un Notu:** `len()` fonksiyonu 'length' (uzunluk) kelimesinden gelir ve listenin içindeki toplam eleman sayısını verir.\n\n**GÖREV:** Boşluğa **len** yazarak listenin boyutunu ölç ve ekrana basılmasını sağla.", "task": "L = [1, 2, 3]\nprint(___(L))", "check": lambda c, o, i: "3" in o, "solution": "L = [1, 2, 3]\nprint(len(L))", "hint": "len yaz."},
            {"msg": "**Pito'un Notu:** `.pop()` metodu listenin en sonundaki elemanı sepetten çıkarır. Bir nevi silme işlemi yapar.\n\n**GÖREV:** Son elemanı silen çıkarma metodu **pop** kelimesini boşluğa yerleştir.", "task": "L = [1, 2]\nL.___()", "check": lambda c, o, i: "pop" in c, "solution": "L = [1, 2]\nL.pop()", "hint": "pop yazmalısın."}
        ]},
        {"module_title": "6. Modülerlik: Fonksiyonlar ve Sözlükler", "exercises": [
            {"msg": "**Pito'un Notu:** Fonksiyonlar tekrar eden kodları paketler. `def` (tanımla) kelimesi ile bir iş paketini mühürleriz.\n\n**GÖREV:** 'pito' fonksiyonunu tanımlayan **def** anahtar kelimesini boşluğa yaz.", "task": "___ pito(): print('Hi')", "check": lambda c, o, i: "def" in c, "solution": "def pito():\n    print('Hi')", "hint": "def yaz."},
            {"msg": "**Pito'un Notu:** **Sözlükler (Dictionary)**, `{anahtar: değer}` çiftleriyle çalışır. Tıpkı rehberdeki isim ve ona bağlı telefon numarası gibi.\n\n**GÖREV:** 'ad' anahtarına karşılık gelen değer boşluğuna **'Pito'** yaz.", "task": "d = {'ad': '___'}", "check": lambda c, o, i: "Pito" in o, "solution": "d = {'ad': 'Pito'}", "hint": "Pito yaz."},
            {"msg": "**Pito'un Notu:** **Tuple (Demet)**, listeye benzer ama parantez `()` ile kurulur ve içeriği asla değiştirilemez.\n\n**GÖREV:** Boşluğa sayısal olarak **1** yazarak demeti tamamla.", "task": "t = (___, 2)", "check": lambda c, o, i: "1" in c, "solution": "t = (1, 2)", "hint": "1 yaz."},
            {"msg": "**Pito'un Notu:** `.keys()` metodu sözlükteki tüm etiketleri (anahtarları) bir liste halinde bize sunar.\n\n**GÖREV:** Boşluğa **keys** yazarak sözlükteki anahtar isimlerini çek.", "task": "d = {'a':1}\nprint(d.___())", "check": lambda c, o, i: "keys" in c, "solution": "d = {'a':1}\nprint(d.keys())", "hint": "keys yaz."},
            {"msg": "**Pito'un Notu:** `return` ifadesi fonksiyonun ürettiği sonucu dışarıya 'fırlatır'. Bu değer bir değişkene kaydedilebilir.\n\n**GÖREV:** 5 sonucunu döndüren fonksiyon için boşluğa **return** yaz.", "task": "def f(): ___ 5", "check": lambda c, o, i: "return" in c, "solution": "def f():\n    return 5", "hint": "return kullan."}
        ]},
        {"module_title": "7. OOP: Nesne Tabanlı Dünya", "exercises": [
            {"msg": "**Pito'un Notu:** `class` (Sınıf) bir taslaktır. Ondan kopyalar yani 'Nesneler' (Object) üretiriz. Sınıf bir fabrikadır, nesne üründür.\n\n**GÖREV:** 'Robot' isminde bir kalıp oluşturmak için boşluğa **class** yaz.", "task": "___ Robot: pass", "check": lambda c, o, i: "class" in c, "solution": "class Robot:\n    pass", "hint": "class yaz."},
            {"msg": "**Pito'un Notu:** Kalıptan nesne üretmek için sınıf ismini parantezlerle `()` çağırırız. Buna 'Instance' (Örnek) denir.\n\n**GÖREV:** Robot kalıbından r isminde bir nesne üretmek için boşluğa **Robot()** yaz.", "task": "class Robot: pass\nr = ___", "check": lambda c, o, i: "Robot()" in c, "solution": "class Robot: pass\nr = Robot()", "hint": "Robot() yaz."},
            {"msg": "**Pito'un Notu:** Nesnelerin özellikleri nokta (`.`) yardımıyla atanır. Bu nesnenin rengi, hızı gibi kimlik bilgileridir.\n\n**GÖREV:** r nesnesinin **renk** özelliğini 'Mavi' yapmak için boşluğa **renk** yaz.", "task": "class R: pass\nr = R()\nr.___ = 'Mavi'", "check": lambda c, o, i: "renk" in c, "solution": "class R: pass\nr = R()\nr.renk = 'Mavi'", "hint": "renk yaz."},
            {"msg": "**Pito'un Notu:** `self` nesnenin kendisini temsil eden bir parametredir. Sınıf içindeki metotlarda ilk sırada mutlaka olmalıdır.\n\n**GÖREV:** Metot parantezi içine nesnenin kendisini temsil eden **self** anahtarını yaz.", "task": "class R:\n def ses(___): print('B')", "check": lambda c, o, i: "self" in c, "solution": "class R:\n    def ses(self):\n        print('B')", "hint": "self yaz."},
            {"msg": "**Pito'un Notu:** Nesnenin bir eylemini (Metot) çalıştırmak için nesne isminden sonra nokta koyup metod ismini yazarız.\n\n**GÖREV:** r nesnesinin s() metodunu çalıştırmak için boşluğa **s()** yaz.", "task": "class R:\n def s(self): pass\nr = R()\nr.___()", "check": lambda c, o, i: "s()" in c, "solution": "class R:\n    def s(self):\n        pass\nr = R()\nr.s()", "hint": "s() yaz."}
        ]},
        {"module_title": "8. Kalıcılık: Dosya Yönetimi", "exercises": [
            {"msg": "**Pito'un Notu:** Bilgileri saklamak için `open()` fonksiyonu kullanılır. **'w'** (write) modu dosyaya veri yazmak içindir.\n\n**GÖREV:** n.txt dosyasını yazma modunda açmak için boşluklara **open** ve **w** yaz.", "task": "f = ___('n.txt', '___')", "check": lambda c, o, i: "open" in c and "w" in c, "solution": "f = open('n.txt', 'w')", "hint": "open ve w yaz."},
            {"msg": "**Pito'un Notu:** `.write()` metodu veriyi dosyanın içine kalıcı olarak mühürler. Önceki içeriği tamamen siler.\n\n**GÖREV:** Dosyaya 'X' harfini yazmak için boşluğa **write** metodunu yaz.", "task": "f = open('t.txt', 'w')\nf.___('X')\nf.close()", "check": lambda c, o, i: "write" in c, "solution": "f = open('t.txt', 'w')\nf.write('X')\nf.close()", "hint": "write yaz."},
            {"msg": "**Pito'un Notu:** Okumak için **'r'** (read) modu kullanılır. Bu mod dosyayı sadece görmemizi sağlar, değiştiremez.\n\n**GÖREV:** Dosyayı sadece okuma modunda açmak için boşluğa **r** harfini koy.", "task": "f = open('t.txt', '___')", "check": lambda c, o, i: "r" in c, "solution": "f = open('t.txt', 'r')", "hint": "r harfini koy."},
            {"msg": "**Pito'un Notu:** `.read()` metodu dosyanın tüm içeriğini bir metin olarak belleğe getirir.\n\n**GÖREV:** İçeriği ekrana basmak için boşluğa **read** metodunu yaz.", "task": "f = open('t.txt', 'r')\nprint(f.___())", "check": lambda c, o, i: "read" in c, "solution": "f = open('t.txt', 'r')\nprint(f.read())", "hint": "read yaz."},
            {"msg": "**Pito'un Notu:** `.close()` hayati önem taşır; dosyayı mutlaka kapatmalısın yoksa veri kaybı olabilir.\n\n**GÖREV:** Dosyayı kapatmak için boşluğa mühürleme komutu olan **close** yaz.", "task": "f = open('t.txt', 'r')\nf.___()", "check": lambda c, o, i: "close" in c, "solution": "f = open('t.txt', 'r')\nf.close()", "hint": "close kullan."}
        ]}
    ]

    # --- QUEST BAR ---
    total_steps = 40
    curr_t_idx = (st.session_state.current_module * 5) + (st.session_state.current_exercise + 1)
    progress_perc = (curr_t_idx / total_steps) * 100
    st.markdown(f"""<div class="quest-container"><div style="display: flex; justify-content: space-between; font-weight: bold; color: #3a7bd5; margin-bottom: 5px;"><span>📍 {training_data[st.session_state.current_module]['module_title']}</span><span>🐍 %{int(progress_perc)} İlerleme</span><span>🏆 {RUTBELER[min(sum(st.session_state.completed_modules), 8)]}</span></div><div class="quest-bar"><div class="quest-fill" style="width: {progress_perc}%;"></div></div></div>""", unsafe_allow_html=True)

    # --- ANA ARAYÜZ ---
    module_labels = [f"{'✅' if i < st.session_state.db_module else '📖'} Modül {i+1}" for i in range(min(st.session_state.db_module + 1, 8))]
    sel_mod_label = st.selectbox("Seviye Seç:", module_labels, index=min(st.session_state.current_module, len(module_labels)-1))
    new_m_idx = module_labels.index(sel_mod_label)
    if new_m_idx != st.session_state.current_module:
        st.session_state.update({'current_module': new_m_idx, 'current_exercise': 0, 'fail_count': 0, 'exercise_passed': False, 'current_potential_score': 20, 'feedback_msg': "", 'last_output': ""}); st.rerun()

    st.divider()
    curr_ex = training_data[st.session_state.current_module]["exercises"][st.session_state.current_exercise]
    is_review_mode = (st.session_state.current_module < st.session_state.db_module)

    c_box_i, c_box_m = st.columns([1, 4])
    with c_box_i: show_pito_img(140)
    with c_box_m:
        st.info(f"##### 🗣️ Pito'nun Notu:\n{curr_ex['msg']}")
        st.caption(f"Adım: {st.session_state.current_exercise + 1}/5 | {'🔒 İnceleme' if is_review_mode else f'🎁 Potansiyel: {st.session_state.current_potential_score} | ❌ Hata: {st.session_state.fail_count}/4'}")

    # --- FEEDBACK VE ÇÖZÜM BLOĞU (MÜHÜRLÜ) ---
    if st.session_state.feedback_msg:
        if "✅" in st.session_state.feedback_msg: st.success(st.session_state.feedback_msg)
        else: st.error(st.session_state.feedback_msg)

    if not st.session_state.exercise_passed and st.session_state.fail_count == 3:
        st.markdown(f'<div class="hint-guide"><div class="hint-header">💡 Pito\'dan Destek: İpucu</div>{curr_ex["hint"]}</div>', unsafe_allow_html=True)
    
    if st.session_state.fail_count >= 4 or is_review_mode:
        st.markdown('<div class="solution-guide"><div class="solution-header">🔍 Doğru Çözüm Yolu (Tam Kod)</div></div>', unsafe_allow_html=True)
        st.code(curr_ex['solution'], language="python")

    # KOD PANELİ
    if not is_review_mode and st.session_state.fail_count < 4 and not st.session_state.exercise_passed:
        code = st_ace(value=curr_ex['task'], language="python", theme="dracula", font_size=14, height=180, key=f"ace_{st.session_state.current_module}_{st.session_state.current_exercise}", auto_update=True)
        if st.button("🔍 Kodumu Kontrol Et", use_container_width=True):
            if "___" in code: st.session_state.feedback_msg = "⚠️ Pito bekliyor: Lütfen önce boşluğu doldur!"; st.rerun()
            else:
                old_stdout, new_stdout = sys.stdout, StringIO(); sys.stdout = new_stdout
                try:
                    mock_env = {"print": print, "input": lambda x: "10", "int": int, "str": str, "len": len, "open": open, "range": range, "s": 10, "L": [10, 20], "d":{'ad':'Pito'}, "t":(1,2), "Robot": lambda: None, "R": lambda: None, "yas": 15, "isim": "Pito", "ad": "Pito"}
                    exec(code, mock_env); out = new_stdout.getvalue(); sys.stdout = old_stdout
                    if curr_ex.get('check', lambda c, o, i: True)(code, out, ""):
                        st.session_state.update({'feedback_msg': "✅ Muhteşem! Başarıyla tamamladın.", 'last_output': out, 'exercise_passed': True})
                        ex_key = f"{st.session_state.current_module}_{st.session_state.current_exercise}"
                        if ex_key not in st.session_state.scored_exercises: st.session_state.total_score += st.session_state.current_potential_score; st.session_state.scored_exercises.add(ex_key); force_save()
                    else: raise Exception()
                except:
                    sys.stdout = old_stdout; st.session_state.fail_count += 1
                    st.session_state.current_potential_score = max(0, st.session_state.current_potential_score - 5)
                    if st.session_state.fail_count < 4:
                        st.session_state.feedback_msg = f"❌ 5 Puan Kaybettin! Kalan Ödül: {st.session_state.current_potential_score} Puan. Tekrar dene!"
                    else:
                        st.session_state.feedback_msg = "🌿 Bu seferlik puan kazanamadın ama tecrübe kazandın! Doğru çözümü yukarıdan inceleyip bir sonraki adıma geçelim."
                st.rerun()

    # --- NAVİGASYON ---
    if st.session_state.exercise_passed or is_review_mode or st.session_state.fail_count >= 4:
        cp, cn = st.columns(2)
        with cp:
            if st.session_state.current_exercise > 0:
                if st.button("⬅️ Önceki Adım"): st.session_state.update({'current_exercise': st.session_state.current_exercise - 1, 'exercise_passed': False, 'fail_count': 0, 'current_potential_score': 20, 'feedback_msg': "", 'last_output': ""}); st.rerun()
        with cn:
            if st.session_state.current_exercise < 4:
                if st.button("➡️ Sonraki Adım"): st.session_state.update({'current_exercise': st.session_state.current_exercise + 1, 'exercise_passed': False, 'fail_count': 0, 'current_potential_score': 20, 'feedback_msg': "", 'last_output': ""}); st.rerun()
            elif st.session_state.current_module < 7:
                if st.button("🏆 Modülü Bitir ve Devam Et"):
                    st.balloons()
                    if not is_review_mode:
                        st.session_state.db_module += 1; st.session_state.db_exercise = 0; st.session_state.completed_modules[st.session_state.current_module] = True; force_save()
                    st.session_state.update({'current_module': st.session_state.current_module + 1, 'current_exercise': 0, 'exercise_passed': False, 'fail_count': 0, 'current_potential_score': 20, 'feedback_msg': ""}); st.rerun()
            elif st.session_state.current_module == 7:
                if st.button("🏁 Akademiyi Tamamla"):
                    st.session_state.completed_modules[7] = True; st.session_state.db_module = 8; force_save(); st.session_state.graduation_view = True; st.rerun()