import json
from channels.generic.websocket import AsyncWebsocketConsumer
from asyncio import sleep
import requests
from .models import CurrencyPreference
from channels.db import database_sync_to_async


class CryptoPriceConsumer(AsyncWebsocketConsumer):

    data = []

    def get_data(self, id):
        return CurrencyPreference.objects.get(pk=id)

    async def connect(self):
        await self.accept()
        self.data = await database_sync_to_async(self.get_data)(self.scope["user"].id)

        from_symbols = []

        from_symbols.append(self.data.first_curr)
        from_symbols.append(self.data.second_curr)
        from_symbols.append(self.data.third_curr)

        to_symbol = 'USD'
        api_key = '08978f0593d717bf8102e726b40714a51f3fbb7fae0d5409af66fa706028523a'

        while True:
            url = f'https://min-api.cryptocompare.com/data/pricemulti?fsyms={from_symbols[0]},{from_symbols[1]},{from_symbols[2]}&tsyms={to_symbol}&api_key={api_key}'
            prices = requests.get(url)
            data = []
            for symbol in from_symbols:
                data.append(prices.json()[symbol][to_symbol])

            await self.send(json.dumps({
                'type': 'connection_established',
                'data': data
            }))
            await sleep(0.2)
