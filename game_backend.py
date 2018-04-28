# coding: utf-8

from __future__ import absolute_import, print_function

import os
import random
import sys
import subprocess
import termios
import tty
import uuid

class FG:
    red='\033[31m'
    black='\033[30m'
    white='\033[97m'

class BG:
    black='\033[40m'
    red='\033[41m'
    green='\033[42m'
    orange='\033[43m'
    blue='\033[44m'
    purple='\033[45m'
    cyan='\033[46m'
    lightgrey='\033[47m'
    n4 = '\033[104m'
    n6 = '\033[44m'

RESET_COLOR = '\033[0m'

B = "🔵"
R = "🔴"
S = FG.red + " "

ROWS, COLUMNS = map(int, subprocess.check_output(['stty', 'size']).split())

H_PADDING = (COLUMNS - 8 * 3) / 2
V_PADDING = (ROWS - 8) / 2

BANNER = """\
 __          __        _    _
 \ \        / /       | |  (_)
  \ \  /\  / /__  _ __| | _____   ____ _
   \ \/  \/ / _ \| '__| |/ / \ \ / / _` |
    \  /\  / (_) | |  |   <| |\ V / (_| |
  ___\/  \/ \___/|_|  |_|\_\_| \_/ \__,_|
 |  __ \                       (_)
 | |__) |_____   _____ _ __ ___ _
 |  _  // _ \ \ / / _ \ '__/ __| |
 | | \ \  __/\ V /  __/ |  \__ \ |
 |_|  \_\___| \_/ \___|_|  |___/_|
 """


class SpotNotEmpty(Exception):
    """
    When the player tries to click on a spot that's taken
    """
    pass


def getch():
    """
    Get the key without pressing return
    """
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(fd)
        char = sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return char


class Cursor(object):
    """
    Manage cursor state on the board
    """
    def __init__(self):
        self.x = 0
        self.y = 0

    def reset(self):
        self.x = 0
        self.y = 0

    def equals(self, x, y):
        return (x, y) == (self.x, self.y)

    def up(self):
        if self.y > 0:
            self.y -= 1

    def down(self):
        if self.y < 7:
            self.y += 1

    def right(self):
        if self.x < 7:
            self.x += 1

    def left(self):
        if self.x > 0:
            self.x -= 1


class State(object):
    """
    Manages all game state including tracking the board, who's turn it is, and
    where the cursor is
    """
    def __init__(self, player_1=R):
        self.board = [[' ' for _ in range(8)] for _ in range(8)]
        self.turn_num = 0
        self.cur_player = player_1
        self.cursor = Cursor()

        # setup middle
        self._set(3, 3, R)
        self._set(3, 4, B)
        self._set(4, 3, B)
        self._set(4, 4, R)

    def board_display(self):
        """
        :returns: a string representing the board for displaying on the terminal
        :rtype: str
        """
        ret = '\n'
        for j, row in enumerate(self.board):
            ret += " " * 5
            for i, cell in enumerate(row):
                if self.cursor.equals(i, j) and not cell.strip():
                    bg = BG.purple
                    cell = self.cur_player
                elif self.cursor.equals(i, j):
                    bg = BG.red
                    cell = S
                elif (i+j) % 2:
                    bg = BG.n4
                else:
                    bg = BG.n6
                ret += "%s %s  %s" % (bg, cell, RESET_COLOR)
            ret += "\n"
        return ret

    def select(self):
        """
        Try selecting the spot the cursor is on. If successful:
        - Set the tile selected
        - Swap tiles that the player has taken
        - Swap the cur_player and increment the turn

        :returns: stats that we can then plug into app_intelligence
        :rtype: (int, int, int, int)
        """
        x, y = self.cursor.x, self.cursor.y
        if self.board[x][y].strip():
            raise SpotNotEmpty()
        self._set(x, y, self.cur_player)

        swap_count = sum((
            self._process_possible_swaps(reversed(range(x)), [y for _ in range(x)]),
            self._process_possible_swaps(range(x+1, 8), [y for _ in range(x+1, 8)]),
            self._process_possible_swaps([x for _ in range(y)], reversed(range(y))),
            self._process_possible_swaps([x for _ in range(y+1, 8)], range(y+1, 8))
            ))

        turn_num = self.turn_num
        if self.cur_player == R:
            self.cur_player = B
        else:
            self.cur_player = R
            self.turn_num += 1

        return turn_num, x, y, swap_count

    def _process_possible_swaps(self, x_range_to_check, y_range_to_check):
        """
        Given an x and a y range (one will always be repeating) determine tiles
        to swap, if any.
        :param list<int> x_range_to_check:
        :param list<int> y_range_to_check:
        :returns: the number of tiles swapped
        :rtype: int
        """
        range_to_check = zip(x_range_to_check, y_range_to_check)
        tiles_to_swap = []
        for i, j in range_to_check:
            if not self.board[j][i].strip():
                return 0
            if self.board[j][i] != self.cur_player:
                tiles_to_swap.append((i, j))
                continue
            if self.board[j][i] == self.cur_player:
                self._swap_tiles(tiles_to_swap)
                return len(tiles_to_swap)
            raise AssertionError("Unhandled swap")
        return 0

    def _swap_tiles(self, tiles_to_swap):
        """
        Given a list of tiles to swap, swap them all
        :param list<(int, int)> tiles_to_swap
        """
        for x, y in tiles_to_swap:
            self._set(x, y, self.cur_player)

    def _set(self, x, y, color):
        """
        TODO
        """
        self.board[y][x] = color


def get_logging_box():
    return ""


def draw(state):
    """
    Single function to clear the screen and draw everything
    :param State state:
    """
    os.system('clear')
    display = BANNER
    display += "\n\n       "
    display += "Your turn" if state.cur_player == R else "Computer thinking..."
    display += "\n"
    display += state.board_display()
    display += "\n"
    display += "     Move with ←a w↑ s↓ d→ \n"
    display += "     Select with spacebar \n"
    display += "     https://www.google.com \n"
    display += get_logs()
    display += "\n\n"
    display += " This will teach you how to use App Intelligence.\n"
    display += " See the README for more info"
    display += '\n' * (ROWS - len(display.split('\n')) - 1)
    print(display)


def handle_human_turn(state):
    """
    In a loop, handle cursor movement. If the human hits enter or space,
    try placing a tile and return stats if successful
    :param State state:
    :rtype: int, int, int, int
    """
    while True:
        draw(state)
        ch = getch()
        if ch in ("\x03", "\x04"):
            raise KeyboardInterrupt
        elif ch == "w":
            state.cursor.up()
        elif ch == "s":
            state.cursor.down()
        elif ch == "a":
            state.cursor.left()
        elif ch == "d":
            state.cursor.right()
        elif ch in (" ", "\r"):
            try:
                return state.select()
            except SpotNotEmpty:
                print("SpotNotEmpty")
                continue

def handle_computer_turn(state):
    """
    TODO
    :param State state:
    :rtype: int, int, int, int
    """
    while True:
        draw(state)
        ch = random.choice(("w", "s", "a", "d", " "))
        if ch == "w":
            state.cursor.up()
        elif ch == "s":
            state.cursor.down()
        elif ch == "a":
            state.cursor.left()
        elif ch == "d":
            state.cursor.right()
        elif ch in (" ", "\r"):
            try:
                return state.select()
            except SpotNotEmpty:
                print("SpotNotEmpty")
                continue
