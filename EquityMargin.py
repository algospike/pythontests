import requests as request 
from bs4 import BeautifulSoup as soup 
from googlefinance.client import get_price_data
import json
from textwrap import indent
import pandas as pd
import time
from math import floor
import os
 
text = ""
amount = 1700


def sendTelegram(totalResponse):
    try:
        print("in sendTelegram" , totalResponse)
        chat_id = ["464308445"] # chat_id
        bot_id = "bot564398612:AAEXUIfrJVFHfBnxS4Uot0Ob5vDPN8Ws69I" #bot id 
        for id in chat_id:
            print(id)
            url = "https://api.telegram.org/" + bot_id + "/sendMessage?chat_id=" + id + "&text= " + str(totalResponse)
            print(url)
            request.get(url)
        return True 
    except Exception as e:
        print(e)
        time.sleep(60)
        sendTelegram(totalResponse)


isDictionaryEmpty = os.stat("dictionary_data").st_size == 0
dict = {}
if isDictionaryEmpty:
    res = request.get("https://zerodha.com/margin-calculator/Equity/")
    encode = res.encoding
    parse_text =soup(res.text,"html.parser")
    idCount = 1
    firstIteration = True
    while firstIteration:
        heading = parse_text.find("tr", {"data-id": idCount})
        if not heading:
            firstIteration = False;
            break
        tr = heading.find("td",{"class":"scrip"})
        tr1 = heading["data-mis_multiplier"]
        dict.update({tr.text:tr1})
        idCount += 1 
    with open('dictionary_data','w') as f:
        f.write(json.dumps(dict))
else:
    print('Loading dictionary from file')
    with open('dictionary_data','r') as f:
        dict = eval(f.read())
    
print('dict',dict)
     
    
while True:
    telegramUpdate = json.loads(request.get("https://api.telegram.org/bot564398612:AAEXUIfrJVFHfBnxS4Uot0Ob5vDPN8Ws69I/getUpdates").text)
    length =  len(telegramUpdate['result'])
    value = telegramUpdate['result'][length - 1]['message']['text']
    print(value)
    if not text:
        text = value
    else :
        if text != value :
            try:
                text = value
                value = value.replace(" ", "+")
                url ="https://www.google.co.in/search?q=" + value +"+nse+code&oq=" +value+"+nse+code&aqs=chrome..69i57j0l2.8499j0j4&sourceid=chrome&ie=UTF-8"
                res = request.get(url)
                parsed_html = soup(res.text, "html.parser")
                #print(parsed_html)
                nseCode = parsed_html.find("a", {"class": "fl"}).text
                priceValue = parsed_html.find("span",{"style":"font-size:157%"}).text.split("\xa0")[0]
                multipler = dict.get(nseCode + ":EQ")
                toBuy = (amount*float(multipler))/float(priceValue.replace(",", ""))
                print(toBuy)
                sendTelegram(floor(toBuy))
            except Exception as e:
                print(e)
                sendTelegram(e)
                
    time.sleep(5)

 






