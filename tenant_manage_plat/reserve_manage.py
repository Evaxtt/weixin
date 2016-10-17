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

'''
url:http://115.28.240.2/stadium/order/
method:post
request:
    {
        'id':'',
        'sport_id':1,
        'date':''//2015-10-31
    }
response:
    {
        'error':0,--success
        'orders':[
            {
                'id':,//place id
                'name':,//place name
                'business_time'::[
                    {
                        "from_hour":8,
                        "to_hour":12
                    }
                ],
                'price':{
                            '8':120,
                            '9':120,
                            ...
                            '22':120,
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
            {
                'id':,//place id
                'name':,//place name
                'business_time'::[
                    {
                        "from_hour":8,
                        "to_hour":12
                    }
                ],
                'price':{
                            '8':120,
                            '9':120,
                            ...
                            '22':120,
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
def stadium_order(request):
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
        result['orders'] = []
        if not content.has_key('sport_id') or content['sport_id']==None or len(str(content['sport_id'])) == 0:
            return HttpResponse(json.dumps(result,ensure_ascii=False))  

        prices = Price.objects.select_related().filter(stadium__id__exact=int(content['id']), weekday__exact=weekday, sport__id__exact=int(content['sport_id']))
        for price in prices:
            if not price_by_type.has_key(price.place_type.id):
                price_by_type[price.place_type.id] = {}
            
            price_by_type[price.place_type.id][price.hour] = price.price
        
        orders_by_place = {}
        places = Place.objects.filter(stadium__id__exact=int(content['id']), sport__id__exact=int(content['sport_id']))
        for place in places:
            if not orders_by_place.has_key(place.name):
                orders_by_place[place.name] = {}
                orders_by_place[place.name]['id'] = place.id
                orders_by_place[place.name]['name'] = place.name
                orders_by_place[place.name]['place_type_id'] = place.place_type.id
                if price_by_type.has_key(place.place_type.id):               
                    orders_by_place[place.name]['price'] = price_by_type[place.place_type.id]
                else:
                    orders_by_place[place.name]['price'] = {}
                orders_by_place[place.name]['order_hours'] = []
                business_times = json.loads(place.business_time)
                for business_time in business_times:
                    if weekday >= business_time['from_weekday'] and weekday <= business_time['to_weekday']:
                        orders_by_place[place.name]['business_time'] = business_time['time_of_day']
                        break
            
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
url:http://115.28.240.2/stadium/order/
method:post
request:
    {
        'id':'',
        'sport_id':1,
        'date':''//2015-10-31
    }
response:
    {
        'error':0,--success
        'orders':[
            {
                'id':,//place id
                'name':,//place name
                'business_time'::[
                    {
                        "from_hour":8,
                        "to_hour":12
                    }
                ],
                'price':{
                            '8':120,
                            '9':120,
                            ...
                            '22':120,
                     },  
                    'order_hours':[8,9,14,15]
             },
            {
                'id':,//place id
                'name':,//place name
                'business_time'::[
                    {
                        "from_hour":8,
                        "to_hour":12
                    }
                ],
                'price':{
                            '8':120,
                            '9':120,
                            ...
                            '22':120,
                     },  
                    'order_hours':[8,9,14,15]
             },
        ]
    }
'''
def wx_stadium_order(request):
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
        prices = Price.objects.select_related().filter(stadium__id__exact=int(content['id']), weekday__exact=weekday, sport__id__exact=int(content['sport_id']))
        for price in prices:
            if not price_by_type.has_key(price.place_type.id):
                price_by_type[price.place_type.id] = {}
            
            price_by_type[price.place_type.id][price.hour] = price.price
        
        orders_by_place = {}
        places = Place.objects.filter(stadium__id__exact=int(content['id']))
        for place in places:
            if not orders_by_place.has_key(place.name):
                orders_by_place[place.name] = {}
                orders_by_place[place.name]['id'] = place.id
                orders_by_place[place.name]['name'] = place.name
                orders_by_place[place.name]['place_type_id'] = place.place_type.id
                if price_by_type.has_key(place.place_type.id):               
                    orders_by_place[place.name]['price'] = price_by_type[place.place_type.id]
                else:
                    orders_by_place[place.name]['price'] = {}
                orders_by_place[place.name]['order_hours'] = []
                business_times = json.loads(place.business_time)
                for business_time in business_times:
                    if weekday >= business_time['from_weekday'] and weekday <= business_time['to_weekday']:
                        orders_by_place[place.name]['business_time'] = business_time['time_of_day']
                        break
            
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
url:http://115.28.111.96/stadium/submit_order/
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
url:http://115.28.240.2/stadium/batch_submit_order/
method:post
request:
    {
        'id':'',//stadium id
        'contact':'',
        'member_card_number':,
        'number':'',
        'telephone':'',
        'note':,
        'money':'',
        'terms_of_payment':,//0--weixin,1-present
        'period':0,//0--by day,1--by week
        'weekday':1,//only for by week,0-monday,1-tuesday
        'place_id':1,
        'start_day':'2015-11-16',
        'end_day':'2015-12-16',
        'order_hours':[1,2,3,4,5,6]
    }
