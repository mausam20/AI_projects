import numpy as np
import random
import cv2
import copy

# Checkers Game Class
class SimpleCheckers:
    def __init__(self):
        # Initialize the empty board
        self.grid = np.zeros((8, 8), dtype=int)
        self.init_grid()
        # Player 1 starts the game
        self.current_turn = 1

    def init_grid(self):
        """ This function put the pieces on the board initially. """
        # Top rows for Player 1
        for i in range(3):
            for j in range(8):
                # Only dark squares
                if (i + j) % 2 == 1:
                    # Player 1 normal pieces
                    self.grid[i][j] = 1
        # Bottom rows for Player 2
        for i in range(5, 8):
            for j in range(8):
                if (i + j) % 2 == 1:
                    # Player 2 normal pieces
                    self.grid[i][j] = -1

    def get_moves(self):
        """
        Find all valid moves for the current player.
        It checks for capturing moves first because jumps are required.
        """
        # For capturing moves
        jumps = []
        # For regular moves
        steps = []

        # loop through all the rows and columns
        for r in range(8):
            for c in range(8):
                # If it's the player's normal piece
                if self.grid[r][c] == self.current_turn:
                    jumps += self.check_jump_moves(r, c, is_king=False)
                    steps += self.check_simple_moves(r, c, is_king=False)
                # If it's a king piece
                elif self.grid[r][c] == 2 * self.current_turn:
                    jumps += self.check_jump_moves(r, c, is_king=True)
                    steps += self.check_simple_moves(r, c, is_king=True)
        # Jump moves have higher priority
        return jumps if jumps else steps

    def check_jump_moves(self, row, col, is_king=False):
        """ Check all possible jump (capture) moves for a piece. """
        moves = []
        dirs = [(1, 1), (1, -1), (-1, 1), (-1, -1)] if is_king else [(1, 1), (1, -1)] if self.current_turn == 1 else [(-1, 1), (-1, -1)]

        for dx, dy in dirs:
            enemy_x, enemy_y = row + dx, col + dy
            # Check for an opponent piece in the adjacent square
            if 0 <= enemy_x < 8 and 0 <= enemy_y < 8 and self.grid[enemy_x][enemy_y] * self.current_turn < 0:
                # Landing square after the jump
                land_x, land_y = enemy_x + dx, enemy_y + dy
                if 0 <= land_x < 8 and 0 <= land_y < 8 and self.grid[land_x][land_y] == 0:
                    # Valid capturing move
                    moves.append(((row, col), (land_x, land_y)))
        return moves

    def check_simple_moves(self, row, col, is_king=False):
        """ Check all simple moves (non-capturing) for a piece. """
        moves = []
        dirs = [(1, 1), (1, -1), (-1, 1), (-1, -1)] if is_king else [(1, 1), (1, -1)] if self.current_turn == 1 else [(-1, 1), (-1, -1)]
        for dx, dy in dirs:
            new_x, new_y = row + dx, col + dy
            if 0 <= new_x < 8 and 0 <= new_y < 8 and self.grid[new_x][new_y] == 0:
                # Valid regular move
                moves.append(((row, col), (new_x, new_y)))
        return moves

    def apply_move(self, move):
        """
        Move a piece to a new position and handle captures or promotions.
        """
        start, end = move
        r1, c1 = start
        r2, c2 = end

        # Move the piece
        self.grid[r2][c2] = self.grid[r1][c1]
        self.grid[r1][c1] = 0

        # Remove captured piece if it was a jump
        if abs(r2 - r1) == 2:
            mid_r, mid_c = (r1 + r2) // 2, (c1 + c2) // 2
            self.grid[mid_r][mid_c] = 0

            # Check for multi-jump
            further_jumps = self.check_jump_moves(r2, c2, is_king=abs(self.grid[r2][c2]) == 2)
            # Continue the turn
            if further_jumps:
                return self

        # Promote to king
        if (self.current_turn == 1 and r2 == 7) or (self.current_turn == -1 and r2 == 0):
            self.grid[r2][c2] = 2 * self.current_turn

        self.switch_turn()
        return copy.deepcopy(self)

    def switch_turn(self):
        """ Switch the current player turn. """
        self.current_turn = -self.current_turn

    def is_game_done(self):
        """ Check if the game is over by verifying if a player has no moves. """
        return len(self.get_moves()) == 0

    def who_won(self):
        """ Determine who won the game if it's over. """
        pieces_p1 = np.sum(self.grid == 1) + np.sum(self.grid == 2)
        pieces_p2 = np.sum(self.grid == -1) + np.sum(self.grid == -2)

        # The current player loses if they can't move
        if len(self.get_moves()) == 0:
            return -self.current_turn
        # Player 2 wins
        elif pieces_p1 == 0:
            return -1
            # Player 1 wins
        elif pieces_p2 == 0:
            return 1
        return 0

def display_board(grid):
    """ Draw the checkers board using OpenCV. """
    square_size = 80
    img = np.zeros((8 * square_size, 8 * square_size, 3), dtype=np.uint8)

    for row in range(8):
        for col in range(8):
            color = (255, 255, 255) if (row + col) % 2 == 0 else (0, 0, 0)
            cv2.rectangle(img, (col * square_size, row * square_size),
                          ((col + 1) * square_size, (row + 1) * square_size), color, -1)

            # Draw pieces
            if grid[row][col] == 1:
                cv2.circle(img, ((col + 1) * square_size - 40, (row + 1) * square_size - 40), 30, (0, 0, 255), -1)
            elif grid[row][col] == -1:
                cv2.circle(img, ((col + 1) * square_size - 40, (row + 1) * square_size - 40), 30, (255, 0, 0), -1)
    return img

def main():
    """ Main function to run the game loop. """
    game = SimpleCheckers()
    cv2.namedWindow("Checkers Game")

    while not game.is_game_done():
        moves = game.get_moves()
        if not moves:
            break
        # Randomly select a move for simplicity
        game.apply_move(random.choice(moves))

        img = display_board(game.grid)
        cv2.imshow("Checkers Game", img)
        cv2.waitKey(500)

    winner = game.who_won()
    print("Game Over!")
    if winner == 1:
        print("Player 1 (Red) wins!")
    elif winner == -1:
        print("Player 2 (Blue) wins!")
    else:
        print("It's a draw!")

    cv2.waitKey(0)
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
