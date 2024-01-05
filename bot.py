# * Importing libraries
import json
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

# * Importing modules
from database import db_manager
from moogold import ServiceMoogold
from jollymax import ServiceJollymax
from config import TG_TOKEN, TG_TOKEN_TEST, TG_ADMINS, JM_URI, JM_MERCHANT_ID, JM_MERCHANT_APP_ID, MG_URI, MG_PARTNER_ID, MG_SECRET_KEY
from logger import bot_log, err_log


class Form(StatesGroup):
    waiting_for_category_id = State()
    waiting_for_product_id = State()

bot = Bot(token=TG_TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())

async def get_main_keyboard():
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    buttons = [
        KeyboardButton(text="📦 Баланс Jollymax"),
        KeyboardButton(text="📊 Статистика"),
        KeyboardButton(text="📞 Связаться с нами")
    ]
    keyboard.add(*buttons)
    return keyboard

async def get_stat_keyboard():
    keyboard_stat = ReplyKeyboardMarkup(resize_keyboard=True)
    buttons_stat = [
        KeyboardButton(text="📊 Статистика по Vipayment"),
        KeyboardButton(text="📊 Статистика по Moogold"),
        KeyboardButton(text="📊 Статистика по Jollymax"),
        KeyboardButton(text="🔙 Назад")
    ]
    keyboard_stat.add(*buttons_stat)
    return keyboard_stat

async def cmd_start(message: types.Message):
    await message.answer("👋🏼 Привет, администратор! Что будем делать?", reply_markup=await get_main_keyboard())

@dp.message_handler(commands=['help'])
async def helping(message: types.Message):
    await message.answer("📘 Список команд:\n\n/help - получение списка команд\n/list - получение продукта\n/id - получение точного продукта")

@dp.message_handler(commands=['list'], state="*")
async def list_command_handler(message: types.Message):
    await message.answer("""📋 Введите номер категории:\n\n
Список номеров категорий:\n
Direct-top up products: 50\n
Other Gift Cards: 51\n
Amazon Gift Cards: 1391\n
Apple Music: 1444\n
Garena Shells: 766\n
Google Play: 538\n
iTunes Gift Card: 2433\n
League of Legends: 1223\n
Netflix: 874\n
PSN: 765\n
Razer Gold: 451\n
Riot Access Code: 1261\n
Spotify: 992\n
Steam: 993\n
Apex Legends: 2377
    """)
    await Form.waiting_for_category_id.set()

@dp.message_handler(commands=['id'], state="*")
async def id_command_handler(message: types.Message):
    await message.answer("📋 Введите ID продукта:")
    await Form.waiting_for_product_id.set()

@dp.message_handler(state=Form.waiting_for_category_id)
async def process_category_id(message: types.Message, state: FSMContext):
    MAX_MESSAGE_LENGTH = 4096
    category_id = int(message.text)
    await state.finish()
    await message.answer(f"Вы ввели category_id: {category_id} обработка...")
    try:
        products = await ServiceMoogold.get_products(uri=MG_URI, api_key=MG_SECRET_KEY, api_id=MG_PARTNER_ID, category_id=category_id)
        if products["status"] == "success":
            formatted_json = json.dumps(products["data"], indent=2, ensure_ascii=False)
            
            if len(formatted_json) <= MAX_MESSAGE_LENGTH:
                await message.answer(f"📋 Список продуктов:\n{formatted_json}")
            else:
                chunks = [formatted_json[i:i+MAX_MESSAGE_LENGTH] for i in range(0, len(formatted_json), MAX_MESSAGE_LENGTH)]
                for chunk in chunks:
                    await message.answer(f"📋 Список продуктов:\n{chunk}")
            
        else:
            err_log(f"[!] Ошибка при получении списка продуктов: {products}")
            await message.answer("Ошибка: продукты не найдены.")
    except Exception as error:
        await message.answer(f"Произошла ошибка: {error}")

@dp.message_handler(state=Form.waiting_for_product_id)
async def process_product_id(message: types.Message, state: FSMContext):
    product_id = int(message.text)
    await state.finish()
    await message.answer(f"Вы ввели product_id: {product_id} обработка...")
    try:
        products = await ServiceMoogold.get_find_product(uri=MG_URI, api_key=MG_SECRET_KEY, api_id=MG_PARTNER_ID, product_id=product_id)
        if products["status"] == "success":
            formatted_json = json.dumps(products["data"], indent=2, ensure_ascii=False)
            await message.answer(f"📋 Список товаров:\n{formatted_json}", parse_mode="Markdown")
        else:
            err_log(f"[!] Ошибка при получении списка товаров: {products}")
            await message.answer("Ошибка: товары не найдены.")
    except Exception as error:
        await message.answer(f"Произошла ошибка: {error}")

