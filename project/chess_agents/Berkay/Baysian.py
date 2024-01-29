from hyperopt import hp, fmin, tpe, Trials, STATUS_OK
import chess
from project.chess_agents.Berkay.MCTSagent import MCTSAgent
from project.chess_agents.Gegeven.example_agent import ExampleAgent
from project.chess_utilities.gegeven.example_utility import ExampleUtility
from project.chess_utilities.tom_utility import TomUtility

import chess
import chess.svg
from project.chess_agents.Berkay.MCTSagent import MCTSAgent
from project.chess_utilities.gegeven.example_utility import ExampleUtility

TestCases = ["8/2K5/8/2k5/2b5/2B5/2Q5/8"]

def test(win, lose, draw, notDone, c, cmb, ccc, cpa, ccp):
    ans = 0
    for i in TestCases:
        ans += play_self(i, win, lose, draw, notDone, c, cmb, ccc, cpa, ccp)
    return ans

def play_self(TestCase,win, lose, draw, notDone, c, cmb, ccc, cpa, ccp):
    # Setup a clean board
    board = chess.Board()
    board.set_fen(TestCase)
    # Create the white and black agent
    white_player = MCTSAgent(TomUtility(), 5.0, win, lose, draw, notDone, c, cmb, ccc, cpa, ccp)
    white_player.name = "White Player"
    black_player = ExampleAgent(ExampleUtility(), 0)
    black_player.name = "Black Player"

    running = True
    turn_white_player = True
    counter = 0

    # Game loop
    while running:
        move = None
        if turn_white_player:
            move = white_player.calculate_move(board)
            turn_white_player = False
            counter += 1
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
                return counter*100
            else:
                print("{} wins!".format(white_player.name))
                return counter


        # Check for draws
        if board.is_stalemate():
            running = False
            print("Draw by stalemate")
            return counter * 10
        elif board.is_insufficient_material():
            running = False
            print("Draw by insufficient material")
            return counter * 10
        elif board.is_fivefold_repetition():
            running = False
            print("Draw by fivefold repitition!")
            return counter * 10
        elif board.is_seventyfive_moves():
            running = False
            print("Draw by 75-moves rule")
            return counter * 10
        elif counter >= 10:
            return counter * 10

# Define the space of hyperparameters to explore
space = {
    'win': hp.uniform('win', 0, 10000),
    'lose': hp.uniform('lose', -10000, 0),
    'draw': hp.uniform('draw', -100, 0),
    'notdone': hp.uniform('notdone', -100, 10),
    'c': hp.uniform('c', 0.1, 1.5),
    'cmb': hp.uniform('cmb', 0.001, 1),
    'ccc': hp.uniform('ccc', 0.001, 1),
    'cpa': hp.uniform('cpa', 0.001, 1),
    'ccp': hp.uniform('ccp', 0.001, 1),
}

# Objective function
def objective(params):
    turns_taken = test(params['win'], params['lose'], params['draw'], params['notdone'],
                            params['c'], params['cmb'], params['ccc'], params['cpa'], params['ccp'])
    return {'loss': turns_taken, 'status': STATUS_OK}

# Run the optimization
trials = Trials()
best = fmin(fn=objective, space=space, algo=tpe.suggest, max_evals=50, trials=trials)

print("Best hyperparameters:", best)


