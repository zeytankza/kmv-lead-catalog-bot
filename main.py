import asyncio
import logging
from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties

from config import BOT_TOKEN
from database import (
    init_db, 
    get_companies_by_category, 
    count_companies, 
    get_user_city, 
    set_user_city
)
from keyboards import main_kb, cities_kb, get_pagination_kb

logging.basicConfig(level=logging.INFO)

bot = Bot(
    token=BOT_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)
dp = Dispatcher()

CATEGORIES_MAP = {
    "🌯 Шаурма и фастфуд": "шаурма",
    "🍽 Рестораны и кафе": "ресторан",
    "🚗 Автомойки и детейлинг": "автомойка",
    "🦷 Стоматологии": "стоматология",
    "🛋 Мебель и кухни": "мебель"
}

PAGE_SIZE = 4

async def build_companies_page(city: str, category: str, offset: int, only_without_site: bool = False):
    total = await count_companies(city, category, only_without_site=only_without_site)
    companies = await get_companies_by_category(
        city=city, 
        category=category, 
        limit=PAGE_SIZE, 
        offset=offset, 
        only_without_site=only_without_site
    )
    
    status_label = " (🎯 Только без сайта)" if only_without_site else ""
    
    if not companies:
        text = f"📍 <b>Организации в г. {city}</b>{status_label}:\n\nНичего не найдено."
        kb = get_pagination_kb(city=city, category=category, offset=offset, limit=PAGE_SIZE, total=total, only_without_site=only_without_site)
        return text, kb

    current_page = (offset // PAGE_SIZE) + 1
    total_pages = max(1, (total + PAGE_SIZE - 1) // PAGE_SIZE)

    response = [f"📍 <b>Организации в г. {city}</b>{status_label} (Стр. {current_page}/{total_pages}):\n"]
    
    for row in companies:
        site_info = f"<a href='{row['website']}'>Перейти на сайт</a>" if row["has_website"] else "<i>Сайта нет</i>"
        card = (
            f"🏢 <b>{row['name']}</b>\n"
            f"🏠 Адрес: {row['address']}\n"
            f"📞 Телефон: <code>{row['phone']}</code>\n"
            f"🌐 Сайт: {site_info}\n"
        )
        response.append(card)
        
    kb = get_pagination_kb(
        city=city,
        category=category, 
        offset=offset, 
        limit=PAGE_SIZE, 
        total=total, 
        only_without_site=only_without_site
    )
    return "\n".join(response), kb

@dp.message(CommandStart())
async def cmd_start(message: Message):
    city = await get_user_city(message.from_user.id)
    text = (
        f"Привет, <b>{message.from_user.first_name}</b>!\n\n"
        f"Текущий город: <b>{city}</b>.\n"
        "Выбери сферу или смени город в меню ниже:"
    )
    await message.answer(text, reply_markup=main_kb)

# Кнопка смены города
@dp.message(F.text == "🏙 Сменить город")
async def choose_city(message: Message):
    await message.answer("Выбери город из списка:", reply_markup=cities_kb)

# Обработка выбора города
@dp.callback_query(F.data.startswith("set_city:"))
async def city_selected(callback: CallbackQuery):
    selected_city = callback.data.split(":")[1]
    await set_user_city(callback.from_user.id, selected_city)
    await callback.message.edit_text(f"Город успешно изменён на: <b>{selected_city}</b>")
    await callback.answer()

@dp.message(F.text.in_(CATEGORIES_MAP.keys()))
async def show_companies_by_category(message: Message):
    city = await get_user_city(message.from_user.id)
    category = CATEGORIES_MAP[message.text]
    text, kb = await build_companies_page(city=city, category=category, offset=0, only_without_site=False)
    await message.answer(text, reply_markup=kb, disable_web_page_preview=True)

# Пагинация и фильтр
@dp.callback_query(F.data.startswith("page:"))
async def paginate_companies(callback: CallbackQuery):
    parts = callback.data.split(":")
    city = parts[1]
    category = parts[2]
    offset = int(parts[3])
    only_without_site = bool(int(parts[4])) if len(parts) > 4 else False
    
    text, kb = await build_companies_page(
        city=city, 
        category=category, 
        offset=offset, 
        only_without_site=only_without_site
    )
    
    await callback.message.edit_text(text, reply_markup=kb, disable_web_page_preview=True)
    await callback.answer()

async def main():
    await init_db()
    print("Бот запущен с поддержкой городов!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())