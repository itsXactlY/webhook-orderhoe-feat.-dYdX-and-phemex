
import config
import concurrent.futures
from concurrent.futures.process import _MAX_WINDOWS_WORKERS


from dydx3 import Client
from dydx3.constants import API_HOST_ROPSTEN
from dydx3.constants import NETWORK_ID_ROPSTEN
from dydx3.constants import ORDER_TYPE_LIMIT, ORDER_TYPE_MARKET, ORDER_TYPE_STOP, ORDER_TYPE_TAKE_PROFIT, ORDER_TYPE_STOP_MARKET
from dydx3.constants import TIME_IN_FORCE_FOK, TIME_IN_FORCE_GTT, TIME_IN_FORCE_IOC

from flask import Flask, request

from web3 import Web3

from telegram import Bot as bot

import time
import json, requests


# Ganache test address.
ETHEREUM_ADDRESS = '0x3dB9FcCC80Eb5dFCCfE6599Df7E7801301aC277f'

# Ganache node.
WEB_PROVIDER_URL = 'http://localhost:8545'

client = Client(
    network_id=NETWORK_ID_ROPSTEN,
    host=API_HOST_ROPSTEN,
    default_ethereum_address=ETHEREUM_ADDRESS,
    web3=Web3(Web3.HTTPProvider(WEB_PROVIDER_URL)),
)

# Set STARK key.
stark_private_key = client.onboarding.derive_stark_key()
client.stark_private_key = '0x2c6a135115741592b3b600b8048d4cb9dabde144c17b5b158b745e1ce666a8a' # stark_private_key

# Get our position ID.
account_response = client.private.get_account()
position_id = account_response.data['account']['positionId']


# Flask Webhook
app = Flask(__name__)

# Flip Order side for Stoploss orders, quick 'n dirty lol

def flip_position_side():
    webhook_message = json.loads(request.data)
    side = webhook_message['strategy']['order_action']
    
    if side == "BUY": stop = "SELL"
    else: stop = "BUY"
    return stop

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
        
    # Market position datas

    side = webhook_message['strategy']['order_action']
    quantity = webhook_message['strategy']['order_contracts']
    price = webhook_message['strategy']['order_price']
    takeprofit = webhook_message['strategy']['order_takeprofit']
    stoploss = webhook_message['strategy']['order_stoploss']
    symbol_d = webhook_message['ticker_d']

    # aLca :: dYdX Orders here
        
    order_params_entry = {
        'position_id': position_id,
        'market': symbol_d,
        'side': side,
        'order_type': ORDER_TYPE_LIMIT,
        'post_only': True,
        'size': quantity,
        'price': str(price),
        'limit_fee': '0.0015',
        'expiration_epoch_seconds': time.time() + 43800 * 60, # 1month
        'time_in_force': TIME_IN_FORCE_GTT,
        }

    order_params_stop = { 
        'position_id': position_id,
        'market': symbol_d,
        'side': flip_position_side(),
        'order_type': ORDER_TYPE_STOP,
        'post_only': False,
        'size': quantity,
        'price': str(stoploss),
        'limit_fee': '0.0015',
        'expiration_epoch_seconds': time.time() + 43800 * 60, # 1month
        'time_in_force': TIME_IN_FORCE_GTT,
        'trigger_price': str(stoploss),
        'reduce_only': False,
        }
    
    order_params_takeprofit = {
        'position_id': position_id,
        'market': symbol_d,
        'side': flip_position_side(),
        'order_type': ORDER_TYPE_TAKE_PROFIT,
        'post_only': True,
        'size': quantity,
        'price': str(takeprofit),
        'trigger_price': str(takeprofit),
        'limit_fee': '0.0015',
        'expiration_epoch_seconds': time.time() + 43800 * 60, # 1month
        'time_in_force': TIME_IN_FORCE_GTT,
        'reduce_only': False,
        }
    
    # Order Threads
    order_entry_respone_thread = client.private.create_order(**order_params_entry)
    order_stop_respone_thread = client.private.create_order(**order_params_stop)
    order_tp_respone_thread = client.private.create_order(**order_params_takeprofit)

  
    # if a DISCORD URL is set in the config file, we will post to the discord webhook
    if config.DISCORD_ENABLED:
        chat_message = {
            "username": "1337 bot has something to say",
            "avatar_url": "https://i.imgur.com/oF6ANhV.jpg",
            "content": f"\n 🔮 Quant alert triggered!\n {side} {symbol_d} \n Entry {price} \n Takeprofit {takeprofit} \n Stoploss {stoploss}"
        }
    
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

    # Threading Messages to the world
    with concurrent.futures.ThreadPoolExecutor(_MAX_WINDOWS_WORKERS-1) as executor:
        executor.map(order_entry_respone_thread, range(3))
        executor.map(order_stop_respone_thread, range(3))
        executor.map(order_tp_respone_thread, range(3))
        executor.map(thread_x, range(3))
        executor.map(thread_y, range(3))

    return "done"

