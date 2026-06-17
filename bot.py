import asyncio
import random
import logging
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from flask import Flask
import threading
import os
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import datetime

TOKEN = "8843234890:AAGqFxhPN7ALZ9VephCAT_NXGtzkg-ROYBU"

logging.basicConfig(level=logging.INFO)
bot = Bot(token=TOKEN)
dp = Dispatcher()

# ========== ПОДКЛЮЧЕНИЕ К GOOGLE TABLES ==========
def get_sheet():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
    client = gspread.authorize(creds)
    # ЗАМЕНИ НА СВОЙ ID ТАБЛИЦЫ (вставь его между кавычками)
    sheet = client.open_by_key("1hoDNwIulpgsefccNZgmyL8ix4JB4e6YlEeRGJ6Mw7S0").sheet1
    return sheet

def log_event(user_id, username, step, result="", score=0):
    """Записывает событие в Google Таблицу"""
    try:
        sheet = get_sheet()
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        all_records = sheet.get_all_values()
        user_found = False
        for i, row in enumerate(all_records):
            if len(row) > 0 and str(row[0]) == str(user_id):
                user_found = True
                sheet.update_cell(i+1, 4, step)
                if result:
                    sheet.update_cell(i+1, 5, result)
                if score > 0:
                    sheet.update_cell(i+1, 6, score)
                break
        if not user_found:
            sheet.append_row([user_id, username, now, step, result, score])
    except Exception as e:
        print(f"Ошибка записи в Google Sheets: {e}")

def shuffle_buttons(buttons_list):
    shuffled = buttons_list.copy()
    random.shuffle(shuffled)
    return shuffled

# ========== ПРИВЕТСТВИЕ ==========
@dp.message(Command("start"))
async def start(message: Message):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="▶ Продолжить", callback_data="continue_after_welcome")]
    ])
    await message.answer_photo(
        photo="https://storage2.bothelp.io/pecherichenko/ec/ec4a/ec4a25e15f7928d21c95f984c74f7fb2/IMG_4962.jpeg",
        caption="🛡 Защищенный канал связи активирован.\n\n"
                "Добро пожаловать в Ситуационный центр магистратуры «Дипломатия: теория, история, практика» Кубанского государственного университета.\n\n"
                "Вы — офицер аналитического отдела. В мире назревает кризис. Ваши решения повлияют на исход событий.\n\n"
                "⬇ Нажмите кнопку «Продолжить», чтобы получить первую вводную.",
        reply_markup=keyboard
    )
    log_event(message.from_user.id, message.from_user.username or "unknown", "Запустил бота")

# ========== СБОР ИМЕНИ ==========
@dp.callback_query(F.data == "continue_after_welcome")
async def collect_name(callback: CallbackQuery):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🛡 Будущий атташе", callback_data="name_atashe")],
        [InlineKeyboardButton(text="📊 Будущий аналитик", callback_data="name_analyst")],
        [InlineKeyboardButton(text="🎙 Будущий пресс-секретарь", callback_data="name_press")],
        [InlineKeyboardButton(text="🕵️ Будущий разведчик", callback_data="name_strategy")]
    ])
    await callback.message.answer(
        "Для идентификации в Системе выберите свой позывной и специализацию.\n\n"
        "⬇ Нажмите на один из вариантов.",
        reply_markup=keyboard
    )
    await callback.answer()

# ========== ВЫБОР ПРОТОКОЛА ==========
@dp.callback_query(F.data.startswith("name_"))
async def choose_protocol(callback: CallbackQuery):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔵 Протокол «Аналитика»", callback_data="protocol_analytics")],
        [InlineKeyboardButton(text="🟢 Протокол «Дипломатия»", callback_data="protocol_diplomacy")]
    ])
    await callback.message.answer(
        "Офицер, доступ разрешён.\n\n"
        "Выберите протокол связи. Как предпочитаете работать?\n\n"
        "⬇ Нажмите на один из вариантов.",
        reply_markup=keyboard
    )
    log_event(callback.from_user.id, callback.from_user.username or "unknown", "Выбрал протокол")
    await callback.answer()

# ===================== ПРОТОКОЛ АНАЛИТИКА =====================
@dp.callback_query(F.data == "protocol_analytics")
async def analytics_choose_track(callback: CallbackQuery):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📊 Экспертная аналитика", callback_data="track_A1")],
        [InlineKeyboardButton(text="🎯 Стратегический менеджмент", callback_data="track_A2")],
        [InlineKeyboardButton(text="🏛 Дипломатическая госслужба", callback_data="track_A3")],
        [InlineKeyboardButton(text="🎙 Публичная дипломатия", callback_data="track_A4")]
    ])
    await callback.message.answer_photo(
        photo="https://storage2.bothelp.io/pecherichenko/7f/7fc7/7fc7f4ec4e46e1c07173d40fbed68166/IMG_5020.jpeg",
        caption="🔵 Протокол «Аналитика» активирован.\n\n"
                "Ваша стихия — данные, прогнозы, разведка.\n"
                "Выберите направление для прохождения миссии:\n\n"
                "⬇ Нажмите на один из вариантов.",
        reply_markup=keyboard
    )
    await callback.answer()

# ----- ТРЕК A1: ЭКСПЕРТНАЯ АНАЛИТИКА -----
@dp.callback_query(F.data == "track_A1")
async def track_A1(callback: CallbackQuery):
    buttons = shuffle_buttons([
        ("📰 Сообщить в СМИ", "A1_panic"),
        ("🗣 Созвать совещание экспертов", "A1_slow"),
        ("📈 Сопоставить снимки за 6 месяцев", "A1_system")
    ])
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text=t, callback_data=d)] for t, d in buttons])
    await callback.message.answer(
        "📊 Трек: Экспертная аналитика\n🔵 Протокол: Аналитика\n\n"
        "Вводная. Спутниковые снимки зафиксировали неопознанную активность в приграничной зоне.\n"
        "У вас есть 2 часа, чтобы проанализировать данные и подготовить заключение.\n\n"
        "С чего начнёте?\n\n⬇ Ваш ответ, офицер.",
        reply_markup=keyboard
    )
    await callback.answer()

@dp.callback_query(F.data == "A1_system")
async def A1_system(callback: CallbackQuery):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔄 Пройти другой трек", callback_data="protocol_analytics")],
        [InlineKeyboardButton(text="🎓 Узнать о поступлении", callback_data="final_common_stub")],
        [InlineKeyboardButton(text="🔁 Сменить протокол", callback_data="choose_protocol")]
    ])
    await callback.message.answer_photo(
        photo="https://storage2.bothelp.io/pecherichenko/a0/a083/a0834f642b569cd81f0e053a0020baa4/IMG_4954.jpeg",
        caption="🟢 Результат: Системный аналитик\n\n"
                "Верный подход. Вы ищете закономерности, а не паникуете.\n"
                "На курсе «Системный анализ и принятие решений в международных отношениях» (доцент Шалимова О.В.) учат именно этому.\n\n"
                "🎧 Анализ миссии: ВЫСОКИЙ УРОВЕНЬ\n\n"
                "Вы мыслите как профессиональный аналитик. Магистратура КубГУ даст вам инструменты для работы с большими данными, прогнозирования и моделирования международных процессов.",
        reply_markup=keyboard
    )
    await callback.answer()

@dp.callback_query(F.data == "A1_slow")
async def A1_slow(callback: CallbackQuery):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔄 Пройти другой трек", callback_data="protocol_analytics")],
        [InlineKeyboardButton(text="🎓 Узнать о поступлении", callback_data="final_common_stub")],
        [InlineKeyboardButton(text="🔁 Сменить протокол", callback_data="choose_protocol")]
    ])
    await callback.message.answer_photo(
        photo="https://storage2.bothelp.io/pecherichenko/5c/5c68/5c684b41b0186f2f1216fdd1c7eebf00/IMG_4958.jpeg",
        caption="🟡 Результат: Осторожный, но медленный\n\n"
                "Коллеги — это ценно. Но время уходит.\n"
                "На курсе «Прогнозирование и моделирование международных процессов» (канд. ист. наук. Кумпан В.А.) вас научат работать с данными быстрее.\n\n"
                "☑ Анализ миссии: ЕСТЬ ПОТЕНЦИАЛ\n\n"
                "Вы чувствуете важность анализа, но пока опираетесь на чужое мнение. Магистратура КубГУ научит вас самостоятельно строить прогнозы и работать с данными.",
        reply_markup=keyboard
    )
    await callback.answer()

@dp.callback_query(F.data == "A1_panic")
async def A1_panic(callback: CallbackQuery):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔄 Пройти другой трек", callback_data="protocol_analytics")],
        [InlineKeyboardButton(text="🎓 Узнать о поступлении", callback_data="final_common_stub")],
        [InlineKeyboardButton(text="🔁 Сменить протокол", callback_data="choose_protocol")]
    ])
    await callback.message.answer_photo(
        photo="https://storage2.bothelp.io/pecherichenko/e3/e317/e317ae09098009ab6053563cc3e39864/IMG_4955.jpeg",
        caption="🔴 Результат: Паникёр\n\n"
                "Вы создали международный скандал на пустом месте.\n"
                "Аналитик должен сначала проверить факты, потом действовать.\n"
                "Магистратура КубГУ научит вас системному подходу.\n\n"
                "🎧 Анализ миссии: ТРЕБУЕТСЯ ОБУЧЕНИЕ\n\n"
                "Вы действуете импульсивно. К счастью, это поправимо. Магистратура КубГУ научит вас системному анализу и прогнозированию.",
        reply_markup=keyboard
    )
    await callback.answer()

# ----- ТРЕК A2: СТРАТЕГИЧЕСКИЙ МЕНЕДЖМЕНТ -----
@dp.callback_query(F.data == "track_A2")
async def track_A2(callback: CallbackQuery):
    buttons = shuffle_buttons([
        ("📋 Анализ структуры управления альянсом", "A2_system"),
        ("☕ Передать исходные данные начальству", "A2_panic"),
        ("🤝 Оценить баланс сил между игроками", "A2_slow")
    ])
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text=t, callback_data=d)] for t, d in buttons])
    await callback.message.answer(
        "🎯 Трек: Стратегический менеджмент\n🔵 Протокол: Аналитика\n\n"
        "Вводная. Вы получили доступ к закрытым данным о долгосрочной стратегии крупного международного альянса.\n"
        "Нужно выделить ключевые зоны нестабильности и точки влияния для России.\n\n"
        "Ваш первый шаг?\n\n⬇ Ваш ответ, офицер.",
        reply_markup=keyboard
    )
    await callback.answer()

@dp.callback_query(F.data == "A2_system")
async def A2_system(callback: CallbackQuery):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔄 Пройти другой трек", callback_data="protocol_analytics")],
        [InlineKeyboardButton(text="🎓 Узнать о поступлении", callback_data="final_common_stub")],
        [InlineKeyboardButton(text="🔁 Сменить протокол", callback_data="choose_protocol")]
    ])
    await callback.message.answer_photo(
        photo="https://storage2.bothelp.io/pecherichenko/a0/a083/a0834f642b569cd81f0e053a0020baa4/IMG_4954.jpeg",
        caption="🟢 Результат: Глубокий аналитик\n\n"
                "Вы видите систему целиком, а не отдельные элементы.\n"
                "Именно такому подходу учат в магистратуре КубГУ.\n\n"
                "🎧 Анализ миссии: ВЫСОКИЙ УРОВЕНЬ\n\n"
                "Вы мыслите как стратегический аналитик. В магистратуре КубГУ вас ждёт системный подход, работа с нестабильной средой и управленческие кейсы.",
        reply_markup=keyboard
    )
    await callback.answer()

