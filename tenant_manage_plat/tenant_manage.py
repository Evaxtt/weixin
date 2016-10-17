from tenant_manage_plat.models import Tenant
from django.http import HttpRequest
from django.http import HttpResponse
from django.core.exceptions import ObjectDoesNotExist
from django.db import IntegrityError
import json

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
        if not (content.has_key('name') and content.has_key('appid') ):
            result['error'] = 1
            return HttpResponse(json.dumps(result,ensure_ascii=False))
        try:
            tenant = Tenant()
            tenant.name=content['name']
            tenant.appid = content['appid']
            if content.has_key('contact'):
                tenant.contact = content['contact']
            if content.has_key('cellphone'):
                tenant.cellphone = content['cellphone']
            if content.has_key('address'):
                tenant.address = content['address']
            if content.has_key('secret'):
                tenant.secret = content['secret']
            if content.has_key('mch_id'):
                tenant.mch_id = content['mch_id']
            if content.has_key('key'):
                tenant.key = content['key']
            tenant.save()
            result['id'] = tenant.id
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
        if not (content.has_key('ids')):
            result['error'] = 1
            return HttpResponse(json.dumps(result,ensure_ascii=False))
        
        Tenant.objects.filter(id__in=content['ids']).delete()
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
        if not content.has_key('id'):
            result['error'] = 1
        
        try: 
            tenant = Tenant.objects.get(id=content['id'])
            if content.has_key('name'):
                tenant.name=content['name']
            if content.has_key('appid'):
                tenant.appid = content['appid']
            if content.has_key('contact'):
                tenant.contact = content['contact']
            if content.has_key('cellphone'):
                tenant.cellphone = content['cellphone']
            if content.has_key('address'):
                tenant.address = content['address']
            if content.has_key('secret'):
                tenant.secret = content['secret']
            if content.has_key('mch_id'):
                tenant.mch_id = content['mch_id']
            if content.has_key('key'):
                tenant.key = content['key']
            tenant.save()
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
    result={'error':0}
    result['tenants'] = []
    try:
        tenants = Tenant.objects.all()
        for tenant in tenants:
           result['tenants'].append(tenant.get_tenant()) 
        return HttpResponse(json.dumps(result,ensure_ascii=False))
    except Exception,e:
        result['error'] = -1
        return HttpResponse(json.dumps(result,ensure_ascii=False))

'''
method:post
url:http://115.28.240.2:8080/tenant/detail
request:
{
    'tenant_id':,
    'appid':
}
response:
    {
        'error':0,
        'tenant':
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
        }
    }
'''    
def detail(request):
    result={'error':0}
    try:
        content = json.loads(request.body)
        filter_condition = {}
        if content.has_key('tenant_id'):
            filter_condition['id__exact'] = int(content['tenant_id'])
        if content.has_key('appid'):
            filter_condition['appid__exact'] = content['appid']
        #xtt
        # if content.has_key('mch_id'):
        #     filter_condition['mch_id'] = content['mch_id']

        tenants = Tenant.objects.filter(**filter_condition)
        for tenant in tenants:
           result['tenant']=tenant.get_tenant()
        return HttpResponse(json.dumps(result,ensure_ascii=False))
    except Exception,e:
        result['error'] = -1
        print e
        return HttpResponse(json.dumps(result,ensure_ascii=False))    