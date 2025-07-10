import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import pyodbc
import pandas as pd
import matplotlib.pyplot as plt
from tkcalendar import DateEntry
from datetime import datetime

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

def urun_ekle_pencere():
    global urunler, urun_adlari, urun_combo

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
            urunler[:] = urunleri_getir()
            urun_adlari[:] = [f"{u.URUNAdi} ({u.Fiyat}₺)" for u in urunler]
            urun_combo["values"] = urun_adlari

    tk.Button(pencere_urun, text="Kaydet", command=kaydet_urun, bg="#1e88e5", fg="white", font=("Arial", 12, "bold"), bd=0, width=15).pack(pady=18)

def urun_guncelle_pencere():
    global urunler, urun_adlari, urun_combo
    secili = urun_combo.current()
    if secili == -1:
        messagebox.showwarning("Uyarı", "Lütfen bir ürün seçin.")
        return
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
            urunler[:] = urunleri_getir()
            urun_adlari[:] = [f"{u.URUNAdi} ({u.Fiyat}₺)" for u in urunler]
            urun_combo["values"] = urun_adlari
            urun_combo.set("")
    tk.Button(pencere_guncelle, text="Kaydet", command=kaydet_guncelle, bg="#ffb300", fg="white", font=("Arial", 12, "bold"), bd=0, width=15).pack(pady=18)

def urun_sil_pencere():
    global urunler, urun_adlari, urun_combo
    secili = urun_combo.current()
    if secili == -1:
        messagebox.showwarning("Uyarı", "Lütfen bir ürün seçin.")
        return
    urun = urunler[secili]
    if messagebox.askyesno("Onay", f"{urun.URUNAdi} adlı ürünü silmek istediğinize emin misiniz?"):
        if urun_sil(urun.URUNID):
            messagebox.showinfo("Başarılı", "Ürün silindi.")
            urunler[:] = urunleri_getir()
            urun_adlari[:] = [f"{u.URUNAdi} ({u.Fiyat}₺)" for u in urunler]
            urun_combo["values"] = urun_adlari
            urun_combo.set("")

def siparis_ekle(urun_id, miktar, toplam_tutar, aciklama):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO siparisler (UrunID, Miktar, ToplamTutar, Aciklama, SiparisTarihi)
            VALUES (?, ?, ?, ?, ?)
        """, (urun_id, miktar, toplam_tutar, aciklama, datetime.now()))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        messagebox.showerror("Veritabanı Hatası", f"Sipariş eklenemedi:\n{e}")
        return False

def siparisleri_listele(aranan="", tarih1=None, tarih2=None):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        query = """
            SELECT s.SiparisID, u.URUNAdi, s.Miktar, s.ToplamTutar, s.Aciklama, s.SiparisTarihi
            FROM siparisler s
            JOIN urunler u ON s.UrunID = u.URUNID
        """
        params = []
        where = []
        if aranan:
            where.append("u.URUNAdi LIKE ?")
            params.append('%' + aranan + '%')
        if tarih1 and tarih2:
            where.append("s.SiparisTarihi BETWEEN ? AND ?")
            params.extend([tarih1, tarih2])
        if where:
            query += " WHERE " + " AND ".join(where)
        query += " ORDER BY s.SiparisID DESC"
        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()
        return rows
    except Exception as e:
        messagebox.showerror("Veritabanı Hatası", f"Siparişler listelenemedi:\n{e}")
        return []

def toplam_satis_ozet(tarih1=None, tarih2=None):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        if tarih1 and tarih2:
            cursor.execute("""
                SELECT COUNT(*), SUM(ToplamTutar) FROM siparisler
                WHERE SiparisTarihi BETWEEN ? AND ?
            """, (tarih1, tarih2))
        else:
            cursor.execute("SELECT COUNT(*), SUM(ToplamTutar) FROM siparisler")
        adet, toplam = cursor.fetchone()
        conn.close()
        return adet or 0, toplam or 0
    except:
        return 0, 0

def siparis_guncelle(siparis_id, urun_id, miktar, toplam_tutar, aciklama):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE siparisler
            SET UrunID=?, Miktar=?, ToplamTutar=?, Aciklama=?
            WHERE SiparisID=?
        """, (urun_id, miktar, toplam_tutar, aciklama, siparis_id))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        messagebox.showerror("Veritabanı Hatası", f"Güncelleme başarısız:\n{e}")
        return False

