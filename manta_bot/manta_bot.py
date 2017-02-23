from __future__ import unicode_literals
from bender import Bot
from bender import final_step
from bender import next_step


class Manta(Bot):
    commands = {'/m': 'se tira un manta'}

    def __init__(self, *args, **kwargs):
        super(Manta, self).__init__(*args, **kwargs)

    def help(self, *args, **kwargs):
        return self.reply({'text': 'You called for help. None given.'})

