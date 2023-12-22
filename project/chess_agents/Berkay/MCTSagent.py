import random
from abc import ABC
import chess
from project.chess_utilities.gegeven.utility import Utility
from project.chess_agents.Berkay.node import Node
from project.chess_agents.Berkay.agent import Agent
from graphviz import Digraph

from project.chess_agents.Berkay.visual import visualize_tree

import time

"""A generic agent class"""


class MCTSAgent(Agent):

    def __init__(self, utility: Utility, time_limit_move: float) -> None:
        """Setup the Search Agent"""
        super().__init__(utility, time_limit_move)
        self.tree = None
        self.color = None

    def calculate_move(self, board: chess.Board):

        if self.color is None:
            self.color = board.turn

        if self.tree is None:
            self.tree = Node(board.copy())
            self.tree.times_visited += 1
        else:
            prev_move = board.peek()
            if prev_move in self.tree.children:
                self.tree = self.tree.children[prev_move]
            else:
                new_node = Node(board.copy())
                new_node.parent = self.tree
                self.tree.children[prev_move] = new_node
                self.tree = new_node

        start_time = time.time()
        test = 0

        # MCST
        while time.time() - start_time < self.time_limit_move:
            leaf = self.selection(self.tree)
            child = self.expansion(leaf)
            result = self.simulation(child)
            self.backprop(result, child)
            test += 1
        print("hoevele keer gedaan deze loop: ", test)

        best_moves = []
        best_score = -float('inf')
        nextStates = self.tree.children

        for move in list(board.legal_moves):
            if move in nextStates:
                if nextStates[move].score > best_score:
                    best_score = nextStates[move].score
                    best_moves = [move]
                elif nextStates[move].score == best_score:
                    best_moves.append(move)

        tree_graph = visualize_tree(self.tree)
        tree_graph.render('mcts_tree', format='svg', view=True)

        print("Best Score: ", best_score)
        best_move = random.choice(best_moves)
        self.tree = nextStates[best_move]
        return best_move

    def selection(self, tree: Node):
        while tree.children:
            bestScore = float('-inf')
            bestChildren = []

            for child in tree.children.values():
                child_score = child.calcUCB()
                if child_score > bestScore:
                    bestScore = child_score
                    bestChildren = [child]
                elif child_score == bestScore:
                    bestChildren.append(child)
            if bestScore <= tree.calcUCB():
                break

            tree = random.choice(bestChildren)

        return tree

    def expansion(self, leaf: Node):  # voegt nodes toe
        legal_moves = leaf.state.legal_moves
        untried_moves = [move for move in legal_moves if move not in leaf.children]

        if not untried_moves:
            return leaf

        move = random.choice(untried_moves)

        new_state = leaf.state.copy()
        new_state.push(move)
        newChild = Node(new_state)
        newChild.parent = leaf
        leaf.children[move] = newChild

        return newChild  # een van de nieuwe Nodes die gemaakt zijn

    def simulation(self, child: Node, depth_limit=6):  # rollout: geeft de reward
        current_state = child.state.copy()
        for i in range(depth_limit):

            if current_state.is_game_over():
                break

            legal_moves = list(current_state.legal_moves)
            if not legal_moves:
                break

            move = random.choice(legal_moves)
            current_state.push(move)

        # uitkomst
        if current_state.is_game_over():
            if current_state.is_checkmate():
                winner = current_state.outcome().winner
                if winner == self.color:
                    return 1000
                else:
                    return -1000
            else:
                return -1
        else:
            return 0

    def backprop(self, result: float, child: Node):
        child.times_visited += 1
        child.score += result
        child = child.parent
        while child.parent is not None:
            child.times_visited += 1
            child.parent.score += result
            child = child.parent
        child.times_visited += 1
