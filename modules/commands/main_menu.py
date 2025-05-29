from vk_api.keyboard import VkKeyboard, VkKeyboardColor

from models.positions import Positions 


positions = {
    'carriers': {
        'emoji': '🍯',
        'title': 'Медоносец'
    },
    'defenders': {
        'emoji': '⚔️',
        'title': 'Защитник'
    },
    'creators': {
        'emoji': '🎨',
        'title': 'Творец'
    },
    'squads': {
        'emoji': '🍁',
        'title': 'В отрядах (ОВП)'
    },
    'helpers': {
        'emoji': '🛟',
        'title': 'Помощь в прокачке'
    }
}

def get_main_menu_keyboard():
    keyboard = VkKeyboard(one_time=True)  
    keyboard.add_button('Обновить', color=VkKeyboardColor.POSITIVE)
    keyboard.add_button('Об активности', color=VkKeyboardColor.PRIMARY)

    keyboard.add_line() 
    for pos in ['carriers', 'defenders', 'creators']:
        keyboard.add_button(
            ' '.join([positions[pos]['emoji'], positions[pos]['title']]),
            color=VkKeyboardColor.SECONDARY 
        )
    
    keyboard.add_line() 
    for pos in ['squads', 'helpers']:
        keyboard.add_button(
            ' '.join([positions[pos]['emoji'], positions[pos]['title']]),
            color=VkKeyboardColor.SECONDARY 
        )

    return keyboard


def command(vk, event, user):
    message = f'''
Статус: {'🟢' if True else '🔴'}
Кошелёк: {0} 🐝
Должности: {', '.join(sorted(map(lambda x: x.title, Positions.find_all(user.id))))}'''

    
    keyboard = get_main_menu_keyboard()
    vk.messages.send(user_id=event.user_id, message=message, random_id=0, keyboard=keyboard.get_keyboard())
