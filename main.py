import asyncio
import sys
import os
import json
import signal

from modules.bot import Bot


def is_number(s):
    try:
        int(s)
    except:
        return False
    return True


def input_value(text, is_numeric, default=None):
    valid_func = lambda x: True
    if is_numeric:
        valid_func = lambda x: is_number(x) == is_numeric

    value = ""
    if default is not None:
        text = f'{text} (значение по умолчанию: "{default}")'
    text += ":"
    while not value or not valid_func(value):
        print(text)
        value = input()

        if default is not None and not value:
            value = default
            break

    if is_number(value):
        return int(value)
    return value


def make_config(file_path, data):
    with open(file_path, "w") as f:
        f.write(json.dumps(data))


def read_config(file_path):
    with open(file_path, "r") as f:
        content = f.read()
        if len(content) > 0:
            return json.loads(content)
        else:
            return dict()


def generate_config(file_path):
    token_question = {
        "text": "Введите токен вашего бота",
        "is_numeric": False,
        "default": None
    }

    config = dict()
    if os.path.isfile(file_path):
        config = read_config(file_path)

    if "token" in config:
        token_question["default"] = config["token"]

    config["token"] = input_value(**token_question)
    make_config(file_path, config)

    return config


def handle_sigint(sig, frame):
    print('Interrupted')
    sys.exit(0)

if __name__ == "__main__":
    try:
        BASE_PATH = sys._MEIPASS
    except Exception:
        BASE_PATH = os.path.abspath(".")

    FILENAME = "config.json"
    FILE_PATH = os.path.join(BASE_PATH, FILENAME)
    config = generate_config(FILE_PATH)

    print("Running...")
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    server = Bot(config["token"])
    asyncio.run(server.run())
