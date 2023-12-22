import math
import chess

CONST_C = 0.8
CONST_GEEN_NULL_PROBELEM = 1


class Node():
    def __init__(self, board: chess.Board):
        self.state = board.copy()
        self.children = dict()
        self.parent = None
        self.times_visited = 0
        self.score = 0

    def calcUCB(self):
        if self.times_visited == 0:
            return float('inf')

        exploit = self.score / (self.times_visited)
        explore = None
        if self.parent is not None:
            explore = CONST_C * math.sqrt(math.log(self.parent.times_visited) / self.times_visited)
        else:
            explore = CONST_C * math.sqrt(math.log(self.times_visited) / self.times_visited)
        return exploit + explore
