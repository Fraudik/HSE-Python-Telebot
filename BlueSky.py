import telebot
from telebot import types
import requests
import random
# 'game' остлеживает, играет ли сейчас пользовтаель, и если да, то во что
# остальные поля этого словаря относятся к игре "Кости" и отслеживают внутриигровые механики
example = {'game': '',
           'player_cash': 100,
           'bot_cash': 100,
           'dice': ''}
# словарь для статусов всех игроков, содержит данные в формате: id пользователя -- словарь в формате 'example'
statuses = {}
# набор возможных костей, вместе с диапазонами их бросков
dices_values = {'один шестигранник': range(1, 7),
                'два шестигранника': range(2, 13),
                'один восьмигранник': range(1, 9),
                'два восьмигранника': range(2, 17),
                'один двадцатигранник': range(1, 21)}
token = '2051717168:AAEdAJ_R9JggheaYe3KKMZV1cDMdXRCrFME'
bot = telebot.TeleBot(token)
# *в сообщении, содержащем несколько ключевых слов, считается только первое


# функция "приветствия" с двумя кнопками (котики и игры)
def greet(message):
    global statuses, example
    # если пользователя нет в базе, добавляем его
    if message.from_user.id not in statuses:
        statuses[message.from_user.id] = example.copy()
    markup = types.InlineKeyboardMarkup()
    cats = types.InlineKeyboardButton('котики', callback_data='котики')
    games = types.InlineKeyboardButton('игры', callback_data='игры')
    markup.row(cats, games)
    bot.send_message(message.chat.id, f'Приветствую, {message.from_user.last_name} {message.from_user.first_name}! '
                                      f'\nМеня зовут BlueSky, и я умею делать две вещи:'
                                      f"\n \t 1) показывать котиков -- комманда '/котики' ;"
                                      f"\n \t 2) играть в игры -- команда  '/игры' ."
                                      f'\nВы можете выбрать одно из двух действий либо написав '
                                      f'в чат соответствующую команду, '
                                      f'либо нажав на одну из кнопок ниже.', reply_markup=markup)


# если пользователь отправил одну из команд, относящихся к функции "приветствия", то вызывется эта функция
@bot.message_handler(commands=['start', 'begin', 'старт', 'начать', 'начало', 'приветствие', 'привет'])
def command_greet(message):
    greet(message)


# если пользователь нажал кнопку, относящуюся к функции "приветствия", то вызывется эта функция
@bot.callback_query_handler(func=lambda call: call.data == 'приветствие')
def call_greet(call):
    greet(call.message)


# если пользователь отпарвил одно из ключевых слов, относящихся к функции "приветствия", то вызывется эта функция
@bot.message_handler(func=lambda message: message.text in ('start', 'begin', 'старт',
                                                           'начать', 'начало', 'приветствие', 'привет'))
def message_greet(message):
    greet(message)


# API для получения случайной фотографии котика или котиков
def get_cat():
    return requests.get('https://aws.random.cat/meow').json()['file']


# если пользователь нажал кнопку, относящуюся к получении фотографии котика или котиков, то вызывется эта функция
@bot.callback_query_handler(func=lambda call: call.data == 'котики')
def call_cats(call):
    bot.send_photo(call.message.chat.id, get_cat())


# если пользователь отправил команду, относящуюся к получении фотографии котика или котиков, то вызывется эта функция
@bot.message_handler(commands=['котики'])
def command_cats(message):
    bot.send_photo(message.chat.id, get_cat())


# если пользователь отправил сообщение, содержащее ключевое слово, 
# относящееся к получении фотографии котика или котиков, то вызывется эта функция
@bot.message_handler(func=lambda message: 'котики' in message.text and message.text[0] != '/')
def message_cats(message):
    bot.send_message(message.chat.id, "Я бот простой. Слышу 'котики' -- кидаю фото с котиками.")
    bot.send_photo(message.chat.id, get_cat())
    
    
# функция "помощи" (выводит все 4 глобальные команды (кроме "помощи") и кнопки к ним)
def send_help_message(message, addition=''):
    markup = types.InlineKeyboardMarkup()
    cats = types.InlineKeyboardButton('котики', callback_data='котики')
    games = types.InlineKeyboardButton('игры', callback_data='игры')
    hello = types.InlineKeyboardButton('приветствие', callback_data='приветствие')
    stop = types.InlineKeyboardButton('стоп', callback_data='стоп')
    markup.row(cats, games)
    markup.row(hello)
    markup.row(stop)
    bot.send_message(message.chat.id, addition + "У меня есть следующие команды: \n"
                                                 "\t /котики \n"
                                                 "\t /игры \n"
                                                 "\t /приветствие \n"
                                                 "\t /стоп", reply_markup=markup)


# если пользователь нажал кнопку, относящуюся к функции "помощи", то вызывется эта функция
@bot.callback_query_handler(func=lambda call: call.data == 'помощь')
def call_for_help(call):
    send_help_message(call.message)


