# coding: utf-8

from __future__ import absolute_import, print_function

import copy
import os
import subprocess
import sys
import termios
import tty

class COLORS:
    reset = '\033[0m'
    black = '\033[40m'
    red = '\033[41m'
    green = '\033[42m'
    orange = '\033[43m'
    blue = '\033[44m'
    purple = '\033[45m'
    cyan = '\033[46m'
    lightgrey = '\033[47m'
    n4 = '\033[104m'
    n6 = '\033[44m'
    clear = '\033[97m'

B = "🔵"
R = "🔴"
E = "  "
S = COLORS.red + "  "

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


class GameOver(Exception):
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
    __slots__ = [
        "board",
        "turn_num",
        "cur_player",
        "cursor",
        "game_hash"
    ]

    def __init__(self, game_hash):
        if ROWS < 35:
            raise AssertionError("Make your terminal full screen")


        self.board = [[E for _ in range(8)] for _ in range(8)]
        self.turn_num = 0
        self.cur_player = R
        self.cursor = Cursor()
        self.game_hash = game_hash

        # setup middle
        self._set(3, 3, R)
        self._set(3, 4, B)
        self._set(4, 3, B)
        self._set(4, 4, R)

    @property
    def other_player(self):
        if self.cur_player == B:
            return R
        return B

    def board_display(self):
        """
        :returns: a string representing the board for displaying on the terminal
        :rtype: str
        """
        ret = '\n'
        for j, row in enumerate(self.board):
            ret += " " * 5
            for i, cell in enumerate(row):
                if self.cursor.equals(i, j) and self.is_valid_placement(i, j):
                    bg = COLORS.lightgrey
                    cell = self.cur_player
                elif self.cursor.equals(i, j):
                    bg = COLORS.red
                    cell = S
                elif (i+j) % 2:
                    bg = COLORS.n4
                else:
                    bg = COLORS.green
                ret += "%s %s %s" % (bg, cell, COLORS.reset)
            ret += "\n"
        return ret

    def all_valid_placements(self):
        ret = []
        for y in range(8):
            for x in range(8):
                if self.is_valid_placement(x, y):
                    ret.append((x, y))
        return ret

    def is_valid_placement(self, x, y):
        if self.board[y][x] != E:
            return False

        for dy, dx in ((-1, 0), (1, 0), (0, 1), (0, -1)):
            if 0 <= y + dy < 8 and 0 <= x + dx < 8 and \
               self.board[y+dy][x+dx] == self.other_player:
                return True
        return False


    def select(self, x=None, y=None):
        """
        Try selecting the spot the cursor is on. If successful:
        - Set the tile selected
        - Swap tiles that the player has taken
        - Swap the cur_player and increment the turn

        :returns: stats that we can then plug into app_intelligence
        :rtype: (int, int, int, int)
        """
        if x is None and y is None:
            x, y = self.cursor.x, self.cursor.y
        if not self.is_valid_placement(x, y):
            raise SpotNotEmpty()

        self._set(x, y, self.cur_player)
        tiles_to_swap = self.get_swaps(x, y, self.cur_player)
        swap_count = len(tiles_to_swap)
        self._do_swap_tiles(tiles_to_swap)

        turn_num = self.turn_num
        self.end_turn()

        return turn_num, x, y, swap_count

    def end_turn(self):
        self.cur_player = self.other_player
        self.turn_num += 1
        if not self.all_valid_placements():
            raise GameOver()

    def get_swaps(self, x, y, color):
        return (
            self._get_swaps_for_line(reversed(range(x)), [y for _ in range(x)], color) +
            self._get_swaps_for_line(range(x+1, 8), [y for _ in range(x+1, 8)], color) +
            self._get_swaps_for_line([x for _ in range(y)], reversed(range(y)), color) +
            self._get_swaps_for_line([x for _ in range(y+1, 8)], range(y+1, 8), color))

    def _get_swaps_for_line(self, x_range_to_check, y_range_to_check, color):
        """
        Given an x and a y range (one will always be repeating) return tiles to swap
        :param list<int> x_range_to_check:
        :param list<int> y_range_to_check:
        :returns: the tiles that can be swapped
        :rtype: list<(int, int)>
        """
        range_to_check = zip(x_range_to_check, y_range_to_check)
        tiles_to_swap = []
        for i, j in range_to_check:
            if self.board[j][i] == E:
                return []
            if self.board[j][i] != color:
                tiles_to_swap.append((i, j))
                continue
            if self.board[j][i] == color:
                return tiles_to_swap
            raise AssertionError("Unhandled swap")
        return []

    def _do_swap_tiles(self, tiles_to_swap):
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


