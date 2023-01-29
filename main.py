import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType

from auth import TOKEN, GROUP_ID    # Желательно хранить данные авторизации в скрытом отдельном файле


""" === USEFUL FUNCTIONS === """


def check_link(message: dict) -> bool:
    """
    :param message: Объект сообщения в формате JSON
    :return: True, если сообщение содержит ссылку в приложении или в тексте сообщения,
        иначе - False
    """
    attachments_list = message['attachments']
    if len(attachments_list) != 0 and attachments_list[0]['type'] == 'link':
        return True
    else:
        if 't.me' in message:
            return True
        for word in message['text'].split():
            if sum(list(map(lambda x: x in word, ['http', ':', '/', '.']))) == 4:
                return True
        return False


def is_follower(user_id: int, group_id: int) -> bool:
    """
    :param user_id: ID пользователя, которого проверяем
    :param group_id: ID группы, в которой ищем пользователя
    :return: True, если пользователь найден в списке участников группы, иначе - False
    """
    if user_id in api.groups.getMembers(group_id=group_id, sort='time_desc'):
        return True
    else:
        return False


def is_first_message(user_id: int, chat_id: int) -> bool:
    """
    :param user_id: ID автора сообщения
    :param chat_id: ID чата, из которого получено сообщение
    :return: True, если пользователь написал в чат впервые, иначе - False
    """
    history = api.messages.getHistory(user_id=chat_id, count=200)['items']
    user_msgs = list(filter(lambda x: x['from_id'] == user_id, history))
    if len(user_msgs) == 1:
        return True
    else:
        return False


""" === MAIN PART === """

session = vk_api.VkApi(token=TOKEN)
api = session.get_api()
longpoll = VkLongPoll(session, group_id=GROUP_ID)


print('===== START =====')
while True:
    try:
        for event in longpoll.listen():

            # Бот реагирует только в том случае, если сообщение приходит в чат
            if event.type == VkEventType.MESSAGE_NEW and event.from_chat:

                # Если в сообщении есть ссылка, будем проверять участника
                if check_link(api.messages.getById(message_ids=event.message_id)['items'][0]):

                    # Если не участник группы и пишет впервые, то удаляем его сообщение и баним
                    if not is_follower(event.user_id, GROUP_ID) and is_first_message(event.user_id, event.peer_id):
                        api.messages.delete(message_ids=event.message_id, delete_for_all=1)
                        api.messages.removeChatUser(chat_id=event.chat_id, user_id=event.user_id)

    except Exception as e:
        print("EXCEPTION: ", e)
