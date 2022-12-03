import config
import discord_channel
import telegram_channel
import json
import time
import requests
import fake_useragent as ua


from concurrent.futures import ThreadPoolExecutor
from flask import Flask, request
from telegram import Bot as bot
from phemex import phemex_order

# TODO :: throw all exchanges aboard, parse them from signal message *which* exchange we target,
#      :: to use a 'generic' template for all exchanges (like almost all)


app = Flask(__name__)

# Alerts

def alerts(data):
    
    side = data['strategy']['order_action']
    price = data['strategy']['order_price']
    takeprofit = data['strategy']['order_takeprofit']
    stoploss = data['strategy']['order_stoploss']
    symbol_d = data['ticker']
    # aLca :: not sure if i need to give leverage, of just set and forget on exchange
    # leverage = data['strategy']['leverage'] 

    stub = f'''
    🔮 Quant Alert
    {side} {symbol_d}
    Leverage: isolated 10x
    Entry: {price}
    Takeprofit {takeprofit}
    Stoploss {stoploss}
    '''
    headers = {
    'Content-Type': 'application/json',
    'User-Agent': ua.random,
    }


    # TODO :: rework slow while loops later
    # if a DISCORD URL is set in the config file, we will post to the discord webhook
    if config.DISCORD_ENABLED == True:
        chat_message = {
            "username": "🔮🔮🔮🔮🔮🔮🔮🔮🔮🔮🔮🔮🔮🔮",
            "avatar_url": "https://i.imgur.com/oF6ANhV.jpg",
            "content" : stub
        }

        i = 0
        dc_channel = discord_channel.hooks
        while i < len(dc_channel):
            start_dc = time.time()
            with ThreadPoolExecutor(max_workers=1) as executor:
                executor.map(requests.post(dc_channel[i], json=chat_message, headers=headers))
                i = i + 1
                end_dc = time.time()

    # telegram for https://t.me/cornix_trading_bot?start=ref-753f57ac5bc94e73a8d0581ea166926a 
    if config.TELEGRAM_ENABLED == True:
        j = 0
        tg_bot = bot(token=config.TELEGRAM_TOKEN)
        tg_channel = telegram_channel.chan
        while j < len(tg_channel):
            start = time.time()
            with ThreadPoolExecutor(max_workers=1) as executor:
                executor.map(tg_bot.sendMessage(tg_channel[j], stub))
                j = j + 1
            end = time.time()

    return("\nTime taken sending Telegram Messages:{}\n".format(end - start) + "\nTime taken sending Discord Messages:{}".format(end_dc - start_dc))


# Webhoe
@app.route('/alert', methods=['POST'])
def get_route_alert():

    webhook_message = json.loads(request.data)
    if webhook_message['passphrase'] != config.WEBHOOK_PASSPHRASE:
        return {
            'code': ' 404 error',
            'message': 'nice try buddy'
        }

    return phemex_order(webhook_message), alerts(webhook_message)

# TODO :: make it multithread, as FLASK and also Telethon blocking both the mainthread, for further Telegram signal parsing.
# TODO :: add a blacklist for certain channels, or only listen to specific channels (more safe, right now we listen to "*")

if __name__ == "__main__":
    # with ThreadPoolExecutor(max_workers=2) as executor:
        app.run(host='0.0.0.0', debug=False)
