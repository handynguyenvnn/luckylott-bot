from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from telegram import ReplyKeyboardMarkup, ParseMode
import logging
import requests
import json
import random
import string
from datetime import datetime
import numpy as np

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

token_telegram = '1565616935:AAEJqVeMh72RPe5vgo4Be_NQOFrn2Pbi_AE'

backend_token = 'Token 5U^7lWMruu05P?Tp)zXCgy#Cmp97#SBx'
backend_endpoint = 'http://206.189.33.52:8080/api/telegram/'
cms_domain = "https://dashboard.luckylott.live"
homepage_domain = "https://luckylott.live"

main_keyboard = [["Balance", "Ticket"], ["Deposit", "LuckyLott Round"], ["Withdraw", "Tutorial"], ["Profile"]]
main_markup = ReplyKeyboardMarkup(main_keyboard, one_time_keyboard=True, resize_keyboard=True)

ticket_keyboard = [["Buy Ticket", "Your Ticket"], ["Dashboard"]]
ticket_markup = ReplyKeyboardMarkup(ticket_keyboard, one_time_keyboard=True, resize_keyboard=True)

ticket_type_keyboard = [["LuckyLott 2", "LuckyLott 3"], ["Jackpot", "Mini jackpot"], ["Dashboard"]]
ticket_type_markup = ReplyKeyboardMarkup(ticket_type_keyboard, one_time_keyboard=True, resize_keyboard=True)

pool_keyboard = [["USDT", "GES"], ["Dashboard"]]
pool_markup = ReplyKeyboardMarkup(pool_keyboard, one_time_keyboard=True, resize_keyboard=True)

main_menu_keyboard = [["Dashboard"]]
main_menu_markup = ReplyKeyboardMarkup(main_menu_keyboard, one_time_keyboard=True, resize_keyboard=True)

restart_menu_keyboard = [["Restart"]]
restart_menu_markup = ReplyKeyboardMarkup(restart_menu_keyboard, one_time_keyboard=True, resize_keyboard=True)

game_info_keyboard = [["The next round", "Your last round ticket"], ["Dashboard"]]
game_info_markup = ReplyKeyboardMarkup(game_info_keyboard, one_time_keyboard=True, resize_keyboard=True)

deposit_type_keyboard = [["USDT ERC-20", "USDT TRC-20"], ["GES"], ["Dashboard"]]
deposit_type_markup = ReplyKeyboardMarkup(deposit_type_keyboard, one_time_keyboard=True, resize_keyboard=True)

withdrawal_type_keyboard = [["USDT ERC-20", "USDT TRC-20"], ["GES"], ["Dashboard"]]
withdrawal_type_markup = ReplyKeyboardMarkup(withdrawal_type_keyboard, one_time_keyboard=True, resize_keyboard=True)

submit_withdrawal_keyboard = [["Confirm"], ["Dashboard"]]
submit_withdrawal_markup = ReplyKeyboardMarkup(submit_withdrawal_keyboard, one_time_keyboard=True, resize_keyboard=True)

setting_keyboard = [["History Transaction", "My Information"], ["Dashboard"]]
setting_markup = ReplyKeyboardMarkup(setting_keyboard, one_time_keyboard=True, resize_keyboard=True)

history_trans_keyboard = [["Deposit", "Withdraw"], ["Dashboard"]]
history_trans_markup = ReplyKeyboardMarkup(history_trans_keyboard, one_time_keyboard=True, resize_keyboard=True)

updater = Updater(token=token_telegram, use_context=True)

welcome_messsage = "Welcome to LuckyLott.\nThe World's Coin Lottery." \
                   "\nJoin our Community at t.me/LuckyLott_365"
error_message = "Something went wrong. Please try again later."

referral_code_message = "Please enter your sponsor's referral code to begin:"

welcome_sticker_id = "CAACAgUAAxkBAAIIzGAGaTDALQLIEKCQos0RQ2AW3VA6AAIFAAPZEIQxwKm20uw3DwkeBA"


def start(update, context):
    user_data = context.user_data
    user_data["previous_action"] = "start"
    ref_code_existed = check_ref_code(update, context)
    if ref_code_existed is False:
        context.bot.send_message(chat_id=update.message.chat_id, text=referral_code_message,
                                 parse_mode=ParseMode.HTML, disable_web_page_preview=True)
        return
    else:
        context.bot.send_sticker(chat_id=update.effective_chat.id, sticker=welcome_sticker_id)
        context.bot.send_message(chat_id=update.effective_chat.id, text=welcome_messsage, reply_markup=main_markup
                                 , disable_web_page_preview=True)
        return

def check_ref_code(update, context):
    user = update.message.from_user
    resp = send_get_request(backend_endpoint + "my-referral-code?teleId=" + str(user.id))

    if resp is None:
        return False

    resp_message = resp.__getitem__("message")

    if resp_message is not None:
        return False

    referee_code = resp.__getitem__("refereeCode")

    if referee_code is None or referee_code == "":
        return False
    else:
        return True

