from decouple import config
import telebot
from telebot import types
import requests
from bs4 import BeautifulSoup

my1lobot = config("TOKEN")
bot = telebot.TeleBot(my1lobot)

HEADERS = {
    "User-Agent": config("USER_AGENT"),
    "accept": "*/*"
}
@bot.message_handler(["help"])
def help(message):
    bot.send_message(message.chat.id, "Введите команду /start или /restart и выберите нужную операцию!")

@bot.message_handler(commands=["start", "restart"])
def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    button_1 = types.KeyboardButton("Погода")
    button_2 = types.KeyboardButton("Курсы валют")
    markup.row(button_1, button_2)

    bot.send_message(message.chat.id, "Погода или курсы валют?", reply_markup=markup)
    bot.register_next_step_handler(message, req_check)

def req_check(message):
    if message.text == "Погода":
        markup = types.InlineKeyboardMarkup()
        button_1 = types.InlineKeyboardButton("Моква", callback_data="москва")
        button_2 = types.InlineKeyboardButton("Бишкек", callback_data="бишкек")
        button_3 = types.InlineKeyboardButton("Тюп", callback_data="тюп")
        markup.row(button_1, button_2, button_3)

        bot.reply_to(message, "Выберите город", reply_markup=markup)

    elif message.text == "Курсы валют":
        markup = types.InlineKeyboardMarkup()
        button_1 = types.InlineKeyboardButton("USD/RUB", callback_data="USD/RUB")
        button_2 = types.InlineKeyboardButton("USD/KGS", callback_data="USD/KGS")
        button_3 = types.InlineKeyboardButton("RUB/KGS", callback_data="RUB/KGS")
        markup.row(button_1, button_2, button_3)

        bot.reply_to(message, "Выберите валюты", reply_markup=markup)

    elif message.text == "Курсы валют":
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        button_1 = types.KeyboardButton("/restart")
        markup.row(button_1)
        bot.send_message(message.chat.id, "Что-то пошло не так)\nНажмите /restart", reply_markup=markup)
        bot.register_next_step_handler(message, start)

@bot.callback_query_handler(func=lambda callback: True)
def callback_message(callback):
    if callback.data in ("москва", "бишкек", "тюп"):
        response = requests.get(f"https://www.google.com/search?q={callback.data}+погода", headers=HEADERS)
        soup = BeautifulSoup(response.text, "html.parser")
        temperature = soup.find("span", class_="wob_t q8U8x").get_text()
        precipitation = soup.find("div", class_="wtsRwe").find_all("span")[0].get_text()
        weather = soup.find("div", class_="wob_dcp").get_text()
        bot.send_message(callback.message.chat.id, f"{callback.data.capitalize()}: {temperature}°C\n"
                                                   f"Вероятность осадков: {precipitation}\n\n"
                                                   f"{weather}\n\n"
                                                     f"Для обновления нажмите: /restart")

    elif callback.data in ("USD/RUB", "USD/KGS", "RUB/KGS"):
        response = requests.get(f"https://www.google.com/search?q=курс {callback.data.split('/')[0]} к {callback.data.split('/')[1]}", headers=HEADERS)
        soup = BeautifulSoup(response.text, "html.parser")
        exchange = soup.find("span", class_="DFlfde SwHCTb").get_text()
        bot.send_message(callback.message.chat.id, f"1 {callback.data.split('/')[0]} = {exchange} {callback.data.split('/')[1]}\n\n"
                                                   f" Для обновления нажмите: /restart")

    else:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        button_1 = types.KeyboardButton("/restart")
        markup.row(button_1)
        bot.send_message(callback.message.chat.id, "Что-то пошло не так)\nНажмите /restart", reply_markup=markup)
        bot.register_next_step_handler(callback.message, start)


bot.infinity_polling()

