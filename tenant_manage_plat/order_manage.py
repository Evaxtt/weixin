#coding:utf8
from tenant_manage_plat.models import Stadium
from tenant_manage_plat.models import Order
from tenant_manage_plat.models import HistoryOrder
from tenant_manage_plat.models import Place
from tenant_manage_plat.models import PlaceOrder
from tenant_manage_plat.models import HistoryPlaceOrder
from tenant_manage_plat.models import Price
from django.http import HttpRequest
from django.http import HttpResponse
from django.core.exceptions import ObjectDoesNotExist
import json
from datetime import timedelta
import datetime
import time
import traceback
import copy
from django.db import transaction
import django.utils.timezone
from django.utils.timezone import utc

from util.tool import logger
'''
url:http://115.28.240.2/order/list/
method:post
request:
    {
        'number':'',//order number
        'openid':'',
        'is_done':0,//need pay,1--done,only for weixin
        'terms_of_payment':1
    }
response:
    {
        'error':0,
        'orders':[
            {
                'stadium_name':'',
                'number':'',
                'contact':'',
                'telephone':'',
                'terms_of_payment':,
                'money':,
                'type':,
                'order_time':,
                'note':,
                'is_payed':True,
                'places':[
                    {
                        'name':'',
                        'day':'',
                        'order_hours':[]
                    }
                ],
                'ext':{
                }
            }
        ]
    }
'''
def list (request):
    result={'error':0}
    
    try:
        content = {}
        if len(request.body) > 0: 
            content = json.loads(request.body)
        logger.debug("get order begin: filter = %s.", content)
        
        filter_condition = {}
        if content.has_key('number') and len(content['number']) > 0:
            filter_condition['order__number__exact'] = content['number']
        else:
            filter_condition['order__parent_order__exact'] = None
        if content.has_key('openid'):
            filter_condition['order__openid__exact'] = content['openid']
        if content.has_key('terms_of_payment'):
            filter_condition['order__terms_of_payment__exact'] = int(content['terms_of_payment'])
        #filter_condition['day__gte'] = datetime.datetime(datetime.date.today().year, datetime.date.today().month, 1, 0, 0, 0,0, utc).date() 

        orders=None
        if content.has_key('is_done'):
            if int(content['is_done']) == 0:
                filter_condition['order__is_payed__exact'] = False
                filter_condition['order__terms_of_payment__exact'] = 0
                place_orders = PlaceOrder.objects.filter(**filter_condition)
            else:
                place_orders = PlaceOrder.objects.filter(**filter_condition).exclude(order__is_payed=False,order__terms_of_payment=0)
        else: 
            place_orders = PlaceOrder.objects.filter(**filter_condition)
        logger.error("filter_condition = %s.\nplace_orders = %s", filter_condition, place_orders)
        
        order_number_to_order = {}
        order_number_to_place_list = {}  
        for place_order in place_orders:
            if not order_number_to_order.has_key(place_order.order.number):
                order_number_to_order[place_order.order.number] = place_order.order.get_order_info()
                order_number_to_place_list[place_order.order.number] = []
            order_number_to_place_list[place_order.order.number].append(place_order)
                
        
        for key in order_number_to_place_list:
            number_place_orders = order_number_to_place_list[key]
            place_order_by_place = {}
            for place_order in number_place_orders:
                if not place_order_by_place.has_key(place_order.place.name):
                    place_order_by_place[place_order.place.name] = {'order_hours':[]}
                place_order_by_place[place_order.place.name]['name'] = place_order.place.name
                place_order_by_place[place_order.place.name]['day'] = place_order.day.strftime('%Y-%m-%d')
                place_order_by_place[place_order.place.name]['order_hours'].append(place_order.hour)
                timeStamp = int(time.mktime(place_order.day.timetuple()))
                #logger.debug("timeStamp = %s, time.time() = %s", timeStamp, time.time())
                place_order_by_place[place_order.place.name]['status'] = 0 if timeStamp < time.time() else 1
                
            
            places = place_order_by_place.keys()
            places.sort()
            for place in places:
                order_number_to_order[place_order.order.number]['places'].append(place_order_by_place[place])

        result['orders'] = order_number_to_order.values()
        logger.info("get orders result: %s", result)
        return HttpResponse(json.dumps(result,ensure_ascii=False))
    except Exception,e:
        print e
        result['error'] = -1
        print traceback.format_exc()
        logger.error("get order list error. %s", e)
        return HttpResponse(json.dumps(result,ensure_ascii=False))

