import telebot
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from config import TELEGRAM_TOKEN, GOOGLE_SHEET_NAME, CREDENTIALS_FILE

# Настройка доступа к Google Sheets
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name(CREDENTIALS_FILE, scope)
client = gspread.authorize(creds)
sheet = client.open(GOOGLE_SHEET_NAME).sheet1

# Инициализация бота
bot = telebot.TeleBot(TELEGRAM_TOKEN)

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "👋 Привет! Отправь ставку в формате:\n\nДата, матч, тип ставки, коэф, сумма")

@bot.message_handler(commands=['результат'])
def set_result(message):
    try:
        # Ожидаем: /результат 5 win
        parts = message.text.split()
        if len(parts) != 3:
            raise ValueError("Неверный формат. Пример: /результат 5 win")

        row_number = int(parts[1]) + 1  # +1 т.к. в Google Sheets первая строка — заголовок
        result = parts[2].lower()

        if result not in ['win', 'loss']:
            raise ValueError("Результат должен быть 'win' или 'loss'")

        # Записываем результат в 6-ю колонку (столбец 'Результат')
        sheet.update_cell(row_number, 6, result)
        bot.send_message(message.chat.id, f"✅ Результат для строки {parts[1]} установлен: {result}")
    except Exception as e:
        bot.send_message(message.chat.id, f"⚠️ Ошибка: {str(e)}")
        
@bot.message_handler(func=lambda message: True)
def save_bet(message):
    try:
        data = [i.strip() for i in message.text.split(',')]
        if len(data) != 5:
            raise ValueError
        row = data + ['']  # Добавляем пустую ячейку для результата
        sheet.append_row(row)
        bot.send_message(message.chat.id, "✅ Ставка добавлена в таблицу!")
    except Exception as e:
        bot.send_message(message.chat.id, f"⚠️ Ошибка. Формат:\n\nДата, матч, ставка, коэф, сумма\n\n{str(e)}")

bot.polling()
