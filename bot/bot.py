import os
import logging
import requests
from telegram import ReplyKeyboardRemove, Update, InlineKeyboardButton, \
    ReplyKeyboardMarkup, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, \
    ContextTypes, ConversationHandler, MessageHandler, filters, CallbackQueryHandler


TELEGRAM_TOKEN = os.environ['TELEGRAM_TOKEN']
API_URL = os.environ['API_URL']

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO)
logger = logging.getLogger(__name__)

# Этапы общения
MAIN_MENU = 1 # вернуться в меню
NAME = 2  # Состояние для запроса имени пользователя
# Этапы для заказа коктейля
WAITING_FOR_DRINK = 3 # Состояние для ожидания ID или названия
RETRY_OR_EXIT = 4  # Новое состояние для обработки кнопок retry/exit
CONFIRM_ORDER = 5
# Этапы общения для подбора коктейля
SIZE = 6  # Размер
STRENGTH = 7  # Крепость
TASTE = 8 

# Получение меню через API
def get_menu():
    try:
        response = requests.get(f"{API_URL}/menu/")
        response.raise_for_status()
        return response.json() if response.status_code == 200 else []
    except requests.exceptions.RequestException as e:
        logging.error(f"Ошибка при запросе меню: {e}")
        return []


# Получение информации о пользователе через API
def get_user(user_id):
    response = requests.get(f"{API_URL}/users/{user_id}/")
    return response.json() if response.status_code == 200 else None

# Добавление пользователя через API
def add_user(user_id, username):
    user_data = {"id": user_id, "username": username}
    response = requests.post(f"{API_URL}/users/", json=user_data)
    return response.json()


# Создание заказа через API
def create_order(user_id, drink_id):
    order_data = {
        "user_id": user_id,
        "drink_id": drink_id,
    }
    response = requests.post(f"{API_URL}/orders/", json=order_data)
    return response.json()

def filter_cocktails(selected_filters):
    response = requests.get(f"{API_URL}/filtered_cocktails/", params=selected_filters)
    return response.json() if response.status_code == 200 else None


# Функция для поиска напитка по ID или названию
def find_drink(query):
    menu_items = get_menu()
    if not menu_items:
        return None  # Если меню недоступно

    # Попробуем найти напиток
    try:
        # Ищем по ID (если ввели число)
        drink_id = int(query)
        for item in menu_items:
            if item['id'] == drink_id:
                return item
    except ValueError:
        # Если это не число, ищем по названию
        for item in menu_items:
            if item['name'].lower() == query.lower():
                return item

    return None  # Напиток не найден

# Главное меню
def get_main_menu():
    keyboard = [["Что у вас есть?👀", "Заказать🍸"], ["Подобрать✨", "Мне повезёт!🍀"]]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

async def main_menu_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_message = update.message.text.strip().lower()

    if user_message == "что у вас есть?👀":
        return await drinks(update, context)
    elif user_message == "заказать🍸":
        return await start_order(update, context)
    elif user_message == "подобрать✨":
        return await start_pick(update, context)
    elif user_message == "мне повезёт!🍀":
        return await random_drink(update, context)
    else:
        await update.message.reply_text(
            "Я не понял вашу команду😰 Используйте кнопки меню или команду /cancel, если всё сломалось.",
            reply_markup=get_main_menu())
        return MAIN_MENU

