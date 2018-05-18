#!/usr/bin/env python
# pylint: disable=W0511,W0612,W0611,R0902,C0301

import uuid
from game_backend import (State, handle_human_turn, handle_computer_turn,
                          handle_game_over, GameOver)
from app_intelligence import analytics

# TODO setup your reporter here

# TODO put your AppIntelligence ReversiGameTurn class here

def play():
    game_hash = uuid.uuid4().hex
    state = State(game_hash)
    try:
        while True:
            turn_num, x, y, swap_count = handle_human_turn(state)
            # TODO add .send code here

            turn_num, x, y, swap_count = handle_computer_turn(state)
            # TODO add .send code here

    except GameOver:
        handle_game_over(state)

if __name__ == "__main__":
    play()

