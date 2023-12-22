#!/usr/bin/python3
import chess

from project.chess_engines.Gegeven.uci_engine import UciEngine
from project.chess_agents.Berkay.MCTSagent import MCTSAgent
from project.chess_utilities.gegeven.example_utility import ExampleUtility

if __name__ == "__main__":
    # Create your utility
    utility = ExampleUtility()
    # Create your agent
    agent = MCTSAgent(utility, 5.0)
    agent.color = chess.BLACK
    # Create the engine
    engine = UciEngine("My Engine", "Berkay", agent)
    # Run the engine (will loop until the game is done or exited)
    engine.engine_operation()
