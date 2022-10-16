from flask import Flask
from threading import Thread

app = Flask('')

@app.route('/')

def home():
    return "if you somehow found this, that is very surprising. but the only news that you will get is that the AFTERMATHIC2 discord bot is working"

def run():
  app.run(host='0.0.0.0',port=8080)

def keep_alive():  
    t = Thread(target=run)
    t.start()