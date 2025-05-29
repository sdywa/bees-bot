import json

import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType

from .commands import commands
from helpers import clean_text
from models import Users


class Bot:
    def __init__(self, token):
        self.token = token

        self.session = vk_api.VkApi(token=token)
        self.vk = self.session.get_api()
        self.longpoll = VkLongPoll(self.session)

        self.group_id = 155268321


    def run(self):
        for event in self.longpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW:
                if event.to_me:
                    id = event.user_id
                    user = Users.find(id)
                    if user is None:
                        user = Users.add({
                            'id': id
                        })

                    if not self.is_member(id):
                        commands['greet'](self.vk, event)
                    else: 
                        text = clean_text(event.message)
                        if text == 'изменить данные':
                            user = Users.edit(id, { 'stage': 0 })

                        if user.stage < 4:
                            user = Users.edit(id, commands['questionnaire'](self.vk, event, user))

                        if user.stage == 4:
                            if text == 'я прочитал':
                                user = Users.edit(id, { 'approved': True })

                            if not user.approved or text == 'об активности':
                                commands['about'](self.vk, event, user)
                            elif text == 'мои данные':
                                commands['info'](self.vk, event, user)
                            elif user.approved:
                                commands['main_menu'](self.vk, event, user)
                        


    def is_member(self, user_id):
        return bool(self.vk.groups.isMember(access_token=self.token, group_id=self.group_id, user_id=user_id))
    