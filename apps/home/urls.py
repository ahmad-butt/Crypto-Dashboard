# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django.urls import path, re_path
from apps.home import views

urlpatterns = [

    # The home page
    path('', views.index, name='home'),
    path('change_preference', views.change_preference, name='change_preference'),
    path('run_backtest', views.run_backtest, name='run_tets'),
    # path('view_all_news', views.view_all_news, name='view_all_news'),

    # Matches any html file
    re_path(r'^.*\.*', views.pages, name='pages'),

]
