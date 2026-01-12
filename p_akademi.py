import streamlit as st
import pandas as pd
import base64
import time

# --- 1. SAYFA YAPILANDIRMASI VE STİL ---
st.set_page_config(page_title="Pito Python Akademi", layout="wide")

st.markdown("""
    <style>
    .stTextInput > div > div > input { border: 2px solid #FF4B4B; font-size: 18px; font-weight: bold; }
    .pito-note { background-color: #E8F5E9; padding: 25px; border-radius: 15px; border: 2px dashed #2E7D32; margin-bottom: 20px; color: #1B5E20; font-size: 1.1rem; }
    .leaderboard-card { background-color: #F8F9FA; padding: 12px; border-radius: 10px; border-left: 5px solid #FFD700; margin-bottom: 8px; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. VERİ VE RÜTBE SİSTEMİ ---
# Google Sheets URL
SHEET_URL = "https://docs.google.com/spreadsheets/d/1lat8rO2qm9QnzEUYlzC_fypG3cRkGlJfSfTtwNvs318/export?format=csv"

def get_rank(points):
    """Puan bazlı rütbe hiyerarşisi [cite: 1]"""
    ranks = [
        (4000, "🏆 Python Kahramanı"), (3500, "🤖 OOP Robotu"), (3000, "📦 Fonksiyon Kaptanı"),
        (2500, "📋 Liste Uzmanı"), (2000, "🌀 Döngü Ustası"), (1500, "🧱 Mantık Mimarı"),
        (1000, "🪵 Kod Oduncusu"), (500, "🌱 Python Çırağı"), (0, "🥚 Yeni Başlayan")
    ]
    for limit, label in ranks:
        if points >= limit: return label
    return "🥚 Yeni Başlayan"

def render_gif(name):
    """GIF dosyasını base64 ile render eder (assets klasörü gereklidir) """
    try:
        with open(f"assets/{name}.gif", "rb") as f:
            data = f.read()
            url = base64.b64encode(data).decode()
            st.markdown(f'<img src="data:image/gif;base64,{url}" width="280">', unsafe_allow_html=True)
    except:
        st.info(f"[{name}.gif yüklenemedi]")

# --- 3. EKSİKSİZ MÜFREDAT (8 MODÜL / 40 ADIM) [cite: 4, 5] ---
training_data = [
    {"module_title": "1. İletişim: print() ve Çıktı Dünyası", "exercises": [
        {"msg": "Python'da ekrana mesaj yazdırmak için `print()` fonksiyonunu kullanırız. Metinleri mutlaka tırnak (' ') içine almalısın.", "task": "print('___')", "solution": "print('Merhaba Pito')", "hint": "Metinleri mutlaka tırnak işaretleri arasına yazmalısın."},
        {"msg": "Sayılar (Integer) tırnak gerektirmez. Boşluğa sadece **100** yaz.", "task": "print(___)", "solution": "print(100)", "hint": "Sayıları yazarken tırnak kullanma!"},
        {"msg": "Virgül (`,`) farklı veri tiplerini birleştirir. 'Puan:' metni ile **100** sayısını yanyana bas.", "task": "print('Puan:', ___)", "solution": "print('Puan:', 100)", "hint": "Virgülden sonra tırnaksız 100 yaz."},
        {"msg": "`#` işareti Python'da yorum satırıdır. Bilgisayar bu satırı okumaz. Başına **#** koy.", "task": "___ bu bir yorumdur", "solution": "# bu bir yorumdur", "hint": "Kare (diyez) işaretini en başa koy."},
        {"msg": "`\\n` karakteri metni alt satıra böler. Boşluğa **\\n** yaz.", "task": "print('Üst' + '___' + 'Alt')", "solution": "print('Üst\\nAlt')", "hint": "Tırnaklar içine \\n yazmalısın."}
    ]},
    {"module_title": "2. Hafıza: Değişkenler ve input()", "exercises": [
        {"msg": "Değişkenler hafızadaki kutulardır. `yas` değişkenine **15** değerini ata.", "task": "yas = ___", "solution": "yas = 15", "hint": "yas = 15 şeklinde yaz."},
        {"msg": "Metin atarken tırnak şarttır. `isim` değişkenine **'Pito'** değerini ata.", "task": "isim = '___'", "solution": "isim = 'Pito'", "hint": "Tırnaklar arasına Pito yaz."},
        {"msg": "`input()` kullanıcıdan bilgi bekler. Boşluğa **input** fonksiyonunu yaz.", "task": "ad = ___('Adın: ')", "solution": "ad = input('Adın: ')", "hint": "Veri alma komutu olan input yaz."},
        {"msg": "`str()` sayıları metne çevirir. 10 sayısını metne çeviren **str** fonksiyonunu yaz.", "task": "print(___(10))", "solution": "print(str(10))", "hint": "str yazmalısın."},
        {"msg": "`int()` metni sayıya çevirir. Boşluklara **int** ve **input** yaz.", "task": "n = ___(___('S: '))", "solution": "n = int(input('S: '))", "hint": "int(input()) yapısını kur."}
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
        {"msg": "`class` bir kalıptır. Robot kalıbı oluşturmak için boşluğa **class** yaz.", "task": "___ Robot: pass", "solution": "class Robot:", "hint": "class yaz."},
        {"msg": "Kalıptan nesne üretmek için Robot() yazılır. Boşluğa **Robot()** yaz.", "task": "class Robot: pass\nr = ___", "solution": "r = Robot()", "hint": "Robot() yazmalısın."},
        {"msg": "Özellikler nokta ile atanır. r nesnesinin **renk** özelliğini 'Mavi' yapmak için boşluğa **renk** yaz.", "task": "class R: pass\nr = R()\nr.___ = 'Mavi'", "solution": "r.renk = 'Mavi'", "hint": "renk yaz."},
        {"msg": "`self` nesnenin kendisidir. Parantez içine **self** yaz.", "task": "class R:\n def ses(___): print('Bip')", "solution": "def ses(self):", "hint": "self yaz."},
        {"msg": "r nesnesinin s() metodunu çalıştırmak için boşluğa **s()** yaz.", "task": "class R:\n def s(self): print('X')\nr = R()\nr.___()", "solution": "r.s()", "hint": "s() yazmalısın."}
    ]},
    {"module_title": "8. Kalıcılık: Dosya Yönetimi", "exercises": [
        {"msg": "Açmak için `open()` kullanılır. Yazmak için **'w'** kipi seçilir. Boşlukları **open** ve **'w'** ile doldur.", "task": "f = ___('n.txt', '___')", "solution": "open('n.txt', 'w')", "hint": "open ve w kullan."},
        {"msg": "`.write()` metodu veriyi yazar. Boşluğa **write** yaz.", "task": "f = open('t.txt', 'w')\nf.___('X')\nf.close()", "solution": "f.write('X')", "hint": "write yaz."},
        {"msg": "Okuma için **'r'** modu kullanılır. Boşluğa **r** harfini koy.", "task": "f = open('t.txt', '___')", "solution": "f = open('t.txt', 'r')", "hint": "r yaz."},
        {"msg": "`.read()` içeriği çeker. Boşluğa **read** yaz.", "task": "f = open('t.txt', 'r')\nprint(f.___())", "solution": "f.read()", "hint": "read yaz."},
        {"msg": "`.close()` dosyayı kapatır. Boşluğa **close** yaz.", "task": "f = open('t.txt', 'r')\nf.___()", "solution": "f.close()", "hint": "close yaz."}
    ]}
]

# --- 4. DURUM YÖNETİMİ ---
if 'user' not in st.session_state:
    st.session_state.user = None
    st.session_state.errors = 0
    st.session_state.score_pool = 20
    st.session_state.is_completed = False

def show_leaderboard():
    try:
        df = pd.read_csv(SHEET_URL)
        st.sidebar.write("### 🎖️ Liderlik Tablosu")
        for _, row in df.sort_values(by="Puan", ascending=False).head(10).iterrows():
            st.sidebar.markdown(f"""<div class="leaderboard-card"><b>{row['Öğrencinin Adı']}</b><br>{row['Rütbe']} | {row['Puan']} P</div>""", unsafe_allow_html=True)
    except:
        st.sidebar.info("Liderlik tablosu yükleniyor...")

# --- 5. GİRİŞ VE ANA PANEL ---
if st.session_state.user is None:
    col_l, col_r = st.columns([2, 1])
    with col_l:
        render_gif("pito_merhaba")
        st.title("Pito Python Akademi")
        okul_no = st.text_input("Okul Numaranı Gir (Sadece Sayı):", placeholder="123")
        if okul_no:
            # Örnek başlangıç verisi (GSheets senkronizasyonu bu aşamada tetiklenir)
            st.session_state.user = {"Okul No": okul_no, "Ad": "Genç Yazılımcı", "Mevcut Modül": 1, "Mevcut Egzersiz": 1, "Puan": 0}
            st.rerun()
    with col_r:
        show_leaderboard()

else:
    u = st.session_state.user
    m_idx = int(u["Mevcut Modül"]) - 1
    e_idx = int(u["Mevcut Egzersiz"]) - 1

    if m_idx >= 8:
        render_gif("pito_mezun")
        st.balloons()
        st.title("🎓 Tebrikler Python Kahramanı!")
        if st.button("Eğitimi Sıfırla"):
            st.session_state.user = None
            st.rerun()
        st.stop()

    curr_ex = training_data[m_idx]["exercises"][e_idx]
    st.progress(((m_idx * 5) + e_idx) / 40)

    c_main, c_side = st.columns([2.5, 1])

    with c_main:
        # --- GIF MANTIĞI GÜNCELLEMESİ ---
        if st.session_state.is_completed:
            # 4. hatada çözüm gösterilirken Pito "düşünüyor" moduna geçsin
            if st.session_state.errors >= 4:
                render_gif("pito_dusunuyor")
            else:
                render_gif("pito_basari")
        elif st.session_state.errors > 0:
            render_gif("pito_hata")
        else:
            render_gif("pito_dusunuyor")

        st.markdown(f'<div class="pito-note">{curr_ex["msg"]}</div>', unsafe_allow_html=True)
        
        ans = st.text_input(f"⌨️ Görev: {curr_ex['task']}", key=f"ans_{m_idx}_{e_idx}", disabled=st.session_state.is_completed)

        if not st.session_state.is_completed:
            if st.button("Kontrol Et"):
                if not ans:
                    st.warning("⚠️ Lütfen boşluğu doldur!")
                else:
                    # Normalizasyon ile kontrol
                    correct_norm = curr_ex["solution"].replace(" ", "").replace("'","").replace('"',"")
                    ans_norm = ans.replace(" ", "").replace("'","").replace('"',"")
                    
                    if ans_norm in correct_norm or correct_norm in ans_norm:
                        st.session_state.is_completed = True
                        u["Puan"] += st.session_state.score_pool
                        st.rerun()
                    else:
                        st.session_state.errors += 1
                        st.session_state.score_pool -= 5
                        if st.session_state.errors == 3: st.warning(f"💡 İpucu: {curr_ex['hint']}")
                        elif st.session_state.errors >= 4:
                            st.session_state.is_completed = True
                            st.rerun()

        if st.session_state.is_completed:
            st.divider()
            if st.session_state.errors >= 4:
                st.error(f"🚨 4 hata yaptın. Puan kazanamadın. Çözümü incele: `{curr_ex['solution']}`")
            else:
                st.success(f"✨ Harika! +{st.session_state.score_pool} Puan Kazandın.")
                out = curr_ex['solution'].replace("print(", "").replace(")", "").replace("'", "").replace('"', "")
                st.code(f"Kod Çıktısı:\n{out}")

            if st.button("Sonraki Adıma Geç ➡️"):
                if e_idx < 4: u["Mevcut Egzersiz"] += 1
                else:
                    u["Mevcut Modül"] += 1
                    u["Mevcut Egzersiz"] = 1
                    st.balloons()
                st.session_state.is_completed = False
                st.session_state.errors = 0
                st.session_state.score_pool = 20
                st.rerun()

    with c_side:
        st.subheader(f"👤 {u['Ad']}")
        st.metric("Puan", u["Puan"])
        st.write(f"**Rütbe:** {get_rank(u['Puan'])}")
        st.divider()
        show_leaderboard()
