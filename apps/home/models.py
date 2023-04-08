# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class CurrencyPreference(models.Model):
    user_id = models.CharField(max_length=100, primary_key=True)
    first_curr = models.CharField(max_length=3, default='BTC')
    second_curr = models.CharField(max_length=3, default='ETH')
    third_curr = models.CharField(max_length=3, default='SOL')

    def __str__(self) -> str:
        return self.user_id

