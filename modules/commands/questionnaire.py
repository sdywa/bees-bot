import re

from playwright.async_api import async_playwright
from vk_api.keyboard import VkKeyboard, VkKeyboardColor

from models.positions import Positions 


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

def ask_position(users_positions): 
    message = 'Какие должности ты занимаешь?'
    keyboard = VkKeyboard(one_time=True)  
    for pos in ['carriers', 'defenders', 'creators']:
        keyboard.add_button(
            ' '.join([positions[pos]['emoji'], positions[pos]['title']]),
            color=VkKeyboardColor.PRIMARY 
                  if positions[pos]['title'] in users_positions 
                  else VkKeyboardColor.SECONDARY
        )
    
    keyboard.add_line() 
    keyboard.add_button(
        ' '.join([positions['squads']['emoji'], positions['squads']['title']]),
        color=VkKeyboardColor.PRIMARY 
              if positions['squads']['title'] in users_positions 
              else VkKeyboardColor.SECONDARY
    )

    return message, keyboard

async def get_name(id):
    async with async_playwright() as p:
        browser = await p.firefox.launch(headless=True)
        page = await browser.new_page()
        await page.goto(f'http://catwar.net/cat{id}')
        await page.wait_for_selector('body')

        name = None
        element = await page.query_selector('big')
        if element:
            name = await element.text_content()

        await browser.close()
        return name

async def get_universe(id):
    async with async_playwright() as p:
        browser = await p.firefox.launch(headless=True)
        page = await browser.new_page()
        await page.goto(f'http://catwar.net/cat{id}')
        await page.wait_for_selector('body')

        universe = None
        element = await page.query_selector('[data-cat] > b')
        if element:
            universe = await element.text_content()

        await browser.close()
        return universe

async def command(vk, event, user):
    message = ''
    keyboard = None
    updates = {}
    skip = False
    text = clean_text(event.message)

    if user.stage == 0:
        message = ask_id()
        updates['stage'] = user.stage + 1
        skip = True
        
    if user.stage == 1:
        skip_prev = skip
        skip = False

        id = re.sub('[^0-9]', '', text)
        if await get_name(id) is not None:
            updates['stage'] = user.stage + 1
            updates['catwar_id'] = id
            skip = True
        elif skip_prev: 
            message = ask_id()
        else:
            message = 'Некорректный айди! Отправь, пожалуйста, корректный.'

    if user.stage == 2 or (user.stage == 1 and skip):
        skip_prev = skip
        skip = False

        id = user.catwar_id
        if id is None:
            id = re.sub('[^0-9]', '', text)
        if await get_universe(id) != 'Озёрная вселенная':
            skip = True
            updates['stage'] = user.stage + 1
        elif text in map(lambda x: x['title'].lower(), clans.values()):
            skip = True
            updates['stage'] = user.stage + 1
            updates['loner'] = text == 'одиночки'
        elif skip_prev:
            message, keyboard = ask_clan()
        else:
            message, keyboard = ask_clan()
            message = 'Не могу понять племя, выбери из предложенных вариантов.'

    if user.stage == 3 or ((user.stage == 1 or user.stage == 2) and skip):
        skip_prev = skip
        skip = False

        if text == 'дальше':
            user_positions = Positions.find_all(user.id)
            if len(user_positions) > 0:
                skip = True
                updates['stage'] = user.stage + 1
            else:
                _, keyboard = ask_position(list(map(lambda x: x.title, user_positions)))
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
            elif not skip_prev:
                message = 'Не могу понять должность, выбери из предложенных вариантов.'

            user_positions = Positions.find_all(user.id)
            new_message, keyboard = ask_position(list(map(lambda x: x.title, user_positions)))

            if message == '':
                message = new_message

            if len(user_positions) > 0:
                keyboard.add_line() 
                keyboard.add_button('Дальше', color=VkKeyboardColor.POSITIVE)


    if user.stage == 4 or (user.stage == 3 and skip):
        message = f'''
Приятно познакомиться, {await get_name(user.catwar_id)}!
Статус: {'одиночка' if user.loner else 'племенной'}
Должности: {', '.join(sorted(map(lambda x: x.title, Positions.find_all(user.id))))}
'''

    if keyboard is None:
        vk.messages.send(user_id=event.user_id, message=message, random_id=0)
    else:
        vk.messages.send(user_id=event.user_id, message=message, random_id=0, keyboard=keyboard.get_keyboard())

    return updates