def echo(update, context):
    ref_code_existed = check_ref_code(update, context)
    if ref_code_existed is False:
        handle_submit_referee_code_dashboard(update, context)
        return
    text = update.message.text
    text_is_action = True
    if text == 'Ticket':
        handle_ticket(update, context)
    elif text == 'Buy Ticket':
        handle_buy_ticket(update, context)
    elif text == 'USDT' or text == 'GES':
        user_data = context.user_data
        if user_data is not None and "previous_action" in user_data.keys():
            if user_data["previous_action"] == "Deposit":
                handle_choose_deposit_type(update, context)
            elif user_data["previous_action"] == "Withdraw":
                handle_choose_withdrawal_type(update, context)
            else:
                handle_choose_pool(update, context)
        else:
            handle_choose_pool(update, context)
    elif text == 'LuckyLott 2' or text == 'LuckyLott 3' or text == 'Jackpot' or text == 'Mini jackpot':
        handle_enter_bet_number(update, context)
    elif text == 'Your Ticket':
        handle_get_running_ticket(update, context)
    elif text == 'Deposit':
        user_data = context.user_data
        if user_data is not None and "previous_action" in user_data.keys():
            if user_data["previous_action"] == "History Transaction":
                handle_deposit_history(update, context)
            else:
                handle_deposit(update, context)
        else:
            handle_deposit(update, context)
    elif text == 'USDT ERC-20' or text == 'USDT TRC-20' or text == 'GES':
        user_data = context.user_data
        if user_data is not None and "previous_action" in user_data.keys():
            if user_data["previous_action"] == "Deposit":
                handle_choose_deposit_type(update, context)
            elif user_data["previous_action"] == "Withdraw":
                handle_choose_withdrawal_type(update, context)
            else:
                handle_unknown(update, context)
        else:
            handle_unknown(update, context)
    elif text == 'Withdraw':
        user_data = context.user_data
        if user_data is not None and "previous_action" in user_data.keys():
            if user_data["previous_action"] == "History Transaction":
                handle_withdrawal_history(update, context)
            else:
                handle_create_withdrawal(update, context)
        else:
            handle_create_withdrawal(update, context)
    elif text == "Confirm":
        handle_submit_withdrawal(update, context)
    elif text == 'LuckyLott Round':
        handle_game_info(update, context)
    elif text == 'The next round':
        handle_get_draw_info(update, context, main_markup)
    elif text == 'Your last round ticket':
        handle_get_last_draw_ticket(update, context)
    elif text == 'Balance':
        handle_get_my_balance(update, context, main_markup)
    elif text == 'Profile':
        handle_setting(update, context)
    elif text == 'Tutorial':
        handle_get_tutorial(update, context)
    elif text == 'History Transaction':
        handle_get_history_trans(update, context)
    elif text == 'Dashboard':
        handle_main_menu(update, context)
    elif text == 'My Information':
        handle_get_my_account(update, context)
    elif text == 'Restart':
        start(update, context)
    else:
        text_is_action = False
        handle_unknown(update, context)

    user_data = context.user_data
    if text_is_action:
        user_data["previous_action"] = text


def handle_main_menu(update, context):
    context.bot.send_message(chat_id=update.message.chat_id, text=welcome_messsage, reply_markup=main_markup
                             , parse_mode=ParseMode.HTML, disable_web_page_preview=True)
    user_data = context.user_data
    if "bet_data" in user_data.keys():
        del user_data["bet_data"]
    if "withdrawal_data" in user_data.keys():
        del user_data["withdrawal_data"]

def handle_ticket(update, context):
    user_data = context.user_data
    message = "Please choose:"
    context.bot.send_message(chat_id=update.message.chat_id, text=message, reply_markup=ticket_markup
                             , parse_mode=ParseMode.HTML, disable_web_page_preview=True)

def handle_buy_ticket(update, context):
    handle_get_draw_info(update, context, None)
    handle_get_my_balance(update, context, pool_markup)
    user_data = context.user_data
    if "server_error" in user_data.keys() and user_data["server_error"] is True:
        return

    message = "Please choose type of ticket:"
    context.bot.send_message(chat_id=update.message.chat_id, text=message, reply_markup=pool_markup
                             , parse_mode=ParseMode.HTML, disable_web_page_preview=True)

def handle_choose_pool(update, context):
    text = update.message.text
    user_data = context.user_data
    if "previous_action" not in user_data.keys() or user_data["previous_action"] != "Buy Ticket":
        handle_unknown(update, context)
        return

    text = update.message.text
    user_data = context.user_data

    pool_type = ""
    if text == "USDT":
        pool_type = "USDT_10"
    elif text == "GES":
        pool_type = "GES_10"

    resp = send_get_request(backend_endpoint + "game-info?poolType=" + pool_type)

    if resp is None:
        context.bot.send_message(chat_id=update.message.chat_id, text=error_message, reply_markup=main_markup
                                 , parse_mode=ParseMode.HTML, disable_web_page_preview=True)
        return

    resp_message = resp.__getitem__("message")

    if resp_message is not None and resp_message == "PLAYER_NOT_FOUND":
        start(update, context)
        return
    elif resp_message is not None:
        context.bot.send_message(chat_id=update.message.chat_id, text=resp_message, reply_markup=main_markup
                                 , parse_mode=ParseMode.HTML, disable_web_page_preview=True)
        return

    game = resp.__getitem__("data")

    game_id = game.__getitem__("id")
    game_code = game.__getitem__("gameCode")
    if game_code is None:
        game_code = ""
    pool_balance = str(game.__getitem__("poolBalance"))
    draw_date = game.__getitem__("drawDate")
    draw_date = convert_date_time(draw_date)
    close_date = game.__getitem__("closeDate")
    close_date = convert_date_time(close_date)

    message = game_code + '\nTotal pool value: ' + pool_balance + ' ' + text + '\nNext round of LuckyLott\n' + \
              draw_date + '\nRound closed date\n' + close_date

    context.bot.send_message(chat_id=update.message.chat_id, text=message, reply_markup=main_menu_markup
                             , parse_mode=ParseMode.HTML, disable_web_page_preview=True)

    bet_data = {
        'pool_type': pool_type,
        'game_id': game_id
    }
    user_data = context.user_data
    user_data["bet_data"] = bet_data

    message = "Please select the type of ticket you want to buy:"
    context.bot.send_message(chat_id=update.message.chat_id, text=message, reply_markup=ticket_type_markup
                             , parse_mode=ParseMode.HTML, disable_web_page_preview=True)


