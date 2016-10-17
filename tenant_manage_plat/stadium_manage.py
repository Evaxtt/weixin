#coding:utf8
from tenant_manage_plat.models import Stadium
from tenant_manage_plat.models import StadiumForm
from tenant_manage_plat.models import Order
from tenant_manage_plat.models import HistoryOrder
from tenant_manage_plat.models import Place
from tenant_manage_plat.models import PlaceOrder
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


def add(request):
    result= {'error':0}
    try:
        form = StadiumForm(request.POST,request.FILES)
        form.save()
        return HttpResponse(json.dumps(result,ensure_ascii=False))
    except Exception,e:
        print e
        result['error'] = -1
        return HttpResponse(json.dumps(result,ensure_ascii=False))

def edit (request):
    result= {'error':0}
    try:
        print request.POST
        if not request.POST.has_key('id'):
            result['error'] = 1
            return HttpResponse(json.dumps(result,ensure_ascii=False))
        try:
            stadium=Stadium.objects.get(id__exact=int(request.POST['id']))
            stadium_form = StadiumForm(request.POST, instance=stadium)
            stadium_form.save()
            return HttpResponse(json.dumps(result,ensure_ascii=False))
        except ObjectDoesNotExist:
            result['error'] = 4
            return HttpResponse(json.dumps(result,ensure_ascii=False))
    except Exception,e:
        print e
        result['error'] = -1
        return HttpResponse(json.dumps(result,ensure_ascii=False))
    
'''
url:http://115.28.111.96/stadium_info/delete/
method:post
request:
    {
        'ids':[]
    }
response:
    {
        'error':0,--success
    }
'''
def delete (request):
    result= {'error':0}
    try:
        content = json.loads(request.body)
        if not content.has_key('ids'):
            result['error'] = 1
            return HttpResponse(json.dumps(result,ensure_ascii=False))
        Stadium.objects.filter(id__in=content['ids']).delete()
        return HttpResponse(json.dumps(result,ensure_ascii=False))
    except Exception,e:
        print e
        result['error'] = -1
        return HttpResponse(json.dumps(result,ensure_ascii=False))

'''
url:http://115.28.111.96/stadium/list/
method:post
request:
    {
        'appid':,
    }
response:
    {
        'error':0,--success
        'stadium_list':{
            'id':,
            'name':,
            'contact':,
            'telephone':,
            'facility':,
            'address':,
        }
    }
'''
def list(request):
    result={'error':0}
    try:
        filter_condition={}
        #filter_condition['tenant__appid__exact'] = 'wx95198705de430c74'
        content = json.loads(request.body)
        if  content.has_key('appid'):
            filter_condition['tenant__appid__exact'] = content['appid']
        
        result['stadium_list'] = []
        stadium_list = Stadium.objects.filter(**filter_condition)
        for stadium in stadium_list:
            result['stadium_list'].append(stadium.get_detail_info())
        return HttpResponse(json.dumps(result,ensure_ascii=False))    
    except Exception,e:
        print e
        result['error'] = -1
        return HttpResponse(json.dumps(result,ensure_ascii=False))

