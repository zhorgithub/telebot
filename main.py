from typing import Text
import telebot
from telebot.types import KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove
import psycopg2

conn = psycopg2.connect(
    host="localhost",
    database="Telebot",
    user="postgres",
    password="postgressa")

# cur = conn.cursor()
# query = 'SELECT * from "Users"'
# cur.execute(query)
# res = cur.fetchall()
# print(res)
# conn.commit()
# cur.close()


bot = telebot.TeleBot(token='1974780707:AAGOs3QbWvuG0R-6s2vld2blTprt0MEd9sk')


@bot.message_handler(commands=['start'])
def start(message):
    user_id = str(message.from_user.id)
    cur = conn.cursor()
    query = 'Select * from "usp_auth"(%s)'
    cur.execute(query, (user_id,))
    res = cur.fetchall()
    conn.commit()
    cur.close()

    if (res[0][0] == True):
        sendOrder(message)
    else:
        msg = bot.send_message(
            message.chat.id, 'Type your key for activation')
        bot.register_next_step_handler(msg, activate)


def activate(message):

    user_id = message.from_user.id
    key = message.text

    cur = conn.cursor()
    query = 'Select * from "usp_activateDriver"(%s, %s)'
    cur.execute(query, (user_id, key))
    res = cur.fetchall()
    conn.commit()
    cur.close()

    if (res[0][0] == True):
        bot.send_message(message.chat.id, 'You are successfully registered')
        sendOrder(message)

    else:
        msg = bot.send_message(
            message.chat.id, 'Key was wrong. Try again')
        bot.register_next_step_handler(msg, activate)


def accepted(message, orderId):
    # if(message.text != 'Yes' or message.text != 'No'):
    #     return
    if (message.text == 'Yes'):
        msg = bot.send_message(message.chat.id, "Type the price",
                               reply_markup=ReplyKeyboardRemove())
        bot.register_next_step_handler(msg, lambda m: setPrice(m, orderId))


def setPrice(message, orderId):

    user_id = str(message.from_user.id)
    price = message.text
    if(message.text.isdecimal() == True):
        cur = conn.cursor()
        query = 'Select * from "usp_addPriceSuggest"(%s, %s, %s)'
        cur.execute(query, (user_id, orderId, price))
        res = cur.fetchall()
        conn.commit()
        cur.close()

        if(res[0][0] == True):
            bot.send_message(
                message.chat.id, "Thank you. Price accepted. Please wait for the next order.")
    else:
        msg = bot.send_message(message.chat.id, "Price should be numeric. Please, type only numbers",
                               reply_markup=ReplyKeyboardRemove())
        bot.register_next_step_handler(msg, lambda m: setPrice(m, orderId))


def sendOrder(message):

    # get order
    cur = conn.cursor()
    query = 'Select * from "usp_getActiveOrder"()'
    cur.execute(query)
    res = cur.fetchall()
    conn.commit()
    cur.close()

    if (len(res) != 0):

        b1 = KeyboardButton('Yes')
        b2 = KeyboardButton('No')

        reply = ReplyKeyboardMarkup(
            one_time_keyboard=True, resize_keyboard=True)
        reply.add(b1)
        reply.add(b2)
        respMess = 'We have a new order. Details: \n Date: ' + \
            res[0][1].strftime('%m/%d/%Y') + '\n' + ' StartPoint: ' + res[0][2] + '\n' + ' EndPoint: ' + \
            res[0][3] + '\n' + ' Weight: ' + \
            str(res[0][4]) + '\n' + ' Will you accept it?'
        msg = bot.send_message(message.chat.id, respMess, reply_markup=reply)
        bot.register_next_step_handler(msg, lambda m: accepted(m, res[0][0]))
    else:
        msg = bot.send_message(message.chat.id, "There is no active orders")


# @bot.message_handler(content_types=['contact'])
# def contact_handler(message):
#     print(message.contact.phone_number)


bot.polling()
