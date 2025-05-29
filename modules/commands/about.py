from vk_api.keyboard import VkKeyboard, VkKeyboardColor

from .main_menu import get_main_menu_keyboard


def command(vk, event, user):
    message = '''
Я бот-помощник, то-то то-то

Советую обязательно ознакомиться с основной информацией о нас:
Наша памятка — https://vk.com/@order_of_bees-pamyatka-ordena
Про плюшки за активность — https://vk.com/@order_of_bees-ob-aktivnosti
'''
    keyboard = None

    if not user.approved:
        keyboard = VkKeyboard(one_time=True)  
        keyboard.add_button('Я прочитал!', color=VkKeyboardColor.POSITIVE)
    else:
        keyboard = get_main_menu_keyboard()

    vk.messages.send(user_id=event.user_id, message=message, random_id=0, keyboard=keyboard.get_keyboard())