def handle_enter_bet_number(update, context):
    text = update.message.text
    user_data = context.user_data
    if "bet_data" not in user_data.keys():
        handle_unknown(update, context)
        return

    bet_type = ""
    if text == 'LuckyLott 2':
        bet_type = "NUM_2"
    elif text == 'LuckyLott 3':
        bet_type = "NUM_3"
    elif text == 'Jackpot':
        bet_type = "NUM_4"
    elif text == 'Mini jackpot':
        bet_type = "NUM_4_RAND"

    bet_data = user_data["bet_data"]
    bet_data["bet_type"] = bet_type
    user_data["bet_data"] = bet_data
    message = "Please enter your lucky number:"
    context.bot.send_message(chat_id=update.message.chat_id, text=message, reply_markup=main_menu_markup
                             , parse_mode=ParseMode.HTML, disable_web_page_preview=True)


def handle_submit_bet(update, context):
    message = "Please enter the correct lucky number"
    text = update.message.text
    user_data = context.user_data
    if "bet_data" not in user_data.keys():
        return
    bet_data = user_data["bet_data"]
    if "bet_type" not in bet_data.keys():
        return
    if "pool_type" not in bet_data.keys():
        return
    bet_type = bet_data["bet_type"]
    pool_type = bet_data["pool_type"]
    game_id = int(bet_data["game_id"])
    if bet_type == "NUM_2":
        if len(text) == 2 and text.isnumeric():
            send_bet_data(update, context, text, bet_type, pool_type, game_id)
            return
        else:
            message = "Note: Enter 2 numbers, please"
            context.bot.send_message(chat_id=update.message.chat_id, text=message, reply_markup=main_menu_markup
                                     , parse_mode=ParseMode.HTML, disable_web_page_preview=True)
            return
    elif bet_type == "NUM_3":
        if len(text) == 3 and text.isnumeric():
            send_bet_data(update, context, text, bet_type, pool_type, game_id)
            return
        else:
            message = "Note: Enter 3 numbers, please"
            context.bot.send_message(chat_id=update.message.chat_id, text=message, reply_markup=main_menu_markup
                                     , parse_mode=ParseMode.HTML, disable_web_page_preview=True)
            return
    elif bet_type == "NUM_4" or bet_type == "NUM_4_RAND":
        if len(text) == 4 and text.isnumeric():
            send_bet_data(update, context, text, bet_type, pool_type, game_id)
            return
        else:
            message = "Note: Enter 4 numbers, please"
            context.bot.send_message(chat_id=update.message.chat_id, text=message, reply_markup=main_menu_markup
                                     , parse_mode=ParseMode.HTML, disable_web_page_preview=True)
            return



def send_bet_data(update, context, bet_number, bet_type, pool_type, game_id):
    user = update.message.from_user
    user_data = context.user_data
    if "bet_data" not in user_data.keys():
        handle_unknown(update, context)
        return
    payload = {
        "teleId": str(user.id),
        "betNumber": bet_number,
        "betType": bet_type,
        "poolType": pool_type,
        "gameId": game_id
    }
    user_data = context.user_data
    del user_data["bet_data"]

    resp = send_post_request(backend_endpoint + "player-bet", json.dumps(payload))

    if resp is None:
        context.bot.send_message(chat_id=update.message.chat_id, text=error_message, reply_markup=main_markup
                                 , parse_mode=ParseMode.HTML, disable_web_page_preview=True)
        return

    resp_message = resp.__getitem__("message")

    if resp_message is not None and resp_message == "PLAYER_NOT_FOUND":
        start(update, context)
        return
    elif resp_message is not None:
        user_data = context.user_data
        user_data["previous_action"] = "start"
        context.bot.send_message(chat_id=update.message.chat_id, text=resp_message, reply_markup=main_markup
                                 , parse_mode=ParseMode.HTML, disable_web_page_preview=True)
        return

    message = "Your lucky number have been submitted"
    context.bot.send_message(chat_id=update.message.chat_id, text=message, reply_markup=main_markup
                             , parse_mode=ParseMode.HTML, disable_web_page_preview=True)
    return


def handle_get_running_ticket(update, context):
    user = update.message.from_user

    resp = send_get_request(backend_endpoint + "running-tickets?teleId=" + str(user.id))

    if resp is None:
        context.bot.send_message(chat_id=update.message.chat_id, text=error_message, reply_markup=main_markup
                                 , parse_mode=ParseMode.HTML, disable_web_page_preview=True)
        return

    resp_message = resp.__getitem__("message")

    if resp_message is not None and resp_message == "PLAYER_NOT_FOUND":
        start(update, context)
        return
    elif resp_message is not None:
        user_data = context.user_data
        user_data["previous_action"] = "start"
        context.bot.send_message(chat_id=update.message.chat_id, text=resp_message, reply_markup=main_markup
                                 , parse_mode=ParseMode.HTML, disable_web_page_preview=True)
        return
    message = ""
    games = resp.__getitem__("data")
    if len(games) == 0:
        message = "You don't have any ticket yet"
    else:
        for game in games:
            game_code = game.__getitem__("gameCode")
            if game_code is None:
                game_code = ""
            message += game_code + "\nTotal pool value: " + \
                       str(game.__getitem__("poolBalance")) +  " " + game.__getitem__("poolName") + "\n" + \
                       "\nTime to publish results: \n" + convert_date_time(game.__getitem__("drawDate")) + \
                       "\nRound status: " + str(game.__getitem__("gameStatus")) + "\nYour lucky numbers:\n"
            for ticket in game.__getitem__("bets"):
                message += convert_bet_type(ticket.__getitem__("betType")) + ": " + \
                           ticket.__getitem__("betNumber") + "\n"

            message += "____________\n\n"

    context.bot.send_message(chat_id=update.message.chat_id, text=message, reply_markup=main_markup
                             , parse_mode=ParseMode.HTML, disable_web_page_preview=True)


