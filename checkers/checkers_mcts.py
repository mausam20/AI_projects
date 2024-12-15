import numpy as np
import random
import math
import cv2
import copy

class CheckersGame:
    def __init__(self):
        self.board = np.zeros((8, 8), dtype=int)
        self.initialize_board()
        self.current_player = 1

    def initialize_board(self):
        for i in range(3):
            for j in range(8):
                if (i + j) % 2 == 1:
                    self.board[i][j] = 1
        for i in range(5, 8):
            for j in range(8):
                if (i + j) % 2 == 1:
                    self.board[i][j] = -1

    def get_legal_moves(self):
        capturing_moves = []
        regular_moves = []

        for i in range(8):
            for j in range(8):
                if self.board[i][j] == self.current_player:  # Regular piece
                    capturing_moves += self.get_capturing_moves(i, j, king=False)
                    regular_moves += self.get_regular_moves(i, j, king=False)
                elif self.board[i][j] == 2 * self.current_player:  # King piece
                    capturing_moves += self.get_capturing_moves(i, j, king=True)
                    regular_moves += self.get_regular_moves(i, j, king=True)

        # Enforce mandatory jumps if capturing moves are available
        return capturing_moves if capturing_moves else regular_moves

    def get_capturing_moves(self, i, j, king=False):
        moves = []
        directions = [(1, 1), (1, -1), (-1, 1), (-1, -1)] if king else [(1, 1), (1, -1)] if self.current_player == 1 else [(-1, 1), (-1, -1)]

        for di, dj in directions:
            x, y = i + di, j + dj
            # Check for opponent's piece
            if 0 <= x < 8 and 0 <= y < 8 and self.board[x][y] * self.current_player < 0:
                nx, ny = x + di, y + dj
                if 0 <= nx < 8 and 0 <= ny < 8 and self.board[nx][ny] == 0:  # Landing spot empty
                    moves.append(((i, j), (nx, ny)))
        return moves

    def get_regular_moves(self, i, j, king=False):
        moves = []
        directions = [(1, 1), (1, -1), (-1, 1), (-1, -1)] if king else [(1, 1), (1, -1)] if self.current_player == 1 else [(-1, 1), (-1, -1)]
        for di, dj in directions:
            x, y = i + di, j + dj
            if 0 <= x < 8 and 0 <= y < 8 and self.board[x][y] == 0:
                moves.append(((i, j), (x, y)))
        return moves

    def make_move(self, move):
        start, end = move
        start_x, start_y = start
        end_x, end_y = end

        # Update the board
        self.board[end_x][end_y] = self.board[start_x][start_y]
        self.board[start_x][start_y] = 0

        # Check for jumps and remove captured pieces
        if abs(end_x - start_x) == 2:
            mid_x = (start_x + end_x) // 2
            mid_y = (start_y + end_y) // 2
            self.board[mid_x][mid_y] = 0

            # Check for multi-jump moves
            additional_jumps = self.get_capturing_moves(end_x, end_y, king=abs(self.board[end_x][end_y]) == 2)
            if additional_jumps:
                return self  # Allow another jump without switching player

        # Check for kinging
        if (self.current_player == 1 and end_x == 7) or (self.current_player == -1 and end_x == 0):
            self.board[end_x][end_y] = 2 * self.current_player

        self.switch_player()
        return copy.deepcopy(self)

    def is_game_over(self):
        # Game is over if the current player has no moves
        return len(self.get_legal_moves()) == 0

    def get_winner(self):
        player_1_pieces = np.sum(self.board == 1) + np.sum(self.board == 2)
        player_2_pieces = np.sum(self.board == -1) + np.sum(self.board == -2)

        # If the current player has no moves, they lose
        if len(self.get_legal_moves()) == 0:
            return -self.current_player

        if player_1_pieces == 0:
            return -1  # Player 2 wins
        elif player_2_pieces == 0:
            return 1  # Player 1 wins
        return 0  # Game not over

    def switch_player(self):
        self.current_player = -self.current_player

class CheckersAgent:
    def __init__(self, player, mcts_itermax=1000):
        self.player = player
        self.mcts = MCTS(CheckersGame(), itermax=mcts_itermax)

    def select_move(self, game_state):
        return self.mcts.search(game_state)

