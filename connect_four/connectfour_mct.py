import numpy as np
import cv2
import math
import random
from collections import defaultdict

# Constants
ROW_COUNT = 6
COLUMN_COUNT = 7
PLAYER_1 = 1
PLAYER_2 = 2
EMPTY = 0
SQUARESIZE = 100
RADIUS = SQUARESIZE // 2 - 5
WINDOW_LENGTH = 4

def create_board():
    return np.zeros((ROW_COUNT, COLUMN_COUNT), dtype=int)

def drop_piece(board, row, col, piece):
    board[row][col] = piece

def is_valid_location(board, col):
    return board[ROW_COUNT - 1][col] == EMPTY

def get_next_open_row(board, col):
    for r in range(ROW_COUNT):
        if board[r][col] == EMPTY:
            return r

def winning_move(board, piece):
    # Check horizontal locations for win
    for c in range(COLUMN_COUNT - 3):
        for r in range(ROW_COUNT):
            if all(board[r, c+i] == piece for i in range(WINDOW_LENGTH)):
                return True

    # Check vertical locations for win
    for c in range(COLUMN_COUNT):
        for r in range(ROW_COUNT - 3):
            if all(board[r+i, c] == piece for i in range(WINDOW_LENGTH)):
                return True

    # Check positively sloped diagonals
    for c in range(COLUMN_COUNT - 3):
        for r in range(ROW_COUNT - 3):
            if all(board[r+i, c+i] == piece for i in range(WINDOW_LENGTH)):
                return True

    # Check negatively sloped diagonals
    for c in range(COLUMN_COUNT - 3):
        for r in range(3, ROW_COUNT):
            if all(board[r-i, c+i] == piece for i in range(WINDOW_LENGTH)):
                return True

    return False

def is_terminal_node(board):
    return winning_move(board, PLAYER_1) or winning_move(board, PLAYER_2) or len(get_valid_locations(board)) == 0

def get_valid_locations(board):
    valid_locations = []
    for col in range(COLUMN_COUNT):
        if is_valid_location(board, col):
            valid_locations.append(col)
    return valid_locations

def simulate_random_game(board, player):
    current_player = player
    sim_board = board.copy()

    while not is_terminal_node(sim_board):
        valid_locations = get_valid_locations(sim_board)
        if not valid_locations:
            break

        col = random.choice(valid_locations)
        row = get_next_open_row(sim_board, col)
        drop_piece(sim_board, row, col, current_player)

        if winning_move(sim_board, current_player):
            return current_player

        current_player = PLAYER_1 if current_player == PLAYER_2 else PLAYER_2

    return 0  # Draw

class MCTSNode:
    def __init__(self, board, player):
        self.board = board
        self.player = player
        self.visits = 0
        self.wins = 0
        self.children = {}

    def is_fully_expanded(self):
        return len(self.children) == len(get_valid_locations(self.board))

    def best_child(self, exploration_weight=1.0):
        choices_weights = [
            (child.wins / (child.visits + 1e-6)) +
            exploration_weight * math.sqrt(math.log(self.visits + 1) / (child.visits + 1e-6))
            for child in self.children.values()
        ]
        return list(self.children.values())[np.argmax(choices_weights)]

def mcts_search(board, player, iterations=1000):
    root = MCTSNode(board, player)

    for _ in range(iterations):
        node = root
        sim_board = board.copy()

        # Selection
        while not is_terminal_node(sim_board) and node.is_fully_expanded():
            node = node.best_child()

        # Expansion
        valid_locations = get_valid_locations(sim_board)
        if valid_locations:
            col = random.choice(valid_locations)
            row = get_next_open_row(sim_board, col)
            next_board = sim_board.copy()
            drop_piece(next_board, row, col, player)
            new_node = MCTSNode(next_board, PLAYER_1 if player == PLAYER_2 else PLAYER_2)
            node.children[col] = new_node
            node = new_node

        # Simulation
        winner = simulate_random_game(sim_board, player)

        # Backpropagation
        while node is not None:
            node.visits += 1
            if node.player == winner:
                node.wins += 1
            node = None  # Parent relationship not implemented

    return max(root.children, key=lambda c: root.children[c].wins / (root.children[c].visits + 1e-6))

def draw_board(board):
    global image
    image = np.ones((SQUARESIZE * ROW_COUNT, SQUARESIZE * COLUMN_COUNT, 3), dtype=np.uint8) * 255
    for c in range(COLUMN_COUNT):
        for r in range(ROW_COUNT):
            color = (0, 0, 0)
            if board[r][c] == PLAYER_1:
                color = (255, 0, 0)
            elif board[r][c] == PLAYER_2:
                color = (255, 255, 0)
            cv2.circle(image, (c * SQUARESIZE + SQUARESIZE // 2, r * SQUARESIZE + SQUARESIZE // 2), RADIUS, color, -1)
    cv2.imshow("Connect Four", image)
    cv2.waitKey(500)

# Game variables
board = create_board()
turn = 0

def display_game():
    global image
    image = np.ones((SQUARESIZE*ROW_COUNT, SQUARESIZE*COLUMN_COUNT, 3), dtype=np.uint8)*255
    draw_board(board)
    cv2.imshow("Connect Four", image)
    cv2.waitKey(500)

# Main game loop
while not is_terminal_node(board):
    display_game()

    if turn == 0:
        # print("Player 1 (AI) turn")
        col = mcts_search(board, PLAYER_1)
    else:
        # print("Player 2 (AI) turn")
        col = mcts_search(board, PLAYER_2)

    if is_valid_location(board, col):
        row = get_next_open_row(board, col)
        drop_piece(board, row, col, PLAYER_1 if turn == 0 else PLAYER_2)

        if winning_move(board, PLAYER_1 if turn == 0 else PLAYER_2):
            display_game()
            print(f"Player {1 if turn == 0 else 2} wins!")
            break

        turn = (turn + 1) % 2

cv2.destroyAllWindows()
