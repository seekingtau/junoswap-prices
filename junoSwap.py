import requests
import random
import json
import base64
import string
import pandas as pd
import ssl
import urllib

# Headers and lists
headers = {
        'Host': 'rpc-juno.itastakers.com',
        'Content-Type': 'application/json',
        }

swapAddressList = []
decimalList = []
symbolList = []

# Probably necessary, I don't know what it does
def genId():
    res = ''
    
    for i in range(12):
        res = res+random.choice(string.digits)
    return int(res)

# JSON reader
urlContext = ssl._create_unverified_context()
url = 'https://raw.githubusercontent.com/CosmosContracts/junoswap-asset-list/main/token_list.json'
jsonData = urllib.request.urlopen(url, context = urlContext)

jsonProcessed = json.load(jsonData)

tokenData = jsonProcessed['tokens']

tokenListLength = len(tokenData)

for x in range(0, tokenListLength):
    swapAddress = tokenData[x]['swap_address']
    decimalCount = tokenData[x]['decimals']
    tokenSymbol = tokenData[x]['symbol']
    
    swapAddressList.append(swapAddress)
    decimalList.append(decimalCount)
    symbolList.append(tokenSymbol)
    
print(swapAddressList)
print(decimalList)
print(symbolList)

# Ratios
def getAssetRatio():
    global headers
    global swapAddressList
    
    for x in swapAddressList:
        rawCommand = '\n?' + x + '7{"token2_for_token1_price":{"token2_amount": "1000000"}}'
        encodedTerm = rawCommand.encode('UTF-8')
        b16EncodedTerm = base64.b16encode(encodedTerm)
        data = str(b16EncodedTerm, encoding = 'UTF-8')
        newData = data.lower()
        print(newData)
    
    jsonData = {"jsonrpc": "2.0", "id": genId(), "method": "abci_query", "params": {"path": "/cosmwasm.wasm.v1.Query/SmartContractState", "data": newData, "prove": False}}
    
    rq = requests.post('https://rpc-juno.itastakers.com/', headers = headers, json = jsonData, timeout = 10)
    
    print(rq.text)

    if rq.status_code == 200:
        print(round(float(base64.b64decode(json.loads(rq.text)['result']['response']['value']).split('"token2_amount":"'.encode('utf-8'),1)[1].split('"}'.encode('utf-8'),1)[0])/1000000,2))

getAssetRatio()