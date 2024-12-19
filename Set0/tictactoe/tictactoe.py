"""
Tic Tac Toe Player
"""

import math
import copy

X = "X"
O = "O"
EMPTY = None


def initial_state():
    """
    Returns starting state of the board.
    """
    return [[EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY]]


def player(board):
    """
    Returns player who has the next turn on a board.
    """
    return X if sum(row.count(X) for row in board) == sum(row.count(O) for row in board) else O
        



def actions(board):
    """
    Returns set of all possible actions (i, j) available on the board.
    """
    return { (i, j) 
            for i, row in enumerate(board) 
                for j, cell in enumerate(row) 
                    if cell == EMPTY 
        }          



def result(board, action):
    """
    Returns the board that results from making move (i, j) on the board.
    """

    (i, j) = action

    if not is_valid_coordinate(board, i, j):
        raise ValueError("Coordinates go beyond the board.")
    
    if board[i][j] != EMPTY:  
        raise ValueError("Cell already taken.")
    
    copy_board = copy.deepcopy(board)

    copy_board[i][j] = player(board)

    return copy_board

    
def winner(board):
    """
    Returns the winner of the game, if there is one.
    """
    n = len(board)

    for i in range(n):

        # Horizontal 
        if check_line(board[i]):
            return board[i][0] 

        # Vertical 
        if check_line([board[j][i] for j in range(n)]):
            return board[0][i] 
    
    # Left to Right    
    if check_line([board[i][i] for i in range(n)]):
        return board[0][0]

    # Right to Left
    if check_line([board[i][n - i - 1] == board[0][n - 1] for i in range(n)]):
        return board[0][n - 1]
    
    return None


def terminal(board):
    """
    Returns True if game is over, False otherwise.
    """
    if winner(board) or all(cell != EMPTY for row in board for cell in row):
       return True
    
    return False




def utility(board):
    """
    Returns 1 if X has won the game, -1 if O has won, 0 otherwise.
    """
    if terminal(board):
        return {X: 1, O: -1}.get(winner(board), 0)
        


def minimax(board):
    """
    Returns the optimal action for the current player on the board.
    """

    best_action = None

    if player(board) == X:
        
       _, best_action = max_value(board, -math.inf, math.inf) 

    else:
       
       _, best_action = min_value(board, -math.inf, math.inf) 


    return best_action            




def max_value(board, alpha, beta):
    
    v = -math.inf
    best_action = None

    if terminal(board):
        return utility(board), None

    for action in actions(board):

        min_val, _ = min_value(result(board, action), alpha, beta)

        v, best_action = update(min_val, action, v, best_action, compare=lambda x, y: x > y)

        # Update alpha
        alpha = max(v, alpha)
        
        # Beta cut-off
        if alpha >= beta:
            break

    return v, best_action 



def min_value(board, alpha, beta):

    v = math.inf

    best_action = None

    if terminal(board):
        return utility(board), None

    for action in actions(board):

        max_val, _ = max_value(result(board, action), alpha, beta)

        v, best_action = update(max_val, action, v, best_action, compare=lambda x, y: x < y)

        beta = min(v, beta)
        
        # Alpha cut off
        if beta <= alpha:
            break  

    return v, best_action    

    

def is_valid_coordinate(board, i, j):
  return 0 <= i < len(board) and 0 <= j < len(board[0])


def check_line(line):
  return line[0] != EMPTY and all(cell == line[0] for cell in line)



def update(current_value, current_action, best_value, best_action, compare):
    """
    Updates the best value and action based on a comparison function.
    :param compare: A function that takes two values and returns True if the first is better.
    """
    if compare(current_value, best_value):
        return current_value, current_action
    return best_value, best_action   
