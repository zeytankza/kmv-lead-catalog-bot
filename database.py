import aiosqlite

DB_PATH = "companies.db"

async def init_db():
    """Создание таблицы компаний, если её ещё нет."""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS companies (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                category TEXT NOT NULL,
                city TEXT NOT NULL,
                address TEXT,
                phone TEXT,
                website TEXT,
                has_website INTEGER DEFAULT 0
            )
        """)
        await db.commit()

async def add_company(name: str, category: str, city: str, address: str, phone: str, website: str = None):
    """Добавление организации в базу."""
    has_website = 1 if website else 0
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            INSERT INTO companies (name, category, city, address, phone, website, has_website)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (name, category, city, address, phone, website, has_website))
        await db.commit()

async def get_companies_by_category(
    city: str, 
    category: str, 
    limit: int = 5, 
    offset: int = 0, 
    only_without_site: bool = False
):
    """Выборка компаний с поддержкой пагинации и фильтра по наличию сайта."""
    query = """
        SELECT name, address, phone, website, has_website
        FROM companies
        WHERE city = ? AND category = ?
    """
    params = [city, category]

    if only_without_site:
        query += " AND has_website = 0"

    query += " LIMIT ? OFFSET ?"
    params.extend([limit, offset])

    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(query, tuple(params)) as cursor:
            return await cursor.fetchall()


async def count_companies(city: str, category: str, only_without_site: bool = False) -> int:
    """Подсчет общего числа организаций с учетом фильтра."""
    query = "SELECT COUNT(*) FROM companies WHERE city = ? AND category = ?"
    params = [city, category]

    if only_without_site:
        query += " AND has_website = 0"

    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute(query, tuple(params)) as cursor:
            res = await cursor.fetchone()
            return res[0] if res else 0

async def init_db():
    """Создание таблиц, если их ещё нет."""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS companies (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                category TEXT NOT NULL,
                city TEXT NOT NULL,
                address TEXT,
                phone TEXT,
                website TEXT,
                has_website INTEGER DEFAULT 0
            )
        """)
        # Новая таблица для сохранения города пользователя
        await db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                city TEXT DEFAULT 'Пятигорск'
            )
        """)
        await db.commit()

async def set_user_city(user_id: int, city: str):
    """Сохранение выбранного города для пользователя."""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            INSERT INTO users (user_id, city) VALUES (?, ?)
            ON CONFLICT(user_id) DO UPDATE SET city = excluded.city
        """, (user_id, city))
        await db.commit()

async def get_user_city(user_id: int) -> str:
    """Получение текущего выбранного города пользователя."""
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT city FROM users WHERE user_id = ?", (user_id,)) as cursor:
            row = await cursor.fetchone()
            return row[0] if row else "Пятигорск"