import os
import telebot
import database as db
from collections import OrderedDict

models.Base.metadata.create_all(bind=db.engine)
session = scoped_session(db.Session)

TOKEN = os.environ['TOKEN']

bot = telebot.TeleBot(TOKEN)


@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message,
                 "Привет, я могу помочь тебе составить одно слово из нескольких!\nВведи свои слова и я выведу тебе "
                 "результат!") 


@bot.message_handler(commands=['help'])
def send_help(message):
    bot.reply_to(message,
                 'Данный бот был создан для того, чтобы помочь находить ответы для игры "Словарная арифметика".\nДля '
                 'того, чтобы получить ответ, введите несколько слов в одном сообщении без пробелов и знаков '
                 'препинания, отправьте боту.\n Вводить нужно исключительно русские буквы, иначе бот выдаст ошибку.')


@bot.message_handler(func=lambda message: True)
def solve(message):
    d = dict()
    word = message.text()
    for i in word:
        if i in d.keys():
            d.update({i: d.get(i) + 1})
        else:
            d.update({i: 1})
    new_d = OrderedDict(sorted(d.items()))
    enc_word = ''

    russian_check = False
    r_a = open('russian_alphabet.txt', mode='r').read()

    for i in new_d.keys():
        if i not in r_a:
            russian_check = True
            break
        enc_word += i * new_d.get(i)

    enc_noun = enc_word.lower()

    if russian_check:
        bot.reply_to(message,
                     'Входные данные некорректны, пожалуйста проверьте их.\nЕсли вам требуется помощь, то введите '
                     'команду "/help".')

    elif enc_noun in session.query(models.Words).filter_by(enc=enc_noun) is not None:
        ans = session.query(models.Words).filter_by(enc=enc_noun).first()
        bot.reply_to(message, ans.result)

    else:
        r_n = open('russian_nouns.txt', mode=r).read()
        nouns = []

        for noun in r_n:
            d = dict()
            for i in noun:
                if i in d.keys():
                    d.update({i: d.get(i) + 1})
                else:
                    d.update({i: 1})
            new_d = OrderedDict(sorted(d.items()))
            enc_noun = ''
            for i in new_d.keys():
                enc_noun += i * new_d.get(i)
            enc_noun = enc_noun.lower()
            nouns.append((noun, enc_noun))

        nouns.sort(key=lambda tup: tup[1])

        left = 0
        right = len(nouns)

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
