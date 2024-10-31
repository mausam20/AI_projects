# -*- coding: utf-8 -*-
import os, time
import numpy as np
import random
import math
import cv2

# Constants
ROWS = 6
COLUMNS = 7
EMPTY = 0
HUMAN = 1
AI = 2

# Constants for board display
CELL_SIZE = 100
PADDING = 20
BOARD_COLOR = (255, 255, 255)  # White
HUMAN_COLOR = (255, 0, 0)  # Blue
AI_COLOR = (0, 0, 255)  # Red

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

def detect_win(board, player):
    # Horizontal win
    for col in range(COLUMNS - 3):
        for row in range(ROWS):
            if board[row][col] == player and board[row][col + 1] == player and \
               board[row][col + 2] == player and board[row][col + 3] == player:
                return True

    # Vertical win
    for col in range(COLUMNS):
        for row in range(ROWS - 3):
            if board[row][col] == player and board[row + 1][col] == player and \
               board[row + 2][col] == player and board[row + 3][col] == player:
                return True

    # Diagonal upwards win
    for col in range(COLUMNS - 3):
        for row in range(ROWS - 3):
            if board[row][col] == player and board[row + 1][col + 1] == player and \
               board[row + 2][col + 2] == player and board[row + 3][col + 3] == player:
                return True

    # Diagonal downwards win
    for col in range(COLUMNS - 3):
        for row in range(3, ROWS):
            if board[row][col] == player and board[row - 1][col + 1] == player and \
               board[row - 2][col + 2] == player and board[row - 3][col + 3] == player:
                return True

    return False

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
    for col in range(COLUMNS - 3):
        for row in range(ROWS):
            adjacent_pieces = [board[row][col], board[row][col + 1],
                               board[row][col + 2], board[row][col + 3]]
            score += evaluate_adjacents(adjacent_pieces, player)

    # Vertical pieces
    for col in range(COLUMNS):
        for row in range(ROWS - 3):
            adjacent_pieces = [board[row][col], board[row + 1][col],
                               board[row + 2][col], board[row + 3][col]]
            score += evaluate_adjacents(adjacent_pieces, player)

    # Diagonal upwards pieces
    for col in range(COLUMNS - 3):
        for row in range(ROWS - 3):
            adjacent_pieces = [board[row][col], board[row + 1][col + 1],
                               board[row + 2][col + 2], board[row + 3][col + 3]]
            score += evaluate_adjacents(adjacent_pieces, player)

    # Diagonal downwards pieces
    for col in range(COLUMNS - 3):
        for row in range(3, ROWS):
            adjacent_pieces = [board[row][col], board[row - 1][col + 1],
                               board[row - 2][col + 2], board[row - 3][col + 3]]
            score += evaluate_adjacents(adjacent_pieces, player)

    return score

def evaluate_adjacents(adjacent_pieces, player):
    opponent = AI if player == HUMAN else HUMAN
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


# Commit 5 - Implement Minimax Algorithm

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

    if maxi_player:
        value = -math.inf
        col = random.choice(valid_cols)
        for c in valid_cols:
            next_board = clone_and_place_piece(board, AI, c)
            new_score = minimax(next_board, ply - 1, alpha, beta, False)[1]
            if new_score > value:
                value = new_score
                col = c
            alpha = max(alpha, new_score)
            if beta <= alpha:
                break
        return col, value
    else:
        value = math.inf
        col = random.choice(valid_cols)
        for c in valid_cols:
            next_board = clone_and_place_piece(board, HUMAN, c)
            new_score = minimax(next_board, ply - 1, alpha, beta, True)[1]
            if new_score < value:
                value = new_score
                col = c
            beta = min(beta, new_score)
            if beta <= alpha:
                break
        return col, value