'''
url:http://115.28.240.2/stadium/wx_order_summary/
method:post
request:
    {
        'id':'',//stadium id
        "sport_id":1,
        'date':'',//2015-10-31
    }
response:
    {
        'error':0,--success
        'stadium':{
            'id':,
            'name':,
            'address':,
            'telephone':，
            'contact':,
            'orders':[
                {
                    'day':'2015-10-31',
                    'remaining':3
                 }
            ],
        }
    }
'''
def wx_order_summary(request):
    result={'error':0}
    try:
        content = json.loads(request.body)
        if not (content.has_key('id') and content.has_key('sport_id')):
            result['error'] = 1
            return HttpResponse(json.dumps(result,ensure_ascii=False))
        
        stadium = Stadium.objects.get(id=int(content['id']))
        place_count = Place.objects.filter(stadium__id__exact=int(content['id']),sport__id__exact=int(content['sport_id'])).count()
        result['stadium'] = stadium.get_detail_info()
        place_remaining = {}
        today=datetime.date.today()
        from_day=datetime.date.today()
        if content.has_key('date'):
            year_month_day = content['date'].split('-')
            from_day = datetime.date(int(year_month_day[0]), int(year_month_day[1]), int(year_month_day[2]))
        
        current_hour = datetime.datetime.now().hour
        if from_day==today and current_hour>7:
            place_remaining[from_day.strftime('%Y-%m-%d')] = place_count*(14 - ((current_hour - 7) if (current_hour < 22) else 14))
        else:
            place_remaining[from_day.strftime('%Y-%m-%d')] = place_count*14
        begin_day = from_day + timedelta(days=1)
        end_day = from_day+timedelta(days=6)
        while begin_day <= end_day:
            place_remaining[begin_day.strftime('%Y-%m-%d')] = place_count*14
            begin_day = begin_day + timedelta(days=1)
        
        place_orders = PlaceOrder.objects.filter(place__stadium__id__exact=int(content['id']),place__sport__id__exact=int(content['sport_id']),day__gte=from_day,day__lte=from_day+timedelta(days=6))
        for order in place_orders:
            if today == order.day:
                if current_hour < order.hour: 
                    place_remaining[order.day.strftime('%Y-%m-%d')] = place_remaining[order.day.strftime('%Y-%m-%d')] - 1
            else:
                place_remaining[order.day.strftime('%Y-%m-%d')] = place_remaining[order.day.strftime('%Y-%m-%d')] - 1
        
        result['stadium']['orders'] = []
        
        for d in place_remaining.keys():
            order_info = {}
            order_info['day'] = d
            order_info['remaining'] = place_remaining[d]
            result['stadium']['orders'].append(order_info)
        return HttpResponse(json.dumps(result,ensure_ascii=False))    
    except Exception,e:
        print traceback.format_exc()
        result['error'] = -1
        return HttpResponse(json.dumps(result,ensure_ascii=False))

'''
url:http://115.28.240.2/stadium/order_detail/
method:post
request:
    {
        'id':'',
        'date':''//2015-10-31
    }
response:
    {
        'error':0,--success
        'orders':[
            {
                'id':,//place id
                'name':,//place name
                'price':{
                       'member':{
                            '8':120,
                            '9':120,
                            ...
                            '22':120,
                        }
                        'nonmember':{
                            '8':160,
                            '9':160,
                            ...
                            '22':160,
                        }
                     },  
                    'order_hours':[8,9,14,15]
             },
            {
                'id':,//place id
                'name':,//place name
                'price':{
                       'member':{
                            '8':120,
                            '9':120,
                            ...
                            '22':120,
                        }
                        'nonmember':{
                            '8':160,
                            '9':160,
                            ...
                            '22':160,
                        }
                     },  
                    'order_hours':[8,9,14,15]
             },
        ]
    }
'''
def order_detail(request):
    result={'error':0}
    try:
        content = json.loads(request.body)
        if not content.has_key('id') or not content.has_key('date'):
            result['error'] = 1
            return HttpResponse(json.dumps(result,ensure_ascii=False))
        
        price_by_type = {}
        year_month_day = content['date'].split('-')
        weekday = datetime.date(int(year_month_day[0]), int(year_month_day[1]), int(year_month_day[2])).weekday()
        weekday = weekday + 1
        prices = Price.objects.filter(stadium__id__exact=int(content['id']), weekday__exact=weekday)
        for price in prices:
            if not price_by_type.has_key(price.type):
                price_by_type[price.type] = {}
                price_by_type[price.type]['member'] = {}
                price_by_type[price.type]['nonmember'] = {}
            
            price_by_type[price.type]['member'][price.hour] = price.member_price
            price_by_type[price.type]['nonmember'][price.hour] = price.nonmember_price
        
        orders_by_place = {}
        places = Place.objects.filter(stadium__id__exact=int(content['id']))
        for place in places:
            if not orders_by_place.has_key(place.name):
                orders_by_place[place.name] = {}
                orders_by_place[place.name]['id'] = place.id
                orders_by_place[place.name]['name'] = place.name
                orders_by_place[place.name]['type'] = place.type
                orders_by_place[place.name]['price'] = price_by_type[place.type]
                orders_by_place[place.name]['order_hours'] = []
            
        result['orders'] = []
        place_orders = PlaceOrder.objects.filter(place__stadium__id__exact=int(content['id']),day__exact=content['date'])
        for order in place_orders:
            orders_by_place[order.place.name]['order_hours'].append(order.hour)
        
        keys = orders_by_place.keys()
        keys.sort()
        for place in keys:
            result['orders'].append(orders_by_place[place])
            
        return HttpResponse(json.dumps(result,ensure_ascii=False))    
    except Exception,e:
        print e
        result['error'] = -1
        print traceback.format_exc()
        return HttpResponse(json.dumps(result,ensure_ascii=False))