'''
def  batch_submit_order(request):
    result={'error':0}
    try:
        content = json.loads(request.body)
        if not content.has_key('id') or not content.has_key('period') or not content.has_key('place_id') or not content.has_key('start_day') or not content.has_key('end_day') or not content.has_key('order_hours') or not content.has_key('number'):
            result['error'] = 1
            return HttpResponse(json.dumps(result,ensure_ascii=False))
        
        with transaction.atomic():
            ext = {}
            order = Order()
            order.stadium = Stadium.objects.get(id=int(content['id']))
            if content.has_key('contact'):
                order.contact=content['contact']
            if content.has_key('member_card_number'):
                order.member_card_number=content['member_card_number']
            if content.has_key('telephone'):
                order.telephone=content['telephone']
            if content.has_key('terms_of_payment'):
                order.terms_of_payment=content['terms_of_payment']
            if content.has_key('money'):
                order.money=content['money']
            if content.has_key('note'):
                order.note=content['note']
            order.number=content['number']
            order.time=datetime.datetime.now().replace(tzinfo=utc)
            sub_order=copy.deepcopy(order)
            ext['period'] = content['period']
            if content.has_key('weekday'):
                ext['weekday'] = content['weekday']
            ext['start_day'] = content['start_day']
            ext['end_day'] = content['end_day']
            ext['order_hours'] = content['order_hours']
            order.ext = json.dumps(ext,ensure_ascii=False)
            order.type=2
            order.save()
            
            #get place object
            place_object=Place.objects.get(id=int(content['place_id']))

            #get price
            prices = {}
            price_objects = Price.objects.filter(stadium__id__exact=int(content['id']),type__exact=place_object.type)
            for price_object in price_objects:
                if not prices.has_key(price_object.weekday):
                    prices[price_object.weekday] = {}
                if content.has_key('member_card_number'):
                    prices[price_object.weekday][price_object.hour] = price_object.member_price
                else:
                    prices[price_object.weekday][price_object.hour] = price_object.nonmember_price

            #insert place order
            place_orders = []
            start_year_month_day = content['start_day'].split('-')
            end_year_month_day = content['end_day'].split('-')
            from_day = datetime.date(int(start_year_month_day[0]), int(start_year_month_day[1]), int(start_year_month_day[2]))
            end_day = datetime.date(int(end_year_month_day[0]), int(end_year_month_day[1]), int(end_year_month_day[2]))
       
            i=0
            while from_day <= end_day:
                weekday = from_day.weekday() + 1
                if int(content['period']) == 0 or (int(content['period']) == 1 and weekday == int(content['weekday'])):
                    new_sub_order = copy.deepcopy(sub_order)
                    new_sub_order.type=1
                    new_sub_order.parent_order=order
                    new_sub_order.number = str(content['number']) + "-" + str(i)
                    i = i + 1
                    money = 0
                    for hour in content['order_hours']:
                        money = money + prices[weekday][hour]
                    new_sub_order.money = money
                    new_sub_order.save()

                    for hour in content['order_hours']:
                        new_place_order = PlaceOrder()
                        new_place_order.place = place_object
                        new_place_order.day=from_day
                        new_place_order.hour = hour
                        new_place_order.order=new_sub_order
                        place_orders.append(new_place_order)
                from_day = from_day + timedelta(days=1)
            PlaceOrder.objects.bulk_create(place_orders)
        return HttpResponse(json.dumps(result,ensure_ascii=False))
    except Exception,e:
        print e
        result['error'] = -1
        print traceback.format_exc()
        return HttpResponse(json.dumps(result,ensure_ascii=False))

'''
url:http://115.28.240.2/stadium/lock_place/
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
url:http://115.28.240.2/stadium/unlock_place/
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
url:http://115.28.240.2/stadium/batch_lock_place/
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
url:http://115.28.111.96/stadium/batch_unlock_place/
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