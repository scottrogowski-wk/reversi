#!/usr/bin/env python

import uuid

from game_backend import State, handle_human_turn, handle_computer_turn, ROWS

def play():
    if ROWS < 35:
        raise AssertionError("Make your terminal full screen")

    state = State()
    game_hash = uuid.uuid4().hex
    while True:
        turn_num, x, y, swap_count = handle_human_turn(state)
        # add app_intelliegence here
        turn_num, x, y, swap_count = handle_computer_turn(state)
        # and add it here too

if __name__ == "__main__":
    play()

