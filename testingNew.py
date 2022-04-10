import requests
import random
import json
import base64
import string
import matplotlib.pyplot as plt
import pandas as pd
import time
import datetime

# Headers and lists
headers = {
        'Host': 'rpc-juno.itastakers.com',
        'Content-Type': 'application/json',
        }

swapAddressList = []
decimalList = []
symbolList = []
ratioList = []
tickerRatioList = []
priceList = []
tickerPriceList = []
tickerDictionary = {'JUNO': {'address': 'juno1hue3dnrtgf9ly2frnnvf8z5u7e224ctc4hk7wks2xumeu3arj6rs9vgzec','decimals': 6, 'tokenCount': '1000000'}}

junoPrice = 0

# Probably necessary, I don't know what it does
def genId():
    res = ''
    
    for i in range(12):
        res = res+random.choice(string.digits)
    return int(res)

# JSON reader
url = 'https://raw.githubusercontent.com/CosmosContracts/junoswap-asset-list/main/token_list.json'
jsonData = requests.get(url,headers={'Host':'raw.githubusercontent.com','Content-Type':'application/json'})

jsonProcessed = json.loads(jsonData.text)

tokenData = jsonProcessed['tokens']

tokenListLength = len(tokenData)

for x in range(0, tokenListLength):
    swapAddress = tokenData[x]['swap_address']
    decimalCount = int(tokenData[x]['decimals'])
    tokenSymbol = tokenData[x]['symbol']
    
    swapAddressList.append(swapAddress)
    decimalList.append(decimalCount)
    symbolList.append(tokenSymbol)
    
    tokenCount = 10 ** decimalCount
    
    tickerDictionary[tokenSymbol] = {'address':swapAddress,'decimals':decimalCount,'tokenCount':tokenCount}
    
def getAssetRatio(ticker):
    global headers
    global swapAddressList
    global tickerDictionary
    
    tokenAmount = tickerDictionary[ticker]['tokenCount']
    swapAddress = tickerDictionary[ticker]['address']
    decimalCount = tickerDictionary[ticker]['decimals']
            
    rawCommand = '\n?' + swapAddress + ''+str(decimalCount + 1)+'{"token2_for_token1_price":{"token2_amount":"'+str(tokenAmount)+'"}}'
    encodedTerm = rawCommand.encode('UTF-8')
    b16EncodedTerm = base64.b16encode(encodedTerm)
    data = str(b16EncodedTerm, encoding = 'UTF-8')
    newData = data.lower()
        
    jsonData = {"jsonrpc":"2.0","id":genId(),"method":"abci_query","params":{"path":"/cosmwasm.wasm.v1.Query/SmartContractState","data":newData,"prove":False}}
        
    a = requests.post('https://rpc-juno.itastakers.com/',headers=headers,json=jsonData,timeout=10)
    
    if a.status_code == 200:
        ratioToJuno = str(float(base64.b64decode(json.loads(a.text)['result']['response']['value']).split('"token1_amount":"'.encode('utf-8'),1)[1].split('"}'.encode('utf-8'),1)[0])/1000000)
        
        return ratioToJuno
    
def returnJunoPrice():
    global headers
    global junoPrice
    
    jsonData = {"jsonrpc":"2.0","id":genId(),"method":"abci_query","params":{"path":"/cosmwasm.wasm.v1.Query/SmartContractState","data":"0a3f6a756e6f3168756533646e72746766396c793266726e6e7666387a3575376532323463746334686b37776b733278756d65753361726a3672733976677a656312377b22746f6b656e315f666f725f746f6b656e325f7072696365223a7b22746f6b656e315f616d6f756e74223a2231303030303030227d7d","prove":False}}
    a = requests.post('https://rpc-juno.itastakers.com/',headers=headers,json=jsonData,timeout=10)
    if a.status_code == 200:
        junoPrice = round(float(base64.b64decode(json.loads(a.text)['result']['response']['value']).split('"token2_amount":"'.encode('utf-8'),1)[1].split('"}'.encode('utf-8'),1)[0])/1000000,4)
    
        return junoPrice
    
def getAssetPrice(ticker):
    global tickerDictionary
    
    assetRatioToJuno = float(getAssetRatio(ticker))
    junoPriceNow = float(returnJunoPrice())
    
    assetPriceNow = assetRatioToJuno * junoPriceNow
    
    return assetPriceNow

def priceAsset(asset):
    priceDict = {'price': [], 'time': []}
    
    path = asset + 'Prices.csv'

    while True:
        price = getAssetPrice(asset)
        
        timeNow = datetime.datetime.now()
        
        priceDict['price'].append(price)
        priceDict['time'].append(timeNow)
        
        df = pd.DataFrame(data = priceDict)
            
        df.to_csv(path, index = False)
        
        time.sleep(15)
        
priceAsset('HOPE')