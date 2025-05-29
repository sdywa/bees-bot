from vk_api.keyboard import VkKeyboard, VkKeyboardColor

from .questionnaire import get_name
from models.positions import Positions 


def command(vk, event, user):
    message = f'''
ID: {user.catwar_id}
Имя: {get_name(user.catwar_id)}
Положение: {'одиночка' if user.loner else 'племенной'}
Должности: {', '.join(sorted(map(lambda x: x.title, Positions.find_all(user.id))))}
'''

    keyboard = VkKeyboard(one_time=True)  
    keyboard.add_button('Изменить данные', color=VkKeyboardColor.POSITIVE)
    keyboard.add_button('Назад', color=VkKeyboardColor.NEGATIVE)

    vk.messages.send(user_id=event.user_id, message=message, random_id=0, keyboard=keyboard.get_keyboard())
