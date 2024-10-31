import numpy as np
import cv2
import random


class GoGame:
    def __init__(self, size=9):
        self.size = size
        self.board = np.zeros((size, size), dtype=int)  # 0: empty, 1: black, 2: white
        self.current_player = 1  # 1: black, 2: white

    def display_board(self):
        img = np.ones((self.size * 50, self.size * 50, 3), dtype=np.uint8) * 200
        for i in range(self.size):
            cv2.line(img, (50 * i, 0), (50 * i, self.size * 50), (0, 0, 0), 1)
            cv2.line(img, (0, 50 * i), (self.size * 50, 50 * i), (0, 0, 0), 1)

        for i in range(self.size):
            for j in range(self.size):
                if self.board[i, j] == 1:
                    cv2.circle(img, (j * 50 + 25, i * 50 + 25), 20, (0, 0, 0), -1)  # black stone
                elif self.board[i, j] == 2:
                    cv2.circle(img, (j * 50 + 25, i * 50 + 25), 20, (255, 255, 255), -1)  # white stone

        cv2.imshow('Go Game', img)
        cv2.waitKey(100)  # Wait for a short time to see the move

    def play_random_move(self):
        empty_positions = np.argwhere(self.board == 0)
        if empty_positions.size > 0:
            move = random.choice(empty_positions)
            self.board[move[0], move[1]] = self.current_player
            self.current_player = 2 if self.current_player == 1 else 1  # Switch player

    def count_score(self):
        black_score = np.sum(self.board == 1)
        white_score = np.sum(self.board == 2)

        # For simplicity, we'll just count the stones. Territory counting would require a more complex algorithm.
        return black_score, white_score

    def determine_winner(self, black_score, white_score):
        if black_score > white_score:
            return "Black wins!"
        elif white_score > black_score:
            return "White wins!"
        else:
            return "It's a draw!"

    def play_game(self):
        for _ in range(self.size * self.size):  # Play up to size*size moves
            self.display_board()
            self.play_random_move()

        cv2.destroyAllWindows()

        # Count scores and determine winner after the game
        black_score, white_score = self.count_score()
        print(f"Final Score - Black: {black_score}, White: {white_score}")
        print(self.determine_winner(black_score, white_score))


if __name__ == "__main__":
    game = GoGame(size=9)
    game.play_game()
