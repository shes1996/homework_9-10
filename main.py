from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters, CallbackQueryHandler
import math
from datetime import datetime as dt

'''Доступные операции''' # обход опасностей, связанных с функцией eval()
ALLOWED_NAMES = {
    k: v for k, v in math.__dict__.items() if not k.startswith("__")
}

def log_operation(data):
    timer = dt.now().strftime('%H:%M:%S')
    with open('log.csv', 'a') as file:
        file.write(f'[{timer}]: {data}\n')


def evaluate(expression):
    """Вычисляет математическое выражение."""
    # Компиляция выражения в байт-код
    code = compile(expression, "<string>", "eval")

    # Валидация доступных имен
    for name in code.co_names:
        if name not in ALLOWED_NAMES:
            raise NameError(f"The use of '{name}' is not allowed")

    return eval(code, {"__builtins__": {}}, ALLOWED_NAMES)


async def calc(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Читает и рассчитывает введенное выражение"""

    # Читаем пользовательский ввод
    try:
        expression = update.message.text
    except (KeyboardInterrupt, EOFError):
        raise SystemExit()
    # Вычисление выражения и обработка ошибок
    try:
        result = evaluate(expression)
        await update.message.reply_text(f"Результат:   {result}")
        log_str = f'{expression} = {result}'
        log_operation(log_str)
    except SyntaxError:
        # Некорректное выражение
        await update.message.reply_text(f"Вы ввели некорректное выражение. Доступные выражения: {ALLOWED_NAMES}"
                                        f"Возведение в квадрат - **; "
                                        f"Комплексные числа - j")
    except (NameError, ValueError) as err:
        # Если пользователь попытался использовать неразрешенное имя
        # или неверное значение в переданной функции
        await update.message.reply_text(f"Вы ввели некорректное выражение. {err}"
                                        f"Возведение в квадрат - **; "
                                        f"Комплексные числа - j")


app = ApplicationBuilder().token("5717990866:AAEfna2WypYLhw4U2j4WIq1M6pM1ggb_TS0").build()

app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, calc))

app.run_polling()
