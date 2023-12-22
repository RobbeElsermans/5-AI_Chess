import math
import chess

CONST_C = 1.0
CONST_GEEN_NULL_PROBELEM = 1


class Node():
    def __init__(self, board: chess.Board):
        self.state = board.copy()
        self.children = dict()
        self.parent = None
        self.times_visited = 0
        self.score = 0

    def calcUCB(self):
        if self.parent is None:
            return float('inf')

        if self.parent.times_visited == 0:
            parent_times_visited = 1
        else:
            parent_times_visited = self.parent.times_visited

        exploit = (self.score / (self.times_visited + CONST_GEEN_NULL_PROBELEM))
        explore = CONST_C * math.sqrt(math.log(parent_times_visited) / (self.times_visited + CONST_GEEN_NULL_PROBELEM))
        return exploit + explore
