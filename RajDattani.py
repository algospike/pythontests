import requests as request 
import urllib
from bs4 import BeautifulSoup as soup 
import  time
from array import array



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
        chat_id = ["","",""] #chat_id 
        bot_id = "" #bot id 
        for id in chat_id:
            url = "https://api.telegram.org/" + bot_id + "/sendMessage?chat_id=" + id + "&text= " + totalResponse
            request.get(url)
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
    try:
        rajDattani()
    except:
        time.sleep(60)
        rajDattani()
    
        
    
