#!/usr/bin/python3
from project.chess_engines.uci_engine import UciEngine
import chess
from project.chess_agents.tom_agent import TomAgent
from project.chess_utilities.example_utility import ExampleUtility

if __name__ == "__main__":
    # Create your utility
    utility = ExampleUtility()
    # Create your agent
    agent = TomAgent(utility, 5.0)
    # Create the engine
    engine = UciEngine("Tom engine", "Tom", agent)
    # Run the engine (will loop until the game is done or exited)
    engine.engine_operation()

