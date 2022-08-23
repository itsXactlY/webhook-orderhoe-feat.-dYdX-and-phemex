import config
import json
from dYdX import dydx_order
from phemex import phemex_order

from flask import Flask, request

app = Flask(__name__)


# Webhook
@app.route('/webhoe_dydx', methods=['POST'])
def get_route_dydx():
    webhook_message = json.loads(request.data)
    
    if webhook_message['passphrase'] != config.WEBHOOK_PASSPHRASE:
        return {
            'code': 'error',
            'message': 'nice try buddy'
        }
    
    return dydx_order(webhook_message)


@app.route('/webhoe_phemex', methods=['POST'])
def get_route_phemex():
    webhook_message = json.loads(request.data)

    if webhook_message['passphrase'] != config.WEBHOOK_PASSPHRASE:
        return {
            'code': 'error',
            'message': 'nice try buddy'
        }
        
    return phemex_order(webhook_message)