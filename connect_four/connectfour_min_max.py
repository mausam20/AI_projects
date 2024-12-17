import numpy as np
import cv2
import math

# Constants for the game
ROW_COUNT = 6  # Number of rows in the board
COLUMN_COUNT = 7  # Number of columns
PLAYER_1 = 1  # Player 1 (AI)
PLAYER_2 = 2  # Player 2 (AI)
EMPTY = 0  # Empty spot in the grid
WINDOW_LENGTH = 4  # For winning (4 connected pieces required)


# Function to create an empty board
# Makes a grid with 6 rows and 7 columns, all set to zero
def make_board():
    return np.zeros((ROW_COUNT, COLUMN_COUNT), dtype=int)


# Function to drop a piece in the board at a specific location
def put_piece(board, row, column, piece):
    board[row][column] = piece  # Puts the piece in the grid


# Function to check if a column is not full
def is_column_valid(board, col):
    return board[ROW_COUNT - 1][col] == EMPTY  # Checks top row


# Function to find the first empty row in a column
def find_next_open_spot(board, col):
    for r in range(ROW_COUNT):
        if board[r][col] == EMPTY:
            return r


# Function to check if a player has won
def check_winner(board, piece):
    # Check horizontal win
    for c in range(COLUMN_COUNT - 3):
        for r in range(ROW_COUNT):
            if all(board[r, c + i] == piece for i in range(WINDOW_LENGTH)):
                return True

    # Check vertical win
    for c in range(COLUMN_COUNT):
        for r in range(ROW_COUNT - 3):
            if all(board[r + i, c] == piece for i in range(WINDOW_LENGTH)):
                return True

    # Check diagonal win (positive slope)
    for c in range(COLUMN_COUNT - 3):
        for r in range(ROW_COUNT - 3):
            if all(board[r + i][c + i] == piece for i in range(WINDOW_LENGTH)):
                return True

    # Check diagonal win (negative slope)
    for c in range(COLUMN_COUNT - 3):
        for r in range(3, ROW_COUNT):
            if all(board[r - i][c + i] == piece for i in range(WINDOW_LENGTH)):
                return True

    return False


# Function to calculate score of a window for AI evaluation
def eval_window(window, piece):
    score = 0
    opp_piece = PLAYER_1 if piece == PLAYER_2 else PLAYER_2  # Opponent's piece

    # Conditions to calculate the score
    if window.count(piece) == 4:  # 4 in a row (win)
        score += 100
    elif window.count(piece) == 3 and window.count(EMPTY) == 1:  # 3 pieces + 1 empty
        score += 5
    elif window.count(piece) == 2 and window.count(EMPTY) == 2:  # 2 pieces + 2 empty
        score += 2
    elif window.count(opp_piece) == 3 and window.count(EMPTY) == 1:  # Opponent has 3 in a row
        score -= 4

    return score


