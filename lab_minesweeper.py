#!/usr/bin/env python3

import typing
import doctest

# NO ADDITIONAL IMPORTS ALLOWED!


def dump(game):
    """
    Prints a human-readable version of a game (provided as a dictionary)
    """
    for key, val in sorted(game.items()):
        if isinstance(val, list) and val and isinstance(val[0], list):
            print(f"{key}:")
            for inner in val:
                print(f"    {inner}")
        else:
            print(f"{key}:", val)


# 2-D IMPLEMENTATION


def new_game_2d(num_rows, num_cols, bombs):
    """
    Start a new game.

    Return a game state dictionary, with the 'dimensions', 'state', 'board' and
    'hidden' fields adequately initialized.

    Parameters:
       num_rows (int): Number of rows
       num_cols (int): Number of columns
       bombs (list): List of bombs, given in (row, column) pairs, which are
                     tuples

    Returns:
       A game state dictionary

    >>> dump(new_game_2d(2, 4, [(0, 0), (1, 0), (1, 1)]))
    board:
        ['.', 3, 1, 0]
        ['.', '.', 1, 0]
    dimensions: (2, 4)
    hidden:
        [True, True, True, True]
        [True, True, True, True]
    state: ongoing
    """
    board = []
    for r in range(num_rows):
        row = []
        for c in range(num_cols):
            if [r, c] in bombs or (r, c) in bombs:
                row.append(".")
            else:
                row.append(0)
        board.append(row)
    hidden = []
    for r in range(num_rows):
        row = []
        for c in range(num_cols):
            row.append(True)
        hidden.append(row)
    for r in range(num_rows):
        for c in range(num_cols):
            if board[r][c] == 0:
                neighbor_bombs = 0
                if 0 <= r - 1 < num_rows:
                    if 0 <= c - 1 < num_cols:
                        if board[r - 1][c - 1] == ".":
                            neighbor_bombs += 1
                if 0 <= r < num_rows:
                    if 0 <= c - 1 < num_cols:
                        if board[r][c - 1] == ".":
                            neighbor_bombs += 1
                if 0 <= r + 1 < num_rows:
                    if 0 <= c - 1 < num_cols:
                        if board[r + 1][c - 1] == ".":
                            neighbor_bombs += 1
                if 0 <= r - 1 < num_rows:
                    if 0 <= c < num_cols:
                        if board[r - 1][c] == ".":
                            neighbor_bombs += 1
                if 0 <= r < num_rows:
                    if 0 <= c < num_cols:
                        if board[r][c] == ".":
                            neighbor_bombs += 1
                if 0 <= r + 1 < num_rows:
                    if 0 <= c < num_cols:
                        if board[r + 1][c] == ".":
                            neighbor_bombs += 1
                if 0 <= r - 1 < num_rows:
                    if 0 <= c + 1 < num_cols:
                        if board[r - 1][c + 1] == ".":
                            neighbor_bombs += 1
                if 0 <= r < num_rows:
                    if 0 <= c + 1 < num_cols:
                        if board[r][c + 1] == ".":
                            neighbor_bombs += 1
                if 0 <= r + 1 < num_rows:
                    if 0 <= c + 1 < num_cols:
                        if board[r + 1][c + 1] == ".":
                            neighbor_bombs += 1
                board[r][c] = neighbor_bombs
    return {
        "dimensions": (num_rows, num_cols),
        "board": board,
        "hidden": hidden,
        "state": "ongoing",
    }