# Основной обработчик
async def handle_conversation(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    current_state = context.user_data.get('current_state', MAIN_MENU)

    if current_state == MAIN_MENU:
        return await main_menu_handler(update, context)
    elif current_state == WAITING_FOR_DRINK:
        return await handle_drink_query(update, context)
    elif current_state == RETRY_OR_EXIT:
        return await retry_or_exit(update, context)
    elif current_state == CONFIRM_ORDER:
        return await retry_or_exit(update, context)
    elif current_state == SIZE:
        return await handle_pick(update, context)
    elif current_state == STRENGTH:
        return await handle_pick(update, context)
    elif current_state == TASTE:
        return await handle_pick(update, context)
    else:
        await update.message.reply_text("Неизвестное состояние", reply_markup=get_main_menu())
        return MAIN_MENU

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_id = update.message.from_user.id
    user_data = get_user(user_id)

    if user_data is None:
        await update.message.reply_text(
            "Привет! Пожалуйста, введи свое имя!",
            reply_markup=ReplyKeyboardMarkup([["Отмена"]], resize_keyboard=True))
        return NAME
    else:
        await update.message.reply_text(
            f"Привет, {user_data['username']}! Ты уже зарегистрирован🎉",
            reply_markup=get_main_menu())
        return MAIN_MENU
        
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Прерывание
    """
    await update.message.reply_text(
        "Прервано. Вот тебе клавиатурка",
        reply_markup=get_main_menu()
    )
    return MAIN_MENU

# меню коктейлей
async def drinks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    menu_items = get_menu()
    if menu_items:
        menu_text = "🎉 Меню напитков:\n" + "\n".join([f"{item['id']}. {item['name']}: {item['components']}" for item in menu_items])
        await update.message.reply_text(menu_text)
    else:
        await update.message.reply_text("Меню недоступно.")
    return MAIN_MENU

# Обработчик команды /order или кнопки "Заказать"
async def start_order(update: Update,
                      context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text(
        "Введите ID или название напитка, который хотите заказать.",
         reply_markup=ReplyKeyboardRemove())
    return WAITING_FOR_DRINK

async def handle_drink_query(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.message.text.strip()
    drink = find_drink(query)
    print(drink)
    if drink:
        drink_text = f"{drink['name']} — {drink['components']}"
        keyboard = [[InlineKeyboardButton("Заказать✅", callback_data=f"order_{drink['id']}")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(f"Вы выбрали: {drink_text}", reply_markup=reply_markup)
        return CONFIRM_ORDER
    else:
        await update.message.reply_text(
            "Напиток с таким ID или названием не найден😥 Ты можешь:\n"
            "- Попробовать ввести другой ID или название.\n"
            "- Вернуться в главное меню.",
            reply_markup=get_retry_menu())
        return RETRY_OR_EXIT
    
# Клавиатура при ошибке ввода
def get_retry_menu():
    keyboard = [
        [InlineKeyboardButton("Попробовать ещё раз", callback_data="Попробовать ещё раз")],
        [InlineKeyboardButton("Выйти в главное меню", callback_data="Выйти в главное меню")],
    ]
    return InlineKeyboardMarkup(keyboard)

async def retry_or_exit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "Попробовать ещё раз":
        await query.edit_message_text("Введи ID или название напитка:", reply_markup=ReplyKeyboardRemove())
        return WAITING_FOR_DRINK
    elif query.data == "Выйти в главное меню":
        await query.edit_message_text("Ты в главном меню.", reply_markup=get_main_menu())
        return MAIN_MENU
    else:
        await query.edit_message_text(
            "Пожалуйста, используй кнопки ниже.",
            reply_markup=get_retry_menu()
        )
        return RETRY_OR_EXIT

async def confirm_order(update: Update,
                        context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()  # Обязательно отправляем ответ на callback

    # Получаем ID напитка из callback_data
    drink_id = int(query.data.split("_")[1])
    user_id = query.from_user.id

    # Создаём заказ на 1 единицу выбранного напитка
    order_response = create_order(user_id, drink_id)
    cocktail = find_drink(drink_id)
    if "status" in order_response:
        await query.edit_message_text(
            f"Заказ на коктейль {cocktail['name']} успешно создан!🍹")
    else:
        await query.edit_message_text("Ошибка при создании заказа😭")

    await context.bot.send_message(
        chat_id=query.from_user.id,
        text="Что-нибудь ещё?",
        reply_markup=get_main_menu()
    )
    return MAIN_MENU

# Обработка имени пользователя
async def receive_name(update: Update,
                       context: ContextTypes.DEFAULT_TYPE) -> int:
    user_id = update.message.from_user.id
    username = update.message.text.strip()
    
    # Проверка на команду отмены
    if username.lower() == "отмена":
        await update.message.reply_text(
            "Регистрация отменена. Для повторной попытки используй /start",
            reply_markup=ReplyKeyboardRemove()
        )
        return ConversationHandler.END
    
    if not username:
        await update.message.reply_text(
            "Не будь так самокритичен")
        return NAME
    
    # Проверка валидности имени
    if len(username) < 2:
        await update.message.reply_text(
            "Имя должно содержать хотя бы 2 символа 🙃"
        )
        return NAME
    
    if len(username) > 50:
        await update.message.reply_text(
            "Ты серьёзно?"
        )
        return NAME

    add_user_response = add_user(user_id, username)

    if add_user_response.get("status") == "User added":
        await update.message.reply_text(
            f"Добро пожаловать, {username}! Регистрация успешно завершена. 🎉",
            reply_markup=get_main_menu())
    else:
        await update.message.reply_text("Ошибка при регистрации пользователя.")

    return MAIN_MENU

# Обновленная функция start_pick
async def start_pick(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['current_state'] = SIZE
    context.user_data['selected_filters'] = {}
    
    keyboard = [
        [InlineKeyboardButton("S", callback_data='S')],
        [InlineKeyboardButton("M", callback_data='M')],
        [InlineKeyboardButton("L", callback_data='L')],
        [InlineKeyboardButton("шот", callback_data='ШОТ')],
        [InlineKeyboardButton("Далее", callback_data='Далее')],
    ]
    await update.message.reply_text(
        "Выбери размер коктейля:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    return SIZE

async def handle_pick(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    
    current_state = context.user_data.get('current_state')
    user_choice = query.data
    print(f"CallbackQuery: {query.data}")
    # Добавим логирование для отладки
    print(f"Current state: {current_state}")
    print(f"User choice: {user_choice}")

    if current_state == SIZE:
        context.user_data['selected_filters'] = {'size': user_choice}
        keyboard = [
            [InlineKeyboardButton("Лёгкий", callback_data='Лёгкий')],
            [InlineKeyboardButton("Средний", callback_data='Средний')],
            [InlineKeyboardButton("Крепкий", callback_data='Крепкий')],
            [InlineKeyboardButton("Сверхрепкий", callback_data='Сверх крепкий')],
            [InlineKeyboardButton("Безалкогольный", callback_data='Б/А')],
            [InlineKeyboardButton("Далее", callback_data='Далее')],
        ]
        await query.edit_message_text(
            "Выбери крепость коктейля:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        context.user_data['current_state'] = STRENGTH
        return STRENGTH
        
    elif current_state == STRENGTH:
        context.user_data['selected_filters']['strength'] = user_choice
        keyboard = [
            [InlineKeyboardButton("Сладкий", callback_data='Сладкий')],
            [InlineKeyboardButton("Кислый", callback_data='Кислый')],
            [InlineKeyboardButton("Горький", callback_data='Горький')],
            [InlineKeyboardButton("Чистый", callback_data='Чистый')],
            [InlineKeyboardButton("Далее", callback_data='Далее')],
        ]
        await query.edit_message_text(
            "Выбери вкус коктейля:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        context.user_data['current_state'] = TASTE
        return TASTE
        
    elif current_state == TASTE:
        context.user_data['selected_filters']['taste'] = user_choice
        selected_filters = context.user_data['selected_filters']
        
        # Получаем отфильтрованные коктейли
        cocktails = filter_cocktails(selected_filters)
        
        if selected_filters == {'size': 'L', 'strength': 'Крепкий', 'taste': 'Чистый'}:
            await query.message.reply_text(
                "Ты что, из канистры хлебнуть хочешь?",
                reply_markup=get_main_menu()
            )
            context.user_data['current_state'] = MAIN_MENU
            return MAIN_MENU
        
        if cocktails:
            cocktails_text = "\n".join([
                f"{cocktail['id']}. {cocktail['name']} - {cocktail['components']}" 
                for cocktail in cocktails
            ])
            await query.edit_message_text(
                f"Подходящие коктейли:\n{cocktails_text}"
            )
        else:
            await query.edit_message_text(
                "К сожалению, подходящих коктейлей не найдено."
            )
        
        # Отправляем новое сообщение с главным меню
        await query.message.reply_text(
            "Попробуем ещё раз?",
            reply_markup=get_main_menu()
        )
        context.user_data['current_state'] = MAIN_MENU
        return MAIN_MENU

# Команда "Мне повезёт!"
async def random_drink(update: Update, context: ContextTypes.DEFAULT_TYPE):
    menu_items = get_menu()
    if not menu_items:
        await update.message.reply_text("Меню недоступно.")
        return

    import random
    random_item = random.choice(menu_items)
    await update.message.reply_text(
        f"Попробуйте: {random_item['name']}!\nСостав: {random_item['components']}\n"
        f"Чтобы заказать, введите /order {random_item['id']} или нажмите 'Мне повезёт!' снова.",
        reply_markup=get_main_menu())
    return MAIN_MENU

# Основной ConversationHandler
conversation_handler = ConversationHandler(
    entry_points=[CommandHandler('start', start)],
    states={
        NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_name)],
        MAIN_MENU: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_conversation)],
        WAITING_FOR_DRINK: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_drink_query)],
        RETRY_OR_EXIT: [CallbackQueryHandler(retry_or_exit)],
        CONFIRM_ORDER: [CallbackQueryHandler(confirm_order)],
        SIZE: [CallbackQueryHandler(handle_pick)],
        STRENGTH: [CallbackQueryHandler(handle_pick)],
        TASTE: [CallbackQueryHandler(handle_pick)],
    },
    fallbacks=[CommandHandler('cancel', cancel)],
)

# Запуск бота
def main():
    application = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    application.add_handler(conversation_handler)
    application.run_polling()

if __name__ == "__main__":
    main()