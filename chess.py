from math import inf as infinity
from random import choice
import numpy as np

HUMAN = 1
COMP = -1


#
#   全下标转换单下标ID
#
def index_trans(i, j):
    return 3 * i + j + 1


class Chess:

    def __init__(self) -> None:
        self.check_board = [[0, 0, 0] for _ in range(3)]  # 监控棋盘
        self.chess_board = [[0, 0, 0] for _ in range(3)]  # 实时棋盘
        self.white_chess = [0, 0, 0, 0, 0]
        self.black_chess = [0, 0, 0, 0, 0]
        self.angle = 0

    def get_angle(self):
        if self.angle > 45:
            return self.angle - 90
        else:
            return self.angle

    def set_angle(self, angle):
        self.angle = angle

    def reset(self):
        self.__init__()

    def find_chess(self, color):
        """找可用棋子

        Args:
            color (_type_): 颜色
        """
        if color == 'white':
            id = self.white_chess.index(0) + 1
            self.select_chess(color, id)
            return id
        else:
            id = self.black_chess.index(0) + 1
            self.select_chess(color, id)
            return id
        
    def find_empty(self, color):
        """找可用位置

        Args:
            color (_type_): _description_
        """
        if color == 'white':
            id = self.white_chess.index(1) + 1
            self.reback_chess(color, id)
            return id
        else:
            id = self.black_chess.index(1) + 1
            self.reback_chess(color, id)
            return id

    def reback_chess(self, color, id):
        """放回指定棋子

        Args:
            color (_type_): 棋子颜色
            id (_type_): 棋子ID (>=1 && <= 5)
        """
        if color == 'white':
            self.white_chess[id - 1] = 0
        else:
            self.black_chess[id - 1] = 0

    def select_chess(self, color, id):
        """指定挑选棋子

        Args:
            color (_type_): 棋子颜色
            id (_type_): 棋子ID (>=1 && <= 5)
        """
        if color == 'white':
            self.white_chess[id - 1] = 1
        else:
            self.black_chess[id - 1] = 1

    def get_board(self):
        return self.chess_board

    def set_board(self, chess_board):
        self.chess_board = chess_board
        print(chess_board)

    def set_check_board(self):
        # 设置当前
        self.check_board = self.chess_board

    def check_chess(self):
        """检查棋盘，当前实时棋盘状态和上一次读取的棋盘状态进行比对，定位人机棋子的偏移

        Returns:
            _type_: 返回修正矩阵 => [起始棋盘格，目标棋盘格]
        """
        def fillter(mat):
            for i in range(len(mat)):
                for j in range(len(mat[0])):
                    if mat[i][j] != COMP:
                        mat[i][j] = 0       

        ans = [0, 0]
        A = np.array(self.chess_board)
        B = np.array(self.check_board)
        fillter(A)
        fillter(B)

        C = A - B

        if np.count_nonzero(B) == 0:
            return ans

        for i in range(len(C)):
            for j in range(len(C[0])):
                if C[i][j] < 0:
                    ans[0] = index_trans(i, j)
                if C[i][j] > 0:
                    ans[1] = index_trans(i, j)

        if ans[0] == 0 or ans[0] == 0:
            return [0, 0]
        else:
            return ans

    def is_end(self):
        return game_over(self.chess_board)

def evaluate(state):
    """
    Function to heuristic evaluation of state.
    :param state: the state of the current board
    :return: +1 if the computer wins; -1 if the human wins; 0 draw
    """
    if wins(state, COMP):
        score = +1
    elif wins(state, HUMAN):
        score = -1
    else:
        score = 0

    return score


def wins(state, player):
    """
    This function tests if a specific player wins. Possibilities:
    * Three rows    [X X X] or [O O O]
    * Three cols    [X X X] or [O O O]
    * Two diagonals [X X X] or [O O O]
    :param state: the state of the current board
    :param player: a human or a computer
    :return: True if the player wins
    """
    win_state = [
        [state[0][0], state[0][1], state[0][2]],
        [state[1][0], state[1][1], state[1][2]],
        [state[2][0], state[2][1], state[2][2]],
        [state[0][0], state[1][0], state[2][0]],
        [state[0][1], state[1][1], state[2][1]],
        [state[0][2], state[1][2], state[2][2]],
        [state[0][0], state[1][1], state[2][2]],
        [state[2][0], state[1][1], state[0][2]],
    ]
    if [player, player, player] in win_state:
        return True
    else:
        return False


def valid_move(board, x, y):
    """
    A move is valid if the chosen cell is empty
    :param x: X coordinate
    :param y: Y coordinate
    :return: True if the board[x][y] is empty
    """
    if [x, y] in empty_cells(board):
        return True
    else:
        return False


def set_move(board, x, y, player):
    """
    Set the move on board, if the coordinates are valid
    :param x: X coordinate
    :param y: Y coordinate
    :param player: the current player
    """
    if valid_move(x, y):
        board[x][y] = player
        return True
    else:
        return False


def game_over(state):
    """
    This function test if the human or computer wins
    :param state: the state of the current board
    :return: True if the human or computer wins
    """
    return wins(state, HUMAN) or wins(state, COMP)


def empty_cells(state):
    """
    Each empty cell will be added into cells' list
    :param state: the state of the current board
    :return: a list of empty cells
    """
    cells = []

    for x, row in enumerate(state):
        for y, cell in enumerate(row):
            if cell == 0:
                cells.append([x, y])

    return cells


def minimax(state, depth, player):
    """
    AI function that choice the best move
    :param state: current state of the board
    :param depth: node index in the tree (0 <= depth <= 9),
    but never nine in this case (see iaturn() function)
    :param player: an human or a computer
    :return: a list with [the best row, best col, best score]
    """
    if player == COMP:
        best = [-1, -1, -infinity]
    else:
        best = [-1, -1, +infinity]

    if depth == 0 or game_over(state):
        score = evaluate(state)
        return [-1, -1, score]

    for cell in empty_cells(state):
        x, y = cell[0], cell[1]
        state[x][y] = player
        score = minimax(state, depth - 1, -player)
        state[x][y] = 0
        score[0], score[1] = x, y

        if player == COMP:
            if score[2] > best[2]:
                best = score  # max value
        else:
            if score[2] < best[2]:
                best = score  # min value

    return best


def ai_turn(board):
    """
    It calls the minimax function if the depth < 9,
    else it choices a random coordinate.
    :param c_choice: computer's choice X or O
    :param h_choice: human's choice X or O
    :return:
    """
    depth = len(empty_cells(board))
    if depth == 0 or game_over(board):
        return

    if depth == 9:
        x = choice([0, 1, 2])
        y = choice([0, 1, 2])
    else:
        move = minimax(board, depth, COMP)
        x, y = move[0], move[1]

    return index_trans(x, y)