@dp.callback_query(F.data == "A2_slow")
async def A2_slow(callback: CallbackQuery):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔄 Пройти другой трек", callback_data="protocol_analytics")],
        [InlineKeyboardButton(text="🎓 Узнать о поступлении", callback_data="final_common_stub")],
        [InlineKeyboardButton(text="🔁 Сменить протокол", callback_data="choose_protocol")]
    ])
    await callback.message.answer_photo(
        photo="https://storage2.bothelp.io/pecherichenko/5c/5c68/5c684b41b0186f2f1216fdd1c7eebf00/IMG_4958.jpeg",
        caption="🟡 Результат: Узкий взгляд\n\n"
                "Оперативные решения важны, но без стратегического видения картина неполная.\n"
                "В КубГУ вас научат сочетать тактику и стратегию.\n\n"
                "📌 Анализ миссии: ЕСТЬ ПОТЕНЦИАЛ\n\n"
                "Вы мыслите как тактик, но стратегу нужен более широкий взгляд. Магистратура КубГУ научит вас комплексному управлению.",
        reply_markup=keyboard
    )
    await callback.answer()

@dp.callback_query(F.data == "A2_panic")
async def A2_panic(callback: CallbackQuery):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔄 Пройти другой трек", callback_data="protocol_analytics")],
        [InlineKeyboardButton(text="🎓 Узнать о поступлении", callback_data="final_common_stub")],
        [InlineKeyboardButton(text="🔁 Сменить протокол", callback_data="choose_protocol")]
    ])
    await callback.message.answer_photo(
        photo="https://storage2.bothelp.io/pecherichenko/e3/e317/e317ae09098009ab6053563cc3e39864/IMG_4955.jpeg",
        caption="🔴 Результат: Поверхностный подход\n\n"
                "Без структурированного анализа ваше решение — просто догадка.\n"
                "В КубГУ вас научат готовить стратегические обоснования.\n\n"
                "☑ Анализ миссии: ТРЕБУЕТСЯ ОБУЧЕНИЕ\n\n"
                "Поверхностный подход не годится для стратегической работы. Магистратура КубГУ даст вам научную базу по стратегическому менеджменту.",
        reply_markup=keyboard
    )
    await callback.answer()

# ----- ТРЕК A3: ДИПЛОМАТИЧЕСКАЯ ГОССЛУЖБА (АНАЛИТИКА) -----
@dp.callback_query(F.data == "track_A3")
async def track_A3(callback: CallbackQuery):
    buttons = shuffle_buttons([
        ("📜 Международные договоры XIX-XX веков", "A3_system"),
        ("🤝 Спросить у старших коллег", "A3_slow"),
        ("📢 Отказаться от архивов, импровизировать", "A3_panic")
    ])
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text=t, callback_data=d)] for t, d in buttons])
    await callback.message.answer(
        "🏛 Трек: Дипломатическая госслужба\n🔵 Протокол: Аналитика\n\n"
        "Вводная. Готовится саммит по спорной территории.\n"
        "Ваша задача — поднять архивы и найти прецеденты, усиливающие позицию страны.\n\n"
        "Где искать в первую очередь?\n\n⬇ Ваш ответ, офицер.",
        reply_markup=keyboard
    )
    await callback.answer()

@dp.callback_query(F.data == "A3_system")
async def A3_system(callback: CallbackQuery):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔄 Пройти другой трек", callback_data="protocol_analytics")],
        [InlineKeyboardButton(text="🎓 Узнать о поступлении", callback_data="final_common_stub")],
        [InlineKeyboardButton(text="🔁 Сменить протокол", callback_data="choose_protocol")]
    ])
    await callback.message.answer_photo(
        photo="https://storage2.bothelp.io/pecherichenko/a0/a083/a0834f642b569cd81f0e053a0020baa4/IMG_4954.jpeg",
        caption="🟢 Результат: Основательный подход\n\n"
                "Дипломатия стоит на прецедентах.\n"
                "Курс «Дипломатическая государственная служба в России» (доцент Шалимова О.В.) даёт правовую базу.\n"
                "А профессор Ратушняк О.В., специалист по истории внешней политики, учит анализировать исторический опыт.\n\n"
                "🎧 Анализ миссии: ВЫСОКИЙ УРОВЕНЬ\n\n"
                "Вы мыслите как профессиональный дипломат. Магистратура КубГУ отточит ваши навыки и добавит знаний.",
        reply_markup=keyboard
    )
    await callback.answer()

@dp.callback_query(F.data == "A3_slow")
async def A3_slow(callback: CallbackQuery):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔄 Пройти другой трек", callback_data="protocol_analytics")],
        [InlineKeyboardButton(text="🎓 Узнать о поступлении", callback_data="final_common_stub")],
        [InlineKeyboardButton(text="🔁 Сменить протокол", callback_data="choose_protocol")]
    ])
    await callback.message.answer_photo(
        photo="https://storage2.bothelp.io/pecherichenko/5c/5c68/5c684b41b0186f2f1216fdd1c7eebf00/IMG_4958.jpeg",
        caption="🟡 Результат: Неплохо для начала\n\n"
                "Опыт старших коллег важен. Но дипломат должен уметь работать с документами сам.\n"
                "На курсах Шалимовой О.В. и Ратушняка О.В. вас научат и правовой базе, и историческому анализу.\n\n"
                "🎧 Анализ миссии: ЕСТЬ ПОТЕНЦИАЛ\n\n"
                "Вы на правильном пути, но не хватает самостоятельности. Магистратура КубГУ даст вам структуру и знания.",
        reply_markup=keyboard
    )
    await callback.answer()

@dp.callback_query(F.data == "A3_panic")
async def A3_panic(callback: CallbackQuery):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔄 Пройти другой трек", callback_data="protocol_analytics")],
        [InlineKeyboardButton(text="🎓 Узнать о поступлении", callback_data="final_common_stub")],
        [InlineKeyboardButton(text="🔁 Сменить протокол", callback_data="choose_protocol")]
    ])
    await callback.message.answer_photo(
        photo="https://storage2.bothelp.io/pecherichenko/e3/e317/e317ae09098009ab6053563cc3e39864/IMG_4955.jpeg",
        caption="🔴 Результат: Авантюрист\n\n"
                "Импровизация без подготовки — путь к провалу.\n"
                "Вам нужна теоретическая база.\n\n"
                "🎧 Анализ миссии: ТРЕБУЕТСЯ ОБУЧЕНИЕ\n\n"
                "Без подготовки в дипломатию не идут. Магистратура КубГУ — ваш шанс освоить профессию.",
        reply_markup=keyboard
    )
    await callback.answer()

# ----- ТРЕК A4: ПУБЛИЧНАЯ ДИПЛОМАТИЯ (АНАЛИТИКА) -----
@dp.callback_query(F.data == "track_A4")
async def track_A4(callback: CallbackQuery):
    buttons = shuffle_buttons([
        ("🚫 Заблокировать враждебные СМИ", "A4_panic"),
        ("📝 Написать ответную статью", "A4_slow"),
        ("🎨 Составить карту источников и тональности", "A4_system")
    ])
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text=t, callback_data=d)] for t, d in buttons])
    await callback.message.answer(
        "🎙 Трек: Публичная и культурная дипломатия\n🔵 Протокол: Аналитика\n\n"
        "Вводная. В зарубежных медиа замечен всплеск негативных публикаций о России.\n"
        "Вам нужно проанализировать инфополе и предложить стратегию.\n\n"
        "С чего начнёте?\n\n⬇ Ваш ответ, офицер.",
        reply_markup=keyboard
    )
    await callback.answer()

@dp.callback_query(F.data == "A4_system")
async def A4_system(callback: CallbackQuery):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔄 Пройти другой трек", callback_data="protocol_analytics")],
        [InlineKeyboardButton(text="🎓 Узнать о поступлении", callback_data="final_common_stub")],
        [InlineKeyboardButton(text="🔁 Сменить протокол", callback_data="choose_protocol")]
    ])
    await callback.message.answer_photo(
        photo="https://storage2.bothelp.io/pecherichenko/a0/a083/a0834f642b569cd81f0e053a0020baa4/IMG_4954.jpeg",
        caption="🟢 Результат: Стратег\n\n"
                "Сначала анализ, потом действие.\n"
                "Курс «Публичная дипломатия: теория и практика» (доцент Безрученко М.П.) учит именно такому подходу.\n\n"
                "🎧 Анализ миссии: ВЫСОКИЙ УРОВЕНЬ\n\n"
                "Вы понимаете силу аналитики в публичной дипломатии. Магистратура КубГУ научит вас создавать и продвигать имидж страны.",
        reply_markup=keyboard
    )
    await callback.answer()

@dp.callback_query(F.data == "A4_slow")
async def A4_slow(callback: CallbackQuery):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔄 Пройти другой трек", callback_data="protocol_analytics")],
        [InlineKeyboardButton(text="🎓 Узнать о поступлении", callback_data="final_common_stub")],
        [InlineKeyboardButton(text="🔁 Сменить протокол", callback_data="choose_protocol")]
    ])
    await callback.message.answer_photo(
        photo="https://storage2.bothelp.io/pecherichenko/5c/5c68/5c684b41b0186f2f1216fdd1c7eebf00/IMG_4958.jpeg",
        caption="🟡 Результат: Торопитесь\n\n"
                "Реакция без анализа — стрельба вслепую.\n"
                "В КубГУ вас научат сначала изучать инфополе.\n\n"
                "⚠️ Анализ миссии: ЕСТЬ ПОТЕНЦИАЛ\n\n"
                "Вы знаете, что имидж важен, но пока действуете шаблонно. Магистратура КубГУ раскроет вам современные инструменты.",
        reply_markup=keyboard
    )
    await callback.answer()

@dp.callback_query(F.data == "A4_panic")
async def A4_panic(callback: CallbackQuery):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔄 Пройти другой трек", callback_data="protocol_analytics")],
        [InlineKeyboardButton(text="🎓 Узнать о поступлении", callback_data="final_common_stub")],
        [InlineKeyboardButton(text="🔁 Сменить протокол", callback_data="choose_protocol")]
    ])
    await callback.message.answer_photo(
        photo="https://storage2.bothelp.io/pecherichenko/e3/e317/e317ae09098009ab6053563cc3e39864/IMG_4955.jpeg",
        caption="🔴 Результат: Непрофессионально\n\n"
                "Блокировки — признак слабости.\n"
                "Публичная дипломатия работает иначе.\n\n"
                "🎧 Анализ миссии: ТРЕБУЕТСЯ ОБУЧЕНИЕ\n\n"
                "Запреты — путь в никуда. Магистратура КубГУ научит вас современной публичной дипломатии.",
        reply_markup=keyboard
    )
    await callback.answer()

# ===================== ПРОТОКОЛ ДИПЛОМАТИЯ =====================
@dp.callback_query(F.data == "protocol_diplomacy")
async def diplomacy_choose_track(callback: CallbackQuery):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🏛 Дипломатическая госслужба", callback_data="track_D1")],
        [InlineKeyboardButton(text="🎙 Публичная дипломатия", callback_data="track_D2")],
        [InlineKeyboardButton(text="📊 Экспертная аналитика", callback_data="track_D3")],
        [InlineKeyboardButton(text="🎯 Стратегический менеджмент", callback_data="track_D4")]
    ])
    await callback.message.answer_photo(
        photo="https://storage2.bothelp.io/pecherichenko/ac/ac37/ac37eed66525200b0678a99e60eba1a5/IMG_4963.jpeg",
        caption="🟢 Протокол «Дипломатия» активирован.\n\n"
                "Ваша стихия — переговоры, риск, давление.\n"
                "Выберите направление для прохождения миссии:\n\n"
                "⬇ Нажмите на один из вариантов.",
        reply_markup=keyboard
    )
    await callback.answer()

# ----- ТРЕК D1: ДИПЛОМАТИЧЕСКАЯ ГОССЛУЖБА -----
@dp.callback_query(F.data == "track_D1")
async def track_D1(callback: CallbackQuery):
    buttons = shuffle_buttons([
        ("🤝 Предложить компромиссный вариант", "D1_slow"),
        ("📜 Настаивать на международном праве", "D1_system"),
        ("📢 Занять жёсткую позицию и давить", "D1_panic")
    ])
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text=t, callback_data=d)] for t, d in buttons])
    await callback.message.answer(
        "🏛 Трек: Дипломатическая госслужба\n🟢 Протокол: Дипломатия\n\n"
        "Вводная. Срочный саммит. Обстановка накалена.\n"
        "У вас 5 минут до начала переговоров. Глава делегации спрашивает: какую линию занять?\n\n"
        "⬇ Ваш ответ, офицер.",
        reply_markup=keyboard
    )
    await callback.answer()

