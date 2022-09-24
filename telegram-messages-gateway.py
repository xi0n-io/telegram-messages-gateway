#!/usr/bin/env python3
"""
Author: xi0n-io
API Documentation: https://core.telegram.org/bots/api
"""
from datetime import datetime

import requests
import signal
import sys

HELP_MESSAGE = """Usage:

Send a message:
    telegram -a <api> -c <chat> -m 'my message'

Send a message from stdin:
    echo 'my message' | telegram -a <api> -c <chat>

Get a list of all the available chat ids (in the last 24h) of the bot:
    telegram -i -a <api>
    telegram --ids --api <api>

Get a list of all messages received in the last 24 hours:
    telegram -ls -a <api>
    telegram --list --api <api>


Options:
     -a, --api <api>            API key of the bot that should send the message
     -c, --chat <chat>          Chat ID of the recipient
     -m, --message <message>    Do not use stdin as input
     -i, --ids                  Get all available chat ids (from last 24h) of the bot
     -ls, --list                Get a list of all the messages from the last 24 hours
     -h, --help                 Get help for commands
     -v, --verbose              Make the operation more talkative"""

TELEGRAM_API_URL = "https://api.telegram.org/bot{}/{}"
TELEGRAM_API_METHOD_SEND_MESSAGE = "sendMessage"
TELEGRAM_API_METHOD_GET_UPDATES = "getUpdates"

DATE_FORMAT = "%H:%M:%S %d-%m-%Y"

POST_ARGUMENT_CHAT_ID = "chat_id"
POST_ARGUMENT_TEXT = "text"

DICT_API = "api"
DICT_CHAT_ID = "chat-id"
DICT_MESSAGE = "message"
DICT_IDS = "ids"
DICT_LIST = "list"
DICT_HELP = "help"
DICT_VERBOSE = "verbose"

ARGUMENT_API = ["-a", "--api"]
ARGUMENT_CHAT_ID = ["-c", "--chat"]
ARGUMENT_MESSAGE = ["-m", "--message"]
ARGUMENT_IDS = ["-i", "--ids"]
ARGUMENT_LIST = ["-ls", "--list"]
ARGUMENT_HELP = ["-h", "--help"]
ARGUMENT_VERBOSE = ["-v", "--verbose"]

API_RESPONSE_CODE_SUCCESS = 200

verbose = False


def get_arguments_from_sysarg() -> dict:
    """
    Extract the arguments used to start the program, also called parameters

    :return: Dictionary containing the found parameters, can also be empty
    """

    extracted_arguments = {}

    for i, argument in enumerate(sys.argv):
        if argument in ARGUMENT_API:
            # make sure we have a 'value' argument for this 'key', 'telegram -m' -> should be 'telegram -m <message>'
            if (i + 1) < len(sys.argv):
                extracted_arguments[DICT_API] = sys.argv[i + 1]

        elif argument in ARGUMENT_CHAT_ID:
            # make sure we have a 'value' argument for this 'key', 'telegram -m' -> should be 'telegram -m <message>'
            if (i + 1) < len(sys.argv):
                extracted_arguments[DICT_CHAT_ID] = sys.argv[i + 1]

        elif argument in ARGUMENT_MESSAGE:
            # make sure we have a 'value' argument for this 'key', 'telegram -m' -> should be 'telegram -m <message>'
            if (i + 1) < len(sys.argv):
                extracted_arguments[DICT_MESSAGE] = sys.argv[i + 1]

        elif argument in ARGUMENT_IDS:
            #  Does not have a 'value', only a 'key'
            extracted_arguments[DICT_IDS] = None

        elif argument in ARGUMENT_LIST:
            #  Does not have a 'value', only a 'key'
            extracted_arguments[DICT_LIST] = None

        elif argument in ARGUMENT_VERBOSE:
            #  Does not have a 'value', only a 'key'
            extracted_arguments[DICT_VERBOSE] = None

        elif argument in ARGUMENT_HELP:
            #  Does not have a 'value', only a 'key'
            extracted_arguments[DICT_HELP] = None

    return extracted_arguments


def print_help() -> None:
    """
    Print the info message to stdout

    :return: None
    """

    print(HELP_MESSAGE)


def send_message(bot_api: str, chat_id: str, message: str) -> int:
    """
    Sends a message to the given telegram bot using an api http request.

    :param bot_api: Bot API token
    :param chat_id: Destination chat id
    :param message: Text to send
    :return: Status code of the API http request
    """

    # Create the correct url
    formatted_url = TELEGRAM_API_URL.format(bot_api, TELEGRAM_API_METHOD_SEND_MESSAGE)

    # Collect the parameters we send
    post_parameters = {
        'chat_id': chat_id,
        'text': message
    }

    # Send the request
    response = requests.post(formatted_url, post_parameters)

    return response.status_code


