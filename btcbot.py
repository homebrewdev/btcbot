# PROJECT: @HBCryptoBot
# DESCRIPTION: my new telegram bot for request of crypto rates from api.exmo.com
# and daily usd rates from 'https://www.cbr-xml-daily.ru/daily_json.js'
# AUTHOR: Egor Devyatov
# DATE: 22-Dec-2020

import requests
from datetime import datetime
import json
import telebot
from telebot import types
import config
import strings
import time
# import logging

# берем из конфига токен бота
bot = telebot.TeleBot(config.token)


# определяем класс который будет описывать хранение всех запрошенных данных по крипте
class CryptoData(object):
    """ Класс CryptoData: несет всю информацию о крипте
        Поля:
            btc_usd, btc_rub : цена битка в долларах и рублях
            eth_usd, eth_rub : цена eth в долларах и рублях
            zec_usd, zec_rub : цена zec в долларах и рублях
        Методы:
            request_prices - запрос данных с API Exmo
            get_prices       - вывод всех цена по btc, eth и zec
    """

    def __init__(self, btc_usd, btc_rub, eth_usd, eth_rub, zec_usd, zec_rub):
        """Constructor"""
        self.btc_usd = btc_usd
        self.btc_rub = btc_rub
        self.eth_usd = eth_usd
        self.eth_rub = eth_rub
        self.zec_usd = zec_usd
        self.zec_rub = zec_rub

    def request_prices(self):
        try:
            # запрос к api.exmo.com
            response = requests.request("GET", config.API_URL)
            decoded_json = json.loads(response.text)
            # распарсим json
            self.btc_usd = decoded_json["BTC_USD"]["sell_price"]
            self.btc_rub = decoded_json["BTC_RUB"]["sell_price"]
            self.eth_usd = decoded_json["ETH_USD"]["sell_price"]
            self.eth_rub = decoded_json["ETH_RUB"]["sell_price"]
            self.zec_usd = decoded_json["ZEC_USD"]["sell_price"]
            self.zec_rub = decoded_json["ZEC_RUB"]["sell_price"]
            return 1

        except requests.exceptions.HTTPError as req_error:
            # logging.error("http Error: %s %s" % (config.API_URL, req_error))
            return 0
        except requests.exceptions.ConnectionError as req_error:
            # logging.error("Error Connecting: %s %s" % (config.API_URL, req_error))
            return 0
        except requests.exceptions.RequestException as req_error:
            # logging.error("Unrecognised error %s %s" % (config.API_URL, req_error))
            return 0

    def get_prices(self):
        prices_string = \
            "BTC : %s USD\n" % self.btc_usd + \
            "BTC : %s RUB\n" % self.btc_rub + \
            "ETH : %s USD\n" % self.eth_usd + \
            "ETH : %s RUB\n" % self.eth_rub + \
            "ZEC : %s USD\n" % self.zec_usd + \
            "ZEC : %s RUB" % self.zec_rub
        return prices_string


# посылаем курс биткоина пользователю в чат
def send_prices_to_user(message):
    # отправляем пользователю сообщение с курсами 3 криптовалют
    time_marker = datetime.timetuple(datetime.now())
    year = str(time_marker.tm_year)
    month = str(time_marker.tm_mon)
    day = str(time_marker.tm_mday)
    bot.send_message(message.chat.id,
                     "Текущий курс криптовалют биржи EXMO.COM дату:\n{}.{}.{}".format(day, month, year))
    bot.send_message(message.chat.id, crypto.get_prices())


# посылаем курс доллара пользователю в чат
def send_usd_rate_to_user(message):
    # отправляем пользователю сообщение с курсами 3 криптовалют
    time_marker = datetime.timetuple(datetime.now())
    year = str(time_marker.tm_year)
    month = str(time_marker.tm_mon)
    day = str(time_marker.tm_mday)
    bot.send_message(message.chat.id,
                     "Текущий курс доллара ЦБР на дату:\n{}.{}.{}".format(day, month, year))
    bot.send_message(message.chat.id, f"{get_usd_rate()}")


# запрос курса доллара с сайта ЦБР
def get_usd_rate():
    try:
        # logging.info("Запрос курса доллара с сайта ЦБР")
        response = requests.request("GET", config.API_URL_USD)
        response.raise_for_status()
        decoded_json = json.loads(response.text)
        usd_rate = decoded_json["Valute"]['USD']['Value']
        return f"1 USD = {usd_rate} рублей"
    except requests.exceptions.HTTPError as req_error:
        # logging.error("http Error: {} {}".format(config.API_URL_USD, req_error))
        return "нет данных"
    except requests.exceptions.ConnectionError as req_error:
        # logging.error("Error Connecting: {} {}".format(config.API_URL_USD, req_error))
        return "нет данных"
    except requests.exceptions.RequestException as req_error:
        # logging.error("unrecognised error: {} {}".format(config.API_URL_USD, req_error))
        return "нет данных"


