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

# Commit 3 - Add Win Detection Logic

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