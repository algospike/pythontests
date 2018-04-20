'''
Created on Apr 13, 2018

@author: C-Arpanjeet.Sandhu
'''

class Share:
    shareId = ""
    shareName = ""
    shareCode = ""
    shareExchange = ""
    boughtPrice = ""
    noOfShares = ""
    stopLoss = ""
    targetPrice = ""
    buyDate = ""
    remainingShare = ""
    sellTicker = ""
    sellShareNo = ""
    sellPrice = ""
    shareReinvest = ""
    reinvestAmount = ""
    netProfit = ""
    realizedProfit = ""
    
    
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