def dig_2d(game, row, col):
    """
    Reveal the cell at (row, col), and, in some cases, recursively reveal its
    neighboring squares.

    Update game['hidden'] to reveal (row, col).  Then, if (row, col) has no
    adjacent bombs (including diagonally), then recursively reveal (dig up) its
    eight neighbors.  Return an integer indicating how many new squares were
    revealed in total, including neighbors, and neighbors of neighbors, and so
    on.

    The state of the game should be changed to 'defeat' when at least one bomb
    is revealed on the board after digging (i.e. game['hidden'][bomb_location]
    == False), 'victory' when all safe squares (squares that do not contain a
    bomb) and no bombs are revealed, and 'ongoing' otherwise.

    Parameters:
       game (dict): Game state
       row (int): Where to start digging (row)
       col (int): Where to start digging (col)

    Returns:
       int: the number of new squares revealed

    >>> game = {'dimensions': (2, 4),
    ...         'board': [['.', 3, 1, 0],
    ...                   ['.', '.', 1, 0]],
    ...         'hidden': [[True, False, True, True],
    ...                  [True, True, True, True]],
    ...         'state': 'ongoing'}
    >>> dig_2d(game, 0, 3)
    4
    >>> dump(game)
    board:
        ['.', 3, 1, 0]
        ['.', '.', 1, 0]
    dimensions: (2, 4)
    hidden:
        [True, False, False, False]
        [True, True, False, False]
    state: victory

    >>> game = {'dimensions': [2, 4],
    ...         'board': [['.', 3, 1, 0],
    ...                   ['.', '.', 1, 0]],
    ...         'hidden': [[True, False, True, True],
    ...                  [True, True, True, True]],
    ...         'state': 'ongoing'}
    >>> dig_2d(game, 0, 0)
    1
    >>> dump(game)
    board:
        ['.', 3, 1, 0]
        ['.', '.', 1, 0]
    dimensions: [2, 4]
    hidden:
        [False, False, True, True]
        [True, True, True, True]
    state: defeat
    """
    if game["state"] == "defeat" or game["state"] == "victory":
        game["state"] = game["state"]  # keep the state the same
        return 0

    if game["board"][row][col] == ".":
        game["hidden"][row][col] = False
        game["state"] = "defeat"
        return 1

    bombs = 0
    hidden_squares = 0
    for r in range(game["dimensions"][0]):
        for c in range(game["dimensions"][1]):
            if game["board"][r][c] == ".":
                if game["hidden"][r][c] == False:
                    bombs += 1
            elif game["hidden"][r][c] == True:
                hidden_squares += 1
    if bombs != 0:
        # if bombs is not equal to zero, set the game state to defeat and
        # return 0
        game["state"] = "defeat"
        return 0
    if hidden_squares == 0:
        game["state"] = "victory"
        return 0

    if game["hidden"][row][col] != False:
        game["hidden"][row][col] = False
        revealed = 1
    else:
        return 0

    if game["board"][row][col] == 0:
        num_rows, num_cols = game["dimensions"]
        if 0 <= row - 1 < num_rows:
            if 0 <= col - 1 < num_cols:
                if game["board"][row - 1][col - 1] != ".":
                    if game["hidden"][row - 1][col - 1] == True:
                        revealed += dig_2d(game, row - 1, col - 1)
        if 0 <= row < num_rows:
            if 0 <= col - 1 < num_cols:
                if game["board"][row][col - 1] != ".":
                    if game["hidden"][row][col - 1] == True:
                        revealed += dig_2d(game, row, col - 1)
        if 0 <= row + 1 < num_rows:
            if 0 <= col - 1 < num_cols:
                if game["board"][row + 1][col - 1] != ".":
                    if game["hidden"][row + 1][col - 1] == True:
                        revealed += dig_2d(game, row + 1, col - 1)
        if 0 <= row - 1 < num_rows:
            if 0 <= col < num_cols:
                if game["board"][row - 1][col] != ".":
                    if game["hidden"][row - 1][col] == True:
                        revealed += dig_2d(game, row - 1, col)
        if 0 <= row < num_rows:
            if 0 <= col < num_cols:
                if game["board"][row][col] != ".":
                    if game["hidden"][row][col] == True:
                        revealed += dig_2d(game, row, col)
        if 0 <= row + 1 < num_rows:
            if 0 <= col < num_cols:
                if game["board"][row + 1][col] != ".":
                    if game["hidden"][row + 1][col] == True:
                        revealed += dig_2d(game, row + 1, col)
        if 0 <= row - 1 < num_rows:
            if 0 <= col + 1 < num_cols:
                if game["board"][row - 1][col + 1] != ".":
                    if game["hidden"][row - 1][col + 1] == True:
                        revealed += dig_2d(game, row - 1, col + 1)
        if 0 <= row < num_rows:
            if 0 <= col + 1 < num_cols:
                if game["board"][row][col + 1] != ".":
                    if game["hidden"][row][col + 1] == True:
                        revealed += dig_2d(game, row, col + 1)
        if 0 <= row + 1 < num_rows:
            if 0 <= col + 1 < num_cols:
                if game["board"][row + 1][col + 1] != ".":
                    if game["hidden"][row + 1][col + 1] == True:
                        revealed += dig_2d(game, row + 1, col + 1)

    bombs = 0  # set number of bombs to 0
    hidden_squares = 0
    for r in range(game["dimensions"][0]):
        # for each r,
        for c in range(game["dimensions"][1]):
            # for each c,
            if game["board"][r][c] == ".":
                if game["hidden"][r][c] == False:
                    # if the game hidden is False, and the board is '.', add 1 to
                    # bombs
                    bombs += 1
            elif game["hidden"][r][c] == True:
                hidden_squares += 1
    bad_squares = bombs + hidden_squares
    if bad_squares > 0:
        game["state"] = "ongoing"
        return revealed
    else:
        game["state"] = "victory"
        return revealed


