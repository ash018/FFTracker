from firebase_admin import messaging


MSG_DICT = {
    'Private': 0,
    'Group': 1,
    'Broadcast': 2,
}

MSG_CHOICES = tuple((value, key) for key, value in MSG_DICT.items())


def send_msg_payload(message, recipient):
    file_urls = ''
    if message.attachments:
        file_urls = '#<brk>#'.join(message.attachments)
    try:
        message = messaging.Message(
            data={
                'type': 'message',
                'text': message.text,
                'file_urls': file_urls,
                'sender': str(message.sender.id),
                'sender_name': str(message.sender.full_name),
                'sender_image': str(message.sender.image),
                'thread_id': str(message.group.id),
            },
            token=recipient.fb_token,
        )
        response = messaging.send(message)
        # print(response)
        return response
    except Exception as e:
        # print('Error:' + str(e))
        return str(e)


def send_group_message(message, group):
    resp = []
    for user in group.members.all():
        if user != message.sender:
            resp.append({'user': user.id, 'resp': send_msg_payload(message, user)})
    return resp

