from tenant_manage_plat.models import Customer
from django.http import HttpRequest
from django.http import HttpResponse
from django.core.exceptions import ObjectDoesNotExist
from django.db import IntegrityError
import json

'''
method:post
url:http://115.28.240.2:8080/customer/add
request:
    {
        'name':xx,
        'contact':xx,
        'cellphone':xx,
        'address':xx,
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
        if not (content.has_key('name') and content.has_key('contact') and content.has_key('cellphone')):
            result['error'] = 1
            return HttpResponse(json.dumps(result,ensure_ascii=False))
        try:
            customer = Customer()
            customer.name=content['name']
            customer.contact=content['contact']
            customer.cellphone=content['cellphone']
            if content.has_key('address'):
                customer.address=content['address']
            customer.save()
            result['id'] = customer.id
            return HttpResponse(json.dumps(result,ensure_ascii=False))
        except IntegrityError,e:
            result['error'] = 4
            return HttpResponse(json.dumps(result,ensure_ascii=False))    
    except Exception,e:
        result['error'] = -1
        print e
        return HttpResponse(json.dumps(result,ensure_ascii=False))
    
'''
method:post
url:http://115.28.240.2:8080/customer/delete
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
        
        Customer.objects.filter(id__in=content['ids']).delete()
        return HttpResponse(json.dumps(result,ensure_ascii=False))
    except Exception,e:
        result['error'] = -1
        return HttpResponse(json.dumps(result,ensure_ascii=False))

'''
method:post
url:http://115.28.240.2:8080/customer/edit
request:
    {
        'id':xx,
        'name':xx,
        'contact':xx,
        'cellphone':xx,
        'address':xx,
    }
response:
    {
        'error':0--success,-1--internal error,1--invalid-parameter,2--custome not exist
    } 
'''  
def edit(request):
    result={'error':0}
    try:
        content = json.loads(request.body)
        if not content.has_key('id'):
            result['error'] = 1
            return HttpResponse(json.dumps(result,ensure_ascii=False))
        
        try: 
            customer = Customer.objects.get(id=content['id'])
            if content.has_key('name'):
                customer.name = content['name']
            if content.has_key('contact'):
                customer.contact = content['contact']
            if content.has_key('cellphone'):
                customer.cellphone = content['cellphone']
            if content.has_key('address'):
                customer.address = content['address']
            customer.save()
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
url:http://115.28.240.2:8080/customer/list
response:
    {
        'error':0--success,
        'customers':[
            {
                'id':xx,
                'name':xx,
                'contact':xx,
                'cellphone':xx,
                'address':xx,
            }
        ]
    }
'''    
def list(request):
    result={'error':0}
    result['customers'] = []
    try:
        customers = Customer.objects.all()
        for customer in customers:
           result['customers'].append(customer.get_customer_info()) 
        return HttpResponse(json.dumps(result,ensure_ascii=False))
    except Exception,e:
        print e
        result['error'] = -1
        return HttpResponse(json.dumps(result,ensure_ascii=False))
    
        