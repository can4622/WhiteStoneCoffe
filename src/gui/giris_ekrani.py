import tkinter as tk
from tkinter import messagebox

try:
    from PIL import Image, ImageTk
except ImportError:
    messagebox.showerror("Modül Hatası", "Pillow (PIL) modülü yüklü değil. Terminalde 'pip install pillow' komutunu çalıştırın.")
    raise

import os
import sys
import hashlib
import pyodbc
import subprocess

# Veritabanı bağlantısı
def get_connection():
    return pyodbc.connect(
        "DRIVER={ODBC Driver 17 for SQL Server};"
        "SERVER=BURAK;"
        "DATABASE=WhiteStoneCoffe;"
        "Trusted_Connection=yes;"
    )

# Şifre hashleme fonksiyonu
def sifre_hashle(sifre):
    return hashlib.sha256(sifre.encode()).hexdigest()

# Giriş işlemi
def giris_yap():
    kullanici = entry_kullanici.get()
    sifre = entry_sifre.get()
    hashli = sifre_hashle(sifre)

    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Kullanicilar WHERE KullaniciAdi = ? AND Sifre = ?", (kullanici, hashli))
        sonuc = cursor.fetchone()

        if sonuc:
            messagebox.showinfo("Giriş Başarılı", f"Hoş geldiniz, {kullanici}!")
            root.destroy()
            try:
                menu_path = os.path.join("src", "gui", "ana_menu.py")
                subprocess.Popen([sys.executable, os.path.abspath(menu_path)])
            except Exception as e:
                messagebox.showerror("Hata", f"Ana menü açılamadı:\n{e}")
        else:
            messagebox.showerror("Hatalı Giriş", "Kullanıcı adı veya şifre yanlış.")
    except Exception as db_error:
        messagebox.showerror("Veritabanı Hatası", f"Bağlantı hatası:\n{db_error}")

def sifreyi_goster():
    if var_goster.get():
        entry_sifre.config(show="")
    else:
        entry_sifre.config(show="*")

def sifremi_unuttum():
    try:
        subprocess.Popen([sys.executable, os.path.abspath("src/gui/şifre_sıfırla.py")])
    except Exception as e:
        messagebox.showerror("Hata", f"Şifre sıfırlama ekranı açılamadı:\n{e}")

# Ana pencere
root = tk.Tk()
root.title("White Stone Cafe Giriş")
root.geometry("500x500")
root.resizable(False, False)

# BooleanVar root oluşturulduktan sonra tanımlanmalı
var_goster = tk.BooleanVar()

# Arka plan rengi
root.configure(bg="#ffffff")

# Başlık yazısı
baslik_label = tk.Label(root, text="WHITE STONE CAFE", font=("Arial", 20), bg="#ffffff")
baslik_label.pack(pady=30)

# Giriş paneli
frame = tk.Frame(root, padx=20, pady=20, bg="#f4f4f4", bd=2, relief="ridge")
frame.pack(pady=10)

# Kullanıcı adı
tk.Label(frame, text="Kullanıcı Adı:", bg="#f4f4f4").grid(row=0, column=0, sticky="w")
entry_kullanici = tk.Entry(frame, width=30)
entry_kullanici.grid(row=0, column=1, pady=5)

# Şifre
tk.Label(frame, text="Şifre:", bg="#f4f4f4").grid(row=1, column=0, sticky="w")
entry_sifre = tk.Entry(frame, width=30, show="*")
entry_sifre.grid(row=1, column=1, pady=5)

# Şifreyi göster kutusu
tk.Checkbutton(frame, text="Şifreyi Göster", variable=var_goster, bg="#f4f4f4", command=sifreyi_goster).grid(row=2, columnspan=2, pady=5)

# Giriş butonu
tk.Button(frame, text="Giriş Yap", width=20, bg="#4CAF50", fg="white", command=giris_yap).grid(row=3, columnspan=2, pady=10)

# Şifremi unuttum
btn_unuttum = tk.Button(root, text="Şifremi Unuttum", fg="blue", bg="white", command=sifremi_unuttum, borderwidth=0)
btn_unuttum.pack(pady=5)

root.mainloop()