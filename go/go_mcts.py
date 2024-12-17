import numpy as np
import cv2
import random
import math

# Node class for the Monte Carlo Tree Search (MCTS)
class GameNode:
    def __init__(self, game_grid, parent=None, move_made=None, current_player=1):
        """
        Represents a node in the game tree.
        """
        self.grid = np.copy(game_grid)
        self.parent = parent
        self.move_made = move_made
        self.player = current_player
        self.visits = 0
        self.score = 0
        self.kids = []

    def expand_node(self, all_moves):
        """
        Add new child nodes for all possible moves.
        """
        # Go through each move
        for m in all_moves:
            # Copy the board state
            new_board = np.copy(self.grid)
            row, col = m
            new_board[row, col] = self.player
            # Add new node
            self.kids.append(GameNode(new_board, self, m, -self.player))

    def find_best_child(self, explore_factor=1.4):
        """
        Find the child node with the highest UCT score.
        """
        # If no moves exist, return None
        if not self.kids:
            return None
        # Formula to balance exploration and exploitation
        return max(self.kids, key=lambda child: child.score / (child.visits + 1e-6) +
                   explore_factor * math.sqrt(math.log(self.visits + 1) / (child.visits + 1e-6)))

    def backtrack_results(self, result):
        """
        Backpropagate results of the simulation to the root node.
        """
        # Increment visit count
        self.visits += 1
        # Update score
        self.score += result
        # Backtrack to parent with flipped result
        if self.parent:
            self.parent.backtrack_results(-result)

    def fully_expanded(self, all_moves):
        """
        Check if all possible moves have been expanded as children.
        """
        return len(self.kids) == len(all_moves)

# Main Go Game class
class SimpleGoGame:
    def __init__(self, board_size=5):
        """
        Set up the game board and basic parameters.
        """
        self.size = board_size
        self.grid = np.zeros((board_size, board_size), dtype=int)
        self.turn = 1
        self.tile_size = 100
        self.bg_color = (255, 220, 180)
        self.black_stone = (0, 0, 0)
        self.white_stone = (255, 255, 255)
        self.pass_counter = 0
        self.done = False

    def check_valid_spot(self, row, col):
        """
        Verify if a move is valid.
        """
        # Outside the board or already occupied
        if not (0 <= row < self.size and 0 <= col < self.size) or self.grid[row, col] != 0:
            return False

        # Check if placing a stone creates liberties
        temp_grid = np.copy(self.grid)
        temp_grid[row, col] = self.turn
        return self.check_liberty(temp_grid, row, col)

    def check_liberty(self, grid_state, row, col, visited=None):
        """
        Check for liberties (free spaces) for a group of stones.
        """
        if visited is None:
            visited = set()
        if (row, col) in visited:
            return False
        visited.add((row, col))

        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            # Check neighboring cells
            nr, nc = row + dx, col + dy
            if 0 <= nr < self.size and 0 <= nc < self.size:
                # Liberty found
                if grid_state[nr, nc] == 0:
                    return True
                if grid_state[nr, nc] == grid_state[row, col] and self.check_liberty(grid_state, nr, nc, visited):
                    return True
        return False

    def possible_moves(self):
        """
        Return all valid moves for the current player.
        """
        return [(row, col) for row in range(self.size) for col in range(self.size) if self.check_valid_spot(row, col)]

    def place_stone(self, row, col):
        """
        Make a move by placing a stone on the board.
        """
        if not self.check_valid_spot(row, col):
            return False
        self.grid[row, col] = self.turn
        # Switch player turn
        self.turn *= -1
        self.pass_counter = 0
        print(f"Player {'Black' if self.turn == -1 else 'White'} placed at ({row}, {col})")
        return True

    def pass_move(self):
        """
        Allow the current player to pass their turn.
        """
        print(f"Player {'Black' if self.turn == 1 else 'White'} passed.")
        self.pass_counter += 1
        self.turn *= -1
        if self.pass_counter >= 2:
            self.calculate_scores()

    def calculate_scores(self):
        """
        Calculate final scores and determine the winner.
        """
        black_score = np.sum(self.grid == 1)
        white_score = np.sum(self.grid == -1)
        print("Game Over!")
        print(f"Final Score -> Black: {black_score}, White: {white_score}")
        if black_score > white_score:
            print("Winner: Black")
        elif white_score > black_score:
            print("Winner: White")
        else:
            print("It's a draw!")
        self.done = True

    def monte_carlo_tree(self, simulations=200):
        """
        Perform Monte Carlo Tree Search to find the best move.
        """
        root = GameNode(self.grid, current_player=self.turn)
        for _ in range(simulations):
            node = root
            while node.kids and node.fully_expanded(self.possible_moves()):
                node = node.find_best_child()
            valid_moves = self.possible_moves()
            if not node.kids and valid_moves:
                node.expand_node(valid_moves)
                node = random.choice(node.kids)
            result = self.simulate_random_game(node.grid, node.player)
            node.backtrack_results(result)
        best_next = root.find_best_child(explore_factor=0)
        return best_next.move_made if best_next else None

    def simulate_random_game(self, grid, player):
        """
        Simulate a game randomly.
        """
        sim_grid = np.copy(grid)
        temp_player = player
        while True:
            all_moves = [(r, c) for r in range(self.size) for c in range(self.size) if sim_grid[r, c] == 0]
            if not all_moves:
                break
            r, c = random.choice(all_moves)
            sim_grid[r, c] = temp_player
            temp_player *= -1
        black = np.sum(sim_grid == 1)
        white = np.sum(sim_grid == -1)
        return 1 if black > white else -1 if white > black else 0

    def show_board(self):
        """
        Render the board visually with OpenCV.
        """
        img_size = self.size * self.tile_size
        img = np.ones((img_size, img_size, 3), dtype=np.uint8) * 255
        img[:, :] = self.bg_color
        for i in range(self.size + 1):
            start = i * self.tile_size
            cv2.line(img, (start, 0), (start, img_size), (0, 0, 0), 2)
            cv2.line(img, (0, start), (img_size, start), (0, 0, 0), 2)
        for r in range(self.size):
            for c in range(self.size):
                center = (c * self.tile_size + self.tile_size // 2, r * self.tile_size + self.tile_size // 2)
                if self.grid[r, c] == 1:
                    cv2.circle(img, center, self.tile_size // 3, self.black_stone, -1)
                elif self.grid[r, c] == -1:
                    cv2.circle(img, center, self.tile_size // 3, self.white_stone, -1)
        return img

    def play_game(self):
        """
        Run the game using MCTS for decisions.
        """
        while not self.done:
            img = self.show_board()
            cv2.imshow("Go Game", img)
            cv2.waitKey(500)
            move = self.monte_carlo_tree(simulations=200)
            if move:
                self.place_stone(*move)
            else:
                self.pass_move()
        img = self.show_board()
        cv2.imshow("Go Game", img)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

# Run the game
game = SimpleGoGame(board_size=5)
game.play_game()
