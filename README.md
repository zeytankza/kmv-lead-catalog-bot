<div align="center">

# KMV Lead Generator & Business Directory Bot

A full-featured Telegram bot and automated web scraper built to discover local business leads without websites across the Caucasian Mineral Waters (KMV) region.

[English](#overview) • [Русский](#обзор-проекта)

</div>

---

## Overview

A B2B lead generation tool and regional catalog. It automatically collects local businesses from interactive map listings, filters out organizations lacking an official web presence, and presents them via an asynchronous Telegram interface or an exported spreadsheet ready for client outreach.

### Tech Stack
- **Language:** Python 3.10+
- **Bot Framework:** `aiogram 3.x` (modular handlers, inline pagination, state storage)
- **Scraping Engine:** `Playwright` (headless Chromium automation, DOM parsing, anti-bot mitigation)
- **Database:** `aiosqlite` / `SQLite3` (async queries, connection pooling, deduplication)
- **Data Export:** `pandas`, `openpyxl` (instant `.xlsx` report generation)

### Key Features
- **Smart Data Scraping:** Browser-driven extraction of verified business names, categories, addresses, and contact phone numbers directly from dynamic map layers.
- **Lead Generation Mode:** Instant filter isolating companies marked with `No Website` to identify immediate targets for web and bot development services.
- **In-Message Pagination:** Real-time Telegram message editing with dynamic page indicators, preventing chat clutter.
- **Multi-City Support:** Flexible database architecture supporting multiple regional cities.
- **One-Click Lead Export:** Clean Excel export of high-intent contacts with structured columns for direct messaging.

### Project Architecture
```text
kmv_catalog_bot/
├── config.py           # Environment variables and bot tokens
├── database.py         # Async SQLite schema, queries, and user state
├── keyboards.py        # Reply and Inline keyboards with dynamic callbacks
├── main.py             # Bot initialization, polling loop, and handlers
├── parser_yandex.py    # Playwright-based scraper for map directories
├── export_leads.py     # Spreadsheet generator for filtered leads
├── requirements.txt    # Dependency specifications
└── .gitignore          # Sensitive credential protection

Quick Start

    Clone the repository:
    Bash

    git clone [https://github.com/your-username/kmv-lead-generator-bot.git](https://github.com/your-username/kmv-lead-generator-bot.git)
    cd kmv-lead-generator-bot

    Set up the virtual environment:
    Bash

    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    pip install -r requirements.txt
    playwright install chromium

    Configure environment:
    Create a .env file in the root directory:
    Фрагмент кода

    BOT_TOKEN=your_telegram_bot_token_here

    Run data scraper & start the bot:
    Bash

    python parser_yandex.py
    python main.py

# KMV Lead Generator & Business Directory Bot

Telegram-бот и парсер организаций для поиска потенциальных B2B-клиентов на веб-разработку по региону КМВ (Пятигорск).

## Стек технологий
- **Python 3.10+**
- **aiogram 3.x** (Асинхронный бот, инлайн-пагинация, переключение городов)
- **Playwright** (Автоматизация сбора данных с Яндекс Карт в обход динамической подгрузки)
- **aiosqlite / SQLite3** (Асинхронная база данных организаций и пользователей)
- **Pandas / OpenPyXL** (Экспорт горячих лидов без сайтов в Excel)

## Возможности
1. Каталог заведений по категориям (автомойки, рестораны, мебель, стоматологии).
2. Фильтр лидогенерации: выборка компаний со статусом «Сайта нет» для продажи услуг веб-разработки и ботов.
3. Постраничная инлайн-навигация без спама сообщениями.
4. Выгрузка контактов (название, телефон, адрес) в Excel-таблицу одной командой.

Обзор проекта

Инструмент автоматизации поиска B2B-клиентов и каталог заведений по региону КМВ (Пятигорск и города-курорты). Проект собирает реальные организации с интерактивных карт, выявляет компании без собственных веб-ресурсов и предоставляет базу для продажи услуг веб-разработки через Telegram-бота или Excel-выгрузку.
Основные возможности

    Автономный парсинг: Сбор названий, адресов и прямых телефонных номеров с интерактивных карт через Playwright.

    Фильтр лидогенерации: Выборка «Только без сайта» для мгновенного формирования базы потенциальных клиентов.

    Инлайн-навигация: Постраничное перелистывание карточек организаций прямо в Telegram без спама новыми сообщениями.

    Экспорт базы: Генерация готовой таблицы leads_without_site.xlsx для холодного или точечного контакта.