def handle_get_ref_code(update, context):
    user = update.message.from_user
    resp = send_get_request(backend_endpoint + "my-referral-code?teleId=" + str(user.id))

    if resp is None:
        context.bot.send_message(chat_id=update.message.chat_id, text=error_message, reply_markup=main_markup
                                 , parse_mode=ParseMode.HTML, disable_web_page_preview=True)
        return

    resp_message = resp.__getitem__("message")

    if resp_message is not None and resp_message == "PLAYER_NOT_FOUND":
        start(update, context)
        return
    elif resp_message is not None:
        user_data = context.user_data
        user_data["previous_action"] = "start"
        context.bot.send_message(chat_id=update.message.chat_id, text=resp_message, reply_markup=main_markup
                                 , parse_mode=ParseMode.HTML, disable_web_page_preview=True)
        return

    ref_code = resp.__getitem__("refCode")
    if ref_code is None:
        ref_code = ""
    referee_code = resp.__getitem__("refereeCode")

    if referee_code is None or referee_code == "":
        context.bot.send_message(chat_id=update.message.chat_id, text=referral_code_message, reply_markup=main_menu_markup,
                                 parse_mode=ParseMode.HTML, disable_web_page_preview=True)
        return
    else:
        user_data = context.user_data
        user_data["previous_action"] = "start"
        message = "Your sponsor's referral code:"
        context.bot.send_message(chat_id=update.message.chat_id, text=message,
                                 parse_mode=ParseMode.HTML, disable_web_page_preview=True)
        context.bot.send_message(chat_id=update.message.chat_id, text=referee_code, reply_markup=main_markup,
                                 parse_mode=ParseMode.HTML, disable_web_page_preview=True)

def handle_get_my_balance(update, context, markup):
    user = update.message.from_user
    resp = send_get_request(backend_endpoint + "my-balance?teleId=" + str(user.id))
    user_data = context.user_data
    if resp is None:
        user_data["server_error"] = True
        context.bot.send_message(chat_id=update.message.chat_id, text=error_message, reply_markup=main_markup
                                 , parse_mode=ParseMode.HTML, disable_web_page_preview=True)
        return

    resp_message = resp.__getitem__("message")

    if resp_message is not None and resp_message == "PLAYER_NOT_FOUND":
        start(update, context)
        return
    elif resp_message is not None:
        user_data["server_error"] = True
        context.bot.send_message(chat_id=update.message.chat_id, text=resp_message, reply_markup=main_markup
                                 , parse_mode=ParseMode.HTML, disable_web_page_preview=True)
        return

    data = resp.__getitem__("data")

    message = ""
    if len(data) == 0:
        message = "You do not have enough money, please go to Deposit to get your LuckyLott's wallet address"
        user_data["server_error"] = True
        context.bot.send_message(chat_id=update.message.chat_id, text=message, reply_markup=main_markup
                                 , parse_mode=ParseMode.HTML, disable_web_page_preview=True)
        return
    else:
        message += "Your balance:\n\n"
        for item in data:
            message += str(item.__getitem__("balance")) + " " + item.__getitem__("tokenName") + "\n"

    if "server_error" in user_data.keys():
        del user_data["server_error"]

    if markup is None:
        context.bot.send_message(chat_id=update.message.chat_id, text=message
                                 , parse_mode=ParseMode.HTML, disable_web_page_preview=True)
    else:
        context.bot.send_message(chat_id=update.message.chat_id, text=message, reply_markup=markup
                             , parse_mode=ParseMode.HTML, disable_web_page_preview=True)

def handle_get_my_account(update, context):
    user = update.message.from_user
    resp = send_get_request(backend_endpoint + "my-account?teleId=" + str(user.id))
    if resp is None:
        context.bot.send_message(chat_id=update.effective_chat.id, text=error_message, reply_markup=main_markup
                                 , disable_web_page_preview=True)
        return

    resp_message = resp.__getitem__("message")

    if resp_message is not None and resp_message == "PLAYER_EXISTED":
        context.bot.send_sticker(chat_id=update.effective_chat.id, sticker=welcome_sticker_id)
        context.bot.send_message(chat_id=update.effective_chat.id, text=welcome_messsage, reply_markup=main_markup
                                 , disable_web_page_preview=True)
        return
    elif resp_message is not None:
        user_data = context.user_data
        user_data["previous_action"] = "start"
        context.bot.send_message(chat_id=update.message.chat_id, text=resp_message, reply_markup=main_markup
                                 , parse_mode=ParseMode.HTML, disable_web_page_preview=True)
        return

    data = resp.__getitem__("data")

    if data is None:
        return

    username = data.__getitem__("username")
    username = username if username is not None else ""

    password = data.__getitem__("password")
    password = password if password is not None else ""

    ref_code = data.__getitem__("refCode")
    ref_code = ref_code if ref_code is not None else ""

    security_code = data.__getitem__("securityCode")
    security_code = security_code if security_code is not None else ""
    ref_link = homepage_domain + "?refCode=" + ref_code
    message = "Your original account information is: \n\nUsername: " + username + \
              "\n\nPassword: " + password + " \n\n" + "Referral Code: " + ref_code + \
              "\nSecurity Code: " + security_code + \
              "\nPlease follow the link below to change your personal information:\n" + cms_domain
    context.bot.send_message(chat_id=update.effective_chat.id, text=message, reply_markup=main_markup
                             , disable_web_page_preview=True)



