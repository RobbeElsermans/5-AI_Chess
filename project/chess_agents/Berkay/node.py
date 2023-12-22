import math
import chess
from project.chess_agents.Berkay import Hyperparameters


class Node():
    def __init__(self, board: chess.Board):
        self.state = board.copy()
        self.children = dict()
        self.parent = None
        self.times_visited = 0
        self.score = 0

    def calcUCB(self, c):
        if self.times_visited == 0:
            return float('inf')

        exploit = self.score / (self.times_visited)
        explore = None
        if self.parent is not None:
            explore = c * math.sqrt(math.log(self.parent.times_visited) / self.times_visited)
        else:
            explore = c * math.sqrt(math.log(self.times_visited) / self.times_visited)
        return exploit + explore
