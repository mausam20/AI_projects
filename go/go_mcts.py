import numpy as np
import cv2
import random
import math

class Node:
    def __init__(self, board, parent=None, move=None, player=1):
        self.board = np.copy(board)
        self.parent = parent
        self.move = move
        self.player = player
        self.visits = 0
        self.value = 0
        self.children = []

    def expand(self, valid_moves):
        for move in valid_moves:
            new_board = np.copy(self.board)
            x, y = move
            new_board[x, y] = self.player
            self.children.append(Node(new_board, self, move, -self.player))

    def best_child(self, exploration_weight=1.4):
        if not self.children:  # Handle case where no valid moves exist
            return None
        return max(self.children, key=lambda child: child.value / (child.visits + 1e-6) + exploration_weight * math.sqrt(math.log(self.visits + 1) / (child.visits + 1e-6)))

    def backpropagate(self, result):
        self.visits += 1
        self.value += result
        if self.parent:
            self.parent.backpropagate(-result)

    def is_fully_expanded(self, valid_moves):
        return len(self.children) == len(valid_moves)

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
        temp_board = np.copy(self.board)
        temp_board[x, y] = self.current_player
        return self.has_liberties(temp_board, x, y)

    def has_liberties(self, board, x, y, visited=None):
        if visited is None:
            visited = set()
        if (x, y) in visited:
            return False
        visited.add((x, y))
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nx, ny = x + dx, y + dy
            if 0 <= nx < self.size and 0 <= ny < self.size:
                if board[nx, ny] == 0:
                    return True
                if board[nx, ny] == board[x, y] and self.has_liberties(board, nx, ny, visited):
                    return True
        return False

    def get_valid_moves(self):
        return [(x, y) for x in range(self.size) for y in range(self.size) if self.is_valid_move(x, y)]

    def make_move(self, x, y):
        if not self.is_valid_move(x, y):
            return False
        self.board[x, y] = self.current_player
        self.current_player *= -1  # Switch player
        self.pass_count = 0
        print(f"Player {'Black' if self.current_player == -1 else 'White'} places a stone at ({x}, {y})")
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

    def mcts(self, simulations=100):
        root = Node(self.board, player=self.current_player)
        for _ in range(simulations):
            node = root
            # Selection
            while node.children and node.is_fully_expanded(self.get_valid_moves()):
                node = node.best_child()
            # Expansion
            valid_moves = self.get_valid_moves()
            if not node.children and valid_moves:
                node.expand(valid_moves)
                node = random.choice(node.children)
            # Simulation
            winner = self.simulate_game(node.board, node.player)
            # Backpropagation
            node.backpropagate(winner)
        best_child = root.best_child(exploration_weight=0)
        return best_child.move if best_child else None

    def simulate_game(self, board, player):
        temp_board = np.copy(board)
        temp_player = player
        while True:
            moves = [(x, y) for x in range(self.size) for y in range(self.size) if temp_board[x, y] == 0]
            if not moves:
                break
            move = random.choice(moves)
            temp_board[move[0], move[1]] = temp_player
            temp_player *= -1
        black_score = np.sum(temp_board == 1)
        white_score = np.sum(temp_board == -1)
        return 1 if black_score > white_score else -1 if white_score > black_score else 0

    def draw_board(self):
        img_size = self.size * self.cell_size
        img = np.ones((img_size, img_size, 3), dtype=np.uint8) * 255
        img[:, :] = self.board_color
        for i in range(self.size + 1):
            start = i * self.cell_size
            cv2.line(img, (start, 0), (start, img_size), (0, 0, 0), 2)
            cv2.line(img, (0, start), (img_size, start), (0, 0, 0), 2)
        for x in range(self.size):
            for y in range(self.size):
                if self.board[x, y] == 1:
                    center = (y * self.cell_size + self.cell_size // 2, x * self.cell_size + self.cell_size // 2)
                    cv2.circle(img, center, self.cell_size // 3, self.black_stone_color, -1)
                elif self.board[x, y] == -1:
                    center = (y * self.cell_size + self.cell_size // 2, x * self.cell_size + self.cell_size // 2)
                    cv2.circle(img, center, self.cell_size // 3, self.white_stone_color, -1)
        return img

    def play_game(self):
        while not self.game_over:
            img = self.draw_board()
            cv2.imshow("Go Game", img)
            cv2.waitKey(500)
            move = self.mcts(simulations=200)
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
