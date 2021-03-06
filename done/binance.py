import hmac
import hashlib
import requests
import json
import sys
import websocket
import gzip
import time
from SaveMysql import updateMysql,insertMysql


class Binance():
    def __init__(self, key, secret, base_url = 'https://www.binance.com'):
        self.key = key
        self.secret = secret
        self.base_url = base_url


    def public_request(self, method, api_url, **payload):
        """request public url"""
        r_url = self.base_url + api_url
        try:
            r = requests.request(method, r_url, params=payload)
            r.raise_for_status()
        except requests.exceptions.HTTPError as err:
            print(err)
            sys.exit(1)
        if r.status_code == 200:
            return r.json()

    def signed_request(self, method, api_url, **payload):
        """request a signed url"""

        r_url = self.base_url + api_url
        payload['timestamp'] = self.get_server_time()
        payload['signature'] = self.get_signed(**payload)


        headers = {
            'X-MBX-APIKEY': self.key,
        }

        try:
            r = requests.request(method, r_url, headers = headers, params=payload)
            r.raise_for_status()
        except requests.exceptions.HTTPError as err:
            print(err)
            print(r.text)
            sys.exit(1)
        if r.status_code == 200:
            return r.json()

    def apikey_request(self,method, api_url, **payload):
        """request a apikey url"""
        r_url = self.base_url + api_url

        headers = {
            'X-MBX-APIKEY': self.key,
        }

        try:
            r = requests.request(method, r_url, headers = headers, params=payload)
            r.raise_for_status()
        except requests.exceptions.HTTPError as err:
            print(err)
            print(r.text)
            sys.exit(1)
        if r.status_code == 200:
            return r.json()


    def get_signed(self, **payload):
        """signed params use sha256"""
        param = ''
        for k in payload:
            param += '&' + k + '=' + str(payload[k])
        param = param.lstrip('&')
        signature = hmac.new(self.secret, param, digestmod=hashlib.sha256).hexdigest()

        return signature


    def get_server_time(self):
        """Get server time"""
        return self.public_request('GET','/api/v1/time')['serverTime']

    def get_all_orders(self, symbol):
        """ GET All orders """
        payload = {'symbol': symbol}
        return self.signed_request('GET', '/api/v3/allOrders', **payload)

    def get_open_orders(self, symbol):
        """ GET All orders """
        payload = {'symbol': symbol}
        return self.signed_request('GET', '/api/v3/openOrders', **payload)

    def get_allPrices(self,symbol=None):
        """GET allPrices"""
        if symbol:
            print(type(symbol))
            print('type(symbol)')
            allprice = self.public_request('GET', '/api/v1/ticker/allPrices')
            print(type(allprice))
            print('type(allprice)')

            for price in allprice:
                if price['symbol'] == symbol:
                    return price
        else:
            print(type(symbol))
            print()
            return self.public_request('GET', '/api/v1/ticker/allPrices')

    def get_account(self):
        """GET Account information"""
        return self.signed_request('GET', '/api/v3/account')

    def get_balance(self, asset = None):
        """GET Account information"""
        if asset:
            balances = self.signed_request('GET', '/api/v3/account')
            for balance in balances['balances']:
                if balance['asset'] == asset:
                    return balance
        else:
            return self.signed_request('GET', '/api/v3/account')

    def get_aggTrades(self,symbol):
        """ GET All orders """
        payload = {'symbol': symbol}
        return self.public_request('GET', '/api/v1/aggTrades', **payload)

    def get_depth(self,symbol):
        """ GET All orders """
        payload = {'symbol': symbol}
        return self.public_request('GET', '/api/v1/depth', **payload)

    def get_klines(self,symbol, interval):
        """GET kline by coin and interval(like 1m,1h,1d....)"""
        payload = {
            'symbol': symbol,
            'interval': interval
        }
        return self.public_request('GET', '/api/v1/klines', **payload)

    def get_24hr_ticker(self,symbol):
        """GET 24hr ticker"""
        payload = {
            'symbol': symbol
        }
        return self.public_request('GET', '/api/v1/ticker/24hr', **payload)

    def get_all_ticker(self, symbol = None):
        """GET all ticker"""
        if symbol:
            tickers = self.public_request('GET', '/api/v1/ticker/allPrices')
            for ticker in tickers:
                if ticker['symbol'] == symbol:
                    return ticker
        else:
            return self.public_request('GET', '/api/v1/ticker/allPrices')

    def get_all_bookticker(self, symbol = None):
        """GET all bookticker"""
        if symbol:
            booktickers = self.public_request('GET', '/api/v1/ticker/allBookTickers')
            for bookticker in booktickers:
                if bookticker['symbol'] == symbol:
                    return bookticker
        else:
            return self.public_request('GET', '/api/v1/ticker/allBookTickers')

    def get_mytrade(self, symbol):
        """GET my trade by symbol"""
        payload = {'symbol': symbol}
        return self.signed_request('GET', '/api/v3/myTrades', **payload)

    def get_deposit_history(self, **payload):
        return self.signed_request('POST', '/wapi/v1/getDepositHistory.html', **payload)

    def get_withdraw_history(self, **payload):
        return self.signed_request('POST', '/wapi/v1/getWithdrawHistory.html', **payload)


    def query_order(self, symbol, orderId):
        """query an order by symbol and orderId"""
        payload = {
            'symbol': symbol,
            'orderId': orderId
        }
        return self.signed_request('GET', '/api/v3/order', **payload)


    def new_order(self, **payload):
        """create new order"""
        return self.signed_request('POST', '/api/v3/order', **payload)

    def buy(self, symbol, mtype, quantity, price = 0.0, timeInForce = 'GTC'):
        """create buy order"""
        payload = {
            'symbol': symbol,
            'side': "BUY",
            'type': mtype,
            'quantity': quantity,
            'price': price,
            'timeInForce': timeInForce
        }

        if mtype == 'MARKET':
            del payload['price']
            del payload['timeInForce']

        return self.new_order(**payload)

    def sell(self, symbol, mtype, quantity, price=0.0, timeInForce='GTC'):
        """create sell order"""
        payload = {
            'symbol': symbol,
            'side': "SELL",
            'type': mtype,
            'quantity': quantity,
            'price': price,
            'timeInForce': timeInForce
        }

        if mtype == 'MARKET':
            del payload['price']
            del payload['timeInForce']

        return self.new_order(**payload)

    def cancel_order(self, symbol, orderId):
        """cancel order by symbol ,orderId is not Mandatory"""
        payload = {
            'symbol': symbol,
            'orderId': orderId
        }

        return self.signed_request('DELETE', '/api/v3/order', **payload)

    def start_userdata_stream(self):
        """GET a websocket listkey"""
        return self.apikey_request('POST', '/api/v1/userDataStream')

    def keepalive_userdata_stream(self, listenKey):
        """keepalive a websocket connect"""
        return self.apikey_request('PUT', '/api/v1/userDataStream', listenKey = listenKey)

    def close_userdata_stream(self, listenKey):
        """close a websocket connect by listenKey"""
        return self.apikey_request('DELETE', '/api/v1/userDataStream', listenKey = listenKey)

    #def withdraw(self, asset, address, amount):
    #    """withdraw you asset,it's not working yet,maybe later"""
    #    payload = {
    #        'asset' : asset,
    #        'address': address,
    #        'amount': amount
    #    }
    #    return self.signed_request('POST','/wapi/v1/withdraw.html', **payload)

    def ws_on_message(self, ws, message):
        print(message)

    def ws_on_error(self, ws, error):
        print(error)

    def ws_on_close(self, ws):
        print("### closed ws ###")


    def ws_request(self,ws_url):
        """do a websocket request"""
        print('wsurl:%s', ws_url)
        url = "wss://stream.binance.com:9443/ws/%s" % (ws_url)
        print('url:%s', url)
        websocket.enableTrace(True)
        ws = websocket.WebSocketApp(url,

                                    on_error=self.ws_on_error,
                                    on_close=self.ws_on_close)
        return ws

    def ws_depth(self,symbol):
        """get symbol depth by websocket"""
        print('symbol.lower(): %s', symbol.lower())
        return self.ws_request('%s@depth' % (symbol.lower()))


    def ws_kline(self, symbol, kdate):
        """get symbol kline by websocket"""
        return self.ws_request('%s@kline_%s' % (symbol.lower(), kdate))


    def ws_aggTrade(self, symbol):
        """get aggTrade by websocket"""
        return self.ws_request('%s@aggTrade' % (symbol.lower()))

    def ws_user_data(self):
        """get user data by websocket"""
        return self.ws_request(self.ws_request(self.start_userdata_stream()['listenKey']))


binance = Binance(
    key='RbJWBqQaAM1WYrdqby1o9pSzSG6yK9oblOq6v2h7EhnRh58QZDRyQahqKygwwMhd', 
    secret = 'Iy14FG3VdsKeqGiatRGlkbnwWzEyy84lY2srtKfu26OohrHxU6JUSNFUGqDuLjRX'
    )
while(1):
    try:
        time.sleep(1.5)
        getpricex = json.dumps(binance.get_allPrices())
        getpricexx = json.loads(getpricex)
        for N in getpricexx:
            print(N['symbol'],'binance',N['price'])
            updateMysql(N['symbol'],'binance',N['price'])
    except:
        continue
    #updateMysql(N['symbol'],'binance',N['price'],0,0,0,0,0)
#print(json.dumps(binance.get_balance(asset='asset'), indent = 2))


# --- ws --- # 
def on_message(ws, message):
    print('web socket message doing')
    print(message)
#print('ws_kline')
# ws = binance.ws_kline('ETHBTC', '1m')
# ws.on_message = on_message
# ws.run_forever()

# --- ws --- # 

