import streamlit as st
from streamlit_ace import st_ace
import sys
from io import StringIO
import pandas as pd
from datetime import datetime
from streamlit_gsheets import GSheetsConnection
import os

# --- 1. SAYFA VE TASARIM AYARLARI ---
st.set_page_config(layout="wide", page_title="Pito Akademi", initial_sidebar_state="collapsed")

# Okulunuzdaki sınıflar
SINIFLAR = ["9-A", "9-B", "10-A", "10-B", "11-A", "11-B"]

st.markdown("""
    <style>
    .pito-bubble {
        position: relative; background: #f0f2f6; border: 2px solid #3a7bd5;
        border-radius: 15px; padding: 20px; margin-bottom: 25px;
        color: #1e1e1e; font-size: 1.1rem; font-weight: 500;
        box-shadow: 4px 4px 10px rgba(0,0,0,0.1);
    }
    .pito-bubble:after {
        content: ''; position: absolute; bottom: -20px; left: 40px;
        border-width: 20px 20px 0; border-style: solid;
        border-color: #3a7bd5 transparent; display: block; width: 0;
    }
    .stAlert { border: 2px solid #3a7bd5 !important; border-radius: 12px !important; }
    .stButton > button {
        width: 100%; border-radius: 12px; height: 3.5em;
        background: linear-gradient(45deg, #3a7bd5, #00d2ff) !important;
        color: white !important; font-weight: bold; border: none;
    }
    header {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# --- 2. VERİ YÖNETİMİ (MÜKERRER KAYIT ÖNLEYİCİ) ---
SHEET_URL = "https://docs.google.com/spreadsheets/d/1lat8rO2qm9QnzEUYlzC_fypG3cRkGlJfSfTtwNvs318/edit#gid=0"
conn = st.connection("gsheets", type=GSheetsConnection)

def get_db():
    try:
        df = conn.read(spreadsheet=SHEET_URL, ttl=0)
        if df is None or df.empty:
            return pd.DataFrame(columns=["Okul No", "Öğrencinin Adı", "Sınıf", "Puan", "Rütbe", "Tamamlanan Modüller", "Tarih"])
        # Okul No sütununu string yaparak karşılaştırma hatalarını önle
        df["Okul No"] = df["Okul No"].astype(str)
        return df.dropna(subset=["Okul No"])
    except:
        return pd.DataFrame(columns=["Okul No", "Öğrencinin Adı", "Sınıf", "Puan", "Rütbe", "Tamamlanan Modüller", "Tarih"])

def auto_save_score():
    """Öğrenci verilerini Okul No'ya göre günceller (Mükerrer kaydı siler)."""
    try:
        no = str(st.session_state.student_no)
        name = st.session_state.student_name
        sınıf = st.session_state.student_class
        score = st.session_state.total_score
        progress = ",".join(["1" if m else "0" for m in st.session_state.completed_modules])
        
        if score < 200: rank = "🌱 Python Çırağı"
        elif score < 500: rank = "💻 Kod Yazarı"
        elif score < 850: rank = "🛠️ Yazılım Geliştirici"
        else: rank = "🏆 Python Ustası"
        
        df = get_db()
        
        # Yeni satırı oluştur
        new_row = pd.DataFrame([[no, name, sınıf, score, rank, progress, datetime.now().strftime("%H:%M:%S")]], 
                               columns=["Okul No", "Öğrencinin Adı", "Sınıf", "Puan", "Rütbe", "Tamamlanan Modüller", "Tarih"])
        
        # --- TEK GİRİŞ MANTIĞI ---
        # 1. Eski verinin içine yeni satırı ekle
        # 2. 'Okul No' sütununa göre en son kaydedileni tut, diğerlerini sil
        updated_df = pd.concat([df, new_row], ignore_index=True)
        updated_df = updated_df.drop_duplicates(subset=["Okul No"], keep="last")
        
        conn.update(spreadsheet=SHEET_URL, data=updated_df)
    except:
        pass

# --- 3. SESSION STATE ---
if 'student_name' not in st.session_state:
    vars = {'student_name': "", 'student_no': "", 'student_class': "", 'completed_modules': [False]*8, 
            'current_module': 0, 'current_exercise': 0, 'exercise_passed': False, 'total_score': 0, 
            'scored_exercises': set(), 'current_potential_score': 20}
    for k, v in vars.items(): st.session_state[k] = v

PITO_IMG = "assets/pito.png"

# --- 4. GİRİŞ EKRANI ---
if st.session_state.student_name == "":
    st.markdown("<br>", unsafe_allow_html=True)
    _, col_mid, _ = st.columns([1, 2, 1])
    with col_mid:
        st.markdown('<div class="pito-bubble">Merhaba Arkadaşlar! Ben <b>Pito</b>. Sınıfını seç ve Python dünyasında yarışmaya başla!</div>', unsafe_allow_html=True)
        if os.path.exists(PITO_IMG): st.image(PITO_IMG, width=150)
        else: st.image("https://img.icons8.com/fluency/150/robot-viewer.png", width=120)
        
        st.title("Pito Akademi")
        in_no = st.text_input("Okul Numaran:", placeholder="Örn: 452")
        in_name = st.text_input("Adın Soyadın:", placeholder="Örn: Gamzenur Muslu")
        in_class = st.selectbox("Sınıfın:", SINIFLAR)
        
        if st.button("Atölyeye Gir 🚀"):
            if in_no.strip() and in_name.strip():
                st.session_state.student_no, st.session_state.student_name, st.session_state.student_class = in_no.strip(), in_name.strip(), in_class
                df = get_db()
                user_data = df[df["Okul No"] == in_no.strip()]
                if not user_data.empty:
                    st.session_state.total_score = int(user_data.iloc[0]["Puan"])
                    prog_str = str(user_data.iloc[0]["Tamamlanan Modüller"])
                    st.session_state.completed_modules = [True if x == "1" else False for x in prog_str.split(",")]
                    st.toast(f"Tekrar hoş geldin {in_name}!", icon="✨")
                st.rerun()
            else: st.warning("Tüm alanları doldurmalısın!")
    st.stop()

# --- 5. MÜFREDAT VE ETKİNLİKLER (EKSİKSİZ 8 MODÜL) ---
training_data = [
    {"module_title": "1. Giriş ve Çıktı", "exercises": [
        {"msg": "Ekrana 'Merhaba Pito' yazdır.", "task": "print('___')", "check": lambda c, o: "Merhaba Pito" in o},
        {"msg": "100 sayısını yazdır.", "task": "print(___)", "check": lambda c, o: "100" in o},
        {"msg": "Puan: 100 yazdır (virgül kullan).", "task": "print('Puan:', ___)", "check": lambda c, o: "Puan: 100" in o},
        {"msg": "Yorum satırı ekle (#).", "task": "___ Bu bir yorumdur", "check": lambda c, o: "#" in c},
        {"msg": "Alt satır karakterini (\\n) tırnaklar içinde kullanarak Üst ve Alt kelimelerini ayır.", "task": "print('Üst' + '___' + 'Alt')", "check": lambda c, o: "\n" in o}
    ]},
    {"module_title": "2. Değişkenler ve Giriş", "exercises": [
        {"msg": "yas = 15 tanımla ve yazdır.", "task": "yas = ___\nprint(yas)", "check": lambda c, o: "15" in o},
        {"msg": "İsim ata (isim = 'Pito').", "task": "isim = '___'\nprint(isim)", "check": lambda c, o: "Pito" in o},
        {"msg": "Kullanıcıdan veri al (input).", "task": "ad = ___('Adın: ')\nprint(ad)", "check": lambda c, o: "input" in c},
        {"msg": "Sayıyı metne çevir (str).", "task": "s = 10\nprint(___(s))", "check": lambda c, o: "str" in c},
        {"msg": "Girişi tam sayıya çevir (int).", "task": "n = ___(___('S: '))\nprint(n + 5)", "check": lambda c, o: "int" in c}
    ]},
    {"module_title": "3. Karar Yapıları", "exercises": [
        {"msg": "Eşitlik kontrolü (==).", "task": "if 10 ___ 10: print('On')", "check": lambda c, o: "==" in c},
        {"msg": "Değilse durumu (else).", "task": "if 5 > 10: print('A')\n___: print('B')", "check": lambda c, o: "else" in c},
        {"msg": "85 ve üstü (>=).", "task": "if 90 ___ 85: print('Pekiyi')", "check": lambda c, o: ">=" in c},
        {"msg": "İki koşul (and).", "task": "if 1==1 ___ 2==2: print('Ok')", "check": lambda c, o: "and" in c},
        {"msg": "Değilse Eğer (elif).", "task": "x=60\nif x>80: pass\n___ x>50: print('B')", "check": lambda c, o: "elif" in c}
    ]},
    {"module_title": "4. Döngü Yapıları", "exercises": [
        {"msg": "3 kez dönen for döngüsü.", "task": "for i in ___(3): print('X')", "check": lambda c, o: o.count("X") == 3},
        {"msg": "Sayacı yazdır.", "task": "for i in range(2): print(___)", "check": lambda c, o: "1" in o},
        {"msg": "While döngüsü başlat.", "task": "i=0\n___ i<1: print('Y'); i+=1", "check": lambda c, o: "while" in c},
        {"msg": "Döngüyü kır (break).", "task": "for i in range(5): if i==2: ___\n print(i)", "check": lambda c, o: "2" not in o},
        {"msg": "Adımı atla (continue).", "task": "for i in range(3): if i==1: ___\n print(i)", "check": lambda c, o: "1" not in o}
    ]},
    {"module_title": "5. Listeler & Fonksiyonlar", "exercises": [
        {"msg": "Liste oluştur [10, 20].", "task": "L = [___, 20]\nprint(L)", "check": lambda c, o: "10" in o},
        {"msg": "İndeks 0'a eriş.", "task": "L = [5, 6]\nprint(L[___])", "check": lambda c, o: "5" in o},
        {"msg": "Uzunluk bul (len).", "task": "L = [1, 2]\nprint(___(L))", "check": lambda c, o: "2" in o},
        {"msg": "Fonksiyon tanımla (def).", "task": "___ f(): print('X')", "check": lambda c, o: "def" in c},
        {"msg": "Fonksiyonu çağır.", "task": "def f(): print('X')\n___", "check": lambda c, o: "f()" in c}
    ]},
    {"module_title": "6. İleri Veri Yapıları", "exercises": [
        {"msg": "Tuple oluştur (1, 2).", "task": "t = (___, 2)\nprint(t)", "check": lambda c, o: "1" in o},
        {"msg": "Set tanımla {1, 2}.", "task": "s = {1, 2, ___}\nprint(s)", "check": lambda c, o: "1" in o},
        {"msg": "Sözlük 'ad': 'Pito'.", "task": "d = {'ad': '___'}\nprint(d['ad'])", "check": lambda c, o: "Pito" in o},
        {"msg": "Anahtar ekle.", "task": "d = {'a': 1}\nd['___'] = 2", "check": lambda c, o: "'b'" in c or '"b"' in c},
        {"msg": "Anahtarları listele.", "task": "d = {'a': 1}\nprint(d.___())", "check": lambda c, o: "keys" in c}
    ]},
    {"module_title": "7. OOP", "exercises": [
        {"msg": "Sınıf tanımla (class).", "task": "___ Robot: pass", "check": lambda c, o: "class" in c},
        {"msg": "Nesne oluştur.", "task": "class R: pass\np = ___()", "check": lambda c, o: "R()" in c},
        {"msg": "Nitelik ata.", "task": "class R: pass\np = R()\np.___ = 'Mavi'", "check": lambda c, o: "renk" in c},
        {"msg": "Metot ekle.", "task": "class R: def ___(self): print('Bip')", "check": lambda c, o: "ses" in c},
        {"msg": "Metot çağır.", "task": "class R: def s(self): print('X')\nr = R()\nr.___()", "check": lambda c, o: "s()" in c}
    ]},
    {"module_title": "8. Dosyalar", "exercises": [
        {"msg": "Dosya aç (open).", "task": "f = ___('n.txt', 'w')", "check": lambda c, o: "open" in c},
        {"msg": "Dosyaya yaz (write).", "task": "f = open('t.txt', 'w')\nf.___('X')\nf.close()", "check": lambda c, o: "write" in c},
        {"msg": "Okuma modu ('r').", "task": "f = open('t.txt', '___')", "check": lambda c, o: "'r'" in c},
        {"msg": "İçeriği oku (read).", "task": "f = open('t.txt', 'r')\ni = f.___()\nprint(i)", "check": lambda c, o: "read" in c},
        {"msg": "Dosyayı kapat (close).", "task": "f = open('t.txt', 'r')\nf.___()", "check": lambda c, o: "close" in c}
    ]}
]

# --- 6. ARA YÜZ VE EDİTÖR ---
st.markdown(f"#### 👋 {st.session_state.student_name} ({st.session_state.student_class}) | ⭐ Puan: {st.session_state.total_score}")
st.progress(min(st.session_state.total_score / 1000, 1.0))

mod_titles = [f"{'✅' if st.session_state.completed_modules[i] else '📖'} {m['module_title']}" for i, m in enumerate(training_data)]
sel_mod = st.selectbox("Modül Seç:", mod_titles, index=st.session_state.current_module)
new_idx = mod_titles.index(sel_mod)
if new_idx != st.session_state.current_module:
    st.session_state.current_module, st.session_state.current_exercise, st.session_state.exercise_passed, st.session_state.current_potential_score = new_idx, 0, False, 20
    st.rerun()

st.divider()
m_idx, e_idx = st.session_state.current_module, st.session_state.current_exercise
curr_ex = training_data[m_idx]["exercises"][e_idx]

# PİTO KONUŞMA ALANI (GÖRSEL BÜYÜTÜLDÜ)
c1, c2 = st.columns([1.5, 5])
with c1:
    if os.path.exists(PITO_IMG): st.image(PITO_IMG, width=180)
    else: st.image("https://img.icons8.com/fluency/180/robot-viewer.png", width=160)
with c2:
    st.info(f"##### 🗣️ Pito Diyor Ki:\n\n{curr_ex['msg']}")
    st.caption(f"🎁 Görev Puanı: {st.session_state.current_potential_score}")

code = st_ace(value=curr_ex['task'], language="python", theme="dracula", font_size=14, height=180, wrap=True, key=f"ace_{m_idx}_{e_idx}")

# --- TEKNİK HATA ÇÖZÜMLERİ ---
if st.button("🔍 Görevi Kontrol Et", use_container_width=True):
    old_stdout = sys.stdout 
    new_stdout = StringIO()
    sys.stdout = new_stdout # Unpack hatası giderildi
    
    def mock_input(p=""): return "10"
    
    try:
        exec(code.replace("___", "None"), {"input": mock_input})
        sys.stdout = old_stdout 
        output = new_stdout.getvalue()
        
        st.subheader("📟 Çıktı")
        st.code(output if output else "Kod çalıştı!")
        
        if curr_ex['check'](code, output) and "___" not in code:
            st.session_state.exercise_passed = True
            ex_key = f"{m_idx}_{e_idx}"
            if ex_key not in st.session_state.scored_exercises:
                st.session_state.total_score += st.session_state.current_potential_score
                st.session_state.scored_exercises.add(ex_key)
                auto_save_score() # Otomatik kayıt
            st.success("Tebrikler! ✅")
        else:
            if not st.session_state.exercise_passed:
                st.session_state.current_potential_score = max(0, st.session_state.current_potential_score - 5)
            st.warning(f"Hatalı! Puanın {st.session_state.current_potential_score}'ye düştü.")
    except Exception as e:
        sys.stdout = old_stdout
        st.error(f"Hata! {e}")

if st.session_state.exercise_passed:
    if e_idx < 4:
        if st.button("➡️ Sonraki Adım"):
            st.session_state.current_exercise, st.session_state.exercise_passed, st.session_state.current_potential_score = e_idx+1, False, 20
            st.rerun()
    else:
        if st.button("🏆 Modülü Bitir"):
            st.session_state.completed_modules[m_idx], st.session_state.exercise_passed, st.session_state.current_potential_score = True, False, 20
            if m_idx < 7: st.session_state.current_module, st.session_state.current_exercise = m_idx+1, 0
            auto_save_score(); st.balloons(); st.rerun()

# --- SINIF BAZLI LİDERLİK TABLOSU (MÜKERRER KAYITSIZ) ---
st.divider()
with st.expander(f"🏆 {st.session_state.student_class} Liderlik Tablosu"):
    df_all = get_db()
    # Sadece kendi sınıfını filtrele ve mükerrer kayıtları (Okul No'ya göre) temizle
    df_class = df_all[df_all["Sınıf"] == st.session_state.student_class]
    df_class = df_class.sort_values(by="Puan", ascending=False).drop_duplicates(subset=["Okul No"])
    
    if not df_class.empty:
        # Sütunları düzenle ve göster
        st.dataframe(df_class[["Öğrencinin Adı", "Puan", "Rütbe"]], use_container_width=True)
    else: 
        st.write("Henüz bu sınıfta kayıt bulunamadı.")