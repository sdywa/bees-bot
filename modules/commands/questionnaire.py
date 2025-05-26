import sys
sys.path.append("../..")

import re

from playwright.async_api import async_playwright
from vk_api.keyboard import VkKeyboard, VkKeyboardColor

from models.positions import Positions 


def ask_id():
    message = '''
Привет! Давай знакомиться. Я то-то то-то, со мной можно делать то-то то-то.
Подскажи айди своего персонажа.
    '''
    return message

def ask_clan(): 
    message = 'В каком племени обитаешь?'
    keyboard = VkKeyboard(one_time=True)
    keyboard.add_button('🏠 Одиночки', color=VkKeyboardColor.POSITIVE)
    
    keyboard.add_line() 
    keyboard.add_button('⚡ Гроза', color=VkKeyboardColor.SECONDARY)
    keyboard.add_button('💨 Ветер', color=VkKeyboardColor.SECONDARY)
    keyboard.add_button('🌊 Река', color=VkKeyboardColor.SECONDARY)
    keyboard.add_button('🔮 Тени', color=VkKeyboardColor.SECONDARY)

    keyboard.add_line() 
    keyboard.add_button('🗻 Клан падающей воды', color=VkKeyboardColor.SECONDARY)
    keyboard.add_button('❄️ Северный клан', color=VkKeyboardColor.SECONDARY)

    return message, keyboard

def ask_position(): 
    message = 'Какие должности ты занимаешь?'
    keyboard = VkKeyboard(one_time=True)  
    keyboard.add_button('🍯 Медоносец', color=VkKeyboardColor.SECONDARY)
    keyboard.add_button('⚔️ Защитник', color=VkKeyboardColor.SECONDARY)
    keyboard.add_button('🎨 Творец', color=VkKeyboardColor.SECONDARY)
    
    keyboard.add_line() 
    keyboard.add_button('🍁 В отрядах ОВП', color=VkKeyboardColor.SECONDARY)

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
    text = re.sub('[^0-9а-яА-Я]', '', event.message).lower()

    if user.stage == 0:
        message = ask_id()
        updates['stage'] = user.stage + 1
        
    if user.stage == 1:
        id = re.sub('[^0-9]', '', text)
        if await get_name(id) is not None:
            updates['stage'] = user.stage + 1
            updates['catwar_id'] = id
            if await get_universe(id) == 'Озёрная вселенная':
                message, keyboard = ask_clan()
            else:
                skip = True
                user.catwar_id = id
        else: 
            message = ask_id()

    if user.stage == 2 or (user.stage == 1 and skip):
        if text == 'дальше':
            skip = True
        else:
            message, keyboard = ask_position()

            user_positions = Positions.find_all(user.id)
            available = ['медоносец', 'защитник', 'творец', 'в отрядах овп']
            if any(map(lambda pos: pos.user_id == user.id, user_positions)):
                [Positions.remove(pos.id) for pos in user_positions if pos.title == text]
                message = f'Должность {text} удалена!'
            elif text in available:
                Positions.add({ 'user': user, 'title': text })
                message = f'Должность {text} добавлена!'

            if len(Positions.find_all(user.id)) > 0:
                keyboard.add_line() 
                keyboard.add_button('Дальше', color=VkKeyboardColor.POSITIVE)


    if user.stage == 3 or (user.stage == 2 and skip):
        message = f'Приятно познакомиться, {await get_name(user.catwar_id)}!'

    if keyboard is None:
        vk.messages.send(user_id=event.user_id, message=message, random_id=0)
    else:
        vk.messages.send(user_id=event.user_id, message=message, random_id=0, keyboard=keyboard.get_keyboard())

    return updates
