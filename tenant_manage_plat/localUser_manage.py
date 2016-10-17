#coding:utf8
'''
Created on 2016年9月26日

@author: Chen xi
'''

from models import WeixinUser
from util.tool import logger
from django.core.exceptions import ObjectDoesNotExist

def add(openid):
    try:
        weixinUser = WeixinUser()
        weixinUser.openid = openid
        weixinUser.name = openid
        weixinUser.save()
        logger.debug('added local info, openid = '+openid)
        return 0
    except Exception,e:
        logger.error('add local info error, openid = %s. \n%s', openid, e)
        return -1

def delete(openid):
    try:
        WeixinUser.objects.get(openid=openid).delete()
        return 0
    except Exception,e:
        logger.error("delete weixin user error, openid = %s. \n%s", openid, e)
        return -1


def edit(localInfo):
    logger.debug('edit local info: %s', localInfo)              
    try: 
        weixinUser = WeixinUser.objects.get(openid=localInfo['openid'])
        if localInfo.has_key('name'):
            weixinUser.name = localInfo['name']
        if localInfo.has_key('avatar'):
            weixinUser.contact = localInfo['avatar']
        if localInfo.has_key('balance'):
            weixinUser.cellphone = localInfo['balance']
        if localInfo.has_key('credits'):
            weixinUser.address = localInfo['credits']
        if localInfo.has_key('phone'):
            weixinUser.address = localInfo['phone']
        weixinUser.save()
        return 0
    except ObjectDoesNotExist:
        logger.error("edit local info fail. obj does not exist.")
        return 2
    except Exception,e:
        logger.error("edit local info error.\n%s", e)
        return -1


def get(openid):
    result={'error':0}
    try:
        logger.info("get local user, openid = " + openid)
        user = WeixinUser.objects.get(openid=openid).get_weixin_user()
        logger.info("get local user, user = %s", user)
        result['weixinUser'] = user
    except Exception,e:
        logger.error("get local user info error, %s", e)
        result['error'] = -1
    return result
    


