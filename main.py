import os
from telegram import Update
from telegram.ext import Application, CommandHandler

# PEGA O TOKEN QUE VOCÊ COLOU NO RENDER
TOKEN = os.environ['TELEGRAM_BOT_TOKEN']

async def start(update: Update, context):
    await update.message.reply_text(
        "👑 Bem-vindo!\n\n"
        "Escolha seu VIP:\n"
        "1. VIP 15 dias - R$20\n"
        "2. VIP 30 dias - R$35"
    )

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    print("Bot is running...") # Pra aparecer no log
    app.run_polling()

if __name__ == '__main__':
    main()
