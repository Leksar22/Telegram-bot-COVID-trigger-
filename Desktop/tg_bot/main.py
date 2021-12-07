from collections import defaultdict
from telegram import Bot, Update
from telegram.error import BadRequest
from telegram.ext import Updater, CommandHandler, Filters, MessageHandler, CallbackContext


TOKEN = '2136138549:AAFUlQLFBkh4tB1I6Ifkml9veLvzGjdu6mY'

##логи
##import logging
##logging.basicConfig(format='%(levelname)s - %(message)s', level=logging.DEBUG)
##logger = logging.getLogger(__name__)


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
            chat_id = "Чат-бот/ID " + str(update.effective_message.chat.id)
        stat_dict[chat_id][user_name.replace('@', '')] +=  1
        update.message.reply_text('Данная информация может быть недостоверна', quote=True)


def stats(update: Update, context: CallbackContext) -> None:
    temp = ''
    if update.effective_message.chat.type == 'private':  # private message to bot
        for group in sorted(stat_dict.keys()):
            temp += group + ':\n'
            for name, val in sorted(stat_dict[group].items(), key = lambda p: -p[1]):
                temp += '\U0000221F' + name + ': ' + str(val) + '\n'
            temp += '\n'
    else:
        chat_name = update.effective_message.chat.title
        for name, val in sorted(stat_dict[chat_name].items(), key = lambda p: -p[1]):
            temp += '\U0000221F' + name + ': ' + str(val) + '\n'

    try:
        update.message.reply_text(temp)
    except BadRequest:
        update.message.reply_text("Данных нет")


def track_chats(update: Update, context: CallbackContext) -> None:
    global stat_dict
    if update.effective_message.left_chat_member['is_bot'] and update.effective_message.left_chat_member['id'] == bot.id:
        chat_name = update.effective_chat.title
        print('Удалена статистика по чату', chat_name)
        del stat_dict[chat_name]


if __name__ == "__main__":
    stat_dict = defaultdict(lambda: defaultdict(int))
    with open("key_words.txt", 'r', encoding='utf-8') as f:
        bad_list = f.read().split()

    bot = Bot(token=TOKEN)
    updater = Updater(token=TOKEN, use_context=True)

    publish_handler = CommandHandler('publish', publish)
    help_handler = CommandHandler('help', help)
    stat_handler = CommandHandler('stats', stats)

    updater.dispatcher.add_handler(publish_handler)
    updater.dispatcher.add_handler(help_handler)
    updater.dispatcher.add_handler(stat_handler)

    updater.dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, echo))
    updater.dispatcher.add_handler(MessageHandler(Filters.status_update.left_chat_member, track_chats))

    updater.start_polling()

