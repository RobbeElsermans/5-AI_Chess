import chess
from project.chess_utilities.gegeven.utility import Utility
from project.chess_agents.Berkay.Hyperparameters import *

class TomUtility(Utility):

    def __init__(self) -> None:
        # Create the board layout
        self.board_layout = []
        for i in range(ord('a'), ord('a') + 8):
            row = [chr(i) + str(j) for j in range(1, 9)]
            self.board_layout.append(row)
        # print(self.board_layout)

        # Get all piece types
        self.piece_types = [chess.PAWN, chess.KNIGHT, chess.BISHOP, chess.ROOK, chess.QUEEN, chess.KING]

    def get_piece_value(self, piece_type: int) -> int:
        if   chess.PAWN   == piece_type: return 1
        elif chess.KNIGHT == piece_type: return 3
        elif chess.BISHOP == piece_type: return 3
        elif chess.ROOK   == piece_type: return 5
        elif chess.QUEEN  == piece_type: return 9
        else: return 0

    # Check how many pieces of a color are left on the board
    def check_material_balance(self, board: chess.Board, color: bool) -> int:
                   # Get all the pieces left of a certain type (for 1 color)
        balances = [len(board.pieces(piece_type=piece_type, color=color)) \
                    # Multiply them by their value
                    * self.get_piece_value(piece_type) \
                    # Do this for all piece types
                    for piece_type in self.piece_types]
        #print(balances)
        return sum(balances)

    # Check which color has more control over the center
    def check_center_control(self, board: chess.Board, color: bool) -> int:
        # Get all locations of all pieces and their values
        pieces_locations = [(board.pieces(piece_type=piece_type, color=color), self.get_piece_value(piece_type))
                            for piece_type in self.piece_types]
        # Flatten the 2-dimensional array
        flattened_array = [(element, value) for sublist, value in pieces_locations for element in sublist]
        # Convert locations to squares
        pieces_squares = [(chess.square_name(square), value) for (square, value) in flattened_array]

        control_scores = [self.position_to_middle(location) * value for location, value in pieces_squares]
        return int(sum(control_scores) / len(control_scores))

    def position_to_middle(self, position: str) -> int:
        for row in range(8):
            for col in range(8):
                if self.board_layout[row][col] in position:
                    # Row & column need to be '+1' since the index start at 0 but the board at '1'
                    distance_to_middle = int((abs(4.5 - (row + 1)) + abs(4.5 - (col + 1))) - 1)
                    score = 5 - distance_to_middle  # Closer to the middle gets a higher score
                    return max(score, 0)  # Ensure the score is at least 1

        return 0  # Return 0 if the target string is not found

    # Check the amount of movement options that pieces have
    def check_piece_activity(self, board: chess.Board, color: bool):
        # Switch player when asking for BLACK pieces legal moves
        board.turn = not board.turn if color == chess.BLACK else board.turn

        # Get all movement options
        movement_options = [board.piece_at(move.from_square).piece_type for move in board.legal_moves]
        #print(movement_options)

        # Switch back if needed
        board.turn = not board.turn if color == chess.BLACK else board.turn

        return len(movement_options)

    # Check the amount of capturable pieces
    def check_capturable_pieces(self, board: chess.Board, color: bool):
        # Switch player when asking for BLACK pieces legal moves
        board.turn = not board.turn if color == chess.BLACK else board.turn

        # Get all captures
        captures = [move for move in board.legal_moves if board.is_capture(move)]
        captures = [(board.piece_at(move.from_square).piece_type, board.piece_at(move.to_square).piece_type)
                    for move in captures]
        # Points are given when a target can be captured
        # Extra points are given if weaker assailants can capture targets
        capture_scores = [self.get_piece_value(target) + (9 - self.get_piece_value(assailant))
                          for assailant, target in captures]
        #print(captures)

        # Switch back if needed
        board.turn = not board.turn if color == chess.BLACK else board.turn

        return sum(capture_scores)

    def board_value(self, board: chess.Board, factors: []):
        n_white, n_black = 0, 0

        n_white += factors[0] * self.check_material_balance(board, chess.WHITE)
        n_white += factors[1] * self.check_center_control(board, chess.WHITE)
        n_white += factors[2] * self.check_piece_activity(board, chess.WHITE)
        n_white += factors[3] * self.check_capturable_pieces(board, chess.WHITE)

        n_black += factors[0] * self.check_material_balance(board, chess.BLACK)
        n_black += factors[1] * self.check_center_control(board, chess.BLACK)
        n_black += factors[2] * self.check_piece_activity(board, chess.BLACK)
        n_black += factors[3] * self.check_capturable_pieces(board, chess.BLACK)

        if board.is_check():  # If white is in check
            n_white /= 2
            n_black *= 2

        checks = [board.gives_check(move) for move in board.legal_moves]
        if any(checks):  # Return True if any true value is in the list
            n_white *= 2
            n_black /= 2



        return n_white - n_black


if __name__ == "__main__":
    # https://www.chess.com/analysis?tab=analysis
    c_board = chess.Board()
    utility = TomUtility()

    # Start condition
    print(c_board)
    print("Board value: ", utility.check_capturable_pieces(c_board, chess.WHITE))
    print()

    # Middle of the game
    c_board.set_fen("7r/4k1p1/rp1p4/5pN1/2QPb2P/6K1/1PN1P3/4n3 w - - 0 1")
    print(c_board)
    print("Board value: ", utility.check_capturable_pieces(c_board, chess.WHITE))
    print()

    # Closer to the end
    c_board.set_fen("8/8/1n2k1p1/8/3RP3/1B6/8/4K2b w - - 0 1")
    print(c_board)
    print("Board value: ", utility.check_capturable_pieces(c_board, chess.WHITE))
    print()