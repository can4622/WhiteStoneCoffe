import tkinter as tk
from tkinter import messagebox
import pyodbc
import hashlib
import os

def get_connection():
    return pyodbc.connect(
        'DRIVER={ODBC Driver 17 for SQL Server};'
        'SERVER=BURAK;'
        'DATABASE=WhiteStoneCoffe;'
        'Trusted_Connection=yes;'
    )

def sifre_hashle(sifre):
    return hashlib.sha256(sifre.encode()).hexdigest()

def sifre_kontrol(sifre):
    return len(sifre) >= 8 and any(c.islower() for c in sifre) and any(c.isupper() for c in sifre)

def sifre_sifirla():
    kullanici = entry_kullanici.get()
    yeni = entry_sifre.get()
    tekrar = entry_tekrar.get()

    if yeni != tekrar:
        messagebox.showerror("Hata", "Şifreler uyuşmuyor.")
        return
    if not sifre_kontrol(yeni):
        messagebox.showerror("Hata", "Şifre en az 8 karakter olmalı, büyük ve küçük harf içermeli.")
        return

    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM [Kullanicilar] WHERE KullaniciAdi = ?", (kullanici,))
        if cursor.fetchone() is None:
            messagebox.showerror("Hata", "Kullanıcı bulunamadı.")
        else:
            hashli = sifre_hashle(yeni)
            cursor.execute("UPDATE [Kullanicilar] SET Sifre = ? WHERE KullaniciAdi = ?", (hashli, kullanici))
            conn.commit()
            messagebox.showinfo("Başarılı", "Şifre başarıyla sıfırlandı. Giriş ekranına yönlendiriliyorsunuz.")
            root.destroy()
            try:
                giris_ekrani_yolu = os.path.abspath("src/gui/giris_ekrani.py")
                os.startfile(giris_ekrani_yolu)
            except Exception as e:
                messagebox.showerror("Hata", f"Giriş ekranı açılamadı:\n{e}")
    except Exception as e:
        messagebox.showerror("Veritabanı Hatası", str(e))

# GUI
root = tk.Tk()
root.title("Şifre Sıfırlama")
root.geometry("400x300")
root.configure(bg="white")

tk.Label(root, text="Kullanıcı Adı:", bg="white").pack(pady=5)
entry_kullanici = tk.Entry(root, width=30)
entry_kullanici.pack(pady=5)

tk.Label(root, text="Yeni Şifre:", bg="white").pack(pady=5)
entry_sifre = tk.Entry(root, width=30, show="*")
entry_sifre.pack(pady=5)

tk.Label(root, text="Yeni Şifre Tekrar:", bg="white").pack(pady=5)
entry_tekrar = tk.Entry(root, width=30, show="*")
entry_tekrar.pack(pady=5)

tk.Button(root, text="Şifreyi Sıfırla", command=sifre_sifirla, bg="#2196F3", fg="white").pack(pady=20)

root.mainloop()
