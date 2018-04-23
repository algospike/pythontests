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
import pandas as pd
from googlefinance.client import get_price_data
import json
import datetime 
from math import floor
import jsonpickle
import time
import schedule
from argcomplete.compat import str
from _ast import Str
from numpy import str0

dict = {}


def readDicFromFile():
    global dict
    dict = {}
    try:
        with open('user_info', 'r') as f:
            dict = eval(f.read())
    except :
        print("no file present to read")


def writeToDisk():
    print('writing to disk')
    now = datetime.datetime.now()
    filename = 'user_info_' + str(now.year) + '-' + str(now.month) + '-' + str(now.day) 
    with open(filename, 'w') as f:
        f.write(jsonpickle.encode(dict))
    with open('user_info', 'w') as f:
        f.write(jsonpickle.encode(dict))
    keys = dict.keys()
    for key in keys:
        with open(str(key) + "_" + str(now.year) + '-' + str(now.month) + '-' + str(now.day), 'w') as f:
            f.write(jsonpickle.encode(dict.get(key)))

    # print('dict',dict)


def shareNameExchange(shareCall):
    text = shareCall.text.split(",")
    shareName = text[1].strip().replace(" " , "+")
    url = "https://www.google.co.in/search?q=" + shareName + "+share+price&oq=" + shareName + "+share+price&aqs=chrome..69i57j0l2.8499j0j4&sourceid=chrome&ie=UTF-8"
    res = request.get(url)
    parsed_html = soup(res.text, "html.parser")
    data = parsed_html.find("h3", {"class": "r"}).text
    arr = data.split("-")
    shareCode = arr[0].strip()
    arr2 = arr[1].split("(")
    shareName = arr2[0].strip()
    shareExchange = arr2[1].split(")")[0]
    shareInfo = ShareInfo()
    shareInfo.populateShareInfo(shareName , shareCode, shareExchange  , shareCall)
    return shareInfo

  
def sendTelegram(totalResponse , chatId):
    try:
        print("in sendTelegram" , totalResponse)
        bot_id = "bot564398612:AAEXUIfrJVFHfBnxS4Uot0Ob5vDPN8Ws69I"  # bot id 
        url = "https://api.telegram.org/" + bot_id + "/sendMessage?chat_id=" + str(chatId) + "&text= " + str(totalResponse) + "&parse_mode=Markdown"   
        request.get(url)
        return True 
    except Exception as e:
        print(e)
        time.sleep(60)
        sendTelegram(totalResponse, chatId)
        
            
def telegramUpdate():
    print("Telegram Update")
    totalCall = []
    nwTime = datetime.datetime.now().timestamp()
    nw = floor(nwTime)
    bfTime = datetime.datetime.now() - datetime.timedelta(hours=10)
    bf = floor(bfTime.timestamp())
    telegramUpdate = json.loads(request.get("https://api.telegram.org/bot564398612:AAEXUIfrJVFHfBnxS4Uot0Ob5vDPN8Ws69I/getUpdates").text)
    length = len(telegramUpdate['result'])
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
    textDecode.noOfShare = int(text[2])
    textDecode.price = float(text[3])
    if "sold" != text[0].lower():
        textDecode.stopLoss = float(text[4])
        textDecode.targetPrice = float(text[5])
    return textDecode


def buyShare(shareInfo):
    shareCall = shareInfo.ShareCall
    shareList = dict.get(shareCall.chatId)
    if len(shareInfo.ShareCall.text.split(",")) != 6:
        return None
    textDecode = convertText(shareInfo.ShareCall.text)
    
    id = 1
    if not shareList:
        shareList = []
    else:
        id = len(shareList) + 1
    
    for shareCheck in shareList:
        shareCode = shareCheck.shareCode
        if shareCode == shareInfo.shareCode:
            boughtPrice = ((shareCheck.boughtPrice*shareCheck.noOfShares) + (textDecode.noOfShare*textDecode.price))/(shareCheck.noOfShares + textDecode.noOfShare)
            shareCheck.boughtPrice = round(boughtPrice,2)
            shareCheck.noOfShares = shareCheck.noOfShares + textDecode.noOfShare
            shareCheck.stopLoss = textDecode.stopLoss
            shareCheck.targetPrice = textDecode.targetPrice
            shareCheck.remainingShare = textDecode.noOfShare
            return shareCheck
            
    share = Share() 
    
    share.populateBasicShare(id, shareInfo.shareName,shareInfo.shareCode,shareInfo.shareExchange , textDecode.price ,
                             textDecode.noOfShare , textDecode.stopLoss , textDecode.targetPrice , shareCall.date) 
    share.remainingShare = textDecode.noOfShare
    shareList.append(share)
    dict.update({shareCall.chatId:shareList})    
    print("in buy share", dict)
    return share

          