def draw(state):
    """
    Clear the screen and draw everything
    :param State state:
    """
    os.system('clear')
    display = BANNER
    display += "\n\n     "
    display += "Your turn" if state.cur_player == R else "Computer thinking..."
    display += "\n"
    display += state.board_display()
    display += "\n"
    display += "     Move with ←a w↑ s↓ d→ \n"
    display += "     Select with spacebar \n\n"
    display += "     game_hash: {} \n".format(state.game_hash)

    display += "\n\n"
    display += " This will teach you how to use App Intelligence.\n"
    display += " See the README.md for more info"
    print(display)

def handle_game_over(state):
    """
    Triggered by a GameOverExceptions ount up the tiles
    TODO
    :param State state:
    """
    r_count = 0
    b_count = 0
    for y in range(8):
        for x in range(8):
            piece = state.board[y][x]
            if piece == R:
                r_count += 1
            if piece == B:
                b_count += 1

    if r_count > b_count:
        winner = "You won!"
    elif b_count > r_count:
        winner = "You lost!"
    else:
        winner = "Game tie."

    print("%s\nRed: %d Blue: %d" % (winner, r_count, b_count))


def handle_human_turn(state):
    """
    In a loop, handle cursor movement. If the human hits enter or space,
    try placing a tile and return stats if successful
    :param State state:
    :rtype: int turn_num, int x, int y, int swap_count
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
                continue

def min_step(state, depth_remaining):
    """
    Computer AI: minimax algorithm
    Given the current state, find the opponents best possible move by checking how many
    tiles that move would flip and how many tiles the you would flip in your
    best move.
    TODO: don't we need to -1 the number of swaps?
    :param State state:
    :param int depth_remaining:
    :rtype: (int aggregate_flips, int x, int y) for the most aggregate flips
    """
    depth_remaining -= 1
    possible_moves = []
    for i, j in state.all_valid_placements():
        new_state = copy.deepcopy(state)
        num_swaps = new_state.select(i, j)[-1]
        if depth_remaining:
            num_swaps += max_step(new_state, depth_remaining)[0]
        possible_moves.append((num_swaps, i, j))
    if not possible_moves:
        return (0, -1, -1)
    return max(possible_moves)


def max_step(state, depth_remaining):
    """
    Computer AI: minimax algorithm
    Given the current state, find the best possible move by checking how many
    tiles that move would flip and how many tiles the opponent would flip in their
    best move.
    :param State state:
    :param int depth_remaining:
    :rtype: (int aggregate_flips, int x, int y) for the most aggregate flips
    """
    depth_remaining -= 1
    possible_moves = []
    for i, j in state.all_valid_placements():
        new_state = copy.deepcopy(state)
        num_swaps = new_state.select(i, j)[-1]
        if depth_remaining:
            num_swaps -= min_step(new_state, depth_remaining)[0]
        possible_moves.append((num_swaps, i, j))
    if not possible_moves:
        return (0, -1, -1)
    return max(possible_moves)


def handle_computer_turn(state):
    draw(state)
    _, x, y = max_step(state, 3)
    return state.select(x, y)