@dp.callback_query(F.data == "D1_system")
async def D1_system(callback: CallbackQuery):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔄 Пройти другой трек", callback_data="protocol_diplomacy")],
        [InlineKeyboardButton(text="🎓 Узнать о поступлении", callback_data="final_common_stub")],
        [InlineKeyboardButton(text="🔁 Сменить протокол", callback_data="choose_protocol")]
    ])
    await callback.message.answer_photo(
        photo="https://storage2.bothelp.io/pecherichenko/a0/a083/a0834f642b569cd81f0e053a0020baa4/IMG_4954.jpeg",
        caption="🟢 Результат: Опора на закон\n\n"
                "Сильная позиция.\n"
                "Курс «Дипломатическая государственная служба в России» (доцент Шалимова О.В.) делает акцент именно на праве как основе переговоров.",
        reply_markup=keyboard
    )
    await callback.answer()

@dp.callback_query(F.data == "D1_slow")
async def D1_slow(callback: CallbackQuery):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔄 Пройти другой трек", callback_data="protocol_diplomacy")],
        [InlineKeyboardButton(text="🎓 Узнать о поступлении", callback_data="final_common_stub")],
        [InlineKeyboardButton(text="🔁 Сменить протокол", callback_data="choose_protocol")]
    ])
    await callback.message.answer_photo(
        photo="https://storage2.bothelp.io/pecherichenko/5c/5c68/5c684b41b0186f2f1216fdd1c7eebf00/IMG_4958.jpeg",
        caption="🟡 Результат: Гибкий переговорщик\n\n"
                "Компромисс — это искусство. Но без правовой базы он может быть невыгодным.\n"
                "Курс «Мировая дипломатия и теория переговоров» (доцент Аванесян А.А.) научит вас балансу.",
        reply_markup=keyboard
    )
    await callback.answer()

@dp.callback_query(F.data == "D1_panic")
async def D1_panic(callback: CallbackQuery):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔄 Пройти другой трек", callback_data="protocol_diplomacy")],
        [InlineKeyboardButton(text="🎓 Узнать о поступлении", callback_data="final_common_stub")],
        [InlineKeyboardButton(text="🔁 Сменить протокол", callback_data="choose_protocol")]
    ])
    await callback.message.answer_photo(
        photo="https://storage2.bothelp.io/pecherichenko/e3/e317/e317ae09098009ab6053563cc3e39864/IMG_4955.jpeg",
        caption="🔴 Результат: Риск срыва\n\n"
                "Жёсткая позиция без подготовки — путь к конфликту.\n"
                "В КубГУ вас научат соизмерять давление с последствиями.",
        reply_markup=keyboard
    )
    await callback.answer()

# ----- ТРЕК D2: ПУБЛИЧНАЯ ДИПЛОМАТИЯ -----
@dp.callback_query(F.data == "track_D2")
async def track_D2(callback: CallbackQuery):
    buttons = shuffle_buttons([
        ("🚫 Уйти от ответа, сменить тему", "D2_panic"),
        ("📝 Чётко ответить по заготовке", "D2_slow"),
        ("🎨 Перевести разговор на культурные достижения", "D2_system")
    ])
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text=t, callback_data=d)] for t, d in buttons])
    await callback.message.answer(
        "🎙 Трек: Публичная и культурная дипломатия\n🟢 Протокол: Дипломатия\n\n"
        "Вводная. Вас пригласили на прямой эфир международного телеканала.\n"
        "Журналист задаёт провокационный вопрос о политике России.\n\n"
        "Ваши действия?\n\n⬇ Ваш ответ, офицер.",
        reply_markup=keyboard
    )
    await callback.answer()

@dp.callback_query(F.data == "D2_system")
async def D2_system(callback: CallbackQuery):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔄 Пройти другой трек", callback_data="protocol_diplomacy")],
        [InlineKeyboardButton(text="🎓 Узнать о поступлении", callback_data="final_common_stub")],
        [InlineKeyboardButton(text="🔁 Сменить протокол", callback_data="choose_protocol")]
    ])
    await callback.message.answer_photo(
        photo="https://storage2.bothelp.io/pecherichenko/a0/a083/a0834f642b569cd81f0e053a0020baa4/IMG_4954.jpeg",
        caption="🟢 Результат: Мастер мягкой силы\n\n"
                "Культурная дипломатия — мощнейший инструмент.\n"
                "Курс «Культурная дипломатия» (декан факультета Евтушенко А.С.) учит именно этому.\n\n"
                "🎧 Анализ миссии: ВЫСОКИЙ УРОВЕНЬ\n\n"
                "Вы понимаете силу культурной дипломатии. Магистратура КубГУ научит вас создавать и продвигать имидж страны через культуру и искусство.",
        reply_markup=keyboard
    )
    await callback.answer()

@dp.callback_query(F.data == "D2_slow")
async def D2_slow(callback: CallbackQuery):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔄 Пройти другой трек", callback_data="protocol_diplomacy")],
        [InlineKeyboardButton(text="🎓 Узнать о поступлении", callback_data="final_common_stub")],
        [InlineKeyboardButton(text="🔁 Сменить протокол", callback_data="choose_protocol")]
    ])
    await callback.message.answer_photo(
        photo="https://storage2.bothelp.io/pecherichenko/5c/5c68/5c684b41b0186f2f1216fdd1c7eebf00/IMG_4958.jpeg",
        caption="🟡 Результат: Хорошо, но шаблонно\n\n"
                "Готовые ответы работают, но публичная дипломатия требует гибкости.\n"
                "Курс «Публичная дипломатия» (доцент Безрученко М.П.) раскроет ваш потенциал.\n\n"
                "☑ Анализ миссии: ЕСТЬ ПОТЕНЦИАЛ\n\n"
                "Вы знаете, что имидж важен, но пока действуете шаблонно. Магистратура КубГУ раскроет вам современные инструменты.",
        reply_markup=keyboard
    )
    await callback.answer()

@dp.callback_query(F.data == "D2_panic")
async def D2_panic(callback: CallbackQuery):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔄 Пройти другой трек", callback_data="protocol_diplomacy")],
        [InlineKeyboardButton(text="🎓 Узнать о поступлении", callback_data="final_common_stub")],
        [InlineKeyboardButton(text="🔁 Сменить протокол", callback_data="choose_protocol")]
    ])
    await callback.message.answer_photo(
        photo="https://storage2.bothelp.io/pecherichenko/e3/e317/e317ae09098009ab6053563cc3e39864/IMG_4955.jpeg",
        caption="🔴 Результат: Потеря инициативы\n\n"
                "Уход от вопроса выглядит как слабость.\n"
                "В КубГУ вас научат держать удар в эфире.\n\n"
                "🎧 Анализ миссии: ТРЕБУЕТСЯ ОБУЧЕНИЕ\n\n"
                "Запреты — путь в никуда. Магистратура КубГУ научит вас современной публичной дипломатии.",
        reply_markup=keyboard
    )
    await callback.answer()

# ----- ТРЕК D3: ЭКСПЕРТНАЯ АНАЛИТИКА (ДИПЛОМАТИЯ) -----
@dp.callback_query(F.data == "track_D3")
async def track_D3(callback: CallbackQuery):
    buttons = shuffle_buttons([
        ("📰 Сказать, что данных недостаточно", "D3_panic"),
        ("📈 Выделить главное и дать краткий прогноз", "D3_system"),
        ("🗣 Позвонить эксперту за консультацией", "D3_slow")
    ])
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text=t, callback_data=d)] for t, d in buttons])
    await callback.message.answer(
        "📊 Трек: Экспертная аналитика\n🟢 Протокол: Дипломатия\n\n"
        "Вводная. Переговоры на грани срыва. Вас просят срочно подготовить аналитическую записку.\n"
        "Времени мало. Данные противоречивы.\n\n"
        "Что делать?\n\n⬇ Ваш ответ, офицер.",
        reply_markup=keyboard
    )
    await callback.answer()

@dp.callback_query(F.data == "D3_system")
async def D3_system(callback: CallbackQuery):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔄 Пройти другой трек", callback_data="protocol_diplomacy")],
        [InlineKeyboardButton(text="🎓 Узнать о поступлении", callback_data="final_common_stub")],
        [InlineKeyboardButton(text="🔁 Сменить протокол", callback_data="choose_protocol")]
    ])
    await callback.message.answer_photo(
        photo="https://storage2.bothelp.io/pecherichenko/a0/a083/a0834f642b569cd81f0e053a0020baa4/IMG_4954.jpeg",
        caption="🟢 Результат: Аналитик под давлением\n\n"
                "Вы умеете работать в кризисных условиях.\n"
                "Курс «Прогнозирование и моделирование международных процессов» (канд. ист. наук. Кумпан В.А.) отточит этот навык.\n\n"
                "🎧 Анализ миссии: ВЫСОКИЙ УРОВЕНЬ\n\n"
                "Вы мыслите как профессиональный аналитик. Магистратура КубГУ даст вам инструменты для работы с большими данными, прогнозирования и моделирования международных процессов.",
        reply_markup=keyboard
    )
    await callback.answer()

@dp.callback_query(F.data == "D3_slow")
async def D3_slow(callback: CallbackQuery):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔄 Пройти другой трек", callback_data="protocol_diplomacy")],
        [InlineKeyboardButton(text="🎓 Узнать о поступлении", callback_data="final_common_stub")],
        [InlineKeyboardButton(text="🔁 Сменить протокол", callback_data="choose_protocol")]
    ])
    await callback.message.answer_photo(
        photo="https://storage2.bothelp.io/pecherichenko/5c/5c68/5c684b41b0186f2f1216fdd1c7eebf00/IMG_4958.jpeg",
        caption="🟡 Результат: Разумно, но медленно\n\n"
                "Консультации важны, но в кризисе решение за вами.\n"
                "КубГУ научит самостоятельности.\n\n"
                "☑ Анализ миссии: ЕСТЬ ПОТЕНЦИАЛ\n\n"
                "Вы чувствуете важность анализа, но пока опираетесь на чужое мнение. Магистратура КубГУ научит вас самостоятельно строить прогнозы и работать с данными.",
        reply_markup=keyboard
    )
    await callback.answer()

@dp.callback_query(F.data == "D3_panic")
async def D3_panic(callback: CallbackQuery):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔄 Пройти другой трек", callback_data="protocol_diplomacy")],
        [InlineKeyboardButton(text="🎓 Узнать о поступлении", callback_data="final_common_stub")],
        [InlineKeyboardButton(text="🔁 Сменить протокол", callback_data="choose_protocol")]
    ])
    await callback.message.answer_photo(
        photo="https://storage2.bothelp.io/pecherichenko/e3/e317/e317ae09098009ab6053563cc3e39864/IMG_4955.jpeg",
        caption="🔴 Результат: Неготовность к кризису\n\n"
                "Аналитик не может сказать «не знаю».\n"
                "Магистратура научит вас работать с неполными данными.\n\n"
                "🎧 Анализ миссии: ТРЕБУЕТСЯ ОБУЧЕНИЕ\n\n"
                "Вы действуете импульсивно. К счастью, это поправимо. Магистратура КубГУ научит вас системному анализу и прогнозированию.",
        reply_markup=keyboard
    )
    await callback.answer()

# ----- ТРЕК D4: СТРАТЕГИЧЕСКИЙ МЕНЕДЖМЕНТ (ДИПЛОМАТИЯ) -----
@dp.callback_query(F.data == "track_D4")
async def track_D4(callback: CallbackQuery):
    buttons = shuffle_buttons([
        ("☕ Передать решение наверх", "D4_panic"),
        ("🤝 Встать на сторону сильного партнёра", "D4_slow"),
        ("📋 Провести стратегическую сессию", "D4_system")
    ])
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text=t, callback_data=d)] for t, d in buttons])
    await callback.message.answer(
        "🎯 Трек: Стратегический менеджмент\n🟢 Протокол: Дипломатия\n\n"
        "Вводная. Вы возглавляете рабочий штаб по международному проекту.\n"
        "Сроки горят, бюджет урезан, а два ключевых партнёра из разных стран конфликтуют между собой.\n\n"
        "Ваше решение?\n\n⬇ Ваш ответ, офицер.",
        reply_markup=keyboard
    )
    await callback.answer()