def render_2d_locations(game, xray=False):
    """
    Prepare a game for display.

    Returns a two-dimensional array (list of lists) of '_' (hidden squares),
    '.' (bombs), ' ' (empty squares), or '1', '2', etc. (squares neighboring
    bombs).  game['hidden'] indicates which squares should be hidden.  If
    xray is True (the default is False), game['hidden'] is ignored and all
    cells are shown.

    Parameters:
       game (dict): Game state
       xray (bool): Whether to reveal all tiles or just the that are not
                    game['hidden']

    Returns:
       A 2D array (list of lists)

    >>> render_2d_locations({'dimensions': (2, 4),
    ...         'state': 'ongoing',
    ...         'board': [['.', 3, 1, 0],
    ...                   ['.', '.', 1, 0]],
    ...         'hidden':  [[True, False, False, True],
    ...                   [True, True, False, True]]}, False)
    [['_', '3', '1', '_'], ['_', '_', '1', '_']]

    >>> render_2d_locations({'dimensions': (2, 4),
    ...         'state': 'ongoing',
    ...         'board': [['.', 3, 1, 0],
    ...                   ['.', '.', 1, 0]],
    ...         'hidden':  [[True, False, True, False],
    ...                   [True, True, True, False]]}, True)
    [['.', '3', '1', ' '], ['.', '.', '1', ' ']]
    """
    board = [[] for i in range(game['dimensions'][0])]

    for r in range(game['dimensions'][0]):

        for c in range(game['dimensions'][1]):

            if game['hidden'][r][c] == True and not xray: board[r].append('_')

            else:
                if game['board'][r][c] == 0: board[r].append(' ')
                else: board[r].append(str(game['board'][r][c]))
    return board

def render_2d_board(game, xray=False):
    """
    Render a game as ASCII art.

    Returns a string-based representation of argument 'game'.  Each tile of the
    game board should be rendered as in the function
        render_2d_locations(game)

    Parameters:
       game (dict): Game state
       xray (bool): Whether to reveal all tiles or just the ones allowed by
                    game['hidden']

    Returns:
       A string-based representation of game

    >>> render_2d_board({'dimensions': (2, 4),
    ...                  'state': 'ongoing',
    ...                  'board': [['.', 3, 1, 0],
    ...                            ['.', '.', 1, 0]],
    ...                  'hidden':  [[False, False, False, True],
    ...                            [True, True, False, True]]})
    '.31_\\n__1_'
    """
    board = render_2d_locations(game, xray)
    string_rep = ''
    for r in range(len(board)):
        if r != 0:
            string_rep += '\n'
        for c in range(len(board[0])):
            string_rep += board[r][c]
    
    return string_rep

# N-D IMPLEMENTATION

def return_value(array, coordinates):
    '''
    A function that, given an N-d array and a tuple/list of coordinates, 
    returns the value at those coordinates in the array.
    '''
    if len(coordinates) == 0:
        return AssertionError, "no coordinates"
    elif len(coordinates) == 1:
        return array[coordinates[0]]
    else:
        return return_value(array[coordinates[0]], coordinates[1:])

def replace_value(array, coordinates, value):
    '''
    A function that, given an N-d array, a tuple/list of coordinates, and a value, 
    replaces the value at those coordinates in the array with the given value.
    '''
    if len(coordinates) == 0:
        return AssertionError, "no coordinates"
    elif len(coordinates) == 1:
        array[coordinates[0]] = value
    else:
        replace_value(array[coordinates[0]], coordinates[1:], value)

def new_N_d_array(dimensions, value):
    '''
    A function that, given a list of dimensions and a value, 
    creates a new N-d array with those dimensions, 
    where each value in the array is the given value.
    '''
    if len(dimensions) == 0:
        return AssertionError, "no dimensions"
    elif len(dimensions) == 1:
        return [value for i in range(dimensions[0])]
    else:
        
        return [new_N_d_array(dimensions[1:], value) for i in range(dimensions[0])]

def game_state(game):
    '''
    A function that, given a game, 
    returns the state of that game ('ongoing', 'defeat', or 'victory').
    '''
    total_num_squares = 1
    for num in game['dimensions']:
        total_num_squares *= num
    if count_squares(game['hidden'], False) == total_num_squares - game["no. bombs"]:
        return 'victory'
    else:
        return game['state']
    
