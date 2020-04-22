# -*- coding: utf-8 -*-
# PROJECT: @HBCryptoBot
# DESCRIPTION: my new telegram bot for request of crypto rates from api.exmo.com
# AUTHOR: Egor Devyatov

import requests
import json


API_URL = "https://api.exmo.com/v1.1/ticker"

response = requests.request("GET", API_URL)

decoded_json = json.loads(response.text)
btc_data_usd = decoded_json["BTC_USD"]
btc_data_rub = decoded_json["BTC_RUB"]

eth_data_usd = decoded_json["ETH_USD"]
eth_data_rub = decoded_json["ETH_RUB"]

zec_data_usd = decoded_json["ZEC_USD"]
zec_data_rub = decoded_json["ZEC_RUB"]


priceBTC_USD = btc_data_usd["sell_price"]
priceBTC_RUB = btc_data_rub["sell_price"]

priceETH_USD = eth_data_usd["sell_price"]
priceETH_RUB = eth_data_rub["sell_price"]

priceZEC_USD = zec_data_usd["sell_price"]
priceZEC_RUB = zec_data_rub["sell_price"]

print(priceBTC_USD)
print(priceBTC_RUB)
print(priceETH_USD)
print(priceETH_RUB)
print(priceZEC_USD)
print(priceZEC_RUB)