# если пользователь отправил команду, относящуюся к функции "помощи", то вызывется эта функция
@bot.message_handler(commands=['помощь', 'help'])
def command_for_help(message):
    send_help_message(message)


# если пользователь отправил ключевое слово, относящеся к функции "помощи", то вызывется эта функция
@bot.message_handler(func=lambda message: 'помощь' in message.text)
def message_for_help(message):
    send_help_message(message, 'Я услышал просьбу о помощи!\n')


# сообщение в формате "Вы уверены?" с двумя кнопками: "Да" и "Нет"
# при нажатии одной из кнопок сообщение удалится

# принимает вопрос, который нужно задать пользователю, и сигнал, который нужно послать при нажатии кнопки "Да"
def check_intentions(message, question, callback):
    markup = types.InlineKeyboardMarkup()
    agree = types.InlineKeyboardButton('Да', callback_data=callback)
    refuse = types.InlineKeyboardButton('Нет', callback_data='отказ')
    markup.row(agree, refuse)
    bot.send_message(message.chat.id, question, reply_markup=markup)


# если после вызова функции "check_intentions" пользователь нажал кнопку "Нет", то вызывется эта функция
@bot.callback_query_handler(func=lambda call: call.data == 'отказ')
def decline(call):
    bot.send_message(call.message.chat.id, "Понял, принял, удалил.")
    bot.delete_message(call.message.chat.id, call.message.message_id)


# выводит все доступные игры (функция "игры")
def send_games(message):
    markup = types.InlineKeyboardMarkup()
    dices = types.InlineKeyboardButton('кости', callback_data='кости')
    markup.row(dices)
    bot.send_message(message.chat.id, "На данный момент у меня есть только одна игра: ",
                     reply_markup=markup)


# если пользователь нажал кнопку, относящуюся к функции "игры", то вызывется эта функция
@bot.callback_query_handler(func=lambda call: 'игры' in call.data)
def call_games(call):
    if call.data == 'подтверждение игры':
        bot.delete_message(call.message.chat.id, call.message.message_id)
    send_games(call.message)


# если пользователь отправил команду, относящуюся к функции "игры", то вызывется эта функция
@bot.message_handler(commands=['игры'])
def command_games(message):
    send_games(message)


# если пользователь отправил ключевое слово, относящееся к функции "игры", то вызывется эта функция
@bot.message_handler(func=lambda message: 'игры' in message.text and message.text[0] != '/')
def message_games(message):
    check_intentions(message, "Желаете сыграть?", 'подтверждение игры')


# функция игры "Кости", объясняет правила и меняет статус внутриигровых элементов для этого пользователя
def play_dices(message):
    global statuses
    # если пользователя нет в базе, добавляем его
    if message.from_user.id not in statuses:
        statuses[message.from_user.id] = example.copy()
    # если пользователь уже играет в какую-то игру, то не даем ему начать новую без остановки старой
    if statuses[message.from_user.id]['game'] != '':
        bot.send_message(message.chat.id, "Вы уже играете в какую-то игру."
                                          "\nЕсли вы хотите остановить игру, отправьте команду \n '/стоп'.")
        return
    bot.send_message(message.chat.id, f' Здесь правила просты. И у вас, и у бота'
                                      f' по 100 монет. Каждый раунд выбирается один случайный тип костей. Затем'
                                      f' вы делаете ставку от 1 до 20 монет на то, что число, которые вы выбросите'
                                      f' с помощью этих костей будет больше чем число, выброшенное ботом.'
                                      f"\nЕсли вы захотите остановить игру, отправьте команду \n '/стоп'.")
    statuses[message.from_user.id]['player_cash'] = 100
    statuses[message.from_user.id]['bot_cash'] = 100
    check_intentions(message, 'Начнём игру в кости?', callback='игра в кости')


# игра в "Кости" начинается, удаляется предыдущий вопрос (строка 182)
@bot.callback_query_handler(func=lambda call: call.data == 'игра в кости')
def call_dices(call):
    bot.delete_message(call.message.chat.id, call.message.message_id)
    dices_round(call)


