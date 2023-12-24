from project.chess_agents.agent import Agent
import chess
from project.chess_utilities.utility import Utility
import time
import random

'''
    2) problemen
        - White Rook moves left and right (only move for white)
        - In check mate the system crashes
'''

class TomAgent(Agent):

    # Initialize your agent with whatever parameters you want
    def __init__(self, utility: Utility, time_limit_move: float) -> None:
        super().__init__(utility, time_limit_move)
        self.name = "Tom search agent"
        self.author = "Tom"

        # Create the board layout
        self.board_layout = []
        for i in range(ord('a'), ord('a') + 8):
            row = [chr(i) + str(j) for j in range(1, 9)]
            self.board_layout.append(row)
        #print(self.board_layout)
        

    # This agent does not perform any searching, it sinmply iterates trough all the moves possible and picks the one with the highest utility
    def calculate_move(self, board: chess.Board):
        
        start_time = time.time()

        # If the agent is playing as black, the utility values are flipped (negative-positive)
        flip_value = 1 if board.turn == chess.WHITE else -1

        # 1) Tree Representation:
        # Represent the possible moves and their outcomes as a tree structure.
        # Each node in the tree represents a game state, and the edges represent possible moves.
        iterations = 37
        moves = board.legal_moves
        results = []
        for _ in range(iterations):
            move = self.select(moves, board)
            temp_board = board.copy()
            new_move = self.expand(move, temp_board)
            simulation_result = self.simulate(new_move, temp_board)
            #self.backpropagate(new_move, temp_board, simulation_result) # not needed since the board is a copy()

            # add the result of the iteration
            move_in_result = False
            for index in range(len(results)):
                if results[index][0] == move:
                    results[index][1] += simulation_result
                    move_in_result = True

            if not move_in_result: results.append([move, simulation_result])
            # 6) Repeat:
            # Repeat the process (selection, expansion, simulation, backpropagation) for a specified number of iterations or until a time limit is reached.

            # Check if the maximum calculation time for this move has been reached
            if time.time() - start_time > self.time_limit_move:
                break

        random_move = random.sample(list(board.legal_moves), 1)[0]
        return self.select_best_move(results) if len(results) > 0 else random_move

    def getPieceScore(self, moveStr):
        if "K" in moveStr: return 0
        elif "Q" in moveStr: return 9
        elif "B" in moveStr: return 3
        elif "N" in moveStr: return 3
        elif "R" in moveStr: return 5
        else: return 1
    def getDestToMiddle(self, dest):
        # The middle of the board is more advantageous than the rest
        rows = len(self.board_layout)
        cols = len(self.board_layout[0])

        for row in range(rows):
            for col in range(cols):
                if self.board_layout[row][col] in dest:
                    distance_to_middle = abs(row - int(row / 2)) + abs(col - int(col / 2))
                    score = 8 - distance_to_middle  # Closer to the middle gets a higher score
                    return max(score, 1)            # Ensure the score is at least 1
        # Return 0 if the target string is not found
        return 0

    def select(self, moves, board):
        # 2) Selection (Tree Traversal):
        # Start at the root node and traverse the tree based on a selection policy.
        # One common policy is the Upper Confidence Bound (UCB) formula,
        # which balances exploration (trying new moves) and exploitation (choosing moves with high estimated value).

        # Use UCB to select a child node
        # Implement tree traversal logic here how to implement

        ''' Data:
            - K = King, Q = Queen, B = bishop, N = knight, R = rook, P = pawn
            - 1 - 8 = rows (up/down), a - f = columns (left/right)
            - Nh3 = Knight can move to row 3 column h (pawn moves do not contain p beforehand: e3)
            - x = indication that a piece can be taken from that spot
            -       Nxe4 = Knight can take piece at e4
            - + = Indicates a check
        '''
        ubc_move = None
        ubc_score = 0
        for move in moves:
            moveStr = move.uci()
            exploitation, exploration = 0, 0
            pos = moveStr[0:2]  # (first 2 characters of MoveString indicate the current position)
            dest = moveStr[2:4] # (the following 2 characters of MoveString indicate the destination)
            # Exploit the current situation
            if (board.is_check()):
                # Move king when in check
                exploitation = 64 if "K" in moveStr else 0
            else:
                # Check piece type
                p_type = str(board.piece_at(chess.parse_square(pos)))
                p_type_value = self.getPieceScore(p_type)

                # Destination
                pos_value = self.getDestToMiddle(dest)

                # Check if piece can take an opponent piece
                o_type_value = 0
                if board.is_capture(move):
                    o_type = str(board.piece_at(chess.parse_square(dest)))
                    o_type_value = 16 if board.gives_check(move) else self.getPieceScore(o_type)

                # Calculate exploitation
                exploitation = p_type_value * pos_value + o_type_value

            # Explore the board
            exploration = random.randint(0, 4)

            # Check the ubc score
            if ubc_score < exploitation + exploration:
                # if the score is higher take new value and move
                ubc_score = exploitation + exploration
                ubc_move = move
            elif ubc_score == exploitation + exploration:
                # if the score is the same randomly pick the old or new move
                ubc_move = move if random.randint(0, 1) == 1 else ubc_move
            else:
                # Keep old value and move
                pass
        #print(ubc_move)
        return ubc_move

    def expand(self, move, board):
        # 3) Expansion:
        # Expand the tree by adding child nodes for unexplored moves from the selected node.
        # This step simulates making a move and creates a new node in the tree for the resulting game state.

        # Add a child node for an unexplored move
        # Implement expansion logic here

        board.push(move)
        new_moves = list(board.legal_moves)
        return new_moves[random.randint(0, len(new_moves)-1)]

    def get_sim_result(self, board):
        result = board.result()
        if result == "1-0":
            return 1  # Win
        elif result == "0-1":
            return -1  # Loss
        else:
            return 0  # Draw

    def simulate(self, new_move, board):
        # 4) Simulation (Rollout):
        # Perform a Monte Carlo simulation from the newly added node.
        # This involves playing out the game randomly or using a simple heuristic until a terminal state (win, lose, or draw) is reached.

        # Simulate a random game from the current node
        # Implement simulation (rollout) logic here

        board.push(new_move)
        while not board.is_game_over():
            new_moves = list(board.legal_moves)
            new_move = new_moves[random.randint(0, len(new_moves) - 1)]
            board.push(new_move)

        return self.get_sim_result(board)

    def backpropagate(self, new_move, board, result):
        # 5) Backpropagation:
        # Update the statistics of all nodes along the path from the expanded node to the root based on the outcome of the simulation.
        # This involves updating visit counts and accumulated scores.

        # Update visit counts and scores for all nodes in the path
        # Implement backpropagation logic here

        while new_move != board.peek(): board.pop()

    def select_best_move(self, results):
        # 7) Move Selection:
        # After the simulations, choose the move with the highest estimated value based on the statistics collected during the simulations.

        # Choose the move with the highest estimated value
        # Implement move selection logic here

        # Take the move with the best result
        best_move, score = results[0]
        for index in range(len(results)):
            if results[index][1] > score:
                # if the score is higher take new value and move
                best_move = results[index][0]
                score = results[index][1]
            elif results[index][1] == score:
                # if the score is the same randomly pick the old or new move
                best_move = results[index][0] if random.randint(0, 1) == 1 else best_move
            else:
                # Keep old value and move
                pass

        #print(best_move, str(best_move), type(best_move))

        return best_move