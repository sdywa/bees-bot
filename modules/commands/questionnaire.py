import re

from playwright.sync_api import sync_playwright
from vk_api.keyboard import VkKeyboard, VkKeyboardColor

from models.positions import Positions 


go_back = {
    1: lambda user: 1,
    2: lambda user: 1,
    3: lambda user: 1 if get_universe(user.catwar_id) != 'Озёрная вселенная' else 2,
    4: lambda user: 3,
}

clans = {
    'loner': {
        'emoji': '🏠',
        'title': 'Одиночки'
    },
    'domestic': {
        'emoji': '💤',
        'title': 'Домашние'
    },
    'thunder': {
        'emoji': '⚡',
        'title': 'Гроза'
    },
    'wind': {
        'emoji': '💨',
        'title': 'Ветер'
    },
    'river': {
        'emoji': '🌊',
        'title': 'Река'
    },
    'shadow': {
        'emoji': '🔮',
        'title': 'Тени'
    },
    'kpv': {
        'emoji': '🗻',
        'title': 'Клан падающей воды'
    },
    'nordgeist': {
        'emoji': '❄️',
        'title': 'Северный клан'
    },
}

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
}

def clean_text(text):
    return re.sub('[^0-9а-яА-Я ()]', '', text).lower().strip()

def ask_id():
    message = '''
Привет! Давай знакомиться. Я то-то то-то, со мной можно делать то-то то-то.
Подскажи айди своего персонажа.
    '''
    return message

def ask_clan(): 
    message = 'В каком племени обитаешь?'
    keyboard = VkKeyboard(one_time=True)

    keyboard.add_button(' '.join([clans['loner']['emoji'], clans['loner']['title']]), color=VkKeyboardColor.POSITIVE)
    keyboard.add_button(' '.join([clans['domestic']['emoji'], clans['domestic']['title']]), color=VkKeyboardColor.PRIMARY)

    for clan in [None, 'thunder', 'wind', 'river', 'shadow', None, 'kpv', 'nordgeist']:
        if clan is None: 
            keyboard.add_line() 
        else:
            keyboard.add_button(' '.join([clans[clan]['emoji'], clans[clan]['title']]), color=VkKeyboardColor.SECONDARY)
    
    return message, keyboard

def ask_position(user): 
    user_positions = Positions.find_all(user.id)
    user_positions = list(map(lambda x: x.title, user_positions))

    message = 'Какие должности ты занимаешь?'
    keyboard = VkKeyboard(one_time=True)  
    for pos in ['carriers', 'defenders', 'creators']:
        keyboard.add_button(
            ' '.join([positions[pos]['emoji'], positions[pos]['title']]),
            color=VkKeyboardColor.PRIMARY 
                  if positions[pos]['title'] in user_positions 
                  else VkKeyboardColor.SECONDARY
        )
    
    keyboard.add_line() 
    keyboard.add_button(
        ' '.join([positions['squads']['emoji'], positions['squads']['title']]),
        color=VkKeyboardColor.PRIMARY 
              if positions['squads']['title'] in user_positions 
              else VkKeyboardColor.SECONDARY
    )

    if len(user_positions) > 0:
        keyboard.add_line() 
        keyboard.add_button('Дальше', color=VkKeyboardColor.POSITIVE)

    return message, keyboard

def get_name(id):
    with sync_playwright() as p:
        browser = p.firefox.launch(headless=True)
        page = browser.new_page()
        page.goto(f'https://catwar.net/cat{id}')
        page.wait_for_selector('body')

        name = None
        element = page.query_selector('big')
        if element:
            name = element.text_content()

        browser.close()
        return name

def get_universe(id):
    with sync_playwright() as p:
        browser = p.firefox.launch(headless=True)
        page = browser.new_page()
        page.goto(f'https://catwar.net/cat{id}')
        page.wait_for_selector('body')

        universe = None
        element = page.query_selector('[data-cat] > b')
        if element:
            universe = element.text_content()

        browser.close()
        return universe

def command(vk, event, user):
    message = ''
    keyboard = None
    
    updates = {}
    back = False

    text = clean_text(event.message)

    if text == 'назад':
        user.stage = go_back[user.stage](user)
        updates['stage'] = user.stage
        back = True

    if user.stage == 0:
        message = ask_id()
        updates['stage'] = 1
        
    if user.stage == 1:
        id = re.sub('[^0-9]', '', text)
        if back:
            message = ask_id()
        elif get_name(id) is not None:
            if get_universe(id) != 'Озёрная вселенная':
                message, keyboard = ask_position(user)
                updates['stage'] = 3
            else:
                message, keyboard = ask_clan()
                updates['stage'] = 2
                
            updates['catwar_id'] = id
            updates['loner'] = False
        else:
            message = 'Некорректный айди! Отправь, пожалуйста, корректный.'

    if user.stage == 2:
        id = user.catwar_id
        if id is None:
            id = re.sub('[^0-9]', '', text)
        
        if back:
            message, keyboard = ask_clan()
        elif text in map(lambda x: x['title'].lower(), clans.values()):
            message, keyboard = ask_position(user)
            updates['stage'] = 3
            updates['loner'] = text == 'одиночки'
        else:
            message, keyboard = ask_clan()
            message = 'Не могу понять племя, выбери из предложенных вариантов.'

    if user.stage == 3:
        if back:
            message, keyboard = ask_position(user)
        elif text == 'дальше':
            user_positions = Positions.find_all(user.id)
            if len(user_positions) > 0:
                updates['stage'] = 4
                user.stage = updates['stage']
            else:
                _, keyboard = ask_position(user)
                message = 'Выберите минимум одну должность!' 
        else:
            picked = [pos['title'] for pos in positions.values() if pos['title'].lower() == text]
            user_positions = Positions.find_all(user.id)

            if len(picked) > 0 and picked[0] in map(lambda pos: pos.title, user_positions):
                [Positions.remove(pos.id) for pos in user_positions if pos.title == picked[0]]
                message = f'Должность "{picked[0]}" убрана!'
            elif len(picked) > 0:
                Positions.add({ 'user': user, 'title': picked[0] })
                message = f'Должность "{picked[0]}" добавлена!'
            else:
                message = 'Не могу понять должность, выбери из предложенных вариантов.'

            _, keyboard = ask_position(user)

    if user.stage == 4:
        message = f'''
Приятно познакомиться, {get_name(user.catwar_id)}!
Статус: {'одиночка' if user.loner else 'племенной'}
Должности: {', '.join(sorted(map(lambda x: x.title, Positions.find_all(user.id))))}
'''

    if keyboard is None:
        vk.messages.send(user_id=event.user_id, message=message, random_id=0)
    else:
        keyboard.add_line() 
        keyboard.add_button('Назад', color=VkKeyboardColor.NEGATIVE)
        vk.messages.send(user_id=event.user_id, message=message, random_id=0, keyboard=keyboard.get_keyboard())

    return updates
