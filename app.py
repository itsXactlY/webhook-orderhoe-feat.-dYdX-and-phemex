from config import API_KEY, API_SECRET
from flask import Flask, render_template, request
from telegram import Bot
import config
import json, requests
import ccxt as tradeapi
import concurrent.futures

# CCXT
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

# Dashboard
# todo :: fix me
@app.route('/dashboard')
def dashboard():
    orders = exchange.fetch_positions(None, {'code':'BTC'})
    
    return render_template('dashboard.html', phemex_orders=orders)

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
    prev_market_position = webhook_message['strategy']['prev_market_situation']
    market_position = webhook_message['strategy']['market_position']
    

    price = webhook_message['strategy']['order_price']
    quantity = webhook_message['strategy']['order_contracts']
    symbol = webhook_message['ticker']
    side = webhook_message['strategy']['order_action']
    takeprofit = webhook_message['strategy']['order_takeprofit']
    stoploss = webhook_message['strategy']['order_stoploss']
    # aLca :: not sure if i need to give leverage, of just set and forget on phemex
    # leverage = webhook_message['strategy']['leverage'] 
    
    # #############################################################################

    # 01. flat to long
    if prev_market_position == "flat" and market_position == "long":
        # Open Long position
        try:
            if side == "buy":
                # Opening a pending contract (limit) order
                opening_order = exchange.create_order(symbol, 'limit', 'buy', quantity, price, {'stopLossPrice': stoploss, 'takeProfitPrice': takeprofit})
                print(opening_order)
        except Exception as e:
            print(f" Long Opening error = {e}")
    
    
    # 02. flat to short
    elif prev_market_position == "flat" and market_position == "short":
        # Open Short position
        try:
            if side == "sell":
                # Opening a pending contract (limit) order
                opening_order = exchange.create_order(symbol, 'limit', 'sell', quantity, price, {'stopLossPrice': stoploss, 'takeProfitPrice': takeprofit})
                print(opening_order)
        except Exception as e:
            print(f" flat to short Short Opening error = {e}")
    
    
    # 03. long to short
    elif prev_market_position == "long" and market_position == "short":
        # Open Short position
        try:
            quantity = quantity * 2
            if side == "sell":
                # Opening a pending contract (limit) order
                opening_order = exchange.create_order(symbol, 'limit', 'sell', quantity, price, {'stopLossPrice': stoploss, 'takeProfitPrice': takeprofit})
                print(opening_order)
        except Exception as e:
            print(f" long to short Short Opening error = {e}")


    # 04. short to long
    elif prev_market_position == "short" and market_position == "long":
        # Open Short position
        try:
            quantity = quantity * 2
            if side == "buy":
                # Opening a pending contract (limit) order
                opening_order = exchange.create_order(symbol, 'limit', 'buy', quantity, price, {'stopLossPrice': stoploss, 'takeProfitPrice': takeprofit})
                print(opening_order)
        except Exception as e:
            print(f" short to long, Long Opening error = {e}")
        
    # Reset leverage to 1
    # try:
    #     leverageResponse = exchange.set_leverage(1, symbol)
    #     print(leverageResponse)
    # except Exception as e:
    #     print(f"Leverage reset error = {e}")
  

    # if a DISCORD URL is set in the config file, we will post to the discord webhook
    if config.DISCORD_ENABLED:
        chat_message = {
            "username": "1337 bot has something to say",
            "avatar_url": "https://i.imgur.com/oF6ANhV.jpg",
            "content": f"\n 🔮 Quant alert triggered!\n {symbol} \n Entry {price} \n Takeprofit {takeprofit} \n Stoploss {stoploss}"
        }

        thread_x = requests.post(config.DISCORD_WEBHOOK_URL, json=chat_message)
        # thread discord webhook
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
            executor.map(thread_x, range(3))
    
    # telegram for https://t.me/cornix_trading_bot?start=ref-753f57ac5bc94e73a8d0581ea166926a 
    if config.TELEGRAM_ENABLED:
        tg_bot = Bot(token=config.TELEGRAM_TOKEN)
        
        chat_message = f'''
        🔮 Quant alert triggered!
        {symbol}
        Leverage: isolated 10x
        Entry: {price}
        Takeprofit {takeprofit}
        Stoploss {stoploss}
        '''
        
        thread_y = tg_bot.sendMessage(config.TELEGRAM_CHANNEL, chat_message)       
        # thread telegram message
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
            executor.map(thread_y, range(3))


    return webhook_message
