"""yxy URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.8/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add an import:  from blog import urls as blog_urls
    2. Add a URL to urlpatterns:  url(r'^blog/', include(blog_urls))
"""
from django.conf.urls import include, url
from django.contrib import admin
from tenant_manage_plat import place_manage
from tenant_manage_plat import user_manage
from tenant_manage_plat import tenant_manage
from tenant_manage_plat import stadium_manage
from tenant_manage_plat import order_manage
from tenant_manage_plat import sport_manage
from tenant_manage_plat import price_manage
from tenant_manage_plat import activity_manage
from tenant_manage_plat import reserve_manage
from tenant_manage_plat import weixin, tenant_settings_manage

urlpatterns = [
    url(r'^admin/', include(admin.site.urls)),
    url(r'^login/$', user_manage.login),
    url(r'^login_out/$', user_manage.login_out),
    url(r'^tenant/add/$', tenant_manage.add),
    url(r'^tenant/edit/$', tenant_manage.edit),
    url(r'^tenant/list/$', tenant_manage.list),
    url(r'^tenant/delete/$', tenant_manage.delete),
    url(r'^tenant/detail/$', tenant_manage.detail),
    url(r'^tenantSettings/edit/$', tenant_settings_manage.edit),
    url(r'^tenantSettings/list/$', tenant_settings_manage.list),
    url(r'^user/add/$', user_manage.add),
    url(r'^user/edit/$', user_manage.edit),
    url(r'^user/delete/$', user_manage.delete),
    url(r'^user/list/$', user_manage.list),
    url(r'^user/get_login_info/$', user_manage.get_login_info),
    url(r'^place/list/$', place_manage.list),
    url(r'^place/add/$', place_manage.add),
    url(r'^place/edit/$', place_manage.edit),
    url(r'^place/delete/$', place_manage.delete),
    url(r'^place_type/set/$', place_manage.set_place_type),
    url(r'^place_type/list/$', place_manage.place_type_list),
    url(r'^sport_type/list/$', sport_manage.type_list),
    url(r'^activity/add/$', activity_manage.add),
    url(r'^activity/delete/$', activity_manage.delete),
    url(r'^activity/apply/$', activity_manage.apply),
    url(r'^activity/list/$', activity_manage.list),
    url(r'^activity/applicant_list/$', activity_manage.applicant_list),
    url(r'^activity/pay/$', activity_manage.pay),
    url(r'^activity/wx_list/$', activity_manage.wx_list),
    url(r'^activity/wx_detail/$', activity_manage.wx_detail),
    url(r'^stadium/list/$', stadium_manage.list),
    url(r'^stadium/add/$', stadium_manage.add),
    url(r'^stadium/edit/$', stadium_manage.edit),
    url(r'^stadium/delete/$', stadium_manage.delete),
    url(r'^stadium/order/$', reserve_manage.stadium_order),
    url(r'^stadium/batch_submit_order/$', reserve_manage.batch_submit_order),
    url(r'^stadium/wx_order_summary/$', stadium_manage.wx_order_summary),
    url(r'^stadium/order_detail/$', stadium_manage.order_detail),
    url(r'^stadium/worder_detail/$', stadium_manage.worder_detail),
    url(r'^stadium/submit_order/$', reserve_manage.submit_order),
    url(r'^stadium/lock_place/$', reserve_manage.lock_place),
    url(r'^stadium/unlock_place/$', reserve_manage.unlock_place),
    url(r'^stadium/batch_lock_place/$', reserve_manage.batch_lock_place),
    url(r'^stadium/batch_unlock_place/$', reserve_manage.batch_unlock_place),
    url(r'^order/list/$', order_manage.list),
    url(r'^order/pay/$', order_manage.pay),
    url(r'^order/wplace_order_info/$', order_manage.wplace_order_info),
    url(r'^order/cancel/$', order_manage.cancel),
    url(r'^price/batch_set/$', price_manage.batch_set),
    url(r'^price/list/$', price_manage.list),
    url(r'^wx/$', weixin.weixin),
    url(r'^wx/get_prepay_id',weixin.get_prepay_id),
    url(r'^wx/start_pay',weixin.start_pay),
    url(r'^wx/get_openid$', weixin.get_openid),
    url(r'^wx/get_openid_redirect$', weixin.get_openid_redirect),
    url(r'^wx/get_openid_redirect_query', weixin.get_openid_redirect_query),
    url(r'^wx/get_wx_pay_notify', weixin.get_wx_pay_notify),
	url(r'^wx/save_appid$', weixin.save_appid),
    
    url(r'^wx/getUserInfo$', weixin.getUserInfo),
    url(r'^wx/delUser$', weixin.deleteUser),
    url(r'^wx/editUser$', weixin.editUser),
    #url(r'^wx/reserve', weixin.reserve'),
]

