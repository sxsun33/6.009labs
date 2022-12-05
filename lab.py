# Snekoban Game

import json
import typing

# NO ADDITIONAL IMPORTS!

direction_vector = {
"up": (-1, 0),
"down": (+1, 0),
"left": (0, -1),
"right": (0, +1),
}

def new_game(level_description):
    """
    Given a description of a game state, create and return a game
    representation of your choice.

    The given description is a list of lists of lists of strs, representing the
    locations of the objects on the board (as described in the lab writeup).

    For example, a valid level_description is:

    [
        [[], ['wall'], ['computer']],
        [['target', 'player'], ['computer'], ['target']],
    ]

    The exact choice of representation is up to you; but note that what you
    return will be used as input to the other functions.
    """
    computer_location, target_location, wall_location = set(), set(), set()
    
    for x, row in enumerate(level_description):
        for y, object in enumerate(row):

            if object == ['player']: player_location = (x, y)
            elif object == ['computer']: computer_location.add((x, y))
            elif object == ['target']: target_location.add((x, y))
            elif object == ['wall']: wall_location.add((x, y))
            elif object == ['target', 'player'] or object == ['player', 'target']: 
                player_location = (x, y)
                target_location.add((x, y))
            elif object == ['target', 'computer'] or object == ['computer', 'target']:
                computer_location.add((x, y))
                target_location.add((x, y))
    
    return player_location, frozenset(computer_location), frozenset(target_location), frozenset(wall_location), len(level_description), len(level_description[0])

def victory_check(game):
    """
    Given a game representation (of the form returned from new_game), return
    a Boolean: True if the given game satisfies the victory condition, and
    False otherwise.
    """
    if len(game[1]) == 0 or len(game[2]) == 0:
        return False
    if len(game[1]) != len(game[2]):
        return False
    for computer in game[2]:
        if computer not in game[1]:
            return False
    return True

def step_game(game, direction):
    """
    Given a game representation (of the form returned from new_game), return a
    new game representation (of that same form), representing the updated game
    after running one step of the game.  The user's input is given by
    direction, which is one of the following: {'up', 'down', 'left', 'right'}.

    This function should not mutate its input.
    """
    vector = direction_vector[direction]
    player = game[0]
    computer_location = game[1]

    if can_move(game, player[0] + vector[0], player[1] + vector[1], direction):
        player_new_location = (player[0] + vector[0], player[1] + vector[1])
    
    else:
        return game
    
    if player_new_location in game[1]:
        computer_location = game[1] - {player_new_location}
        computer_location = computer_location.union(frozenset({(player_new_location[0] + vector[0], player_new_location[1] + vector[1])}))
    
    return player_new_location, computer_location, game[2], game[3], game[4], game[5]


def can_move(game, r, c, direction):

    vector = direction_vector[direction]
    potential_spot = (r + vector[0], c + vector[1])

    if 0 <= r < game[4] and 0 <= c < game[5] and (r, c) not in game[3]:
        if (r, c) in game[1]:
            return potential_spot not in game[1] and potential_spot not in game[3]
        else:
            return True

    return False

def dump_game(game):
    """
    Given a game representation (of the form returned from new_game), convert
    it back into a level description that would be a suitable input to new_game
    (a list of lists of lists of strings).

    This function is used by the GUI and the tests to see what your game
    implementation has done, and it can also serve as a rudimentary way to
    print out the current state of your game for testing and debugging on your
    own.
    """
    board = [[[] for i in range(game[5])] for i in range(game[4])]

    for row in range(game[4]):

        for col in range(game[5]):
            
        #    if game[0] == (row, col): # if location in player_location and target_location
        #       board[row][col] = ['target', 'player']

        #     if (row, col) in game[1] and (row, col) in game[2]: # if location in computer_location and target_location
        #         board[row].append(['target', 'computer'])

            if game[0] == (row, col): board[row][col].append('player') # if location in player_location

            if (row, col) in game[1]: board[row][col].append('computer') # if location in computer_location

            if (row, col) in game[2]: board[row][col].append('target') # if location in target_location

            if (row, col) in game[3]: board[row][col].append('wall') # if location in wall_location

    return board

def neighbors(game):
    '''
    returns the neighbors of a given state as well as the direction from the original state to the neighbor
    '''
    return [
        (step_game(game, direction), direction) for direction in direction_vector.keys()
    ]


def solve_puzzle(game):
    """
    Given a game representation (of the form returned from new game), find a
    solution.

    Return a list of strings representing the shortest sequence of moves ("up",
    "down", "left", and "right") needed to reach the victory condition.

    If the given level cannot be solved, return None.
    """
    if victory_check(game):
        return []
    
    agenda = [((game, "invalid"), )]
    visited = {game}

    while agenda:
        this_path = agenda.pop(0)
        terminal_state = this_path[-1][0]
        #print(neighbors(terminal_state))

        for neighbor in neighbors(terminal_state):
            if neighbor[0] not in visited:
                #print(neighbor[1])
                new_path = this_path + (neighbor, )

                if victory_check(neighbor[0]):
                    return [step for _, step in new_path if step != "invalid"]
                
                agenda.append(new_path)
                visited.add(neighbor[0])


if __name__ == "__main__":
    pass