@dp.callback_query(F.data == "D4_system")
async def D4_system(callback: CallbackQuery):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔄 Пройти другой трек", callback_data="protocol_diplomacy")],
        [InlineKeyboardButton(text="🎓 Узнать о поступлении", callback_data="final_common_stub")],
        [InlineKeyboardButton(text="🔁 Сменить протокол", callback_data="choose_protocol")]
    ])
    await callback.message.answer_photo(
        photo="https://storage2.bothelp.io/pecherichenko/a0/a083/a0834f642b569cd81f0e053a0020baa4/IMG_4954.jpeg",
        caption="🟢 Результат: Тонкий дипломат\n\n"
                "Вы чувствуете систему.\n"
                "Профессора Вартаньян Э.Г., Ратушняк О.В., Иванов А.Г. учат именно так — видеть целиком, а не кусками.\n\n"
                "🎧 Анализ миссии: ВЫСОКИЙ УРОВЕНЬ\n\n"
                "Вы показали стратегическое мышление и умение работать в нестабильной среде. Именно этому подходу вас научат профессора Вартаньян Э.Г., Ратушняк О.В., Иванов А.Г. в магистратуре КубГУ.",
        reply_markup=keyboard
    )
    await callback.answer()

@dp.callback_query(F.data == "D4_slow")
async def D4_slow(callback: CallbackQuery):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔄 Пройти другой трек", callback_data="protocol_diplomacy")],
        [InlineKeyboardButton(text="🎓 Узнать о поступлении", callback_data="final_common_stub")],
        [InlineKeyboardButton(text="🔁 Сменить протокол", callback_data="choose_protocol")]
    ])
    await callback.message.answer_photo(
        photo="https://storage2.bothelp.io/pecherichenko/5c/5c68/5c684b41b0186f2f1216fdd1c7eebf00/IMG_4958.jpeg",
        caption="🟡 Результат: Прагматик\n\n"
                "Быстро, но рискованно.\n"
                "Курс «Управление международными проектами» научит балансу.\n\n"
                "☑ Анализ миссии: ЕСТЬ ПОТЕНЦИАЛ\n\n"
                "Решать быстро — важно, но стратегия требует глубины. Магистратура КубГУ расширит ваш подход.",
        reply_markup=keyboard
    )
    await callback.answer()

@dp.callback_query(F.data == "D4_panic")
async def D4_panic(callback: CallbackQuery):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔄 Пройти другой трек", callback_data="protocol_diplomacy")],
        [InlineKeyboardButton(text="🎓 Узнать о поступлении", callback_data="final_common_stub")],
        [InlineKeyboardButton(text="🔁 Сменить протокол", callback_data="choose_protocol")]
    ])
    await callback.message.answer_photo(
        photo="https://storage2.bothelp.io/pecherichenko/e3/e317/e317ae09098009ab6053563cc3e39864/IMG_4955.jpeg",
        caption="🔴 Результат: Поверхностно\n\n"
                "Уход от ответственности — не стратегия.\n"
                "В КубГУ вам помогут научиться решать, а не избегать.\n\n"
                "🎧 Анализ миссии: ТРЕБУЕТСЯ ОБУЧЕНИЕ\n\n"
                "Перекладывать ответственность — не выход. В КубГУ вас научат управлять решениями, а не уходить от них.",
        reply_markup=keyboard
    )
    await callback.answer()

# ===================== ОБЩИЙ ФИНАЛ =====================
@dp.callback_query(F.data == "final_common_stub")
async def final_common_stub(callback: CallbackQuery):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💼 Основная информация о программе", callback_data="info_placeholder")],
        [InlineKeyboardButton(text="👨‍🏫 Задать вопрос о поступлении", callback_data="contacts_placeholder")],
        [InlineKeyboardButton(text="📝 Пройти пробный тест", callback_data="start_test")],
        [InlineKeyboardButton(text="🔄 Вернуться к симуляции", callback_data="choose_protocol")],
        [InlineKeyboardButton(text="🎓 Прожить день магистранта", callback_data="start_day")]
    ])
    await callback.message.answer_photo(
        photo="https://storage2.bothelp.io/pecherichenko/8e/8ed7/8ed7ee41fb372606bdfececd74eda094/IMG_4966.jpeg",
        caption="🎓 Ситуационный центр КубГУ завершает работу.\n\n"
                "Вы прошли испытание и увидели лишь малую часть того, чему учат в магистратуре «Дипломатия: теория, история, практика» Кубанского государственного университета.\n\n"
                "Руководитель программы — Кумпан Вадим Александрович, кандидат исторических наук, доцент кафедры всеобщей истории и международных отношений.\n\n"
                "В преподавательском составе — доктора наук со стажировками в США, Турции, Болгарии.\n\n"
                "⬇ Выберите действие:",
        reply_markup=keyboard
    )
    log_event(callback.from_user.id, callback.from_user.username or "unknown", "Прошёл трек до финала")
    await callback.answer()

# ========== ТЕСТ ==========
@dp.callback_query(F.data == "start_test")
async def start_test(callback: CallbackQuery):
    user_id = callback.from_user.id
    test_score[user_id] = {"score": 0, "current": 1}
    await callback.message.answer(
        "📝 **Пробный тест магистратуры КубГУ**\n\n"
        "**Вопрос 1 из 7.**\n\n"
        "Что из перечисленного является примером «мягкой силы» (soft power) в международных отношениях?\n\n"
        "⬇ Выберите вариант ответа.",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="А) Военное присутствие в регионе", callback_data="test_wrong1a")],
            [InlineKeyboardButton(text="Б) Культурный обмен", callback_data="test_correct1")],
            [InlineKeyboardButton(text="В) Экономические санкции", callback_data="test_wrong1b")]
        ]),
        parse_mode="Markdown"
    )
    log_event(callback.from_user.id, callback.from_user.username or "unknown", "Начал тест")
    await callback.answer()