def handle_deposit(update, context):
    user = update.message.from_user
    resp = send_get_request(backend_endpoint + "my-balance?teleId=" + str(user.id))
    user_data = context.user_data
    if resp is None:
        user_data["server_error"] = True
        context.bot.send_message(chat_id=update.message.chat_id, text=error_message, reply_markup=main_markup
                                 , parse_mode=ParseMode.HTML, disable_web_page_preview=True)
        return

    resp_message = resp.__getitem__("message")

    if resp_message is not None and resp_message == "PLAYER_NOT_FOUND":
        start(update, context)
        return
    elif resp_message is not None:
        user_data["server_error"] = True
        context.bot.send_message(chat_id=update.message.chat_id, text=resp_message, reply_markup=main_markup
                                 , parse_mode=ParseMode.HTML, disable_web_page_preview=True)
        return

    data = resp.__getitem__("data")

    message = ""
    if len(data) == 0:
        message = "You do not have enough money, please go to Deposit to get your LuckyLott's wallet address"
        user_data["server_error"] = True
        context.bot.send_message(chat_id=update.message.chat_id, text=message, reply_markup=main_markup
                                 , parse_mode=ParseMode.HTML, disable_web_page_preview=True)
        return
    else:
        message += "Your balance:\n\n"
        for item in data:
            message += str(item.__getitem__("balance")) + " " + item.__getitem__("tokenName") + "\n"
    message += "\nPlease select the kind of crypto currency you want to deposit:"
    context.bot.send_message(chat_id=update.message.chat_id, text=message, reply_markup=deposit_type_markup
                             , parse_mode=ParseMode.HTML, disable_web_page_preview=True)


def handle_choose_deposit_type(update, context):
    user = update.message.from_user
    text = update.message.text
    message = ""
    token = ""
    network = ""
    if text == "USDT ERC-20":
        token = "USDT"
        network = "ERC"
        message += "Note: Minimum deposit amount: 100.0 USDT\n"
    elif text == "USDT TRC-20":
        token = "USDT"
        network = "TRC"
        message += "Note: Minimum deposit amount: 5.0 USDT\n"
    elif text == "GES":
        token = "GES"
        network = "ERC"
        message += "Note: Minimum deposit amount: 200.0 GES\n"
    resp = send_get_request(backend_endpoint + "register-address?network="+ network + "&token=" + token + "&teleId=" + str(user.id))

    if resp is None:
        context.bot.send_message(chat_id=update.message.chat_id, text=error_message, reply_markup=main_markup
                                 , parse_mode=ParseMode.HTML, disable_web_page_preview=True)
        return

    resp_message = resp.__getitem__("message")

    if resp_message is not None and resp_message == "PLAYER_NOT_FOUND":
        start(update, context)
        return
    elif resp_message is not None:
        user_data = context.user_data
        user_data["previous_action"] = "start"
        context.bot.send_message(chat_id=update.message.chat_id, text=resp_message, reply_markup=main_markup
                                 , parse_mode=ParseMode.HTML, disable_web_page_preview=True)
        return


    data = resp.__getitem__("data")
    address = data.__getitem__("address")
    message += "\nPlease deposit money to your LuckyLott's wallet address below:"
    context.bot.send_message(chat_id=update.message.chat_id, text=message, parse_mode=ParseMode.HTML, disable_web_page_preview=True)
    context.bot.send_message(chat_id=update.message.chat_id, text=address, reply_markup=main_markup,
                             parse_mode=ParseMode.HTML, disable_web_page_preview=True)
    return


def handle_choose_withdrawal_type(update, context):
    user = update.message.from_user
    text = update.message.text
    token = ""
    network = ""
    if text == "USDT ERC-20":
        token = "USDT"
        network = "ERC"
    elif text == "USDT TRC-20":
        token = "USDT"
        network = "TRC"
    elif text == "GES":
        token = "GES"
        network = "ERC"

    resp = send_get_request(backend_endpoint + "withdrawal-info?teleId=" + str(user.id) + "&token=" + token)

    if resp is None:
        context.bot.send_message(chat_id=update.message.chat_id, text=error_message, reply_markup=main_markup
                                 , parse_mode=ParseMode.HTML, disable_web_page_preview=True)
        return

    resp_message = resp.__getitem__("message")
    is_success = resp.__getitem__("success")

    if resp_message is not None and resp_message == "PLAYER_NOT_FOUND":
        start(update, context)
        return
    elif resp_message is not None:
        user_data = context.user_data
        user_data["previous_action"] = "start"
        context.bot.send_message(chat_id=update.message.chat_id, text=resp_message, reply_markup=main_markup
                                 , parse_mode=ParseMode.HTML, disable_web_page_preview=True)
        return
    elif not is_success:
        context.bot.send_message(chat_id=update.message.chat_id, text=error_message, reply_markup=main_markup
                                 , parse_mode=ParseMode.HTML, disable_web_page_preview=True)
        return

    fee = str(resp.__getitem__("withdrawalFee"))
    min = str(resp.__getitem__("withdrawalMin"))
    balance = str(resp.__getitem__("balance"))

    withdrawal_data = {
        'token': token,
        'network': network,
        'fee': fee,
        'min': min,
        'balance': balance
    }
    user_data = context.user_data
    user_data["withdrawal_data"] = withdrawal_data

    message = gen_withdrawal_info_message(fee, min, balance, token)

    context.bot.send_message(chat_id=update.message.chat_id, text=message, reply_markup=main_menu_markup,
                             parse_mode=ParseMode.HTML, disable_web_page_preview=True)
    return


