import pyodbc

try:
    conn = pyodbc.connect(
        "DRIVER={ODBC Driver 17 for SQL Server};"
        "SERVER=BURAK;"
        "DATABASE=WhiteStoneCoffe;"
        "Trusted_Connection=yes;"
    )
    print("SQL Server bağlantısı başarılı")
    conn.close()
except Exception as e:
    print("SQL Server bağlantısı başarısız:", e)