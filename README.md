# reversi

This is also in presentation form

TODO still
1. move the presentation over to here
2. game_hash goes in the game
3. either setup logging or don't
4. be sure all the rules are correct
5. computer seems to still make puzzling moves. Investigate
6. cleanup backend code

# Final reversi.py

```
#!/usr/bin/env python
# pylint: disable=W0511,W0612,W0611,R0902,C0301

import uuid
from game_backend import (State, handle_human_turn, handle_computer_turn,
                          handle_game_over, GameOver)
from app_intelligence import analytics

ENDPOINT_URL = analytics.Hosts.SDLC_DEV
reporter = analytics.AnalyticsReporter(ENDPOINT_URL)

class ReversiGameTurn(object):
    """A single turn in a reversi learning game"""

    def __init__(self, value=None, swap_count=None, turn_num=None,
                 player=None, game_hash=None, y=None, x=None):
        """
        :param value: A simple count of an action, should always be 1
        :param swap_count: (integer) The number of pieces of the opposing player flipped on this turn
        :param turn_num: (integer) A simple turn count. Human players are even. Computer is odd
        :param player: (string) human|computer
        :param game_hash: (string) A unique hash generated at the start of each reversi game
        :param y: (integer) The y position where the piece was placed
        :param x: (integer) The x position where the piece was placed
        """
        self.guid = None
        self.category = 'learning'
        self.action = 'reversi-game-turn'
        self.version = '1'
        self.dimension_meta = {
            'swap_count': {
                'type': 'integer',
                'required': True,
                'autofill': False
            },
            'turn_num': {
                'type': 'integer',
                'required': True,
                'autofill': False
            },
            'player': {
                'type': 'string',
                'required': True,
                'autofill': False
            },
            'game_hash': {
                'type': 'string',
                'required': True,
                'autofill': False
            },
            'y': {
                'type': 'integer',
                'required': True,
                'autofill': False
            },
            'x': {
                'type': 'integer',
                'required': True,
                'autofill': False
            },
        }

        self.mixins = [
        ]

        self.value_meta = {
            'type': 'integer'
        }

        self.value = value
        self.dimensions = {
            'swap_count': swap_count,
            'turn_num': turn_num,
            'player': player,
            'game_hash': game_hash,
            'y': y,
            'x': x,
        }


def play():
    state = State()
    game_hash = uuid.uuid4().hex
    try:
        while True:
            turn_num, x, y, swap_count = handle_human_turn(state)
            reporter.send(ReversiGameTurn(
                value=1,

                turn_num=turn_num,
                x=x,
                y=y,
                swap_count=swap_count,

                game_hash=game_hash,
                player="human",
                ))

            turn_num, x, y, swap_count = handle_computer_turn(state)
            reporter.send(ReversiGameTurn(
                value=1,

                turn_num=turn_num,
                x=x,
                y=y,
                swap_count=swap_count,

                game_hash=game_hash,
                player="computer",
                ))

    except GameOver:
        handle_game_over(state)

if __name__ == "__main__":
    play()


```
