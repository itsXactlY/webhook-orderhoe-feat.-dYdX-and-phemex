# webhook-orderhoe-feat.-phemex
TradingView Strategy Alert Webhook for phemex or any ccxt supported exchange plus Discord alerts.

if u like this work, join me and grab an exclusive BTC bonus on top. https://phemex.com/register-vt1?referralCode=D5ATL


# Quick 'n dirty how to for your doomers


git clone https://github.com/itsaLca/webhook-orderhoe-feat.-phemex

cd webhook-orderhoe-feat.-phemex

python3 -m venv .

source venv/bin/activate

pip3 install -r requirements.txt

Edit api key in config.py

flask run

throw webhooks from tradingview, tuned, quants, etc. at 127.0.0.1/webhook 

# example test

curl -X POST -H "Content-Type: application/json" -d @phemex_example_webhook.json http://localhost:5000/webhook
