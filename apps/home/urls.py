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
    path('run_data_builder', views.run_data_builder, name='data_builder'),
    path('run_technical_indicators',
         views.run_technical_indicators, name='data_engineer'),
    path('run_backtrader', views.run_backtrader, name='backtrader'),
    path('get_form_features', views.get_form_features, name='get_features'),
    # Matches any html file
    re_path(r'^.*\.*', views.pages, name='pages'),

]
