# Game AI with Minimax and MCTS

This project is a collection of classic games implemented with Artificial Intelligence (AI) algorithms such as **Minimax** and **Monte Carlo Tree Search (MCTS)**. The games included are:
- Checkers
- Connect Four
- Go

Each game can be played using either the Minimax algorithm or MCTS for decision-making.

---

## Features
- **Checkers**:
  - AI agents playing with Minimax or MCTS.
  - Complete gameplay with rules such as mandatory jumps and king promotion.
- **Connect Four**:
  - AI plays strategically using Minimax or MCTS.
- **Go**:
  - AI competes on a simplified Go board using either Minimax or MCTS.

---

## Prerequisites
- Python 3.7 or later
- Required libraries:
  - `numpy`
  - `opencv-python`
  - `argparse`

You can install the required libraries using:
```bash
pip install numpy opencv-python
```
---

### Usage
To play a game, use the main.py script and specify the game and the algorithm you want to use.

- Command:
    ```bash
    python main.py --game <game_name> --algorithm <algorithm>
  ```
  - Parameters:
    - game: The name of the game to play. Options:
      - checkers
      - connectfour
      - go
    - algorithm: The AI algorithm to use. Options:
      - minimax
      - mcts
  - Example:
     - Play Checkers with the Monte carlo search tree algorithm:
    ```bash
    python main.py --game checkers --algorithm mcts
    ```
    - Play Connect Four with Minimax:
    ```bash
    python main.py --game connectfour --algorithm minimax
    ```