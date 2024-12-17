import numpy as np
import cv2
import math
import random

# Constants
ROWS = 6  # Total rows on the board
COLS = 7  # Total columns
PLAYER1 = 1  # First player (AI)
PLAYER2 = 2  # Second player (AI)
EMPTY = 0  # Empty cell
SQUARE = 100  # Size of each square in the GUI
RADIUS = SQUARE // 2 - 5  # Circle radius
WIN_LENGTH = 4  # Length to win the game (4 in a row)

# Create an empty game board
def make_board():
    return np.zeros((ROWS, COLS), dtype=int)

# Drop the piece in the selected column
def place_piece(board, row, col, player):
    # Put the player's piece at the right spot
    board[row][col] = player

# Check if the column has space to place a piece
def valid_column(board, col):
    # Topmost row should be empty
    return board[ROWS - 1][col] == EMPTY

# Find the lowest empty row in a column
def find_empty_row(board, col):
    for r in range(ROWS):
        if board[r][col] == EMPTY:
            return r  # Return the first empty spot

# Check if a player has won
def has_won(board, player):
    # Check horizontal win
    for c in range(COLS - 3):
        for r in range(ROWS):
            if all(board[r, c+i] == player for i in range(WIN_LENGTH)):
                return True

    # Check vertical win
    for c in range(COLS):
        for r in range(ROWS - 3):
            if all(board[r+i, c] == player for i in range(WIN_LENGTH)):
                return True

    # Check diagonals (positive slope)
    for c in range(COLS - 3):
        for r in range(ROWS - 3):
            if all(board[r+i, c+i] == player for i in range(WIN_LENGTH)):
                return True

    # Check diagonals (negative slope)
    for c in range(COLS - 3):
        for r in range(3, ROWS):
            if all(board[r-i, c+i] == player for i in range(WIN_LENGTH)):
                return True

    return False

# Check if the game is over (win or draw)
def is_game_over(board):
    return has_won(board, PLAYER1) or has_won(board, PLAYER2) or len(find_valid_cols(board)) == 0

# Find all valid columns where a move can be made
def find_valid_cols(board):
    valid_cols = []
    for col in range(COLS):
        if valid_column(board, col):
            valid_cols.append(col)
    return valid_cols

# Simulate a random game to see who wins
def random_game_sim(board, player):
    temp_board = board.copy()
    current_player = player

    while not is_game_over(temp_board):
        valid_cols = find_valid_cols(temp_board)
        if not valid_cols:
            break  # Stop if no moves left
        # Pick a random column
        col = random.choice(valid_cols)
        row = find_empty_row(temp_board, col)
        place_piece(temp_board, row, col, current_player)

        if has_won(temp_board, current_player):
            return current_player  # Return the winner

        # Switch player turn
        current_player = PLAYER1 if current_player == PLAYER2 else PLAYER2

    return 0  # Draw

# MCTS Node Class
class MCTSNode:
    def __init__(self, board, player):
        self.board = board
        self.player = player
        self.visits = 0
        self.wins = 0
        # Stores child nodes
        self.children = {}

    def is_fully_expanded(self):
        return len(self.children) == len(find_valid_cols(self.board))

    def best_child(self, explore=1.0):
        scores = [
            (child.wins / (child.visits + 1e-6)) + explore * math.sqrt(math.log(self.visits + 1) / (child.visits + 1e-6))
            for child in self.children.values()
        ]
        return list(self.children.values())[np.argmax(scores)]

# Monte Carlo Tree Search (MCTS) to decide the best move
def mcts_search(board, player, iterations=1000):
    root = MCTSNode(board, player)

    for _ in range(iterations):
        node = root
        sim_board = board.copy()

        # Selection phase: Move to best child until unexpanded node
        while not is_game_over(sim_board) and node.is_fully_expanded():
            node = node.best_child()

        # Expansion phase: Add a child node for a valid move
        valid_cols = find_valid_cols(sim_board)
        if valid_cols:
            col = random.choice(valid_cols)
            row = find_empty_row(sim_board, col)
            next_board = sim_board.copy()
            place_piece(next_board, row, col, player)
            node.children[col] = MCTSNode(next_board, PLAYER1 if player == PLAYER2 else PLAYER2)

        # Simulation phase: Random game to determine winner
        winner = random_game_sim(sim_board, player)

        # Backpropagation phase: Update visit and win stats
        while node:
            node.visits += 1
            if node.player == winner:
                node.wins += 1
            # Parent relationship not implemented
            node = None

    return max(root.children, key=lambda c: root.children[c].wins / (root.children[c].visits + 1e-6))

# Draw the Connect Four game board
def draw_board(board):
    global image
    image = np.ones((SQUARE * ROWS, SQUARE * COLS, 3), dtype=np.uint8) * 255
    for c in range(COLS):
        for r in range(ROWS):
            # Black for empty
            color = (0, 0, 0)
            if board[r][c] == PLAYER1:
                color = (255, 0, 0)
            elif board[r][c] == PLAYER2:
                color = (255, 255, 0)
            cv2.circle(image, (c * SQUARE + SQUARE // 2, r * SQUARE + SQUARE // 2), RADIUS, color, -1)
    cv2.imshow("Connect Four", image)
    cv2.waitKey(500)


# Game variables
game_board = make_board()
# 0 for Player 1, 1 for Player 2
turn = 0

# Show the board
def show_game():
    draw_board(game_board)

# Main game loop
while not is_game_over(game_board):
    show_game()

    # AI move using MCTS
    if turn == 0:
        col = mcts_search(game_board, PLAYER1)
    else:
        col = mcts_search(game_board, PLAYER2)

    if valid_column(game_board, col):
        row = find_empty_row(game_board, col)
        place_piece(game_board, row, col, PLAYER1 if turn == 0 else PLAYER2)

        # Check for a win
        if has_won(game_board, PLAYER1 if turn == 0 else PLAYER2):
            show_game()
            print(f"Player {1 if turn == 0 else 2} wins!")
            break
        # Switch turns
        turn = (turn + 1) % 2

cv2.destroyAllWindows()
