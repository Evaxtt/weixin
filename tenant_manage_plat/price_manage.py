#coding:utf8
from tenant_manage_plat.models import Stadium
from tenant_manage_plat.models import PlaceType
from tenant_manage_plat.models import Place
from tenant_manage_plat.models import Tenant
from tenant_manage_plat.models import Price
from tenant_manage_plat.models import Sport
from django.http import HttpRequest
from django.http import HttpResponse
from django.core.exceptions import ObjectDoesNotExist
import json
from datetime import timedelta
import datetime
import time
import traceback
import copy
import traceback
from django.db import transaction
import django.utils.timezone
from django.utils.timezone import utc


'''
url:http://115.28.111.96/price/batch_set/
action:post
request:
{
    "stadium_id":1,
    "sport_id";1,
    "place_type":1,
    "prices":{
            "weekday1":{
                    "hour1":255,//hour1 8,9,10...
                    "hour2":255, //hour2 12,13...
                    ...
                    "hourN":212//hourN 14,...
              "weekday2":{//1-monday,2--tuesday...
                    "hour1":255,//hour1 8,9,10...
                    "hour2":255, //hour2 12,13...
                    ...
                    "hourN":212//hourN 14,...
                    },//optional
                ...
                "weekday3":{//1-monday,2--tuesday...
                    "hour1":255,//hour1 8,9,10...
                    "hour2":255, //hour2 12,13...
                    ...
                    "hourN":212//hourN 14,...
                    },//optional
                }
         }
}
'''
def batch_set (request):
    result= {'error':0}
    try:
        content = json.loads(request.body)
        if not (content.has_key('stadium_id') and content.has_key('place_type') and content.has_key('sport_id')):
            result['error'] = 1
            return HttpResponse(json.dumps(result,ensure_ascii=False))
        
        place_prices = content['prices']

        stadium = None
        try:
            stadium=Stadium.objects.get(id__exact=int(content['stadium_id']))
        except ObjectDoesNotExist:
            result['error'] = 501
            return HttpResponse(json.dumps(result,ensure_ascii=False))

        place_type = None
        try:
            place_type=PlaceType.objects.get(id__exact=int(content['place_type']))
        except ObjectDoesNotExist:
            result['error'] = 502
            return HttpResponse(json.dumps(result,ensure_ascii=False))

        sport = None
        try:
            sport=Sport.objects.get(id__exact=int(content['sport_id']))
        except ObjectDoesNotExist:
            result['error'] = 503
            return HttpResponse(json.dumps(result,ensure_ascii=False))

        with transaction.atomic():
            weekdays = content['prices'].keys()
            Price.objects.filter(stadium__id=int(content['stadium_id']), sport__id=int(content['sport_id']), place_type__id=int(content['place_type']), weekday__in=weekdays).delete()
            for weekday in weekdays:
                for hour,money in content['prices'][weekday].items(): 
                    price = Price()
                    price.weekday = int(weekday)
                    price.hour = hour
                    price.price=money
                    price.stadium=stadium
                    price.place_type=place_type
                    price.sport=sport
                    price.save()
        return HttpResponse(json.dumps(result,ensure_ascii=False))
    except Exception,e:
        print traceback.format_exc()
        print e
        result['error'] = -1
        return HttpResponse(json.dumps(result,ensure_ascii=False))    
 

'''
url:http://115.28.111.96/price/list/
action:post
request:
    {
        "stadium_id":1,
        "sport_id";1,
        "weekday":1
    }
response:
    {
        "error":0,--success
        "place_prices":[
         {
            "place_type_name":"vip1",
            "business_time":[
                    {
                        "from_hour":8,
                        "to_hour":12
                    }
                ],
            "prices":{
                      "hour1":255,//hour1 8,9,10...
                        "hour2":255, //hour2 12,13...
                        ...
                        "hourN":212//hourN 14,...
                        }
        ]     }
    }
'''
def list (request):
    result= {'error':0}
    try:
        content = json.loads(request.body)
        if not (content.has_key('stadium_id') and content.has_key('sport_id') and content.has_key('weekday')):
            result['error'] = 1
            return HttpResponse(json.dumps(result,ensure_ascii=False))

        place_type_name_to_business_time = {}
        places = Place.objects.select_related().filter(stadium__id__exact=int(content['stadium_id']), sport__id__exact=int(content['sport_id']))
        for place in places:
            business_times = json.loads(place.business_time)
            for business_time in business_times:
                if int(content['weekday']) >= business_time['from_weekday'] and int(content['weekday']) <= business_time['to_weekday']:
                    place_type_name_to_business_time[place.place_type.name] = business_time['time_of_day']
                    break
        
        place_type_name_to_price = {}
        result['place_prices'] = []
        prices = Price.objects.select_related().filter(stadium__id__exact=int(content['stadium_id']), sport__id__exact=int(content['sport_id']), weekday__exact=int(content['weekday']))
        for price in prices:
            if not place_type_name_to_price.has_key(price.place_type.name):
                place_type_name_to_price[price.place_type.name] = {}
            place_type_name_to_price[price.place_type.name][str(price.hour)] = price.price
        
        for key,value in place_type_name_to_price.items():
            place_price = {}
            place_price['place_type_name'] = key
            place_price['prices'] = value
            if place_type_name_to_business_time.has_key(key):
                place_price['business_time']=place_type_name_to_business_time[key]
            else:
                place_price['business_time']=[]
            result['place_prices'].append(place_price)
        return HttpResponse(json.dumps(result,ensure_ascii=False))
    except Exception,e:
        print traceback.format_exc()
        print e
        result['error'] = -1
        return HttpResponse(json.dumps(result,ensure_ascii=False)) 
