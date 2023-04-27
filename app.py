import config
from concurrent.futures.process import _MAX_WINDOWS_WORKERS
import concurrent.futures
import json
from dYdX import dydx_order
from phemex import phemex_order

from flask import Flask, request

import requests

from telegram import Bot as bot

app = Flask(__name__)

# Alerts

def alerts(data):
    
    side = data['strategy']['order_action']
    price = data['strategy']['order_price']
    takeprofit = data['strategy']['order_takeprofit']
    stoploss = data['strategy']['order_stoploss']
    symbol_d = data['ticker']
  
    # if a DISCORD URL is set in the config file, we will post to the discord webhook
    if config.DISCORD_ENABLED:
        chat_message = {
            "username": "1337 bot has something to say",
            "avatar_url": "https://i.imgur.com/oF6ANhV.jpg",
            "content": f"\n 🔮 Quant alert triggered!\n {side} {symbol_d} \n Entry {price} \n Takeprofit {takeprofit} \n Stoploss {stoploss}"
        }
        discord_x = requests.post(config.DISCORD_WEBHOOK_URL_ZERODAY, json=chat_message)
        discord_y = requests.post(config.DISCORD_WEBHOOK_URL_TOURISTINFORMATION, json=chat_message)

    # telegram for https://t.me/cornix_trading_bot?start=ref-753f57ac5bc94e73a8d0581ea166926a 
    if config.TELEGRAM_ENABLED:
        tg_bot = bot(token=config.TELEGRAM_TOKEN)
        
        chat_message = f'''
        🔮 Quant alert triggered!
        {side} {symbol_d}
        Leverage: isolated 10x
        Entry: {price}
        Takeprofit {takeprofit}
        Stoploss {stoploss}
        '''
        telegram_x = tg_bot.sendMessage(config.TELEGRAM_CHANNEL, chat_message)

    # Threading Messages to the world
    with concurrent.futures.ThreadPoolExecutor(_MAX_WINDOWS_WORKERS-1) as executor:
        executor.map(telegram_x, range (1))
        executor.map(discord_x, range(1))
        executor.map(discord_y, range(1))

# Webhook
@app.route('/webhoe_dydx', methods=['POST'])
def get_route_dydx():
    webhook_message = json.loads(request.data)
    
    if webhook_message['passphrase'] != config.WEBHOOK_PASSPHRASE:
        return {
            'code': 'error',
            'message': 'nice try buddy'
        }
        
    alerts(webhook_message)
    
    return dydx_order(webhook_message)


@app.route('/webhoe_phemex', methods=['POST'])
def get_route_phemex():
    webhook_message = json.loads(request.data)

    if webhook_message['passphrase'] != config.WEBHOOK_PASSPHRASE:
        return {
            'code': 'error',
            'message': 'nice try buddy'
        }
        
    alerts(webhook_message)
        
    return phemex_order(webhook_message)