# раунд игры в "Кости"
def dices_round(call):
    global statuses
    # условия выигрыша и проигрыша
    if statuses[call.message.from_user.id]['player_cash'] == 0:
        bot.send_message(call.message.chat.id, "К сожалению, вы проиграли. Мои соболезнования.")
        statuses[call.message.from_user.id]['game'] = ''
        return
    elif statuses[call.message.from_user.id]['bot_cash'] == 0:
        bot.send_message(call.message.chat.id, 'Поздравляю с победой! Это была хорошая игра.')
        statuses[call.message.from_user.id]['game'] = ''
        return
    # какая игра сейчас запущена у конкретного пользователя
    statuses[call.message.from_user.id]['game'] = 'dices'
    dice = random.choice([v for v in dices_values.keys()])
    # какая кость сейчас выбрана в текущем раунде у конкретного пользователя
    statuses[call.message.from_user.id]['dice'] = dice
    random.seed(random.randint(10 ** 10, 10 ** 20))
    markup = types.InlineKeyboardMarkup()
    bets = []
    # добавляем кнопки, являющимися ставками в игре.
    for bet in range(1, 20 + 1):
        # ставка не может быть больше
        if bet <= min(statuses[call.message.from_user.id]['player_cash'],
                      statuses[call.message.from_user.id]['bot_cash']):
            bets.append(types.InlineKeyboardButton(str(bet), callback_data=str(bet)))
            # кнопки располагаем по 5 (максимум) в ряд
            if bet % 5 == 0:
                markup.row(*bets)
                bets.clear()
    if len(bets) != 0:
        markup.row(*bets)
    bot.send_message(call.message.chat.id, f' В этом раунде вы бросаете {dice}.\nСделайте ставку'
                                           f' (от 1 до 20 монет, не больше количества '
                                           f'оставшихся у вас или бота монет).', reply_markup=markup)


# когда пользователь делает ставку в игре "Кости", вызывается эта функция
@bot.callback_query_handler(func=lambda call: call.data in map(lambda x: str(x), range(1, 21)))
def dices_round_calculate(call):
    global statuses
    bot.delete_message(call.message.chat.id, call.message.message_id)
    # если пользователь уже закончил игру с помощью функции 'стоп'
    # и хочет сделать ставку в уже завершенной игре
    if statuses[call.message.from_user.id]['game'] != 'dices':
        bot.send_message(call.message.chat.id, "Вы уже не играете в эту игру.")
        return
    # считаем результаты бросков пользователя и бота
    player_throw, bot_throw = [random.choice(dices_values[statuses[call.message.from_user.id]['dice']])
                               for _ in range(2)]
    # определяем выигравшего в этом раунде
    if player_throw > bot_throw:
        statuses[call.message.from_user.id]['player_cash'] += int(call.data)
        statuses[call.message.from_user.id]['bot_cash'] -= int(call.data)
    elif bot_throw > player_throw:
        statuses[call.message.from_user.id]['bot_cash'] += int(call.data)
        statuses[call.message.from_user.id]['player_cash'] -= int(call.data)
    # оповещаем пользователя о результатах раунда
    bot.send_message(call.message.chat.id, f'Вы выбросили {player_throw}, а бот {bot_throw}.\n'
                                           f'Ваших монет осталось - '
                                           f'{statuses[call.message.from_user.id]["player_cash"]}\n'
                                           f'Монет бота осталось - '
                                           f'{statuses[call.message.from_user.id]["bot_cash"]}')
    # начинаем новый раунд
    dices_round(call)


# если нажата кнопка, относящаяся к функции начала игры в "Кости", то вызывется эта функция
@bot.callback_query_handler(func=lambda call: 'кости' in call.data)
def call_dices(call):
    # если был задан вопрос формата "Вы уверены?", то после ответа удаляем его
    if call.data == 'подтверждение кости':
        bot.delete_message(call.message.chat.id, call.message.message_id)
    play_dices(call.message)


# если нажата кнопка, относящаяся к функции начала игры в "Кости", то вызывется эта функция
@bot.message_handler(func=lambda message: 'кости' in message.text and message.text[0] != '/')
def message_dices(message):
    check_intentions(message, "Желаете сыграть в кости?", 'подтверждение кости')


# функция досрочного прекращения текущей игры (функция "стоп")
def stop_games(message):
    global statuses
    # если пользователя нет в базе, добавляем его
    if message.from_user.id not in statuses:
        statuses[message.from_user.id] = example.copy()
    if statuses[message.from_user.id]['game'] == '':
        bot.send_message(message.chat.id, 'Активных игр не обнаружено.')
    else:
        statuses[message.from_user.id]['game'] = ''
        bot.send_message(message.chat.id, 'Игра была прекращена.')


# если нажата кнопка, относящаяся к функции "стоп", то вызывется эта функция
@bot.callback_query_handler(func=lambda call: 'стоп' == call.data)
def call_stop(call):
    stop_games(call.message)


# если отправлена команда или ключевое слово, относящиеся к функции "стоп", то вызывется эта функция
@bot.message_handler(func=lambda message: 'стоп' == message.text or '/стоп' == message.text)
def message_stop(message):
    stop_games(message)


# если была отправлена неизвестная команда или сообщение, не содержащее ключевых слов, то вызывется эта функция
@bot.message_handler()
def unknown_message(message):
    markup = types.InlineKeyboardMarkup()
    support = types.InlineKeyboardButton('помощь', callback_data='помощь')
    markup.row(support)
    if message.text[0] == '/':
        message_reaction = "Неизвестная команда.\n"
    else:
        message_reaction = "Я не понимаю :( \n"
    bot.send_message(message.chat.id, message_reaction
                     + "Посмотреть доступные действия можно с помощью команды '/помощь'.",
                     reply_markup=markup)


bot.polling()
