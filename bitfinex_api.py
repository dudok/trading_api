
import requests
import json
import base64
import hashlib
import time
import hmac

'''
This is an example of how to use a cryptocurrency trading exchange API.
The trading exchange is Bitfinex. Other exchanges have similar API.
In this specific case requests to the public ticker and balances are being made.
Other requests are possible with the BitfinexResponse and BitfinexAUTH object.
Only the url needs to be changed for this at the bottom of the script.

For the API to work you need to fill in your API key and secret of Bitfinex
at the bottom of the script.
The authentication procedure is as follows:

The payload is the parameters object, first JSON encoded, and then encoded into Base64
payload = parameters-object -> JSON encode -> base64

The signature is the hex digest of an HMAC-SHA384 hash where the message is your payload, 
and the secret key is your API secret.
'''

class BitfinexAUTH:
    """creates an authenticator object for accessing the bitfinex api."""
    def __init__(self, key, secret, params):
        
        self.key = key
        self.secret = secret
        self.params = params
        self.hashing()
    
    def hashing(self):
        """keyed-hashing for message authentication. Creates a signature.
        """
        payload_json = json.dumps(self.params)
        self.payload = base64.b64encode(bytes(payload_json, "utf-8"))
        self.signature = hmac.new(self.secret, self.payload, hashlib.sha384).hexdigest()
        
    

class BitfinexResponse:
    """Creates a response object from a GET request that has an authenticator 
    object and has attributes:
    r: the response of the get request.
    data: the decoded json content from the request.
    """
    def __init__(self, url, key, secret, pairs=None):
        
        self.url = url 
        if pairs == None:
            pairs = {}
        self.pairs = pairs
        self.params()
        self.auth = BitfinexAUTH(key, secret, self.params)
        self.r = self.request()
        self.data = self.r.json()
        
    def request(self):
        """returns the response of the GET request.
        """
        headers = {
          'X-BFX-APIKEY' : self.auth.key,
          'X-BFX-PAYLOAD' : self.auth.payload,
          'X-BFX-SIGNATURE' : self.auth.signature
          }
        
        return requests.get(self.url, headers=headers)
    
    def params(self):
        """the params needed for the authentication request.
        """
        request = self.url.replace('https://api.bitfinex.com', '')
        self.params = {
            'request': request,
            'nonce':str( int(time.time()) ), 
            'options':{}    }
        self.params.update(self.pairs)
    
    def __str__(self): 
        """the output when response object is printed.
        """
        code= 'Response Code: ' + str(self.r.status_code) 
        headers = 'Response Header: ' + str(self.r.headers)
        content = 'Response Content: '+ str(self.r.content)
        return '\n'.join((code, headers, content))
    

class TickersBitfinex:
    """creates a ticker object with the live data of the currencies stored
    in the self.data dictionary.
    """
    def __init__(self, portfolio):
        self.data = {}
        self.url = "https://api.bitfinex.com/v1/pubticker/"
    
        for d in portfolio:
            currency = d['currency'] 
            if currency != 'usd':
                url = self.url + currency + "usd"
                r = requests.request("GET", url)
                self.data[currency] = r.json()
                
    def __str__(self):
        return str(self.data)
                
class BitfinexPortfolio:
    """creates a portfolio object of all the currencies owned on Bitfinex.
    It has a Response object and a Tickers object. It has attributes:
    self.data: the data of the Response object with usd price added and zero
    balances removed.
    self.total: the total amount of currencies owned calculated in dollars.
    """
    def __init__(self):
        self.total = 0
        self.currencies = []
        self.response = BitfinexResponse(bitfinexURL, bitfinexKey, bitfinexSecret)
        self.data = self.response.data
        self.remove_zero_balances()
        self.tickers = TickersBitfinex(self.data)
        self.add_usd_prices()
        self.total_usd()
        
    def add_usd_prices(self):  
        for d in self.data:
            currency = d['currency']
            if currency == 'usd':   
                d["price"] = "1.0"
            else:     
                d["price"] = self.tickers.data[currency]["last_price"]
            d["usd"] = str( float(d["price"]) * float(d["amount"]) )
                
    def remove_zero_balances(self):
        self.data = [d for d in self.data if float(d["amount"]) != 0]
                
    def total_usd(self):
        for d in self.data:
            self.total += float(d["usd"])
    
    def __str__(self):
        """prints a table of all the currencies owned with their amount
        and the value of that in dollars.
        """
        table = ''
        for d in self.data:
            if float(d["usd"]) >= 1:
                table += '{}\t{}\t\t{}\n'.format(d["currency"], d["amount"], d["usd"])
        table += '\ntotal usd\t' + str(self.total)
        return table


if __name__=='__main__':            

    # fill in the url of the api, your api key and secret here.
    bitfinexURL = 'https://api.bitfinex.com/v1/balances'
    bitfinexKey = '...'
    bitfinexSecret = b'...'             

    portfolio = BitfinexPortfolio()
    print(portfolio)