'''
url:http://115.28.240.2/stadium_info/submit_order/
method:post
request:
    {
        'id':'',//stadium id
        'contact':'',
        'openid':'',
        'member_card_number':,
        'number':'',
        'telephone':'',
        'note':,
        'type':0,
        'prepay_id':,
        'day':,
        'money':'',
        'terms_of_payment':,//0--weixin,1-present
        'places':[
            {
                'id':,//place id
                'order_hours':[8,9]
            },
        ]
    }
'''
def  submit_order(request):
    result={'error':0}
    try:
        content = json.loads(request.body)
        if not content.has_key('id') or not content.has_key('places') or not content.has_key('day') or not content.has_key('number'):
            result['error'] = 1
            return HttpResponse(json.dumps(result,ensure_ascii=False))
        
        with transaction.atomic():
            order = Order()
            order.stadium = Stadium.objects.get(id=int(content['id']))
            if content.has_key('contact'):
                order.contact=content['contact']
            if content.has_key('openid'):
                order.openid=content['openid']
            if content.has_key('number'):
                order.number=content['number']
            if content.has_key('member_card_number'):
                order.member_card_number=content['member_card_number']
            if content.has_key('prepay_id'):
                order.prepay_id=content['prepay_id']
            if content.has_key('telephone'):
                order.telephone=content['telephone']
            if content.has_key('terms_of_payment'):
                order.terms_of_payment=content['terms_of_payment']
            if content.has_key('money'):
                order.money=content['money']
            if content.has_key('note'):
                order.note=content['note']
            if content.has_key('type'):
                order.type=content['type']
            order.time=datetime.datetime.now().replace(tzinfo=utc)
            for place in content['places']:
                if content.has_key('openid'):
                    count=PlaceOrder.objects.filter(order__openid__exact=content['openid'],order__is_payed__exact=False,order__terms_of_payment__exact=0).count()
                    if count>0:
                        result['error'] = 3
                        return HttpResponse(json.dumps(result,ensure_ascii=False))
                count=PlaceOrder.objects.filter(place__id__exact=place['id'], day__exact=content['day'], hour__in=place['order_hours']).count()
                if count>0:
                    result['error'] = 2
                    result['place'] = place
                    return HttpResponse(json.dumps(result,ensure_ascii=False))

            order.save()

            #insert place order
            place_orders = []
            for place in content['places']:
                place_order = PlaceOrder()
                place_order.place = Place.objects.get(id=int(place['id']))
                place_order.day=content['day']
                for hour in place['order_hours']:
                    new_place_order = copy.deepcopy(place_order)
                    new_place_order.hour = hour
                    new_place_order.order=order
                    place_orders.append(new_place_order)
            
            PlaceOrder.objects.bulk_create(place_orders)
        return HttpResponse(json.dumps(result,ensure_ascii=False))
    except Exception,e:
        print e
        result['error'] = -1
        print traceback.format_exc()
        return HttpResponse(json.dumps(result,ensure_ascii=False))

