# calculator_bot.py
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

class CalculatorBot:
    def __init__(self, token):
        self.token = token
        self.application = Application.builder().token(token).build()
        self.setup_handlers()
    
    def setup_handlers(self):
        """Настройка обработчиков команд"""
        self.application.add_handler(CommandHandler("start", self.start))
        self.application.add_handler(CommandHandler("calc", self.calculator))
        self.application.add_handler(CallbackQueryHandler(self.button_handler))
    
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /start"""
        welcome_text = (
            "🔢 *Калькулятор Бот*\n\n"
            "Я могу выполнять математические операции:\n"
            "• Сложение (+)\n"
            "• Вычитание (-)\n"
            "• Умножение (*)\n"
            "• Деление (/)\n"
            "• Степень (^)\n"
            "• Квадратный корень (√)\n\n"
            "Используйте /calc чтобы открыть калькулятор"
        )
        
        await update.message.reply_text(welcome_text, parse_mode='Markdown')
    
    async def calculator(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Открывает калькулятор"""
        keyboard = [
            [
                InlineKeyboardButton("7", callback_data="7"),
                InlineKeyboardButton("8", callback_data="8"),
                InlineKeyboardButton("9", callback_data="9"),
                InlineKeyboardButton("÷", callback_data="/")
            ],
            [
                InlineKeyboardButton("4", callback_data="4"),
                InlineKeyboardButton("5", callback_data="5"),
                InlineKeyboardButton("6", callback_data="6"),
                InlineKeyboardButton("×", callback_data="*")
            ],
            [
                InlineKeyboardButton("1", callback_data="1"),
                InlineKeyboardButton("2", callback_data="2"),
                InlineKeyboardButton("3", callback_data="3"),
                InlineKeyboardButton("-", callback_data="-")
            ],
            [
                InlineKeyboardButton("0", callback_data="0"),
                InlineKeyboardButton(".", callback_data="."),
                InlineKeyboardButton("=", callback_data="="),
                InlineKeyboardButton("+", callback_data="+")
            ],
            [
                InlineKeyboardButton("C", callback_data="C"),
                InlineKeyboardButton("⌫", callback_data="backspace"),
                InlineKeyboardButton("√", callback_data="sqrt"),
                InlineKeyboardButton("x²", callback_data="^2")
            ],
            [
                InlineKeyboardButton("(", callback_data="("),
                InlineKeyboardButton(")", callback_data=")"),
                InlineKeyboardButton("x^y", callback_data="^"),
                InlineKeyboardButton("%", callback_data="/100*")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            "🧮 *Калькулятор*\n\n`0`\n\nВыберите операцию:",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    
    def calculate_expression(self, expression):
        """Вычисление математического выражения"""
        try:
            # Заменяем символы для Python
            expression = expression.replace('×', '*').replace('÷', '/')
            expression = expression.replace('^', '**')
            
            # Безопасное вычисление
            allowed_chars = set('0123456789+-*/.() ')
            if not all(c in allowed_chars for c in expression.replace('**', '')):
                return "Ошибка: Недопустимые символы"
            
            result = eval(expression)
            
            # Проверка на бесконечность
            if abs(result) == float('inf'):
                return "Ошибка: Деление на ноль"
            
            # Форматирование результата
            if isinstance(result, float) and result.is_integer():
                result = int(result)
            
            return str(result)
            
        except ZeroDivisionError:
            return "Ошибка: Деление на ноль"
        except SyntaxError:
            return "Ошибка: Неверное выражение"
        except Exception as e:
            return f"Ошибка: {str(e)}"
    
    async def button_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик нажатий на кнопки"""
        query = update.callback_query
        await query.answer()
        
        data = query.data
        current_text = query.message.text
        
        # Извлекаем текущее выражение из текста сообщения
        lines = current_text.split('\n')
        if len(lines) >= 2:
            current_expression = lines[-2].strip('`')
        else:
            current_expression = "0"
        
        # Обработка специальных кнопок
        if data == "C":
            new_expression = "0"
        elif data == "backspace":
            if len(current_expression) > 1:
                new_expression = current_expression[:-1]
            else:
                new_expression = "0"
        elif data == "=":
            if current_expression != "0":
                result = self.calculate_expression(current_expression)
                new_expression = result
            else:
                new_expression = "0"
        elif data == "sqrt":
            try:
                num = float(current_expression)
                if num >= 0:
                    result = num ** 0.5
                    if result.is_integer():
                        new_expression = str(int(result))
                    else:
                        new_expression = str(round(result, 6))
                else:
                    new_expression = "Ошибка: Отрицательное число"
            except:
                new_expression = "Ошибка"
        elif data == "^2":
            try:
                num = float(current_expression)
                result = num ** 2
                if result.is_integer():
                    new_expression = str(int(result))
                else:
                    new_expression = str(result)
            except:
                new_expression = "Ошибка"
        elif data == "/100*":
            # Процент
            new_expression = current_expression + "/100*"
        else:
            # Обычные цифры и операторы
            if current_expression == "0" or current_expression in ["Ошибка", "Ошибка: Деление на ноль"]:
                if data in ["+", "-", "*", "/", "^"]:
                    new_expression = "0" + data
                else:
                    new_expression = data
            else:
                new_expression = current_expression + data
        
        # Обновляем сообщение
        keyboard = query.message.reply_markup
        await query.edit_message_text(
            f"🧮 *Калькулятор*\n\n`{new_expression}`\n\nВыберите операцию:",
            reply_markup=keyboard,
            parse_mode='Markdown'
        )
    
    def run(self):
        """Запуск бота"""
        print("🧮 Calculator Bot started!")
        self.application.run_polling()

# Запуск бота
def main():
    # Замените на ваш токен бота
    BOT_TOKEN = "8524064485:AAFRnhu_t3OCVMfgQsNkPCKdPZrLlv72MXw"
    
    bot = CalculatorBot(BOT_TOKEN)
    bot.run()

if __name__ == "__main__":
    main()