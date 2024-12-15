import numpy as np
import cv2
import math

# Constants
ROW_COUNT = 6
COLUMN_COUNT = 7
PLAYER_1 = 1
PLAYER_2 = 2
EMPTY = 0
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

def evaluate_window(window, piece):
    score = 0
    opp_piece = PLAYER_1 if piece == PLAYER_2 else PLAYER_2

    if window.count(piece) == 4:
        score += 100
    elif window.count(piece) == 3 and window.count(EMPTY) == 1:
        score += 5
    elif window.count(piece) == 2 and window.count(EMPTY) == 2:
        score += 2

    if window.count(opp_piece) == 3 and window.count(EMPTY) == 1:
        score -= 4

    return score

def score_position(board, piece):
    score = 0

    # Score center column
    center_array = [int(i) for i in list(board[:, COLUMN_COUNT//2])]
    center_count = center_array.count(piece)
    score += center_count * 3

    # Score Horizontal
    for r in range(ROW_COUNT):
        row_array = [int(i) for i in list(board[r, :])]
        for c in range(COLUMN_COUNT - 3):
            window = row_array[c:c+WINDOW_LENGTH]
            score += evaluate_window(window, piece)

    # Score Vertical
    for c in range(COLUMN_COUNT):
        col_array = [int(i) for i in list(board[:, c])]
        for r in range(ROW_COUNT - 3):
            window = col_array[r:r+WINDOW_LENGTH]
            score += evaluate_window(window, piece)

    # Score positively sloped diagonals
    for r in range(ROW_COUNT - 3):
        for c in range(COLUMN_COUNT - 3):
            window = [board[r+i][c+i] for i in range(WINDOW_LENGTH)]
            score += evaluate_window(window, piece)

    # Score negatively sloped diagonals
    for r in range(ROW_COUNT - 3):
        for c in range(COLUMN_COUNT - 3):
            window = [board[r+3-i][c+i] for i in range(WINDOW_LENGTH)]
            score += evaluate_window(window, piece)

    return score

def is_terminal_node(board):
    return winning_move(board, PLAYER_1) or winning_move(board, PLAYER_2) or len(get_valid_locations(board)) == 0

def minimax(board, depth, alpha, beta, maximizingPlayer):
    valid_locations = get_valid_locations(board)
    is_terminal = is_terminal_node(board)
    if depth == 0 or is_terminal:
        if is_terminal:
            if winning_move(board, PLAYER_2):
                return (None, 100000000000000)
            elif winning_move(board, PLAYER_1):
                return (None, -10000000000000)
            else:  # Game is over, no more valid moves
                return (None, 0)
        else:  # Depth is zero
            return (None, score_position(board, PLAYER_2))
    if maximizingPlayer:
        value = -math.inf
        column = np.random.choice(valid_locations)
        for col in valid_locations:
            row = get_next_open_row(board, col)
            b_copy = board.copy()
            drop_piece(b_copy, row, col, PLAYER_2)
            new_score = minimax(b_copy, depth-1, alpha, beta, False)[1]
            if new_score > value:
                value = new_score
                column = col
            alpha = max(alpha, value)
            if alpha >= beta:
                break
        return column, value
    else:  # Minimizing player
        value = math.inf
        column = np.random.choice(valid_locations)
        for col in valid_locations:
            row = get_next_open_row(board, col)
            b_copy = board.copy()
            drop_piece(b_copy, row, col, PLAYER_1)
            new_score = minimax(b_copy, depth-1, alpha, beta, True)[1]
            if new_score < value:
                value = new_score
                column = col
            beta = min(beta, value)
            if alpha >= beta:
                break
        return column, value

def get_valid_locations(board):
    valid_locations = []
    for col in range(COLUMN_COUNT):
        if is_valid_location(board, col):
            valid_locations.append(col)
    return valid_locations

def draw_board(board):
    for c in range(COLUMN_COUNT):
        for r in range(ROW_COUNT):
            color = (0, 0, 0)
            if board[r][c] == PLAYER_1:
                color = (255, 0, 0)
            elif board[r][c] == PLAYER_2:
                color = (255, 255, 0)
            cv2.circle(image, (c*SQUARESIZE + SQUARESIZE//2, r*SQUARESIZE + SQUARESIZE//2), RADIUS, color, -1)

def display_game():
    global image
    image = np.ones((SQUARESIZE*ROW_COUNT, SQUARESIZE*COLUMN_COUNT, 3), dtype=np.uint8)*255
    draw_board(board)
    cv2.imshow("Connect Four", image)
    cv2.waitKey(500)

# Game variables
board = create_board()
SQUARESIZE = 100
RADIUS = SQUARESIZE // 2 - 5
turn = 0

# Main game loop
while not is_terminal_node(board):
    display_game()

    # AI Move
    if turn == 0:
        col, minimax_score = minimax(board, 4, -math.inf, math.inf, True)
    else:
        col, minimax_score = minimax(board, 4, -math.inf, math.inf, False)

    if is_valid_location(board, col):
        row = get_next_open_row(board, col)
        drop_piece(board, row, col, PLAYER_1 if turn == 0 else PLAYER_2)

        if winning_move(board, PLAYER_1 if turn == 0 else PLAYER_2):
            display_game()
            print(f"Player {1 if turn == 0 else 2} wins!")
            break

        turn = (turn + 1) % 2

cv2.destroyAllWindows()
