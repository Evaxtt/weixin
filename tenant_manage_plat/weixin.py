#coding:utf8
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.encoding import smart_str
import hashlib
from xml.etree import ElementTree as etree

import urllib2
import json

import time
from tenant_manage_plat.util import wx_pay_sdk, menu

from util.tool import logger
from util.tool import AccessTokenTool, WeixinUserTool

import localUser_manage

#测试环境
#appid = 'wx95198705de430c74' 
#secret = 'b032a7cc9a585f13075aa1d03cfacb02'
#accessUrl = "https://101.226.90.58/cgi-bin/token?grant_type=client_credential&appid=" + appid + "&secret=" + secret
#mch_id = '10057206'
#key = '00000000000000000000000000000000'

appid = "wx95198705de430c74"
secret = ""
accessUrl = ""
mch_id = "10057206"
key = "00000000000000000000000000000000"

#正式环境
#appid = 'wxe2199cc318a1f4db' 
#secret = 'e1452caab791a1f0f268e78294a6da7b'
#accessUrl = "https://101.226.90.58/cgi-bin/token?grant_type=client_credential&appid=" + appid + "&secret=" + secret
#mch_id = '1273376801'
#key = 'abcde123450000000000q1w2e3r4t5y6'
#check_online_kflist_url = 'https://101.226.90.58/cgi-bin/customservice/getonlinekflist?access_token='
#PicUrl = 'https://mmbiz.qlogo.cn/mmbiz/feFQGpxBYpjCdyBFqFJPHMnibLR8l437SRQvQ9OCh4VsshRHXeAVveubuQvfn6QIS5DEEVOnZU6gkpZo5lyFuwA/0?wx_fmt=png'

logger.warning("weixin.py has loaded.")

menuManager = menu.MenuManager()
accessTokenTool = AccessTokenTool()

access_token = accessTokenTool.getAccessToken()
menuManager.createMenu(access_token)

@csrf_exempt
def save_appid(request):
    logger.info("save appid in.")
    appid = request.GET["appid"]
    mch_id = request.GET["mch_id"]
    key = request.GET["key"]
    secret = request.GET["secret"]

    request.session['appid'] = appid
    request.session['mch_id'] = mch_id
    request.session['key'] = key
    request.session['secret'] = secret
    request.session.save()
    logger.info("session saved. appid=%s, mch_id=%s, key=%s, secret=%s"%(appid,mch_id,key,secret))
    return HttpResponse(json.dumps({'result':"ok"},ensure_ascii=False))


def weixin(request):
    if request.method=='GET':
        response=HttpResponse(checkSignature(request))
        return response

    xmlstr = smart_str(request.body)
    logger.debug(xmlstr)
    xml = etree.fromstring(xmlstr)
   
    ToUserName = xml.find('ToUserName').text
    FromUserName = xml.find('FromUserName').text
    CreateTime = xml.find('CreateTime').text
    MsgType = xml.find('MsgType').text
    
    try:
        MsgId = xml.find('MsgId').text
        Content = xml.find('Content').text
    except:
        MsgId = ''
        Content = ''
    
    try:
        Event = xml.find('Event').text
    except:
        Event = ""
        
    if Event == 'subscribe':
        reply_xml = reply_text(FromUserName,ToUserName,CreateTime, "欢迎您关注")
        localUser_manage.add(FromUserName)
        
        
    elif Event == 'unsubscribe':
        localUser_manage.delete(FromUserName)
        return HttpResponse()
        
    elif Content.encode("utf-8") == '帮助':
        reply_xml = reply_custom_help(FromUserName,ToUserName,CreateTime)        
    else:
        reply_xml = reply_text(FromUserName,ToUserName,CreateTime,"欢迎使用宝钢云盘微信服务号，如果需要帮助，请回复 “帮助” 将会有客服人员在线为您解答")
    return HttpResponse(reply_xml)

def checkSignature(request):
    signature=request.GET.get('signature',None)
    timestamp=request.GET.get('timestamp',None)
    nonce=request.GET.get('nonce',None)
    echostr=request.GET.get('echostr',None)
    token="uV1JizBxfPQQGv3MZd8bZdJnFHMk"    

    tmplist=[token,timestamp,nonce]
    tmplist.sort()
    tmpstr="%s%s%s"%tuple(tmplist)
    tmpstr=hashlib.sha1(tmpstr).hexdigest()
    if tmpstr==signature:
        return echostr
    else:
        return None


def post(url, data):  
    req = urllib2.Request(url)  
    #data = urllib.urlencode(data)  
    #enable cookie  
    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor())  
    response = opener.open(req, data)  
    return response.read()  

