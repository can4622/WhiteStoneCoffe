import tkinter as tk
from tkinter import ttk, messagebox
import pyodbc
from datetime import datetime

urun_pencere = None  # Tek pencere kontrolü için global

def get_connection():
    return pyodbc.connect(
        "DRIVER={ODBC Driver 17 for SQL Server};"
        "SERVER=BURAK;"
        "DATABASE=WhiteStoneCoffe;"
        "Trusted_Connection=yes;"
    )

def urunleri_getir():
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT URUNID, URUNAdi, Fiyat FROM urunler")
        urunler = cursor.fetchall()
        conn.close()
        return urunler
    except Exception as e:
        messagebox.showerror("Hata", f"Ürünler çekilemedi:\n{e}")
        return []

def urun_ekle(urun_adi, fiyat):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO urunler (URUNAdi, Fiyat) VALUES (?, ?)", (urun_adi, fiyat))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        messagebox.showerror("Veritabanı Hatası", f"Ürün eklenemedi:\n{e}")
        return False

def urun_guncelle(urun_id, yeni_ad, yeni_fiyat):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE urunler SET URUNAdi=?, Fiyat=? WHERE URUNID=?", (yeni_ad, yeni_fiyat, urun_id))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        messagebox.showerror("Veritabanı Hatası", f"Ürün güncellenemedi:\n{e}")
        return False

def urun_sil(urun_id):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM siparisler WHERE UrunID=?", (urun_id,))
        count = cursor.fetchone()[0]
        if count > 0:
            messagebox.showwarning("Silme Engellendi", "Bu ürüne ait siparişler olduğu için silinemez!")
            conn.close()
            return False
        cursor.execute("DELETE FROM urunler WHERE URUNID=?", (urun_id,))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        messagebox.showerror("Veritabanı Hatası", f"Ürün silinemedi:\n{e}")
        return False

def urun_yonetimi_ekrani():
    global urun_pencere, urunler, urun_adlari, urun_combo

    if urun_pencere is not None and urun_pencere.winfo_exists():
        urun_pencere.lift()
        return

    urunler = urunleri_getir()
    urun_adlari = [f"{u.URUNAdi} ({u.Fiyat}₺)" for u in urunler]

    urun_pencere = tk.Toplevel()
    urun_pencere.title("Ürün Yönetimi")
    urun_pencere.geometry("600x450")
    urun_pencere.configure(bg="#2c3e50")
    urun_pencere.protocol("WM_DELETE_WINDOW", lambda: pencereyi_kapat())

    def pencereyi_kapat():
        global urun_pencere
        urun_pencere.destroy()
        urun_pencere = None

    tk.Label(urun_pencere, text="Ürün Yönetimi", font=("Arial", 16, "bold"), fg="white", bg="#2c3e50").pack(pady=10)

    urun_combo = ttk.Combobox(urun_pencere, font=("Arial", 12), width=40, state="readonly", values=urun_adlari)
    urun_combo.pack(pady=10)

    btn_frame = tk.Frame(urun_pencere, bg="#2c3e50")
    btn_frame.pack(pady=10)

    tk.Button(btn_frame, text="Yeni Ürün Ekle", command=urun_ekle_pencere,
              bg="#27ae60", fg="white", font=("Arial", 11, "bold"), width=18).grid(row=0, column=0, padx=10)

    tk.Button(btn_frame, text="Ürünü Güncelle", command=lambda: urun_guncelle_pencere() if urun_combo.current() != -1 else messagebox.showwarning("Uyarı", "Lütfen bir ürün seçin."),
              bg="#f39c12", fg="white", font=("Arial", 11, "bold"), width=18).grid(row=0, column=1, padx=10)

    tk.Button(btn_frame, text="Ürünü Sil", command=lambda: urun_sil_pencere() if urun_combo.current() != -1 else messagebox.showwarning("Uyarı", "Lütfen bir ürün seçin."),
              bg="#c0392b", fg="white", font=("Arial", 11, "bold"), width=18).grid(row=0, column=2, padx=10)

    tree_frame = tk.Frame(urun_pencere)
    tree_frame.pack(fill="both", expand=True, padx=20, pady=10)

    kolonlar = ("ID", "Ad", "Fiyat")
    tree = ttk.Treeview(tree_frame, columns=kolonlar, show="headings", height=8)
    for col in kolonlar:
        tree.heading(col, text=col)
        tree.column(col, anchor="center", width=150)
    tree.pack(fill="both", expand=True)

    def tabloyu_doldur():
        global urunler
        urunler[:] = urunleri_getir()
        for i in tree.get_children():
            tree.delete(i)
        for u in urunler:
            tree.insert("", "end", values=(u.URUNID, u.URUNAdi, f"{u.Fiyat:.2f} ₺"))
        urun_adlari[:] = [f"{u.URUNAdi} ({u.Fiyat}₺)" for u in urunler]
        urun_combo["values"] = urun_adlari

    urun_pencere.tabloyu_doldur = tabloyu_doldur
    tabloyu_doldur()

