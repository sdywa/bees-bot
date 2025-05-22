def command(vk, event):
    message = '''Привет! Добро пожаловать в орден пчёл'''
    vk.messages.send(user_id=event.user_id, message=message, random_id=0)
