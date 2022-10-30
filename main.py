from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters
import math

'''Доступные операции''' # обход опасностей, связанных с функцией eval()
ALLOWED_NAMES = {
    k: v for k, v in math.__dict__.items() if not k.startswith("__")
}


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
        await update.message.reply_text(f"Результат: {result}")
    except SyntaxError:
        # Некорректное выражение
        update.message.reply_text("Вы ввели некорректное выражение.")
    except (NameError, ValueError) as err:
        # Если пользователь попытался использовать неразрешенное имя
        # или неверное значение в переданной функции
        update.message.reply_text(err)


app = ApplicationBuilder().token("YOUR TOKEN").build()

app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, calc))

app.run_polling()

