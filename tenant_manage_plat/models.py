from django.db import models
from django.template.defaultfilters import default
import time
from datetime import date
from datetime import datetime
from django.utils.timezone import utc
import django.utils.timezone
from django.forms import ModelForm
import json
    
class Tenant(models.Model):
    id=models.AutoField(primary_key=True)
    name=models.CharField(max_length=64,null=False,unique=True)
    contact=models.CharField(max_length=64,null=False)
    cellphone=models.CharField(max_length=20,null=False)
    address=models.CharField(max_length=128,null=True,blank=True)
    secret=models.CharField(max_length=64,null=True)
    mch_id=models.CharField(max_length=64,null=True)
    key=models.CharField(max_length=64,null=True)
    appid=models.CharField(max_length=64,null=True)
    
    def get_tenant (self):
        tenant_detail={}
        tenant_detail['id'] = self.id
        tenant_detail['name'] = self.name
        tenant_detail['contact'] = self.contact
        tenant_detail['cellphone'] = self.cellphone
        tenant_detail['address'] = self.address
        tenant_detail['secret'] = self.secret
        tenant_detail['mch_id'] = self.mch_id
        tenant_detail['key'] = self.key
        tenant_detail['appid'] = self.appid
        return tenant_detail
            
    class Meta:
        db_table="tenant"
        
class User(models.Model):
    id=models.AutoField(primary_key=True)
    name=models.CharField(max_length=64,null=False,unique=True)
    passwd=models.CharField(max_length=64,null=False)
    tenant=models.ForeignKey(Tenant,null=True,blank=True)
    telephone=models.CharField(max_length=20,null=True)
    role=models.IntegerField(default=1)
    status=models.IntegerField(default=1)
    expire_time=models.DateTimeField(auto_now_add=True)
    
    def check_passwd(self, password):
        if self.passwd == password:
            return True
        return False
    
    class Meta:
        db_table="user"

class Sport(models.Model):
    id=models.AutoField(primary_key=True)
    name=models.CharField(max_length=64,null=False) 

    class Meta:
        db_table="sport"

class Area(models.Model):
    id=models.AutoField(primary_key=True)
    name=models.CharField(max_length=128,null=False)
    type=models.PositiveSmallIntegerField(null=False,db_index=True)
    parent_id=models.PositiveIntegerField(null=False)

    class Meta:
        db_table="area"    
        
class Stadium(models.Model):
    id=models.AutoField(primary_key=True)
    tenant=models.ForeignKey(Tenant,null=True,blank=True)
    name=models.CharField(max_length=64,null=False)
    contact=models.CharField(max_length=64,null=False)
    address=models.CharField(max_length=256,null=False)
    telephone=models.CharField(max_length=20,null=False)
    facility=models.CharField(max_length=256,null=False)
    area=models.ForeignKey(Area)
    img=models.ImageField(upload_to='photos/stadium',null=True,blank=True)

    def get_detail_info(self):
        stadium_info = {}
        stadium_info['id'] = self.id
        stadium_info['name'] = self.name
        stadium_info['address'] = self.address
        stadium_info['contact'] = self.contact
        stadium_info['telephone'] = self.telephone
        stadium_info['facility'] = self.facility
        stadium_info['contact'] = self.contact
        stadium_info['area'] = self.area.id
        return stadium_info

    class Meta:
        db_table="stadium"

class StadiumForm(ModelForm):
    class Meta:
        model = Stadium
        fields = ['tenant', 'name', 'contact', 'address', 'telephone', 'facility', 'area', 'img']

class UserStadium(models.Model):
    id=models.AutoField(primary_key=True)
    user=models.ForeignKey(User,null=False)
    stadium=models.ForeignKey(Stadium,null=False)

    class Meta:
        db_table="user_stadium"
    
class PlaceType(models.Model):
    id=models.AutoField(primary_key=True)
    name=models.CharField(max_length=64,null=False,unique=True)
    tenant=models.ForeignKey(Tenant)
    class Meta:
        db_table="place_type"

class Place(models.Model):
    id=models.AutoField(primary_key=True)
    name=models.CharField(max_length=64,null=False,db_index=True)
    note=models.CharField(max_length=128,null=True)
    place_type=models.ForeignKey(PlaceType)
    sport=models.ForeignKey(Sport)
    time_unit=models.PositiveSmallIntegerField(null=False,default=60)
    stadium=models.ForeignKey(Stadium)
    business_time=models.CharField(max_length=512,null=True)      
    class Meta:
        db_table="place"
        ordering = ["name"]
        unique_together = (("place_type", "sport", "stadium", "name"),)
    
class Price(models.Model):
    id=models.AutoField(primary_key=True)
    weekday=models.PositiveSmallIntegerField(null=False)
    hour=models.PositiveSmallIntegerField(null=False)
    stadium=models.ForeignKey(Stadium)
    place_type=models.ForeignKey(PlaceType)
    sport=models.ForeignKey(Sport)
    price=models.PositiveSmallIntegerField(null=False)
  
    class Meta:
        db_table="price"
        ordering = ["hour"]

