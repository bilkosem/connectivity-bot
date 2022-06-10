from dataclasses import dataclass
from textwrap import indent
from matplotlib.pyplot import title
from sqlalchemy import false, true
from telegram.ext.updater import Updater
from telegram.update import Update
from telegram.ext.callbackcontext import CallbackContext
from telegram.ext.commandhandler import CommandHandler
from telegram.ext.messagehandler import MessageHandler
from telegram.ext.filters import Filters
  
import sys
import json

@dataclass
class TelegramMessageFormat():
    header: str = 'header'
    tailer: str = ''
    line_indent: str = '\n        '
    line_format: str = ''
    constant_message: None = None

    def build_from_dict(self, data) -> str:
        body = ''
        for key, pair in data.items():
            line = self.line_indent + self.line_format.format(key, pair)
            body += line
        return body 

    def build_from_list(self, data) -> str:
        body = ''
        for datum in data:
            line = self.line_indent + self.line_format.format(datum)
            body += line
        return body

    def build(self, data, is_constant=false) -> str:
        message = self.header
        if type(data) == dict:
            message += self.build_from_dict(data)
        elif type(data) == list:
            message += self.build_from_list(data)
        message += self.tailer

        # If message is constant, store it to be used
        if is_constant:
            self.constant_message = message

        return message


class TelegramBot():
    updater = None
    chatId = None
    help_message = None
    command_desc = {}
    telegram_formats = {}

    @staticmethod
    def setToken(token):
        TelegramBot.updater = Updater(token,
                  use_context=True)
    @staticmethod
    def setChatId(chatId):
        TelegramBot.chatId = chatId

    @staticmethod
    def send_raw_message(message):
        # Send the message if updater and chatId exist
        if TelegramBot.updater != None and TelegramBot.chatId != None:
            TelegramBot.updater.bot.send_message(TelegramBot.chatId, text=message)
        return message

    @staticmethod
    def send_formatted_message(format, data=[]):
        message = ''
        if message := TelegramBot.telegram_formats[format].constant_message:
            pass
        else:
            message = TelegramBot.telegram_formats[format].build(data)
        return TelegramBot.send_raw_message(message)

    @staticmethod
    def add_format(format_name, telegram_format, constant_data=None):
        if constant_data != None:
            telegram_format.build(constant_data, true)
        TelegramBot.telegram_formats[format_name] = telegram_format

    @staticmethod
    def add_handler(handler, description = ""):
        TelegramBot.updater.dispatcher.add_handler(handler)
        if type(handler) == CommandHandler:
            TelegramBot.command_desc[handler.command[0]] = description

    @staticmethod
    def help(update: Update, context: CallbackContext):
        message = 'Available Commands:\n'
        for command, desc in TelegramBot.command_desc.items():
            message += f'        /{command}: {TelegramBot.command_desc.get(command, "")}\n'
        update.message.reply_text(message)


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
    TelegramBot.add_handler(CommandHandler('start', start), description="start desc")
    TelegramBot.add_handler(CommandHandler('help', TelegramBot.help), description="")

    TelegramBot.add_handler(MessageHandler(Filters.text, unknown))
    TelegramBot.add_handler(MessageHandler(
        Filters.command, unknown))  # Filters out unknown commands
    
    # Filters out unknown messages.
    TelegramBot.add_handler(MessageHandler(Filters.text, unknown_text))

    # How to get chatId: https://api.telegram.org/bot<YourBOTToken>/getUpdates
    TelegramBot.send_raw_message("dummy message")

    format = TelegramMessageFormat('Header','\ntailer','\n        ','/{}: {}')
    TelegramBot.add_format('help', format, constant_data=TelegramBot.command_desc)
    TelegramBot.send_formatted_message('help')

    commandss = [cmd_handler.command[0] for cmd_handler in TelegramBot.updater.dispatcher.handlers[0] if type(cmd_handler) == CommandHandler]
    TelegramBot.updater.start_polling()
    print("after start polling")
    TelegramBot.updater.idle()
    print("after idle")
    # TODO: PoC of error logging to Telegram