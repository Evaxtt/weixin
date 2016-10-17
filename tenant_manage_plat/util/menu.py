# encoding:utf8

import urllib2
import json
import sys
from tool import logger

reload(sys)

sys.setdefaultencoding('utf8')# important
 
appid = 'wx95198705de430c74' 
secret = 'b032a7cc9a585f13075aa1d03cfacb02'

class MenuManager:
    accessUrl = "https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid=" + appid + "&secret=" + secret
    delMenuUrl = "https://api.weixin.qq.com/cgi-bin/menu/delete?access_token="
    createUrl = "https://api.weixin.qq.com/cgi-bin/menu/create?access_token="
    getMenuUri="https://api.weixin.qq.com/cgi-bin/menu/get?access_token="
    def getAccessToken(self):
        f = urllib2.urlopen(self.accessUrl)
        accessT = f.read().decode("utf-8")
        jsonT = json.loads(accessT)
        return jsonT["access_token"]
    def delMenu(self, accessToken):
        html = urllib2.urlopen(self.delMenuUrl + accessToken)
        result = json.loads(html.read().decode("utf-8"))
        return result["errcode"]
    def createMenu(self, accessToken):
        logger.info("createMenu in...........")
        redirect_uri1 = 'http://www.dabooster.com/sport/reserve_middleware_wx.html?query=yes'
        redirect_uri2 = 'http://www.dabooster.com/sport/reserve_middleware_wx.html?query=no'
        redirect_uri3 = 'http://www.dabooster.com/sport/personal_center_wx.html'
        url1 = "https://open.weixin.qq.com/connect/oauth2/authorize?appid=" + appid + "&redirect_uri=" + redirect_uri1 + "&response_type=code&scope=snsapi_base&state=OK#wechat_redirect" 
        url2 = "https://open.weixin.qq.com/connect/oauth2/authorize?appid=" + appid + "&redirect_uri=" + redirect_uri2 + "&response_type=code&scope=snsapi_base&state=OK#wechat_redirect" 
        url3 = "https://open.weixin.qq.com/connect/oauth2/authorize?appid=" + appid + "&redirect_uri=" + redirect_uri3 + "&response_type=code&scope=snsapi_base&state=OK#wechat_redirect"
        menu = '''{
                 "button":[
                     { 
                         "name":"在线预定",
                         "sub_button":[
                              {"type":"view",
                              "name":"场地预定",
                              "url":"http://www.dabooster.com/sport/reserve_wx.html?appid=wx95198705de430c74"},
                               {"type":"view",
                              "name":"我的订单",
                              "url":"%s"}                              
                         ]
                    },
                    {
                          "type":"view",
                          "name":"活动",
                          "url":"%s"
                    },
                     { 
                          "type":"view",
                          "name":"个人中心",
                          "url":"%s"
                    }
                         
                    }
                ]}'''%(url1,url2,url3)
        html = urllib2.urlopen(self.createUrl + accessToken, menu.encode("utf-8"))
        result = json.loads(html.read().decode("utf-8"))
        
        logger.info("html=" + str(result))
        
        return result["errcode"]
    def getMenu(self, accessToken):
        html = urllib2.urlopen(self.getMenuUri + accessToken)
        print(html.read().decode("utf-8"))
     