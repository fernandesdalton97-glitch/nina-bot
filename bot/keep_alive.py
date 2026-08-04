from threading import Thread
from flask import Flask

app = Flask('')

@app.route('/')
def home():
    return "Bot está online!"

def run_flask():
    app.run(host='0.0.0.0', port=8080)
