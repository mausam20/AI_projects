import argparse
import subprocess

# Map of games to their respective gameplay scripts
GAME_SCRIPTS = {
    "checkers": {"minimax": "checkers/checkers_minmax.py", "mcts": "checkers/checkers_mcts.py"},
    "connectfour": {"minimax": "connect_four/connectfour_min_max.py", "mcts": "connectfour/connectfour_mct.py"},
    "go": {"minimax": "go/go_minmax.py", "mcts": "go/go_mcts.py"}
}

# Map of algorithms to their respective logic scripts
ALGORITHM_MODULES = {
    "minimax": "minimax_logic",
    "mcts": "mcts_logic"
}


def main():
    # Set up argument parser
    parser = argparse.ArgumentParser(description="Run a game with a specific AI algorithm.")
    parser.add_argument(
        "--game",
        type=str,
        required=True,
        choices=GAME_SCRIPTS.keys(),
        help="The game to play (e.g., checkers, connectfour, go)."
    )
    parser.add_argument(
        "--algorithm",
        type=str,
        required=True,
        choices=ALGORITHM_MODULES.keys(),
        help="The algorithm to use (e.g., minimax, mcts)."
    )

    # Parse the arguments
    args = parser.parse_args()
    game = args.game
    algorithm = args.algorithm

    # Check for the corresponding script
    if game in GAME_SCRIPTS:
        print(f"Running {game.capitalize()} with {algorithm.upper()}...")
        # Run the game script
        subprocess.run(["python", GAME_SCRIPTS[game][algorithm]])
    else:
        print(f"Error: Game {game} is not supported!")


if __name__ == "__main__":
    main()