def get_openid_redirect(request):
    id = request.GET['id']
    sport_id = request.GET["sport_id"]
    #place_id = request.GET['place_id']
    day = request.GET['day']
    total_fee = request.GET['total_fee']
    order_detail = request.GET['order_detail']
    redirect_uri = 'http://www.dabooster.com/sport/reserve_middleware_wx.html?id=' + id + "&sport_id=" + sport_id + '&day=' + day + '&total_fee=' + total_fee + '&order_detail=' + order_detail
    appid = request.session["appid"]
    return HttpResponse(json.dumps({'redirect_uri':redirect_uri,'appid':appid, "id":id, "day":day, "total_fee":total_fee, "order_detail":order_detail},ensure_ascii=False))

def get_openid_redirect_query(request):
    redirect_uri = 'http://www.dabooster.com/sport/reserve_middleware_wx.html?query=yes'   
    appid = request.session["appid"]
    return HttpResponse(json.dumps({'redirect_uri':redirect_uri,'appid':appid},ensure_ascii=False))

def get_openid(request):
    
    code = request.GET.get('code')
    logger.debug("get open_id, code = %s", code)
    weixinUser = WeixinUserTool(code)
    openid = weixinUser.getOpenid()
    logger.debug("get openid result: %s", openid)
    return HttpResponse(json.dumps({'openid':openid},ensure_ascii=False))
    
    
    try:
        code = request.GET['code']
        openid = ""
        appid = request.session["appid"]
        secret = request.session["secret"]
        url = "https://api.weixin.qq.com/sns/oauth2/access_token?appid=" + appid + "&secret=" + secret + "&code=" + code + "&grant_type=authorization_code"
        result = post(url, '')
        
        result = json.loads(result)
        openid = result['openid']
        logger.debug("get openid = "+openid)
        
    except Exception,e:
        logger.error(e)

    return HttpResponse(json.dumps({'openid':openid},ensure_ascii=False))
    
def get_prepay_id(request):
    new_path_filename = '/home/text.txt'
    f = open(new_path_filename, 'a')
    f.writelines('start\r\n')
    
    logger.warning("prepay start")
    
    pay_url = 'https://api.mch.weixin.qq.com/pay/unifiedorder'
    
    
    nonce_str = wx_pay_sdk.Common_util_pub().createNoncestr()
    body = '悦享源场馆预定'
    
    new_path_filename = '/home/text.txt'
    f = open(new_path_filename, 'a')
    f.writelines('body:' + body)
    
    out_trade_no = request.GET['num']
    
    f.writelines('out_trade_no:' + out_trade_no)
    
    
    total_fee = request.GET['total_fee']
    
    f.writelines('total_fee:' + total_fee)
    
    
    spbill_create_ip = request.META['REMOTE_ADDR']  
    
    f.writelines('spbill_create_ip:' + spbill_create_ip)
    notify_url = 'http://115.28.111.96/wx/get_wx_pay_notify'
    trade_type = 'JSAPI'
    #openid = 'oawF8jjPjmMzuth315_7teoBsZyI'
    openid = request.GET['openid']
    #appid = request.session["appid"]
    #mch_id = request.session["mch_id"]
    para = {}
    para['appid'] = appid
    para['body'] = body
    para['spbill_create_ip'] = spbill_create_ip
    para['mch_id'] = mch_id
    para['nonce_str'] = nonce_str
    para['notify_url'] = notify_url
    para['openid'] = openid
    para['out_trade_no'] = out_trade_no
    para['total_fee'] = total_fee
    para['trade_type'] = trade_type

    #new
    para["key"] = key#request.session["key"]
    
    logger.debug("prepay para: %s", para)
    #para = 'appid=%s&body=%s&ip=%s&mch_id=%s&nonce_str=%s&notify_url=%s&openid=%s&out_trade_no=%s&total_fee=%s&trade_type=%s' % (appid,body,ip,mch_id,nonce_str,notify_url,openid,out_trade_no,total_fee,trade_type)
    #sign = 'appid=%s&body=%s&mch_id=%s&nonce_str=%s&notify_url=%s&openid=%s&out_trade_no=%s&spbill_create_ip=%s&total_fee=%s&trade_type=%s&key=%s' % (appid,body,mch_id,nonce_str,notify_url,openid,out_trade_no,spbill_create_ip,total_fee,trade_type,key)
    #sign = hashlib.md5(sign).hexdigest().upper()
    
    sign_new =  wx_pay_sdk.Common_util_pub().getSign(para)
    
#     new_path_filename = '/home/text.txt'
#     f = open(new_path_filename, 'a')
#     #f.writelines(sign)
#     f.writelines(sign_new)
    para['sign'] = sign_new
    logger.debug("prepay sign = %s", sign_new)
    
    data = wx_pay_sdk.Common_util_pub().arrayToXml(para)
    result = post(pay_url, data)  
    #result = wx_pay_sdk.Common_util_pub().xmlToArray(result)
    #prepay_id =result['prepay_id']
    new_path_filename = '/home/text.txt'
    f = open(new_path_filename, 'a')
    f.writelines(result)
    logger.debug("prepay result: %s", result)
    
    result = wx_pay_sdk.Common_util_pub().xmlToArray(result)
    return_msg = result['return_msg']
    prepay_id = ''
    if return_msg == 'OK':
        prepay_id = result['prepay_id']
    
    new_path_filename = '/home/text.txt'
    f = open(new_path_filename, 'a')
    f.writelines('prepay_id:' + prepay_id + '\r\n')
    
    
    #jsonT = json.loads(result)
   
    return HttpResponse(json.dumps({'result':return_msg,'prepay_id':prepay_id},ensure_ascii=False))

