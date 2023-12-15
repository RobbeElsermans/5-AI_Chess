import copy

from project.chess_agents.agent import Agent
import chess
import chess.engine
from project.chess_utilities.utility import Utility
# from project.chess_agents.robbeAgent import Node
import math
import random


black_player = chess.engine.SimpleEngine.popen_uci(
    "C:/Users/robel/Documents/GitHub/stockfish/stockfish-windows-x86-64-avx2.exe")
# Determine the skill level of Stockfish:
black_player.configure({"Skill Level": 4})
limit = chess.engine.Limit(time=1.0)
"""
De node is 1 enkel object in een tree
Deze classe gaan we gebruiken om de nodes te doorzoeken en bij te houden:
    De state waarin deze node zich in bevind
    hoeveel keer deze bezocht is
    Hoe vaak deze node een win heeft bezorgd
    wie de parent node is
    welke childs deze node heeft
"""

class Node:
    def __init__(self, state: chess.Board, parent=None, move=None):
        self.state = state     # De state waarin het zich bevind
        self.parent = parent    # De parent van de node
        self.children = []      # De mogelijke children
        self.move: chess.Move = move        # De move om deze actie uit te voeren
        self.reward = 0         # 0, 0.5, 1 -> lose, draw, win
        self.moves = 0          # Aantal moves gedaan
        self.parent_moves = 0   # Aantal parent moves

    # geeft weer met een bool ofdat de huidige node een leaf node is.
    # Dit is wanneer de node geen kinderen meer heeft en het is volledig bekeken
    def is_leaf(self) -> bool:
        return len(self.children) == 0 and self.is_expanded()

    # Om een child toe te voegen aan de node
    def add_child(self, child) -> None:
        self.children.append(child)

    # hulp functie om te bepalen ofdat we alle mogelijke childs bekeken hebben.
    def is_expanded(self) -> bool:
        return len(self.children) == len(list(self.state.legal_moves))

    def get_reward(self) -> float:
        return self.reward

# monte carlo tree search agent
class RobbeAgent(Agent):
    def __init__(self, utility: Utility, time_limit_move: float) -> None:
        super().__init__(utility, time_limit_move)
    def calculate_move(self, board: chess.Board):# -> chess.Move:
        moves = board.legal_moves
        print(moves)
        move = monte_carlo_tree_search(initial_board=board,iterations=int(self.time_limit_move))
        return move

# https://www.youtube.com/watch?v=lhFXKNyA0QA&t=462s
#CHECK DEES EN BOUW HIEROP ALLES

# MCTS bestaat uit 4 delen die blijven lopen todat een limiet bereikt is:

    # Selection
        # Hier gaan we d.m.v. een exploration en eplotation rate, beslissen naar waar we gaan.
            #We kunnen hiervoor UGB gebruiken
        # Als we exploration toepassen, gaan we een random selectie nemen van een mogelijke state.
        # Als we explotation toepassen, gaan we al eerder bezochte states gebruiken
def monte_carlo_tree_search(initial_board: chess.Board, iterations: int) -> chess.Move:

    root_node = Node(initial_board)  # Root node has parent = None

    #expand 1ste node
    for move in root_node.state.legal_moves:
        print(move)
        tmp_state = copy.deepcopy(root_node.state)
        tmp_state.push(move)
        child = Node(tmp_state, root_node, move)
        root_node.children.append(child)

    for i in range(iterations):
        print("Iteration " + str(i))

        selected_node = selecting_node(selected_node=root_node)                             # Bepaal de volgende a.d.h.v. een child nodes.
        expanded_child = expansion(selected_node=selected_node, board=selected_node.state)        # Selecteer 1 van de mogelijke acties (childs) van de selected_node
        sim_result = simulation(expanded_child)                       # Simuleer de geselecteerde child node

        print(sim_result[0].state)

        root_node = backpropagation(sim_result)                 # Backpropagatie

    next_node = max(list(root_node.children), key=lambda x: x.get_reward())
    return next_node.move

# Selecteer eerst een child van de geselecteerde node
    # Kan random of met een UCB gewicht
def ucb(curr_node: Node):
    ans = curr_node.reward + 2*(math.sqrt(math.log(curr_node.parent.moves + math.e+(10**-6))/(curr_node.moves +(10**-10))))
    return ans

def selecting_node(selected_node: Node) -> Node:

    # We selecteren een random child. Als er geen childs beschikbaar zijn gaan we ze eerst aanmaken.
   # if selected_node.is_expanded():
   #     pass
   # else:
   #     return selected_node #Als deze nog niet expanded is
   #     pass
        #ran_node = expansion(selected_node, selected_node.state)
        #return ran_node

    if not selected_node.is_leaf():
        #next_node = random.choice(list(selected_node.children))  # We kunnen hier een random selectie volgen

        #Met UCB berekening
        max_UCB_value = 0
        node_max_value = 0
        for node in selected_node.children:
            tmp = ucb(node)
            if tmp > max_UCB_value:
                max_UCB_value = tmp
                node_max_value = node

        next_node = node_max_value

        # next_node = max(list(selected_node.children), key=lambda x: x.get_reward()) # we kunnen hier de beste actie node kiezen die de hoogste win heeft bv.

        return next_node

    return selected_node

