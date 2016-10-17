from django.shortcuts import render
from tenant_manage_plat.models import Tenant
from tenant_manage_plat.models import User
from tenant_manage_plat.models import Stadium
from tenant_manage_plat.models import UserStadium
from django.http import HttpRequest
from django.http import HttpResponse
from django.db import transaction
from django.core.exceptions import ObjectDoesNotExist
import json
import traceback
from util.tool import logger

# Create your views here.
'''
method:post
url:http://115.28.111.96/login/
request:
    {
        'name':'user@tenant',
        'passwd':xx
    }
response:
    {
        'error':0--success,1--invalid parameter,2--user not exist,3--password error
    }
'''
def login(request):
    result={'error':0}
    try:
        content = json.loads(request.body)
        logger.debug("login in: %s", content)
        
        if not (content.has_key('name') and content.has_key('passwd')):
            result['error'] = 1
            return HttpResponse(json.dumps(result,ensure_ascii=False))
        
        user_tenant = content['name'].split("@")
        user = None
        try:
            user = User.objects.get(name=user_tenant[0], tenant__name=user_tenant[1])
        except ObjectDoesNotExist:
            result['error'] = 2
            return HttpResponse(json.dumps(result,ensure_ascii=False))
        
        if user.check_passwd(content['passwd']):
            print user_tenant
            request.session['id'] = user.id
            request.session['user'] = user_tenant[0]
            request.session['tenant'] = user_tenant[1]
            return HttpResponse(json.dumps(result,ensure_ascii=False))
        else:
            print 'here'
            result['error'] = 3
            return HttpResponse(json.dumps(result,ensure_ascii=False))
    except Exception,e:
        result['error'] = -1
        logger.error("login error. \n%s", traceback.format_exc())
        return HttpResponse(json.dumps(result,ensure_ascii=False))

'''
method:post
url:http://115.28.111.96/user/add/
request:
    {
        'name':'user',
        'passwd':xx,
        'telephone':13917562774,
        'manage_stadiums':[id1,id2]
    }
response:
    {
        'error':0--success,1--invalid parameter
    }
'''
def add(request):
    result={'error':0}
    try:
        content = json.loads(request.body)
        if not (content.has_key('name') and content.has_key('passwd')):
            result['error'] = 1
            return HttpResponse(json.dumps(result,ensure_ascii=False))
        
        with transaction.atomic():
            user = User()
            user.name = content['name']
            user.passwd = content['passwd']
            if content.has_key('telephone'):
                user.telephone = content['telephone']
            user.tenant = Tenant.objects.get(id=1)
            user.save()
            
            user_stadiums = []
            if content.has_key('manage_stadiums'):
                for stadium_id in content['manage_stadiums']:
                    user_stadium = UserStadium()
                    user_stadium.user=user
                    user_stadium.stadium=Stadium.objects.get(id=stadium_id)
                    user_stadiums.append(user_stadium)
            UserStadium.objects.bulk_create(user_stadiums)
        return HttpResponse(json.dumps(result,ensure_ascii=False))
    except Exception,e:
        result['error'] = -1
        print traceback.format_exc()
        return HttpResponse(json.dumps(result,ensure_ascii=False))

'''
method:post
url:http://115.28.111.96/user/edit/
request:
    {
        'user_id':user_id,
        'name':'user',
        'passwd':xx,
        'telephone':13917562774,
        'manage_stadiums':[id1,id2]
    }
response:
    {
        'error':0--success,1--invalid parameter
    }
'''
def edit(request):
    result={'error':0}
    try:
        content = json.loads(request.body)
        if not content.has_key('user_id'):
            result['error'] = 1
            return HttpResponse(json.dumps(result,ensure_ascii=False))
        
        with transaction.atomic():
            user = User.objects.get(id=int(content['user_id']))
            if content.has_key('name'):         
                user.name = content['name']
            if content.has_key('passwd'): 
                user.passwd = content['passwd']
            if content.has_key('telephone'):
                user.telephone = content['telephone']
            user.save()
            
            user_stadiums = []
            if content.has_key('manage_stadiums'):
                UserStadium.objects.filter(user__id=int(content["user_id"])).delete()
                for stadium_id in content['manage_stadiums']:
                    user_stadium = UserStadium()
                    user_stadium.user=user
                    user_stadium.stadium=Stadium.objects.get(id=stadium_id)
                    user_stadiums.append(user_stadium)
            UserStadium.objects.bulk_create(user_stadiums)
        return HttpResponse(json.dumps(result,ensure_ascii=False))
    except Exception,e:
        result['error'] = -1
        print traceback.format_exc()
        return HttpResponse(json.dumps(result,ensure_ascii=False))

