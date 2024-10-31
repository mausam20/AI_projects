# -*- coding: utf-8 -*-
import os, time
import numpy as np
import random
import math
import cv2

ROWS = 6
COLUMNS = 7
EMPTY = 0
HUMAN = 1
AI = 2

MAX_SPACE_TO_WIN = 3  # Farthest space where a winning connection may start

# Constants for board display
CELL_SIZE = 100
ROWS, COLS = 6, 7
PADDING = 20
BOARD_COLOR = (255, 255, 255)  # White
HUMAN_COLOR = (255, 0, 0)  # Blue
AI_COLOR = (0, 0, 255)  # Red
HIGHLIGHT_COLOR = (0, 255, 255)  # Yellow for highlighting the AI move


def create_board():
    return np.zeros((ROWS, COLUMNS), np.int8)


# Checks if column is full or not
def is_valid_column(board, column):
    return board[0][column - 1] == EMPTY


# Returns list of columns that are still not full
def valid_locations(board):
    valid_locations = []
    for i in range(1, 8):
        if is_valid_column(board, i):
            valid_locations.append(i)
    return valid_locations


def place_piece(board, player, column):
    index = column - 1
    for row in reversed(range(ROWS)):
        if board[row][index] == EMPTY:
            board[row][index] = player
            return


# Returns a successor board
def clone_and_place_piece(board, player, column):
    new_board = board.copy()
    place_piece(new_board, player, column)
    return new_board


# Checks if the player won the given board
def detect_win(board, player):
    # Horizontal win
    for col in range(COLUMNS - MAX_SPACE_TO_WIN):
        for row in range(ROWS):
            if board[row][col] == player and board[row][col + 1] == player and \
                    board[row][col + 2] == player and board[row][col + 3] == player:
                return True
    # Vertical win
    for col in range(COLUMNS):
        for row in range(ROWS - MAX_SPACE_TO_WIN):
            if board[row][col] == player and board[row + 1][col] == player and \
                    board[row + 2][col] == player and board[row + 3][col] == player:
                return True
    # Diagonal upwards win
    for col in range(COLUMNS - MAX_SPACE_TO_WIN):
        for row in range(ROWS - MAX_SPACE_TO_WIN):
            if board[row][col] == player and board[row + 1][col + 1] == player and \
                    board[row + 2][col + 2] == player and board[row + 3][col + 3] == player:
                return True
    # Diagonal downwards win
    for col in range(COLUMNS - MAX_SPACE_TO_WIN):
        for row in range(MAX_SPACE_TO_WIN, ROWS):
            if board[row][col] == player and board[row - 1][col + 1] == player and \
                    board[row - 2][col + 2] == player and board[row - 3][col + 3] == player:
                return True
    return False


# Returns true if current board is a terminal board which happens when
# either player wins or no more spaces on the board are free
def is_terminal_board(board):
    return detect_win(board, HUMAN) or detect_win(board, AI) or \
        len(valid_locations(board)) == 0


def score(board, player):
    score = 0
    # Give more weight to center columns
    for col in range(2, 5):
        for row in range(ROWS):
            if board[row][col] == player:
                if col == 3:
                    score += 3
                else:
                    score += 2
    # Horizontal pieces
    for col in range(COLUMNS - MAX_SPACE_TO_WIN):
        for row in range(ROWS):
            adjacent_pieces = [board[row][col], board[row][col + 1],
                               board[row][col + 2], board[row][col + 3]]
            score += evaluate_adjacents(adjacent_pieces, player)
    # Vertical pieces
    for col in range(COLUMNS):
        for row in range(ROWS - MAX_SPACE_TO_WIN):
            adjacent_pieces = [board[row][col], board[row + 1][col],
                               board[row + 2][col], board[row + 3][col]]
            score += evaluate_adjacents(adjacent_pieces, player)
    # Diagonal upwards pieces
    for col in range(COLUMNS - MAX_SPACE_TO_WIN):
        for row in range(ROWS - MAX_SPACE_TO_WIN):
            adjacent_pieces = [board[row][col], board[row + 1][col + 1],
                               board[row + 2][col + 2], board[row + 3][col + 3]]
            score += evaluate_adjacents(adjacent_pieces, player)
    # Diagonal downwards pieces
    for col in range(COLUMNS - MAX_SPACE_TO_WIN):
        for row in range(MAX_SPACE_TO_WIN, ROWS):
            adjacent_pieces = [board[row][col], board[row - 1][col + 1],
                               board[row - 2][col + 2], board[row - 3][col + 3]]
            score += evaluate_adjacents(adjacent_pieces, player)
    return score


def evaluate_adjacents(adjacent_pieces, player):
    opponent = AI
    if player == AI:
        opponent = HUMAN
    score = 0
    player_pieces = 0
    empty_spaces = 0
    opponent_pieces = 0
    for p in adjacent_pieces:
        if p == player:
            player_pieces += 1
        elif p == EMPTY:
            empty_spaces += 1
        elif p == opponent:
            opponent_pieces += 1
    if player_pieces == 4:
        score += 99999
    elif player_pieces == 3 and empty_spaces == 1:
        score += 100
    elif player_pieces == 2 and empty_spaces == 2:
        score += 10
    return score


