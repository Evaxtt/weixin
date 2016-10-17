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
from django.db import transaction
import django.utils.timezone
from django.utils.timezone import utc
import log

'''
url:http://115.28.111.96/place/add/
action:post
request:
    {
        "stadium_id":1,
        "sport_id":1,
        "time_unit":60,
        "place_type":1,
        "places":[ "name1","name2"],
        "business_time":[
            {
                "from_weekday":1,
                "to_weekday":1,
                "time_of_day":[
                    {
                        "from_hour":8,
                        "to_hour":12
                    }
                ]
              },
        ]
    }
'''
def add (request):
    result= {'error':0}
    try:
        content = json.loads(request.body)
        if not (content.has_key('time_unit') and content.has_key('sport_id') and content.has_key('stadium_id') and content.has_key('place_type')):
            result['error'] = 1
            return HttpResponse(json.dumps(result,ensure_ascii=False))
        
        stadium = None
        try:
            stadium = Stadium.objects.get(id__exact=int(content['stadium_id']))
        except ObjectDoesNotExist:
            result['error'] = 401
            return HttpResponse(json.dumps(result,ensure_ascii=False)) 

        sport = None
        try:
            sport = Sport.objects.get(id__exact=int(content['sport_id']))
        except ObjectDoesNotExist:
            result['error'] = 402
            return HttpResponse(json.dumps(result,ensure_ascii=False)) 

        place_type = None
        try:
            place_type = PlaceType.objects.get(id__exact=int(content['place_type']))
        except ObjectDoesNotExist:
            result['error'] = 403
            return HttpResponse(json.dumps(result,ensure_ascii=False)) 

        #places = []
        for place_name in content['places']:
            place = Place()
            place.name = place_name
            place.place_type=place_type
            place.stadium = stadium
            place.sport = sport
            place.time_unit = int(content['time_unit'])
            if content.has_key('business_time'):
                place.business_time = json.dumps(content['business_time'],ensure_ascii=False)
            #places.append(place)
            place.save()
        
        return HttpResponse(json.dumps(result,ensure_ascii=False))
    except Exception,e:
        traceback.print_exc()
        result['error'] = -1
        return HttpResponse(json.dumps(result,ensure_ascii=False))    

'''
url:http://115.28.111.96/place/edit/
action:post
request:
    {
        "stadium_id":1,
        "sport_id":1,
        "time_unit":60,
        "place_type":1,
        "places":[ "name1","name2"],
        "business_time":[
            {
                "from_weekday":1,
                "to_weekday":1,
                "time_of_day":[
                    {
                        "from_hour":8,
                        "to_hour":12
                    }
                ]
              },
        ]
    }
'''
def edit (request):
    result= {'error':0}
    try:
        content = json.loads(request.body)
        if not (content.has_key('time_unit') and content.has_key('sport_id') and content.has_key('stadium_id') and content.has_key('place_type')):
            result['error'] = 1
            return HttpResponse(json.dumps(result,ensure_ascii=False))
        with transaction.atomic():
            Place.objects.filter(stadium__id__exact=int(content['stadium_id']), sport__id__exact=int(content['sport_id']), place_type__id__exact=int(content['place_type'])).exclude(name__in=content["places"]).delete()
            stadium = None
            try:
                stadium = Stadium.objects.get(id__exact=int(content['stadium_id']))
            except ObjectDoesNotExist:
                result['error'] = 401
                return HttpResponse(json.dumps(result,ensure_ascii=False)) 

            sport = None
            try:
                sport = Sport.objects.get(id__exact=int(content['sport_id']))
            except ObjectDoesNotExist:
                result['error'] = 402
                return HttpResponse(json.dumps(result,ensure_ascii=False)) 

            place_type = None
            try:
                place_type = PlaceType.objects.get(id__exact=int(content['place_type']))
            except ObjectDoesNotExist:
                result['error'] = 403
                return HttpResponse(json.dumps(result,ensure_ascii=False)) 
            

            places = Place.objects.filter(stadium__id__exact=int(content['stadium_id']), sport__id__exact=int(content['sport_id']), place_type__id__exact=int(content['place_type']), name__in=content['places'])
            name_to_place = {}
            for place in places:
                name_to_place[place.name] = place
                
            #places = []
            for place_name in content['places']:
                place = None
                if name_to_place.has_key(place_name):
                    place = name_to_place[place_name]
                else:
                    place = Place()
                
                place.name = place_name
                place.place_type=place_type
                place.stadium = stadium
                place.sport = sport
                place.time_unit = int(content['time_unit'])
                if content.has_key('business_time'):
                    place.business_time = json.dumps(content['business_time'],ensure_ascii=False)
                #places.append(place)
                place.save()
        
        return HttpResponse(json.dumps(result,ensure_ascii=False)) 
    except Exception,e:
        print e
        result['error'] = -1
        return HttpResponse(json.dumps(result,ensure_ascii=False))    

