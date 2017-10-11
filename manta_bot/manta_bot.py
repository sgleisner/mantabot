from __future__ import unicode_literals
from bender import Bot
from bender import final_step
from bender import next_step


class Manta(Bot):
    commands = {
        '/m': 'get_message',
        '/mn': 'new_message',
        '/cancel': 'cancel',
        '/delete': 'delete',
    }

    def __init__(self, *args, **kwargs):
        super(Manta, self).__init__(*args, **kwargs)

    def clear_pending_message(self, *args, **kwargs):
        # delete pending message
        key = self.redis_prefix + 'users:' + str(self._from['id']) + ':pending_message'
        pending_message = self.redis.hgetall(key)
        self.redis.delete(key)
        # delete shortcut from the list of pending shortcuts
        self.redis.srem(self.redis_prefix + 'pending_messages', pending_message.get('shortcut', ''))
        return True

    def shortcut_available(self, shortcut):
        # search for saved commands
        is_saved = self.redis.sismember(self.redis_prefix + 'messages', shortcut)
        # search for pending commands
        is_pending = self.redis.sismember(self.redis_prefix + 'pending_messages', shortcut)
        return not (is_saved or is_pending)

    # bot commands
    def get_message(self, *args, **kwargs):
        shortcut = kwargs.get('rest', u'')

        if shortcut:
            key = self.redis_prefix + 'messages:' + shortcut
            message = self.redis.hgetall(key)
            if message:
                return self.reply(message)
            else:
                return self.reply({'text': "I don't know about that one."})
        else:
            message_id = self.redis.srandmember(self.redis_prefix + 'messages')
            message = self.redis.hgetall(self.redis_prefix + 'messages:' + str(message_id))
            return self.reply(message)

    @next_step('set_message_shortcut')
    def new_message(self, *args, **kwargs):
        message = {'text': u"Alright! Somebody dropped a line too good to be lost in the sands of time. How do we call it?",
                   'reply_markup': {'force_reply': True, 'selective': True}}
        return self.reply(message)

    @next_step('set_message_text')
    def set_message_shortcut(self, *args, **kwargs):
        text = self._message.get('text', u'')
        if text:
            # save the message's shortcut
            if self.shortcut_available(text):
                # save on pending_message
                key = self.redis_prefix + 'users:' + str(self._from['id']) + ':pending_message'
                self.redis.hset(key, 'shortcut', text)

                # add to list of unavailable shortcuts
                self.redis.sadd(self.redis_prefix + 'pending_messages', text)
                return self.reply({'text': u"OK. Send me the text.", 'reply_markup': {'force_reply': True, 'selective': True}})
            else:
                self.reply({'text': u"That name is taken. Choose another one.", 'reply_markup': {'force_reply': True, 'selective': True}})
        else:
            self.reply({'text': u"I need a short name for the message. One word (or emoji) will do.", 'reply_markup': {'force_reply': True, 'selective': True}})

    @next_step('set_message_author')
    def set_message_text(self, *args, **kwargs):
        text = self._message.get('text', u'')
        if text:
            # save the message's text
            key = self.redis_prefix + 'users:' + str(self._from['id']) + ':pending_message'
            self.redis.hset(key, 'text', text)
            return self.reply({'text': u"Who said that?", 'reply_markup': {'force_reply': True, 'selective': True}})
        else:
            self.reply({'text': u"I need a text for the new message.", 'reply_markup': {'force_reply': True, 'selective': True}})

    @next_step('pimp_my_message')
    def set_message_author(self, *args, **kwargs):
        text = self._message.get('text', u'')
        if text:
            # save the message's author
            author = text
            key = self.redis_prefix + 'users:' + str(self._from['id']) + ':pending_message'
            self.redis.hset(key, 'author', author)
            # modify the message text (Markdown)
            pending_message_text = self.redis.hget(key, 'text')
            processed_pending_text = "*{}:*\n    _{}_".format(author, pending_message_text)
            self.redis.hset(key, 'text', processed_pending_text)
            return self.reply({'text': u"Optional: Pimp your message with a photo or sticker (or both!). When ready, send me 'done'.", 'reply_markup': {'force_reply': True, 'selective': True}})
        else:
            self.reply({'text': u"I need someone to blame.", 'reply_markup': {'force_reply': True, 'selective': True}})

    @next_step('save_message')
    def pimp_my_message(self, *args, **kwargs):
        try:
            sticker_file_id = self._message['sticker']['file_id']
            key = self.redis_prefix + 'users:' + str(self._from['id']) + ':pending_message'
            self.redis.hset(key, 'sticker', sticker_file_id)
        except KeyError:
            pass

        try:
            photo_file_id = self._message['photo'][-1]['file_id']
            photo_caption = self._message.get('caption', u'')
            key = self.redis_prefix + 'users:' + str(self._from['id']) + ':pending_message'
            self.redis.hset(key, 'photo', photo_file_id)
            self.redis.hset(key, 'caption', photo_caption)
        except (KeyError, IndexError):
            pass

        try:
            document_file_id = self._message['document']['file_id']
            key = self.redis_prefix + 'users:' + str(self._from['id']) + ':pending_message'
            self.redis.hset(key, 'document', document_file_id)
        except KeyError:
            pass


        text = self._message.get('text', u'')
        if text == 'done':
            pending_message_key = self.redis_prefix + 'users:' + str(self._from['id']) + ':pending_message'
            pending_message = self.redis.hgetall(pending_message_key)
            self.reply(pending_message)
            return self.reply({'text': "Good. Write 'save' to keep it. Cancel anytime with '/cancel'", 'reply_markup': {'force_reply': True, 'selective': True}})
        else:
            self.reply({'text': u"Send me a photo or sticker. When finished, write 'done'.", 'reply_markup': {'force_reply': True, 'selective': True}})

    @final_step
    def save_message(self, *args, **kwargs):
        text = self._message.get('text', u'')

        if not text:
            return False

        if text == 'save':
            pending_message_key = self.redis_prefix + 'users:' + str(self._from['id']) + ':pending_message'
            pending_message = self.redis.hgetall(pending_message_key)

            if not pending_message:
                return self.reply({'sticker': "BQADAQADFgEAAgfchQABGqitkKZMNPEC"})
            # save the message
            message_key = self.redis_prefix + 'messages:' + pending_message['shortcut']
            self.redis.hmset(message_key, pending_message)
            self.redis.sadd(self.redis_prefix + 'messages', pending_message['shortcut'])

            self.clear_pending_message()
            return self.reply({'text': u"Saved. Use it with /m %s" % pending_message['shortcut']}) #### TODO: AVOID CONFLICTING NAMEEEES!!!!
        else:
            self.reply({'text': u"Write 'save' to keep it. Cancel anytime with '/cancel'", 'reply_markup': {'force_reply': True, 'selective': True}})

    @final_step
    def cancel(self, *args, **kwargs):
        self.clear_pending_message()
        self._end_transaction()
        return self.reply({'text': 'Your command has been cancelled. Anything else?', 'reply_markup': {'hide_keyboard': True, 'selective': True}})

    @final_step
    def delete(self, *args, **kwargs):
        self.clear_pending_message()
        self._end_transaction()
        return self.reply({'text': 'Your command has been cancelled. Anything else?', 'reply_markup': {'hide_keyboard': True, 'selective': True}})

    def help(self, *args, **kwargs):
        return self.reply({'text': 'You called for help. None given.'})