class Member(models.Model):
    id=models.AutoField(primary_key=True)
    name=models.CharField(max_length=64,null=False)
    telephone=models.CharField(max_length=20,null=False)
    is_full_member=models.BooleanField()
    point=models.PositiveIntegerField(null=False, default=0)

    class Meta:
        db_table="member"

class Order(models.Model):
    id=models.AutoField(primary_key=True)
    stadium=models.ForeignKey(Stadium)
    #order type,0-mobile order,1-web ,2-batch order,order 3-lock
    type=models.PositiveSmallIntegerField(null=False, default=0)
    number=models.CharField(max_length=32,null=False,unique=True)
    contact=models.CharField(max_length=64,null=False)
    openid=models.CharField(max_length=64,null=True,blank=True)
    member_card_number=models.CharField(max_length=64,null=True,blank=True)
    telephone=models.CharField(max_length=20,null=False)
    terms_of_payment=models.PositiveSmallIntegerField(null=False,default=0)
    money=models.PositiveIntegerField(null=False)
    note=models.CharField(max_length=128,null=True)
    prepay_id=models.CharField(max_length=64,null=True)
    time=models.DateTimeField()
    is_payed=models.BooleanField(default=False)
    ext=models.CharField(max_length=512,null=True,blank=True)
    parent_order=models.ForeignKey('self',null=True,blank=True)

    def get_order_info (self):
        order_info={}
        order_info['stadium_name'] = self.stadium.name
        order_info['type'] = self.type
        order_info['number'] = self.number
        order_info['contact'] = self.contact
        order_info['money'] = self.money
        if self.openid != None:
            order_info['openid'] = self.openid
        else:
            order_info['openid'] = ''
        if self.member_card_number != None: 
            order_info['member_card_number'] = self.member_card_number
        else:
            order_info['member_card_number'] = ''
        if self.telephone != None: 
            order_info['telephone'] = self.telephone
        else:
            order_info['telephone'] = ''
        if self.contact != None: 
            order_info['contact'] = self.contact
        else:
            order_info['contact'] = ''
        order_info['terms_of_payment'] = self.terms_of_payment
        if self.note != None:    
            order_info['note'] = self.note
        else:
            order_info['note'] = ''
        order_info['order_time'] = self.time.strftime('%Y-%m-%d %H:%M:%S')
        order_info['is_payed']=self.is_payed
        if self.prepay_id != None:
            order_info['prepay_id'] = self.prepay_id
        else:
            order_info['prepay_id'] = ''
        if self.ext != None:
            order_info['ext'] = json.loads(self.ext)
        order_info['places'] = []
        
        order_info['stadium_img'] = self.stadium.img.url
        order_info['place'] = self.stadium.area.name
        return order_info

    class Meta:
        db_table="order"
        ordering = ["-time"]
    
class PlaceOrder(models.Model):
    id=models.AutoField(primary_key=True)
    place=models.ForeignKey(Place)
    day=models.DateField(null=False)
    hour=models.PositiveSmallIntegerField(null=False)
    order=models.ForeignKey(Order,null=True,blank=True)
 
    class Meta:
        ordering = ["day", "hour"]
        db_table="place_order"


class HistoryOrder(models.Model):
    id=models.AutoField(primary_key=True)
    stadium=models.ForeignKey(Stadium)
    openid=models.CharField(max_length=64,null=True,blank=True)
    member_card_number=models.CharField(max_length=64,null=True,blank=True)
    type=models.PositiveSmallIntegerField(null=False, default=0)
    number=models.CharField(max_length=32,null=False,unique=True)
    contact=models.CharField(max_length=64,null=False)
    telephone=models.CharField(max_length=20,null=False)
    note=models.CharField(max_length=128,null=True)
    terms_of_payment=models.PositiveSmallIntegerField(null=False,default=0)
    money=models.PositiveIntegerField(null=False)
    prepay_id=models.CharField(max_length=64,null=True)
    is_payed=models.BooleanField(default=False)
    time=models.DateTimeField()
    #0--done,1--user cancel,2--system cancel
    status=models.PositiveSmallIntegerField(null=False, default=0)

    @classmethod  
    def from_order(cls,order):
        history_order=HistoryOrder()
        history_order.id=order.id
        history_order.number=order.number
        history_order.stadium=order.stadium
        history_order.openid=order.openid
        history_order.member_card_number=order.member_card_number
        history_order.type=order.type
        history_order.contact=order.contact
        history_order.telephone=order.telephone
        history_order.note=order.note
        history_order.terms_of_payment=order.terms_of_payment
        history_order.prepay_id=order.prepay_id
        history_order.time=order.time
        history_order.money=order.money
        history_order.is_payed=order.is_payed
        return history_order

    class Meta:
        db_table="history_order"

class HistoryPlaceOrder(models.Model):
    id=models.AutoField(primary_key=True)
    place=models.ForeignKey(Place)
    day=models.DateField(null=False)
    hour=models.PositiveSmallIntegerField(null=False)
    order=models.ForeignKey(HistoryOrder,null=True,blank=True)

    @classmethod  
    def from_place_order(cls,place_order):
        history_place_order = HistoryPlaceOrder()
        history_place_order.id=place_order.id
        history_place_order.place=place_order.place
        history_place_order.day=place_order.day
        history_place_order.hour=place_order.hour
        history_place_order.order=HistoryOrder.from_order(place_order.order)
        return history_place_order
 
    class Meta:
        ordering = ["day", "hour"]
        db_table="history_place_order"

