import os
from binance.spot import Spot

API_KEY = os.getenv('API_KEY')
API_SECRET = os.getenv('API_SECRET')

client = Spot(api_key=API_KEY, api_secret=API_SECRET)


def get_avg_price(currency):
    return float(client.avg_price(symbol=f'{currency}USDT')['price'])