'''
method:post
url:http://115.28.111.96/user/delete/
request:
    {
        'user_ids':[1,2,3],
    }
response:
    {
        'error':0--success,1--invalid parameter
    }
'''
def delete(request):
    result={'error':0}
    try:
        content = json.loads(request.body)
        if not content.has_key('user_ids'):
            result['error'] = 1
            return HttpResponse(json.dumps(result,ensure_ascii=False))
        User.objects.filter(id__in=content['user_ids']).delete()
        return HttpResponse(json.dumps(result,ensure_ascii=False))
    except Exception,e:
        result['error'] = -1
        print traceback.format_exc()
        return HttpResponse(json.dumps(result,ensure_ascii=False))

'''
method:post
url:http://115.28.111.96/user/list/
request:
    {
        'stadium_id':3',//optional
    }
response:
    {
        'error':0--success,
        'users':[{
        'id':1,
        'name':'user',
        'telephone':13917562774,
        'manage_stadiums':{id1:"name1",id2:"name2"}
        }
        ]
    }
'''
def list(request):
    result={'error':0, 'users':[]}
    try:
        content = json.loads(request.body)
        user_name_to_info={}
        user_stadiums = []
        if content.has_key('stadium_id'):
            user_stadiums=UserStadium.objects.select_related().filter(stadium__id__exact=int(content['stadium_id']))
        else:
            user_stadiums=UserStadium.objects.select_related().filter(stadium__tenant_id__exact=1)
        for user_stadium in user_stadiums:
            if not user_name_to_info.has_key(user_stadium.user.id):
                user_name_to_info[user_stadium.user.id] = {'manage_stadiums':{}}
                user_name_to_info[user_stadium.user.id]['id'] = user_stadium.user.id
                user_name_to_info[user_stadium.user.id]['name'] = user_stadium.user.name
                user_name_to_info[user_stadium.user.id]['telephone'] = user_stadium.user.telephone
                user_name_to_info[user_stadium.user.id]['passwd'] = user_stadium.user.passwd
            if user_stadium.stadium != None:
                user_name_to_info[user_stadium.user.id]['manage_stadiums'][user_stadium.stadium.id] = user_stadium.stadium.name
        if not content.has_key('stadium_id'):
            users = User.objects.filter(tenant_id__exact=1).exclude(id__in=user_name_to_info.keys())
            for user in users:
                user_name_to_info[user.id] = {'manage_stadiums':{}}
                user_name_to_info[user.id]['id'] = user.id
                user_name_to_info[user.id]['name'] = user.name
                user_name_to_info[user.id]['telephone'] = user.telephone
                user_name_to_info[user.id]['passwd'] = user.passwd
        result['users']=user_name_to_info.values()
        return HttpResponse(json.dumps(result,ensure_ascii=False))
    except Exception,e:
        result['error'] = -1
        print traceback.format_exc()
        return HttpResponse(json.dumps(result,ensure_ascii=False))


def get_login_info(request):
    result={'error':0, 'login_info':{}}
    if request.session.has_key('id'):
        result['login_info']['id'] = request.session['id']
    else:
        result['error'] = 1
    if request.session.has_key('user'):
        result['login_info']['user'] = request.session['user']
    else:
        result['error'] = 1
    if request.session.has_key('tenant'):
        result['login_info']['tenant'] = request.session['tenant']
    else:
        result['error'] = 1
    return HttpResponse(json.dumps(result,ensure_ascii=False))

def login_out(request):
    if request.session.has_key('id'):
        del request.session['id']
    if request.session.has_key('user'):
        del request.session['user']
    if request.session.has_key('tenant'):
        del request.session['tenant']
    return HttpResponse(json.dumps({'error':0},ensure_ascii=False))    
