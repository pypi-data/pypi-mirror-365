# -*- coding:utf-8 -*- 
__author__ = 'denishuang'
from django.urls import re_path
from . import views
app_name = 'common'
urlpatterns = [
    re_path(r'^async_result/(?P<task_id>[\w-]+)/', views.async_result),
    # url(r'^stream/', views.stream),
]