@dp.callback_query(F.data.startswith("test_"))
async def handle_test(callback: CallbackQuery):
    user_id = callback.from_user.id
    data = test_score.get(user_id, {"score": 0, "current": 1})
    score = data["score"]

    # ===== ВОПРОС 1 =====
    if callback.data == "test_correct1":
        score += 1
        await callback.message.answer(
            "✅ **Верно!**\n\nКультурный обмен — классический пример «мягкой силы». Термин ввёл Джозеф Най. На курсе «Публичная дипломатия: теория и практика» (доцент Безрученко М.П.) вы изучите это глубже.\n\n▶ Нажмите «Дальше»",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="▶ Дальше", callback_data="test_next2")]]),
            parse_mode="Markdown"
        )
    elif callback.data == "test_wrong1a":
        await callback.message.answer(
            "❌ **Неверно.**\n\nВоенное присутствие — это классический инструмент «жёсткой силы». Она опирается на принуждение и страх. Мягкая сила, напротив, работает через привлекательность культуры, ценностей и политических институтов. Именно её изучают на курсе «Публичная дипломатия» в магистратуре КубГУ.\n\n▶ Нажмите «Дальше»",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="▶ Дальше", callback_data="test_next2")]]),
            parse_mode="Markdown"
        )
    elif callback.data == "test_wrong1b":
        await callback.message.answer(
            "❌ **Неверно.**\n\nЭкономические санкции — это тоже «жёсткая сила». Они заставляют, а не привлекают. Мягкая сила — это когда другие страны сами хотят с вами сотрудничать, потому что разделяют ваши ценности и восхищаются вашей культурой.\n\n▶ Нажмите «Дальше»",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="▶ Дальше", callback_data="test_next2")]]),
            parse_mode="Markdown"
        )

    # ===== ВОПРОС 2 =====
    elif callback.data == "test_next2":
        await callback.message.answer(
            "📝 **Вопрос 2 из 7.**\n\n"
            "Как называется процесс, при котором страны передают часть суверенитета наднациональным органам?\n\n"
            "⬇ Выберите вариант ответа.",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="А) Глобализация", callback_data="test_wrong2a")],
                [InlineKeyboardButton(text="Б) Демократизация", callback_data="test_wrong2b")],
                [InlineKeyboardButton(text="В) Интеграция", callback_data="test_correct2")]
            ]),
            parse_mode="Markdown"
        )
    elif callback.data == "test_correct2":
        score += 1
        await callback.message.answer(
            "✅ **Верно!**\n\nИнтеграция — это процесс сближения государств с передачей части полномочий общим органам. Яркий пример — Европейский союз. На курсе «Европейский регионализм» (доцент Аванесян А.А.) вы разберёте это детально.\n\n▶ Нажмите «Дальше»",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="▶ Дальше", callback_data="test_next3")]]),
            parse_mode="Markdown"
        )
    elif callback.data == "test_wrong2a":
        await callback.message.answer(
            "❌ **Неверно.**\n\nГлобализация — это более широкий процесс: рост взаимозависимости стран в экономике, культуре, информации. А вот передача части суверенитета наднациональным органам — это именно интеграция. ЕС — самый яркий пример. На курсе «Европейский регионализм» вы разберёте, как это работает на практике.\n\n▶ Нажмите «Дальше»",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="▶ Дальше", callback_data="test_next3")]]),
            parse_mode="Markdown"
        )
    elif callback.data == "test_wrong2b":
        await callback.message.answer(
            "❌ **Неверно.**\n\nДемократизация — это процесс внедрения демократических принципов и институтов внутри страны. К передаче суверенитета она не имеет прямого отношения. А интеграция — это когда страны добровольно отдают часть полномочий общим органам. Например, страны ЕС передали Брюсселю право регулировать торговлю и миграцию.\n\n▶ Нажмите «Дальше»",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="▶ Дальше", callback_data="test_next3")]]),
            parse_mode="Markdown"
        )

    # ===== ВОПРОС 3 =====
    elif callback.data == "test_next3":
        await callback.message.answer(
            "📝 **Вопрос 3 из 7.**\n\n"
            "Какая концепция лежит в основе теории «демократического мира»?\n\n"
            "⬇ Выберите вариант ответа.",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="А) Гарантия мира во всём мире", callback_data="test_wrong3a")],
                [InlineKeyboardButton(text="Б) Демократия всегда побеждает", callback_data="test_wrong3b")],
                [InlineKeyboardButton(text="В) Демократии не воюют между собой", callback_data="test_correct3")]
            ]),
            parse_mode="Markdown"
        )
    elif callback.data == "test_correct3":
        score += 1
        await callback.message.answer(
            "✅ **Верно!**\n\nТеория демократического мира утверждает: демократии крайне редко или никогда не воюют друг с другом. С авторитарными режимами они конфликтуют, но между собой — нет. На курсе профессора Ратушняка О.В. «Теория международных отношений: современные направления исследований» вы разберёте эту концепцию.\n\n▶ Нажмите «Дальше»",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="▶ Дальше", callback_data="test_next4")]]),
            parse_mode="Markdown"
        )
    elif callback.data == "test_wrong3a":
        await callback.message.answer(
            "❌ **Неверно.**\n\nТеория демократического мира не утверждает, что демократии приносят мир всем. Они вполне воюют с авторитарными режимами. Суть в другом: демократии не воюют между собой. Это подтверждается статистикой за последние два столетия. На курсе профессора Ратушняка О.В. вы разберёте критику этой теории.\n\n▶ Нажмите «Дальше»",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="▶ Дальше", callback_data="test_next4")]]),
            parse_mode="Markdown"
        )
    elif callback.data == "test_wrong3b":
        await callback.message.answer(
            "❌ **Неверно.**\n\nТеория демократического мира ничего не говорит о том, кто побеждает. Она объясняет, почему демократии избегают войн друг с другом. Вьетнам и Афганистан показали, что демократии могут и проигрывать.\n\n▶ Нажмите «Дальше»",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="▶ Дальше", callback_data="test_next4")]]),
            parse_mode="Markdown"
        )

    # ===== ВОПРОС 4 =====
    elif callback.data == "test_next4":
        await callback.message.answer(
            "📝 **Вопрос 4 из 7.**\n\n"
            "Что означает термин «балансирование» (balancing) в теории международных отношений?\n\n"
            "⬇ Выберите вариант ответа.",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="А) Сдерживание сильного через союзы и усилия", callback_data="test_correct4")],
                [InlineKeyboardButton(text="Б) Отказ от союзов и нейтралитет", callback_data="test_wrong4b")],
                [InlineKeyboardButton(text="В) Равное распределение сил между всеми", callback_data="test_wrong4c")]
            ]),
            parse_mode="Markdown"
        )
    elif callback.data == "test_correct4":
        score += 1
        await callback.message.answer(
            "✅ **Верно!**\n\nБалансирование — это когда государство стремится уравновесить силу доминирующей державы: либо наращивая свою мощь (внутреннее балансирование), либо создавая союзы (внешнее балансирование). На курсе «Теория международных отношений» вы разберёте это.\n\n▶ Нажмите «Дальше»",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="▶ Дальше", callback_data="test_next5")]]),
            parse_mode="Markdown"
        )
    elif callback.data == "test_wrong4b":
        await callback.message.answer(
            "❌ **Неверно.**\n\nОтказ от союзов и нейтралитет — это другая стратегия: изоляционизм. А балансирование — это как раз создание коалиций против сильного. Кеннет Уолц, классик неореализма, считал балансирование главным законом международной политики.\n\n▶ Нажмите «Дальше»",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="▶ Дальше", callback_data="test_next5")]]),
            parse_mode="Markdown"
        )
    elif callback.data == "test_wrong4c":
        await callback.message.answer(
            "❌ **Неверно.**\n\nРавное распределение сил между всеми — это утопия. Балансирование — это конкретная стратегия: когда одна держава усиливается, другие объединяются или вооружаются, чтобы её сдержать. Это не про равенство, а про сдерживание гегемона.\n\n▶ Нажмите «Дальше»",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="▶ Дальше", callback_data="test_next5")]]),
            parse_mode="Markdown"
        )

    # ===== ВОПРОС 5 =====
    elif callback.data == "test_next5":
        await callback.message.answer(
            "📝 **Вопрос 5 из 7.**\n\n"
            "Термин «Восточный вопрос» в дипломатической истории XIX века обозначал:\n\n"
            "⬇ Выберите вариант ответа.",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="А) Спор России и Китая о границах", callback_data="test_wrong5a")],
                [InlineKeyboardButton(text="Б) Борьба держав за наследство Турции", callback_data="test_correct5")],
                [InlineKeyboardButton(text="В) Борьба России и Японии за Корею", callback_data="test_wrong5c")],
                [InlineKeyboardButton(text="Г) Статус Босфора после 1945 года", callback_data="test_wrong5d")]
            ]),
            parse_mode="Markdown"
        )
    elif callback.data == "test_correct5":
        score += 1
        await callback.message.answer(
            "✅ **Верно!**\n\n«Восточный вопрос» — это дипломатическая борьба европейских держав за раздел ослабевшей Османской империи на протяжении всего XIX века. В магистратуре КубГУ вы детально разберёте эту тему на курсах по истории дипломатии и российско-турецким отношениям.\n\n▶ Нажмите «Дальше»",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="▶ Дальше", callback_data="test_next6")]]),
            parse_mode="Markdown"
        )
    elif callback.data == "test_wrong5a":
        await callback.message.answer(
            "❌ **Неверно.**\n\nСпор о границах с Китаем — это «Дальневосточный вопрос», а не «Восточный». В дипломатии XIX века «Восток» — это Ближний Восток и Османская империя. Именно её распад породил «Восточный вопрос»: кому достанутся Балканы, проливы и арабские земли.\n\n▶ Нажмите «Дальше»",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="▶ Дальше", callback_data="test_next6")]]),
            parse_mode="Markdown"
        )
    elif callback.data == "test_wrong5c":
        await callback.message.answer(
            "❌ **Неверно.**\n\nРусско-японский конфликт — это часть борьбы за Дальний Восток. А «Восточный вопрос» в XIX веке — это про Османскую империю. «Больной человек Европы», как её называл Николай I. Все великие державы решали: добить или сохранить, и кому что достанется.\n\n▶ Нажмите «Дальше»",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="▶ Дальше", callback_data="test_next6")]]),
            parse_mode="Markdown"
        )
    elif callback.data == "test_wrong5d":
        await callback.message.answer(
            "❌ **Неверно.**\n\nСтатус проливов после Второй мировой — это уже совсем другая эпоха и другая проблема. «Восточный вопрос» возник в конце XVIII века и доминировал в дипломатии весь XIX век. Суть: Османская империя слабеет, кто займёт её место на Балканах и Ближнем Востоке.\n\n▶ Нажмите «Дальше»",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="▶ Дальше", callback_data="test_next6")]]),
            parse_mode="Markdown"
        )

    # ===== ВОПРОС 6 =====
    elif callback.data == "test_next6":
        await callback.message.answer(
            "📝 **Вопрос 6 из 7.**\n\n"
            "Утрехтский мир 1713 года, завершивший войну за Испанское наследство, впервые в истории международного права закрепил принцип:\n\n"
            "⬇ Выберите вариант ответа.",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="А) Свободы мореплавания", callback_data="test_wrong6a")],
                [InlineKeyboardButton(text="Б) Национального самоопределения", callback_data="test_wrong6b")],
                [InlineKeyboardButton(text="В) Баланса сил как основы порядка", callback_data="test_correct6")],
                [InlineKeyboardButton(text="Г) Нерушимости границ", callback_data="test_wrong6d")]
            ]),
            parse_mode="Markdown"
        )
    elif callback.data == "test_correct6":
        score += 1
        await callback.message.answer(
            "✅ **Верно!**\n\nУтрехтский мир впервые письменно закрепил принцип «баланса сил» как цель международных договоров. Испанская и французская короны никогда не должны были объединиться под одним монархом. Этот принцип стал основой европейской дипломатии на два столетия вперёд.\n\n▶ Нажмите «Дальше»",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="▶ Дальше", callback_data="test_next7")]]),
            parse_mode="Markdown"
        )
    elif callback.data == "test_wrong6a":
        await callback.message.answer(
            "❌ **Неверно.**\n\nСвобода морей — это концепция XVII века, сформулированная голландским юристом Гуго Гроцием в трактате «Mare Liberum» (1609). А Утрехтский мир закрепил другое: принцип баланса сил. Испания и Франция никогда не должны объединиться — это записано в договоре.\n\n▶ Нажмите «Дальше»",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="▶ Дальше", callback_data="test_next7")]]),
            parse_mode="Markdown"
        )
    elif callback.data == "test_wrong6b":
        await callback.message.answer(
            "❌ **Неверно.**\n\nНациональное самоопределение — это принцип XX века. Его сформулировал президент США Вудро Вильсон после Первой мировой войны. А в 1713 году о правах наций не думали. Утрехт закрепил баланс сил: никакая держава не должна доминировать в Европе.\n\n▶ Нажмите «Дальше»",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="▶ Дальше", callback_data="test_next7")]]),
            parse_mode="Markdown"
        )
    elif callback.data == "test_wrong6d":
        await callback.message.answer(
            "❌ **Неверно.**\n\nПринцип нерушимости границ закреплён в Хельсинкском заключительном акте 1975 года. До этого границы перекраивались постоянно. Утрехтский мир закрепил другое: баланс сил. Испанская и французская короны разделены навсегда — это первый письменный принцип равновесия в истории.\n\n▶ Нажмите «Дальше»",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="▶ Дальше", callback_data="test_next7")]]),
            parse_mode="Markdown"
        )

    # ===== ВОПРОС 7 =====
    elif callback.data == "test_next7":
        await callback.message.answer(
            "📝 **Вопрос 7 из 7.**\n\n"
            "В чём суть концепции «хартленда» в классической геополитике?\n\n"
            "⬇ Выберите вариант ответа.",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="А) Господство на море — ключ к торговле", callback_data="test_wrong7a")],
                [InlineKeyboardButton(text="Б) Власть над Евразией — власть над миром", callback_data="test_correct7")],
                [InlineKeyboardButton(text="В) Демократии должны нести свои ценности", callback_data="test_wrong7c")],
                [InlineKeyboardButton(text="Г) Мир — это борьба цивилизаций", callback_data="test_wrong7d")]
            ]),
            parse_mode="Markdown"
        )

    # ===== ОБРАБОТКА ОТВЕТОВ НА 7-й ВОПРОС =====
    elif callback.data == "test_correct7":
        score += 1
        final_score = score
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="💼 Основная информация о программе", callback_data="info_placeholder")],
            [InlineKeyboardButton(text="👨‍🏫 Задать вопрос о поступлении", callback_data="contacts_placeholder")],
            [InlineKeyboardButton(text="🔄 Вернуться к симуляции", callback_data="choose_protocol")],
            [InlineKeyboardButton(text="🔄 Пройти тест заново", callback_data="start_test")],
            [InlineKeyboardButton(text="🎓 Прожить день магистранта", callback_data="start_day")]
        ])
        log_event(callback.from_user.id, callback.from_user.username or "unknown", "Завершил тест", result=f"{final_score} из 7", score=final_score)
        await callback.message.answer_photo(
            photo="https://storage2.bothelp.io/pecherichenko/a2/a2f1/a2f1eb3120c4158fe8cb11bb44b99e07/IMG_5030.jpeg",
            caption=f"✅ **Верно!**\n\nХартленд — это сердцевинная земля Евразии. Маккиндер считал: кто контролирует Восточную Европу — командует хартлендом, кто командует хартлендом — командует Мировым островом, кто командует Мировым островом — командует миром. На курсе «Международные отношения в XX–XXI вв. в контексте геополитических концепций» (профессор Ратушняк О.В.) вы разберёте эту теорию и её влияние на мировую политику.\n\n"
                f"🎓 **Тест пройден!**\n\n"
                f"Вы ответили правильно на {final_score} из 7 вопросов.\n\n"
                "Если вам было интересно — представьте, насколько глубже вы разберётесь в этих темах за два года обучения.\n\n"
                "Магистратура «Дипломатия: теория, история, практика» Кубанского государственного университета — это:\n"
                "• Сильный преподавательский состав\n"
                "• Аналитика, переговоры, публичная дипломатия\n"
                "• Специализация по регионам: Европа, Турция, АТР, Черноморский бассейн\n\n"
                "Приходите учиться. Мир ждёт тех, кто в нём разбирается.\n\n"
                "⬇ Выберите действие:",
            reply_markup=keyboard,
            parse_mode="Markdown"
        )

    elif callback.data == "test_wrong7a":
        final_score = score
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="💼 Основная информация о программе", callback_data="info_placeholder")],
            [InlineKeyboardButton(text="👨‍🏫 Задать вопрос о поступлении", callback_data="contacts_placeholder")],
            [InlineKeyboardButton(text="🔄 Вернуться к симуляции", callback_data="choose_protocol")],
            [InlineKeyboardButton(text="🔄 Пройти тест заново", callback_data="start_test")],
            [InlineKeyboardButton(text="🎓 Прожить день магистранта", callback_data="start_day")]
        ])
        log_event(callback.from_user.id, callback.from_user.username or "unknown", "Завершил тест", result=f"{final_score} из 7", score=final_score)
        await callback.message.answer_photo(
            photo="https://storage2.bothelp.io/pecherichenko/a2/a2f1/a2f1eb3120c4158fe8cb11bb44b99e07/IMG_5030.jpeg",
            caption=f"❌ **Неверно.**\n\nЭто концепция «морской силы» адмирала Мэхэна. Он считал, что господство на море — ключ к мировому влиянию. А хартленд — это противоположная теория: Маккиндер утверждал, что решает контроль над сухопутным центром Евразии. Две конкурирующие концепции, которые вы разберёте в магистратуре КубГУ.\n\n"
                f"🎓 **Тест пройден!**\n\n"
                f"Вы ответили правильно на {final_score} из 7 вопросов.\n\n"
                "Если вам было интересно — представьте, насколько глубже вы разберётесь в этих темах за два года обучения.\n\n"
                "Магистратура КубГУ ждёт вас!\n\n⬇ Выберите действие:",
            reply_markup=keyboard,
            parse_mode="Markdown"
        )

    elif callback.data == "test_wrong7c":
        final_score = score
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="💼 Основная информация о программе", callback_data="info_placeholder")],
            [InlineKeyboardButton(text="👨‍🏫 Задать вопрос о поступлении", callback_data="contacts_placeholder")],
            [InlineKeyboardButton(text="🔄 Вернуться к симуляции", callback_data="choose_protocol")],
            [InlineKeyboardButton(text="🔄 Пройти тест заново", callback_data="start_test")],
            [InlineKeyboardButton(text="🎓 Прожить день магистранта", callback_data="start_day")]
        ])
        log_event(callback.from_user.id, callback.from_user.username or "unknown", "Завершил тест", result=f"{final_score} из 7", score=final_score)
        await callback.message.answer_photo(
            photo="https://storage2.bothelp.io/pecherichenko/a2/a2f1/a2f1eb3120c4158fe8cb11bb44b99e07/IMG_5030.jpeg",
            caption=f"❌ **Неверно.**\n\nЭто ближе к теории демократического мира или концепции «распространения демократии». Хартленд — совсем другое. Это географический детерминизм: рельеф и расположение определяют силу государства. Центр Евразии неуязвим для морских держав — вот в чём суть.\n\n"
                f"🎓 **Тест пройден!**\n\n"
                f"Вы ответили правильно на {final_score} из 7 вопросов.\n\n"
                "Магистратура КубГУ ждёт вас!\n\n⬇ Выберите действие:",
            reply_markup=keyboard,
            parse_mode="Markdown"
        )

    elif callback.data == "test_wrong7d":
        final_score = score
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="💼 Основная информация о программе", callback_data="info_placeholder")],
            [InlineKeyboardButton(text="👨‍🏫 Задать вопрос о поступлении", callback_data="contacts_placeholder")],
            [InlineKeyboardButton(text="🔄 Вернуться к симуляции", callback_data="choose_protocol")],
            [InlineKeyboardButton(text="🔄 Пройти тест заново", callback_data="start_test")],
            [InlineKeyboardButton(text="🎓 Прожить день магистранта", callback_data="start_day")]
        ])
        log_event(callback.from_user.id, callback.from_user.username or "unknown", "Завершил тест", result=f"{final_score} из 7", score=final_score)
        await callback.message.answer_photo(
            photo="https://storage2.bothelp.io/pecherichenko/a2/a2f1/a2f1eb3120c4158fe8cb11bb44b99e07/IMG_5030.jpeg",
            caption=f"❌ **Неверно.**\n\nЭто концепция Сэмюэля Хантингтона — «Столкновение цивилизаций». Она появилась в 1990-е годы. А хартленд — это классическая геополитика начала XX века. Маккиндер смотрел на карту и видел: огромная территория в центре Евразии недоступна для флота — и в этом ключ к мировому господству.\n\n"
                f"🎓 **Тест пройден!**\n\n"
                f"Вы ответили правильно на {final_score} из 7 вопросов.\n\n"
                "Магистратура КубГУ ждёт вас!\n\n⬇ Выберите действие:",
            reply_markup=keyboard,
            parse_mode="Markdown"
        )

    # ===== СОХРАНЕНИЕ РЕЗУЛЬТАТА =====
    test_score[user_id] = {"score": score, "current": 1}
    await callback.answer()

