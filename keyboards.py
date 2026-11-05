from aiogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardMarkup,
    InlineKeyboardButton
)

# Главное меню с категориями и кнопкой города
main_kb = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="🌯 Шаурма и фастфуд"),
            KeyboardButton(text="🍽 Рестораны и кафе")
        ],
        [
            KeyboardButton(text="🚗 Автомойки и детейлинг"),
            KeyboardButton(text="🦷 Стоматологии")
        ],
        [
            KeyboardButton(text="🛋 Мебель и кухни"),
            KeyboardButton(text="🏙 Сменить город")
        ]
    ],
    resize_keyboard=True,
    input_field_placeholder="Выберите категорию или действие..."
)

# Инлайн-кнопки выбора городов КМВ
cities_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="Пятигорск", callback_data="set_city:Пятигорск"),
            InlineKeyboardButton(text="Ессентуки", callback_data="set_city:Ессентуки")
        ],
        [
            InlineKeyboardButton(text="Кисловодск", callback_data="set_city:Кисловодск"),
            InlineKeyboardButton(text="Минеральные Воды", callback_data="set_city:Минеральные Воды")
        ]
    ]
)

# Инлайн-кнопки перелистывания страниц (обновляем, чтобы передавать city)
def get_pagination_kb(
    city: str,
    category: str, 
    offset: int, 
    limit: int, 
    total: int, 
    only_without_site: bool = False
) -> InlineKeyboardMarkup | None:
    nav_row = []

    filter_val = 1 if only_without_site else 0
    toggle_val = 0 if only_without_site else 1
    
    toggle_text = "🌐 Показать все" if only_without_site else "🎯 Только без сайта"
    toggle_btn = InlineKeyboardButton(
        text=toggle_text,
        callback_data=f"page:{city}:{category}:0:{toggle_val}"
    )

    if offset > 0:
        prev_offset = max(0, offset - limit)
        nav_row.append(
            InlineKeyboardButton(text="⬅️ Назад", callback_data=f"page:{city}:{category}:{prev_offset}:{filter_val}")
        )

    if offset + limit < total:
        next_offset = offset + limit
        nav_row.append(
            InlineKeyboardButton(text="Вперёд ➡️", callback_data=f"page:{city}:{category}:{next_offset}:{filter_val}")
        )

    keyboard = [[toggle_btn]]
    if nav_row:
        keyboard.append(nav_row)

    return InlineKeyboardMarkup(inline_keyboard=keyboard)