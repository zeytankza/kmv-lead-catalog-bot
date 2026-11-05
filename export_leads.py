import sqlite3
import pandas as pd

DB_PATH = "companies.db"
OUTPUT_FILE = "leads_without_site.xlsx"

def export_leads():
    conn = sqlite3.connect(DB_PATH)
    
    # Забираем только те компании, у которых нет сайта
    query = """
        SELECT category AS 'Сфера',
               name AS 'Название компании',
               city AS 'Город',
               address AS 'Адрес',
               phone AS 'Номер телефона'
        FROM companies
        WHERE has_website = 0
        ORDER BY category, name
    """
    
    df = pd.read_sql_query(query, conn)
    conn.close()

    if df.empty:
        print("В базе пока нет организаций без сайта.")
        return

    # Сохраняем в красивый Excel-файл
    with pd.ExcelWriter(OUTPUT_FILE, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Лиды без сайта")

    print(f"✅ Успешно выгружено {len(df)} потенциальных клиентов в файл: {OUTPUT_FILE}")

if __name__ == "__main__":
    export_leads()