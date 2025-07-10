import tkinter as tk
from tkinter import messagebox, filedialog
from tkcalendar import DateEntry
from PIL import Image, ImageTk
import os
import pyodbc
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from datetime import datetime, timedelta
import json

# SQL Bağlantısı
def get_connection():
    return pyodbc.connect(
        "DRIVER={ODBC Driver 17 for SQL Server};"
        "SERVER=BURAK;"
        "DATABASE=WhiteStoneCoffe;"
        "Trusted_Connection=yes;"
    )

# Veritabanından verileri çek
def verileri_getir(baslangic, bitis, filtre):
    conn = get_connection()
    cursor = conn.cursor()

    if filtre == "Gelir":
        query = """
            SELECT ISLEMTURU, TUTAR, Tarih
            FROM GelirGider
            WHERE Tarih BETWEEN ? AND ? AND ISLEMTURU = 'Gelir'
        """
    elif filtre == "Gider":
        query = """
            SELECT ISLEMTURU, TUTAR, Tarih
            FROM GelirGider
            WHERE Tarih BETWEEN ? AND ? AND ISLEMTURU = 'Gider'
        """
    else:
        query = """
            SELECT ISLEMTURU, TUTAR, Tarih
            FROM GelirGider
            WHERE Tarih BETWEEN ? AND ?
        """

    cursor.execute(query, (baslangic, bitis))
    return cursor.fetchall()

# Raporlama işlemi
def raporlama_yap():
    baslangic = tarih1.get_date()
    bitis = tarih2.get_date()
    filtre = filtre_var.get()
    veriler = verileri_getir(baslangic, bitis, filtre)

    if not veriler:
        messagebox.showinfo("Bilgi", "Seçilen tarihler arasında veri bulunamadı.")
        return

    gunler = list(sorted(set(v[2] for v in veriler)))
    gelir_dict = {g: 0 for g in gunler}
    gider_dict = {g: 0 for g in gunler}

    toplam_gelir = 0
    toplam_gider = 0

    for islem, tutar, tarih in veriler:
        if islem.lower() == "gelir":
            gelir_dict[tarih] += float(tutar)
            toplam_gelir += float(tutar)
        else:
            gider_dict[tarih] += float(tutar)
            toplam_gider += float(tutar)

    kar = toplam_gelir - toplam_gider

    ax.clear()
    if filtre in ("Tümü", "Gelir"):
        ax.plot(gunler, [gelir_dict[g] for g in gunler], label="Gelir", color="green", marker="o")
    if filtre in ("Tümü", "Gider"):
        ax.plot(gunler, [gider_dict[g] for g in gunler], label="Gider", color="orange", marker="o")

    ax.set_title("Satış ve Gider Trendi")
    ax.set_ylabel("₺")
    ax.set_xlabel("Tarih")
    ax.legend()
    ax.grid(True)
    ax.set_xticks(gunler)
    ax.set_xticklabels([g.strftime('%d.%m') for g in gunler], rotation=45)

    canvas.draw()

    # Kar/zarar gösterimi
    sonuc_yazi = f"📊 Toplam Gelir: {toplam_gelir:.2f} ₺\n📉 Toplam Gider: {toplam_gider:.2f} ₺\n"
    if kar >= 0:
        sonuc_yazi += f"💰 Toplam Kar: {kar:.2f} ₺"
    else:
        sonuc_yazi += f"💸 Toplam Zarar: {-kar:.2f} ₺"
    lbl_sonuc.config(text=sonuc_yazi, fg="green" if kar >= 0 else "red")

    # 🔽 Raporu Kaydet
    kayit_zamani = datetime.now().strftime("%Y-%m-%d_%H-%M")
    klasor = os.path.abspath("raporlar")
    os.makedirs(klasor, exist_ok=True)

    # TXT kaydet
    txt_yol = os.path.join(klasor, f"rapor_{kayit_zamani}.txt")
    with open(txt_yol, "w", encoding="utf-8") as f:
        f.write(f"Başlangıç Tarihi: {baslangic.strftime('%d.%m.%Y')}\n")
        f.write(f"Bitiş Tarihi: {bitis.strftime('%d.%m.%Y')}\n")
        f.write(f"İşlem Türü: {filtre}\n")
        f.write(f"Toplam Gelir: {toplam_gelir:.2f} ₺\n")
        f.write(f"Toplam Gider: {toplam_gider:.2f} ₺\n")
        f.write(f"{'Toplam Kar' if kar >= 0 else 'Toplam Zarar'}: {abs(kar):.2f} ₺\n")

    # JSON kaydet
    json_yol = os.path.join(klasor, f"rapor_{kayit_zamani}.json")
    with open(json_yol, "w", encoding="utf-8") as jf:
        json.dump({
            "baslangic": baslangic.strftime("%Y-%m-%d"),
            "bitis": bitis.strftime("%Y-%m-%d"),
            "filtre": filtre,
            "gelir": toplam_gelir,
            "gider": toplam_gider,
            "kar": kar
        }, jf, indent=4, ensure_ascii=False)

