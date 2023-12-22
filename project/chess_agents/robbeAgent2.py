import copy
import math
import random
import time

from project.chess_agents.agent import Agent
import chess
import chess.engine
from project.chess_utilities.utility import Utility
import csv

class Node:
    def __init__(self, state, parent=None, move=None, piece=True, weight=1):
        self.state: chess.Board = state
        self.parent: Node = parent
        self.by_move: chess.Move = move
        self.moves: int = 0
        self.reward: float = 0
        self.children: [Node] = []
        self.weight: int = weight
        self.pion: bool = piece  #Welk pion deze is.

    def __str__(self):
        return f'piece: {self.pion}, moves: {self.moves}, reward: {self.reward}, amount_children: {len(self.children)}, by_move: {self.by_move}, has_parents: {not (self.parent == None)}, ID: {id(self)}'

    def add_child(self, child):
        self.children.append(child)

    def has_childs(self ) -> bool:
        return len(self.children) > 0

class RobbeAgent2(Agent):
    def __init__(self, utility: Utility, time_limit_move: float) -> None:
        """Setup the Search Agent"""
        super().__init__(utility, time_limit_move)

        self.csvFile = r'C:\Users\robel\Documents\GitHub\5-AI_Chess\output\output_' + time.strftime("%Y%m%d-%H%M%S") + "_.csv"
        self.has_write_header = False
        self.moves = 0

    def calculate_move(self, board: chess.Board) -> chess.Move:
        mcst = MonteCarloAlgorithm(board, int(self.time_limit_move))
        best_move = mcst.run()
        mcst.stats()

        with open(self.csvFile, 'a', newline='') as f:
            writer = csv.writer(f)
            if not self.has_write_header:
                writer.writerow(mcst.get_stats()[1])
                self.has_write_header = True

            stats = mcst.get_stats()[0]
            stats[0] = self.moves
            writer.writerow(stats)
        self.moves += 1
        return best_move
