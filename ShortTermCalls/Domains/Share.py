'''
Created on Apr 13, 2018

@author: C-Arpanjeet.Sandhu
'''

class Share:
    shareId = ""
    shareName = ""
    shareCode = ""
    shareExchange = ""
    boughtPrice = 0.0
    noOfShares = 0
    stopLoss = 0.0
    targetPrice = 0.0
    buyDate = ""
    remainingShare = 0
    sellTicker = 0
    sellShareNo = 0
    sellPrice = 0.0
    shareReinvest = 0
    reinvestAmount = 0.0
    netProfit = 0.0
    realizedProfit = 0.0
    
    def populateShare(self,e):
        self.shareId = e['shareId'] if 'shareId' in e else 0 
        self.shareName = e['shareName'] if 'shareName' in e else "Not Found" 
        self.shareExchange = e['shareExchange'] if 'shareExchange' in e else "NSE"
        self.shareCode = e['shareCode'] if 'shareCode' in e else "Not Found"
        self.boughtPrice = e['boughtPrice'] if 'boughtPrice' in e else 0.0
        self.noOfShares = e['noOfShares'] if 'noOfShares' in e else 0
        self.stopLoss = e['stopLoss'] if 'stopLoss' in e else 0.0
        self.targetPrice = e['targetPrice'] if 'targetPrice' in e else 0.0
        self.buyDate = e['buyDate'] if 'buyDate' in e else "Not Found"
        self.sellTicker = e['sellTicker'] if 'sellTicker' in e else 0
        self.sellShareNo = e['sellShareNo'] if 'sellShareNo' in e else 0
        self.sellPrice =  e['sellPrice'] if 'sellPrice' in e else 0.0
        self.shareReinvest = e['shareReinvest'] if 'shareReinvest' in e else 0
        self.reinvestAmount = e['reinvestAmount'] if 'reinvestAmount' in e else 0.0
        self.remainingShare = e['remainingShare'] if 'remainingShare' in e else 0
        self.netProfit = e['netProfit'] if 'netProfit' in e else 0.0
        self.realizedProfit = e['realizedProfit'] if 'realizedProfit' in e else 0.0



    def populateBasicShare(self, shareId , sharename ,shareCode ,shareExchange, boughtPrice , noOfShare , stopLoss , targetPrice , buydate ):
        self.shareId = shareId
        self.shareName = sharename
        self.shareExchange = shareExchange
        self.shareCode = shareCode
        self.boughtPrice = boughtPrice
        self.noOfShares = noOfShare
        self.stopLoss = stopLoss
        self.targetPrice = targetPrice
        self.buyDate = buydate
        
    def populateCalShare (self,sellTicker , sellShareNo , sellPrice , shareReinvest , reinvestAmount ,remainingShare, netProfit , realizedProfit):
        self.sellTicker = sellTicker
        self.sellShareNo = sellShareNo 
        self.sellPrice =  sellPrice
        self.shareReinvest = shareReinvest
        self.reinvestAmount = reinvestAmount
        self.remainingShare = remainingShare
        self.netProfit = netProfit
        self.realizedProfit = realizedProfit
