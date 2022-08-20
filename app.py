# CCXT

from config import API_KEY, API_SECRET
from flask import Flask, request
from telegram import Bot
import config
import json, requests
import ccxt as tradeapi
import concurrent.futures


exchange = tradeapi.phemex({
    'enableRateLimit': True,
    'apiKey': API_KEY,
    'secret': API_SECRET,
})
exchange.set_sandbox_mode(True)  # set to false for real net
exchange.verbose = False
if exchange.verbose == True:
    print('CCXT Version:', tradeapi.__version__)

# Flask Webhook
app = Flask(__name__)

# Webhook
@app.route('/webhook', methods=['POST'])
def webhook():
    print(f"==> data getting from request ...")
    
    webhook_message = json.loads(request.data)
    
    if webhook_message['passphrase'] != config.WEBHOOK_PASSPHRASE:
        return {
            'code': 'error',
            'message': 'nice try buddy'
        }

    opening_order = ""
        
    # Market position datas
    # prev_market_position = webhook_message['strategy']['prev_market_situation']
    market_position = webhook_message['strategy']['market_position']

    price = webhook_message['strategy']['order_price']
    quantity = webhook_message['strategy']['order_contracts']
    symbol_d = webhook_message['ticker_d']
    symbol_p = webhook_message['ticker_p']
    side = webhook_message['strategy']['order_action']
    takeprofit = webhook_message['strategy']['order_takeprofit']
    stoploss = webhook_message['strategy']['order_stoploss']
    # aLca :: not sure if i need to give leverage, of just set and forget on phemex
    # leverage = webhook_message['strategy']['leverage'] 
    
    # aLca :: ccxt Orders here

    if side == "buy" or "BUY":
        # Opening a pending contract (limit) order
        opening_order = exchange.create_order(symbol_p, 'limit', 'buy', quantity, price, {'stopLossPrice': stoploss, 'takeProfitPrice': takeprofit})
        print("Opening Phemex Order!", opening_order)
        
    if side == "sell" or "SELL":
        # Opening a pending contract (limit) order
        opening_order = exchange.create_order(symbol_p, 'limit', 'sell', quantity, price, {'stopLossPrice': stoploss, 'takeProfitPrice': takeprofit})
        print("Opening Phemex Order!", opening_order)


    # if a DISCORD URL is set in the config file, we will post to the discord webhook
    if config.DISCORD_ENABLED:
        chat_message = {
            "username": "1337 bot has something to say",
            "avatar_url": "https://i.imgur.com/oF6ANhV.jpg",
            "content": f"\n 🔮 Quant alert triggered!\n {side} {symbol_d} \n Entry {price} \n Takeprofit {takeprofit} \n Stoploss {stoploss}"
        }
        thread_x = requests.post(config.DISCORD_WEBHOOK_URL, json=chat_message)
    
    # telegram for https://t.me/cornix_trading_bot?start=ref-753f57ac5bc94e73a8d0581ea166926a 
    if config.TELEGRAM_ENABLED:
        tg_bot = Bot(token=config.TELEGRAM_TOKEN)
        
        chat_message = f'''
        🔮 Quant alert triggered!
        {side} {symbol_d}
        Leverage: isolated 10x
        Entry: {price}
        Takeprofit {takeprofit}
        Stoploss {stoploss}
        '''
        thread_y = tg_bot.sendMessage(config.TELEGRAM_CHANNEL, chat_message)
        
        
    # Send Messages to the world    
    # threading bot messages
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
        executor.map(thread_x and thread_y, range(3))


    return webhook_message