def sellShare(shareInfo):
    shareCall = shareInfo.ShareCall
    shareList = dict.get(shareCall.chatId)
    text = convertText(shareCall.text)
    if not shareList:
        return "no share present to sell"
    else:
        for share in shareList:
            if share.shareCode == shareInfo.shareCode and share.remainingShare >= text.noOfShare:
                if share.sellTicker == 0:
                    share.sellTicker = 1
                    share.sellShareNo = text.noOfShare
                    share.sellPrice = text.price
                    share.netProfit = (float(share.sellShareNo) * share.sellPrice) - (float(share.sellShareNo) * share.boughtPrice)   
                    share.remainingShare = share.noOfShares - share.sellShareNo
                else:
                    share.sellPrice = ((share.sellShareNo * share.sellPrice) + (float(text.noOfShare) * text.price)) / float((share.sellShareNo + text.noOfShare))
                    share.sellShareNo = share.sellShareNo + text.noOfShare
                    share.netProfit = (share.sellPrice * share.sellShareNo) - (share.sellShareNo * share.boughtPrice) 
                    share.remainingShare = share.noOfShares - share.sellShareNo
        return share
    
def getLivePrice(shareCode , shareExchange):
    print(shareCode, shareExchange)
    params = {
            'q': shareCode,
            'x': shareExchange,
            'i': "1",
            }
    data_list = get_price_data(params)
    print(data_list)
    data = pd.DataFrame(data_list);
    price = data.at[data.last_valid_index(), 'High']
    return price    

def getLivePrice1(value):
    url ="https://www.google.co.in/search?q=" + value +"+share+price&oq=" +value+"+share+price&aqs=chrome..69i57j0l2.8499j0j4&sourceid=chrome&ie=UTF-8"
    res = request.get(url)
    parsed_html = soup(res.text, "html.parser")
   # print(parsed_html)
    priceValue = parsed_html.find("span",{"style":"font-size:157%"}).text.split("\xa0")[0]
    return float(priceValue.replace(",",""))

def monitorShare(share , chatId):
    print("in MonitorShare")
    #livePrice = getLivePrice(share.shareCode , share.shareExchange)
    livePrice = getLivePrice1(share.shareCode)
    realizedProfit = float(share.remainingShare) * livePrice - float((int(share.remainingShare) * int(share.boughtPrice)))
    realizedProfit = round(realizedProfit , 2)
    share.realizedProfit = realizedProfit
    stopLoss = share.stopLoss
    targetPrice = share.targetPrice
    stopLivePercent = (livePrice - stopLoss) * (float(100)) / livePrice
    print(floor(stopLivePercent))
    targetLivePercent = (targetPrice - livePrice) * (float(100)) / livePrice
    print(floor(targetLivePercent))
    if floor(stopLivePercent) < 1.5:
        text = "`Stop Loss` " + str(stopLoss) + " for " + share.shareName + " is `less than 1.5 pecent` at live price " + str(livePrice)
        #sendTelegram(text , chatId)
    if floor(targetLivePercent) < 2:
        text = "target Price " + str(targetPrice) + " for " + share.shareName + " is less than 2 pecent at live price " + str(livePrice)
        #sendTelegram(text , chatId)

    
def monitorShares():
    print("in MonitorShares")
    print(dict)
    keys = dict.keys()
    for key in keys:
        shareList = dict.get(key)
        for share in shareList:
            print("in second for loop")
            try:
                share = jsonpickle.decode(json.dumps(share))
            except :
                print("file read share")
            if share.remainingShare != 0:
                print("in if " , share.remainingShare)
                monitorShare(share , key)
                print(dict.get(key)[0])
    writeToDisk()        

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


def sendUpdateMessage(type , share , call):
    text = ""
    if share:
        text = type + " order for "+share.shareName +" has been updated "
    else:
        text = "some error occur plz resend the order" + call.text
    sendTelegram(text, call.chatId) 
    
