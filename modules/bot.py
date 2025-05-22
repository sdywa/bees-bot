import json

import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType

from .commands import commands


class Bot:
    def __init__(self, token):
        self.token = token
        self.session = vk_api.VkApi(token=token)
        self.vk = self.session.get_api()
        self.longpoll = VkLongPoll(self.session)

        self.group_id = 155268321
        self.i = 0


    def run(self):
        for event in self.longpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW:
                if event.to_me:
                    msg = event.text.lower()
                    id = event.user_id

                    if not self.is_member(id):
                        commands['greet'](self.vk, event)
                    else: 
                        commands['questionnaire'](self.vk, event, self.i)
                        self.i += 1


    def is_member(self, user_id):
        return bool(self.vk.groups.isMember(access_token=self.token, group_id=self.group_id, user_id=user_id))
    