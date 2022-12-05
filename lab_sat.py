#!/usr/bin/env python3

import sys
import typing
import doctest

sys.setrecursionlimit(10_000)
# NO ADDITIONAL IMPORTS

def modify_rules(current_rules, new_assignment):
    '''
    update the CNF formula based upon the new assignment; the new assignment is passed in as a tuple ('a', True/False)
    '''
    reverse_assignment = test_assignment(new_assignment)
    updated_rules = [list({(i[0], i[1]) for i in j}) for j in current_rules]
    
    for i, condition in enumerate(current_rules):
        if reverse_assignment in condition:
            updated_rules[i].remove(reverse_assignment)
    for con in updated_rules:
        if new_assignment in con:
            updated_rules.remove(con)
    
    return updated_rules

def test_assignment(new_assignment):
    '''
    returns the opposite condition from given
    '''
    if new_assignment[1]: return (new_assignment[0], False)

    else: return (new_assignment[0], True)

def satisfying_assignment(formula):
    """
    Find a satisfying assignment for a given CNF formula.
    Returns that assignment if one exists, or None otherwise.

    >>> satisfying_assignment([])
    {}
    >>> x = satisfying_assignment([[('a', True), ('b', False), ('c', True)]])
    >>> x.get('a', None) is True or x.get('b', None) is False or x.get('c', None) is True
    True
    >>> satisfying_assignment([[('a', True)], [('a', False)]])
    """
    if len(formula) == 0: # base case
        return {}

    if [] in formula:
        return None

    for condition in formula:
        if len(condition) == 1:
            condition_guessed = condition[0]
            break
        else:
            condition_guessed = formula[0][0]

    condition_guessed_reversed = test_assignment(condition_guessed)

    new_rules = modify_rules(formula, condition_guessed)

    if [] in new_rules:
        result = satisfying_assignment(modify_rules(formula, condition_guessed_reversed))
        if result is not None: 
            return {condition_guessed_reversed[0]: condition_guessed_reversed[1]} | result

    result = satisfying_assignment(new_rules) 
    if result is not None:
        return {condition_guessed[0]: condition_guessed[1]} | result

    else:
        result_a = satisfying_assignment(modify_rules(formula, condition_guessed_reversed)) 
        if result_a is not None: 
            return {condition_guessed_reversed[0]: condition_guessed_reversed[1]} | result_a  

def subgrid(board, r, c):
    '''
    identify the subgrid of a board given the location of the grid of interest
    '''
    sw = int(len(board) ** (1/2))
    return (r//sw, c//sw)

def values_in_row(board, r):
    return set(board[r]) - {0}

def values_in_column(board, c):
    return set(board[r][c] for r in range(len(board))) - {0}

def values_and_coord_in_subgrid(board, sr, sc):
    sw = int(len(board) ** (1/2))
    values = set()
    coord = set()
    for r in range(sr*sw, (sr + 1)*sw):
        for c in range(sc*sw, (sc + 1)*sw):
            values.add(board[r][c])
            coord.add((r, c))
    return values - {0}, coord

def not_possible_values(board):
    '''
    Return a dict mapping values already exsisting in each row
    '''
    result_row = {}
    result_col = {}
    result_subgrid = {}
    n = len(board)
    for i in range(n):
        result_row[str(i)] =  values_in_row(board, i)
        result_col[str(i)] = values_in_column(board, i)
    for j in range(int(len(board) ** (1/2))):
        for k in range(int(len(board) ** (1/2))):
            result_subgrid[(j, k)] = values_and_coord_in_subgrid(board, j, k)[0]
        
    return result_row, result_col, result_subgrid  

def rule_1(board):
    '''
    grid contains one of the numbers in remaining possibilities if its value is 0 in the original board; otherwise set it to the value in the original board
    '''
    not_possible_dicts = not_possible_values(board)
    all_values = {i + 1 for i in range(len(board))}
    rule_1_list = []
    n = len(board)
    for r in range(n):
        for c in range(n):

            if board[r][c] != 0:
                for i in range(1, n+1):
                    if i != board[r][c]:
                        rule_1_list.append([((r, c, i), False)])
                    else:
                        rule_1_list.append([((r, c, i), True)])
  
            else:
                not_possible = not_possible_dicts[0][str(r)] | not_possible_dicts[1][str(c)] | not_possible_dicts[2][subgrid(board, r, c)]
                remaining_possibilities = all_values - not_possible
                possibility_rule = [((r, c, j), True) for j in remaining_possibilities]
                
                rule_1_list.append(possibility_rule)
    return rule_1_list

def rule_list_coord_possible_values(coordinates, possibilities):
    '''
    Generate a rule list making sure only one value per coord given a set of coordinates and all their value possibilities
    '''
    rule_list = set()
    for value in possibilities:
        for coord1 in coordinates:
            for coord2 in coordinates:
                if coord1 != coord2 and ((coord2 + (value, ), False), (coord1 + (value, ), False)) not in rule_list:
                    rule_list.add(((coord1 + (value, ), False), (coord2 + (value, ), False)))
    return list(list(condition) for condition in rule_list)

def rule_row_column_subgrid(board):
    '''
    no duplicates in a row, column or subgrid
    '''
    result = []
    # no duplicates in row
    for r in range(len(board)):
        possibilities = {(i + 1) for i in range(len(board))} - values_in_row(board, r)
        coord_with_0 = {(r, c) for c in range(len(board)) if board[r][c] == 0}
        result.extend(rule_list_coord_possible_values(coord_with_0, possibilities))
    
    # no duplicates in col
    for c in range(len(board)):
        possibilities = {(i + 1) for i in range(len(board))} - values_in_column(board, c)
        coord_with_0 = {(r, c) for r in range(len(board)) if board[r][c] == 0}
        result.extend(rule_list_coord_possible_values(coord_with_0, possibilities))

    # no duplicates in subgrid
    for sr in range(int(len(board) ** (1/2))):
        for sc in range(int(len(board) ** (1/2))):
            possibilities = {(i + 1) for i in range(len(board))} - values_and_coord_in_subgrid(board, sr, sc)[0]
            coord_with_0 = {coord for coord in values_and_coord_in_subgrid(board, sr, sc)[1] if board[coord[0]][coord[1]] == 0}
            result.extend(rule_list_coord_possible_values(coord_with_0, possibilities))
    return result    

def sudoku_board_to_sat_formula(sudoku_board):
    """
    Generates a SAT formula that, when solved, represents a solution to the
    given sudoku board.  The result should be a formula of the right form to be
    passed to the satisfying_assignment function above.
    """
    return rule_1(sudoku_board) + rule_row_column_subgrid(sudoku_board)

def assignments_to_sudoku_board(assignments, n):
    """
    Given a variable assignment as given by satisfying_assignment, as well as a
    size n, construct an n-by-n 2-d array (list-of-lists) representing the
    solution given by the provided assignment of variables.

    If the given assignments correspond to an unsolveable board, return None
    instead.
    """
    if assignments is None:
        return None
    object_set = set()
    for object, assignment in assignments.items():
        if assignment:
            object_set.add(object)
    if len(object_set) != (n ** 2):
        return None
    
    else:
        board = [[0 for _ in range(n)] for __ in range(n)]
        for stuff in object_set:

            board[stuff[0]][stuff[1]] = stuff[2]

    return board

if __name__ == "__main__":
    import doctest

    _doctest_flags = doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS
    doctest.testmod(optionflags=_doctest_flags)
