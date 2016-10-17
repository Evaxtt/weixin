#coding:utf8
'''
Created on 2016.9.27

@author: Sirius Chen
'''

import urllib2
import json
import time
import logging


logging.basicConfig(level=logging.DEBUG,
                    format='[%(asctime)s] [%(filename)s] [line:%(lineno)d] [%(levelname)s] %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S',
                    filename='D:/weixin.txt',
                    filemode='a')
logger = logging.getLogger("LOGGER")

appid = 'wx95198705de430c74' 
secret = 'b032a7cc9a585f13075aa1d03cfacb02'

class AccessTokenTool:
    accessUrl = "https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid=" + appid + "&secret=" + secret
    access_token = ''
    expires_in = 0
    token_time = 0
    
#     def __init__(self):
#         logger.debug("init access token...")
#         f = urllib2.urlopen(self.accessUrl)
#         accessToken = f.read().decode("utf-8")
#         jsonToken = json.loads(accessToken)
#         if not jsonToken.has_key('access_token'):
#             logger.error("get access token fail. " + accessToken)
#             return
#         self.token_time = time.time()
#         self.expires_in = jsonToken['expires_in']
#         self.access_token = jsonToken['access_token']
#         return
        
        
    def getAccessToken(self):
        logger.debug('getAccessToken in')
        if time.time() - self.token_time >=  self.expires_in - 60:
            f = urllib2.urlopen(self.accessUrl)
            accessToken = f.read().decode("utf-8")
            jsonToken = json.loads(accessToken)
            if not jsonToken.has_key('access_token'):
                logger.error("get access token fail. " + accessToken)
                return 'fail', jsonToken['errmsg']
            self.token_time = time.time()
            self.expires_in = jsonToken['expires_in']
            self.access_token = jsonToken['access_token']
        logger.debug("get token: " + self.access_token)
        return self.access_token
    
    
class WeixinUserTool:
    openidUrl = "https://api.weixin.qq.com/sns/oauth2/access_token?appid=" + appid + "&secret=" + secret + "&code=%s&grant_type=authorization_code"
    
    userUrl = 'https://api.weixin.qq.com/cgi-bin/user/info?access_token=%s&openid=%s&lang=zh_CN'
    
    def __init__(self, code):
        logger.debug("init weixin user, code=" + code)
        self.code = code
        try:
            f = urllib2.urlopen(self.openidUrl % code)
            obj = f.read().decode("utf-8")
            jsonRes = json.loads(obj)
            logger.info("get openid response: %s", jsonRes)
            self.access_token = jsonRes['access_token']
            self.openid = jsonRes['openid']
            self.expires_in = jsonRes['expires_in']
            self.refresh_token = jsonRes['refresh_token']
            self.scope = jsonRes['scope']
        except Exception,e:
            logger.error("init weixin failed. %s", e)
    
    def getOpenid(self):
        return self.openid
    
    def getWeixinUser(self, global_access_token):
        logger.debug("get weixin user info in.")
        try:
            f = urllib2.urlopen(self.userUrl % (global_access_token, self.openid))
            obj = f.read().decode("utf-8")
            jsonRes = json.loads(obj)
            logger.info("get weixin user response: %s", jsonRes)
            return jsonRes
        except Exception,e:
            logger.error("get weixin user failed. %s", e)
            return ''