def siparis_sil(siparis_id):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM siparisler WHERE SiparisID=?", (siparis_id,))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        messagebox.showerror("Veritabanı Hatası", f"Silme başarısız:\n{e}")
        return False

def tabloyu_excele_aktar(siparisler):
    try:
        df = pd.DataFrame(siparisler, columns=["ID", "Ürün", "Miktar", "Tutar", "Açıklama", "Tarih"])
        dosya = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel Dosyası", "*.xlsx")])
        if dosya:
            df.to_excel(dosya, index=False)
            messagebox.showinfo("Başarılı", f"Excel olarak kaydedildi:\n{dosya}")
    except Exception as e:
        messagebox.showerror("Hata", f"Excel aktarım hatası:\n{e}")

def en_cok_siparis_urun_grafik():
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT u.URUNAdi, SUM(s.Miktar) as Toplam
            FROM siparisler s
            JOIN urunler u ON s.UrunID = u.URUNID
            GROUP BY u.URUNAdi
            ORDER BY Toplam DESC
        """)
        data = cursor.fetchall()
        conn.close()
        if not data:
            messagebox.showinfo("Bilgi", "Grafik için yeterli veri yok.")
            return
        urunler = [row.URUNAdi for row in data]
        miktarlar = [row.Toplam for row in data]
        plt.figure(figsize=(8,5))
        plt.bar(urunler, miktarlar, color="#1e88e5")
        plt.title("En Çok Sipariş Edilen Ürünler")
        plt.xlabel("Ürün")
        plt.ylabel("Toplam Sipariş")
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.show()
    except Exception as e:
        messagebox.showerror("Hata", f"Grafik oluşturulamadı:\n{e}")

def aylik_satis_grafik():
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT FORMAT(SiparisTarihi, 'yyyy-MM') as Ay, SUM(ToplamTutar) as Toplam
            FROM siparisler
            GROUP BY FORMAT(SiparisTarihi, 'yyyy-MM')
            ORDER BY Ay
        """)
        data = cursor.fetchall()
        conn.close()
        if not data:
            messagebox.showinfo("Bilgi", "Grafik için yeterli veri yok.")
            return
        aylar = [row.Ay for row in data]
        tutarlar = [row.Toplam for row in data]
        plt.figure(figsize=(8,5))
        plt.plot(aylar, tutarlar, marker="o", color="#43a047")
        plt.title("Aylık Satış Grafiği")
        plt.xlabel("Ay")
        plt.ylabel("Toplam Satış (₺)")
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.show()
    except Exception as e:
        messagebox.showerror("Hata", f"Grafik oluşturulamadı:\n{e}")

