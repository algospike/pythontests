'''
Created on Apr 17, 2018

@author: C-Arpanjeet.Sandhu
'''
from Domains.ShareCal  import ShareCall
class ShareInfo:
    shareName = ""
    shareCode = ""
    shareExchange = ""
    ShareCall = ""
    def populateShareInfo(self , shareName , shareCode , shareExchange , shareCall):
        self.shareName = shareName
        self.shareCode = shareCode
        self.shareExchange = shareExchange
        self.ShareCall = shareCall