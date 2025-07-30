from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

TOKEN = "7407212502:AAHlRgnu6wqnSP-CPsF7mLugHQwx0YHYCJw"

# Store expenses in memory
expenses = []

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Welcome! Send me your expense in the format: 250 groceries")

async def add_expense(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        amount, category = update.message.text.split(maxsplit=1)
        amount = float(amount)
        expenses.append({'amount': amount, 'category': category})
        await update.message.reply_text(f"Added {amount} to {category}.")
    except:
        await update.message.reply_text("Invalid format. Use: 250 groceries")

async def summary(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not expenses:
        await update.message.reply_text("No expenses recorded yet.")
        return

    total = sum(e['amount'] for e in expenses)
    reply = f"Total Expenses: {total}\n"
    for e in expenses:
        reply += f"- {e['category']}: {e['amount']}\n"
    await update.message.reply_text(reply)

if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("summary", summary))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, add_expense))

    print("Bot running... Ctrl+C to stop.")
    app.run_polling()
