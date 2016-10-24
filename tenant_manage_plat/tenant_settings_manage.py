from tenant_manage_plat.models import TenantSettings
from django.http import HttpRequest
from django.http import HttpResponse
from django.core.exceptions import ObjectDoesNotExist
from django.db import IntegrityError
import json
from util.tool import logger

'''
method:post
url:http://115.28.240.2:8080/tenant/add
request:
    {
        'name':xx,
        'appid':xx,
        'contact':xx,
        'cellphone':xx,
        'address':xx,
        'secret':xx,
        'mch_id':xx,
        'key':xx,
    }
response:
    {
        'error':0--success,-1--internal error,1--invalid-parameter,4--name duplicated
    }
'''
def add(request):
    result={'error':0}
    try:
        content = json.loads(request.body)
        if not (content.has_key('name') and content.has_key('value') ):
            result['error'] = 1
            return HttpResponse(json.dumps(result,ensure_ascii=False))
        try:
            tenant = TenantSettings()
            tenant.settingName=content['name']
            tenant.settingValue = content['value']
            tenant.save()
            return HttpResponse(json.dumps(result,ensure_ascii=False))
        except IntegrityError,e:
            print e
            result['error'] = 4
            return HttpResponse(json.dumps(result,ensure_ascii=False))    
    except Exception,e:
        result['error'] = -1
        return HttpResponse(json.dumps(result,ensure_ascii=False))
    
'''
method:post
url:http://115.28.240.2:8080/tenant/delete
request:
    {
        'ids':[
        id1,
        id2,
        ]
    }
response:
    {
        'error':0--success,-1--internal error,1--invalid-parameter
    }
'''
def delete(request):
    result={'error':0}
    try:
        content = json.loads(request.body)
        if not (content.has_key('name')):
            result['error'] = 1
            return HttpResponse(json.dumps(result,ensure_ascii=False))
        
        TenantSettings.objects.filter(settingName=content['name']).delete()
        return HttpResponse(json.dumps(result,ensure_ascii=False))
    except Exception,e:
        result['error'] = -1
        return HttpResponse(json.dumps(result,ensure_ascii=False))

'''
method:post
url:http://115.28.240.2:8080/tenant/edit
request:
    {
        'id':xx,
        'name':xx,
        'contact':xx,
        'cellphone':xx,
        'address':xx,
        'secret':xx,
        'mch_id':xx,
        'key':xx,
        'appid':xx,
    }
response:
    {
        'error':0--success,-1--internal error,1--invalid-parameter,2--tenant not exist
    } 
'''  
def edit(request):
    result={'error':0}
    try:
        content = json.loads(request.body)
        if not (content.has_key('name') and content.has_key('value') ):
            result['error'] = 1
            return HttpResponse(json.dumps(result,ensure_ascii=False))
        
        try: 
            tenantSettings = TenantSettings.objects.get(settingName=content['name'])
            tenantSettings.settingValue = content['value']
            tenantSettings.save()
            return HttpResponse(json.dumps(result,ensure_ascii=False))
        except ObjectDoesNotExist:
            result['error'] = 2
            return HttpResponse(json.dumps(result,ensure_ascii=False))
    except Exception,e:
        print e
        result['error'] = -1
        return HttpResponse(json.dumps(result,ensure_ascii=False))

'''
method:get
url:http://115.28.240.2:8080/tenant/list
response:
    {
        'error':0,
        'tenants':[
        {
            'id':xx,
            'name':xx,
            'appid':xx,
            'contact':xx,
            'cellphone':xx,
            'address':xx,
            'secret':xx,
            'mch_id':xx,
            'key':xx,
            'appid':xx,
        }
        ]
    }
'''    
def list(request):
    result={'error':0, 'value':''}
    try:
        content = json.loads(request.body)
        if not content.has_key('name'):
            result['error'] = 1
            return HttpResponse(json.dumps(result,ensure_ascii=False))

        tenantSettings = TenantSettings.objects.get(settingName=content['name'])
        result['value'] = tenantSettings.get_tenant_setting()

        return HttpResponse(json.dumps(result,ensure_ascii=False))
    except Exception,e:
        result['error'] = -1
        return HttpResponse(json.dumps(result,ensure_ascii=False))