'''
url:http://115.28.240.2/stadium_info/worder_detail/
method:post
request:
    {
        'id':'',
        'date':''//2015-10-31
    }
response:
    {
        'error':0,--success
        'orders':[
             {
                'id':,//place id
                'name':,//place name
                'price':{
                       'member':{
                            '8':120,
                            '9':120,
                            ...
                            '22':120,
                        }
                        'nonmember':{
                            '8':160,
                            '9':160,
                            ...
                            '22':160,
                        }
                     },  
                    'order_hours':[
                        {
                            'hour':8,
                            'number':,
                            'is_payed':,
                            'member_card_number':,
                            'contact':,
                            'order_type':0,0--mobile order,1--web order,3--lock
                        }
                    ]
             },
        ]
    }
'''
def worder_detail(request):
    result={'error':0}
    try:
        content = json.loads(request.body)
        if not content.has_key('id') or not content.has_key('date'):
            result['error'] = 1
            return HttpResponse(json.dumps(result,ensure_ascii=False))
        
        price_by_type = {}
        year_month_day = content['date'].split('-')
        weekday = datetime.date(int(year_month_day[0]), int(year_month_day[1]), int(year_month_day[2])).weekday()
        weekday = weekday + 1
        prices = Price.objects.filter(stadium__id__exact=int(content['id']), weekday__exact=weekday)
        for price in prices:
            if not price_by_type.has_key(price.type):
                price_by_type[price.type] = {}
                price_by_type[price.type]['member'] = {}
                price_by_type[price.type]['nonmember'] = {}
            
            price_by_type[price.type]['member'][price.hour] = price.member_price
            price_by_type[price.type]['nonmember'][price.hour] = price.nonmember_price
        
        orders_by_place = {}
        places = Place.objects.filter(stadium__id__exact=int(content['id']))
        for place in places:
            if not orders_by_place.has_key(place.name):
                orders_by_place[place.name] = {}
                orders_by_place[place.name]['id'] = place.id
                orders_by_place[place.name]['name'] = place.name
                orders_by_place[place.name]['type'] = place.type
                orders_by_place[place.name]['price'] = price_by_type[place.type]
                orders_by_place[place.name]['order_hours'] = []
            
        result['orders'] = []
        place_orders = PlaceOrder.objects.filter(place__stadium__id__exact=int(content['id']),day__exact=content['date'])
        for place_order in place_orders:
            order_info = {}
            order_info['hour'] = place_order.hour
            if place_order.order != None:
                order_info['order_type'] = place_order.order.type
                order_info['number'] = place_order.order.number
                order_info['is_payed'] = place_order.order.is_payed
                if place_order.order.member_card_number != None:
                    order_info['member_card_number']=place_order.order.member_card_number
                if place_order.order.contact != None:
                    order_info['contact']=place_order.order.contact
            else:
                order_info['order_type'] = 3
            orders_by_place[place_order.place.name]['order_hours'].append(order_info)
              
        keys = orders_by_place.keys()
        keys.sort()
        for place in keys:
            result['orders'].append(orders_by_place[place])
            
        return HttpResponse(json.dumps(result,ensure_ascii=False))    
    except Exception,e:
        print e
        result['error'] = -1
        print traceback.format_exc()
        return HttpResponse(json.dumps(result,ensure_ascii=False))

'''
url:http://115.28.240.2/stadium_info/lock_place/
method:post
request:
    {
        'id':'',//stadium id
        'date':'2014-11-07',
        'places':[
            {
                'id':'',//place id
                'lock_hours':[8,0]
            }
        ]
    }
'''
def lock_place (request):
    result={'error':0}
    try:
        content = json.loads(request.body)
        if not content.has_key('id') or not content.has_key('date') or not content.has_key('places'):
            result['error'] = 1
            return HttpResponse(json.dumps(result,ensure_ascii=False))
        
        with transaction.atomic():
            for place in content['places']:
                count=PlaceOrder.objects.filter(place__id__exact=int(place['id']), day__exact=content['date'], hour__in=place['lock_hours']).count()
                if count>0:
                    result['error'] = 2
                    result['place'] = place
                    return HttpResponse(json.dumps(result,ensure_ascii=False))
            #insert place order
            place_orders = []
            for place in content['places']:
                place_order = PlaceOrder()
                place_order.place = Place.objects.get(id=int(place['id']))
                place_order.day=content['date']
                for hour in place['lock_hours']:
                    new_place_order = copy.deepcopy(place_order)
                    new_place_order.hour = hour
                    new_place_order.order=None
                    place_orders.append(new_place_order)
            
            PlaceOrder.objects.bulk_create(place_orders)
        return HttpResponse(json.dumps(result,ensure_ascii=False))
    except Exception,e:
        print e
        result['error'] = -1
        print traceback.format_exc()
        return HttpResponse(json.dumps(result,ensure_ascii=False))


'''
url:http://115.28.240.2/stadium_info/unlock_place/
method:post
request:
    {
        'id':'',//stadium id
        'date':'2014-11-07',
        'places':[
            {
                'id':'',//place id
                'unlock_hours':[8,0]
            }
        ]
    }
'''
def unlock_place (request):
    result={'error':0}
    try:
        content = json.loads(request.body)
        if not content.has_key('id') or not content.has_key('date') or not content.has_key('places'):
            result['error'] = 1
            return HttpResponse(json.dumps(result,ensure_ascii=False))
        
        with transaction.atomic():
            for place in content['places']:
                PlaceOrder.objects.filter(place__id__exact=place['id'], day__exact=content['date'], hour__in=place['unlock_hours']).delete()
        return HttpResponse(json.dumps(result,ensure_ascii=False))
    except Exception,e:
        print e
        result['error'] = -1
        print traceback.format_exc()
        return HttpResponse(json.dumps(result,ensure_ascii=False))