def start_pay(request):
    logger.warning("start pay")
    prepay_id = request.GET['prepay_id']
    #appid = request.session["appid"]
    para = {}
    para['appId'] = appid
    para['timeStamp'] = int(time.time())
    para['nonceStr'] = wx_pay_sdk.Common_util_pub().createNoncestr()
    para['package'] = 'prepay_id=' + prepay_id
    para['signType'] = "MD5"
    para["key"] = key#request.session["key"]
    logger.debug("start pay para: %s", para)
    para['paySign'] = wx_pay_sdk.Common_util_pub().getSign(para)
    logger.debug("start pay result: %s", para['paySign'])
    return HttpResponse(json.dumps(para,ensure_ascii=False))

def get_wx_pay_notify(request):
    xmlstr = smart_str(request.body)
    xml = etree.fromstring(xmlstr)
    return_code = xml.find('return_code').text
    
    
    new_path_filename = '/home/text.txt'
    f = open(new_path_filename, 'a')
    msg = "return_code" + return_code
    
    
    
    if return_code == "SUCCESS":
        result_code = xml.find('result_code').text
        msg += " result_code:" + result_code
        if return_code == "SUCCESS":
            bank_type = xml.find('bank_type').text
            total_fee = xml.find("total_fee").text
            transaction_id = xml.find("transaction_id").text
            out_trade_no = xml.find("out_trade_no").text
            time_end = xml.find("time_end").text
            msg += " bank_type:" + bank_type
            msg += " total_fee:" + total_fee
            msg += " transaction_id:" + transaction_id
            msg += " out_trade_no:" + out_trade_no
            msg += " time_end:" + time_end
            f.writelines(msg)
            #do sth
        else:
            err_code = xml.find("err_code").text
            err_code_des = xml.find("err_code_des").text
    else:
        return_msg = xml.find("return_msg").text
    return HttpResponse(reply_pay_notify())
        
    
    
def reply_text(FromUserName,ToUserName,CreateTime,Content):
    reply_xml = """<xml>
           <ToUserName><![CDATA[%s]]></ToUserName>
           <FromUserName><![CDATA[%s]]></FromUserName>
           <CreateTime>%s</CreateTime>
           <MsgType><![CDATA[text]]></MsgType>
           <Content><![CDATA[%s]]></Content>
           </xml>"""%(FromUserName,ToUserName,CreateTime, Content)
    return reply_xml

def reply_custom_help(FromUserName,ToUserName,CreateTime):
    reply_xml = """<xml>
           <ToUserName><![CDATA[%s]]></ToUserName>
           <FromUserName><![CDATA[%s]]></FromUserName>
           <CreateTime>%s</CreateTime>
           <MsgType><![CDATA[transfer_customer_service]]></MsgType>
           </xml>"""%(FromUserName,ToUserName,CreateTime)
    return reply_xml

def reply_pay_notify():
    reply_xml = """<xml>
           <return_code><![CDATA[%s]]></return_code>
           <return_msg></return_msg>
           </xml>"""%('SUCCESS')
    return reply_xml



#################################################################
#chen xi 
#2016.9
#################################################################
'''
method:get
url:/wx/getUserInfo
request:
    {
    'code': get new weixin user info.
    None: get session weixin user info.
    }
response:
    {
    'error' = 0--sucess, -1--internal error, 1 --param error,
    'userInfo' = {
                
                }
    }
'''
def getUserInfo(request):
    result = {"error" : 0}
    if not request.GET.has_key('code'):
        if not request.session.has_key('weixinUser'):
            result['error'] = 1
            return HttpResponse(json.dumps(result,ensure_ascii=False))
        result['userInfo'] = request.session['weixinUser']
        return HttpResponse(json.dumps(result,ensure_ascii=False))
    
    code = request.GET.get('code')
    weixinUser = WeixinUserTool(code)
    info = weixinUser.getWeixinUser(accessTokenTool.getAccessToken())
    getlocaluser = localUser_manage.get(info['openid'])
    if getlocaluser['error'] == 0 :
        localuser = getlocaluser['weixinUser']
        info['avatar'] = localuser['avatar']
        info['balance'] = localuser['balance']
        info['credits'] = localuser['credits']
        info['name'] = localuser['name']
    result['userInfo'] = info
    request.session['weixinUser'] = info
    return HttpResponse(json.dumps(result,ensure_ascii=False))
    
    
def deleteUser(request):
    return

def editUser(request):
    return  
    





    
