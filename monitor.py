'''
Created on Apr 13, 2018

@author: C-Arpanjeet.Sandhu
'''

from Domains.Share import Share
from Domains.ShareCal import ShareCall
from Domains.shareInfo import ShareInfo
import requests as request 
from bs4 import BeautifulSoup as soup 
from googlefinance.client import get_price_data
import json
import datetime 
from math import floor
import sched, time


dict ={}
s = sched.scheduler(time.time, time.sleep)

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
    print("asdfg")
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

def buyShare(chatId , shareName ,shareExchange,buyPrice , noOfShare , stopLoss , targetPrice , buyDate):
    shareList = dict.get(chatId)
    share = Share() 
    id = 1
    if not shareList:
        shareList = []
    else:
        id = len(shareList) + 1
    share.populateBasicShare(id, shareName,shareExchange , buyPrice , noOfShare , stopLoss , targetPrice , buyDate) 
    share.populateCalShare(0, 0, 0, 0, 0, 0, 0,0)
    shareList.append(share)
    dict.update({chatId:shareList})    
          
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
                    
            
    


buyShare(1234, "asdassd","NSE", 10, 2, "stopLoss", "targetPrice", "buyDate")
sellShare(1234, 1, 1 , 15)
print(dict.get(1234)[0].shareName)
print(dict.get(1234)[0].sellTicker)
print(dict.get(1234)[0].netProfit)
print("changes")
sellShare(1234, 1, 1, 20)
print(dict.get(1234)[0].netProfit)

totalCall = telegramUpdate()
for call in totalCall:
    shareInfo = shareNameExchange(call)
    text = shareInfo.ShareCall.text.split(",")
    
    
    


  

