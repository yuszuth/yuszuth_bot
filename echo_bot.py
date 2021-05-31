import os
import telebot
import database as db
import models
from sqlalchemy.orm import scoped_session
from collections import OrderedDict
import codecs

models.Base.metadata.create_all(bind=db.engine)
session = scoped_session(db.Session)

TOKEN = os.environ['TOKEN']

bot = telebot.TeleBot(TOKEN)


@bot.message_handler(commands=['start'])
def send_welcome(message):
    # print('start')
    bot.reply_to(message,
                 "Привет, я могу помочь тебе составить одно слово из нескольких!\nВведи свои слова и я выведу тебе "
                 "результат!")


@bot.message_handler(commands=['help'])
def send_help(message):
    # print('help')
    bot.reply_to(message,
                 'Данный бот был создан для того, чтобы помочь находить ответы для игры "Словарная арифметика".\nДля '
                 'того, чтобы получить ответ, введите несколько слов в одном сообщении без пробелов и знаков '
                 'препинания, отправьте боту.\nВводить нужно исключительно русские буквы, иначе бот выдаст ошибку.')


@bot.message_handler(func=lambda message: True)
def solve(message):
    d = dict()
    word = message.text
    word = word.lower()
    for i in word:
        if i in d.keys():
            d.update({i: d.get(i) + 1})
        else:
            d.update({i: 1})
    new_d = OrderedDict(sorted(d.items()))
    enc_word = ''

    russian_check = False
    r_a = codecs.open('russian_alphabet.txt', mode='r', encoding='utf-8').read()

    for i in new_d.keys():
        if i not in r_a:
            russian_check = True
            break
        enc_word += i * new_d.get(i)

    enc_word = enc_word.lower()

    if russian_check:
        bot.reply_to(message,
                     'Входные данные некорректны, пожалуйста проверьте их.\nЕсли вам требуется помощь, то введите '
                     'команду "/help".')

    elif enc_word in session.query(models.Words).filter_by(enc=enc_word) is not None:
        ans = session.query(models.Words).filter_by(enc=enc_word).first()
        bot.reply_to(message, ans.result)

    else:
        r_n = codecs.open('russian_nouns.txt', mode='r', encoding='utf-8').read()
        nouns = []

        right = 0
        d = dict()
        noun_k = ''
        for noun in r_n:
            if noun != '\n':
                if noun == '\r':
                    continue
                else:
                    noun_k += noun
                    if noun in d.keys():
                        d.update({noun: d.get(noun) + 1})
                    else:
                        d.update({noun: 1})
            else:
                right += 1
                new_d = OrderedDict(sorted(d.items()))
                enc_noun = ''
                for i in new_d.keys():
                    enc_noun += i * new_d.get(i)
                enc_noun = enc_noun.lower()
                nouns.append((noun_k, enc_noun))
                d = dict()
                noun_k = ''

        nouns.sort(key=lambda tup: tup[1])

        left = 0

        while left + 1 != right:
            mid = (left + right) >> 1
            if nouns[mid][1] > enc_word:
                right = mid
            else:
                left = mid

        if enc_word == nouns[left][1]:
            bot.reply_to(message, f"Ваше слово - {nouns[left][0]}")
            session.add(models.Words(enc=enc_word, result=nouns[left][0]))
            session.commit()

        else:
            bot.reply_to(message, "Приносим извинения, но мы не смогли найти слово, подходящее под данные критерии.")


bot.polling()