async def send_message_order(message_text):
    for user_id in TG_ADMINS:
        try:
            await bot.send_message(user_id, message_text)
            bot_log(f"[+] Сообщение отправлено администратору: {user_id}")
        except Exception as error:
            err_log(f"[!] Ошибка при отправке сообщения администратору: {error}")
            continue

async def handle_req_balance(message: types.Message):
    try:
        bot_log(f"[+] Получен запрос на баланс")
        balance = await ServiceJollymax.balance_query(JM_URI, JM_MERCHANT_APP_ID, JM_MERCHANT_ID)
        await message.answer(f"💰 Баланс: ${balance['jm_balance']}.")
    except Exception as error:
        err_log(f"[!] Ошибка при получении баланса: {error}")
        await message.answer(f"Произошла ошибка: {error}")

async def handle_req_stat(message: types.Message):
    vp_count = await db_manager.getCountOrderVP()
    mg_count = await db_manager.getCountOrderMG()
    jm_count = await db_manager.getCountOrderJM()
    total_count = vp_count + mg_count + jm_count
    await message.answer(f"📊 Общая статистика: {total_count}\n\nВсего заказов VIPAYMENT: {vp_count}\nВсего заказов MOOGOLD: {mg_count}\nВсего заказов JOLLYMAX: {jm_count}", reply_markup=await get_stat_keyboard())
    bot_log(f"[+] Получен запрос на статистику")

async def handle_contact(message: types.Message):
    await message.answer("✒️ О Нас:\n\nСервис: Skyshop API\nМаршрут: https://skydev.host/v1/\nАвтор: Daniar Jabagin\nВерсия: 2.4.1\nAdmin: @pashsky\nDeveloper: @daniar_state")

async def format_orders(orders):
    return "\n".join([f"{idx + 1}. UserID: {order['user_id']}, ID: {order['order_id']}, Статус: {order['status']}" for idx, order in enumerate(orders)])

async def send_large_message(chat_id, text, max_length=4000):
    while text:
        part = text[:max_length]
        await bot.send_message(chat_id, part)
        text = text[max_length:]
        
async def handle_show_vp(message: types.Message):
    orders = await db_manager.getOrderByStatusVP()
    count = len(orders)
    orders_formatted = await format_orders(orders)
    await message.answer(f"📊 Статистика VIPAYMENT: {count}\n\n{orders_formatted}")
    bot_log(f"[+] Получен запрос на статистику VIPAYMENT")

async def handle_show_mg(message: types.Message):
    orders = await db_manager.getOrderByStatusMG()
    count = len(orders)
    orders_formatted = await format_orders(orders)
    await message.answer(f"📊 Статистика MOOGOLD: {count}\n\n{orders_formatted}")
    bot_log(f"[+] Получен запрос на статистику MOOGOLD")

async def handle_show_jm(message: types.Message):
    orders = await db_manager.getOrderByStatusJM()
    count = len(orders)
    orders_formatted = await format_orders(orders)
    await message.answer(f"📊 Статистика JOLLYMAX: {count}\n\n{orders_formatted}")
    bot_log(f"[+] Получен запрос на статистику JOLLYMAX")

async def handle_back(message: types.Message):
    await message.answer("🔙 Вы вернулись в главное меню.", reply_markup=await get_main_keyboard())

def setup(dp: Dispatcher):
    dp.register_message_handler(cmd_start, commands=['start'])
    dp.register_message_handler(helping, commands=['help'])
    dp.register_message_handler(handle_req_balance, text="📦 Баланс Jollymax")
    dp.register_message_handler(handle_req_stat, text="📊 Статистика")
    dp.register_message_handler(handle_contact, text="📞 Связаться с нами")
    dp.register_message_handler(handle_show_vp, text="📊 Статистика по Vipayment")
    dp.register_message_handler(handle_show_mg, text="📊 Статистика по Moogold")
    dp.register_message_handler(handle_show_jm, text="📊 Статистика по Jollymax")
    dp.register_message_handler(handle_back, text="🔙 Назад")

setup(dp)