def handle_key_withdraw_amount(update, context):
    user = update.message.from_user
    text = update.message.text
    user_data = context.user_data
    if "withdrawal_data" not in user_data.keys():
        return
    withdrawal_data = user_data["withdrawal_data"]
    if "token" not in withdrawal_data.keys() or "network" not in withdrawal_data.keys():
        return


    token = withdrawal_data["token"]
    balance = float(withdrawal_data["balance"])
    fee = float(withdrawal_data["fee"])
    min_amount = float(withdrawal_data["min"])
    withdrawal_message_error = "Warning:\n- Enter the correct number format (example: 100.25)\n" \
                               "- Minimum withdrawal amount is " + str(min_amount) + " " + token + \
                               "\n- Maximum withdrawal amount must not exceed the balance"

    if not text.isnumeric():
        context.bot.send_message(chat_id=update.message.chat_id, text=withdrawal_message_error, reply_markup=main_menu_markup
                                 , disable_web_page_preview=True)
        return

    amount = float(text)
    if balance < amount or amount < min_amount:
        context.bot.send_message(chat_id=update.message.chat_id, text=withdrawal_message_error, reply_markup=main_menu_markup
                                 , disable_web_page_preview=True)
        return

    withdrawal_data["actual_amount"] = str(amount - fee)
    withdrawal_data["amount"] = text

    message = 'Please enter your withdrawal address:'
    context.bot.send_message(chat_id=update.message.chat_id, text=message, reply_markup=main_menu_markup
                             , disable_web_page_preview=True)


def handle_key_withdraw_address(update, context):
    user = update.message.from_user
    text = update.message.text
    user_data = context.user_data
    if "withdrawal_data" not in user_data.keys():
        return
    withdrawal_data = user_data["withdrawal_data"]
    if "token" not in withdrawal_data.keys() or "network" not in withdrawal_data.keys():
        return

    withdrawal_data["address"] = text
    user_data["withdrawal_data"] = withdrawal_data
    handle_confirm_withdrawal(update, context)


def handle_confirm_withdrawal(update, context):
    user = update.message.from_user
    text = update.message.text
    user_data = context.user_data
    if "withdrawal_data" not in user_data.keys():
        return
    withdrawal_data = user_data["withdrawal_data"]
    if "token" not in withdrawal_data.keys() or "network" not in withdrawal_data.keys():
        return

    token = withdrawal_data["token"]
    network = withdrawal_data["network"]
    amount = withdrawal_data["amount"]
    address = withdrawal_data["address"]
    actual_amount = withdrawal_data["actual_amount"]
    fee = withdrawal_data["fee"]

    message = 'The amount you requested to withdraw: ' + amount + ' ' + token + '\nBlockchain network: ' + network + '\n' + \
              'Withdraw fee: ' + fee + ' ' + token + '\n' + \
              'You will get: ' + actual_amount + ' ' + token + '\n' + \
              'Your withdrawal address: ' + address + '\n' + \
              'Click confirm to submit your withdrawal request'

    context.bot.send_message(chat_id=update.message.chat_id, text=message, reply_markup=submit_withdrawal_markup
                             , disable_web_page_preview=True)


def handle_submit_withdrawal(update, context):
    user = update.message.from_user
    text = update.message.text
    user_data = context.user_data
    if "withdrawal_data" not in user_data.keys():
        return
    withdrawal_data = user_data["withdrawal_data"]
    if "token" not in withdrawal_data.keys() or "network" not in withdrawal_data.keys():
        return

    payload = {
        "token": withdrawal_data["token"],
        "network": withdrawal_data["network"],
        "amount": withdrawal_data["amount"],
        "address": withdrawal_data["address"],
        "teleId": str(user.id)
    }

    resp = send_post_request(backend_endpoint + "withdrawal-request", json.dumps(payload))

    if resp is None:
        context.bot.send_message(chat_id=update.message.chat_id, text=error_message, reply_markup=main_markup
                                 , parse_mode=ParseMode.HTML, disable_web_page_preview=True)
        return

    resp_message = resp.__getitem__("message")

    if resp_message is not None and resp_message == "PLAYER_NOT_FOUND":
        start(update, context)
        return
    elif resp_message is not None:
        user_data = context.user_data
        user_data["previous_action"] = "start"
        context.bot.send_message(chat_id=update.message.chat_id, text=resp_message, reply_markup=main_markup
                                 , parse_mode=ParseMode.HTML, disable_web_page_preview=True)
        return

    if "withdrawal_data" in user_data.keys():
        del user_data["withdrawal_data"]

    message = "Your withdrawal request has been submitted"

    context.bot.send_message(chat_id=update.message.chat_id, text=message, reply_markup=main_markup
                             , parse_mode=ParseMode.HTML, disable_web_page_preview=True)
    return

