import ccxt as tradeapi

import concurrent.futures

import config
from config import API_KEY, API_SECRET

from concurrent.futures.process import _MAX_WINDOWS_WORKERS

from flask import request
from telegram import Bot as bot

import json

import requests


exchange = tradeapi.phemex({
    'enableRateLimit': True,
    'apiKey': API_KEY,
    'secret': API_SECRET,
})
exchange.set_sandbox_mode(True)  # set to false for real net
exchange.verbose = False
if exchange.verbose == True:
    print('CCXT Version:', tradeapi.__version__)


def phemex_order(webhook_message):
    print(f"==> Phemex data getting from request ...")
    
    webhook_message = json.loads(request.data)
    print(webhook_message)
    
    if webhook_message['passphrase'] != config.WEBHOOK_PASSPHRASE:
        return {
            'code': 'error',
            'message': 'nice try buddy'
        }

    opening_order = ""
        
    # Market position datas

    price = webhook_message['strategy']['order_price']
    quantity = webhook_message['strategy']['order_contracts']
    symbol_phemex = webhook_message['ticker']
    side = webhook_message['strategy']['order_action']
    takeprofit = webhook_message['strategy']['order_takeprofit']
    stoploss = webhook_message['strategy']['order_stoploss']
    # aLca :: not sure if i need to give leverage, of just set and forget on phemex
    # leverage = webhook_message['strategy']['leverage'] 
    
    # aLca :: ccxt Orders here
    
    try:
        if side == "buy" or "BUY":
            # Opening a pending contract (limit) order
            opening_order = exchange.create_order(symbol_phemex, 'limit', 'buy', quantity, price, {'stopLossPrice': stoploss, 'takeProfitPrice': takeprofit})
        
        if side == "sell" or "SELL":
            # Opening a pending contract (limit) order
            opening_order = exchange.create_order(symbol_phemex, 'limit', 'sell', quantity, price, {'stopLossPrice': stoploss, 'takeProfitPrice': takeprofit})
    except Exception as e:
        print(f" Long Opening error = {e}")

    # if a DISCORD URL is set in the config file, we will post to the discord webhook
    if config.DISCORD_ENABLED:
        chat_message = {
            "username": "1337 bot has something to say",
            "avatar_url": "https://i.imgur.com/oF6ANhV.jpg",
            "content": f"\n 🔮 Quant alert triggered!\n {side} {symbol_phemex} \n Entry {price} \n Takeprofit {takeprofit} \n Stoploss {stoploss}"
        }
        discord_x = requests.post(config.DISCORD_WEBHOOK_URL_ZERODAY, json=chat_message)
        discord_y = requests.post(config.DISCORD_WEBHOOK_URL_TOURISTINFORMATION, json=chat_message)

    # telegram for https://t.me/cornix_trading_bot?start=ref-753f57ac5bc94e73a8d0581ea166926a 
    if config.TELEGRAM_ENABLED:
        tg_bot = bot(token=config.TELEGRAM_TOKEN)
        
        chat_message = f'''
        🔮 Quant alert triggered!
        {side} {symbol_phemex}
        Leverage: isolated 10x
        Entry: {price}
        Takeprofit {takeprofit}
        Stoploss {stoploss}
        '''
        telegram_x = tg_bot.sendMessage(config.TELEGRAM_CHANNEL, chat_message)


    # Threading Messages to the world
    with concurrent.futures.ThreadPoolExecutor(_MAX_WINDOWS_WORKERS-1) as executor:
        executor.map(opening_order, range(3))
        executor.map(telegram_x, range (3))
        executor.map(discord_x, range(3))
        executor.map(discord_y, range(3))

    return "done"