def read_from_stdin(bot_api: str, chat_id: str) -> None:
    """
    Send a message to a user, from stdin
    :param bot_api: Bot API token
    :param chat_id: Destination chat id
    :return: None
    """

    for line in sys.stdin:  # Wait for line from stdin
        message = line.rstrip()
        status_code = send_message(bot_api, chat_id, message)  # Send the message

        if status_code == API_RESPONSE_CODE_SUCCESS and verbose:  # Have there been any problems?
            print("Send '{}' to {}".format(message, chat_id))

        else:
            print("Could not send message ({})\n".format(status_code), file=sys.stderr)


def send_direct_message(bot_api: str, chat_id: str, message: str) -> None:
    """
    Send a message to a user
    :param bot_api: Bot API token
    :param chat_id: Destination chat id
    :param message: Text to send
    :return: None
    """
    status_code = send_message(bot_api, chat_id, message)  # Send the message

    if status_code == API_RESPONSE_CODE_SUCCESS and verbose:  # Have there been any problems?
        print("Send '{}' to {}".format(message, chat_id))

    elif status_code != API_RESPONSE_CODE_SUCCESS:
        print("Could not send message ({})\n".format(status_code), file=sys.stderr)


def get_chat_ids_from_json(json: dict) -> dict:
    """
    Get all the chat ids from a json formatted document
    :param json: json document
    :return: Dictionary [username:id]
    """
    chat_ids = {}

    for update in json["result"]:
        username = ""
        chat_id = ""

        if "my_chat_member" in update:
            username = update["my_chat_member"]["chat"]["username"]
            chat_id = update["my_chat_member"]["chat"]["id"]
        elif "message" in update:
            username = update["message"]["chat"]["first_name"]
            chat_id = update["message"]["chat"]["id"]

        if chat_id not in chat_ids:
            chat_ids[chat_id] = username

    return chat_ids


def get_all_chat_ids(bot_api: str) -> int:
    """
    Get all the available chat ids (from last 24h) of the bot
    :param bot_api: Bot API token
    :return: Status code of the API http request
    """
    formatted_url = TELEGRAM_API_URL.format(bot_api, TELEGRAM_API_METHOD_GET_UPDATES)
    response = requests.post(formatted_url)

    if response.status_code == API_RESPONSE_CODE_SUCCESS:
        chat_ids = get_chat_ids_from_json(response.json())

        if len(chat_ids) > 0:
            if verbose:
                print("Chat ID : Name")

            for key, value in chat_ids.items():
                print(key, ':', value)

    else:
        print("No updates found, please send a new message to your bot")

    return response.status_code


def get_all_messages_list(bot_api: str) -> None:
    """
    Get all the messages (of last 24h) of the bot
    :param bot_api: Bot API token
    :return: None
    """
    formatted_url = TELEGRAM_API_URL.format(bot_api, TELEGRAM_API_METHOD_GET_UPDATES)
    response = requests.post(formatted_url)

    if response.status_code == API_RESPONSE_CODE_SUCCESS:
        json = response.json()

        if verbose:
            print("Name : User ID : Chat ID: Date: Message")

        for update in json["result"]:
            human_readable_date = datetime.fromtimestamp(update["message"]["date"])

            print("{} : {} : {} : {} : {}".format(update["message"]["from"]["first_name"],
                                                  update["message"]["from"]["id"],
                                                  update["message"]["chat"]["id"],
                                                  human_readable_date.strftime(DATE_FORMAT),
                                                  update["message"]["text"]))

    else:
        print("No updates found, please send a new message to your bot")


def handler_exit(signal_received, frame) -> None:
    exit(0)


def main():
    signal.signal(signal.SIGINT, handler_exit)  # Handle keyboard interrupt

    arguments = get_arguments_from_sysarg()

    if DICT_HELP in arguments:
        print_help()
    else:
        if DICT_VERBOSE in arguments:
            global verbose
            verbose = True

        if DICT_API in arguments and DICT_CHAT_ID in arguments and DICT_MESSAGE in arguments:  # Send direct message
            send_direct_message(arguments[DICT_API], arguments[DICT_CHAT_ID], arguments[DICT_MESSAGE])

        elif DICT_API in arguments and DICT_CHAT_ID in arguments:
            read_from_stdin(arguments[DICT_API], arguments[DICT_CHAT_ID])

        elif DICT_API in arguments and DICT_LIST in arguments:
            get_all_messages_list(arguments[DICT_API])

        elif DICT_API in arguments and DICT_IDS in arguments:
            get_all_chat_ids(arguments[DICT_IDS])

        else:
            print("Cannot process input", file=sys.stderr)
            print_help()


if __name__ == '__main__':
    main()
