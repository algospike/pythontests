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
from math import floor, ceil
import jsonpickle
import schedule
from datetime import datetime as dt, time as t
import time
import datetime
dict = {}

runTelegramHr = 1


def fileOperation():
    print("in file Operation")
    writeToDisk()
    readDicFromFile()
    print("file Operation end")
    
    
def readDicFromFile():
    global dict
    read_dict = {}
    read_fail =  False
    try:
        with open('/home/shortterm/files/user_info', 'r') as f:
            print('reading file user_info at /home/shortterm/files/user_info')
            read_dict = eval(f.read())
    except :
        print("no file present to read")
        read_fail = True
    if not read_fail:
        print('read from file ', read_dict)
        populateSharesInDic(read_dict)


def populateSharesInDic(read_dic):
    global dict
    dict = {}
    for k,v in read_dic.items():
        shareList = []
        for e in v:
            share = Share()
            share.populateShare(e)
            shareList.append(share)
        dict.update({k:shareList})
    print('dict after read ',dict)


def writeToDisk():
    print('writing to disk')
    now = datetime.datetime.now()
    filename = '/home/shortterm/files/user_info_' + str(now.year) + '-' + str(now.month) + '-' + str(now.day) 
    with open(filename, 'w') as f:
        f.write(jsonpickle.encode(dict))
    with open('/home/shortterm/files/user_info', 'w') as f:
        f.write(jsonpickle.encode(dict))
    print('dict after write ',dict)
    print('file written')


def shareNameExchange(shareCall):
    text = shareCall.text.strip().split(",")
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
        url = "https://api.telegram.org/" + bot_id + "/sendMessage?chat_id=" + str(chatId) + "&text= " + str(totalResponse) + "&parse_mode=HTML"   
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
    nw = ceil(nwTime)
    bfTime = datetime.datetime.now() - datetime.timedelta(hours=runTelegramHr)
    bf = floor(bfTime.timestamp())
    print("time to compare before",bf)
    print("time to compare now",nw)
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
    text = text.strip().split(",")
    textDecode = TextDecode()
    textDecode.typeMethod = text[0].strip()
    textDecode.shareName = text[1].strip()
    textDecode.noOfShare = int(text[2].strip())
    textDecode.price = float(text[3].strip())
    if "sold" != text[0].lower():
        textDecode.stopLoss = float(text[4].strip())
        textDecode.targetPrice = float(text[5].strip())
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
    share.realizedProfit = 0.0
    shareList.append(share)
    dict.update({shareCall.chatId:shareList})    
    #print("in buy share", dict)
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
    #print(shareCode, shareExchange)
    params = {
            'q': shareCode,
            'x': shareExchange,
            'i': "1",
            }
    data_list = get_price_data(params)
    #print(data_list)
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
    livePrice = 0.0
    try:
        livePrice = getLivePrice(share.shareCode , share.shareExchange)
    except Exception as e: 
        print("excpetion occur due to market close " , e)
        livePrice = getLivePrice1(share.shareCode)
    
    #print("live price for",share.shareCode,livePrice)
    realizedProfit = (share.remainingShare * livePrice) - (share.remainingShare * share.boughtPrice)
    realizedProfit = round(realizedProfit , 2)
    share.realizedProfit = realizedProfit
    stopLoss = share.stopLoss
    targetPrice = share.targetPrice
    stopLivePercent = (livePrice - stopLoss) * (float(100)) / livePrice
    targetLivePercent = (targetPrice - livePrice) * (float(100)) / livePrice
    if floor(stopLivePercent) < 1.5:
        text = "Stop Loss " + str(stopLoss) + " for " + share.shareName + " is less than 1.5 percent at live price " + str(livePrice)
        sendTelegram(text , chatId)
    if floor(targetLivePercent) < 2:
        text = "target Price " + str(targetPrice) + " for " + share.shareName + " is less than 2 percent at live price " + str(livePrice)
        sendTelegram(text , chatId)



def monitorShares():
    marketOpen = False
    print("time on server",dt.now().time())
    if t(9,0) <=  dt.now().time() <= t(15,30) and datetime.datetime.today().weekday() < 5:
        marketOpen  = True
    if marketOpen:
        print("in MonitorShares")
        print(dict)
        keys = dict.keys()
        for key in keys:
            shareList = dict.get(key)
            for share in shareList:
                if share.remainingShare != 0:
                    print("in if " , share.remainingShare)
                    monitorShare(share , key)
                    print(dict.get(key)[0])
        writeToDisk()
    else:
        print('Market closed')        



def sendUpdateMessage(type , share , call):
    text = ""
    if share:
        text = type + " order for "+share.shareName +" has been updated "
    else:
        text = "some error occur plz resend the order" + call.text
    sendTelegram(text, call.chatId) 
    
