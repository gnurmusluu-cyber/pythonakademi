import streamlit as st
import pandas as pd
import base64
import time

# --- 1. SAYFA YAPILANDIRMASI VE STİL ---
st.set_page_config(page_title="Pito Python Akademi", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
    <style>
    .stTextInput > div > div > input { border: 2px solid #FF4B4B; font-size: 18px; }
    .stTextInput > div > div > input:focus { border-color: #2E7D32; box-shadow: 0 0 10px #2E7D32; }
    .pito-note { background-color: #E8F5E9; padding: 20px; border-radius: 15px; border: 1px dashed #2E7D32; margin-bottom: 20px; }
    .leaderboard-card { background-color: #F8F9FA; padding: 12px; border-radius: 10px; border-left: 5px solid #FFD700; margin-bottom: 8px; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. VERİ VE RÜTBE YÖNETİMİ ---
SHEET_URL = "https://docs.google.com/spreadsheets/d/1lat8rO2qm9QnzEUYlzC_fypG3cRkGlJfSfTtwNvs318/export?format=csv"

def get_rank(points):
    # Kullanıcı tarafından belirtilen rütbe hiyerarşisi
    ranks = [
        (800, "🏆 Python Kahramanı"), (700, "🤖 OOP Robotu"), (600, "📦 Fonksiyon Kaptanı"),
        (500, "📋 Liste Uzmanı"), (400, "🌀 Döngü Ustası"), (300, "🧱 Mantık Mimarı"),
        (200, "🪵 Kod Oduncusu"), (100, "🌱 Python Çırağı"), (0, "🥚 Yeni Başlayan")
    ]
    for limit, label in ranks:
        if points >= limit: return label
    return "🥚 Yeni Başlayan"

def render_gif(name):
    """GIF'lerin donmasını engellemek için base64 ile gömme yöntemi."""
    try:
        with open(f"assets/{name}.gif", "rb") as f:
            data = f.read()
            url = base64.b64encode(data).decode()
            st.markdown(f'<img src="data:image/gif;base64,{url}" width="280">', unsafe_allow_html=True)
    except:
        st.info(f"[{name} GIF'i Hazırlanıyor...]")

# --- 3. 8 MODÜL VE 40 EGZERSİZLİK MÜFREDAT ---
training_data = [
    {"module_title": "1. İletişim: print() ve Çıktı Dünyası", "exercises": [
        {"msg": "Python'da ekrana mesaj yazdırmak için `print()` fonksiyonunu kullanırız. Bilgisayara bir metin yazdırmak için o metni mutlaka tırnak (' ') içine almalısın.\n\n**Görev:** Ekrana tam olarak **'Merhaba Pito'** yazdır.", "task": "print('___')", "solution": "print('Merhaba Pito')", "hint": "Metinleri mutlaka tırnak işaretleri arasına yazmalısın."},
        {"msg": "Sayılar (Integer), metinlerden farklıdır; tırnak gerektirmezler.\n\n**Görev:** Boşluğa tırnak kullanmadan sadece **100** sayısını yaz.", "task": "print(___)", "solution": "print(100)", "hint": "Sayıları yazarken tırnak kullanma!"},
        {"msg": "Virgül (`,`) farklı veri tiplerini aynı satırda birleştirir.\n\n**Görev:** 'Puan:' metni ile **100** sayısını yanyana bas.", "task": "print('Puan:', ___)", "solution": "print('Puan:', 100)", "hint": "Virgülden sonra tırnaksız 100 yaz."},
        {"msg": "`#` işareti Python'a 'Bu satırı görmezden gel' demektir. Sadece kod yazanlara not bırakmak içindir.\n\n**Görev:** Satırın en başına **#** işaretini koy.", "task": "___ bu bir yoldur", "solution": "# bu bir yoldur", "hint": "Kare (diyez) işaretini en başa koy."},
        {"msg": "`\\n` kaçış karakteri metni alt satıra böler.\n\n**Görev:** Boşluğa **\\n** yaz.", "task": "print('Üst' + '___' + 'Alt')", "solution": "print('Üst\\nAlt')", "hint": "Tırnaklar içine \\n karakterini yazmalısın."}
    ]},
    {"module_title": "2. Hafıza: Değişkenler ve input()", "exercises": [
        {"msg": "Değişkenler hafızadaki kutulardır. `=` işareti atama yapar.\n\n**Görev:** `yas` değişkenine **15** değerini ata.", "task": "yas = ___", "solution": "yas = 15", "hint": "yas = 15 şeklinde yaz."},
        {"msg": "Metin atarken tırnak şarttır.\n\n**Görev:** `isim` değişkenine **'Pito'** değerini ata.", "task": "isim = '___'", "solution": "isim = 'Pito'", "hint": "Tırnaklar arasına Pito yaz."},
        {"msg": "`input()` kullanıcıdan bilgi bekler.\n\n**Görev:** Boşluğa **input** fonksiyonunu yaz.", "task": "ad = ___('Adın: ')", "solution": "ad = input('Adın: ')", "hint": "Veri alma kelimesi olan input yaz."},
        {"msg": "`str()` sayıları metne çevirir.\n\n**Görev:** 10 sayısını metne çeviren **str** fonksiyonunu yaz.", "task": "print(___(10))", "solution": "print(str(10))", "hint": "str yazmalısın."},
        {"msg": "`int()` metni sayıya çevirir. Matematik için şarttır.\n\n**Görev:** Dış boşluğa **int**, içe **input** yaz.", "task": "n = ___(___('S: '))", "solution": "n = int(input('S: '))", "hint": "int(input()) yapısını kur."}
    ]},
    {"module_title": "3. Karar Yapıları: If-Else Dünyası", "exercises": [
        {"msg": "`if` (eğer) şart kontrolüdür. Eşitlik için `==` kullanılır.\n\n**Görev:** Sayı 10'a eşitse 'OK' yazdıracak operatörü (**==**) boşluğa yaz.", "task": "if 10 ___ 10: print('OK')", "solution": "if 10 == 10:", "hint": "Çift eşittir kullan."},
        {"msg": "Şart yanlışsa `else:` bloğu çalışır.\n\n**Görev:** Boşluğa **else** yaz.", "task": "if 5 > 10: pass\n___: print('Hata')", "solution": "else:", "hint": "Sadece else: yaz."},
        {"msg": "`elif` birden fazla şartı denetler.\n\n**Görev:** Puan 50'den büyükse 'Pass' yazacak şartı eklemek için boşluğa **elif** yaz.", "task": "p = 60\nif p < 50: pass\n___ p > 50: print('Geçti')", "solution": "elif p > 50:", "hint": "elif kullanmalısın."},
        {"msg": "`and` (ve) iki tarafın da doğru olmasını bekler.\n\n**Görev:** Boşluğa **and** yaz.", "task": "if 1 == 1 ___ 2 == 2: print('OK')", "solution": "and", "hint": "ve anlamına gelen and yaz."},
        {"msg": "`!=` eşit değilse demektir.\n\n**Görev:** s değişkeni 0'a eşit değilse 'Var' yazdıran operatörü (**!=**) boşluğa koy.", "task": "s = 5\nif s ___ 0: print('Var')", "solution": "if s != 0:", "hint": "!= operatörünü koy."}
    ]},
    {"module_title": "4. Otomasyon: For ve While Döngüleri", "exercises": [
        {"msg": "`for` döngüsü tekrar yapar. `range(5)` sayıları üretir.\n\n**Görev:** Boşluğa **range** yaz.", "task": "for i in ___(5): print(i)", "solution": "for i in range(5):", "hint": "range yaz."},
        {"msg": "`while` şart doğru oldukça döner.\n\n**Görev:** Boşluğa **while** yaz.", "task": "i = 0\n___ i == 0: print('Dönüyor'); i += 1", "solution": "while i == 0:", "hint": "while ile başlat."},
        {"msg": "`break` döngüyü bitirir.\n\n**Görev:** i değeri 1 olduğunda döngüyü bitiren **break** komutunu yaz.", "task": "for i in range(5):\n if i == 1: ___\n print(i)", "solution": "break", "hint": "break yaz."},
        {"msg": "`continue` o adımı atlar.\n\n**Görev:** 1 değerini atlayan **continue** komutunu yaz.", "task": "for i in range(3):\n if i == 1: ___\n print(i)", "solution": "continue", "hint": "continue yaz."},
        {"msg": "Listede gezinmek için `in` kullanılır.\n\n**Görev:** Listedeki her harfi basmak için **in** anahtarını yaz.", "task": "for x ___ ['A', 'B']: print(x)", "solution": "for x in", "hint": "in kullan."}
    ]},
    {"module_title": "5. Gruplama: Listeler", "exercises": [
        {"msg": "Listeler `[]` içine yazılır.\n\n**Görev:** Boşluğa **10** yazarak listeyi kur.", "task": "L = [___, 20]", "solution": "L = [10, 20]", "hint": "Sadece 10 yaz."},
        {"msg": "Saymaya 0'dan başlarız! `[0]` ilk elemanı verir.\n\n**Görev:** İlk elemana (50) erişmek için **0** yaz.", "task": "L = [50, 60]\nprint(L[___])", "solution": "L[0]", "hint": "İlk indeks 0'dır."},
        {"msg": "`.append()` sonuna yeni eleman ekler.\n\n**Görev:** Boşluğa **append** yaz.", "task": "L = [10]\nL.___ (30)\nprint(L)", "solution": "L.append(30)", "hint": "append yaz."},
        {"msg": "`len()` boyut ölçer.\n\n**Görev:** Boşluğa **len** yaz.", "task": "L = [1, 2, 3]\nprint(___(L))", "solution": "len(L)", "hint": "len kullan."},
        {"msg": "`.pop()` son elemanı atar.\n\n**Görev:** Boşluğa **pop** yaz.", "task": "L = [1, 2]\nL.___()", "solution": "L.pop()", "hint": "pop yaz."}
    ]},
    {"module_title": "6. Modülerlik: Fonksiyonlar ve Sözlükler", "exercises": [
        {"msg": "`def` fonksiyon tanımlar.\n\n**Görev:** Boşluğa **def** yaz.", "task": "___ pito(): print('Hi')", "solution": "def pito():", "hint": "def yaz."},
        {"msg": "**Sözlükler (Dictionary)**, veri çiftlerini `{anahtar: değer}` şeklinde tutar.\n\n**Görev:** 'ad' anahtarına karşılık gelen değer boşluğuna **'Pito'** yaz.", "task": "d = {'ad': '___'}", "solution": "d = {'ad': 'Pito'}", "hint": "Pito yaz."},
        {"msg": "**Tuple**, listeye benzer ama `()` ile kurulur.\n\n**Görev:** Boşluğa sadece **1** yaz.", "task": "t = (___, 2)", "solution": "t = (1, 2)", "hint": "Boşluğa 1 yaz."},
        {"msg": "`.keys()` metodu sözlükteki tüm anahtarları listeler.\n\n**Görev:** Boşluğa **keys** yaz.", "task": "d = {'a':1}\nprint(d.___())", "solution": "d.keys()", "hint": "keys yaz."},
        {"msg": "`return` sonucu dışarı fırlatır.\n\n**Görev:** Boşluğa **return** yaz.", "task": "def f(): ___ 5", "solution": "return 5", "hint": "return kullan."}
    ]},
    {"module_title": "7. OOP: Nesne Tabanlı Dünya", "exercises": [
        {"msg": "`class` bir fabrikadır (kalıptır). Nesne ise o fabrikadan çıkan üründür.\n\n**Görev:** Bir Robot kalıbı oluşturmak için boşluğa **class** anahtar kelimesini yaz.", "task": "___ Robot: pass", "solution": "class Robot:", "hint": "class yaz."},
        {"msg": "Robot kalıbından r isminde bir ürün almak için boşluğa **Robot()** yaz.", "task": "class Robot: pass\nr = ___", "solution": "r = Robot()", "hint": "Robot() yazmalısın."},
        {"msg": "Özellikler nokta (`.`) ile atanır.\n\n**Görev:** r nesnesinin **renk** özelliğini 'Mavi' yapmak için boşluğa **renk** yaz.", "task": "class R: pass\nr = R()\nr.___ = 'Mavi'", "solution": "r.renk = 'Mavi'", "hint": "renk yaz."},
        {"msg": "`self` nesnenin kendisidir.\n\n**Görev:** Parantez içine **self** anahtarını yaz.", "task": "class R:\n def ses(___): print('Bip')", "solution": "def ses(self):", "hint": "self yaz."},
        {"msg": "r nesnesinin s() metodunu çalıştırmak için boşluğa **s()** yaz.", "task": "class R:\n def s(self): print('X')\nr = R()\nr.___()", "solution": "r.s()", "hint": "s() yazmalısın."}
    ]},
    {"module_title": "8. Kalıcılık: Dosya Yönetimi", "exercises": [
        {"msg": "Saklamak için `open()` kullanılır. **'w'** yazmak içindir.\n\n**Görev:** Boşlukları **open** ve **'w'** ile doldur.", "task": "f = ___('n.txt', '___')", "solution": "open('n.txt', 'w')", "hint": "open ve w kullan."},
        {"msg": "`.write()` metodu veriyi dosyaya yazar.\n\n**Görev:** Boşluğa **write** yaz.", "task": "f = open('t.txt', 'w')\nf.___('X')\nf.close()", "solution": "f.write('X')", "hint": "write yaz."},
        {"msg": "Okuma için **'r'** modu kullanılır.\n\n**Görev:** Boşluğa **r** harfini koy.", "task": "f = open('t.txt', '___')", "solution": "f = open('t.txt', 'r')", "hint": "r yaz."},
        {"msg": "`.read()` içeriği çeker.\n\n**Görev:** İçeriği almak için boşluğa **read** yaz.", "task": "f = open('t.txt', 'r')\nprint(f.___())", "solution": "f.read()", "hint": "read yaz."},
        {"msg": "`.close()` dosyayı kapatır.\n\n**Görev:** Dosyayı kapatmak için boşluğa **close** yaz.", "task": "f = open('t.txt', 'r')\nf.___()", "solution": "f.close()", "hint": "close yaz."}
    ]}
]

# --- 4. DURUM YÖNETİMİ ---
if 'user' not in st.session_state:
    st.session_state.user = None
    st.session_state.errors = 0
    st.session_state.score_pool = 20
    st.session_state.review_mode = False

def update_db(user_data):
    # Gerçek uygulamada burası GSheets'e yazma yapmalı.
    # Şimdilik session'da tutuluyor.
    st.session_state.user = user_data

def show_sidebar_leaderboard():
    try:
        df = pd.read_csv(SHEET_URL)
        st.sidebar.markdown("### 🏆 Okul Liderlik Tablosu")
        for _, row in df.sort_values(by="Puan", ascending=False).head(10).iterrows():
            st.sidebar.markdown(f"""
            <div class="leaderboard-card">
                <b>{row['Öğrencinin Adı']}</b> ({row['Sınıf']})<br>
                {row['Rütbe']} | {row['Puan']} P
            </div>
            """, unsafe_allow_html=True)
    except:
        st.sidebar.info("Liderlik tablosu yükleniyor...")

# --- 5. GİRİŞ EKRANI ---
if st.session_state.user is None:
    col1, col2 = st.columns([2, 1])
    with col1:
        render_gif("pito_merhaba")
        st.title("Pito Python Akademi")
        st.subheader("Hoş geldin Genç Yazılımcı!")
        
        okul_no = st.text_input("Okul Numaranı Gir (Sadece Sayı):", placeholder="Örn: 123")
        
        if okul_no:
            try:
                df = pd.read_csv(SHEET_URL)
                user_match = df[df["Okul No"] == int(okul_no)]
                
                if not user_match.empty:
                    u = user_match.iloc[0].to_dict()
                    st.success(f"Merhaba {u['Öğrencinin Adı']}!")
                    st.write(f"Şu an: Modül {u['Mevcut Modül']}, Egzersiz {u['Mevcut Egzersiz']}")
                    if st.button("Evet, Benim! Devam Et"):
                        st.session_state.user = u
                        st.rerun()
                    if st.button("Hayır, Ben Değilim"):
                        st.rerun()
                else:
                    st.warning("Numara kayıtlı değil. Yeni Kayıt Ol!")
                    with st.form("kayit"):
                        ad = st.text_input("Ad Soyad:")
                        snf = st.selectbox("Sınıf:", ["9-A", "9-B", "10-A", "10-B"])
                        if st.form_submit_button("Kayıt Ol ve Başla"):
                            new_user = {
                                "Okul No": int(okul_no), "Öğrencinin Adı": ad, "Sınıf": snf,
                                "Puan": 0, "Rütbe": "🥚 Yeni Başlayan", "Mevcut Modül": 1, "Mevcut Egzersiz": 1
                            }
                            st.session_state.user = new_user
                            st.rerun()
            except:
                st.error("Veri tabanı bağlantısı kurulamadı!")
    with col2:
        show_sidebar_leaderboard()

# --- 6. EĞİTİM PANELİ ---
else:
    u = st.session_state.user
    mod_idx = int(u["Mevcut Modül"]) - 1
    ex_idx = int(u["Mevcut Egzersiz"]) - 1
    
    # Tüm modüller bittiyse
    if mod_idx >= 8:
        render_gif("pito_mezun")
        st.balloons()
        st.title("🎓 Tebrikler Python Kahramanı!")
        if st.button("Eğitimi Sıfırla ve Tekrar Al"):
            u["Puan"] = 0; u["Mevcut Modül"] = 1; u["Mevcut Egzersiz"] = 1
            st.rerun()
        st.stop()

    curr_mod = training_data[mod_idx]
    curr_ex = curr_mod["exercises"][ex_idx]

    # İlerleme Çubuğu
    total_steps = (mod_idx * 5) + (ex_idx + 1)
    st.progress(total_steps / 40)
    st.write(f"**Modül {mod_idx+1}:** {curr_mod['module_title']} | **Adım:** {ex_idx+1}/5")

    col_play, col_side = st.columns([2.5, 1])

    with col_play:
        if st.session_state.errors == 0: render_gif("pito_dusunuyor")
        else: render_gif("pito_hata")

        st.markdown(f'<div class="pito-note"><b>🐍 Pito\'nun Notu:</b><br>{curr_ex["msg"]}</div>', unsafe_allow_html=True)
        
        # Giriş Alanı
        st.markdown("### ⌨️ Kod Paneli")
        answer = st.text_input(f"Giriş: {curr_ex['task']}", key=f"ans_{mod_idx}_{ex_idx}")

        if st.button("Kontrol Et"):
            if not answer:
                st.warning("⚠️ Lütfen bir veri gir!")
            else:
                # Boşluk temizleme ile basit kontrol
                is_correct = answer.strip().replace(" ","") in curr_ex["solution"].replace(" ","")
                
                if is_correct:
                    st.session_state.errors = 0
                    st.balloons()
                    render_gif("pito_basari")
                    st.success(f"Tebrikler! +{st.session_state.score_pool} Puan Kazandın.")
                    
                    # HATA VEREN KISIMIN GÜVENLİ ÇÖZÜMÜ:
                    clean_out = curr_ex['solution'].replace('print(', '').replace(')', '').replace("'", "").replace('"', "")
                    st.code(f"Kod Çıktısı:\n{clean_out}")
                    
                    # Puan ve İlerleme Güncelleme
                    u["Puan"] += st.session_state.score_pool
                    u["Rütbe"] = get_rank(u["Puan"])
                    if ex_idx < 4: u["Mevcut Egzersiz"] += 1
                    else: u["Mevcut Modül"] += 1; u["Mevcut Egzersiz"] = 1
                    
                    st.session_state.score_pool = 20
                    time.sleep(1.5)
                    st.rerun()
                else:
                    st.session_state.errors += 1
                    st.session_state.score_pool -= 5
                    if st.session_state.score_pool < 0: st.session_state.score_pool = 0
                    
                    if st.session_state.errors < 3:
                        st.error(f"Yanlış cevap! Bu {st.session_state.errors}. hatan. Puanın düşüyor!")
                    elif st.session_state.errors == 3:
                        st.warning(f"💡 Pito'dan İpucu: {curr_ex['hint']}")
                    else:
                        st.error("4 kez hata yaptın. Bu sorudan puan alamadın.")
                        st.info(f"✅ Doğru Çözüm: {curr_ex['solution']}")
                        if st.button("Sonraki Soruya Geç"):
                            st.session_state.errors = 0
                            if ex_idx < 4: u["Mevcut Egzersiz"] += 1
                            else: u["Mevcut Modül"] += 1; u["Mevcut Egzersiz"] = 1
                            st.rerun()

    with col_side:
        st.write(f"### 👤 {u['Öğrencinin Adı']}")
        st.metric("Toplam Puan", f"{u['Puan']}")
        st.write(f"**Rütbe:** {u['Rütbe']}")
        st.divider()
        show_sidebar_leaderboard()