# Ana pencere
pencere = tk.Tk()
pencere.title("Raporlama Ekranı")
pencere.geometry("1000x720")
pencere.resizable(False, False)

# Arka plan görseli
try:
    bg_path = os.path.join("assets", "bg_kahve.jpg")
    bg_image = Image.open(bg_path)
    bg_image = bg_image.resize((1000, 720))
    bg_photo = ImageTk.PhotoImage(bg_image)
    bg_label = tk.Label(pencere, image=bg_photo)
    bg_label.place(x=0, y=0, relwidth=1, relheight=1)
except Exception as e:
    print("Arka plan yüklenemedi:", e)
    pencere.configure(bg="#f5f5f5")

# Tarih ve filtre alanı
frame_tarih = tk.Frame(pencere, bg="#ffffff")
frame_tarih.place(relx=0.5, rely=0.05, anchor="n")

lbl1 = tk.Label(frame_tarih, text="Başlangıç Tarihi:", bg="white")
lbl1.grid(row=0, column=0, padx=5)
tarih1 = DateEntry(frame_tarih, date_pattern="dd.MM.yyyy")
tarih1.grid(row=0, column=1, padx=5)

lbl2 = tk.Label(frame_tarih, text="Bitiş Tarihi:", bg="white")
lbl2.grid(row=0, column=2, padx=5)
tarih2 = DateEntry(frame_tarih, date_pattern="dd.MM.yyyy")
tarih2.grid(row=0, column=3, padx=5)

# Filtre butonları
filtre_var = tk.StringVar(value="Tümü")
tk.Radiobutton(frame_tarih, text="Tümü", variable=filtre_var, value="Tümü", bg="white").grid(row=1, column=0, pady=5)
tk.Radiobutton(frame_tarih, text="Sadece Gelir", variable=filtre_var, value="Gelir", bg="white").grid(row=1, column=1)
tk.Radiobutton(frame_tarih, text="Sadece Gider", variable=filtre_var, value="Gider", bg="white").grid(row=1, column=2)

# Buton
btn_rapor = tk.Button(pencere, text="Raporla", bg="green", fg="white", font=("Arial", 12), command=raporlama_yap)
btn_rapor.place(relx=0.5, rely=0.2, anchor="n")

# Grafik alanı
fig, ax = plt.subplots(figsize=(9, 4))
canvas = FigureCanvasTkAgg(fig, master=pencere)
canvas.get_tk_widget().place(relx=0.5, rely=0.32, anchor="n")

# Sonuç metni
lbl_sonuc = tk.Label(pencere, text="", font=("Arial", 12, "bold"), bg="#ffffff")
lbl_sonuc.place(relx=0.5, rely=0.9, anchor="center")

pencere.mainloop()
