import os
import json
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from telegram import Chat
import logging
from settings import TOKEN, SCAN_CHANNEL_ID, NOTIFICATION_CHAT_ID

# Путь к файлу для сохранения словаря
FILE_PATH = "keywords_data.json"
SECONDARY_FILE_PATH = "secondary_keywords_data.json"



# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

keywords = set()

def load_keywords():
    """Загрузка словаря из файла."""
    try:
        with open(FILE_PATH, 'r') as file:
            data = json.load(file)
            return {k: set(v) for k, v in data.items()}
    except (json.JSONDecodeError, FileNotFoundError):
        print("Ошибка при чтении файла или файл не найден. Используется пустой словарь.")
        return {}


def load_secondary_keywords():
    """Загрузка второго словаря из файла."""
    try:
        with open(SECONDARY_FILE_PATH, 'r') as file:
            data = json.load(file)
            return {k: set(v) for k, v in data.items()}
    except (json.JSONDecodeError, FileNotFoundError):
        print("Ошибка при чтении второго файла или файл не найден. Используется пустой словарь.")
        return {}


# Загрузка словаря из файла при запуске
keywords_dict = load_keywords()
secondary_keywords_dict = load_secondary_keywords()  # Загрузим второй словарь аналогичным образом



def save_keywords():
    """Сохранение словаря в файл."""
    # Преобразование множеств в списки для сохранения в JSON
    with open(FILE_PATH, 'w') as file:
        json.dump({k: list(v) for k, v in keywords_dict.items()}, file)

def save_secondary_keywords():
    """Сохранение второго словаря в файл."""
    with open(SECONDARY_FILE_PATH, 'w') as file:
        json.dump({k: list(v) for k, v in secondary_keywords_dict.items()}, file)


def start(update, context):
    commands = """
    /start - Запуск бота.
    /add_keyword <ключ> <значение1> <значение2> ... - Добавление ключевых слов в первый словарь.
    /add_secondary_keyword <ключ> <значение1> <значение2> ... - Добавление ключевых слов во второй словарь.
    /help - Вывод мануала.
    """
    update.message.reply_text(commands)

def help_command(update, context):
    with open("readme.txt", "r",encoding="utf-8") as file:
        manual = file.read()
    update.message.reply_text(manual)


def add_keyword(update, context):
    keyword, *values = update.message.text.split()[1:]
    if keyword not in keywords_dict:
        keywords_dict[keyword] = set()
    keywords_dict[keyword].update(values)
    save_keywords()
    update.message.reply_text(f"Ключ '{keyword}' добавлен с значениями: {', '.join(values)}.")
    
def add_secondary_keyword(update, context):
    keyword, *values = update.message.text.split()[1:]
    if keyword not in secondary_keywords_dict:
        secondary_keywords_dict[keyword] = set()
    secondary_keywords_dict[keyword].update(values)
    save_secondary_keywords()
    update.message.reply_text(f"Во второй словарь добавлен ключ '{keyword}' с значениями: {', '.join(values)}.")


def handle_message(update, context):
    if update.channel_post:
        message_text = update.channel_post.text

        # Поиск ключевых слов из первого словаря
        found_primary_keywords = [keyword for keyword, values in keywords_dict.items() if any(value in message_text for value in values)]

        # Поиск ключевых слов из второго словаря
        found_secondary_keywords = [keyword for keyword, values in secondary_keywords_dict.items() if any(value in message_text for value in values)]

        if found_primary_keywords or found_secondary_keywords:
            response = " ".join(found_primary_keywords) + " : " + " ".join(found_secondary_keywords) + "\n" + update.channel_post.link
            context.bot.send_message(chat_id=NOTIFICATION_CHAT_ID, text=response)


def main():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("add_keyword", add_keyword))
    dp.add_handler(CommandHandler("add_secondary_keyword", add_secondary_keyword))
    dp.add_handler(CommandHandler("help", help_command))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
