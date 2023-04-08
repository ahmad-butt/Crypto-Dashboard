# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""
from django.core.files.storage import FileSystemStorage
from django.shortcuts import render
from django import template
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from django.urls import reverse
import requests
from .models import CurrencyPreference
from django.views.decorators.csrf import csrf_protect
import strategies
import utils
import pandas as pd
import numpy as np
from utils import Rule


@login_required(login_url="/login/")
def index(request):
    context = {'segment': 'index'}
    if not CurrencyPreference.objects.filter(user_id=request.user.id).exists():
        pref = CurrencyPreference(
            user_id=request.user.id, first_curr='BTC', second_curr='ETH', third_curr='SOL')
        pref.save()

    html_template = loader.get_template('home/index.html')
    return HttpResponse(html_template.render(context, request))


@csrf_protect
def change_preference(request):
    print(request.user.id)
    data = request.POST.getlist('preference')
    c = CurrencyPreference()
    c.user_id = request.user.id
    c.first_curr = data[0]
    c.second_curr = data[1]
    c.third_curr = data[2]
    preference = CurrencyPreference.objects.get(pk=request.user.id)
    preference = c
    preference.save()

    return HttpResponseRedirect('home/index.html')


@csrf_protect
def run_backtest(request):
    result = strategies.run_backtest()
    context = {
        'result': result,
        'return': result.total_return()*100,
        'chart_data': result.plot().to_html()
    }
    return render(request, 'home/backtest_results.html', context)


@csrf_protect
def run_backtrader(request):
    pass


@csrf_protect
def run_data_builder(request):

    if(request.POST):
        data = request.POST.dict()
        symbol = data.get("symbol")
        interval = data.get("interval")
        start_date = data.get("start_date")
        end_date = data.get("end_date")
        print(symbol, interval, start_date, end_date)

    result = utils.get_crypto_data(symbol, interval, start_date, end_date)
    print(result.columns)
    context = {
        'result': result,
    }
    return render(request, 'home/data_builder.html', context)


@csrf_protect
def run_technical_indicators(request):

    if request.method == 'POST' and request.FILES['upload']:
        upload = request.FILES['upload']
        fss = FileSystemStorage()
        file = fss.save(upload.name, upload)
        file_url = fss.url(file)

        data = request.POST.dict()
        indicators_list = request.POST.getlist('indicators')
        result = utils.calculate_technical_indicators_multiple(
            indicators_list, file_url)
        print(type(result))
        context = {
            'indicator_result': result,
        }
        return render(request, 'home/technical_indicator.html', context)


@csrf_protect
def get_form_features(request):
    if request.method == 'POST' and request.FILES['file-upload']:
        upload = request.FILES['file-upload']
        fss = FileSystemStorage()
        file = fss.save(upload.name, upload)
        file_url = fss.url(file)
    result = utils.filter_features(file_url)
    print(type(result))
    context = {
        'filtered_features': result,
    }
    return render(request, 'home/backtrader.html', context)


@csrf_protect
def run_backtrader(request):
    if(request.POST):
        data = request.POST.dict()
        ticker1 = data.get("compare_from_feature")
        constant1 = data.get("first_multiplier")
        ticker2 = data.get("compare_to_feature")
        constant2 = data.get("second_multiplier")
        lag = data.get("lookback_period")
        relation = data.get("relation")
        kind = data.get("action")

    rule = Rule(ticker1, ticker2, constant1,
                constant2, lag, relation, kind)
    context = {
        'rule': rule,
    }
    return render(request, 'home/backtrader.html', context)


@login_required(login_url="/login/")
def pages(request):
    context = {}
    # All resource paths end in .html.
    # Pick out the html file name from the url. And load that template.
    try:

        load_template = request.path.split('/')[-1]
        if load_template == 'admin':
            return HttpResponseRedirect(reverse('admin:index'))
        elif load_template == 'form_elements.html' or load_template == 'backtest.html' or load_template == 'data_builder.html':
            url = f'https://min-api.cryptocompare.com/data/blockchain/list?api_key=08978f0593d717bf8102e726b40714a51f3fbb7fae0d5409af66fa706028523a'
            currencies = requests.get(url)
            symbols = []
            for k in currencies.json()['Data']:
                symbols.append(k)
            context['symbols'] = symbols

            # Getting Tickers for Form Selection
            context['tickers'] = utils.get_tickers()

        context['segment'] = load_template
        html_template = loader.get_template('home/' + load_template)
        return HttpResponse(html_template.render(context, request))

    except template.TemplateDoesNotExist:

        html_template = loader.get_template('home/page-404.html')
        return HttpResponse(html_template.render(context, request))

    except:
        html_template = loader.get_template('home/page-500.html')
        return HttpResponse(html_template.render(context, request))
