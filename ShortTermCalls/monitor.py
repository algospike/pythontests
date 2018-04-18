'''
Created on Apr 13, 2018

@author: C-Arpanjeet.Sandhu
'''

from Domains.Share import Share
from Domains.ShareCal import ShareCall
from Domains.shareInfo import ShareInfo
from Domains.TextDecode import TextDecode
import requests as request 
from bs4 import BeautifulSoup as soup 
from googlefinance.client import get_price_data
import json
import datetime 
from math import floor
import jsonpickle
import pprint

dict ={}

def writeToDisk():
    print('writing to disk')
    global dict
    now = datetime.datetime.now()
    filename = 'user_info_' + str(now.year) + '-'+ str(now.month) + '-' + str(now.day) 
    with open(filename,'w') as f:
        f.write(jsonpickle.encode(dict))
    with open('user_info','w') as f:
        f.write(jsonpickle.encode(dict))

def readDicFromFile():
    global dict
    dict = {}
    with open('user_info','r') as f:
        dict = eval(f.read())
    print('dict',dict)

def shareNameExchange(shareCall):
    text = shareCall.text.split(",")
    shareName = text[1].strip().replace(" " , "+")
    url ="https://www.google.co.in/search?q=" + shareName +"+share+price&oq=" +shareName+"+share+price&aqs=chrome..69i57j0l2.8499j0j4&sourceid=chrome&ie=UTF-8"
    res = request.get(url)
    parsed_html = soup(res.text, "html.parser")
    data = parsed_html.find("h3", {"class": "r"}).text
    arr = data.split("-")
    shareCode = arr[0].strip()
    arr2 = arr[1].split("(")
    shareName = arr2[0].strip()
    shareExchange = arr2[1].split(")")[0]
    shareInfo = ShareInfo()
    shareInfo.populateShareInfo(shareName , shareExchange , shareCode , shareCall)
    return shareInfo
    


def telegramUpdate():
    print("Telegram Update")
    totalCall = []
    nwTime = datetime.datetime.now().timestamp()
    nw = floor(nwTime)
    bfTime = datetime.datetime.now() - datetime.timedelta(hours = 5)
    bf = floor(bfTime.timestamp())
    telegramUpdate = json.loads(request.get("https://api.telegram.org/bot564398612:AAEXUIfrJVFHfBnxS4Uot0Ob5vDPN8Ws69I/getUpdates").text)
    length =  len(telegramUpdate['result'])
    if not length:
        return "no text"
    else:
        value = telegramUpdate['result']
        for val in value:
            interval = val['message']['date']
            if bf <= interval <= nw :
                shareCall = ShareCall()
                shareCall.chatId = val['message']['chat']['id']
                shareCall.date = interval
                shareCall.text = val['message']['text']
                totalCall.append(shareCall)
                
    
    return totalCall

def convertText(text):
    text = text.split(",")
    textDecode = TextDecode()
    textDecode.typeMethod = text[0]
    textDecode.shareName = text[1]
    textDecode.noOfShare = text[2]
    textDecode.price = text[3]
    if "buy" == text[0].lower():
        textDecode.stopLoss = text[4]
        textDecode.targetPrice = text[5]
    return textDecode

def buyShare(shareInfo):
    shareCall = shareInfo.ShareCall
    shareList = dict.get(shareCall.chatId)
    if len(shareInfo.ShareCall.text.split(",")) != 6:
        return None
    textDecode = convertText(shareInfo.ShareCall.text)
    share = Share() 
    id = 1
    if not shareList:
        shareList = []
    else:
        id = len(shareList) + 1
    share.populateBasicShare(id, shareInfo.shareName, shareInfo.shareExchange , textDecode.price , 
                             textDecode.noOfShare , textDecode.stopLoss , textDecode.targetPrice , shareCall.date) 
    share.populateCalShare(0, 0, 0, 0, 0, 0, 0, 0)
    shareList.append(share)
    dict.update({shareCall.chatId:shareList})    
          
def sellShare(chatId ,shareId, noOfShare , sellPrice):
    shareList = dict.get(chatId)
    if not shareList:
        return "no share present to sell"
    else:
        for share in shareList:
            if share.shareId == shareId:
                if share.sellTicker == 0:
                    share.sellTicker = 1
                    share.sellShareNo = noOfShare
                    share.sellPrice = sellPrice
                    share.netProfit =(share.sellShareNo*share.sellPrice) - (share.sellShareNo*share.boughtPrice)   
                    share.remainingShare = share.noOfShares  - share.sellShareNo
                else:
                    share.sellPrice = ((share.sellShareNo*share.sellPrice) + (noOfShare*sellPrice))/(share.sellShareNo +noOfShare)
                    share.sellShareNo = share.sellShareNo + noOfShare
                    share.netProfit = (share.sellPrice*share.sellShareNo) - (share.sellShareNo*share.boughtPrice) 
                    share.remainingShare = share.noOfShares - share.sellShareNo
                    
            
    

'''
buyShare(1234, "asdassd","NSE", 10, 2, "stopLoss", "targetPrice", "buyDate")
sellShare(1234, 1, 1 , 15)
print(dict.get(1234)[0].shareName)
print(dict.get(1234)[0].sellTicker)
print(dict.get(1234)[0].netProfit)
print("changes")
sellShare(1234, 1, 1, 20)
print(dict.get(1234)[0].netProfit)
'''
                    
totalCall = telegramUpdate()
for call in totalCall:
    shareInfo = None
    try:
        shareInfo = shareNameExchange(call)    
    except:
        print('Error')
    if shareInfo:
        text = shareInfo.ShareCall.text.split(",")
        if "buy" == text[0].lower():
            buyShare(shareInfo)
            #print('printing dict',dict)
            if dict.get(464308445):
                print(dict.get(464308445)[0].shareName)
writeToDisk()
readDicFromFile()
    


  

