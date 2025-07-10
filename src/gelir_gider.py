
import tkinter as tk
from tkinter import ttk, messagebox
import pyodbc
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from decimal import Decimal

gg_pencere = None

def get_connection():
    return pyodbc.connect(
        "DRIVER={ODBC Driver 17 for SQL Server};"
        "SERVER=BURAK;"
        "DATABASE=WhiteStoneCoffe;"
        "Trusted_Connection=yes;"
    )

def gelir_gider_ekle(islem_turu, tutar, aciklama):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        tarih = datetime.now().date()
        cursor.execute("INSERT INTO GELİRGİDER (ISLEMTURU, TUTAR, Aciklama, Tarih) VALUES (?, ?, ?, ?)",
                       (islem_turu, tutar, aciklama, tarih))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        messagebox.showerror("Hata", f"İşlem eklenemedi:\n{e}")
        return False

def gelir_gider_guncelle(id_, islem_turu, tutar, aciklama):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE GELİRGİDER SET ISLEMTURU=?, TUTAR=?, Aciklama=? WHERE ID=?",
                       (islem_turu, tutar, aciklama, id_))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        messagebox.showerror("Hata", f"Güncelleme başarısız:\n{e}")
        return False

def gelir_gider_sil(id_):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM GELİRGİDER WHERE ID=?", (id_,))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        messagebox.showerror("Hata", f"Silme başarısız:\n{e}")
        return False

def gelir_gider_listele():
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT ID, ISLEMTURU, TUTAR, Aciklama, Tarih FROM GELİRGİDER ORDER BY ID DESC")
        kayitlar = cursor.fetchall()
        conn.close()
        return kayitlar
    except Exception as e:
        messagebox.showerror("Hata", f"Veriler alınamadı:\n{e}")
        return []

def toplam_rapor():
    try:
        conn = get_connection()
        cursor = conn.cursor()
        bugun = datetime.now().date()
        bir_hafta_once = bugun - timedelta(days=7)

        cursor.execute("""
            SELECT ISLEMTURU, SUM(TUTAR)
            FROM GELİRGİDER
            WHERE Tarih >= ?
            GROUP BY ISLEMTURU
        """, (bir_hafta_once,))
        veriler = cursor.fetchall()
        conn.close()

        gelir = 0
        gider = 0
        for tur, toplam in veriler:
            toplam = float(toplam)
            if tur == "Gelir":
                gelir += toplam
            else:
                gider += toplam

        kar = gelir - gider
        messagebox.showinfo("7 Günlük Özet", f"Toplam Gelir: {gelir:.2f} ₺\nToplam Gider: {gider:.2f} ₺\nKar: {kar:.2f} ₺")
    except Exception as e:
        messagebox.showerror("Hata", f"Rapor alınamadı:\n{e}")