def handle_submit_referee_code_dashboard(update, context):
    user = update.message.from_user
    text = update.message.text
    ref_code = text

    user_name = " @" + user.username if user.username else ""
    first_name = user.first_name if user.first_name else ""
    last_name = user.last_name if user.last_name else ""
    full_name = first_name + ' ' + last_name + user_name if last_name != "" else first_name + user_name

    temp = homepage_domain + "?refCode="
    if temp in text:
        ref_code = text.replace(temp, "")

    register_data = {
        'teleName': full_name,
        'teleId': str(user.id),
        'refCode': ref_code
    }

    resp = send_post_request(backend_endpoint + 'register-player', json.dumps(register_data))

    if resp is None:
        context.bot.send_message(chat_id=update.message.chat_id, text=error_message
                                 , parse_mode=ParseMode.HTML, disable_web_page_preview=True)
        start(update, context)
        return

    resp_message = resp.__getitem__("message")

    if resp_message is not None and resp_message == "PLAYER_NOT_FOUND":
        start(update, context)
        return
    elif resp_message is not None:
        context.bot.send_message(chat_id=update.message.chat_id, text=resp_message
                                 , parse_mode=ParseMode.HTML, disable_web_page_preview=True)
        start(update, context)
        return
    is_success = resp.__getitem__("success")
    if is_success is None or is_success is False:
        context.bot.send_message(chat_id=update.message.chat_id, text=error_message
                                 , parse_mode=ParseMode.HTML, disable_web_page_preview=True)
        start(update, context)
        return

    data = resp.__getitem__("data")

    if data is None:
        context.bot.send_message(chat_id=update.message.chat_id, text=error_message
                                 , parse_mode=ParseMode.HTML, disable_web_page_preview=True)
        start(update, context)
        return

    username = data.__getitem__("username")
    username = username if username is not None else ""

    password = data.__getitem__("password")
    password = password if password is not None else ""

    ref_code = data.__getitem__("refCode")
    ref_code = ref_code if ref_code is not None else ""

    security_code = data.__getitem__("securityCode")
    security_code = security_code if security_code is not None else ""

    message = "Congratulation!"

    context.bot.send_message(chat_id=update.message.chat_id, text=message,
                             parse_mode=ParseMode.HTML, disable_web_page_preview=True)

    context.bot.send_sticker(chat_id=update.effective_chat.id, sticker=welcome_sticker_id)

    message = welcome_messsage + "\n \nYour original account information is: \n\nUsername: " + username + \
              "\n\nPassword: " + password + " \n\n" + "Referral Code: " + ref_code + \
              "\nSecurity Code: " + security_code + \
              "\nPlease follow the link below to change your personal information:\n" + cms_domain
    context.bot.send_message(chat_id=update.effective_chat.id, text=message, reply_markup=main_markup
                             , disable_web_page_preview=True)

    return


def handle_setting(update, context):
    message = "Please choose:"
    context.bot.send_message(chat_id=update.message.chat_id, text=message, reply_markup=setting_markup
                             , parse_mode=ParseMode.HTML, disable_web_page_preview=True)

def handle_get_tutorial(update, context):
    message = "Please visit luckylott.live to learn how to play"
    context.bot.send_message(chat_id=update.message.chat_id, text=message, reply_markup=main_markup
                             , parse_mode=ParseMode.HTML, disable_web_page_preview=True)

def handle_game_info(update, context):
    message = "Please choose:"
    context.bot.send_message(chat_id=update.message.chat_id, text=message, reply_markup=game_info_markup
                             , parse_mode=ParseMode.HTML, disable_web_page_preview=True)

def handle_get_history_trans(update, context):
    message = "Please select the transaction history you would like to check:"
    context.bot.send_message(chat_id=update.message.chat_id, text=message, reply_markup=history_trans_markup
                             , parse_mode=ParseMode.HTML, disable_web_page_preview=True)

def handle_create_withdrawal(update, context):
    message = "Please select the kind of crypto currency you want to withdraw:"
    context.bot.send_message(chat_id=update.message.chat_id, text=message, reply_markup=withdrawal_type_markup
                             , parse_mode=ParseMode.HTML, disable_web_page_preview=True)

def handle_deposit_history(update, context):
    url = cms_domain
    message = "Please click on the link below to check your deposit history\n" + url
    context.bot.send_message(chat_id=update.message.chat_id, text=message, reply_markup=main_markup
                             , parse_mode=ParseMode.HTML, disable_web_page_preview=True)


def handle_withdrawal_history(update, context):
    url = cms_domain
    message = "Please click on the link below to check your withdrawal history\n" + url
    context.bot.send_message(chat_id=update.message.chat_id, text=message, reply_markup=main_markup
                             , parse_mode=ParseMode.HTML, disable_web_page_preview=True)


def handle_get_draw_info(update, context, markup):
    user = update.message.from_user
    resp = send_get_request(backend_endpoint + "draw-info")

    if resp is None:
        context.bot.send_message(chat_id=update.message.chat_id, text=error_message, reply_markup=main_markup
                                 , parse_mode=ParseMode.HTML, disable_web_page_preview=True)
        return

    resp_message = resp.__getitem__("message")

    if resp_message is not None and resp_message == "PLAYER_NOT_FOUND":
        start(update, context)
        return
    elif resp_message is not None:
        user_data = context.user_data
        user_data["previous_action"] = "start"
        context.bot.send_message(chat_id=update.message.chat_id, text=resp_message, reply_markup=main_markup
                                 , parse_mode=ParseMode.HTML, disable_web_page_preview=True)
        return

    games = resp.__getitem__("data")
    message = ""
    if len(games) == 0:
        message = "This round is currently closed. Please come back later"
    else:
        for game in games:
            pool_name = game.__getitem__("poolName")
            pool_balance = str(game.__getitem__("poolBalance"))
            game_id = game.__getitem__("id")
            game_code = game.__getitem__("gameCode")
            if game_code is None:
                game_code = ""
            draw_date = game.__getitem__("drawDate")
            draw_date = convert_date_time(draw_date)
            close_date = game.__getitem__("closeDate")
            close_date = convert_date_time(close_date)

            message += game_code + '\nTotal pool value: ' + pool_balance \
                       + ' ' + pool_name  + '\nTime to publish results: \n' + draw_date + '\n' + \
                       'Round closed date: \n' + close_date

            message += "\n\n____________\n\n"

    if markup is None:
        context.bot.send_message(chat_id=update.message.chat_id, text=message
                                 , parse_mode=ParseMode.HTML, disable_web_page_preview=True)
    else:
        context.bot.send_message(chat_id=update.message.chat_id, text=message, reply_markup=markup
                             , parse_mode=ParseMode.HTML, disable_web_page_preview=True)