class Activity(models.Model):
    id=models.AutoField(primary_key=True)
    stadium=models.ForeignKey(Stadium,null=False)
    start_time=models.DateTimeField(null=False)
    end_time=models.DateTimeField(null=False)
    price=models.PositiveIntegerField(null=False)
    wx_title=models.CharField(max_length=64,null=False)
    title=models.CharField(max_length=64,null=False)
    content=models.CharField(max_length=1024,null=False)
    attendant_count=models.PositiveIntegerField(null=False,default=0)
    publish=models.PositiveSmallIntegerField(null=False,default=0)
    img=models.ImageField(upload_to='photos/activity',null=True,blank=True)

    def get_detail_info(self):
        activity_info = {}
        activity_info['id'] = self.id
        activity_info['stadium_name'] = self.stadium.name
        activity_info['price'] = self.price
        activity_info['start_time'] = self.start_time.strftime('%Y-%m-%d %H:%M:%S')
        activity_info['end_time'] = self.end_time.strftime('%Y-%m-%d %H:%M:%S')
        activity_info['title'] = self.title
        activity_info['content'] = self.content
        activity_info['attendant_count'] = self.attendant_count
        activity_info['registered_count']=ActivityApplicant.objects.filter(activity__id__exact=self.id).count()
        activity_info['img']=self.img.url
        return activity_info

    class Meta:
        db_table="activity"

class ActivityForm(ModelForm):
    class Meta:
        model = Activity
        fields = ['stadium', 'start_time', 'end_time', 'price', 'title', 'wx_title', 'content', 'publish', 'attendant_count', 'img']

class ActivityApplicant(models.Model):
    id=models.AutoField(primary_key=True)
    activity=models.ForeignKey(Activity,null=False)
    name=models.CharField(max_length=64,null=False)
    telephone=models.CharField(max_length=20,null=False)
    openid=models.CharField(max_length=64,null=True,blank=True)
    number=models.CharField(max_length=32,null=True,unique=True)
    checked=models.SmallIntegerField(default=0)
    prepay_id=models.CharField(max_length=64,null=True)
    apply_time=models.DateTimeField(auto_now_add=True)
    is_payed=models.BooleanField(default=False)
    terms_of_payment=models.PositiveSmallIntegerField(null=False,default=0)
    def get_applicant (self):
        applicant = {}
        applicant['id'] = self.id
        applicant['activity_id'] = self.activity.id
        applicant['name'] = self.name
        applicant['telephone'] = self.telephone
        applicant['checked'] = self.checked
        applicant['is_payed'] = self.is_payed
        applicant['apply_time'] = self.apply_time.strftime('%Y-%m-%d %H:%M:%S')
        
        applicant['activity_name'] = self.activity.title
        applicant['stadium_name'] = self.activity.stadium.name
        applicant['activity_state'] = 0 if int(time.mktime(self.activity.end_time.timetuple())) < time.time() else 1
        applicant['img'] = self.activity.img.url
        applicant['price'] = self.activity.price
        applicant['start_time'] = self.activity.start_time.strftime('%Y-%m-%d %H:%M:%S')
        applicant['end_time'] = self.activity.end_time.strftime('%Y-%m-%d %H:%M:%S')
        return applicant

    class Meta:
        db_table="activity_applicant"    
            
class Log(models.Model):
    id=models.AutoField(primary_key=True)
    operator_name=models.CharField(max_length=64,null=False)
    operator_role=models.CharField(max_length=32,null=False)
    type=models.PositiveSmallIntegerField(null=False)
    time=models.DateTimeField(auto_now_add=True)
    desc=models.CharField(max_length=256,null=False)

    class Meta:
        db_table="log"
    
    
class WeixinUser(models.Model):
    openid = models.CharField(primary_key=True,max_length=128)
    name = models.CharField(max_length=32,unique=True)
    phone = models.CharField(max_length=20,null=True,default="")
    avatar = models.CharField(max_length=164,default="/media/photos/users/wx_test.jpg")
    balance = models.PositiveSmallIntegerField(default=0)
    credits = models.PositiveSmallIntegerField(default=0)
    #activitise = models.ManyToManyField(Activity, through="Activity")
    
    def get_weixin_user(self):
        user = {}
        user['openid'] = self.openid
        user['name'] = self.name
        user['phone'] = self.phone
        user['avatar'] = self.avatar
        user['balance'] = self.balance
        user['credits'] = self.credits
        #user['activitise'] = self.activitise.all()
        return user
    
    class Meta:
        db_table="weixin_user"


    
class TenantSettings(models.Model):
    settingName = models.CharField(primary_key=True, max_length=64)
    settingValue = models.CharField(max_length=128)


    def get_tenant_setting(self):
        return self.settingValue

    class Meta:
        db_table="tenantsettings"



    
    