def count_squares(board, bomb_or_False):
    count = 0
    if not isinstance(board[0], list):
        count += board.count(bomb_or_False)
    else:
        for r in board:
            count += count_squares(r, bomb_or_False)
    return count

def neighbors(coordinates, dimensions):
    '''
    A function that returns all the neighbors of a given set of coordinates 
    in a given game coordinate.
    '''
    if len(coordinates) == 0:
        return AssertionError, "no coordinates"
    elif len(coordinates) != len(dimensions):
        return AssertionError, 'coordinates and dimensions not matching'
    else:
        neighbors_set = {()}
        for i, coordinate in enumerate(coordinates):
            possible_variation = {(coordinate, )}
            if coordinate > 0:
                possible_variation.add((coordinate - 1, ))
            if coordinate + 1 < dimensions[i]:
                possible_variation.add((coordinate + 1, ))

            neighbors_set = {first + rest for first in neighbors_set
            for rest in possible_variation}
    return neighbors_set - {coordinates}         

def all_possible_coordinates(dim):
    '''
    A function that returns all possible coordinates in a given board dimension.
    '''
    if len(dim) == 1:
        for i in range(dim[0]):
            yield (i, )
    else:
        for first in range(dim[0]):
            for rest in all_possible_coordinates(dim[1:]):
                yield (first, ) + rest

def new_game_nd(dimensions, bombs):
    """
    Start a new game.

    Return a game state dictionary, with the 'dimensions', 'state', 'board' and
    'hidden' fields adequately initialized.


    Args:
       dimensions (tuple): Dimensions of the board
       bombs (list): Bomb locations as a list of tuples, each an
                     N-dimensional coordinate

    Returns:
       A game state dictionary

    >>> g = new_game_nd((2, 4, 2), [(0, 0, 1), (1, 0, 0), (1, 1, 1)])
    >>> dump(g)
    board:
        [[3, '.'], [3, 3], [1, 1], [0, 0]]
        [['.', 3], [3, '.'], [1, 1], [0, 0]]
    dimensions: (2, 4, 2)
    hidden:
        [[True, True], [True, True], [True, True], [True, True]]
        [[True, True], [True, True], [True, True], [True, True]]
    no. bombs: 3
    state: ongoing
    
    """
    board = new_N_d_array(dimensions, 0)
    for bomb in bombs: 
        replace_value(board, bomb, '.')
    for coordinate in all_possible_coordinates(dimensions):
        if return_value(board, coordinate) != '.':
            num_neigh_bomb = 0
            for neigh in neighbors(coordinate, dimensions):
                if return_value(board, neigh) == '.':
                    num_neigh_bomb += 1
            replace_value(board, coordinate, num_neigh_bomb)

    return {
        "dimensions": dimensions,
        "board": board,
        "hidden": new_N_d_array(dimensions, True),
        "state": "ongoing",
        "no. bombs": len(bombs),
    }