# Expansion
    # Hier gaan we alle nodes afgaan en ze toevoegen aan de selected_node
    # Hiervan nemen we een random variable en geven we terug
def expansion(selected_node: Node, board: chess.Board, player=1) -> Node:

    # Als de selected_node geen childs heeft, retourneren we de selected_node
    if len(selected_node.children) == 0:
        return selected_node

    # we gaan over alle mogelijke states die we kunnen bekomen in de huidige state.
   # for move in board.legal_moves:
   #     temp_board_state = copy.deepcopy(board)  # copy van huidige state
   #     temp_board_state.push(move)
   #     new_node = Node(state=temp_board_state, parent=selected_node, move=move)  # Definieer de nieuwe node met de huidige state + move en de parent node
   #     selected_node.add_child(new_node)
    #Wanneer we gedaan hebben, stoppen we

    next_node: Node = None
    # Met UCB berekening gaan we minimax berekenen
    if player:  #eigen speler
        max_UCB_value = -math.inf
        node_max_value = 0
        for node in selected_node.children:
            tmp = ucb(node)
            if tmp > max_UCB_value:
                max_UCB_value = tmp
                node_max_value = node

        next_node = node_max_value
        return (next_node, 0)

    else: # Tegenstander
        min_UCB_value = math.inf
        node_min_value = 0
        for node in selected_node.children:
            tmp = ucb(node)
            if tmp < min_UCB_value:
                min_UCB_value = tmp
                node_min_value = node

        next_node = node_min_value
        return (next_node, 1)

    return selected_node


    # We retourneren een random child dat we gaan bekijken
    #return random.choice(list(selected_node.children))

# Roll out (simulation)
    # Als we bij de expansion in een leaf node terecht komen, is de game ten einde
        # en gaan we een reward moeten geven.
    #Zolang de game niet ten einde is, blijven we opnieuw een simulation uitvoeren met de volgende geselecteerde node (random).
def simulation(sim_node: Node, player = 1) -> (Node, float):
    # We gaan simuleren
    #print(player)
    #print(sim_node.state)
    #print("-----------------------")
    #print()


    #display de chess board in simulation
    #if player:
    #    print("White plays")
    #else:
    #    print("Black plays")

    # The move is played and the board is printed
    #print(board)
    #print("----------------------------------------")

    #check ofdat we in een leaf node terecht komen of dat het spel afgelopen is




    # Bepaal de zet van de huidige (1)
   # if player:
   #     sim_node = expansion(selected_node=sim_node, board=sim_node.state)

    # Bepaal de zet van de volgende (0)
   # else:
        #De zet van de andere partij is random.
        # Kunnen we later nog naar bv. stockfish overbrengen
        # sim_node.state.push(random.choice(list(sim_node.state.legal_moves)))

        # Door stockfish een zet laten bepalen
   #     move = black_player.play(sim_node.state, limit).move
   #     sim_node.state.push(move)

   # return simulation(sim_node, not player)  # recursief diep zoeken totdat er een leaf node komt.

    if (sim_node.state.is_game_over()):
        board = sim_node.state
        if (board.result() == '1-0'):

            return (sim_node, 1)
        elif (board.result() == '0-1'):

            return (sim_node, -1)
        else:
            return (sim_node, 0.5)

    for move in sim_node.state.legal_moves:
        tmp_state = copy.deepcopy(sim_node.state)
        tmp_state.push(move)
        child = Node(tmp_state, sim_node, move)

        sim_node.children.append(child)
    rnd_state = random.choice(list(sim_node.children))

    return simulation(rnd_state, not player)
# Backpropagation
    # We gaan, vanaf de eind node, terug de parents benaderen en het aantal wins instellen dat deze node ons heeft bezorgd
def backpropagation(end_result: (Node, float)):
    reward = end_result[1]
    parent = end_result[0].parent

    end_result[0].reward += reward
    end_result[0].moves += 1

    while(parent.parent != None):
        # parent.reward += reward
        parent.moves += 1

        parent = parent.parent

    parent.moves += 1

    return parent
    # MCTS bestaat uit 4 delen die blijven lopen todat een limiet bereikt is:
        # Selection
            # Hier gaan we d.m.v. een exploration en eplotation rate, beslissen naar waar we gaan.
                #We kunnen hiervoor UGB gebruiken
            # Als we exploration toepassen, gaan we een random selectie nemen van een mogelijke state.
            # Als we explotation toepassen, gaan we al eerder bezochte states gebruiken
        # Expansion
            #Hier gaan we steeds dieper in op een child node tot dat we een leaf node bereiken (geen childs meer).
            #We blijven recursief in de childs gaan totdat de child een leaf node is
        # Roll out (simulation)
            # Als we bij de expansion in een leaf node terecht komen, is de game ten einde
            # en gaan we een reward moeten geven.
        # Backpropagation
            # We gaan, vanaf de eind node, terug de parents benaderen en het aantal wins instellen dat deze node ons heeft bezorgd