# обработчик при старте команды - /start
@bot.message_handler(commands=["start"])
def start(message):
    bot.send_message(message.chat.id, strings.msg_help)
    start_dlg(message)


# обработчик при старте команды - /rate - узнать курс биткоина
@bot.message_handler(commands=["rate"])
def rate(message):
    # запрос по API
    crypto.request_prices()
    send_prices_to_user(message)  # отсылаем месседж с ценами
    time.sleep(5)
    start_dlg(message)


# обработчик при старте команды - /rateUSD - узнать курс доллара
@bot.message_handler(commands=["rateusd"])
def rate_usd(message):
    # отсылаем месседж с курсом доллара
    send_usd_rate_to_user(message)
    time.sleep(5)
    start_dlg(message)


# обработчик при старте команды - /help - послать пользователю help
@bot.message_handler(commands=["help"])
def settings(message):
    bot.send_message(message.chat.id, strings.msg_help)
    start_dlg(message)


# на любые ответы пользователя в чат бота
# показываем опять главное меню, дабы пользователь только нажимал кнопки диалога
@bot.message_handler(content_types=["text"])
def any_msg(message):
    start_dlg(message)


# при старте бота выводим основные кнопки меню - начало диалога с пользователем
def start_dlg(message):
    # Создаем клавиатуру и каждую из кнопок
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    callback_btn = types.InlineKeyboardButton(text=strings.btn_get_rate, callback_data="rate")
    callback_usd_btn = types.InlineKeyboardButton(text=strings.btn_USD_rate, callback_data="usd_rate")
    url_btn = types.InlineKeyboardButton(text=strings.msg_my_site, url=config.my_site_URL)
    # размещаем кнопки курса криптовалют, курса доллара и кнопки - посетить сайт разраба
    keyboard.add(callback_btn, callback_usd_btn, url_btn)
    # основное сообщение в меню
    bot.send_message(message.chat.id, "Выбирай пункт меню для дальнейших действий:", reply_markup=keyboard)


# ---------------------------------------------------------------------------------------
# главный обработчик всех нажатий пользователя на кнопки диалога, для формирования заказа
@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    # Если сообщение из чата с ботом
    if call.message:
        # Если нажата inline-кнопка 'Узнать курс криптовалют'
        if call.data == "rate":
            # logging.info("Нажата кнопка 'Узнать курс криптовалют'")
            # запрос по API
            crypto.request_prices()
            # показываем pop up окно с инфой show_alert=True
            bot.answer_callback_query(callback_query_id=call.id, show_alert=True, text=crypto.get_prices())
            # отсылаем цены крипты месседжем
            send_prices_to_user(call.message)
            time.sleep(5)
            start_dlg(call.message)

        if call.data == "usd_rate":
            # logging.info("Нажата кнопка 'Курс доллара'")
            # показываем pop up окно с инфой show_alert=True
            bot.answer_callback_query(callback_query_id=call.id, show_alert=True,
                                      text=f"Курс доллара на сегодня: \n{get_usd_rate()}")
            send_usd_rate_to_user(call.message)
            time.sleep(5)
            start_dlg(call.message)


# обработчик действий после нажатия юзером на кнопку - Узнать курс криптовалют
def category1(message):
    send_prices_to_user(message)
    start_dlg(message)


# самое основное тут )
if __name__ == '__main__':
    '''
    # настройка логирования
    # logging.basicConfig(filename='btcbot {}.log'.format(datetime.now()), filemode='w',
    #                    format='%(name)s - %(levelname)s - %(message)s', datefmt='%d-%b-%y %H:%M:%S', level=logging.INFO)
    # logging.info("Btcbot запущен!")
    '''
    # инициализируем объект через конструктор
    crypto = CryptoData(0, 0, 0, 0, 0, 0)
    # делаем так чтобы наш бот не падал когда сервер api.telegram.org выкидывает нашего бота)
    while True:
        try:
            bot.polling(none_stop=True)

        except Exception as e:
            print(str(e))  # или просто print(e) если у вас логгера нет,
            # или import traceback; traceback.print_exc() для печати полной инфы
            time.sleep(15)

        # чтобы остановить бот по нажатию CTRL-C в терминале
        except KeyboardInterrupt:
            exit()