# Function to calculate the score of the current board for AI decision
def calc_score(board, piece):
    score = 0

    # Score center column
    center_array = [int(i) for i in list(board[:, COLUMN_COUNT // 2])]
    center_count = center_array.count(piece)
    score += center_count * 3

    # Score horizontally
    for r in range(ROW_COUNT):
        row_array = [int(i) for i in list(board[r, :])]
        for c in range(COLUMN_COUNT - 3):
            window = row_array[c:c + WINDOW_LENGTH]
            score += eval_window(window, piece)

    # Score vertically
    for c in range(COLUMN_COUNT):
        col_array = [int(i) for i in list(board[:, c])]
        for r in range(ROW_COUNT - 3):
            window = col_array[r:r + WINDOW_LENGTH]
            score += eval_window(window, piece)

    # Score diagonally (positive slope)
    for r in range(ROW_COUNT - 3):
        for c in range(COLUMN_COUNT - 3):
            window = [board[r + i][c + i] for i in range(WINDOW_LENGTH)]
            score += eval_window(window, piece)

    # Score diagonally (negative slope)
    for r in range(ROW_COUNT - 3):
        for c in range(COLUMN_COUNT - 3):
            window = [board[r + 3 - i][c + i] for i in range(WINDOW_LENGTH)]
            score += eval_window(window, piece)

    return score


# Function to check if game is over (no moves left or someone won)
def game_over(board):
    return check_winner(board, PLAYER_1) or check_winner(board, PLAYER_2) or len(find_valid_columns(board)) == 0


# Minimax algorithm with pruning to decide best move
def minimax(board, depth, alpha, beta, is_maximizing):
    valid_cols = find_valid_columns(board)  # Get all valid columns
    terminal = game_over(board)  # Check if game is over

    # If game over or depth reached, return score
    if depth == 0 or terminal:
        if terminal:
            if check_winner(board, PLAYER_2):
                return (None, 1000000000)
            elif check_winner(board, PLAYER_1):
                return (None, -1000000000)
            else:  # Draw
                return (None, 0)
        else:
            return (None, calc_score(board, PLAYER_2))

    if is_maximizing:  # AI's turn to maximize
        value = -math.inf
        best_col = np.random.choice(valid_cols)
        for col in valid_cols:
            row = find_next_open_spot(board, col)
            b_copy = board.copy()
            put_piece(b_copy, row, col, PLAYER_2)
            new_score = minimax(b_copy, depth - 1, alpha, beta, False)[1]
            if new_score > value:
                value = new_score
                best_col = col
            alpha = max(alpha, value)
            if alpha >= beta:  # Prune
                break
        return best_col, value
    else:  # Opponent's turn to minimize
        value = math.inf
        best_col = np.random.choice(valid_cols)
        for col in valid_cols:
            row = find_next_open_spot(board, col)
            b_copy = board.copy()
            put_piece(b_copy, row, col, PLAYER_1)
            new_score = minimax(b_copy, depth - 1, alpha, beta, True)[1]
            if new_score < value:
                value = new_score
                best_col = col
            beta = min(beta, value)
            if alpha >= beta:  # Prune
                break
        return best_col, value


# Function to find all valid columns for moves
def find_valid_columns(board):
    valid_cols = []
    for col in range(COLUMN_COUNT):
        if is_column_valid(board, col):
            valid_cols.append(col)
    return valid_cols


# Draw the board visually
def draw_board_image(board):
    for c in range(COLUMN_COUNT):
        for r in range(ROW_COUNT):
            color = (0, 0, 0)  # Black for empty spaces
            if board[r][c] == PLAYER_1:
                color = (255, 0, 0)
            elif board[r][c] == PLAYER_2:
                color = (255, 255, 0)
            cv2.circle(image, (c * SQUARESIZE + SQUARESIZE // 2, r * SQUARESIZE + SQUARESIZE // 2), RADIUS, color, -1)


# Function to show the board
def show_game():
    global image
    image = np.ones((SQUARESIZE * ROW_COUNT, SQUARESIZE * COLUMN_COUNT, 3), dtype=np.uint8) * 255
    draw_board_image(board)
    cv2.imshow("Connect Four", image)
    cv2.waitKey(500)


# Game variables
board = make_board()
SQUARESIZE = 100
RADIUS = SQUARESIZE // 2 - 5
turn = 0  # Start with Player 1

# Main Game Loop
while not game_over(board):
    show_game()

    # AI move (Player 2) or opponent move
    if turn == 0:
        col, minimax_score = minimax(board, 4, -math.inf, math.inf, True)
    else:
        col, minimax_score = minimax(board, 4, -math.inf, math.inf, False)

    if is_column_valid(board, col):
        row = find_next_open_spot(board, col)
        put_piece(board, row, col, PLAYER_1 if turn == 0 else PLAYER_2)

        if check_winner(board, PLAYER_1 if turn == 0 else PLAYER_2):
            show_game()
            print(f"Player {1 if turn == 0 else 2} wins!")
            break

        turn = (turn + 1) % 2  # Switch turn
cv2.waitKey(0)
cv2.destroyAllWindows()
