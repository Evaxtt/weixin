#coding:utf8
from tenant_manage_plat.models import Sport
from tenant_manage_plat.models import Place
from django.http import HttpRequest
from django.http import HttpResponse
from django.core.exceptions import ObjectDoesNotExist
import json
import traceback
import django.utils.timezone
from django.utils.timezone import utc


'''
url:http://115.28.111.96/sport_type/list/?stadium_id
action:get
response:
    {
        "error":0,--success
        "sport_types":[
         {
            "id":1,
            "name":"足球"
          }
          ]
    }
'''
def type_list (request):
    result={'error':0, 'sport_types':[]}
    content = request.GET.dict()
    try:
        if not content.has_key('stadium_id'):
            sport_types = Sport.objects.all()
            for sport_type in sport_types:
                sport_type_info = {}
                sport_type_info['id'] = sport_type.id
                sport_type_info['name'] = sport_type.name
                result['sport_types'].append(sport_type_info)
        else:
            places = Place.objects.select_related().only('sport').filter(stadium__id__exact=int(content['stadium_id']))
            sport_type_id_to_type = {}
            for place in places:
                if not sport_type_id_to_type.has_key(place.sport.id):
                    sport_type_id_to_type[place.sport.id] = {'id':place.sport.id, 'name':place.sport.name}
            print sport_type_id_to_type
            result['sport_types'] = sport_type_id_to_type.values()
        return HttpResponse(json.dumps(result,ensure_ascii=False))
    except Exception,e:
        print e
        result['error'] = -1
        print traceback.format_exc()
        return HttpResponse(json.dumps(result,ensure_ascii=False))

