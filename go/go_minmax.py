import numpy as np
import cv2

class GoGameWithOpenCV:
    def __init__(self, size=5):
        self.size = size
        self.board = np.zeros((size, size), dtype=int)
        self.current_player = 1  # 1 for black, -1 for white
        self.cell_size = 100
        self.board_color = (255, 220, 180)  # Light beige
        self.black_stone_color = (0, 0, 0)
        self.white_stone_color = (255, 255, 255)
        self.previous_states = []
        self.pass_count = 0
        self.game_over = False
        self.move_history = []

    def is_valid_move(self, x, y):
        if not (0 <= x < self.size and 0 <= y < self.size) or self.board[x, y] != 0:
            return False

        # Simulate the move to check for suicide
        self.board[x, y] = self.current_player
        valid = self.has_liberties(x, y)
        self.board[x, y] = 0  # Undo the move
        return valid

    def has_liberties(self, x, y, visited=None):
        if visited is None:
            visited = set()
        if (x, y) in visited:
            return False
        visited.add((x, y))

        if self.board[x, y] == 0:  # Empty space means liberty
            return True

        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nx, ny = x + dx, y + dy
            if 0 <= nx < self.size and 0 <= ny < self.size:
                if self.board[nx, ny] == 0 or (self.board[nx, ny] == self.board[x, y] and self.has_liberties(nx, ny, visited)):
                    return True
        return False

    def remove_captured_stones(self):
        to_remove = []
        for x in range(self.size):
            for y in range(self.size):
                if self.board[x, y] != 0 and not self.has_liberties(x, y):
                    to_remove.append((x, y))
        for x, y in to_remove:
            self.board[x, y] = 0

    def make_move(self, x, y):
        if not self.is_valid_move(x, y):
            return False
        self.board[x, y] = self.current_player
        self.remove_captured_stones()
        self.move_history.append((self.current_player, x, y))
        print(f"Player {'Black' if self.current_player == 1 else 'White'} places a stone at ({x}, {y})")
        self.current_player *= -1  # Switch player
        self.pass_count = 0  # Reset pass count after a valid move
        return True

    def pass_turn(self):
        print(f"Player {'Black' if self.current_player == 1 else 'White'} passes their turn.")
        self.current_player *= -1
        self.pass_count += 1
        if self.pass_count >= 2:
            self.calculate_winner()

    def calculate_winner(self):
        black_score = np.sum(self.board == 1)
        white_score = np.sum(self.board == -1)
        print("Game Over")
        print(f"Final Scores -> Black: {black_score}, White: {white_score}")
        if black_score > white_score:
            print("Winner: Black")
        elif white_score > black_score:
            print("Winner: White")
        else:
            print("It's a tie!")
        self.game_over = True

    def calculate_score(self):
        black_score = np.sum(self.board == 1)
        white_score = np.sum(self.board == -1)
        return black_score, white_score

    def get_valid_moves(self):
        return [(x, y) for x in range(self.size) for y in range(self.size) if self.is_valid_move(x, y)]

    def best_move(self):
        valid_moves = self.get_valid_moves()
        if not valid_moves:
            return None
        return valid_moves[np.random.randint(len(valid_moves))]

    def draw_board(self):
        img_size = self.size * self.cell_size
        img = np.ones((img_size, img_size, 3), dtype=np.uint8) * 255
        img[:, :] = self.board_color

        # Draw grid lines
        for i in range(self.size + 1):
            start = i * self.cell_size
            cv2.line(img, (start, 0), (start, img_size), (0, 0, 0), 2)
            cv2.line(img, (0, start), (img_size, start), (0, 0, 0), 2)

        # Draw stones
        for x in range(self.size):
            for y in range(self.size):
                if self.board[x, y] == 1:  # Black stone
                    center = (y * self.cell_size + self.cell_size // 2, x * self.cell_size + self.cell_size // 2)
                    cv2.circle(img, center, self.cell_size // 3, self.black_stone_color, -1)
                elif self.board[x, y] == -1:  # White stone
                    center = (y * self.cell_size + self.cell_size // 2, x * self.cell_size + self.cell_size // 2)
                    cv2.circle(img, center, self.cell_size // 3, self.white_stone_color, -1)

        return img

    def play_game(self):
        while not self.game_over:
            img = self.draw_board()
            cv2.imshow("Go Game", img)
            cv2.waitKey(500)
            move = self.best_move()
            if move:
                self.make_move(*move)
            else:
                self.pass_turn()

        img = self.draw_board()
        cv2.imshow("Go Game", img)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

# Run the game
game = GoGameWithOpenCV(size=5)
game.play_game()
