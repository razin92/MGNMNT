import telepot

def check_msg(bot_body):

    def check(msg):
        content_type, chat_type, chat_id = telepot.glance(msg)
        if content_type == 'text':
            return bot_body(msg)

    return check