'''
url:http://115.28.240.2/order/cancel/
method:post
request:
    {
        'number':'',//order number
    }
response:
    {
        'error':0
    }
'''
def cancel(request):
    result={'error':0}
    try:
        content = {}
        if len(request.body) > 0: 
            content = json.loads(request.body)
        
        filter_condition = {}
        if not content.has_key('number'):
            result['error'] = 1
            return HttpResponse(json.dumps(result,ensure_ascii=False))
        
        order_list = Order.objects.filter(number__exact=content['number'], is_payed__exact=False)
        with transaction.atomic():
            order_id_list = []
            for order in order_list:
                history_order = HistoryOrder.from_order(order)
                history_order.status=1
                history_order.save()
                order_id_list.append(order.id)

            place_order_list = PlaceOrder.objects.filter(order__id__in=order_id_list)
            for place_order in place_order_list:
                history_place_order = HistoryPlaceOrder.from_place_order(place_order)
                history_place_order.save()

            PlaceOrder.objects.filter(order__id__in=order_id_list).delete()
            Order.objects.filter(number__exact=content['number'], is_payed__exact=False).delete()
        return HttpResponse(json.dumps(result,ensure_ascii=False))
    except Exception,e:
        print e
        result['error'] = -1
        print traceback.format_exc()
        return HttpResponse(json.dumps(result,ensure_ascii=False))

'''
url:http://115.28.240.2/order/pay/
method:post
request:
    {
        'number':'',//pay number
        'money':'',
    }
'''
def pay (request):
    result={'error':0}
    try:
        with transaction.atomic():
            content = json.loads(request.body)
            if not content.has_key('number') or not content.has_key('money'):
                result['error'] = 1
                return HttpResponse(json.dumps(result,ensure_ascii=False))

            HistoryOrder.objects.filter(number=content['number']).update(money=content['money'], is_payed=True)
            if Order.objects.filter(number=content['number']).count() == 0:
                result['error'] = 4
                return HttpResponse(json.dumps(result,ensure_ascii=False))
            Order.objects.filter(number=content['number']).update(money=content['money'], is_payed=True)
        return HttpResponse(json.dumps(result,ensure_ascii=False))
    except Exception,e:
        print e
        result['error'] = -1
        print traceback.format_exc()
        return HttpResponse(json.dumps(result,ensure_ascii=False))


'''
url:http://115.28.240.2/order/wplace_order_info/
method:post
request:
    {
        'place_id':'',//cann't be null
        'date':'',//cann't be null
        'hour':0,//0
    }
response:
    {
        'error':0,
        'order_info':{
                'type':'',
                'number':'',
                'contact':'',
                'telephone':'',
                'member_card_number':,
                'terms_of_payment':,
                'telephone':,
                'order_time':,
                'note':,
                'is_payed':True,
             }
    }
'''
def wplace_order_info (request):
    result={'error':0}
    try:
        content = {}
        content = json.loads(request.body)
        
        if not content.has_key('place_id') or not content.has_key('date') or not content.has_key('hour'):
            result['error'] = 1
            return HttpResponse(json.dumps(result,ensure_ascii=False))
        
        try:
            place_order = PlaceOrder.objects.get(place__id=int(ontent['place_id']), day=content['date'], hour=int(content[hour]))
            result['order_info'] = place_order.get_order_info()   
        except ObjectDoesNotExist:
            pass
        return HttpResponse(json.dumps(result,ensure_ascii=False))
    except Exception,e:
        print e
        result['error'] = -1
        print traceback.format_exc()
        return HttpResponse(json.dumps(result,ensure_ascii=False))
    