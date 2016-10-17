#coding:utf8
from django_cron import CronJobBase, Schedule
from stadium.models import Stadium
from stadium.models import Order
from stadium.models import HistoryOrder
from stadium.models import HistoryPlaceOrder
from stadium.models import Place
from stadium.models import PlaceOrder
import datetime
import time
import traceback
from datetime import timedelta
from django.db import transaction
from django.utils.timezone import utc

class OrderPayMaintain(CronJobBase):
    RUN_EVERY_MINS = 5 # every 5 miniutes

    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
    code = 'stadium.OrderPayMaintain'    # a unique code

    def do(self):
        try:
            with transaction.atomic():
                order_id_list = []
                order_list=Order.objects.filter(time__lt=datetime.datetime.now().replace(tzinfo=utc)-timedelta(seconds=300),is_payed__exact=False,terms_of_payment__exact=0,type__exact=0)
                for order in order_list:
                    history_order = HistoryOrder.from_order(order)
                    history_order.status=2
                    history_order.save()
                    order_id_list.append(order.id)

                place_order_list = PlaceOrder.objects.filter(order__id__in=order_id_list)
                for place_order in place_order_list:
                    history_place_order = HistoryPlaceOrder.from_place_order(place_order)
                    history_place_order.save()

                PlaceOrder.objects.filter(order__id__in=order_id_list).delete()
                Order.objects.filter(time__lt=datetime.datetime.now().replace(tzinfo=utc)-timedelta(seconds=300),is_payed=False,terms_of_payment__exact=0,terms_of_payment__exact=0,type__exact=0).delete()
                return 0
        except Exception,e:
            print traceback.format_exc()
            return -1
                