def mainfunction():
    print("in mainFunction")
    #readDicFromFile()
    totalCall = telegramUpdate()
     
    for call in totalCall:
        shareInfo = None
        try:
            print(call.text)
            shareInfo = shareNameExchange(call)    
        except Exception as e:
            print(e)
        if shareInfo:
            
            text = shareInfo.ShareCall.text.split(",")
            if "bought" == text[0].lower():
                share = buyShare(shareInfo)
                #sendUpdateMessage(text[0].lower() , share , call)
            if "sold" == text[0].lower():
                share = sellShare(shareInfo)
               # sendUpdateMessage(text[0].lower() , share , call)
            if "reinvest" == text[0].lower():
                share = reinvestShare(shareInfo)
                sendUpdateMessage(text[0].lower() , share , call)
            
    writeToDisk()
    #readDicFromFile()

        
def reinvestShare(shareInfo):
    shareCall = shareInfo.ShareCall
    shareList = dict.get(shareCall.chatId)
    if len(shareInfo.ShareCall.text.split(",")) != 6:
        return None
    textDecode = convertText(shareInfo.ShareCall.text)
    share = Share() 
    reinvestAmount = textDecode.price * textDecode.noOfShare
    for share in shareList:
        if share.sellTicker == 1 and share.reinvestAmount < share.netProfit:
            reinvestAvaiable = share.netProfit - share.reinvestAmount
            if reinvestAmount > 0 :
                reinvestAmount = reinvestAmount - reinvestAvaiable
                share.reinvestAmount = share.reinvestAmount + reinvestAvaiable
            
    return buyShare(shareInfo)


def finalShortTermRst():
    keys = dict.keys()
    for key in keys:
        shareList = dict.get(key)
        totalBuy = 0.0
        totalReinvest = 0.0
        totalProfit = 0.0
        totalRealizedProfit = 0.0
        netBuy = 0.0
        text = "``` TotalAmount  NetProfit  Profit \n"
        for share in shareList:
            totalBuy = totalBuy + (share.boughtPrice * share.noOfShares)
            totalBuy = round(totalBuy , 2)
            totalProfit = totalProfit + share.netProfit
            totalReinvest = totalReinvest + share.reinvestAmount
            totalRealizedProfit = totalRealizedProfit + share.realizedProfit  
            netBuy = totalBuy - totalReinvest
        text = text + str(netBuy)
        if totalProfit < 0:
            text = text + "  `" + str(totalProfit) + "`"
        else:
            text = text + "  " + str(totalProfit)
        if totalRealizedProfit < 0:
            text = text + "  `" + str(totalRealizedProfit) + "`"
        else:
            text = text + "  " + str(totalRealizedProfit)
        text = text + "```"  
        sendTelegram(text, key)

                   
def sendPortfolioUpdates():
    print('send portfolio updates')
    #readDicFromFile()
    # print(dict)
    keys = dict.keys()
    now = datetime.datetime.now()
    for key in keys:
        filename = str(key) + "_" + str(now.year) + '-' + str(now.month) + '-' + str(now.day)
        # print('reading file',filename)
        with open(filename, 'r') as f:
            s = f.read()
            share = jsonpickle.decode(s)
            createMessageForShares(key, share)


def createMessageForShares(key, shares):
    text = '```'
    for s in shares:
        text = text + ' ' + str(s.shareCode)
        if s.netProfit < 0:
            text = text + "    `" + str(s.netProfit) + "`"
        else:
            text = text + "    " + str(s.netProfit)
        if s.realizedProfit < 0:
            text = text + "    `" + str(s.realizedProfit) + "`\n"
        else:
            text = text + "    " + str(s.realizedProfit) +"\n"
    print('sending to ', key)
    sendTelegram(text + '```', key)


    # print(v)
def createInstruction():
    text = "``` For Bought Share :-Bought,Sharename,NoOfShare,BoughtPrice,StopLoss,TargetPrice \n \n For Sold Share :-Sold,Sharename,NoOfShare,BoughtPrice```"
    keys = dict.keys()
    for key in keys:
        sendTelegram(text, key)


mainfunction()
monitorShares()
sendPortfolioUpdates()
finalShortTermRst()
#readDicFromFile()
#createInstruction()
#schedule.every().day.interval
# schedule.every(1).seconds.do(mainfunction)
# schedule.every(5).seconds.do(monitorShares)
# schedule.every(10).seconds.do(sendPortfolioUpdates)
# schedule.every().day.at("20:30").do(sendPortfolioUpdates)
# schedule.every().day.at("9:00").do(createInstruction)

# schedule.every(5).minutes.do(mainfunction)
# schedule.every(2).hour.do(monitorShares)

while True:
    schedule.run_pending()
    time.sleep(1) 

