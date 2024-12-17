import numpy as np
import copy
import math
import cv2

# Constants
SQUARE_SIZE = 80  # Size of each square in pixels
BOARD_SIZE = 8  # 8x8 board
PLAYER_ONE = 1  # Player 1's pieces
PLAYER_TWO = -1  # Player 2's pieces
KING_ONE = 2  # Player 1's kings
KING_TWO = -2  # Player 2's kings

# Colors for the board and pieces
COLORS = {
    "light": (255, 255, 255),
    "dark": (0, 0, 0),
    "p1_piece": (0, 0, 255),  # Player 1
    "p2_piece": (255, 0, 0),  # Player 2
    "p1_king": (0, 0, 200),  # Player 1 King
    "p2_king": (200, 0, 0),  # Player 2 King
}

# Checkers Game Class
class CheckersGame:
    def __init__(self):
        self.board = np.zeros((8, 8), dtype=int)
        self.current_player = PLAYER_ONE
        self.initialize_board()

    def initialize_board(self):
        """Place pieces on the board for both players."""
        for i in range(3):  # Top rows for Player 1
            for j in range(8):
                if (i + j) % 2 == 1:
                    self.board[i][j] = PLAYER_ONE
        for i in range(5, 8):  # Bottom rows for Player 2
            for j in range(8):
                if (i + j) % 2 == 1:
                    self.board[i][j] = PLAYER_TWO

    def get_legal_moves(self):
        capturing_moves = []
        regular_moves = []

        for i in range(8):
            for j in range(8):
                if self.board[i][j] == self.current_player:
                    capturing_moves += self.get_capturing_moves(i, j, king=False)
                    regular_moves += self.get_regular_moves(i, j, king=False)
                elif self.board[i][j] == 2 * self.current_player:
                    capturing_moves += self.get_capturing_moves(i, j, king=True)
                    regular_moves += self.get_regular_moves(i, j, king=True)

        return capturing_moves if capturing_moves else regular_moves

    def get_capturing_moves(self, i, j, king=False):
        moves = []
        directions = [(1, 1), (1, -1), (-1, 1), (-1, -1)] if king else [(1, 1), (1, -1)] if self.current_player == PLAYER_ONE else [(-1, 1), (-1, -1)]

        for dx, dy in directions:
            x, y = i + dx, j + dy
            if 0 <= x < 8 and 0 <= y < 8 and self.board[x][y] * self.current_player < 0:
                nx, ny = x + dx, y + dy
                if 0 <= nx < 8 and 0 <= ny < 8 and self.board[nx][ny] == 0:
                    moves.append(((i, j), (nx, ny)))
        return moves

    def get_regular_moves(self, i, j, king=False):
        moves = []
        directions = [(1, 1), (1, -1), (-1, 1), (-1, -1)] if king else [(1, 1), (1, -1)] if self.current_player == PLAYER_ONE else [(-1, 1), (-1, -1)]

        for dx, dy in directions:
            x, y = i + dx, j + dy
            if 0 <= x < 8 and 0 <= y < 8 and self.board[x][y] == 0:
                moves.append(((i, j), (x, y)))
        return moves

    def make_move(self, move):
        start, end = move
        i, j = start
        x, y = end
        self.board[x][y] = self.board[i][j]
        self.board[i][j] = 0

        if abs(x - i) == 2:
            self.board[(i + x) // 2][(j + y) // 2] = 0

        if (self.current_player == PLAYER_ONE and x == 7) or (self.current_player == PLAYER_TWO and x == 0):
            self.board[x][y] = 2 * self.current_player

        self.switch_player()

    def switch_player(self):
        self.current_player = -self.current_player

    def is_terminal(self):
        return len(self.get_legal_moves()) == 0

    def evaluate(self):
        score = 0
        for row in self.board:
            for piece in row:
                if piece == PLAYER_ONE:
                    score += 1
                elif piece == PLAYER_TWO:
                    score -= 1
                elif piece == KING_ONE:
                    score += 2
                elif piece == KING_TWO:
                    score -= 2
        return score

    def get_next_state(self, move):
        new_game = copy.deepcopy(self)
        new_game.make_move(move)
        return new_game

class MinimaxAgent:
    def __init__(self, depth=4):
        self.depth = depth

    def minimax(self, game, depth, alpha, beta, maximizing_player):
        if depth == 0 or game.is_terminal():
            return game.evaluate(), None

        legal_moves = game.get_legal_moves()
        if maximizing_player:
            max_eval = -math.inf
            best_move = None
            for move in legal_moves:
                new_game = game.get_next_state(move)
                eval_score, _ = self.minimax(new_game, depth - 1, alpha, beta, False)
                if eval_score > max_eval:
                    max_eval = eval_score
                    best_move = move
                alpha = max(alpha, eval_score)
                if beta <= alpha:
                    break
            return max_eval, best_move
        else:
            min_eval = math.inf
            best_move = None
            for move in legal_moves:
                new_game = game.get_next_state(move)
                eval_score, _ = self.minimax(new_game, depth - 1, alpha, beta, True)
                if eval_score < min_eval:
                    min_eval = eval_score
                    best_move = move
                beta = min(beta, eval_score)
                if beta <= alpha:
                    break
            return min_eval, best_move

    def select_move(self, game):
        _, best_move = self.minimax(game, self.depth, -math.inf, math.inf, True)
        return best_move

def draw_board(board):
    img = np.zeros((SQUARE_SIZE * BOARD_SIZE, SQUARE_SIZE * BOARD_SIZE, 3), dtype=np.uint8)

    for row in range(BOARD_SIZE):
        for col in range(BOARD_SIZE):
            color = COLORS["light"] if (row + col) % 2 == 0 else COLORS["dark"]
            cv2.rectangle(img, (col * SQUARE_SIZE, row * SQUARE_SIZE),
                          ((col + 1) * SQUARE_SIZE, (row + 1) * SQUARE_SIZE), color, -1)
            piece = board[row][col]
            center = (col * SQUARE_SIZE + SQUARE_SIZE // 2, row * SQUARE_SIZE + SQUARE_SIZE // 2)
            radius = SQUARE_SIZE // 3
            if piece == PLAYER_ONE:
                cv2.circle(img, center, radius, COLORS["p1_piece"], -1)
            elif piece == PLAYER_TWO:
                cv2.circle(img, center, radius, COLORS["p2_piece"], -1)
            elif piece == KING_ONE:
                cv2.circle(img, center, radius, COLORS["p1_king"], -1)
            elif piece == KING_TWO:
                cv2.circle(img, center, radius, COLORS["p2_king"], -1)
    return img

def main():
    game = CheckersGame()
    agent = MinimaxAgent(depth=4)

    while not game.is_terminal():
        img = draw_board(game.board)
        cv2.imshow("Checkers Game", img)
        cv2.waitKey(500)

        move = agent.select_move(game)
        if move:
            game.make_move(move)
        else:
            print("No moves left!")
            break

    print("Game Over!")

    #print which player won the game
    final_score = game.evaluate()
    if final_score > 0:
        print("Player 1 (Red) wins!")
    elif final_score < 0:
        print("Player 2 (Blue) wins!")
    else:
        print("It's a draw!")

    cv2.waitKey(0)
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
