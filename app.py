from flask import Flask, render_template, request
import json, requests
import config
from config import API_KEY, API_SECRET, WEBHOOK_PASSPHRASE
from telegram import Bot
import ccxt as tradeapi

print('CCXT Version:', tradeapi.__version__)

exchange = tradeapi.phemex({
    'enableRateLimit': True,
    'apiKey': API_KEY,  # testnet keys if using the testnet sandbox
    'secret': API_SECRET,
})

exchange.verbose = False
exchange.set_sandbox_mode(True)  # set to false for real net

app = Flask(__name__)


# todo :: fix me
@app.route('/dashboard')
def dashboard():
    orders = exchange.fetch_positions(None, {'code':'BTC'})
    
    return render_template('dashboard.html', phemex_orders=orders)

@app.route('/webhook', methods=['POST'])
def webhook():
    print(f"==> data getting from request ...")
    
    webhook_message = json.loads(request.data)
    
    if webhook_message['passphrase'] != WEBHOOK_PASSPHRASE:
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

        requests.post(config.DISCORD_WEBHOOK_URL, json=chat_message)
    
    # telegram for cornix coming here soon ™️
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
        
        tg_bot.sendMessage(config.TELEGRAM_CHANNEL, chat_message)



    return webhook_message
