import _thread
from board_gui import *
from ai_player import *


class CheckerGame():
    def __init__(self):
        self.lock = _thread.allocate_lock()

        self.board = self.initBoard()

        # Initialize two AI players
        self.playerAI = AIPlayer(self)
        self.playerTurn = True
        self.opponentAI = AIPlayer(self)
        self.GUI = BoardGUI(self)

        # Start the game loop with two AI agents
        _thread.start_new_thread(self.AIMakeMove, ())

        self.GUI.startGUI()

    # Initialize the game board with positions
    def initBoard(self):
        board = [[0] * 6 for _ in range(6)]
        self.playerCheckers = set()
        self.opponentCheckers = set()
        self.checkerPositions = {}
        for i in range(6):
            self.playerCheckers.add(i + 1)
            self.opponentCheckers.add(-(i + 1))
            if i % 2 == 0:
                board[1][i] = -(i + 1)
                board[5][i] = i + 1
                self.checkerPositions[-(i + 1)] = (1, i)
                self.checkerPositions[i + 1] = (5, i)
            else:
                board[0][i] = -(i + 1)
                board[4][i] = i + 1
                self.checkerPositions[-(i + 1)] = (0, i)
                self.checkerPositions[i + 1] = (4, i)

        self.boardUpdated = True

        return board

    def getBoard(self):
        return self.board

    def printBoard(self):
        for i in range(len(self.board)):
            for j in range(len(self.board[i])):
                check = self.board[i][j]
                if (check < 0):
                    print(check, end=' ')
                else:
                    print(' ' + str(check), end=' ')

            print()

    def isBoardUpdated(self):
        return self.boardUpdated

    def setBoardUpdated(self):
        self.lock.acquire()
        self.boardUpdated = True
        self.lock.release()

    def completeBoardUpdate(self):
        self.lock.acquire()
        self.boardUpdated = False
        self.lock.release()

    def isPlayerTurn(self):
        return self.playerTurn

    # Switch turns between AI player and AI opponent.
    def changePlayerTurn(self):
        if self.playerTurn and self.playerCanContinue():
            self.playerTurn = False
        elif not self.playerTurn and self.opponentCanContinue():
            self.playerTurn = True

    # Apply the given move in the game
    def move(self, oldrow, oldcol, row, col):
        if not self.isValidMove(oldrow, oldcol, row, col, self.playerTurn):
            return

        self.makeMove(oldrow, oldcol, row, col)
        _thread.start_new_thread(self.next, ())

    # Update game state
    def next(self):
        if self.isGameOver():
            self.getGameSummary()
            return
        self.changePlayerTurn()
        self.AIMakeMove()

    # Pause GUI and let the current AI make the next move.
    def AIMakeMove(self):
        self.GUI.pauseGUI()
        if self.playerTurn:
            oldrow, oldcol, row, col = self.playerAI.getNextMove()
        else:
            oldrow, oldcol, row, col = self.opponentAI.getNextMove()

        self.move(oldrow, oldcol, row, col)
        self.GUI.resumeGUI()

    # Update checker position
    def makeMove(self, oldrow, oldcol, row, col):
        toMove = self.board[oldrow][oldcol]
        self.checkerPositions[toMove] = (row, col)

        # Move the checker
        self.board[row][col] = self.board[oldrow][oldcol]
        self.board[oldrow][oldcol] = 0

        # Capture move, remove captured checker
        if abs(oldrow - row) == 2:
            toRemove = self.board[(oldrow + row) // 2][(oldcol + col) // 2]
            if toRemove > 0:
                self.playerCheckers.remove(toRemove)
            else:
                self.opponentCheckers.remove(toRemove)
            self.board[(oldrow + row) // 2][(oldcol + col) // 2] = 0
            self.checkerPositions.pop(toRemove, None)

        self.setBoardUpdated()

    # Get all possible moves for the current player
    def getPossiblePlayerActions(self):
        checkers = self.playerCheckers if self.playerTurn else self.opponentCheckers
        regularDirs = [[-1, -1], [-1, 1]] if self.playerTurn else [[1, -1], [1, 1]]
        captureDirs = [[-2, -2], [-2, 2]] if self.playerTurn else [[2, -2], [2, 2]]

        regularMoves = []
        captureMoves = []
        for checker in checkers:
            oldrow = self.checkerPositions[checker][0]
            oldcol = self.checkerPositions[checker][1]
            for dir in regularDirs:
                if self.isValidMove(oldrow, oldcol, oldrow + dir[0], oldcol + dir[1], self.playerTurn):
                    regularMoves.append([oldrow, oldcol, oldrow + dir[0], oldcol + dir[1]])
            for dir in captureDirs:
                if self.isValidMove(oldrow, oldcol, oldrow + dir[0], oldcol + dir[1], self.playerTurn):
                    captureMoves.append([oldrow, oldcol, oldrow + dir[0], oldcol + dir[1]])

        # Must take capture move if possible
        return captureMoves if captureMoves else regularMoves

    # Check if the given move is valid
    def isValidMove(self, oldrow, oldcol, row, col, playerTurn):
        if oldrow < 0 or oldrow > 5 or oldcol < 0 or oldcol > 5 \
                or row < 0 or row > 5 or col < 0 or col > 5:
            return False
        if self.board[oldrow][oldcol] == 0 or self.board[row][col] != 0:
            return False

        if playerTurn:
            if row - oldrow == -1:
                return abs(col - oldcol) == 1
            elif row - oldrow == -2:
                return (col - oldcol == -2 and self.board[row + 1][col + 1] < 0) \
                    or (col - oldcol == 2 and self.board[row + 1][col - 1] < 0)
            else:
                return False
        else:
            if row - oldrow == 1:
                return abs(col - oldcol) == 1
            elif row - oldrow == 2:
                return (col - oldcol == -2 and self.board[row - 1][col + 1] > 0) \
                    or (col - oldcol == 2 and self.board[row - 1][col - 1] > 0)
            else:
                return False

    # Checks if either AI can continue
    def playerCanContinue(self):
        return any(self.isValidMove(r, c, r + d[0], c + d[1], True)
                   for checker in self.playerCheckers
                   for r, c in [self.checkerPositions[checker]]
                   for d in [[-1, -1], [-1, 1], [-2, -2], [-2, 2]])

    def opponentCanContinue(self):
        return any(self.isValidMove(r, c, r + d[0], c + d[1], False)
                   for checker in self.opponentCheckers
                   for r, c in [self.checkerPositions[checker]]
                   for d in [[1, -1], [1, 1], [2, -2], [2, 2]])

    # Checks if game is over
    def isGameOver(self):
        return len(self.playerCheckers) == 0 or len(self.opponentCheckers) == 0 \
            or (not self.playerCanContinue() and not self.opponentCanContinue())

    def getGameSummary(self):
        self.GUI.pauseGUI()
        print("Game Over!")
        playerNum = len(self.playerCheckers)
        opponentNum = len(self.opponentCheckers)
        if playerNum > opponentNum:
            print("AI Player 1 won by {0:d} checkers!".format(playerNum - opponentNum))
        elif playerNum < opponentNum:
            print("AI Player 2 won by {0:d} checkers!".format(opponentNum - playerNum))
        else:
            print("It is a draw! Try again!")

