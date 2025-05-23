from playwright.async_api import async_playwright
from vk_api.keyboard import VkKeyboard, VkKeyboardColor

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
    welcome = False

    if user.stage == 0:
        message = ask_id()
        updates['stage'] = user.stage + 1
        
    if user.stage == 1:
        if await get_name(event.message) is not None:
            updates['stage'] = user.stage + 1
            updates['catwar_id'] = event.text
            if await get_universe(event.message) == 'Озёрная вселенная':
                message, keyboard = ask_clan()
            else:
                welcome = True
                user.catwar_id = event.message
        else: 
            message = ask_id()

    if user.stage == 2 or welcome:
        message = f'Приятно познакомиться, {await get_name(user.catwar_id)}!'

    if keyboard is None:
        vk.messages.send(user_id=event.user_id, message=message, random_id=0)
    else:
        vk.messages.send(user_id=event.user_id, message=message, random_id=0, keyboard=keyboard.get_keyboard())

    return updates