def ana_ekran():
    global urunler, urun_adlari, urun_combo

    pencere = tk.Tk()
    pencere.title("Sipariş Yönetimi")
    pencere.geometry("1100x700")
    pencere.configure(bg="#23272e")

    style = ttk.Style()
    style.theme_use("clam")
    style.configure("Treeview", background="#23272e", foreground="white", fieldbackground="#23272e", rowheight=28, font=("Arial", 12))
    style.configure("Treeview.Heading", background="#1e88e5", foreground="white", font=("Arial", 13, "bold"))
    style.map("Treeview", background=[("selected", "#1565c0")])

    buton_stil = {"font": ("Arial", 12, "bold"), "bg": "#1e88e5", "fg": "white", "activebackground": "#1565c0", "activeforeground": "white", "bd": 0, "highlightthickness": 0}

    urunler = urunleri_getir()
    urun_adlari = [f"{u.URUNAdi} ({u.Fiyat}₺)" for u in urunler]

    frame_ozet = tk.Frame(pencere, bg="#23272e")
    frame_ozet.pack(pady=(10, 0))
    lbl_ozet = tk.Label(frame_ozet, text="", font=("Arial", 13, "bold"), fg="#43a047", bg="#23272e")
    lbl_ozet.pack()

    frame_ara = tk.Frame(pencere, bg="#23272e")
    frame_ara.pack(pady=5)
    tk.Label(frame_ara, text="Başlangıç Tarihi:", font=("Arial", 12, "bold"), fg="white", bg="#23272e").pack(side="left", padx=2)
    entry_tarih1 = DateEntry(frame_ara, width=12, font=("Arial", 12), date_pattern="yyyy-mm-dd", locale="tr_TR")
    entry_tarih1.pack(side="left", padx=2)
    tk.Label(frame_ara, text="Bitiş Tarihi:", font=("Arial", 12, "bold"), fg="white", bg="#23272e").pack(side="left", padx=2)
    entry_tarih2 = DateEntry(frame_ara, width=12, font=("Arial", 12), date_pattern="yyyy-mm-dd", locale="tr_TR")
    entry_tarih2.pack(side="left", padx=2)
    tk.Label(frame_ara, text="Ürün Ara:", font=("Arial", 12, "bold"), fg="white", bg="#23272e").pack(side="left", padx=5)
    entry_ara = tk.Entry(frame_ara, font=("Arial", 12), width=20)
    entry_ara.pack(side="left", padx=5)
    def ara():
        tarih1 = entry_tarih1.get_date()
        tarih2 = entry_tarih2.get_date()
        siparisleri_goster(entry_ara.get(), tarih1, tarih2)
    tk.Button(frame_ara, text="🔍 Ara", command=ara, bg="#43a047", fg="white", activebackground="#2e7031", activeforeground="white", font=("Arial", 12, "bold"), bd=0, width=8).pack(side="left", padx=5)
    tk.Button(frame_ara, text="Tümünü Göster", command=lambda: siparisleri_goster(), bg="#757575", fg="white", activebackground="#616161", activeforeground="white", font=("Arial", 12, "bold"), bd=0, width=13).pack(side="left", padx=5)

    frame_urun = tk.Frame(pencere, bg="#23272e")
    frame_urun.pack(pady=(5, 0))
    tk.Button(frame_urun, text="➕ Yeni Ürün Ekle", command=urun_ekle_pencere, bg="#43a047", fg="white", font=("Arial", 12, "bold"), bd=0, width=18).pack(side="left", padx=5)
    tk.Button(frame_urun, text="✏️ Ürün Güncelle", command=urun_guncelle_pencere, bg="#ffb300", fg="white", font=("Arial", 12, "bold"), bd=0, width=18).pack(side="left", padx=5)
    tk.Button(frame_urun, text="🗑️ Ürün Sil", command=urun_sil_pencere, bg="#e53935", fg="white", font=("Arial", 12, "bold"), bd=0, width=18).pack(side="left", padx=5)

    frame_ekle = tk.Frame(pencere, bg="#23272e")
    frame_ekle.pack(pady=15)

    tk.Label(frame_ekle, text="Ürün", font=("Arial", 13, "bold"), fg="white", bg="#23272e").grid(row=0, column=0, padx=8, pady=5, sticky="w")
    urun_combo = ttk.Combobox(frame_ekle, values=urun_adlari, font=("Arial", 12), width=25, state="readonly")
    urun_combo.grid(row=0, column=1, padx=8, pady=5)

    tk.Label(frame_ekle, text="Miktar", font=("Arial", 13, "bold"), fg="white", bg="#23272e").grid(row=0, column=2, padx=8, pady=5, sticky="w")
    entry_miktar = tk.Entry(frame_ekle, font=("Arial", 12), width=10)
    entry_miktar.grid(row=0, column=3, padx=8, pady=5)

    tk.Label(frame_ekle, text="Toplam Tutar", font=("Arial", 13, "bold"), fg="white", bg="#23272e").grid(row=0, column=4, padx=8, pady=5, sticky="w")
    entry_tutar = tk.Entry(frame_ekle, font=("Arial", 12), width=12, state="readonly")
    entry_tutar.grid(row=0, column=5, padx=8, pady=5)

    tk.Label(frame_ekle, text="Açıklama", font=("Arial", 13, "bold"), fg="white", bg="#23272e").grid(row=0, column=6, padx=8, pady=5, sticky="w")
    entry_aciklama = tk.Entry(frame_ekle, font=("Arial", 12), width=25)
    entry_aciklama.grid(row=0, column=7, padx=8, pady=5)

    def tutar_hesapla(event=None):
        try:
            secilen = urun_combo.current()
            if secilen == -1:
                entry_tutar.config(state="normal")
                entry_tutar.delete(0, tk.END)
                entry_tutar.config(state="readonly")
                return
            fiyat = urunler[secilen].Fiyat
            miktar = int(entry_miktar.get())
            toplam = fiyat * miktar
            entry_tutar.config(state="normal")
            entry_tutar.delete(0, tk.END)
            entry_tutar.insert(0, str(toplam))
            entry_tutar.config(state="readonly")
        except:
            entry_tutar.config(state="normal")
            entry_tutar.delete(0, tk.END)
            entry_tutar.config(state="readonly")

    entry_miktar.bind("<KeyRelease>", tutar_hesapla)
    urun_combo.bind("<<ComboboxSelected>>", tutar_hesapla)

    def temizle():
        urun_combo.set("")
        entry_miktar.delete(0, tk.END)
        entry_tutar.config(state="normal")
        entry_tutar.delete(0, tk.END)
        entry_tutar.config(state="readonly")
        entry_aciklama.delete(0, tk.END)

    def kaydet():
        secilen = urun_combo.current()
        if secilen == -1:
            messagebox.showwarning("Uyarı", "Lütfen bir ürün seçin.")
            return
        try:
            urun_id = urunler[secilen].URUNID
            miktar = int(entry_miktar.get())
            toplam_tutar = float(entry_tutar.get())
            aciklama = entry_aciklama.get().strip()
        except:
            messagebox.showerror("Hata", "Geçerli değerler giriniz.")
            return
        if siparis_ekle(urun_id, miktar, toplam_tutar, aciklama):
            messagebox.showinfo("Başarılı", "Sipariş başarıyla eklendi.")
            temizle()
            siparisleri_goster()

    tk.Button(frame_ekle, text="💾 Kaydet", command=kaydet, **buton_stil, width=12).grid(row=0, column=8, padx=12)
    tk.Button(frame_ekle, text="🧹 Temizle", command=temizle, bg="#757575", fg="white", activebackground="#616161", activeforeground="white", font=("Arial", 12, "bold"), bd=0, width=10).grid(row=0, column=9, padx=5)

    frame_liste = tk.Frame(pencere, bg="#23272e")
    frame_liste.pack(pady=10, fill="both", expand=True)

    kolonlar = ("id", "urun", "miktar", "tutar", "aciklama", "tarih")
    tree = ttk.Treeview(frame_liste, columns=kolonlar, show="headings", selectmode="browse")
    tree.heading("id", text="ID")
    tree.heading("urun", text="Ürün")
    tree.heading("miktar", text="Miktar")
    tree.heading("tutar", text="Toplam Tutar (₺)")
    tree.heading("aciklama", text="Açıklama")
    tree.heading("tarih", text="Tarih")
    tree.column("id", width=60, anchor="center")
    tree.column("urun", width=180)
    tree.column("miktar", width=80, anchor="center")
    tree.column("tutar", width=120, anchor="center")
    tree.column("aciklama", width=250)
    tree.column("tarih", width=120)
    tree.pack(fill="both", expand=True)

    frame_guncelle = tk.Frame(pencere, bg="#23272e")
    frame_guncelle.pack(pady=8)

    tk.Button(frame_guncelle, text="📝 Güncelle", bg="#ffb300", fg="white", activebackground="#ff8f00", activeforeground="white", font=("Arial", 12, "bold"), bd=0, width=12,
              command=lambda: guncelle()).pack(side="left", padx=10)
    tk.Button(frame_guncelle, text="🗑️ Sil", bg="#e53935", fg="white", activebackground="#b71c1c", activeforeground="white", font=("Arial", 12, "bold"), bd=0, width=12,
              command=lambda: sil()).pack(side="left", padx=10)
    tk.Button(frame_guncelle, text="Excel'e Aktar", bg="#1976d2", fg="white", activebackground="#0d47a1", activeforeground="white", font=("Arial", 12, "bold"), bd=0, width=14,
              command=lambda: tabloyu_excele_aktar(siparisleri_listele(entry_ara.get(), entry_tarih1.get_date(), entry_tarih2.get_date()))).pack(side="left", padx=10)
    tk.Button(frame_guncelle, text="Ürün Grafiği", bg="#43a047", fg="white", activebackground="#2e7031", activeforeground="white", font=("Arial", 12, "bold"), bd=0, width=14,
              command=en_cok_siparis_urun_grafik).pack(side="left", padx=10)
    tk.Button(frame_guncelle, text="Aylık Satış Grafiği", bg="#8e24aa", fg="white", activebackground="#4a148c", activeforeground="white", font=("Arial", 12, "bold"), bd=0, width=16,
              command=aylik_satis_grafik).pack(side="left", padx=10)

    secili_id = [None]

    def siparisleri_goster(aranan="", tarih1=None, tarih2=None):
        for i in tree.get_children():
            tree.delete(i)
        rows = siparisleri_listele(aranan, tarih1, tarih2)
        for row in rows:
            tree.insert("", "end", values=(row.SiparisID, row.URUNAdi, row.Miktar, row.ToplamTutar, row.Aciklama, row.SiparisTarihi.strftime("%Y-%m-%d %H:%M")))
        adet, toplam = toplam_satis_ozet(tarih1, tarih2)
        lbl_ozet.config(text=f"Toplam Sipariş: {adet} | Toplam Satış: {toplam}₺")

    def tree_sec(event):
        secili = tree.focus()
        if not secili:
            secili_id[0] = None
            return
        values = tree.item(secili, "values")
        secili_id[0] = values[0]
        urun_adi = values[1]
        miktar = values[2]
        tutar = values[3]
        aciklama = values[4]
        for i, u in enumerate(urunler):
            if u.URUNAdi == urun_adi:
                urun_combo.current(i)
                break
        entry_miktar.delete(0, tk.END)
        entry_miktar.insert(0, miktar)
        entry_tutar.config(state="normal")
        entry_tutar.delete(0, tk.END)
        entry_tutar.insert(0, tutar)
        entry_tutar.config(state="readonly")
        entry_aciklama.delete(0, tk.END)
        entry_aciklama.insert(0, aciklama)

    tree.bind("<<TreeviewSelect>>", tree_sec)

    def guncelle():
        if not secili_id[0]:
            messagebox.showwarning("Uyarı", "Lütfen bir sipariş seçin.")
            return
        secilen = urun_combo.current()
        if secilen == -1:
            messagebox.showwarning("Uyarı", "Lütfen bir ürün seçin.")
            return
        try:
            urun_id = urunler[secilen].URUNID
            miktar = int(entry_miktar.get())
            toplam_tutar = float(entry_tutar.get())
            aciklama = entry_aciklama.get().strip()
        except:
            messagebox.showerror("Hata", "Geçerli değerler giriniz.")
            return
        if siparis_guncelle(secili_id[0], urun_id, miktar, toplam_tutar, aciklama):
            messagebox.showinfo("Başarılı", "Sipariş güncellendi.")
            temizle()
            siparisleri_goster(entry_ara.get(), entry_tarih1.get_date(), entry_tarih2.get_date())

    def sil():
        if not secili_id[0]:
            messagebox.showwarning("Uyarı", "Lütfen bir sipariş seçin.")
            return
        if messagebox.askyesno("Onay", "Seçili siparişi silmek istediğinize emin misiniz?"):
            if siparis_sil(secili_id[0]):
                messagebox.showinfo("Başarılı", "Sipariş silindi.")
                temizle()
                siparisleri_goster(entry_ara.get(), entry_tarih1.get_date(), entry_tarih2.get_date())

    siparisleri_goster()
    pencere.mainloop()

if __name__ == "__main__":
    ana_ekran()