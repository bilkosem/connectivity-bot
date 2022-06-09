from telegram.ext.updater import Updater
from telegram.update import Update
from telegram.ext.callbackcontext import CallbackContext
from telegram.ext.commandhandler import CommandHandler
from telegram.ext.messagehandler import MessageHandler
from telegram.ext.filters import Filters
  
import sys
import json

class TelegramBot():
    updater = None
    chatId = None
    help_message = None

    @staticmethod
    def setToken(token):
        TelegramBot.updater = Updater(token,
                  use_context=True)
    @staticmethod
    def setChatId(chatId):
        TelegramBot.chatId = chatId

    @staticmethod
    def send_message(message):
        TelegramBot.updater.bot.send_message(TelegramBot.chatId, text=message)

    @staticmethod
    def add_handler(handler):
        #TelegramBot.updater.dispatcher.add_handler(handler)
        TelegramBot.updater.dispatcher.add_handler(handler)

    #@staticmethod
    def configure_help_message():
        commands = [cmd_handler.command[0] for cmd_handler in TelegramBot.updater.dispatcher.handlers[0] if type(cmd_handler) == CommandHandler]
        #help_message
        TelegramBot.add_handler(CommandHandler('help', TelegramBot.help))
        TelegramBot.add_handler(CommandHandler('method', TelegramBot.method))


    @staticmethod
    def help(update: Update, context: CallbackContext):
        update.message.reply_text("""Available Commands :-
        /youtube - To get the youtube URL
        /linkedin - To get the LinkedIn profile URL
        /gmail - To get gmail URL
        /geeks - To get the GeeksforGeeks URL""")

    @staticmethod
    def method(update: Update, context: CallbackContext):
        update.message.reply_text(
            "methoddddddd")

def start(update: Update, context: CallbackContext):
    update.message.reply_text(
        "Hello sir, Welcome to the Bot.Please write\
        /help to see the commands available.")


def unknown(update: Update, context: CallbackContext):
    update.message.reply_text(
        "Sorry '%s' is not a valid command" % update.message.text)


def unknown_text(update: Update, context: CallbackContext):
    update.message.reply_text(
        "Sorry I can't recognize you , you said '%s'" % update.message.text)

if __name__ == "__main__":
    f = open(str(sys.argv[1]),'r')
    config = json.load(f)

    TelegramBot.setToken(config['Telegram']['Token'])
    TelegramBot.setChatId(config['Telegram']['ChatId'])
    TelegramBot.add_handler(CommandHandler('start', start))

    TelegramBot.add_handler(MessageHandler(Filters.text, unknown))
    TelegramBot.add_handler(MessageHandler(
        Filters.command, unknown))  # Filters out unknown commands
    
    # Filters out unknown messages.
    TelegramBot.add_handler(MessageHandler(Filters.text, unknown_text))

    # How to get chatId: https://api.telegram.org/bot<YourBOTToken>/getUpdates
    TelegramBot.send_message("my dummy message")
    TelegramBot.configure_help_message() # TODO: help message
    commandss = [cmd_handler.command[0] for cmd_handler in TelegramBot.updater.dispatcher.handlers[0] if type(cmd_handler) == CommandHandler]
    print(commandss)
    TelegramBot.updater.start_polling()