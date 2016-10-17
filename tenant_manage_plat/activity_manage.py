#coding:utf8
from tenant_manage_plat.models import Sport
from django.http import HttpRequest
from django.http import HttpResponse
from tenant_manage_plat.models import Activity
from tenant_manage_plat.models import ActivityApplicant
from tenant_manage_plat.models import ActivityForm
from django.core.exceptions import ObjectDoesNotExist
import json
import traceback
import django.utils.timezone
from django.utils.timezone import utc
from sport import log
import django.utils.timezone
from django.utils.timezone import utc
from util.tool import logger

def add(request):
    result= {'error':0}
    try:
        form = ActivityForm(request.POST,request.FILES)
        form.save()
        return HttpResponse(json.dumps(result,ensure_ascii=False))
    except Exception,e:
        log.exception(e)
        result['error'] = -1
        return HttpResponse(json.dumps(result,ensure_ascii=False))

'''
url:http://115.28.111.96/activity/list/
method:post
request:
    {
        'publish':0// 0 or 1
    }
response:
    {
        'error':0,--success
        'activity_list':{
            'id':,
            'stadium_name':,
            'price':,
            'start_time':,
            'end_time':,
            'title':,
            'content':,
            'attendant_count':100,
            'registered_count':100,
        }
    }
'''
def list(request):
    result= {'error':0,'activity_list':[]}
    try:
        filter_condition = {"stadium__tenant__id__exact":1}
        if len(request.body) != 0:   
            content = json.loads(request.body)
            if content.has_key('publish'):
                filter_condition["publish__exact"] = int(content["publish"])
            if content.has_key('id'):
                filter_condition["id__exact"] = int(content["id"])
        activities=Activity.objects.filter(**filter_condition)
        for activity in activities:
            result['activity_list'].append(activity.get_detail_info())
            
        return HttpResponse(json.dumps(result,ensure_ascii=False))
    except Exception,e:
        log.exception(e)
        result['error'] = -1
        return HttpResponse(json.dumps(result,ensure_ascii=False))

'''
url:http://115.28.111.96/activity/wx_list/
method:post
request:
    {
        'custormer_id'://tanant wx id
    }
response:
    {
        'error':0,--success
        'activity_list':{
            'id':,
            'wx_title':,
            'img':
        }
    }
'''
def wx_list(request):
    result= {'error':0,'activity_list':[]}
    try:
        filter_condition = {}
        if len(request.body) != 0:   
            content = json.loads(request.body)
            if content.has_key('customer_id'):
                filter_condition["stadium__tenant__customer_id__exact"] = content["customer_id"]
        activities=Activity.objects.filter(**filter_condition)
        for activity in activities:
            activity_info = {}
            activity_info['id'] = activity.id
            activity_info['wx_title'] = activity.wx_title
            activity_info['img'] = activity.img.url
            result['activity_list'].append(activity_info)
            
        return HttpResponse(json.dumps(result,ensure_ascii=False))
    except Exception,e:
        log.exception(e)
        result['error'] = -1
        return HttpResponse(json.dumps(result,ensure_ascii=False))

'''
url:http://115.28.111.96/activity/wx_detail/
method:post
request:
    {
        'activity_id'://acitivity id
    }
response:
    {
        'error':0,--success
        'activity_detail':{
            'id':,
            'stadium_name':,
            'price':,
            'start_time':,
            'end_time':,
            'title':,
            'content':,
            'attendant_count':100,
            'registered_count':100,
            'img':
        }
    }
'''
def wx_detail(request):
    result= {'error':0,'activity_detail':[]}
    try:
        filter_condition = {}
        content = json.loads(request.body)
        if not content.has_key('activity_id'):
            result['error'] = 1
            return HttpResponse(json.dumps(result,ensure_ascii=False))

        activity=Activity.objects.get(id=int(content['activity_id']))
        result['activity_detail'] = activity.get_detail_info()
            
        return HttpResponse(json.dumps(result,ensure_ascii=False))
    except Exception,e:
        log.exception(e)
        result['error'] = -1
        return HttpResponse(json.dumps(result,ensure_ascii=False))


'''
url:http://115.28.111.96/activity/applicant_list/
method:post
request:
{
    'activity_id':
}
response:
{
    'error':0,--success
    'applicant':{
    'id':,
    'activity_id':,
    'name':,
    'telephone':,
    'checked':,
    'is_payed':,
    'apply_name':
    }
}
'''
def applicant_list (request):
    result= {'error':0,'applicants':[]}
    try:
        content = json.loads(request.body)
        logger.warning("get applicants: %s", content)
        filter_condition = {}
        if content.has_key('openid'):
            filter_condition['openid__exact'] = content['openid']
            # result['error'] = 1
            # return HttpResponse(json.dumps(result,ensure_ascii=False))
        if content.has_key('activity_id'):
            filter_condition['activity_id__exact'] = content['activity_id']

        activity_applicants=ActivityApplicant.objects.filter(**filter_condition)
        logger.debug("activity_applicants=%s",activity_applicants)
        for  activity_applicant in activity_applicants:
            result['applicants'].append(activity_applicant.get_applicant())
        logger.info("activity result: %s", result) 
        return HttpResponse(json.dumps(result,ensure_ascii=False))
    except Exception,e:
        log.exception(e)
        result['error'] = -1
        return HttpResponse(json.dumps(result,ensure_ascii=False))

'''
url:http://115.28.111.96/activity/apply/
method:post
request:
{
    'activity_id':,
    'name':'',
    'telephone':,
} 
response:
{
    'error':0,--success
    'apply_id':apply id//this id for pay
}
'''
def apply (request):
    result= {'error':0}
    try:
        content = json.loads(request.body)
        if not (content.has_key('activity_id') and content.has_key('name') and content.has_key('telephone')):
            result['error'] = 1
            return HttpResponse(json.dumps(result,ensure_ascii=False))

        activity_applicant=ActivityApplicant()
        activity_applicant.activity = Activity.objects.get(id=int(content['activity_id']))
        activity_applicant.name = content['name']
        activity_applicant.telephone = content['telephone']
        activity_applicant.save()
        result['apply_id'] =  activity_applicant.id   
        return HttpResponse(json.dumps(result,ensure_ascii=False))
    except Exception,e:
        log.exception(e)
        result['error'] = -1
        return HttpResponse(json.dumps(result,ensure_ascii=False))

'''
url:http://115.28.111.96/activity/pay/
method:post
request:
{
    'apply_id':,
    'openid':,
    'prepay_id':,
    'number':
    'money':,
} 
response:
{
    'error':0,--success
}
'''
def pay (request):
    result= {'error':0}
    try:
        content = json.loads(request.body)
        logger.warning("activity pay in: %s", content)
        if not (content.has_key('apply_id') and content.has_key('openid') and content.has_key('prepay_id') and content.has_key('number')):
            result['error'] = 1
            return HttpResponse(json.dumps(result,ensure_ascii=False))

        activity_applicant=ActivityApplicant.objects.get(id=int(content['apply_id']))
        activity_applicant.openid = content['openid']
        activity_applicant.prepay_id = content['prepay_id']
        activity_applicant.number = content['number']
        activity_applicant.is_payed=True
        activity_applicant.save()
            
        return HttpResponse(json.dumps(result,ensure_ascii=False))
    except Exception,e:
        log.exception(e)
        result['error'] = -1
        return HttpResponse(json.dumps(result,ensure_ascii=False))