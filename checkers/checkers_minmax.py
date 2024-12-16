import numpy as np
import cv2
import math

# Constants
BOARD_SIZE = 8
PLAYER_1 = 1
PLAYER_2 = 2
EMPTY = 0
KING_PLAYER_1 = 3
KING_PLAYER_2 = 4
SQUARE_SIZE = 100
COLORS = {
    "empty": (255, 255, 255),
    "board_dark": (0, 0, 0),
    "player_1": (255, 0, 0),
    "player_2": (0, 0, 255),
    "king_player_1": (200, 0, 0),
    "king_player_2": (0, 0, 200),
}

# Directions for normal pieces and kings
DIRECTIONS = {
    PLAYER_1: [(-1, -1), (-1, 1)],
    PLAYER_2: [(1, -1), (1, 1)],
    "king": [(-1, -1), (-1, 1), (1, -1), (1, 1)]
}

# Initialize the board
def create_board():
    board = np.zeros((BOARD_SIZE, BOARD_SIZE), dtype=int)
    for row in range(BOARD_SIZE):
        for col in range(BOARD_SIZE):
            if (row + col) % 2 == 1:
                if row < 3:
                    board[row, col] = PLAYER_2
                elif row > 4:
                    board[row, col] = PLAYER_1
    return board

# Draw the board using OpenCV
def draw_board(board):
    image = np.zeros((BOARD_SIZE * SQUARE_SIZE, BOARD_SIZE * SQUARE_SIZE, 3), dtype=np.uint8)

    for row in range(BOARD_SIZE):
        for col in range(BOARD_SIZE):
            top_left = (col * SQUARE_SIZE, row * SQUARE_SIZE)
            bottom_right = ((col + 1) * SQUARE_SIZE, (row + 1) * SQUARE_SIZE)

            # Draw the board square
            color = COLORS["empty"] if (row + col) % 2 == 0 else COLORS["board_dark"]
            cv2.rectangle(image, top_left, bottom_right, color, -1)

            # Draw the pieces
            piece = board[row, col]
            if piece in [PLAYER_1, PLAYER_2, KING_PLAYER_1, KING_PLAYER_2]:
                center = (col * SQUARE_SIZE + SQUARE_SIZE // 2, row * SQUARE_SIZE + SQUARE_SIZE // 2)
                radius = SQUARE_SIZE // 2 - 10
                if piece == PLAYER_1:
                    cv2.circle(image, center, radius, COLORS["player_1"], -1)
                elif piece == PLAYER_2:
                    cv2.circle(image, center, radius, COLORS["player_2"], -1)
                elif piece == KING_PLAYER_1:
                    cv2.circle(image, center, radius, COLORS["king_player_1"], -1)
                elif piece == KING_PLAYER_2:
                    cv2.circle(image, center, radius, COLORS["king_player_2"], -1)
    return image

# Check if a move is valid
def is_valid_move(board, player, start_pos, end_pos):
    sx, sy = start_pos
    ex, ey = end_pos

    if not (0 <= ex < BOARD_SIZE and 0 <= ey < BOARD_SIZE):
        return False  # Move out of bounds

    if board[ex, ey] != EMPTY:
        return False  # Destination not empty

    piece = board[sx, sy]
    directions = DIRECTIONS["king"] if piece in [KING_PLAYER_1, KING_PLAYER_2] else DIRECTIONS[player]

    for dx, dy in directions:
        if (sx + dx, sy + dy) == (ex, ey):
            return True

    return False

# Apply a move on the board
def apply_move(board, start_pos, end_pos):
    sx, sy = start_pos
    ex, ey = end_pos

    board[ex, ey] = board[sx, sy]
    board[sx, sy] = EMPTY

    # Check for king promotion
    if ex == 0 and board[ex, ey] == PLAYER_1:
        board[ex, ey] = KING_PLAYER_1
    elif ex == BOARD_SIZE - 1 and board[ex, ey] == PLAYER_2:
        board[ex, ey] = KING_PLAYER_2

# Minimax algorithm with alpha-beta pruning
def minimax(board, depth, alpha, beta, maximizing_player):
    valid_moves = get_all_valid_moves(board, PLAYER_1 if maximizing_player else PLAYER_2)

    if depth == 0 or not valid_moves:
        return evaluate_board(board), None

    best_move = None

    if maximizing_player:
        max_eval = -math.inf
        for move in valid_moves:
            new_board = board.copy()
            apply_move(new_board, move[0], move[1])
            eval_score, _ = minimax(new_board, depth - 1, alpha, beta, False)
            if eval_score > max_eval:
                max_eval = eval_score
                best_move = move
            alpha = max(alpha, eval_score)
            if beta <= alpha:
                break
        return max_eval, best_move

    else:
        min_eval = math.inf
        for move in valid_moves:
            new_board = board.copy()
            apply_move(new_board, move[0], move[1])
            eval_score, _ = minimax(new_board, depth - 1, alpha, beta, True)
            if eval_score < min_eval:
                min_eval = eval_score
                best_move = move
            beta = min(beta, eval_score)
            if beta <= alpha:
                break
        return min_eval, best_move

# Evaluate the board
def evaluate_board(board):
    score = 0
    for row in range(BOARD_SIZE):
        for col in range(BOARD_SIZE):
            piece = board[row, col]
            if piece == PLAYER_1:
                score += 1
            elif piece == PLAYER_2:
                score -= 1
            elif piece == KING_PLAYER_1:
                score += 2
            elif piece == KING_PLAYER_2:
                score -= 2
    return score

# Get all valid moves for a player
def get_all_valid_moves(board, player):
    moves = []
    for row in range(BOARD_SIZE):
        for col in range(BOARD_SIZE):
            if board[row, col] in [player, player + 2]:  # Normal or King
                for dx, dy in DIRECTIONS["king"]:
                    new_pos = (row + dx, col + dy)
                    if is_valid_move(board, player, (row, col), new_pos):
                        moves.append(((row, col), new_pos))
    return moves

# Determine the winner
def get_winner(board):
    player_1_pieces = np.sum((board == PLAYER_1) | (board == KING_PLAYER_1))
    player_2_pieces = np.sum((board == PLAYER_2) | (board == KING_PLAYER_2))

    if player_1_pieces == 0:
        return "Player 2 wins!"
    elif player_2_pieces == 0:
        return "Player 1 wins!"
    return None

# Main game loop
def main():
    board = create_board()
    turn = PLAYER_1

    while True:
        # Draw the board
        image = draw_board(board)
        cv2.imshow("Checkers", image)
        cv2.waitKey(500)

        # Minimax to decide the move
        _, best_move = minimax(board, 4, -math.inf, math.inf, turn == PLAYER_1)

        if best_move:
            apply_move(board, best_move[0], best_move[1])
        else:
            winner = get_winner(board)
            print(winner if winner else f"Player {turn} has no valid moves! Game over.")
            break

        # Switch turns
        turn = PLAYER_1 if turn == PLAYER_2 else PLAYER_2

    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
