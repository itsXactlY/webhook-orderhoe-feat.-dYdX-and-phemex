from config import API_KEY, API_SECRET
from flask import Flask, render_template, request
import config, json, requests

import ccxt as tradeapi
from pprint import pprint

print('CCXT Version:', tradeapi.__version__)

exchange = tradeapi.phemex({
    'enableRateLimit': True,
    'apiKey': '1b34e80b-568d-4e78-932e-99c4ff79b32e',  # testnet keys if using the testnet sandbox
    'secret': '_u0WHC_xseMjpKmLmIDeGSLYvkVa4b7pZLA8myGUsN0xNjk2ZTdmNi0yZThhLTQ4ZTItYjg3My00MDc4OGNhNWZlYWM',
})

# markets = exchange.load_markets()

# symbol = 'BTC/USD:USD'
# market = exchange.market(symbol)
# exchange.verbose = True
exchange.set_sandbox_mode(True)  # uncomment to use the testnet sandbox

# params = {
#     'currency': market['quoteId'],
# }
# response = exchange.privateGetAccountsAccountPositions(params)
# pprint(response)

app = Flask(__name__)


# todo :: fix me
# @app.route('/')
# def dashboard():
#     orders = tradeapi.list_orders()
    
#     return render_template('dashboard.html', alpaca_orders=orders)

@app.route('/webhook', methods=['POST'])
def webhook():
    print(f"==> data getting from request ...")
    
    webhook_message = json.loads(request.data)
    
    if webhook_message['passphrase'] != config.WEBHOOK_PASSPHRASE:
        return {
            'code': 'error',
            'message': 'nice try buddy'
        }
    
    price = webhook_message['strategy']['order_price']
    quantity = webhook_message['strategy']['order_contracts']
    symbol = webhook_message['ticker']
    side = webhook_message['strategy']['order_action']
    
    # aLca :: not sure if i need to give leverage, of just set and forget on phemex
    # leverage = webhook_message['strategy']['leverage'] 
    
    # order = api.submit_order(symbol, quantity, side, 'limit', 'gtc', limit_price=price)
    
    # tradeapi.set_leverage(10, 'BTC/USD:USD')
    # leverageResponse = exchange.set_leverage(1, symbol)
    # print(leverageResponse)

    # markets = tradeapi.load_markets()
    # print(markets)

    opening_order = ""
    closing_order = ""
    # try:
    #     # Change leverage to the desired value
    #     leverageResponse = exchange.set_leverage(leverage=leverage, symbol=symbol)
    #     print(f"Leverage changing ={leverageResponse}")
    # except Exception as e:
    #     print(f"Leverage changing error ={e}")


    # #############################################################################

    # 01. flat to long
    # if prev_market_position == "flat" and market_position == "long":
        # Open Long position
    try:
        if side == "buy":
            # Opening a pending contract (limit) order
            opening_order = exchange.create_order(symbol, 'market', 'buy', quantity)
            print(opening_order)
    except Exception as e:
        print(f" Long Opening error = {e}")
    # 02. flat to short
    # elif prev_market_position == "flat" and market_position == "short":
        # Open Short position
    try:
        if side == "sell":
            # Opening a pending contract (limit) order
            opening_order = exchange.create_order(symbol, 'market', 'sell', quantity)
            print(opening_order)
    except Exception as e:
        print(f" flat to short Short Opening error = {e}")
    # 03. long to short
    # elif prev_market_position == "long" and market_position == "short":
        # Open Short position
    try:
        quantity = quantity * 2
        if side == "sell":
            # Opening a pending contract (limit) order
            opening_order = exchange.create_order(symbol, 'market', 'sell', quantity)
            print(opening_order)
    except Exception as e:
        print(f" long to short Short Opening error = {e}")

    # 04. short to long
    # elif prev_market_position == "short" and market_position == "long":
        # Open Short position
    try:
        quantity = quantity * 2
        if side == "buy":
            # Opening a pending contract (limit) order
            opening_order = exchange.create_order(symbol, 'market', 'buy', quantity)
            print(opening_order)
    except Exception as e:
        print(f" short to long, Long Opening error = {e}")
        
    # Reset leverage to 1
    # try:
    #     leverageResponse = exchange.set_leverage('cross', symbol)
    #     print(leverageResponse)
    # except Exception as e:
    #     print(f"Leverage reset error = {e}")
  

    # if a DISCORD URL is set in the config file, we will post to the discord webhook
    if config.DISCORD_WEBHOOK_URL:
        chat_message = {
            "username": "1337 bot has something to say",
            "avatar_url": "https://i.imgur.com/oF6ANhV.jpg",
            "content": f"tradingview strategy alert triggered: {quantity} {symbol} @ {price}"
        }

        requests.post(config.DISCORD_WEBHOOK_URL, json=chat_message)
        
        
    # $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$

    return webhook_message, {
        "open order ": opening_order ,
        "close order ": closing_order,
        
    }

    # return webhook_message