import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import os
import sys

# Kök dizini import'a dahil et
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from src.urunler import urun_yonetimi_ekrani
from src.gelir_gider import gelir_gider_ekrani

def urun_yonetimi():
    try:
        urun_yonetimi_ekrani()
    except Exception as e:
        messagebox.showerror("Hata", f"Ürün yönetimi ekranı açılamadı:\n{e}")

def siparis_yonetimi():
    import subprocess
    subprocess.Popen([sys.executable, os.path.abspath("src/siparişler.py")])

def gelir_gider():
    try:
        gelir_gider_ekrani()
    except Exception as e:
        messagebox.showerror("Hata", f"Gelir-Gider ekranı açılamadı:\n{e}")

def raporlama():
    import subprocess
    subprocess.Popen([sys.executable, os.path.abspath("src/gui/raporlama.py")])

def gecmis_raporlar():
    import subprocess
    subprocess.Popen([sys.executable, os.path.abspath("src/gui/geçmiş_raporlar.py")])

def cikis():
    pencere.destroy()

# === ANA PENCERE
pencere = tk.Tk()
pencere.title("White Stone Cafe | Ana Menü")
pencere.geometry("600x500")
pencere.resizable(False, False)

# === ARKA PLAN
bg_path = os.path.abspath("assets/bg.jpg")
try:
    bg_img = Image.open(bg_path)
    bg_img = bg_img.resize((600, 500))
    bg_photo = ImageTk.PhotoImage(bg_img)
    bg_label = tk.Label(pencere, image=bg_photo)
    bg_label.image = bg_photo  # Referans kaybolmasın!
    bg_label.place(x=0, y=0, relwidth=1, relheight=1)
except Exception as e:
    pencere.configure(bg="#fdf6f0")
    messagebox.showerror("Arka Plan Hatası", f"Görsel yüklenemedi:\n{e}")

# === BAŞLIK
baslik = tk.Label(pencere, text="WHITE STONE CAFE", font=("Helvetica", 24, "bold"), fg="#4e342e", bg="white")
baslik.place(relx=0.5, y=40, anchor="center")

# === BUTON STİLİ
buton_stil = {"font": ("Arial", 14), "width": 20, "bg": "#6d4c41", "fg": "white", "bd": 0, "highlightthickness": 0}

# === BUTONLAR
tk.Button(pencere, text="Ürün Yönetimi", command=urun_yonetimi, **buton_stil).place(relx=0.5, y=110, anchor="center")
tk.Button(pencere, text="Siparişler", command=siparis_yonetimi, **buton_stil).place(relx=0.5, y=160, anchor="center")
tk.Button(pencere, text="Gelir - Gider", command=gelir_gider, **buton_stil).place(relx=0.5, y=210, anchor="center")
tk.Button(pencere, text="Raporlama", command=raporlama, **buton_stil).place(relx=0.5, y=260, anchor="center")
tk.Button(pencere, text="Geçmiş Raporlar", command=gecmis_raporlar, **buton_stil).place(relx=0.5, y=310, anchor="center")
tk.Button(pencere, text="Çıkış Yap", command=cikis, **buton_stil).place(relx=0.5, y=380, anchor="center")

# === BAŞLAT
pencere.mainloop()