def urun_ekle_pencere():
    global urunler, urun_adlari, urun_combo, urun_pencere

    pencere_urun = tk.Toplevel()
    pencere_urun.title("Yeni Ürün Ekle")
    pencere_urun.geometry("350x200")
    pencere_urun.configure(bg="#23272e")

    tk.Label(pencere_urun, text="Ürün Adı:", font=("Arial", 12, "bold"), fg="white", bg="#23272e").pack(pady=10)
    entry_adi = tk.Entry(pencere_urun, font=("Arial", 12), width=25)
    entry_adi.pack()

    tk.Label(pencere_urun, text="Fiyat (₺):", font=("Arial", 12, "bold"), fg="white", bg="#23272e").pack(pady=10)
    entry_fiyat = tk.Entry(pencere_urun, font=("Arial", 12), width=25)
    entry_fiyat.pack()

    def kaydet_urun():
        urun_adi = entry_adi.get().strip()
        try:
            fiyat = float(entry_fiyat.get())
        except:
            messagebox.showerror("Hata", "Fiyat sayısal olmalı.")
            return
        if not urun_adi or fiyat <= 0:
            messagebox.showwarning("Uyarı", "Tüm alanları doğru doldurun.")
            return
        if urun_ekle(urun_adi, fiyat):
            messagebox.showinfo("Başarılı", "Ürün başarıyla eklendi.")
            pencere_urun.destroy()
            urun_pencere.tabloyu_doldur()

    tk.Button(pencere_urun, text="Kaydet", command=kaydet_urun,
              bg="#1e88e5", fg="white", font=("Arial", 12, "bold"), bd=0, width=15).pack(pady=18)

def urun_guncelle_pencere():
    global urunler, urun_adlari, urun_combo, urun_pencere
    secili = urun_combo.current()
    urun = urunler[secili]

    pencere_guncelle = tk.Toplevel()
    pencere_guncelle.title("Ürün Güncelle")
    pencere_guncelle.geometry("350x200")
    pencere_guncelle.configure(bg="#23272e")

    tk.Label(pencere_guncelle, text="Ürün Adı:", font=("Arial", 12, "bold"), fg="white", bg="#23272e").pack(pady=10)
    entry_adi = tk.Entry(pencere_guncelle, font=("Arial", 12), width=25)
    entry_adi.insert(0, urun.URUNAdi)
    entry_adi.pack()

    tk.Label(pencere_guncelle, text="Fiyat (₺):", font=("Arial", 12, "bold"), fg="white", bg="#23272e").pack(pady=10)
    entry_fiyat = tk.Entry(pencere_guncelle, font=("Arial", 12), width=25)
    entry_fiyat.insert(0, urun.Fiyat)
    entry_fiyat.pack()

    def kaydet_guncelle():
        yeni_ad = entry_adi.get().strip()
        try:
            yeni_fiyat = float(entry_fiyat.get())
        except:
            messagebox.showerror("Hata", "Fiyat sayısal olmalı.")
            return
        if not yeni_ad or yeni_fiyat <= 0:
            messagebox.showwarning("Uyarı", "Tüm alanları doğru doldurun.")
            return
        if urun_guncelle(urun.URUNID, yeni_ad, yeni_fiyat):
            messagebox.showinfo("Başarılı", "Ürün güncellendi.")
            pencere_guncelle.destroy()
            urun_pencere.tabloyu_doldur()

    tk.Button(pencere_guncelle, text="Kaydet", command=kaydet_guncelle,
              bg="#ffb300", fg="white", font=("Arial", 12, "bold"), bd=0, width=15).pack(pady=18)

def urun_sil_pencere():
    global urunler, urun_adlari, urun_combo, urun_pencere
    secili = urun_combo.current()
    urun = urunler[secili]
    if messagebox.askyesno("Onay", f"{urun.URUNAdi} adlı ürünü silmek istediğinize emin misiniz?"):
        if urun_sil(urun.URUNID):
            messagebox.showinfo("Başarılı", "Ürün silindi.")
            urun_pencere.tabloyu_doldur()
