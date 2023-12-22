#!/usr/bin/python3
import chess
import chess.svg
from project.chess_agents.Berkay.MCTSagent import MCTSAgent
from project.chess_utilities.gegeven.example_utility import ExampleUtility
from project.chess_agents.Gegeven.example_agent import ExampleAgent

""" Two agents play against eachother until the game is finished """


def play_self():
    # Setup a clean board
    board = chess.Board()
    board.set_fen("8/2K5/8/2k5/2b5/2B5/2Q5/8")
    # Create the white and black agent
    white_player = MCTSAgent(ExampleUtility(), 5.0)
    white_player.name = "White Player"
    white_player.color = chess.WHITE
    black_player = MCTSAgent(ExampleUtility(), 10.0)
    black_player.name = "Black Player"
    black_player.color = chess.BLACK

    running = True
    turn_white_player = True
    counter = 0

    # Game loop
    while running:
        counter += 1
        move = None

        if turn_white_player:
            move = white_player.calculate_move(board)
            turn_white_player = False
            print("White plays")
        else:
            move = black_player.calculate_move(board)
            turn_white_player = True
            print("Black plays")

        # The move is played and the board is printed
        board.push(move)
        print(board)
        print("----------------------------------------")

        # Check if a player has won
        if board.is_checkmate():
            running = False
            if turn_white_player:
                print("{} wins!".format(black_player.name))
            else:
                print("{} wins!".format(white_player.name))

        # Check for draws
        if board.is_stalemate():
            running = False
            print("Draw by stalemate")
        elif board.is_insufficient_material():
            running = False
            print("Draw by insufficient material")
        elif board.is_fivefold_repetition():
            running = False
            print("Draw by fivefold repitition!")
        elif board.is_seventyfive_moves():
            running = False
            print("Draw by 75-moves rule")


def main():
    play_self()


if __name__ == "__main__":
    main()