'''
url:http://115.28.111.96/place/delete/
action:post
request:
    {
        "stadium_id":1,
        "sport_id":1,
        "place_type":1
    }
'''
def delete (request):
    result= {'error':0}
    try:
        content = json.loads(request.body)
        if not (content.has_key('sport_id') and content.has_key('stadium_id') and content.has_key('place_type')):
            result['error'] = 1
            return HttpResponse(json.dumps(result,ensure_ascii=False))

        Place.objects.filter(stadium__id__exact=int(content['stadium_id']), sport__id__exact=int(content['sport_id']), place_type__id__exact=int(content['place_type'])).delete()
        return HttpResponse(json.dumps(result,ensure_ascii=False))
    except Exception,e:
        print e
        result['error'] = -1
        return HttpResponse(json.dumps(result,ensure_ascii=False))    



'''
url:http://115.28.111.96/place/list/
action:post
request:
    {
        "stadium_id":1,
    }
response:
    {
        "error":0,--success
        "places":[
            {
                "sport":{"id":1,"name":"test"},
                "time_unit":60,
                "place_type":{"id":1,"name":"test"},
                "places":[ {"id":1,"name":"test"}],
                "business_time":[
                    {
                        "from_weekday":1,
                        "to_weekday":1,
                        "time_of_day":[
                            {
                                "from_hour":8,
                                "to_hour":12
                            }
                        ]
                      },
                ]
            }
        ]
    }
'''
def list (request):
    result= {'error':0, 'places':[]}
    try:
        content = json.loads(request.body)
        if not content.has_key('stadium_id'):
            result['error'] = 1
            return HttpResponse(json.dumps(result,ensure_ascii=False))

        places = Place.objects.select_related().filter(stadium__id__exact=int(content['stadium_id']))
        place_group_by = {}
        for place in places:
            if not place_group_by.has_key(place.sport.id):
                place_group_by[place.sport.id] = {}
            if not place_group_by[place.sport.id].has_key(place.place_type.id):
                place_group_by[place.sport.id][place.place_type.id] = {"places":[]} 
            place_group_by[place.sport.id][place.place_type.id]['sport'] = {'id':place.sport.id, 'name':place.sport.name}
            place_group_by[place.sport.id][place.place_type.id]['time_unit'] = place.time_unit
            place_group_by[place.sport.id][place.place_type.id]['place_type'] = {'id':place.place_type.id, 'name':place.place_type.name}
            place_group_by[place.sport.id][place.place_type.id]['places'].append({'id':place.id, 'name':place.name})
            place_group_by[place.sport.id][place.place_type.id]['business_time']=json.loads(place.business_time)
        
        for key_sport in place_group_by.keys():
            print place_group_by[key_sport]
            for key_place_type,value in place_group_by[key_sport].items():
                result['places'].append(value)
                
        return HttpResponse(json.dumps(result,ensure_ascii=False))
    except Exception,e:
        print e
        result['error'] = -1
        return HttpResponse(json.dumps(result,ensure_ascii=False)) 

'''
url:http://115.28.111.96/place_type/add/
action:post
request:
    {
        "type_names":["VVIP1","VIP2"]
    }
response:
    {
        'error':0,--success
    }
'''
def set_place_type (request):
    result= {'error':0}
    try:
        content = json.loads(request.body)
        if not content.has_key('type_names'):
            result['error'] = 1
            return HttpResponse(json.dumps(result,ensure_ascii=False))
        
        with transaction.atomic():
            PlaceType.objects.filter(tenant__id__exact=1).exclude(name__in=content['type_names']).delete()
            place_types=[]
            exist_places = []
            tenant = None
            place_type_objects=PlaceType.objects.select_related().filter(tenant__id__exact=1, name__in=content['type_names'])
            for place_type_object in place_type_objects:
                tanant = place_type_object.tenant
                exist_places.append(place_type_object.name)
            if tenant == None:       
                tenant=Tenant.objects.get(id__exact=1)

            for name in content['type_names']:
                if name in exist_places:
                    continue
                place_type = PlaceType()
                place_type.name=name
                place_type.tenant = tenant
                place_types.append(place_type)
            PlaceType.objects.bulk_create(place_types)
            return HttpResponse(json.dumps(result,ensure_ascii=False))
    except Exception,e:
        print e
        result['error'] = -1
        return HttpResponse(json.dumps(result,ensure_ascii=False))

'''
url:http://115.28.111.96/place_type/list/
action:get
request:
response:
    {
        'error':0,
        'place_types'[{
            "id":1
            "name":"VVIP1"
        }]
    }
'''
def place_type_list (request):
    result= {'error':0}
    try:
        place_types = PlaceType.objects.filter(tenant__id__exact=1)
        result['place_types'] = []
        for place_type in place_types:
            place_type_info = {}
            place_type_info['id'] = place_type.id
            place_type_info['name'] = place_type.name
            result['place_types'].append(place_type_info)
        return HttpResponse(json.dumps(result,ensure_ascii=False))
    except Exception,e:
        print e
        result['error'] = -1
        return HttpResponse(json.dumps(result,ensure_ascii=False))