def grafik_goster(pencere):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT MONTH(Tarih) AS Ay, ISLEMTURU, SUM(TUTAR) AS Toplam
            FROM GELİRGİDER
            GROUP BY MONTH(Tarih), ISLEMTURU
            ORDER BY Ay
        """)
        veriler = cursor.fetchall()
        conn.close()

        aylar = list(range(1, 13))
        gelirler = [0] * 12
        giderler = [0] * 12

        for v in veriler:
            ay, tur, toplam = v
            toplam = float(toplam)
            if tur == "Gelir":
                gelirler[ay - 1] = toplam
            elif tur == "Gider":
                giderler[ay - 1] = toplam

        fig, ax = plt.subplots(figsize=(6, 4))
        ax.bar(aylar, gelirler, label="Gelir", color="green")
        ax.bar(aylar, giderler, label="Gider", bottom=gelirler, color="red")
        ax.set_title("Aylık Gelir - Gider")
        ax.set_xlabel("Ay")
        ax.set_ylabel("₺ Tutar")
        ax.legend()
        ax.set_xticks(aylar)

        pencere_grafik = tk.Toplevel(pencere)
        pencere_grafik.title("Aylık Gelir-Gider Grafiği")
        canvas = FigureCanvasTkAgg(fig, master=pencere_grafik)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
    except Exception as e:
        messagebox.showerror("Hata", f"Grafik yüklenemedi:\n{e}")

def gelir_gider_ekrani():
    global gg_pencere
    if gg_pencere and gg_pencere.winfo_exists():
        gg_pencere.lift()
        return

    gg_pencere = tk.Tk()
    gg_pencere.title("Gelir - Gider Yönetimi")
    gg_pencere.geometry("900x600")
    gg_pencere.configure(bg="#2d3436")

    tk.Label(gg_pencere, text="Gelir - Gider İşlemleri", font=("Arial", 16, "bold"),
             bg="#2d3436", fg="white").pack(pady=10)

    kolonlar = ("ID", "Tür", "Tutar", "Açıklama", "Tarih")
    tree = ttk.Treeview(gg_pencere, columns=kolonlar, show="headings")
    for col in kolonlar:
        tree.heading(col, text=col)
        tree.column(col, anchor="center", width=120)
    tree.pack(fill="both", expand=True, padx=20, pady=10)

    def tabloyu_yenile():
        for i in tree.get_children():
            tree.delete(i)
        for v in gelir_gider_listele():
            tree.insert("", "end", values=(v.ID, v.ISLEMTURU, f"{v.TUTAR:.2f} ₺", v.Aciklama, v.Tarih))

    
    # Tarih filtresi alanı
    filtre_frame = tk.Frame(gg_pencere, bg="#2d3436")
    filtre_frame.pack(pady=5)

    tk.Label(filtre_frame, text="Başlangıç Tarihi:", bg="#2d3436", fg="white").grid(row=0, column=0, padx=5)
    baslangic_entry = tk.Entry(filtre_frame)
    baslangic_entry.grid(row=0, column=1, padx=5)

    tk.Label(filtre_frame, text="Bitiş Tarihi:", bg="#2d3436", fg="white").grid(row=0, column=2, padx=5)
    bitis_entry = tk.Entry(filtre_frame)
    bitis_entry.grid(row=0, column=3, padx=5)

    def filtrele():
        for i in tree.get_children():
            tree.delete(i)
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT ID, ISLEMTURU, TUTAR, Aciklama, Tarih FROM GELİRGİDER WHERE Tarih BETWEEN ? AND ? ORDER BY Tarih DESC",
                           (baslangic_entry.get(), bitis_entry.get()))
            veriler = cursor.fetchall()
            conn.close()
            for v in veriler:
                tree.insert("", "end", values=(v.ID, v.ISLEMTURU, f"{v.TUTAR:.2f} ₺", v.Aciklama, v.Tarih))
        except Exception as e:
            messagebox.showerror("Hata", f"Filtre uygulanamadı:\n{e}")

    tk.Button(filtre_frame, text="Filtrele", command=filtrele).grid(row=0, column=4, padx=10)

    form = tk.Frame(gg_pencere, bg="#2d3436")
    form.pack(pady=10)

    ttk.Label(form, text="Tür:").grid(row=0, column=0, padx=5)
    tur_var = ttk.Combobox(form, values=["Gelir", "Gider"], state="readonly", width=10)
    tur_var.grid(row=0, column=1, padx=5)

    ttk.Label(form, text="Tutar:").grid(row=0, column=2, padx=5)
    tutar_entry = tk.Entry(form, width=10)
    tutar_entry.grid(row=0, column=3, padx=5)

    ttk.Label(form, text="Açıklama:").grid(row=0, column=4, padx=5)
    aciklama_entry = tk.Entry(form, width=30)
    aciklama_entry.grid(row=0, column=5, padx=5)

    def ekle():
        tur = tur_var.get()
        try:
            tutar = float(tutar_entry.get())
        except:
            messagebox.showwarning("Uyarı", "Tutar sayı olmalı.")
            return
        aciklama = aciklama_entry.get().strip()
        if not tur or not aciklama or tutar <= 0:
            messagebox.showwarning("Uyarı", "Tüm alanları doldur.")
            return
        if gelir_gider_ekle(tur, tutar, aciklama):
            messagebox.showinfo("Başarılı", "Kayıt eklendi.")
            tur_var.set("")
            tutar_entry.delete(0, "end")
            aciklama_entry.delete(0, "end")
            tabloyu_yenile()

    def sil():
        secili = tree.selection()
        if not secili:
            messagebox.showwarning("Uyarı", "Lütfen silinecek satırı seçin.")
            return
        secilen_id = tree.item(secili[0])["values"][0]
        if messagebox.askyesno("Onay", "Bu kaydı silmek istediğinize emin misiniz?"):
            if gelir_gider_sil(secilen_id):
                messagebox.showinfo("Başarılı", "Kayıt silindi.")
                tabloyu_yenile()

    def guncelle():
        secili = tree.selection()
        if not secili:
            messagebox.showwarning("Uyarı", "Lütfen güncellenecek satırı seçin.")
            return
        secilen = tree.item(secili[0])["values"]
        id_ = secilen[0]
        yeni_tur = tur_var.get()
        try:
            yeni_tutar = float(tutar_entry.get())
        except:
            messagebox.showerror("Hata", "Tutar sayı olmalı.")
            return
        yeni_aciklama = aciklama_entry.get().strip()
        if not yeni_tur or not yeni_aciklama:
            messagebox.showwarning("Uyarı", "Alanlar boş olamaz.")
            return
        if gelir_gider_guncelle(id_, yeni_tur, yeni_tutar, yeni_aciklama):
            messagebox.showinfo("Başarılı", "Kayıt güncellendi.")
            tabloyu_yenile()

    ttk.Button(form, text="Ekle", command=ekle).grid(row=0, column=6, padx=10)
    ttk.Button(form, text="Sil", command=sil).grid(row=0, column=7, padx=10)
    ttk.Button(form, text="Güncelle", command=guncelle).grid(row=0, column=8, padx=10)

    # Ekstra butonlar
    tk.Button(gg_pencere, text="Aylık Grafik", command=lambda: grafik_goster(gg_pencere), bg="#6c5ce7", fg="white").pack(pady=5)
    tk.Button(gg_pencere, text="7 Günlük Rapor", command=toplam_rapor, bg="#00cec9", fg="white").pack(pady=5)

    tabloyu_yenile()
    gg_pencere.mainloop()

if __name__ == "__main__":
    gelir_gider_ekrani()
