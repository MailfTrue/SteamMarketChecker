import requests
import os
from bs4 import BeautifulSoup
from telebot import TeleBot, apihelper, types
from time import sleep

tb = TeleBot('1135142333:AAGoEjLyAa-t8hoi-B5CTamX-WapeEVds5o')
proxy = {
    "http": "http://ADn53r:fB1D0y@213.166.72.225:9268",
    "https": "https://ADn53r:fB1D0y@213.166.72.225:9268"
}
exclude_words = ['Сувенирный',]
chat_id = 448406310
sleep_time = 5
apihelper.proxy = proxy


def get_price(hash_name):
	try:
		response = requests.get('https://steamcommunity.com/market/priceoverview/?appid=730&country=US&currency=1&market_hash_name=' + hash_name, proxies=proxy)
		return response.json()['lowest_price']
	except Exception as e:
		print('error passed', e)

os.system('cls')
while True:
	tb.send_chat_action(chat_id, 'typing')
	try:
		response = requests.get('https://steamcommunity.com/market/recent?country=RU&language=russian&currency=1', proxies=proxy)
	except Exception as e:
		print('error passed', e)
		continue
	response_json = response.json()
	if not response_json:
		sleep(sleep_time)
		print('Blocked')
		continue
	contexts = response_json.get('assets', {}).get('730', {})
	for context in contexts:
		for item_id, item in contexts[context].items():
			stickers = []
			if any(k in item['market_name'] for k in exclude_words):
				continue
			for description in item.get('descriptions'):
				if 'Наклейка' in description['value']:
					description_html = BeautifulSoup(description['value'], 'lxml')
					try:
						stickers_string = description_html.get_text().split('Наклейка: ')[1]
					except IndexError:
						stickers_string = description_html.get_text()
					for k in stickers_string.strip().split(','):
						stickers.append(k.strip())
			if len(stickers) > 0:
				price = get_price(item['market_hash_name'])
				for k in response_json['listinginfo'].values():
					if k['asset']['id'] == item_id:
						try:
							item_price = (k['converted_fee'] + k['converted_price']) / 100
						except KeyError:
							item_price = '-'
				stickers_text = '  -- ' + '\n  -- '.join(k.strip() for k in stickers)
				message_text = '\n'.join([item['market_name'],
					                      'Минимальная цена: ' + str(price),
					                      'Цена этого предмета: $' + str(item_price),
					                      'Наклейки:',
					                      stickers_text])
				markup = types.InlineKeyboardMarkup()
				markup.add(
					types.InlineKeyboardButton('Открыть ТП', "https://steamcommunity.com/market/listings/730/" + item['market_hash_name'])
				)
				tb.send_message(chat_id, message_text, reply_markup=markup)
	sleep(sleep_time)
