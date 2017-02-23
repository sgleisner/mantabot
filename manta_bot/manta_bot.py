from __future__ import unicode_literals
from bender import Bot
from bender import final_step
from bender import next_step


class Manta(Bot):
    commands = {'/m': 'se tira un manta'}

    def __init__(self, dunno_sticker, go_away_sticker, *args, **kwargs):
        self.dunno_sticker = dunno_sticker
        self.go_away_sticker = go_away_sticker
        super(Manta, self).__init__(*args, **kwargs)
