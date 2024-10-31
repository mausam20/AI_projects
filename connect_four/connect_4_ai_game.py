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