class MCTS:
    def __init__(self, game, itermax=1000):
        self.game = game
        self.itermax = itermax

    def search(self, state):
        root = MCTSNode(copy.deepcopy(state))

        for i in range(self.itermax):
            node = self.select(root)
            if node is None:
                break
            score = self.rollout(node.state)
            self.backpropagate(node, score)

        if not root.children:
            return None

        return root.most_visited_child().move

    def select(self, node):
        while not node.state.is_game_over():
            if not node.is_fully_expanded():
                return self.expand(node)
            else:
                node = node.best_child()
        return node

    def expand(self, node):
        tried_moves = [child.move for child in node.children]
        possible_moves = node.state.get_legal_moves()
        for move in possible_moves:
            if move not in tried_moves:
                next_state = node.state.make_move(move)
                new_node = MCTSNode(next_state, parent=node, move=move)
                node.children.append(new_node)
                return new_node
        return None

    def rollout(self, state):
        current_rollout_state = copy.deepcopy(state)
        steps = 0
        while not current_rollout_state.is_game_over():
            possible_moves = current_rollout_state.get_legal_moves()
            if not possible_moves:
                return 0
            move = self.rollout_policy(possible_moves)
            current_rollout_state = current_rollout_state.make_move(move)
            steps += 1
            if steps > 100:
                break
        return 1 if current_rollout_state.get_winner() == state.current_player else -1

    def backpropagate(self, node, result):
        while node is not None:
            node.visits += 1
            node.value += result if node.state.current_player == self.game.current_player else -result
            node = node.parent

    def rollout_policy(self, possible_moves):
        return possible_moves[np.random.randint(len(possible_moves))]

class MCTSNode:
    def __init__(self, state, parent=None, move=None):
        self.state = state
        self.parent = parent
        self.move = move
        self.children = []
        self.visits = 0
        self.value = 0

    def is_fully_expanded(self):
        return len(self.children) == len(self.state.get_legal_moves())

    def best_child(self, c_param=1.4):
        choices_weights = [
            (child.value / child.visits) + c_param * math.sqrt((2 * math.log(self.visits) / child.visits))
            for child in self.children
        ]
        return self.children[np.argmax(choices_weights)]

    def most_visited_child(self):
        return max(self.children, key=lambda c: c.visits)

def draw_board(board):
    cell_size = 80
    board_size = 8 * cell_size
    img = np.zeros((board_size, board_size, 3), dtype=np.uint8)

    for i in range(8):
        for j in range(8):
            color = (255, 255, 255) if (i + j) % 2 == 0 else (0, 0, 0)
            cv2.rectangle(img, (j * cell_size, i * cell_size), ((j + 1) * cell_size, (i + 1) * cell_size), color, -1)

    for i in range(8):
        for j in range(8):
            if board[i][j] == 1:
                cv2.circle(img, (j * cell_size + cell_size // 2, i * cell_size + cell_size // 2), cell_size // 3, (255, 0, 0), -1)
            elif board[i][j] == -1:
                cv2.circle(img, (j * cell_size + cell_size // 2, i * cell_size + cell_size // 2), cell_size // 3, (0, 0, 255), -1)
            elif board[i][j] == 2:
                cv2.circle(img, (j * cell_size + cell_size // 2, i * cell_size + cell_size // 2), cell_size // 3, (255, 165, 0), -1)
            elif board[i][j] == -2:
                cv2.circle(img, (j * cell_size + cell_size // 2, i * cell_size + cell_size // 2), cell_size // 3, (0, 255, 255), -1)

    return img

def play_game():
    game = CheckersGame()
    agent1 = CheckersAgent(player=1)
    agent2 = CheckersAgent(player=-1)

    cv2.namedWindow('Checkers Game')

    while not game.is_game_over():
        if game.current_player == 1:
            move = agent1.select_move(game)
            print(f"Player 1 makes move: {move}")
        else:
            move = agent2.select_move(game)
            print(f"Player 2 makes move: {move}")

        game.make_move(move)
        img = draw_board(game.board)
        cv2.imshow('Checkers Game', img)
        cv2.waitKey(500)

    winner = game.get_winner()
    if winner == 0:
        print("Game ended in a draw!")
    else:
        print(f"Winner: {'Player 1' if winner == 1 else 'Player 2'}")

    cv2.waitKey(0)
    cv2.destroyAllWindows()

if __name__ == "__main__":
    play_game()