# ========== ДЕНЬ МАГИСТРАНТА ==========
@dp.callback_query(F.data == "start_day")
async def start_day(callback: CallbackQuery):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="☕ Встать и пойти на пары", callback_data="day_early")],
        [InlineKeyboardButton(text="😴 Поспать ещё полчаса", callback_data="day_late")]
    ])
    await callback.message.answer_photo(
        photo="https://storage2.bothelp.io/pecherichenko/3d/3df2/3df2bd9dcc521053a3ff1e9a8940d760/IMG_5021.jpeg",
        caption="🎓 **Один день из жизни магистранта КубГУ**\n\n"
                "⏰ 7:30. Будильник. Сегодня лекция по дипломатической истории Европы. Ведёт профессор Иванов А.Г.\n\n"
                "Вы встаёте или ещё пять минут?\n\n⬇ Ваш выбор:",
        reply_markup=keyboard,
        parse_mode="Markdown"
    )
    log_event(callback.from_user.id, callback.from_user.username or "unknown", "Начал день магистранта")
    await callback.answer()

@dp.callback_query(F.data == "day_early")
async def day_early(callback: CallbackQuery):
    await callback.message.answer_photo(
        photo="https://storage2.bothelp.io/pecherichenko/1b/1b5a/1b5acaeafdaa3594065d4577a718a416/IMG_5022.jpeg",
        caption="Вы пришли вовремя. Иванов А.Г. разбирает Берлинский конгресс 1878 года. Вы задаёте вопрос про роль Бисмарка. Профессор кивает: «Хороший вопрос. Именно Бисмарк тогда играл роль честного маклера».\n\n"
                "После пары он советует вам книгу из библиотеки КубГУ.\n\n▶ Нажмите «Дальше»",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="▶ Дальше", callback_data="day_lunch")]])
    )
    await callback.answer()

@dp.callback_query(F.data == "day_late")
async def day_late(callback: CallbackQuery):
    await callback.message.answer_photo(
        photo="https://storage2.bothelp.io/pecherichenko/d8/d8ff/d8ff716ed08c9138224e70c8144cde0a/IMG_4957.jpeg",
        caption="Вы проспали. Тихо заходите в аудиторию. Иванов А.Г. замолкает, смотрит на вас: «Рад, что вы всё же решили присоединиться к европейской дипломатии». Все смеются.\n\n"
                "Вы садитесь, но половина лекции уже пропала. Придётся просить конспект у однокурсницы.\n\n▶ Нажмите «Дальше»",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="▶ Дальше", callback_data="day_lunch")]])
    )
    await callback.answer()

@dp.callback_query(F.data == "day_lunch")
async def day_lunch(callback: CallbackQuery):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🌍 Записаться на Модель ООН", callback_data="day_model")],
        [InlineKeyboardButton(text="📚 Отказаться, пойти в библиотеку", callback_data="day_library")]
    ])
    await callback.message.answer_photo(
        photo="https://storage2.bothelp.io/pecherichenko/f3/f351/f351deb6edeeec07a7e22105b85fe75c/IMG_5023.jpeg",
        caption="🍲 12:30. Столовая КубГУ. Вы с однокурсниками обсуждаете пары. К вам подсаживается студент старшего курса.\n\n"
                "— Слышал, вы на магистратуре МО? Я в прошлом году ездил на стажировку в Турцию по программе университета. Кстати, на следующей неделе Модель ООН. Будете участвовать?\n\n⬇ Ваш выбор:",
        reply_markup=keyboard
    )
    await callback.answer()

@dp.callback_query(F.data == "day_model")
async def day_model(callback: CallbackQuery):
    await callback.message.answer_photo(
        photo="https://storage2.bothelp.io/pecherichenko/e7/e7f0/e7f0504efb5f13733e14c156e742c7e3/IMG_5025.jpeg",
        caption="🌍 Вы записались. Через неделю будете представлять Турцию в Совете Безопасности. Это крутая практика: переговоры, дебаты, резолюции.\n\n"
                "На курсе «Мировая дипломатия и теория переговоров» вас как раз к такому готовят.\n\n▶ Нажмите «Дальше»",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="▶ Дальше", callback_data="day_evening")]])
    )
    await callback.answer()

@dp.callback_query(F.data == "day_library")
async def day_library(callback: CallbackQuery):
    await callback.message.answer_photo(
        photo="https://storage2.bothelp.io/pecherichenko/c2/c2f5/c2f5ca31c3b3a26d00f0877ad9722607/IMG_5024.jpeg",
        caption="📚 Вы идёте в библиотеку КубГУ. Здесь есть доступ к электронным базам данных, архивам и редким изданиям.\n\n"
                "Вы находите монографию Вартаньян Э.Г. по истории Турции. Тишина, лампы, запах книг — идеально.\n\n▶ Нажмите «Дальше»",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="▶ Дальше", callback_data="day_evening")]])
    )
    await callback.answer()

@dp.callback_query(F.data == "day_evening")
async def day_evening(callback: CallbackQuery):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📝 Остаться и дописать записку", callback_data="day_work")],
        [InlineKeyboardButton(text="🎨 Пойти с друзьями на выставку", callback_data="day_exhibition")]
    ])
    await callback.message.answer_photo(
        photo="https://storage2.bothelp.io/pecherichenko/bf/bfdf/bfdfea6ba25dc9be67b7eac929660fea/IMG_5026.jpeg",
        caption="🌙 19:00. Вы дома. Завтра семинар по прогнозированию международных процессов. Нужно дописать аналитическую записку. Но друзья зовут в центр — говорят, в Краснодаре открылся новый выставочный зал.\n\n⬇ Ваш выбор:",
        reply_markup=keyboard
    )
    await callback.answer()

@dp.callback_query(F.data == "day_work")
async def day_work(callback: CallbackQuery):
    await callback.message.answer_photo(
        photo="https://storage2.bothelp.io/pecherichenko/df/df66/df667390746e372efe4df2e7aa7b0ef3/IMG_5028.jpeg",
        caption="📝 Вы дописали записку. На следующий день Кумпан В.А. отметил ваш анализ и предложил участвовать в научной конференции. Первая публикация не за горами.\n\n▶ Нажмите «Дальше»",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="▶ Дальше", callback_data="day_final")]])
    )
    await callback.answer()

@dp.callback_query(F.data == "day_exhibition")
async def day_exhibition(callback: CallbackQuery):
    await callback.message.answer_photo(
        photo="https://storage2.bothelp.io/pecherichenko/04/045f/045f9ac0f7e9029d3dc9c11b785a4198/IMG_5027.jpeg",
        caption="🎨 Вы пошли с друзьями. Выставка оказалась посвящена культурной дипломатии — как раз тема курса Евтушенко А.С. Вы даже сделали заметки для семинара. Совместили приятное с полезным.\n\n▶ Нажмите «Дальше»",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="▶ Дальше", callback_data="day_final")]])
    )
    await callback.answer()

@dp.callback_query(F.data == "day_final")
async def day_final(callback: CallbackQuery):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💼 Основная информация о программе", callback_data="info_placeholder")],
        [InlineKeyboardButton(text="👨‍🏫 Задать вопрос о поступлении", callback_data="contacts_placeholder")],
        [InlineKeyboardButton(text="📝 Пройти пробный тест", callback_data="start_test")],
        [InlineKeyboardButton(text="🔄 Вернуться к симуляции", callback_data="choose_protocol")],
        [InlineKeyboardButton(text="🎓 Прожить день магистранта", callback_data="start_day")]
    ])
    await callback.message.answer_photo(
        photo="https://storage2.bothelp.io/pecherichenko/db/db59/db59335304a94c50d1a9dfb0f50d48a2/IMG_5029.jpeg",
        caption="🎓 **Вот так проходит обычный день магистранта КубГУ.**\n\n"
                "Лекции профессоров-экспертов, работа с реальными кейсами, Модель ООН, научные конференции, библиотека с редкими изданиями и друзья, которые разделяют ваш интерес к миру.\n\n"
                "Хотите так каждый день? Приходите учиться.\n\n⬇ Выберите действие:",
        reply_markup=keyboard,
        parse_mode="Markdown"
    )
    await callback.answer()

