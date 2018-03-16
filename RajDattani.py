import requests as request 
import urllib
from bs4 import BeautifulSoup as soup 
import  time

lastText = ""


def urlRajDattani():
    try:
        print("in urlRajDattani")
        res = request.get('http://www.rajdattani.com/')
        return res
    except:
        time.sleep(60)
        urlRajDattani()


def sendTelegram(totalResponse):
    try:
        print("in sendTelegram")
        url = "https://api.telegram.org/bot564398612:AAEXUIfrJVFHfBnxS4Uot0Ob5vDPN8Ws69I/sendMessage?chat_id=464308445&text= " + totalResponse
        url1 = "https://api.telegram.org/bot564398612:AAEXUIfrJVFHfBnxS4Uot0Ob5vDPN8Ws69I/sendMessage?chat_id=506426930&text= " + totalResponse
        url2 = "https://api.telegram.org/bot564398612:AAEXUIfrJVFHfBnxS4Uot0Ob5vDPN8Ws69I/sendMessage?chat_id=489260733&text= " + totalResponse
        request.get(url)
        request.get(url1)
        request.get(url2)
        return True 
    except:
        time.sleep(60)
        sendTelegram(totalResponse)


def rajDattani():
    res = urlRajDattani()
    parsed_html = soup(res.text, "html.parser")
    heading = parsed_html.findAll("h3", {"class": "post-title entry-title"})
    headingValue = heading[0].findChildren();
    
    
    content = parsed_html.findAll("div", {"class": "post-body entry-content"})
    contentChild = content[0].findChildren(recursive=False);
    
    
    childValue = ""
    for child in contentChild:
        childValue += urllib.parse.quote_plus(child.text)
    totalResponse = headingValue[0].text + childValue
    global lastText
    if not lastText:
        lastText = totalResponse 
        sendTelegram(totalResponse)
    else:
        print(totalResponse)
        if lastText != totalResponse:
            lastText = totalResponse
            sendTelegram(totalResponse)
    time.sleep(20)
    


while True:
    rajDattani()
