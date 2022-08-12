# webhook-orderhoe-feat.-phemex
TradingView Strategy Alert Webhook for phemex or any ccxt supported exchange plus Discord alerts.

if u like this work, join me and grab an exclusive BTC bonus on top. https://phemex.com/register-vt1?referralCode=D5ATL


# Quick 'n dirty how to


git clone https://github.com/itsaLca/webhook-orderhoe-feat.-phemex

cd webhook-orderhoe-feat.-phemex

python3 -m venv .

source venv/bin/activate

pip3 install -r requirements.txt

Edit api key in config.py

export FLASK_APP=app.py

flask run

throw webhooks from tradingview, tuned, quants, weather forecasts etc. to localhost/webhook 

# example test

curl -X POST -H "Content-Type: application/json" -d @phemex_example_webhook.json http://localhost:5000/webhook

# Final step

Host a vps in Singapore for phemex. Best option same co-location: AWS ap-southeast-1 region (Singapore, Asia Pacific)