def handle_get_last_draw_ticket(update, context):
    user = update.message.from_user
    resp = send_get_request(backend_endpoint + "my-draw-ticket?teleId=" + str(user.id))

    if resp is None:
        context.bot.send_message(chat_id=update.message.chat_id, text=error_message, reply_markup=main_markup
                                 , parse_mode=ParseMode.HTML, disable_web_page_preview=True)
        return

    resp_message = resp.__getitem__("message")

    if resp_message is not None and resp_message == "PLAYER_NOT_FOUND":
        start(update, context)
        return
    elif resp_message is not None:
        user_data = context.user_data
        user_data["previous_action"] = "start"
        context.bot.send_message(chat_id=update.message.chat_id, text=resp_message, reply_markup=main_markup
                                 , parse_mode=ParseMode.HTML, disable_web_page_preview=True)
        return

    games = resp.__getitem__("data")
    message = ""
    if len(games) == 0:
        message = "You do not have any tickets purchased in the last round"
    else:
        for game in games:
            game_code = game.__getitem__("gameCode")
            if game_code is None:
                game_code = ""
            message += game_code + "\n" + convert_date_time(game.__getitem__("drawDate")) + "\nYour lucky numbers:\n"
            for ticket in game.__getitem__("bets"):
                message += convert_bet_type(ticket.__getitem__("betType")) + ": " + \
                           ticket.__getitem__("betNumber") + "\n"

            message += "____________\n\n"

    context.bot.send_message(chat_id=update.message.chat_id, text=message, reply_markup=main_markup
                             , parse_mode=ParseMode.HTML, disable_web_page_preview=True)


def handle_unknown(update, context):
    text = update.message.text
    user_data = context.user_data
    if type(user_data) is dict and "bet_data" in user_data.keys():
        bet_data = user_data["bet_data"]
        if bet_data is not None and "pool_type" in bet_data.keys():
            handle_submit_bet(update, context)
            return
    if type(user_data) is dict and "withdrawal_data" in user_data.keys():
        withdrawal_data = user_data["withdrawal_data"]
        if withdrawal_data is not None:
            withdrawal_keys = withdrawal_data.keys()
            if "amount" not in withdrawal_keys and "address" not in withdrawal_keys:
                handle_key_withdraw_amount(update, context)
                return
            elif "amount" in withdrawal_keys and "address" not in withdrawal_keys:
                handle_key_withdraw_address(update, context)
                return
            else:
                handle_confirm_withdrawal(update, context)
                return
    message = welcome_messsage
    context.bot.send_message(chat_id=update.message.chat_id, text=message, reply_markup=main_markup
                             , parse_mode=ParseMode.HTML, disable_web_page_preview=True)


def send_post_request(end_point, payload):
    session_requests = requests.session()
    session_requests.headers['Authorization'] = backend_token
    session_requests.headers['Content-Type'] = 'application/json'
    session_requests.headers['Accept'] = '*/*'

    try:
        r = session_requests.post(end_point, data=payload, timeout=30)
        r.raise_for_status()
        return process_response_data(r.text)
    except requests.exceptions.HTTPError as err:
        return None
    except requests.exceptions.ConnectionError:
        return None


def send_get_request(end_point):
    session_requests = requests.session()
    session_requests.headers['Authorization'] = backend_token
    try:
        r = session_requests.get(end_point)
        r.raise_for_status()
        return process_response_data(r.text)
    except requests.exceptions.HTTPError as err:
        return None
    except requests.exceptions.ConnectionError:
        return None


def process_response_data(res):
    try:
        json_object = json.loads(res)
        return json_object
    except ValueError as e:
        return None


def random_string(string_length=8):
    letters = string.ascii_lowercase + string.digits
    return ''.join(random.choice(letters) for i in range(string_length))


def convert_bet_type(bet_type):
    if bet_type == "NUM_2":
        return "LuckyLott 2"
    elif bet_type == "NUM_3":
        return "LuckyLott 3"
    elif bet_type == "NUM_4":
        return "Jackpot"
    elif bet_type == "NUM_4_RAND":
        return "Mini jackpot"
    return ""


def convert_date_time(date):
    draw_date = datetime.strptime(str(date), '%Y-%m-%dT%H:%M:%SZ')
    return draw_date.strftime("%d/%m/%Y %H:%M:%S")


def gen_withdrawal_info_message(fee, min_amount, balance, token):
    withdraw_messsage = 'You are in the withdrawal section.' \
                        '\nPlease note that withdrawals can take up to 24 hours to complete.\n' + \
                        '\nYour balance: ' + balance + ' ' + token +\
                        '\nWithdrawal fee: ' + fee +  ' ' + token + \
                        '\nMinimum withdrawal amount: ' + min_amount + ' ' + token + \
                        '\nPlease enter the amount you want to withdraw'
    return withdraw_messsage

def run_bot():
    dispatcher = updater.dispatcher
    start_handler = CommandHandler('start', start)
    dispatcher.add_handler(start_handler)
    updater.start_polling()
    echo_handler = MessageHandler(Filters.text & (~Filters.command), echo)
    dispatcher.add_handler(echo_handler)
    unknown_handler = MessageHandler(Filters.command, handle_unknown)
    dispatcher.add_handler(unknown_handler)


run_bot()
