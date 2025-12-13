import logging
logging.basicConfig(level=logging.DEBUG)

from telethon import TelegramClient
import csv
from telethon.tl.functions.messages import GetDialogsRequest
from telethon.tl.types import InputPeerEmpty
import asyncio
import telebot
from telebot import types

api_id = API_ID
api_hash = API
phone = 'phone number'
BOT_TOKEN = TOKEN

bot = telebot.TeleBot(BOT_TOKEN)

# Асинхронная функция для работы с Telethon
async def get_groups():
    client = TelegramClient(phone, api_id, api_hash, connection_retries=10)
    await client.start()

    print("Получение списка чатов...")
    chats = []
    last_date = None
    size_chats = 200
    groups = []

    result = await client(GetDialogsRequest(
        offset_date=last_date,
        offset_id=0,
        offset_peer=InputPeerEmpty(),
        limit=size_chats,
        hash=0
    ))
    chats.extend(result.chats)

    for chat in chats:
        try:
            if chat.megagroup:
                groups.append(chat)
        except AttributeError:
            continue

    await client.disconnect()  # Закрытие соединения
    return groups

# Асинхронная функция для получения участников и записи в файл
async def get_group_members_and_save_to_file(group):
    client = TelegramClient(phone, api_id, api_hash)
    await client.start()

    print(f'Получаем участников группы: {group.title}...')
    all_participants = await client.get_participants(group)

    # Сохранение данных в файл
    print('Сохраняем данные в файл...')
    with open("members.txt", "w", encoding="UTF-8") as file_members:
        writer = csv.writer(file_members, delimiter=",", lineterminator="\n")
        writer.writerow(['id', 'username', 'name', 'group', 'phone'])
        for user in all_participants:
            user_id = user.id or ""
            username = user.username or ""
            first_name = user.first_name or ""
            last_name = user.last_name or ""
            phone_number = user.phone or ""
            name = (first_name + ' ' + last_name).strip()
            writer.writerow([user_id, username, name, group.title, phone_number])

    await client.disconnect()  # Закрытие соединения
    print('Парсинг участников группы успешно выполнен.')


@bot.message_handler(commands=['start'])
def start(message):
    markup = telebot.types.InlineKeyboardMarkup()
    parser = telebot.types.InlineKeyboardButton("🔍 Парсинг", callback_data="parser")
    help_btn = telebot.types.InlineKeyboardButton("🆘 Помощь", callback_data="help")

    markup.add(parser, help_btn)
    bot.send_message(message.chat.id, "Главное меню", reply_markup=markup)


@bot.callback_query_handler(func=lambda call: True)
def handle_group_selection(call):
    if call.data == "parser":
        main(call.message)  # Proceed to the group selection process
    elif call.data == "help":
        help_function(call.message)  # Show help


def main(message):
    # Запуск асинхронной задачи в отдельном потоке
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    # Получаем список групп
    groups = loop.run_until_complete(get_groups())

    # Send group options
    bot.send_message(message.chat.id, f"Выберите номер группы из показанного:")
    for i, g in enumerate(groups):
        bot.send_message(message.chat.id, f"{i} - {g.title}")

    # Create a handler for the user's reply to select a group
    @bot.message_handler(func=lambda m: m.text.isdigit())
    def select_group(message):
        try:
            g_index = int(message.text)
            target_group = groups[g_index]

            # Асинхронно получаем участников и сохраняем в файл
            loop.run_until_complete(get_group_members_and_save_to_file(target_group))
            bot.send_message(message.chat.id, f"Данные участников группы '{target_group.title}' успешно сохранены в файл.")

            # Send the saved file to the user
            with open("members.txt", "rb") as file:
                bot.send_document(message.chat.id, document=file)

        except (ValueError, IndexError):
            bot.send_message(message.chat.id, "Неверный выбор группы, попробуйте снова.")

# Function to provide help
def help_function(message):
    bot.send_message(message.chat.id, "❗️ Важно: Для начала работы нажмите на кнопку 'Парсинг', чтобы выбрать группу и начать парсинг участников.")

if __name__ == "__main__":
    bot.polling(none_stop=True)
