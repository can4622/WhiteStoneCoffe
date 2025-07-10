import tkinter as tk
from tkinter import messagebox
import os

def rapor_goster(dosya):
    try:
        with open(os.path.abspath(f"raporlar/{dosya}"), "r", encoding="utf-8") as f:
            icerik = f.read()

        goster_pencere = tk.Toplevel()
        goster_pencere.title(dosya)
        goster_pencere.geometry("500x400")

        text = tk.Text(goster_pencere, wrap="word")
        text.insert("1.0", icerik)
        text.config(state="disabled")
        text.pack(expand=True, fill="both")
    except Exception as e:
        messagebox.showerror("Hata", f"Rapor gösterilemedi:\n{e}")

def rapor_sil(dosya):
    yol = os.path.abspath(f"raporlar/{dosya}")
    if os.path.exists(yol):
        os.remove(yol)
        listele()
    else:
        messagebox.showerror("Hata", "Dosya bulunamadı.")

def listele(*args):
    arama = entry_ara.get().lower()
    listebox.delete(0, tk.END)
    try:
        dosyalar = os.listdir("raporlar")
        for dosya in dosyalar:
            if dosya.lower().endswith(".txt") and arama in dosya.lower():
                listebox.insert(tk.END, dosya)
    except Exception as e:
        messagebox.showerror("Hata", f"Klasör okunamadı:\n{e}")

def secileni_goster():
    secim = listebox.curselection()
    if secim:
        dosya = listebox.get(secim[0])
        rapor_goster(dosya)

def secileni_sil():
    secim = listebox.curselection()
    if secim:
        dosya = listebox.get(secim[0])
        onay = messagebox.askyesno("Onay", f"{dosya} silinsin mi?")
        if onay:
            rapor_sil(dosya)

# Arayüz
pencere = tk.Tk()
pencere.title("Geçmiş Raporlar")
pencere.geometry("500x500")

entry_ara = tk.Entry(pencere, width=40)
entry_ara.pack(pady=10)
entry_ara.bind("<KeyRelease>", listele)

listebox = tk.Listbox(pencere, width=60, height=20)
listebox.pack(pady=5)

btn_goster = tk.Button(pencere, text="Raporu Görüntüle", command=secileni_goster)
btn_goster.pack(pady=5)

btn_sil = tk.Button(pencere, text="Raporu Sil", command=secileni_sil, fg="white", bg="red")
btn_sil.pack(pady=5)

listele()
pencere.mainloop()