def minimax(board, ply, alpha, beta, maxi_player):
    valid_cols = valid_locations(board)
    is_terminal = is_terminal_board(board)
    if ply == 0 or is_terminal:
        if is_terminal:
            if detect_win(board, HUMAN):
                return (None, -1000000000)
            elif detect_win(board, AI):
                return (None, 1000000000)
            else:  # There is no winner
                return (None, 0)
        else:  # Ply == 0
            return (None, score(board, AI))
    # If max player
    if maxi_player:
        value = -math.inf
        # If every choice has an equal score, choose randomly
        col = random.choice(valid_cols)
        # Expand current node/board
        for c in valid_cols:
            next_board = clone_and_place_piece(board, AI, c)
            new_score = minimax(next_board, ply - 1, alpha, beta, False)[1]
            if new_score > value:
                value = new_score
                col = c
            # Alpha pruning
            if value > alpha:
                alpha = new_score
            # If beta is less than or equal to alpha, there will be no need to
            # check other branches because there will not be a better move
            if beta <= alpha:
                break
        return col, value
    # if min player
    else:
        value = math.inf
        col = random.choice(valid_cols)
        for c in valid_cols:
            next_board = clone_and_place_piece(board, HUMAN, c)
            new_score = minimax(next_board, ply - 1, alpha, beta, True)[1]
            if new_score < value:
                value = new_score
                col = c
            if value < beta:
                beta = value
            if beta <= alpha:
                break
        return col, value


# Function to draw the game board
def draw_game(board, turn, game_over=False, AI_move=0, running_time=0):
    # Set up the OpenCV canvas for the board
    if turn == HUMAN and not game_over:
        message = "Your turn!"
    elif turn == AI and not game_over:
        message = "Computer's turn"
    elif turn == HUMAN and game_over:
        message = "You win!!"
    elif turn == AI and game_over:
        message = "Computer wins"

    width = COLS * CELL_SIZE + 2 * PADDING
    height = ROWS * CELL_SIZE + 3 * PADDING + 50  # Extra space for messages
    image = np.ones((height, width, 3), dtype=np.uint8) * 50  # Dark gray background

    # Draw background rectangle for the board
    board_start_y = 2 * PADDING
    board_end_y = board_start_y + ROWS * CELL_SIZE
    cv2.rectangle(image, (PADDING, board_start_y), (width - PADDING, board_end_y), BOARD_COLOR, -1)

    # Draw each cell with human or AI pieces
    for row in range(ROWS):
        for col in range(COLS):
            center = (PADDING + col * CELL_SIZE + CELL_SIZE // 2,
                      board_start_y + row * CELL_SIZE + CELL_SIZE // 2)
            piece = board[row][col]
            if piece == HUMAN:
                color = HUMAN_COLOR
            elif piece == AI:
                # color = HIGHLIGHT_COLOR if col == AI_move - 1 else AI_COLOR
                color = AI_COLOR
            else:
                color = BOARD_COLOR

            # Draw piece
            cv2.circle(image, center, CELL_SIZE // 2 - 10, color, -1)

    # Add column numbers
    for col in range(COLS):
        col_text = str(col + 1)
        text_size, _ = cv2.getTextSize(col_text, cv2.FONT_HERSHEY_SIMPLEX, 1, 2)
        col_pos = (PADDING + col * CELL_SIZE + CELL_SIZE // 2 - text_size[0] // 2, board_end_y + PADDING)
        cv2.putText(image, col_text, col_pos, cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
    # print(turn)
    # Display turn or game status message

    print(message)

    text_pos = (PADDING, PADDING)
    cv2.putText(image, message, text_pos, cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

    # Running time display if it's the human's turn
    if turn == HUMAN and not game_over:
        time_message = f"Minimax running time: {running_time:.4f} seconds"
        time_text_pos = (PADDING, height - PADDING)
        cv2.putText(image, time_message, time_text_pos, cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200, 200, 200), 1)

    # Display the final image
    cv2.imshow("Connect Four", image)
    cv2.waitKey(1)  # Briefly show the updated image; adjust based on your game loop


# Start of game loop:
board = create_board()
turn = random.choice([HUMAN, AI])
is_game_won = False
AI_move = -1
running_time = 0
draw_game(board, turn)
total_moves = 0
minimax_times = []
while not is_game_won:
    total_moves += 1
    if turn == HUMAN:
        # Take user input
        pressed_key = input()
        try:
            pressed_key = int(pressed_key)
        except ValueError:
            pass
            # If typed 1 to 7
        if pressed_key in range(1, 8) and is_valid_column(board, pressed_key):
            place_piece(board, HUMAN, pressed_key)
            is_game_won = detect_win(board, turn)
            if is_game_won:
                draw_game(board, turn, game_over=True,
                          running_time=running_time)
                break
            else:
                turn = AI
                draw_game(board, turn, running_time=running_time)
                continue
        # If player chooses to quit game
        elif pressed_key == "q":
            print("\033c")  # Clear screen
            print("\nThank you for playing!")
            exit()
        # Invalid input
        else:
            print("\nInvalid input, try again...")
            time.sleep(1)
            draw_game(board, turn, AI_move=AI_move, running_time=running_time)

    elif turn == AI:
        initial_time = time.time()
        # For alpha-beta pruning we initialize minimax with worse value for
        # alpha, -inf, and worse value for beta, inf.
        AI_move, minimax_value = minimax(board, 5, -math.inf, math.inf, True)
        place_piece(board, AI, AI_move)
        is_game_won = detect_win(board, AI)
        running_time = time.time() - initial_time
        minimax_times.append(running_time)
        if is_game_won:
            draw_game(board, turn, game_over=True, AI_move=AI_move,
                      running_time=running_time)
            break
        else:
            turn = HUMAN
            draw_game(board, turn, AI_move=AI_move, running_time=running_time)
            continue
if is_game_won:
    running_time = sum(minimax_times) / len(minimax_times)
    print("                    Thank you for playing!")
    print("          Average minimax running time: %.4f seconds" % running_time)
    print("                   Total number of moves: %s" % total_moves)