class MonteCarloAlgorithm:
    def __init__(self, board_state: chess.Board, iterations: float = 10.0):
        self.initial_board = board_state
        self.iterations: float = iterations
        self.root_node: Node = Node(board_state) #define the root node

        # statistics
        self.completed_iterations = 0
        self.total_simulations = 0
        self.total_wins = 0
        self.total_losses = 0
        self.total_end_games = 0
        self.max_reward = 0
    def stats(self):

        print(f"Completed iterations: {self.completed_iterations}\r\n"
              f"total_simulations: {self.total_simulations}\r\n"
              f"average simulations per iteration: {self.total_simulations / self.completed_iterations}\r\n"
              f"max reward: {self.max_reward}\r\n"
              f"total_wins: {self.total_wins}\r\n"
              f"total_losses: {self.total_losses}\r\n\r\n"
              f"win/iteration : {self.total_wins / self.completed_iterations}\r\n\r\n\r\n")

    def get_stats(self) -> [[], []]:
        return [[0,self.completed_iterations, self.total_simulations, self.total_simulations / self.completed_iterations, self.max_reward, self.total_wins, self.total_losses, self.total_wins / self.completed_iterations],
                ["round","Completed_iteration","total_simulations","average_sim_per_it","max_reward","total_wins", "total_losses","total_wins_per_it"]]


    def run(self) -> chess.Move:
        """Run the Monte Carlo
        :return: the requireded move to be played
        """

        #populate the root node
        #is zoizo een wit chess stuk
        for move in self.initial_board.legal_moves:
            temp_board = self.initial_board.copy()
            temp_board.push(move)
            child = Node(temp_board, self.root_node, move, True)
            self.root_node.add_child(child)

        # for move in self.initial_board.legal_moves:
        #     print(move)
        #     print(self.root_node.state.is_capture(move))
        #     print(self.root_node.state.is_into_check(move))
        #     print(self.root_node.state.is_en_passant(move))
        # Voer iteraties uit totdat de tijd op is
        set_time = time.time()

        #om met een timer te werken
        while(time.time() - set_time < self.iterations):
        #while self.completed_iterations < 600: # zolang er geen x-aantal iteraties gebeurd zijn
            self.completed_iterations += 1

            leaf_node = self.selection(self.root_node)
            child_node = self.expansion(leaf_node)
            result = self.simulate(child_node)
            self.backpropagation(result, child_node)

        # bepaal de node met hoogste reward
        best_node: Node = max(self.root_node.children, key=lambda child: child.reward)
        self.max_reward = best_node.reward
        return best_node.by_move

    def selection(self, node: Node) -> Node:
        """Select de beste move bekomen door de eval_functie.
        Zal blijven zoeken, in functie van de eval_functie, totdat er een leaf gevonden wordt (geen childs).
        We nemen dan deze leaf.
        :param node: the
        :return: the
        """

        if node.has_childs():
            # bepaal de eval_functie voor elke child in de node
            eval: float = 0
            selected_node: Node = node.children[0]
            # not_visited_nodes = [node for node in ]
            for child in node.children:
                new_eval = self.eval_function(child)
                if new_eval > eval:
                    eval = new_eval
                    selected_node = child
            # print(list(n for n in node.children if n.moves == 0))
            # Als alle nodes nog niet bezocht zijn, selecteer dan een random node die nog niet bezocht is
            if eval == math.inf:
                selected_node = random.choice(list(n for n in node.children if n.moves == 0))

            return self.selection(selected_node) #recursieve functie

        # heeft geen child, dus is een leaf
        return node

        pass
    def expansion(self, node: Node, player:bool=chess.WHITE) -> Node:

        # De game is definitief gedaan en expansion is dus niet nuttig
        #if node.state.is_checkmate or node.state.is_stalemate():
        #    return node

        #if node.moves == 0:  # Wanneer we hier nog geen kansen hebben, voeren we eerst de simulatie uit.
        #    return node
        # Anders expanden we de leaf node en nemen we een random child hiervan

        # We bekijken alle mogelijke moves van de node en we voegen ze toe aan de node
        for move in node.state.legal_moves:
            temp_state = node.state.copy()
            temp_state.push(move)

            new_child: Node = Node(temp_state, node, move, not node.pion) #voeg een zet toe van de andere pion
            node.add_child(new_child)

        # kies een willekeurige node hiervan
        if node.has_childs():
            new_node = random.choice(node.children)
            return new_node
        return node

    def simulate(self, node: Node) -> float:
        # create a copy of the board and node
        # sim_board : chess.Board = node.state.copy()
        sim_state: chess.Board = node.state.copy() #copy zodat er geen referenties zijn

        # start_player: bool = True

        # Speel tegen stockfish
        # black_player = chess.engine.SimpleEngine.popen_uci("C:/Users/robel/Documents/GitHub/stockfish/stockfish-windows-x86-64-avx2.exe")
        # Determine the skill level of Stockfish:
        # black_player.configure({"Skill Level": 4})
        # limit = chess.engine.Limit(time=0.5)

        #while not node.state.is_checkmate or not node.state.is_stalemate():
        while not sim_state.is_game_over():
            self.total_simulations += 1
            # print(sim_state)
            # kies een random actie van de mogelijke states
            #if start_player:
            # ran_move = random.choice(list(sim_state.legal_moves))

            #use_special_sim = sim_state.turn  # Zorg ervoor dat enkel WHITE de privillege krijgt
            use_special_sim = False
            ran_move = None
            super_move = []

            if use_special_sim:
                #i.p.v. random te lopen, kunnen we kijken dat als we een pion kunnen nemen, we deze prefereren boven de andere
                has_taken: bool = False
                super_move = []

                #loop_state = copy.deepcopy(sim_state)
                for move in list(sim_state.legal_moves):
                    if sim_state.is_capture(move):
                        # has_taken = True
                        # print("-- when super move --")
                        # print("From")
                        # print(sim_state)
                        # sim_state.push(move)
                        # print("To")
                        # print(sim_state)
                        # sim_state.pop()
                        # print()

                        super_move.append(move)

                        #print(sim_state.is_capture(move))
                        #print("sim_state")
                        #print(sim_state)
                        #loop_state.push(move)
                        #print("loop_state")

                # Als we andere moves gevonden hebben die een andere pion kunnen nemen, neem dan een random van deze.
                if len(super_move):
                    ran_move = random.choice(super_move)
                else:   # Anders gebruiken we de random move
                    ran_move = random.choice(list(sim_state.legal_moves))
            else:
                ran_move = random.choice(list(sim_state.legal_moves))


            sim_state.push(ran_move)
            # print()
            # print("-- pushed move --")
            # print(sim_state)

            #if len(super_move):
            #    print(sim_state)

            #else:
                #move = black_player.play(sim_state, limit).move
                #sim_state.push(move)

            #sim_state = sim_state
            #print()
            #print("is_game_over: " + str(sim_state.is_game_over()))
            #print("player:" + str(start_player))

        #    start_player = not start_player #flip de player
        #else:
        #    start_player = not start_player  # flip de player naar degenen die ervoor gezorgt heeft dat de uitslag is_game_over voorkwam

        #print()
        #print("player:" + str(start_player))
        #print("is_game_over: " + str(sim_state.is_game_over()))
        #print("is_checkmate: " + str(sim_state.is_checkmate()))
        #print("is_stalemate: " + str(sim_state.is_stalemate()))

        #if start_player and sim_state.is_checkmate():
        #    self.total_wins += 1
        #    return 1.0
        #if not start_player and sim_state.is_checkmate():
        #    self.total_losses += 1
        #    return -1.0

        #if white is checkmate
        # if node.pion and sim_state.is_checkmate():
            # self.total_losses += 1
            # self.total_end_games += 1
            # return 1.0

        # if black is checkmate
        # if not node.pion and sim_state.is_checkmate():
            # self.total_wins += 1
            # self.total_end_games += 1
            # return -1.0
        if sim_state.is_checkmate():
            # Als de not pion schaak staat door de poin -> 1
            # if not sim_state.turn:
            #     return -1
            # return 1
            if not sim_state.turn: # De not pion is schaakmat
                if node.pion:
                    return 1            # Als het de pion is die de sim starte, stuur 1 terug.
                else:
                    return -1           # Als het de NOT pion is die de sim starte, stuur -1 terug.
            else:                   # De pion is schaakmat
                if node.pion:
                    return -1           # Als het de pion is die de sim starte, stuur -1 terug.
                else:
                    return 1            # Als het de NOT pion is die de sim starte, stuur 1 terug.

        # self.total_end_games += 1
        # Als draw, stuur 0.5 voor NOT pion en -0.5 voor PION
        if node.pion:
           return -0.5
        else:
           return 0.5

        return -0.5

    def backpropagation(self, reward: float, node: Node):

        node.moves += 1
        node.reward += reward
        parent = node.parent
        reward = -1*reward # flip value
        # Back propagate de reward en plaats alle visited nodes + 1
        #alter de rewards om en om, om de juiste -1 en 1 terug te brengen.
        while True:
            parent.moves += 1
            parent.reward += reward

            if not parent.parent == None: # als er een parent aanwezig is
                parent = parent.parent  # next parent
                reward = (-1)*reward  # flip value
            else:
                break

    def eval_function(self, node: Node) -> float:
        # We gebruiken hier de UCB functie

        # Exploitation
        total_utility = node.reward
        number_of_playouts = node.moves

        # Exploration
        #c = math.sqrt(2)
        c = 1
        number_of_parent_playouts = self.root_node.moves

        ucb = math.inf  # Als  number_of_playouts = 0 -> x/0 = infinity -> ucb = infinity

        if number_of_playouts > 0:
            exploitation = total_utility / (number_of_playouts +1)
            exploration = c * math.sqrt(math.log(number_of_parent_playouts)/(number_of_playouts+1))

            ucb = exploitation + exploration

        return ucb