'''
url:http://115.28.240.2/stadium_info/batch_lock_place/
method:post
request:
    {
        'id':'',//stadium id
        'period':0,//0--by day,1--by week
        'weekday':1,//only for by week,0-monday,1-tuesday
        'place_id':1,
        'start_day':'2015-11-16',
        'end_day':'2015-12-16',
        'lock_hours':[1,2,3,4,5,6]
    }
'''
def batch_lock_place (request):
    result={'error':0}
    try:
        content = json.loads(request.body)
        if not content.has_key('id') or not content.has_key('period') or not content.has_key('place_id') or not content.has_key('start_day') or not content.has_key('end_day') or not content.has_key('lock_hours'):
            result['error'] = 1
            return HttpResponse(json.dumps(result,ensure_ascii=False))
        
        with transaction.atomic():
            place_orders = []
            start_year_month_day = content['start_day'].split('-')
            end_year_month_day = content['end_day'].split('-')
            from_day = datetime.date(int(start_year_month_day[0]), int(start_year_month_day[1]), int(start_year_month_day[2]))
            end_day = datetime.date(int(end_year_month_day[0]), int(end_year_month_day[1]), int(end_year_month_day[2]))
            
            while from_day <= end_day:
                weekday = from_day.weekday() + 1
                if int(content['period']) == 0 or (int(content['period']) == 1 and weekday == int(content['weekday'])):
                    place_order_object=PlaceOrder()
                    place_order_object.place=Place.objects.get(id=int(content['place_id']))
                    for hour in content['lock_hours']:
                        new_place_order = copy.deepcopy(place_order_object)
                        new_place_order.hour = hour
                        new_place_order.order=None
                        new_place_order.day=from_day
                        place_orders.append(new_place_order)
                from_day = from_day + timedelta(days=1)  
            print place_orders
            PlaceOrder.objects.bulk_create(place_orders)
        return HttpResponse(json.dumps(result,ensure_ascii=False))
    except Exception,e:
        print e
        result['error'] = -1
        print traceback.format_exc()
        return HttpResponse(json.dumps(result,ensure_ascii=False))

'''
url:http://115.28.240.2/stadium_info/batch_unlock_place/
method:post
request:
    {
        'id':'',//stadium id
        'period':0,//0--by day,1--by week
        'weekday':1,//only for by week,1-monday,2-tuesday
        'place_id':1,
        'start_day':'2015-11-16',
        'end_day':'2015-12-16',
        'unlock_hours':[1,2,3,4,5,6]
    }
'''
def batch_unlock_place (request):
    result={'error':0}
    try:
        content = json.loads(request.body)
        if not content.has_key('id') or not content.has_key('period') or not content.has_key('place_id') or not content.has_key('start_day') or not content.has_key('end_day') or not content.has_key('unlock_hours'):
            result['error'] = 1
            return HttpResponse(json.dumps(result,ensure_ascii=False))
        
        with transaction.atomic():
            place_orders = []
            start_year_month_day = content['start_day'].split('-')
            end_year_month_day = content['end_day'].split('-')
            from_day = datetime.date(int(start_year_month_day[0]), int(start_year_month_day[1]), int(start_year_month_day[2]))
            end_day = datetime.date(int(end_year_month_day[0]), int(end_year_month_day[1]), int(end_year_month_day[2]))
            if int(content['period']) == 0:
                PlaceOrder.objects.filter(place__id__exact=int(content['place_id']),day__gte=from_day,day__lte=end_day,hour__in=content['unlock_hours'],order__exact=None).delete()
            
            need_match_day=[]
            if int(content['period']) == 1:
                while from_day <= end_day:
                    weekday = from_day.weekday() + 1
                    if weekday == int(content['weekday']):  
                        need_match_day.append(from_day)
                    from_day = from_day + timedelta(days=1)
                PlaceOrder.objects.filter(place__id__exact=int(content['place_id']),day__in=need_match_day,hour__in=content['unlock_hours'],order__exact=None).delete()
        return HttpResponse(json.dumps(result,ensure_ascii=False))
    except Exception,e:
        print e
        result['error'] = -1
        print traceback.format_exc()
        return HttpResponse(json.dumps(result,ensure_ascii=False))

