import numpy as np
import cv2
import math


class SimpleGoGame:
    def __init__(self, board_size=5):
        # Initialize board and some settings
        self.board_size = board_size
        self.grid = np.zeros((board_size, board_size), dtype=int)
        self.player_turn = 1
        self.tile_size = 100
        self.background_color = (255, 220, 180)
        self.black_color = (0, 0, 0)
        self.white_color = (255, 255, 255)
        self.pass_moves = 0
        self.game_finished = False

    def check_valid_move(self, row, col):
        """
        Check if the move is valid by placing a stone temporarily.
        """
        # Out of bounds or not empty
        if not (0 <= row < self.board_size and 0 <= col < self.board_size) or self.grid[row, col] != 0:
            return False

        # Place the stone temporarily and check if it has liberties
        self.grid[row, col] = self.player_turn
        is_valid = self.check_liberty(row, col)
        # reverse the move
        self.grid[row, col] = 0
        return is_valid

    def check_liberty(self, row, col, visited=None):
        """
        Check if a stone (or group) has any liberties (empty spaces around it).
        """
        if visited is None:
            visited = set()
        if (row, col) in visited:
            return False
        visited.add((row, col))

        # Found an empty space
        if self.grid[row, col] == 0:
            return True

        for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nr, nc = row + dr, col + dc
            if 0 <= nr < self.board_size and 0 <= nc < self.board_size:
                if self.grid[nr, nc] == 0 or (
                        self.grid[nr, nc] == self.grid[row, col] and self.check_liberty(nr, nc, visited)):
                    return True
        return False

    def clear_captured_stones(self):
        """
        Remove stones that are captured (no liberties).
        """
        # List of stones to remove
        captured = []
        for r in range(self.board_size):
            for c in range(self.board_size):
                if self.grid[r, c] != 0 and not self.check_liberty(r, c):
                    # Mark stone to remove
                    captured.append((r, c))
        for r, c in captured:
            # Remove the captured stones
            self.grid[r, c] = 0

    def apply_move(self, row, col):
        """
        Place a stone on the board and check for captures.
        """
        self.grid[row, col] = self.player_turn
        self.clear_captured_stones()
        # Switch players
        self.player_turn *= -1

    def find_valid_moves(self):
        """
        Get a list of all possible moves for the player.
        """
        possible_moves = []
        for r in range(self.board_size):
            for c in range(self.board_size):
                if self.check_valid_move(r, c):
                    possible_moves.append((r, c))
        return possible_moves

    def calculate_score(self):
        """
        Simple evaluation: count black stones and white stones.
        """
        return np.sum(self.grid)

    def minimax(self, depth, alpha, beta, is_max):
        """
        Minimax algorithm with pruning to make a decision.
        """
        if depth == 0 or self.check_game_end():
            # Score the board
            return self.calculate_score(), None

        valid_moves = self.find_valid_moves()
        # If no moves, score the board
        if not valid_moves:
            return self.calculate_score(), None

        # Maximizing player (black)
        if is_max:
            max_value = -math.inf
            best_step = None
            for move in valid_moves:
                temp_game = self.deep_copy()
                temp_game.apply_move(*move)
                score, _ = temp_game.minimax(depth - 1, alpha, beta, False)
                if score > max_value:
                    max_value = score
                    best_step = move
                alpha = max(alpha, score)
                if beta <= alpha:
                    break  # Prune
            return max_value, best_step
        # Minimizing player (white)
        else:
            min_value = math.inf
            best_step = None
            for move in valid_moves:
                temp_game = self.deep_copy()
                temp_game.apply_move(*move)
                score, _ = temp_game.minimax(depth - 1, alpha, beta, True)
                if score < min_value:
                    min_value = score
                    best_step = move
                beta = min(beta, score)
                # Prune
                if beta <= alpha:
                    break
            return min_value, best_step

    def check_game_end(self):
        """
        Check if the game has ended after two consecutive passes.
        """
        return self.pass_moves >= 2

    def deep_copy(self):
        """
        Create a copy of the game state for simulations.
        """
        copied_game = SimpleGoGame(self.board_size)
        copied_game.grid = np.copy(self.grid)
        copied_game.player_turn = self.player_turn
        return copied_game

    def display_board(self):
        """
        Draw the game board using OpenCV.
        """
        board_img_size = self.board_size * self.tile_size
        board_img = np.ones((board_img_size, board_img_size, 3), dtype=np.uint8) * 255
        board_img[:, :] = self.background_color

        for i in range(self.board_size + 1):
            pos = i * self.tile_size
            cv2.line(board_img, (pos, 0), (pos, board_img_size), (0, 0, 0), 2)
            cv2.line(board_img, (0, pos), (board_img_size, pos), (0, 0, 0), 2)

        for r in range(self.board_size):
            for c in range(self.board_size):
                center = (c * self.tile_size + self.tile_size // 2, r * self.tile_size + self.tile_size // 2)
                if self.grid[r, c] == 1:
                    cv2.circle(board_img, center, self.tile_size // 3, self.black_color, -1)
                elif self.grid[r, c] == -1:
                    cv2.circle(board_img, center, self.tile_size // 3, self.white_color, -1)
        return board_img

    def start_game(self, search_depth=3):
        """Run the Go game using minimax."""
        while not self.check_game_end():
            img = self.display_board()
            cv2.imshow("Simple Go Game", img)
            cv2.waitKey(500)

            _, chosen_move = self.minimax(search_depth, -math.inf, math.inf, self.player_turn == 1)
            if chosen_move:
                self.apply_move(*chosen_move)
                print(f"Player {'Black' if self.player_turn == -1 else 'White'} moves to {chosen_move}")
            else:
                print(f"Player {'Black' if self.player_turn == 1 else 'White'} passes.")
                self.pass_moves += 1
                self.player_turn *= -1

        print("Game Over!")
        black, white = np.sum(self.grid == 1), np.sum(self.grid == -1)
        print(f"Final Score: Black = {black}, White = {white}")
        print("Winner:", "Black" if black > white else "White" if white > black else "Tie")

        cv2.waitKey(0)
        cv2.destroyAllWindows()


# Start the game
if __name__ == "__main__":
    game = SimpleGoGame(board_size=5)
    game.start_game(search_depth=3)
