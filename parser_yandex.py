import asyncio
import aiosqlite
from playwright.async_api import async_playwright

from database import init_db

DB_PATH = "companies.db"

async def save_to_db(company: dict):
    has_website = 1 if company["website"] else 0
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute(
            "SELECT id FROM companies WHERE name = ? AND address = ?",
            (company["name"], company["address"])
        ) as cursor:
            if await cursor.fetchone():
                return False

        await db.execute("""
            INSERT INTO companies (name, category, city, address, phone, website, has_website)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            company["name"],
            company["category"],
            company["city"],
            company["address"],
            company["phone"],
            company["website"],
            has_website
        ))
        await db.commit()
        return True


async def scrape_yandex_maps(city: str, category_name: str, search_query: str, max_items: int = 20):
    print(f"\n🔍 Сбор данных: '{search_query}' (нужно до {max_items} шт.)...")
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            viewport={"width": 1440, "height": 900},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            locale="ru-RU"
        )
        page = await context.new_page()

        encoded_query = search_query.replace(" ", "%20")
        url = f"https://yandex.ru/maps/?text={encoded_query}"
        
        try:
            await page.goto(url, wait_until="domcontentloaded", timeout=25000)
        except Exception as e:
            print(f"⚠️ Ошибка загрузки страницы: {e}")
            await browser.close()
            return

        await page.wait_for_timeout(3000)

        # Закрываем всплывашки если вылезли
        for btn_text in ["Хорошо", "Принять", "Да"]:
            try:
                btn = await page.query_selector(f"button:has-text('{btn_text}')")
                if btn:
                    await btn.click()
                    await page.wait_for_timeout(500)
            except Exception:
                pass

        # Находим контейнер списка
        list_container = await page.query_selector("ul.search-list-view__list")
        if not list_container:
            print("⚠️ Не найден список организаций на странице.")
            await browser.close()
            return

        # Наводим курсор строго на левую панель и крутим список
        await list_container.hover()
        for _ in range(8):
            await page.mouse.wheel(0, 3000)
            await page.wait_for_timeout(1000)

        items = await page.query_selector_all("li.search-snippet-view")
        print(f"📦 Подгружено карточек: {len(items)}")

        saved_count = 0

        for item in items[:max_items]:
            try:
                name_elem = await item.query_selector(".search-business-snippet-view__title")
                if not name_elem:
                    continue
                name = (await name_elem.inner_text()).strip()

                address_elem = await item.query_selector(".search-business-snippet-view__address")
                address = (await address_elem.inner_text()).strip() if address_elem else "Адрес не указан"

                # Кликаем на карточку для открытия деталей
                await name_elem.click()
                await page.wait_for_timeout(1200)

                # --- ДОРАБОТАННЫЙ БЛОК ИЗВЛЕЧЕНИЯ НОМЕРА ТЕЛЕФОНА ---
                try:
                    show_phone_btn = await page.query_selector("button:has-text('Показать телефон'), div[class*='phones-view__action']")
                    if show_phone_btn:
                        await show_phone_btn.click()
                        await page.wait_for_timeout(500)
                except Exception:
                    pass

                phone = "Телефон не указан"
                phone_links = await page.query_selector_all("a[href^='tel:']")
                if phone_links:
                    phone_raw = await phone_links[0].get_attribute("href")
                    phone = phone_raw.replace("tel:", "").strip()
                else:
                    phone_elem = await page.query_selector("div.orgpage-phones-view__phone-number, [itemprop='telephone']")
                    if phone_elem:
                        phone = (await phone_elem.inner_text()).strip()
                # ----------------------------------------------------

                # Забираем сайт
                website = None
                site_elem = await page.query_selector("a.card-feature-view__link, a[class*='business-urls-view']")
                if site_elem:
                    href = await site_elem.get_attribute("href")
                    if href and "yandex" not in href and "tel:" not in href:
                        website = href.strip()

                company = {
                    "name": name,
                    "category": category_name,
                    "city": city,
                    "address": address,
                    "phone": phone,
                    "website": website
                }

                added = await save_to_db(company)
                if added:
                    saved_count += 1
                    status = f"Сайт: {website}" if website else "🎯 БЕЗ САЙТА"
                    print(f"  [+] {name} | Тел: {phone} | {status}")

            except Exception as e:
                print(f"  [!] Ошибка в карточке: {e}")
                continue

        await browser.close()
        print(f"✅ Успешно добавлено: {saved_count}")


async def main():
    await init_db()

    tasks = [
        ("Пятигорск", "шаурма", "шаурма Пятигорск"),
        ("Пятигорск", "ресторан", "ресторан кафе Пятигорск"),
        ("Пятигорск", "автомойка", "автомойка детейлинг Пятигорск"),
        ("Пятигорск", "стоматология", "стоматология Пятигорск"),
        ("Пятигорск", "мебель", "мебель на заказ кухни Пятигорск")
    ]

    for city, cat, query in tasks:
        await scrape_yandex_maps(city=city, category_name=cat, search_query=query, max_items=15)
        await asyncio.sleep(2)

if __name__ == "__main__":
    asyncio.run(main())