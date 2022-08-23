import ccxt as tradeapi

import concurrent.futures
from concurrent.futures.process import _MAX_WINDOWS_WORKERS

import config
from config import API_KEY, API_SECRET

from flask import request

import json


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


    # Threading Messages to the world
    with concurrent.futures.ThreadPoolExecutor(_MAX_WINDOWS_WORKERS-1) as executor:
        executor.map(opening_order, range(3))


    return "done"
