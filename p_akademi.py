import streamlit as st
import pandas as pd
import base64
from datetime import datetime

# --- 1. SAYFA AYARLARI VE CSS ---
st.set_page_config(page_title="Pito Python Akademi", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
    <style>
    .stTextInput > div > div > input {
        border: 2px solid #FF4B4B;
        font-size: 18px;
        color: #1E1E1E;
    }
    .stTextInput > div > div > input:focus {
        border-color: #2E7D32;
        box-shadow: 0 0 10px #2E7D32;
    }
    .leaderboard-card {
        background-color: #F8F9FA;
        padding: 15px;
        border-radius: 12px;
        border-left: 5px solid #FFD700;
        margin-bottom: 10px;
    }
    .pito-note {
        background-color: #E8F5E9;
        padding: 20px;
        border-radius: 15px;
        border: 1px dashed #2E7D32;
        margin-bottom: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. VERİ TABANI VE YARDIMCI FONKSİYONLAR ---
SHEET_URL = "https://docs.google.com/spreadsheets/d/1lat8rO2qm9QnzEUYlzC_fypG3cRkGlJfSfTtwNvs318/export?format=csv"

def get_rank(points):
    ranks = [
        (4000, "🏆 Python Kahramanı"), (3200, "🤖 OOP Robotu"), (2400, "📦 Fonksiyon Kaptanı"),
        (1800, "📋 Liste Uzmanı"), (1200, "🌀 Döngü Ustası"), (800, "🧱 Mantık Mimarı"),
        (400, "🪵 Kod Oduncusu"), (100, "🌱 Python Çırağı"), (0, "🥚 Yeni Başlayan")
    ]
    for limit, label in ranks:
        if points >= limit: return label
    return "🥚 Yeni Başlayan"

def render_gif(name):
    try:
        file_ = open(f"assets/{name}.gif", "rb")
        contents = file_.read()
        data_url = base64.b64encode(contents).decode("utf-8")
        file_.close()
        st.markdown(f'<img src="data:image/gif;base64,{data_url}" width="280">', unsafe_allow_html=True)
    except FileNotFoundError:
        st.warning(f"{name}.gif bulunamadı.")

def load_db():
    try:
        return pd.read_csv(SHEET_URL)
    except:
        return pd.DataFrame(columns=["Okul No", "Öğrencinin Adı", "Sınıf", "Puan", "Rütbe", "Mevcut Modül", "Mevcut Egzersiz"])

# --- 3. MÜFREDAT VERİSİ (40 ADIM) ---
training_data = [
    {"module_title": "1. İletişim: print() ve Çıktı Dünyası", "exercises": [
        {"msg": "Python'da ekrana mesaj yazdırmak için `print()` fonksiyonunu kullanırız. Metinleri mutlaka tırnak (' ') içine almalısın.", "task": "print('___')", "solution": "print('Merhaba Pito')", "hint": "Metinleri mutlaka tırnak işaretleri arasına yazmalısın."},
        {"msg": "Sayılar (Integer), metinlerden farklıdır; tırnak gerektirmezler. Boşluğa sadece **100** yaz.", "task": "print(___)", "solution": "print(100)", "hint": "Sayıları yazarken tırnak kullanma!"},
        {"msg": "Virgül (`,`) farklı veri tiplerini birleştirir. 'Puan:' metni ile **100** sayısını yanyana bas.", "task": "print('Puan:', ___)", "solution": "print('Puan:', 100)", "hint": "Virgülden sonra tırnaksız 100 yaz."},
        {"msg": "`#` işareti Python'da yorum satırıdır. Bilgisayar bu satırı okumaz. Satırın başına **#** koy.", "task": "___ bu bir yoldur", "solution": "# bu bir yoldur", "hint": "Kare (diyez) işaretini en başa koy."},
        {"msg": "`\\n` karakteri metni alt satıra böler. Boşluğa **\\n** yaz.", "task": "print('Üst' + '___' + 'Alt')", "solution": "print('Üst\\nAlt')", "hint": "Tırnaklar içine \\n karakterini yazmalısın."}
    ]},
    {"module_title": "2. Hafıza: Değişkenler ve input()", "exercises": [
        {"msg": "Değişkenler hafızadaki kutulardır. `yas` değişkenine **15** değerini ata.", "task": "yas = ___", "solution": "yas = 15", "hint": "yas = 15 şeklinde yaz."},
        {"msg": "Metin atarken tırnak şarttır. `isim` değişkenine **'Pito'** değerini ata.", "task": "isim = '___'", "solution": "isim = 'Pito'", "hint": "Tırnaklar arasına Pito yaz."},
        {"msg": "`input()` kullanıcıdan bilgi bekler. Boşluğa **input** fonksiyonunu yaz.", "task": "ad = ___('Adın: ')", "solution": "ad = input('Adın: ')", "hint": "Veri alma kelimesi olan input yaz."},
        {"msg": "`str()` sayıları metne çevirir. 10 sayısını metne çeviren **str** fonksiyonunu yaz.", "task": "print(___(10))", "solution": "print(str(10))", "hint": "str yazmalısın."},
        {"msg": "`int()` metni sayıya çevirir. Dış boşluğa **int**, içe **input** yaz.", "task": "n = ___(___('S: '))", "solution": "n = int(input('S: '))", "hint": "int(input()) yapısını kur."}
    ]},
    {"module_title": "3. Karar Yapıları: If-Else Dünyası", "exercises": [
        {"msg": "Eşitlik için `==` kullanılır. Sayı 10'a eşitse kontrolü için **==** yaz.", "task": "if 10 ___ 10: print('OK')", "solution": "if 10 == 10:", "hint": "Çift eşittir kullan."},
        {"msg": "Şart yanlışsa `else:` çalışır. Boşluğa **else** yaz.", "task": "if 5 > 10: pass\n___: print('Hata')", "solution": "else:", "hint": "Sadece else: yaz."},
        {"msg": "`elif` birden fazla şartı denetler. Boşluğa **elif** yaz.", "task": "p = 60\nif p < 50: pass\n___ p > 50: print('Geçti')", "solution": "elif p > 50:", "hint": "elif kullanmalısın."},
        {"msg": "`and` (ve) iki tarafın da doğru olmasını bekler. Boşluğa **and** yaz.", "task": "if 1 == 1 ___ 2 == 2: print('OK')", "solution": "and", "hint": "ve anlamına gelen and yaz."},
        {"msg": "`!=` eşit değilse demektir. s değişkeni 0'a eşit değilse kontrolü için **!=** yaz.", "task": "s = 5\nif s ___ 0: print('Var')", "solution": "if s != 0:", "hint": "!= operatörünü koy."}
    ]},
    {"module_title": "4. Otomasyon: For ve While Döngüleri", "exercises": [
        {"msg": "`for` döngüsü tekrar yapar. `range(5)` sayıları üretir. Boşluğa **range** yaz.", "task": "for i in ___(5): print(i)", "solution": "for i in range(5):", "hint": "range yaz."},
        {"msg": "`while` şart doğru oldukça döner. Boşluğa **while** yaz.", "task": "i = 0\n___ i == 0: print('Dönüyor'); i += 1", "solution": "while i == 0:", "hint": "while ile başlat."},
        {"msg": "i değeri 1 olduğunda döngüyü bitiren **break** komutunu yaz.", "task": "for i in range(5):\n if i == 1: ___\n print(i)", "solution": "break", "hint": "break yaz."},
        {"msg": "1 değerini atlayan **continue** komutunu yaz.", "task": "for i in range(3):\n if i == 1: ___\n print(i)", "solution": "continue", "hint": "continue yaz."},
        {"msg": "Listede gezinmek için `in` kullanılır. Boşluğa **in** yaz.", "task": "for x ___ ['A', 'B']: print(x)", "solution": "for x in", "hint": "in kullan."}
    ]},
    {"module_title": "5. Gruplama: Listeler", "exercises": [
        {"msg": "Listeler `[]` içine yazılır. Boşluğa **10** yazarak listeyi kur.", "task": "L = [___, 20]", "solution": "L = [10, 20]", "hint": "Sadece 10 yaz."},
        {"msg": "Saymaya 0'dan başlarız! İlk elemana (50) erişmek için **0** yaz.", "task": "L = [50, 60]\nprint(L[___])", "solution": "L[0]", "hint": "İlk indeks 0'dır."},
        {"msg": "`.append()` sonuna yeni eleman ekler. Boşluğa **append** yaz.", "task": "L = [10]\nL.___ (30)\nprint(L)", "solution": "L.append(30)", "hint": "append yaz."},
        {"msg": "`len()` boyut ölçer. Boşluğa **len** yaz.", "task": "L = [1, 2, 3]\nprint(___(L))", "solution": "len(L)", "hint": "len kullan."},
        {"msg": "`.pop()` son elemanı atar. Boşluğa **pop** yaz.", "task": "L = [1, 2]\nL.___()", "solution": "L.pop()", "hint": "pop yaz."}
    ]},
    {"module_title": "6. Modülerlik: Fonksiyonlar ve Sözlükler", "exercises": [
        {"msg": "`def` fonksiyon tanımlar. Boşluğa **def** yaz.", "task": "___ pito(): print('Hi')", "solution": "def pito():", "hint": "def yaz."},
        {"msg": "Sözlükler `{anahtar: değer}` tutar. 'ad' anahtarı için değer boşluğuna **'Pito'** yaz.", "task": "d = {'ad': '___'}", "solution": "d = {'ad': 'Pito'}", "hint": "Pito yaz."},
        {"msg": "Tuple `()` ile kurulur ve değiştirilemez. Boşluğa sadece **1** yaz.", "task": "t = (___, 2)", "solution": "t = (1, 2)", "hint": "Boşluğa 1 yaz."},
        {"msg": "`.keys()` sözlükteki tüm anahtarları listeler. Boşluğa **keys** yaz.", "task": "d = {'a':1}\nprint(d.___())", "solution": "d.keys()", "hint": "keys yaz."},
        {"msg": "`return` sonucu dışarı fırlatır. Boşluğa **return** yaz.", "task": "def f(): ___ 5", "solution": "return 5", "hint": "return kullan."}
    ]},
    {"module_title": "7. OOP: Nesne Tabanlı Dünya", "exercises": [
        {"msg": "`class` bir fabrikadır (kalıptır). Boşluğa **class** anahtar kelimesini yaz.", "task": "___ Robot: pass", "solution": "class Robot:", "hint": "class yaz."},
        {"msg": "Robot kalıbından r isminde bir ürün almak için boşluğa **Robot()** yaz.", "task": "class Robot: pass\nr = ___", "solution": "r = Robot()", "hint": "Robot() yazmalısın."},
        {"msg": "Özellikler nokta (`.`) ile atanır. r nesnesinin **renk** özelliğini 'Mavi' yapmak için boşluğa **renk** yaz.", "task": "class R: pass\nr = R()\nr.___ = 'Mavi'", "solution": "r.renk = 'Mavi'", "hint": "renk yaz."},
        {"msg": "`self` nesnenin kendisidir. Parantez içine **self** anahtarını yaz.", "task": "class R:\n def ses(___): print('Bip')", "solution": "def ses(self):", "hint": "self yaz."},
        {"msg": "r nesnesinin s() metodunu çalıştırmak için boşluğa **s()** yaz.", "task": "class R:\n def s(self): print('X')\nr = R()\nr.___()", "solution": "r.s()", "hint": "s() yazmalısın."}
    ]},
    {"module_title": "8. Kalıcılık: Dosya Yönetimi", "exercises": [
        {"msg": "Saklamak için `open()` kullanılır. **'w'** (write) yazmak içindir. Boşlukları **open** ve **'w'** ile doldur.", "task": "f = ___('n.txt', '___')", "solution": "open('n.txt', 'w')", "hint": "open ve w kullan."},
        {"msg": "`.write()` metodu veriyi dosyaya yazar. Boşluğa **write** yaz.", "task": "f = open('t.txt', 'w')\nf.___('X')\nf.close()", "solution": "f.write('X')", "hint": "write yaz."},
        {"msg": "Okuma için **'r'** (read) modu kullanılır. Boşluğa **r** harfini koy.", "task": "f = open('t.txt', '___')", "solution": "f = open('t.txt', 'r')", "hint": "r yaz."},
        {"msg": "`.read()` içeriği dosyadan çeker. Boşluğa **read** yaz.", "task": "f = open('t.txt', 'r')\nprint(f.___())", "solution": "f.read()", "hint": "read yaz."},
        {"msg": "`.close()` dosyayı kapatır. Boşluğa **close** yaz.", "task": "f = open('t.txt', 'r')\nf.___()", "solution": "f.close()", "hint": "close yaz."}
    ]}
]

# --- 4. SESSION STATE YÖNETİMİ ---
if 'user' not in st.session_state:
    st.session_state.user = None
    st.session_state.errors = 0
    st.session_state.current_score = 20
    st.session_state.review_mode = False

# --- 5. LİDERLİK TABLOSU (SAĞ PANEL) ---
def show_leaderboard():
    df = load_db()
    st.write("### 🏅 Sınıf Liderliği")
    for _, row in df.sort_values(by="Puan", ascending=False).head(10).iterrows():
        st.markdown(f"""
        <div class="leaderboard-card">
            <b>{row['Öğrencinin Adı']}</b> ({row['Sınıf']})<br>
            {row['Rütbe']} - {row['Puan']} Puan
        </div>
        """, unsafe_allow_html=True)

# --- 6. GİRİŞ VE KAYIT EKRANI ---
if st.session_state.user is None:
    col_main, col_lead = st.columns([2, 1])
    with col_main:
        render_gif("pito_merhaba")
        st.title("Pito Python Akademi")
        st.info("Nusaybin Süleyman Bölünmez Anadolu Lisesi Python Eğitim Platformu")
        
        okul_no = st.text_input("Okul Numaranı Gir:", key="login_input")
        if okul_no:
            df = load_db()
            user_data = df[df["Okul No"] == int(okul_no)]
            
            if not user_data.empty:
                u = user_data.iloc[0]
                st.success(f"Seni tanıdım, {u['Öğrencinin Adı']}!")
                st.write(f"Kaldığın yer: Modül {u['Mevcut Modül']}, Egzersiz {u['Mevcut Egzersiz']}")
                if st.button("Evet, Benim! Eğitime Devam"):
                    st.session_state.user = u.to_dict()
                    st.rerun()
                if st.button("Hayır, Ben Değilim"):
                    st.rerun()
            else:
                st.warning("Bu numara sistemde kayıtlı değil. Hemen kayıt ol!")
                with st.form("kayit_form"):
                    ad = st.text_input("Adın ve Soyadın:")
                    sinif = st.selectbox("Sınıfın:", ["9-A", "9-B", "9-C", "10-A", "10-B"])
                    if st.form_submit_button("Kayıt Ol ve Başla"):
                        new_user = {
                            "Okul No": int(okul_no), "Öğrencinin Adı": ad, "Sınıf": sinif,
                            "Puan": 0, "Rütbe": "🥚 Yeni Başlayan", "Mevcut Modül": 1, "Mevcut Egzersiz": 1
                        }
                        st.session_state.user = new_user
                        st.rerun()
    with col_lead:
        show_leaderboard()

# --- 7. ANA EĞİTİM PANELİ ---
else:
    u = st.session_state.user
    m_idx = int(u["Mevcut Modül"]) - 1
    e_idx = int(u["Mevcut Egzersiz"]) - 1
    
    # Tüm modüller bitti mi?
    if m_idx >= 8:
        render_gif("pito_mezun")
        st.balloons()
        st.title("🎓 Tebrikler, Python Kahramanı!")
        st.write("Tüm modülleri başarıyla tamamladın.")
        if st.button("Eğitimi Sıfırla ve Yeniden Başla"):
            st.session_state.user["Puan"] = 0
            st.session_state.user["Mevcut Modül"] = 1
            st.session_state.user["Mevcut Egzersiz"] = 1
            st.rerun()
        if st.button("Liderlik Listesinde Kal"):
            st.info("Liderlik listesindeki yerin korunuyor!")
            st.session_state.review_mode = True
            st.rerun()
        st.stop()

    curr_mod = training_data[m_idx]
    curr_ex = curr_mod["exercises"][e_idx]

    # İlerleme Çubuğu
    total_progress = (m_idx * 5 + e_idx + 1) / 40
    st.progress(total_progress)
    st.write(f"🚀 İlerleme: %{int(total_progress*100)} | Modül: {m_idx+1} | Egzersiz: {e_idx+1}")

    col_play, col_info = st.columns([2.5, 1])

    with col_play:
        if st.session_state.errors == 0: render_gif("pito_dusunuyor")
        else: render_gif("pito_hata")

        st.markdown(f'<div class="pito-note"><b>Pito\'nun Notu:</b><br>{curr_ex["msg"]}</div>', unsafe_allow_html=True)
        
        st.markdown("### 💻 Kod Paneli")
        answer = st.text_input(f"Giriş: {curr_ex['task']}", key=f"ex_{m_idx}_{e_idx}")

        if st.button("Kontrol Et", key="check_btn"):
            if not answer or answer.strip() == "":
                st.warning("⚠️ Lütfen bir veri gir!")
            else:
                # Basit kontrol mekanizması (Kullanıcının solution verisiyle kıyaslama)
                clean_ans = answer.replace(" ", "")
                clean_sol = curr_ex["solution"].replace(" ", "")
                
                if clean_ans in clean_sol or clean_sol in clean_ans:
                    st.session_state.errors = 0
                    st.balloons()
                    render_gif("pito_basari")
                    st.success(f"✨ Harika! Doğru cevap. +{st.session_state.current_score} Puan!")
                    st.code(f"Çıktı: {curr_ex['solution'].replace('print(', '').replace(')', '').replace(\"'\", '')}")
                    
                    # Veriyi Güncelle
                    st.session_state.user["Puan"] += st.session_state.current_score
                    st.session_state.user["Rütbe"] = get_rank(st.session_state.user["Puan"])
                    
                    if e_idx < 4:
                        st.session_state.user["Mevcut Egzersiz"] += 1
                    else:
                        st.session_state.user["Mevcut Modül"] += 1
                        st.session_state.user["Mevcut Egzersiz"] = 1
                    
                    st.session_state.current_score = 20
                    time_sleep = 2
                    st.button("Sonraki Adıma Geç ➡️", on_click=lambda: None)
                else:
                    st.session_state.errors += 1
                    st.session_state.current_score -= 5
                    if st.session_state.current_score < 0: st.session_state.current_score = 0
                    
                    if st.session_state.errors < 3:
                        st.error(f"❌ Hata! Bu {st.session_state.errors}. denemen. Puanın 5 düştü!")
                    elif st.session_state.errors == 3:
                        st.warning(f"💡 Pito'dan İpucu: {curr_ex['hint']}")
                    else:
                        st.error("🚨 4 kez hata yaptın. Bu sorudan puan alamadın.")
                        st.info(f"✅ Doğru Çözüm: {curr_ex['solution']}")
                        if st.button("Sonraki Soruya Geç"):
                            st.session_state.errors = 0
                            if e_idx < 4: st.session_state.user["Mevcut Egzersiz"] += 1
                            else: 
                                st.session_state.user["Mevcut Modül"] += 1
                                st.session_state.user["Mevcut Egzersiz"] = 1
                            st.rerun()

    with col_info:
        st.write(f"### 👤 {u['Öğrencinin Adı']}")
        st.metric("Mevcut Puan", f"{st.session_state.user['Puan']}")
        st.write(f"**Rütbe:** {st.session_state.user['Rütbe']}")
        st.divider()
        show_leaderboard()

# --- 8. TEKNİK KARARLILIK ---
# Her buton st.rerun() içermeli veya state üzerinden yönetilmeli
