#!/usr/bin/env python

import uuid
from game_backend import State, handle_human_turn, handle_computer_turn, handle_game_over, GameOver, ROWS

def play():
    if ROWS < 35:
        raise AssertionError("Make your terminal full screen")

    state = State()
    game_hash = uuid.uuid4().hex
    try:
        while True:
            turn_num, x, y, swap_count = handle_human_turn(state)
            # add app_intelliegence here

            turn_num, x, y, swap_count = handle_computer_turn(state)
            # and add it here too
    except GameOver:
        handle_game_over(state)

if __name__ == "__main__":
    play()

