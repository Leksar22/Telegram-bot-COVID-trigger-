from collections import defaultdict
from telegram import Bot, Update
from telegram.error import BadRequest
from telegram.ext import Updater, CommandHandler, Filters, MessageHandler, CallbackContext


TOKEN = '2136138549:AAFUlQLFBkh4tB1I6Ifkml9veLvzGjdu6mY'


def is_bad(text: str) -> bool:
    for word in bad_list:
        if word in text.lower():
            return True
    else:
        return False


def help(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('Вот мои команды:\n/help - список доступных команд,\n/stats - пользователи, упомяновшие о COVID-19', quote=True)


def publish(bot, update):
    str_msg = ' '.join(update.args)
    print("Message from tlg: ", str_msg)


def echo(update: Update, context: CallbackContext) -> None:
    global stat_dict
    if is_bad(update.message.text):
        chat_id = update.effective_message.chat.title
        user_name = update.effective_message.from_user.name
        if isinstance(chat_id, type(None)):
            chat_id = "Чат-бот, ID: " + str(update.effective_message.chat.id)
        stat_dict[chat_id][user_name.replace('@', '')] +=  1
        update.message.reply_text('Данная информация может быть недостоверна', quote=True)


def stats(update: Update, context: CallbackContext) -> None:
    chat_id = str(update.effective_message.chat_id)
    temp = ''
    if update.effective_message.chat.type == 'private':  # private message to bot
        for i in stat_dict.keys():
            temp += i + ':\n'
            for key, val in stat_dict[i].items():
                temp += key + ': ' + str(val) + '\n'
            temp += '\n\n'      
    else:
        for key, val in sorted(stat_dict[chat_id].items(), key = lambda p: -p[1]):
            print(i)
            temp += key + ': ' + str(val) + '\n'

    try:
        update.message.reply_text(temp)
    except BadRequest:
        update.message.reply_text("Данных нет")
    

if __name__ == "__main__":
    stat_dict = defaultdict(lambda: defaultdict(int))
    with open("key_words.txt", 'r', encoding='utf-8') as f:
        bad_list = f.read().split()

    bot = Bot(token=TOKEN)
    updater = Updater(token=TOKEN, use_context=True)

    publish_handler = CommandHandler('publish', publish)
    help_handler = CommandHandler('help', help)
    stat_handler = CommandHandler('stats', stats)
    
    updater.dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, echo))
    updater.dispatcher.add_handler(publish_handler)
    updater.dispatcher.add_handler(help_handler)
    updater.dispatcher.add_handler(stat_handler)

    
    updater.start_polling()

