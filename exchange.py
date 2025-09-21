import os
import time
import hmac
import json
import requests
from hashlib import sha256
import bot_messages as messages
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

API_URL = "https://open-api.bingx.com"
API_KEY = os.getenv('API_KEY')
API_SECRET = os.getenv('API_SECRET')


def get_avg_price(ticker):
    path = "/openApi/swap/v1/ticker/price"
    payload = {}
    method = "GET"
    params = {
        "symbol": f"{ticker}-USDT"
    }
    paramStr = parseMapToStr(params)
    responce = send_request(method, path, paramStr, payload)
    if responce["msg"] != "":
        return messages.NO_SUCH_CURRENCY
    else:
        return float(responce["data"]["price"])


def get_signature(payload):
    signature = hmac.new(API_SECRET.encode("utf-8"), payload.encode("utf-8"), digestmod=sha256).hexdigest()
    return signature


def send_request(method, path, params, payload):
    signature = get_signature(path)
    url = f"{API_URL}{path}?{params}&signature={signature}"
    print(url)
    headers = {
        "X-BX-APIKEY" : API_KEY
    }
    responce = requests.request(method, url, headers=headers, data=payload)
    print(responce.text)
    return json.loads(responce.text)


def parseMapToStr(map):
    sortedKeys = sorted(map)
    paramStr = "&".join(["%s=%s" % (x, map[x]) for x in sortedKeys])
    if paramStr != "":
        return paramStr + "&timestamp=" + str(int(time.time() * 1000))
    else:
        return paramStr + "timestamp=" + str(int(time.time() * 1000))