def mainfunction():
    print("in mainFunction")
    totalCall = telegramUpdate()
     
    for call in totalCall:
        shareInfo = None
        try:
            print(call.text)
            shareInfo = shareNameExchange(call)    
        except Exception as e:
            print('share info error',e)
        if shareInfo:
            
            text = shareInfo.ShareCall.text.strip().split(",")
            if "bought" == text[0].lower():
                share = buyShare(shareInfo)
                sendUpdateMessage(text[0].lower() , share , call)
            if "sold" == text[0].lower():
                share = sellShare(shareInfo)
                sendUpdateMessage(text[0].lower() , share , call)
            if "reinvest" == text[0].lower():
                share = reinvestShare(shareInfo)
                sendUpdateMessage(text[0].lower() , share , call)
    print('first time',dict)        
    writeToDisk()

        
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
       
        for share in shareList:
            totalBuy = totalBuy + (share.boughtPrice * share.noOfShares)
            totalBuy = round(totalBuy , 2)
            totalProfit = totalProfit + share.netProfit
            totalReinvest = totalReinvest + share.reinvestAmount
            totalRealizedProfit = totalRealizedProfit + share.realizedProfit  
            netBuy = totalBuy - totalReinvest
        lenBuy = len(str(netBuy))
        lenAmount = len("Amount")
        lenProfit = len(str(totalProfit))
        offset = 0 
        offsetProfit = 0
        text = ""
        if lenBuy < lenAmount:
            text = text + "<pre> Amount" + " "
            offset = lenAmount
        else:
            text = text + "<pre> Amount" + " "*(lenBuy - lenAmount + 1)
            offset = lenBuy
        if lenProfit < len("Net"):
            text = text + "Net "
            offsetProfit = len("Net")
        else:
            text = text + "Net" + " "*(lenProfit - len("Net") + 1)
            offsetProfit = lenProfit
        text = text + "Relz. \n"
         
         
        text = text + " " + str(netBuy) + " " * (offset - len(str(netBuy)))
        text = text +  " " + str(totalProfit) + " " * (offsetProfit - len(str(totalProfit)))
        text = text +  " " + str(totalRealizedProfit)
        text = text + " </pre>"  
        sendTelegram(text, key)

                   
def sendPortfolioUpdates():
    print('send portfolio updates')
    keys = dict.keys()
    now = datetime.datetime.now()
    for key in keys:
        shareList = dict.get(key)
        createMessageForShares(key, shareList)


def createMessageForShares(key, shares):
    lnCode = 0
    lnProfit = 0
    for sh in shares:
        if lnCode < len(str(sh.shareCode)):
            lnCode = len(str(sh.shareCode))
        if lnProfit < len(str(round(sh.netProfit,2))):
            lnProfit = len(str(round(sh.netProfit,2)))
        
    shareLen = len("ShareName")
    text = ""
    if shareLen < lnCode:
        text = text + "<pre> ShareName" + " "*((lnCode - shareLen) + 1) 
    else:
        text = text + "<pre> ShareName" + " "*((shareLen - lnCode) + 1)
    text = text + "Net"+" "*((lnProfit - len("Net")) + 1 ) + "Relz \n"  
    for s in shares:
        offset = (lnCode - len(str(s.shareCode)))
        offsetProfit = (lnProfit - len(str(round(s.netProfit,2)))) 
        text = text + ' ' + str(s.shareCode) + " " * offset
        text = text + " " + str(round(s.netProfit,2)) + " " * offsetProfit 
        text = text + " " + str(round(s.realizedProfit,2)) + "\n"
    text = text + " </pre>"  
    print('sending to ', key)
    sendTelegram(text + '', key)


def createInstruction():
    text = "<pre> For Bought Share :-Bought,Sharename,NoOfShare,BoughtPrice,StopLoss,TargetPrice \n \n For Sold Share :-Sold,Sharename,NoOfShare,BoughtPrice \n \n For Reinvest Share :-reinvest,Sharename,NoOfShare,BoughtPrice,StopLoss,TargetPrice  </pre> "
    keys = dict.keys()
    for key in keys:
        sendTelegram(text, key)


schedule.every(runTelegramHr).hours.do(mainfunction)
schedule.every(2).hours.do(monitorShares)
schedule.every().day.at("9:00").do(fileOperation)
schedule.every().day.at("9:02").do(createInstruction)
schedule.every().day.at("20:45").do(sendPortfolioUpdates)
schedule.every().day.at("20:55").do(finalShortTermRst)

print('Started')
while True:
    schedule.run_pending()
    time.sleep(1) 
