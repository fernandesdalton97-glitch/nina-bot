import os
import sqlite3
from datetime import datetime, timedelta
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from keep_alive import keep_alive

TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
DB_NAME = '/home/runner/workspace/bot/vip.db'


# BANCO DE DADOS
def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS vip_users
                 (user_id INTEGER PRIMARY KEY, username TEXT, end_date TEXT)''')
    conn.commit()
    conn.close()


# COMANDO /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("📋 MENU VIP", callback_data='menu')],
        [InlineKeyboardButton("💰 COMO COMPRAR", callback_data='comprar')],
        [InlineKeyboardButton("✅ JÁ PAGUEI", callback_data='paguei')]
    ]
    await update.message.reply_text(
        "Oi amor 💋 Bem vinda ao meu VIP",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


# BOTÕES
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == 'menu':
        await query.edit_message_text("Aqui está o MENU VIP 🔥")
    elif query.data == 'comprar':
        await query.edit_message_text(
            "Pix: 123.456.789-00\nDepois clica em JÁ PAGUEI",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("✅ JÁ PAGUEI", callback_data='paguei')]
            ])
        )
    elif query.data == 'paguei':
        await query.edit_message_text("Me manda o comprovante que eu libero manual 😊")


# COMANDO /add ID_USUARIO DIAS — só a admin usa
async def add_vip(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user_id = int(context.args[0])
        dias = int(context.args[1])
        end_date = datetime.now() + timedelta(days=dias)

        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute("INSERT OR REPLACE INTO vip_users VALUES (?,?,?)",
                  (user_id, "", end_date.strftime('%Y-%m-%d')))
        conn.commit()
        conn.close()

        # Agenda lembrete 1 dia antes
        context.job_queue.run_once(
            reminder,
            when=end_date - timedelta(days=1),
            data=user_id,
            name=f"reminder_{user_id}"
        )

        # Agenda remoção no dia
        context.job_queue.run_once(
            remove_vip,
            when=end_date,
            data=user_id,
            name=f"remove_{user_id}"
        )

        await update.message.reply_text(
            f"✅ VIP adicionado! Expira em {end_date.strftime('%d/%m/%Y')}"
        )
    except Exception as e:
        await update.message.reply_text("Use: /add ID_DO_USUARIO DIAS")


# LEMBRETE 1 DIA ANTES
async def reminder(context: ContextTypes.DEFAULT_TYPE):
    job = context.job
    await context.bot.send_message(
        job.data,
        "Oi amor 💋 Seu VIP acaba amanhã! Quer renovar pra não perder o acesso?\n"
        "Me manda uma mensagem aqui 👇"
    )


# REMOVER VIP NO DIA
async def remove_vip(context: ContextTypes.DEFAULT_TYPE):
    job = context.job
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("DELETE FROM vip_users WHERE user_id = ?", (job.data,))
    conn.commit()
    conn.close()

    await context.bot.send_message(
        job.data,
        "Seu acesso VIP expirou 😢\nMas pode voltar quando quiser! Me chama aqui 👇"
    )


def main():
    init_db()
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("add", add_vip))
    app.add_handler(CallbackQueryHandler(button))

    keep_alive()
    print("Bot da Nina está online!")
    app.run_polling()


if __name__ == '__main__':
    main()