# ========== ОСНОВНАЯ ИНФОРМАЦИЯ О ПРОГРАММЕ (ПОЛНАЯ ВЕРСИЯ) ==========
@dp.callback_query(F.data == "info_placeholder")
async def info_main_menu(callback: CallbackQuery):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🎓 Цели и задачи программы", callback_data="info_goals")],
        [InlineKeyboardButton(text="📚 Учебный план (дисциплины)", callback_data="info_disciplines_menu")],
        [InlineKeyboardButton(text="🧠 Формируемые компетенции", callback_data="info_competencies_menu")],
        [InlineKeyboardButton(text="🏢 Практика и стажировки", callback_data="info_practices_menu")],
        [InlineKeyboardButton(text="🧪 Научно-исследовательская работа", callback_data="info_research")],
        [InlineKeyboardButton(text="📋 Условия поступления", callback_data="info_admission")],
        [InlineKeyboardButton(text="📅 Сроки и календарный график", callback_data="info_schedule")],
        [InlineKeyboardButton(text="📞 Контакты и ресурсы", callback_data="contacts_placeholder")],
        [InlineKeyboardButton(text="🔙 Вернуться к симуляции", callback_data="choose_protocol")]
    ])
    await callback.message.answer(
        "💼 **Основная информация о программе**\n\n"
        "Здесь представлена вся информация о практике, компетенциях и учебном процессе.\n\n"
        "⬇ Выберите раздел:",
        reply_markup=keyboard,
        parse_mode="Markdown"
    )
    log_event(callback.from_user.id, callback.from_user.username or "unknown", "Открыл информацию")
    await callback.answer()

@dp.callback_query(F.data == "info_goals")
async def info_goals(callback: CallbackQuery):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔙 Назад к информации об обучении", callback_data="info_placeholder")]
    ])
    await callback.message.answer(
        "🎓 *Цель программы* – подготовка высококвалифицированных международников-аналитиков, способных решать комплексные задачи в области дипломатии, мировой политики и регионоведения.\n\n"
        "*Задачи:*\n"
        "• сформировать системное понимание современных международных отношений;\n"
        "• развить навыки многосторонней дипломатии и аналитики;\n"
        "• подготовить к работе в международных организациях и государственных структурах.",
        reply_markup=keyboard,
        parse_mode="Markdown"
    )
    await callback.answer()

@dp.callback_query(F.data == "info_disciplines_menu")
async def info_disciplines_menu(callback: CallbackQuery):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📓 Обязательная часть", callback_data="disciplines_mandatory")],
        [InlineKeyboardButton(text="📘 Часть, формируемая участниками", callback_data="disciplines_variable")],
        [InlineKeyboardButton(text="📚 Дисциплины по выбору 1", callback_data="disciplines_elective1")],
        [InlineKeyboardButton(text="📚 Дисциплины по выбору 2", callback_data="disciplines_elective2")],
        [InlineKeyboardButton(text="📗 Факультативные дисциплины", callback_data="disciplines_facultative")],
        [InlineKeyboardButton(text="🔙 Назад к информации об обучении", callback_data="info_placeholder")]
    ])
    await callback.message.answer(
        "📚 **Дисциплины магистерской программы**\n\n"
        "Дисциплины разделены на блоки: обязательная часть, вариативная часть, дисциплины по выбору и факультативы.\n\n"
        "👇 *Выберите интересующий блок:*",
        reply_markup=keyboard,
        parse_mode="Markdown"
    )
    await callback.answer()

@dp.callback_query(F.data == "disciplines_mandatory")
async def disciplines_mandatory(callback: CallbackQuery):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔙 Назад ко всем дисциплинам", callback_data="info_disciplines_menu")],
        [InlineKeyboardButton(text="🔙 Назад к информации об обучении", callback_data="info_placeholder")]
    ])
    await callback.message.answer(
        "📓 *Дисциплины (модули). Обязательная часть*\n\n"
        "• Системный анализ и принятие решений в международных отношениях\n"
        "• Управление проектами в международных отношениях\n"
        "• Психология профессиональной деятельности\n"
        "• Теория и практика межкультурной коммуникации в профессиональной сфере\n"
        "• Теория личностного роста: психолого-педагогические технологии в преподавании общественно-научных дисциплин\n"
        "• Роль идеологий в международных процессах и в дипломатии\n"
        "• Актуальные проблемы дипломатической истории Европы\n"
        "• Теория международных отношений: современные направления исследований\n"
        "• Дипломатическая государственная служба в России\n"
        "• Стратегический и инновационный менеджмент в международных организациях\n"
        "• Европейский регионализм\n"
        "• Азиатско-тихоокеанский регион: процессы глобализации и интеграции",
        reply_markup=keyboard,
        parse_mode="Markdown"
    )
    await callback.answer()

@dp.callback_query(F.data == "disciplines_variable")
async def disciplines_variable(callback: CallbackQuery):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔙 Назад ко всем дисциплинам", callback_data="info_disciplines_menu")],
        [InlineKeyboardButton(text="🔙 Назад к информации об обучении", callback_data="info_placeholder")]
    ])
    await callback.message.answer(
        "📘 *Часть, формируемая участниками образовательных отношений*\n\n"
        "• Взаимоотношения России и Турции в контексте международного и регионального сотрудничества\n"
        "• Проблема диалога культур в условиях глобализации\n"
        "• Международные отношения в ХХ в. – начале XXI в. в контексте геополитических концепций, подходов и принципов\n"
        "• Культурная дипломатия\n"
        "• Научно-исследовательский семинар: Прогнозирование и моделирование международных процессов\n"
        "• Содержание и методы преподавания обществознания и истории\n"
        "• Мировая дипломатия и теория переговоров\n"
        "• Публичная дипломатия: теория и практика",
        reply_markup=keyboard,
        parse_mode="Markdown"
    )
    await callback.answer()

@dp.callback_query(F.data == "disciplines_elective1")
async def disciplines_elective1(callback: CallbackQuery):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔙 Назад ко всем дисциплинам", callback_data="info_disciplines_menu")],
        [InlineKeyboardButton(text="🔙 Назад к информации об обучении", callback_data="info_placeholder")]
    ])
    await callback.message.answer(
        "📚 *Дисциплины (модули) по выбору 1*\n\n"
        "• Национальные истории в современной культурной дипломатии: проблемы изучения и преподавания\n"
        "• История международных отношений в средневековье",
        reply_markup=keyboard,
        parse_mode="Markdown"
    )
    await callback.answer()

@dp.callback_query(F.data == "disciplines_elective2")
async def disciplines_elective2(callback: CallbackQuery):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔙 Назад ко всем дисциплинам", callback_data="info_disciplines_menu")],
        [InlineKeyboardButton(text="🔙 Назад к информации об обучении", callback_data="info_placeholder")]
    ])
    await callback.message.answer(
        "📚 *Дисциплины (модули) по выбору 2*\n\n"
        "• Истоки международных отношений в бассейне Черного моря\n"
        "• Восток и Запад: истоки взаимоотношений",
        reply_markup=keyboard,
        parse_mode="Markdown"
    )
    await callback.answer()

@dp.callback_query(F.data == "disciplines_facultative")
async def disciplines_facultative(callback: CallbackQuery):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔙 Назад ко всем дисциплинам", callback_data="info_disciplines_menu")],
        [InlineKeyboardButton(text="🔙 Назад к информации об обучении", callback_data="info_placeholder")]
    ])
    await callback.message.answer(
        "📗 *Факультативные дисциплины*\n\n"
        "• Экономическая дипломатия: региональные и глобальные формы\n"
        "• Организация объединенных наций: основные этапы развития",
        reply_markup=keyboard,
        parse_mode="Markdown"
    )
    await callback.answer()

@dp.callback_query(F.data == "info_competencies_menu")
async def info_competencies_menu(callback: CallbackQuery):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🎓 Универсальные компетенции (УК)", callback_data="comp_uk")],
        [InlineKeyboardButton(text="📊 Общепрофессиональные компетенции (ОПК)", callback_data="comp_opk")],
        [InlineKeyboardButton(text="🏛 Профессиональные компетенции (ПК)", callback_data="comp_pk")],
        [InlineKeyboardButton(text="🔙 Назад к информации об обучении", callback_data="info_placeholder")]
    ])
    await callback.message.answer(
        "🧠 **Компетенции, которые вы приобретёте в магистратуре**\n\n"
        "Универсальные, общепрофессиональные и профессиональные.\n\n"
        "👇 *Выберите группу, чтобы увидеть перечень компетенций:*",
        reply_markup=keyboard,
        parse_mode="Markdown"
    )
    await callback.answer()

@dp.callback_query(F.data == "comp_uk")
async def comp_uk(callback: CallbackQuery):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔙 Назад к перечню компетенций", callback_data="info_competencies_menu")],
        [InlineKeyboardButton(text="🔙 Назад к информации об обучении", callback_data="info_placeholder")]
    ])
    await callback.message.answer(
        "🎓 *Универсальные компетенции (УК)*\n\n"
        "*УК-1:* Способность осуществлять критический анализ глобальных и региональных политических процессов, выявлять причинно-следственные связи, формулировать обоснованные выводы.\n\n"
        "*УК-2:* Готовность к стратегическому планированию внешнеполитической деятельности, включая разработку сценариев развития международной обстановки.\n\n"
        "*УК-3:* Способность вести межкультурный диалог, работать в многонациональных коллективах, учитывая национальные и конфессиональные особенности.\n\n"
        "*УК-4:* Владение иностранными языками для решения профессиональных задач.",
        reply_markup=keyboard,
        parse_mode="Markdown"
    )
    await callback.answer()

@dp.callback_query(F.data == "comp_opk")
async def comp_opk(callback: CallbackQuery):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔙 Назад к перечню компетенций", callback_data="info_competencies_menu")],
        [InlineKeyboardButton(text="🔙 Назад к информации об обучении", callback_data="info_placeholder")]
    ])
    await callback.message.answer(
        "📊 *Общепрофессиональные компетенции (ОПК)*\n\n"
        "*ОПК-1:* Умение анализировать интеграционные процессы (ЕС, ЕАЭС, АСЕАН) и влияние глобальных институтов (ООН, ВТО, МВФ).\n\n"
        "*ОПК-2:* Способность применять количественные методы и качественные подходы в исследованиях международных отношений.\n\n"
        "*ОПК-3:* Навыки подготовки экспертно-аналитических записок, докладов, концепций для государственных структур.",
        reply_markup=keyboard,
        parse_mode="Markdown"
    )
    await callback.answer()

@dp.callback_query(F.data == "comp_pk")
async def comp_pk(callback: CallbackQuery):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔙 Назад к перечню компетенций", callback_data="info_competencies_menu")],
        [InlineKeyboardButton(text="🔙 Назад к информации об обучении", callback_data="info_placeholder")]
    ])
    await callback.message.answer(
        "🏛 *Профессиональные компетенции (ПК)*\n\n"
        "*ПК-1:* Организация дипломатической и консульской работы.\n\n"
        "*ПК-2:* Участие в переговорных треках (двусторонние и многосторонние переговоры, медиация).\n\n"
        "*ПК-3:* Мониторинг международной повестки и раннее предупреждение конфликтов.",
        reply_markup=keyboard,
        parse_mode="Markdown"
    )
    await callback.answer()

@dp.callback_query(F.data == "info_practices_menu")
async def info_practices_menu(callback: CallbackQuery):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💴 Научно-исследовательская работа", callback_data="practice_research")],
        [InlineKeyboardButton(text="💵 Профессиональная практика", callback_data="practice_professional")],
        [InlineKeyboardButton(text="💶 Педагогическая практика", callback_data="practice_pedagogical")],
        [InlineKeyboardButton(text="💷 Преддипломная практика", callback_data="practice_prediploma")],
        [InlineKeyboardButton(text="🔙 Назад к информации об обучении", callback_data="info_placeholder")]
    ])
    await callback.message.answer(
        "🏛 **Ниже – виды практик по программе «Международные отношения»**\n\n"
        "Выберите интересующий вас тип:",
        reply_markup=keyboard,
        parse_mode="Markdown"
    )
    await callback.answer()

