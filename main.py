import threading
from bot.bot import run_bot
from bot.keep_alive import run_flask

# Roda os 2 juntos
if __name__ == "__main__":
    threading.Thread(target=run_flask).start()
    run_bot()
