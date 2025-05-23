from vk_api.keyboard import VkKeyboard, VkKeyboardColor


def command(vk, event, stage):
    keyboard = None
    message = '''
Привет! Давай знакомиться. Я то-то то-то, со мной можно делать то-то то-то.
Подскажи айди своего персонажа.
    '''

    if stage == 1:
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
    elif stage == 2:
        message = 'Приятно познакомиться, пчёлка!'

    if keyboard is None:
        vk.messages.send(user_id=event.user_id, message=message, random_id=0)
    else:
        vk.messages.send(user_id=event.user_id, message=message, random_id=0, keyboard=keyboard.get_keyboard())
