# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

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
import requests
from datetime import datetime
from nlp import SentimentAnalysis


def get_crypto_news():
    url = "https://min-api.cryptocompare.com/data/v2/news/?lang=EN&api_key=08978f0593d717bf8102e726b40714a51f3fbb7fae0d5409af66fa706028523a"
    response = requests.get(url)
    return response.json()


# def view_all_news(request):
#     all_news = get_crypto_news()

#     context = {
#         "all_news": all_news,
#         'range': range(0, len(all_news["Data"]))
#     }

#     return HttpResponseRedirect('home/view_all_news.html', context)


@login_required(login_url="/login/")
def index(request):
    if not CurrencyPreference.objects.filter(user_id=request.user.id).exists():
        pref = CurrencyPreference(
            user_id=request.user.id, first_curr='BTC', second_curr='ETH', third_curr='SOL')
        pref.save()

    user_pref = CurrencyPreference.objects.get(pk=request.user.id)

    news_res = get_crypto_news()

    sa = SentimentAnalysis(news_res)

    sentiments = sa.run_sentiment_analysis()

    i = 0

    for d in news_res["Data"]:
        d["sentiment"] = sentiments[i]
        i += 1
        if i == 5:
            break

    context = {
        'segment': 'index',
        'first_curr': user_pref.first_curr,
        'second_curr': user_pref.second_curr,
        'third_curr': user_pref.third_curr,
        'news': news_res["Data"][0:5]
    }

    html_template = loader.get_template('home/index.html')
    return HttpResponse(html_template.render(context, request))


@csrf_protect
def change_preference(request):
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
    pf = strategies.run_backtest()

    data = {
        "Start": pf.stats()["Start"],
        "End": pf.stats()["End"],
        "Period": pf.stats()["Period"],
        "Start Value": pf.stats()["Start Value"],
        "End Value": pf.stats()["End Value"],
        "Total Trades": pf.stats()["Total Trades"],
        "Win Rate": pf.stats()["Win Rate [%]"],
        "Best Trade": pf.stats()["Best Trade [%]"],
        "Worst Trade": pf.stats()["Worst Trade [%]"],
        "Avg Win Trade": pf.stats()["Avg Winning Trade [%]"],
        "Avg Losing Trade": pf.stats()["Avg Losing Trade [%]"],
        "Total Profit": pf.total_profit(),
        "Total Return": pf.stats()["Total Return [%]"],
        "Total Fees Paid": pf.stats()["Total Fees Paid"],
        "Max Drawdown": pf.stats()["Max Drawdown [%]"],
    }

    context = {
        'chart_data': pf.plot().to_html(),
        'data': data,
    }
    return render(request, 'home/backtest_results.html', context)


@login_required(login_url="/login/")
def pages(request):
    user_pref = CurrencyPreference.objects.get(pk=request.user.id)
    news_res = get_crypto_news()

    context = {
        'segment': 'index',
        'first_curr': user_pref.first_curr,
        'second_curr': user_pref.second_curr,
        'third_curr': user_pref.third_curr,
        'news': news_res["Data"][0:5],
    }

    # All resource paths end in .html.
    # Pick out the html file name from the url. And load that template.
    try:

        load_template = request.path.split('/')[-1]
        if load_template == 'admin':
            return HttpResponseRedirect(reverse('admin:index'))
        elif load_template == 'form_elements.html' or load_template == 'backtest.html':
            url = f'https://min-api.cryptocompare.com/data/blockchain/list?api_key=08978f0593d717bf8102e726b40714a51f3fbb7fae0d5409af66fa706028523a'
            currencies = requests.get(url)
            symbols = []
            for k in currencies.json()['Data']:
                symbols.append(k)
            context['symbols'] = symbols
        elif load_template == 'coint_pairs.html':
            context = {
                "range": range(20),
            }
        elif load_template == 'view_all_news.html':
            sa = SentimentAnalysis(news_res)

            sentiments = sa.run_sentiment_analysis()

            i = 0

            for d in news_res["Data"]:
                d["sentiment"] = sentiments[i]
                i += 1

            context = {
                'all_news': news_res,
                'range': range(0, len(news_res["Data"]))
            }

        context['segment'] = load_template
        html_template = loader.get_template('home/' + load_template)
        return HttpResponse(html_template.render(context, request))

    except template.TemplateDoesNotExist:

        html_template = loader.get_template('home/page-404.html')
        return HttpResponse(html_template.render(context, request))

    except:
        html_template = loader.get_template('home/page-500.html')
        return HttpResponse(html_template.render(context, request))