def dig_nd(game, coordinates):
    """
    Recursively dig up square at coords and neighboring squares.

    Update the hidden to reveal square at coords; then recursively reveal its
    neighbors, as long as coords does not contain and is not adjacent to a
    bomb.  Return a number indicating how many squares were revealed.  No
    action should be taken and 0 returned if the incoming state of the game
    is not 'ongoing'.

    The updated state is 'defeat' when at least one bomb is revealed on the
    board after digging, 'victory' when all safe squares (squares that do
    not contain a bomb) and no bombs are revealed, and 'ongoing' otherwise.

    Args:
       coordinates (tuple): Where to start digging

    Returns:
       int: number of squares revealed

    >>> g = {'dimensions': (2, 4, 2),
    ...      'board': [[[3, '.'], [3, 3], [1, 1], [0, 0]],
    ...                [['.', 3], [3, '.'], [1, 1], [0, 0]]],
    ...      'hidden': [[[True, True], [True, False], [True, True],
    ...                [True, True]],
    ...               [[True, True], [True, True], [True, True],
    ...                [True, True]]],
    ...      'state': 'ongoing',
    ...      'no. bombs': 3,}
    >>> dig_nd(g, (0, 3, 0))
    8
    >>> dump(g)
    board:
        [[3, '.'], [3, 3], [1, 1], [0, 0]]
        [['.', 3], [3, '.'], [1, 1], [0, 0]]
    dimensions: (2, 4, 2)
    hidden:
        [[True, True], [True, False], [False, False], [False, False]]
        [[True, True], [True, True], [False, False], [False, False]]
    no. bombs: 3
    state: ongoing
    >>> g = {'dimensions': (2, 4, 2),
    ...      'board': [[[3, '.'], [3, 3], [1, 1], [0, 0]],
    ...                [['.', 3], [3, '.'], [1, 1], [0, 0]]],
    ...      'hidden': [[[True, True], [True, False], [True, True],
    ...                [True, True]],
    ...               [[True, True], [True, True], [True, True],
    ...                [True, True]]],
    ...      'state': 'ongoing'
    ...      'no. bombs': 3,}
    >>> dig_nd(g, (0, 0, 1))
    1
    >>> dump(g)
    board:
        [[3, '.'], [3, 3], [1, 1], [0, 0]]
        [['.', 3], [3, '.'], [1, 1], [0, 0]]
    dimensions: (2, 4, 2)
    hidden:
        [[True, False], [True, False], [True, True], [True, True]]
        [[True, True], [True, True], [True, True], [True, True]]
    no. bombs: 3
    state: defeat
    """
    if game["state"] == "defeat" or game["state"] == "victory":
        return 0

    if return_value(game['board'], coordinates) == '.':
        replace_value(game['hidden'], coordinates, False)
        game["state"] = "defeat"
        return 1

    elif return_value(game['board'], coordinates) != 0:
        replace_value(game['hidden'], coordinates, False)
        game["state"] = game_state(game)
        return 1

    else:
        revealed = 1
        replace_value(game['hidden'], coordinates, False)
        for neigh in neighbors(coordinates, game['dimensions']):
            if not return_value(game['hidden'], neigh):
                if return_value(game['board'], neigh) != '.':
                    revealed += dig_nd(game, neigh)
        return revealed


def render_nd(game, xray=False):
    """
    Prepare the game for display.

    Returns an N-dimensional array (nested lists) of '_' (hidden squares), '.'
    (bombs), ' ' (empty squares), or '1', '2', etc. (squares neighboring
    bombs).  The game['hidden'] array indicates which squares should be
    hidden.  If xray is True (the default is False), the game['hidden'] array
    is ignored and all cells are shown.

    Args:
       xray (bool): Whether to reveal all tiles or just the ones allowed by
                    game['hidden']

    Returns:
       An n-dimensional array of strings (nested lists)

    >>> g = {'dimensions': (2, 4, 2),
    ...      'board': [[[3, '.'], [3, 3], [1, 1], [0, 0]],
    ...                [['.', 3], [3, '.'], [1, 1], [0, 0]]],
    ...      'hidden': [[[True, True], [True, False], [False, False],
    ...                [False, False]],
    ...               [[True, True], [True, True], [False, False],
    ...                [False, False]]],
    ...      'state': 'ongoing'}
    >>> render_nd(g, False)
    [[['_', '_'], ['_', '3'], ['1', '1'], [' ', ' ']],
     [['_', '_'], ['_', '_'], ['1', '1'], [' ', ' ']]]

    >>> render_nd(g, True)
    [[['3', '.'], ['3', '3'], ['1', '1'], [' ', ' ']],
     [['.', '3'], ['3', '.'], ['1', '1'], [' ', ' ']]]
    """
    
    if xray:
        return_list = new_N_d_array(game['dimensions'], ' ')
        for coordinate in all_possible_coordinates(game['dimensions']):
            if return_value(game['board'], coordinate) != 0:
                replace_value(return_list, coordinate, str(return_value(game['board'], coordinate)))
    else:
        return_list = new_N_d_array(game['dimensions'], '_')
        for coordinate in all_possible_coordinates(game['dimensions']):
            if not return_value(game['hidden'], coordinate):

                if return_value(game['board'], coordinate) == 0:
                    replace_value(return_list, coordinate, ' ')
                else:
                    replace_value(return_list, coordinate, str(return_value(game['board'], coordinate)))
    return return_list

if __name__ == "__main__":
    # Test with doctests. Helpful to debug individual lab.py functions.
    _doctest_flags = doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS
    doctest.testmod(optionflags=_doctest_flags)  # runs ALL doctests

    # Alternatively, can run the doctests JUST for specified function/methods,
    # e.g., for render_2d_locations or any other function you might want.  To
    # do so, comment out the above line, and uncomment the below line of code.
    # This may be useful as you write/debug individual doctests or functions.
    # Also, the verbose flag can be set to True to see all test results,
    # including those that pass.
    #
    #doctest.run_docstring_examples(
    #    render_2d_locations,
    #    globals(),
    #    optionflags=_doctest_flags,
    #    verbose=False
    # )