@dp.callback_query(F.data == "practice_research")
async def practice_research(callback: CallbackQuery):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔙 Назад к типам практики", callback_data="info_practices_menu")],
        [InlineKeyboardButton(text="🔙 Назад к информации об обучении", callback_data="info_placeholder")]
    ])
    await callback.message.answer(
        "💴 *Научно-исследовательская практика*\n\n"
        "*Цель:* формирование у студентов первичных умений и навыков научно-исследовательской деятельности в сфере международных отношений.\n\n"
        "*Этапы практики:*\n\n"
        "*1. Подготовительный этап (1-ая неделя)* — вводная лекция, инструктаж по технике безопасности, получение индивидуального задания, выбор темы, обоснование актуальности, подбор литературы и источников (на русском и иностранном языке).\n\n"
        "*2. Научно-исследовательский этап (2–4 недели)* — сбор материалов, реферирование источников, обработка и анализ информации, подготовка аналитической записки.\n\n"
        "*3. Подготовка отчёта (5–6 недели)* — оформление отчёта, формирование пакета документов.",
        reply_markup=keyboard,
        parse_mode="Markdown"
    )
    await callback.answer()

@dp.callback_query(F.data == "practice_professional")
async def practice_professional(callback: CallbackQuery):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔙 Назад к типам практики", callback_data="info_practices_menu")],
        [InlineKeyboardButton(text="🔙 Назад к информации об обучении", callback_data="info_placeholder")]
    ])
    await callback.message.answer(
        "💵 *Профессиональная практика*\n\n"
        "*Цель:* формирование навыков и умений магистрантов в проведении профессиональной деятельности в организациях, реализующих функции международных отношений в экономической, политической и социальной сферах.\n\n"
        "*Этапы практики (общая продолжительность – по графику):*\n\n"
        "*1. Подготовительный этап (2 дня)* — установочная конференция, ознакомительная беседа по месту прохождения, инструктаж по технике безопасности.\n\n"
        "*2. Экспериментальный (научно-исследовательский) этап (9 дней)* — сбор информации по теме ВКР, разработка рабочей программы и инструментария, обработка и анализ результатов.\n\n"
        "*3. Заключительный этап (3 дня)* — подготовка отчёта, итоговая конференция с публичным выступлением.",
        reply_markup=keyboard,
        parse_mode="Markdown"
    )
    await callback.answer()

@dp.callback_query(F.data == "practice_pedagogical")
async def practice_pedagogical(callback: CallbackQuery):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔙 Назад к типам практики", callback_data="info_practices_menu")],
        [InlineKeyboardButton(text="🔙 Назад к информации об обучении", callback_data="info_placeholder")]
    ])
    await callback.message.answer(
        "💶 *Педагогическая практика*\n\n"
        "*Цель:* формирование навыков и умений по организации педагогической работы, проведению всего комплекса действий в педагогическом процессе.\n\n"
        "*Этапы практики:*\n\n"
        "*1. Подготовительный этап (3 дня)* — инструктаж, изучение литературы по организации международных мероприятий, командообразование, распределение сфер деятельности, целеполагание.\n\n"
        "*2. Организационный этап (8 дней)* — работа с материалами мероприятия, концептуальная отработка целей, сбор и систематизация информации, выступление с презентацией.\n\n"
        "*3. Подготовка отчёта (3 дня)* — формирование пакета документов.",
        reply_markup=keyboard,
        parse_mode="Markdown"
    )
    await callback.answer()

@dp.callback_query(F.data == "practice_prediploma")
async def practice_prediploma(callback: CallbackQuery):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔙 Назад к типам практики", callback_data="info_practices_menu")],
        [InlineKeyboardButton(text="🔙 Назад к информации об обучении", callback_data="info_placeholder")]
    ])
    await callback.message.answer(
        "💷 *Преддипломная практика*\n\n"
        "*Цель:* формирование навыков и умений в проведении научно-исследовательской работы, анализа и обобщения результатов научного исследования с использованием фундаментальных и прикладных дисциплин, завершение написания магистерской диссертации.\n\n"
        "*Этапы практики:*\n\n"
        "*1. Подготовительный этап (1 неделя)* — установочная лекция, инструктаж по технике безопасности, согласование индивидуального задания, корректировка списка литературы и источников.\n\n"
        "*2. Научно-исследовательский этап (2 недели)* — сбор материалов, работа с источниками правовой, статистической, аналитической информации, систематизация по теме ВКР.\n\n"
        "*3. Подготовка отчёта (1 неделя)* — обработка материала, написание отчёта.\n\n"
        "*4. Предзащита (1 день)* — выступление с презентацией, ответы на вопросы.",
        reply_markup=keyboard,
        parse_mode="Markdown"
    )
    await callback.answer()

@dp.callback_query(F.data == "info_research")
async def info_research(callback: CallbackQuery):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔙 Назад к информации об обучении", callback_data="info_placeholder")]
    ])
    await callback.message.answer(
        "🧪 *Научно-исследовательская работа*\n\n"
        "*Направления исследований:*\n"
        "• Актуальные проблемы дипломатической истории\n"
        "• Процессы глобализации и регионализации (ЕС, АТР, СНГ)\n"
        "• Цифровая дипломатия и «большие данные» в международных отношениях\n"
        "• Внешняя политика России и стран постсоветского пространства\n"
        "• Теория и практика международных переговоров\n"
        "• Культурная и публичная дипломатия\n\n"
        "*Формы работы:*\n"
        "• *Научно-исследовательский семинар:* «Прогнозирование и моделирование международных процессов»\n"
        "• *Курсовая работа:* Не предусмотрена. Основной фокус — на магистерскую диссертацию.\n"
        "• *Участие в конференциях:* Студенты готовят доклады и публикации по результатам своих исследований.\n"
        "• *Работа с источниками:* Анализ документов МИД РФ, ООН, ЕС, а также зарубежных архивных материалов (на русском и иностранных языках).\n\n"
        "*Магистерская диссертация (ВКР):*\n"
        "• Защита ВКР является обязательной частью государственной итоговой аттестации и завершает обучение.\n"
        "• Темы работ связаны с актуальными проблемами международных отношений, дипломатии, регионоведения.\n"
        "• Руководство осуществляют ведущие профессора и практикующие специалисты.",
        reply_markup=keyboard,
        parse_mode="Markdown"
    )
    await callback.answer()

@dp.callback_query(F.data == "info_admission")
async def info_admission(callback: CallbackQuery):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔙 Назад к информации об обучении", callback_data="info_placeholder")]
    ])
    await callback.message.answer(
        "📋 *Условия поступления*\n\n"
        "*Требования к поступающим:*\n"
        "• К освоению программы допускаются лица, имеющие высшее образование любого уровня (бакалавриат, специалитет, магистратура).\n\n"
        "*Вступительные испытания:*\n"
        "• Проводятся в форме, определяемой вузом (как правило, собеседование или экзамен по направлению подготовки «Международные отношения»).\n"
        "• Требования к абитуриенту, вступительные испытания и особые права регламентируются локальным нормативным актом КубГУ.\n\n"
        "*Рекомендации для подготовки:*\n"
        "• Глубокое понимание истории и теории международных отношений.\n"
        "• Владение основами политологии, экономики и права.\n"
        "• Знание иностранного языка (для работы с источниками и литературой).\n\n"
        "*Бюджетные места / Контракт:*\n"
        "• Актуальную информацию о количестве бюджетных мест и стоимости обучения необходимо уточнять в Приемной комиссии КубГУ.",
        reply_markup=keyboard,
        parse_mode="Markdown"
    )
    await callback.answer()

@dp.callback_query(F.data == "info_schedule")
async def info_schedule(callback: CallbackQuery):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔙 Назад к информации об обучении", callback_data="info_placeholder")]
    ])
    await callback.message.answer(
        "📅 *Сроки и календарный график*\n\n"
        "*Сроки обучения:*\n"
        "• Форма обучения: *очная*\n"
        "• Общая продолжительность: *2 года*\n"
        "• Объем программы: *120 зачетных единиц*\n\n"
        "*Календарный график (по семестрам):*\n\n"
        "*1 курс:*\n"
        "• 1 семестр: теоретическое обучение (модули Б1), экзаменационная сессия, *учебная практика*\n"
        "• 2 семестр: теоретическое обучение, экзаменационная сессия, *производственная практика (профессиональная)*\n\n"
        "*2 курс:*\n"
        "• 3 семестр: теоретическое обучение, экзаменационная сессия, *производственная практика (педагогическая)*\n"
        "• 4 семестр: *производственная практика (преддипломная / НИР)*, *государственная итоговая аттестация* (госэкзамен и защита магистерской диссертации)\n\n"
        "*Сроки приёма на обучение по договорам (ключевые даты Приёмной комиссии):*\n"
        "• 20 июня — начало приёма документов\n"
        "• 27 июля — начало вступительных испытаний КубГУ\n"
        "• 12 августа — завершение приёма документов\n"
        "• 17 августа — завершение вступительных испытаний КубГУ\n"
        "• 25 августа — публикация конкурсных списков\n"
        "• 27 августа (до 12:00 мск) — предоставить согласие на зачисление, договор и подтверждение оплаты\n"
        "• 28 августа — издание приказа о зачислении",
        reply_markup=keyboard,
        parse_mode="Markdown"
    )
    await callback.answer()

@dp.callback_query(F.data == "contacts_placeholder")
async def contacts_full(callback: CallbackQuery):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💼 К информации об обучении", callback_data="info_placeholder")],
        [InlineKeyboardButton(text="🔙 Вернуться к симуляции", callback_data="choose_protocol")]
    ])
    await callback.message.answer(
        "📞 **Контакты и ресурсы**\n\n"
        "*Кубанский государственный университет (КубГУ):*\n"
        "📍 Адрес: 350040, г. Краснодар, ул. Ставропольская, 149\n"
        "🌐 Сайт: [www.kubsu.ru](https://www.kubsu.ru)\n"
        "📧 E-mail: abitur@kubsu.ru\n"
        "📞 Приёмная комиссия: 8 (861) 219-95-30\n\n"
        "*Деканат факультета истории, социологии и международных отношений (ФИСМО):*\n"
        "📧 E-mail: decanatfismo@mail.ru\n"
        "📞 Телефон: 8 (861) 219-95-30\n"
        "🔗 Страница программы: [www.kubsu.ru/ru/fismo/410405-mezhdunarodnye-otnosheniya](https://www.kubsu.ru/ru/fismo/410405-mezhdunarodnye-otnosheniya)\n\n"
        "*Руководитель магистерской программы:*\n"
        "👨‍🏫 Кумпан Вадим Александрович\n"
        "• Кандидат исторических наук, доцент, магистр менеджмента, психолог\n"
        "📞 Телефон: +7 909 460 53 39\n\n"
        "*Электронные ресурсы (ЭИОС):*\n"
        "• Среда модульного обучения: [moodle.kubsu.ru](https://moodle.kubsu.ru)\n"
        "• База учебных планов и УМК: [mschool.kubsu.ru](https://mschool.kubsu.ru)\n"
        "• Электронный архив документов: [docspace.kubsu.ru](https://docspace.kubsu.ru)",
        reply_markup=keyboard,
        parse_mode="Markdown"
    )
    await callback.answer()

# ========== ВСПОМОГАТЕЛЬНЫЕ ПЕРЕХОДЫ ==========
@dp.callback_query(F.data == "choose_protocol")
async def back_to_protocol(callback: CallbackQuery):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔵 Протокол «Аналитика»", callback_data="protocol_analytics")],
        [InlineKeyboardButton(text="🟢 Протокол «Дипломатия»", callback_data="protocol_diplomacy")]
    ])
    await callback.message.answer(
        "Выберите протокол связи. Как предпочитаете работать?",
        reply_markup=keyboard
    )
    await callback.answer()

# ========== ВЕБ-СЕРВЕР ДЛЯ RENDER ==========
app = Flask(__name__)

@app.route('/')
@app.route('/health')
def health():
    return "Bot is running", 200

def run_web():
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

# Запускаем веб-сервер в отдельном потоке
threading.Thread(target=run_web, daemon=True).start()

# ========== ЗАПУСК ==========
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
