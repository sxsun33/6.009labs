#!/usr/bin/env python3

##################
# Game Constants #
##################

# other than TILE_SIZE, feel free to move, modify, or delete these constants as
# you see fit.

TILE_SIZE = 128

# vertical movement
GRAVITY = -9
MAX_DOWNWARD_SPEED = 48
PLAYER_JUMP_SPEED = 62
PLAYER_JUMP_DURATION = 3
PLAYER_BORED_THRESHOLD = 60

# horizontal movement
PLAYER_DRAG = 6
PLAYER_MAX_HORIZONTAL_SPEED = 48
PLAYER_HORIZONTAL_ACCELERATION = 16


# the following maps single-letter strings to the name of the object they
# represent, for use with deserialization in Game.__init__.
SPRITE_MAP = {
    "p": "player",
    "c": "cloud",
    "=": "floor",
    "B": "building",
    "C": "castle",
    "u": "cactus",
    "t": "tree",
}


##########################
# Classes and Game Logic #
##########################


class Rectangle:
    """
    A rectangle object to help with collision detection and resolution.
    """

    def __init__(self, x, y, w, h):
        """
        Initialize a new rectangle.

        `x` and `y` are the coordinates of the bottom-left corner. `w` and `h`
        are the dimensions of the rectangle.
        """
        self.x = x
        self.y = y
        self.w = w
        self.h = h

    def intersects(self, other):
        """
        Check whether `self` and `other` (another Rectangle) overlap.

        Rectangles are open on the top and right sides, and closed on the
        bottom and left sides; concretely, this means that the rectangle
        [0, 0, 1, 1] does not intersect either of [0, 1, 1, 1] or [1, 0, 1, 1].
        """
        return self.horizontal_collision(other) and self.vertical_collision(other)

    def horizontal_collision(self, r2):
        horizontal = False
        if self.x > r2.x and (r2.x + r2.w) > self.x:
            horizontal = True
        if r2.x > self.x and (self.x + self.w) > r2.x:
            horizontal = True
        if r2.x == self.x:
            horizontal = True
        return horizontal
    
    def vertical_collision(self, r2):
        vertical = False
        if self.y > r2.y and (r2.y + r2.h) > self.y:
            vertical = True
        if r2.y > self.y and (self.y + self.h) > r2.y:
            vertical = True
        if r2.y == self.y:
            vertical = True
        return vertical

    @staticmethod
    def translation_vector(r1, r2):
        """
        Compute how much `r2` needs to move to stop intersecting `r1`.

        If `r2` does not intersect `r1`, return `None`.  Otherwise, return a
        minimal pair `(x, y)` such that translating `r2` by `(x, y)` would
        suppress the overlap. `(x, y)` is minimal in the sense of the "L1"
        distance; in other words, the sum of `abs(x)` and `abs(y)` should be
        as small as possible.

        When two pairs `(x1, y1)` and `(x2, y2)` are tied in terms of this
        metric, return the one whose first element has the smallest
        magnitude.
        """
        if not r1.intersects(r2):
            return None
        else:
            # horizontal overlap
            if (r1.x + r1.w - r2.x) < (r2.x + r2.w - r1.x):
                x = r1.x + r1.w - r2.x
            else:
                x = -(r2.x + r2.w - r1.x)
            
            # vertical overlap
            if (r1.y + r1.h - r2.y) < (r2.y + r2.h - r1.y):
                y = r1.y + r1.h - r2.y
            else:
                y = -(r2.y + r2.h - r1.y)
            
            # compare which overlap is smaller
            if abs(x) < abs(y):
                y = 0
            else:
                x = 0

            return (x, y)

class Game:
    def __init__(self, level_map):
        """
        Initialize a new game, populated with objects from `level_map`.

        `level_map` is a 2D array of 1-character strings; all possible strings
        (and some others) are listed in the SPRITE_MAP dictionary.  Each
        character in `level_map` corresponds to a sprite of size `TILE_SIZE *
        TILE_SIZE`.

        This function is free to store `level_map`'s data however it wants.
        For example, it may choose to just keep a copy of `level_map`; or it
        could choose to read through `level_map` and extract the position of
        each sprite listed in `level_map`.

        Any choice is acceptable, as long as it works with the implementation
        of `timestep` and `render` below.
        """
        level_map_dict = {}
        n = len(level_map)
        l = len(level_map[0])

        for r in range(n):
            for c in range(l):
                if level_map[r][c] == "p":
                    level_map_dict['player'] = (c* TILE_SIZE, (n - 1 - r)*TILE_SIZE)
                else:
                    char = level_map[r][c]
                    sprite = SPRITE_MAP.get(char, None)
                    if sprite is not None:
                        if sprite not in level_map_dict:
                            level_map_dict[sprite] = {(c* TILE_SIZE, (n - 1 - r)*TILE_SIZE), }
                        else:
                            level_map_dict[sprite].add((c* TILE_SIZE, (n - 1 - r)*TILE_SIZE))

        self.level_map = level_map_dict
        self.velocity = (0, 0)
        self.status = 'ongoing'
        self.num_steps = -1

    def timestep(self, keys):
        """
        Simulate the evolution of the game state over one time step.  `keys` is
        a list of currently pressed keys.
        """
        if len(keys) == 0:
            self.num_steps += 1
        else:
            self.num_steps = -1
            
        if self.status == 'ongoing':

            # gravity

            new_y_velocity = self.velocity[1] + GRAVITY
            if new_y_velocity < -MAX_DOWNWARD_SPEED:
                self.velocity = (self.velocity[0], -MAX_DOWNWARD_SPEED)
            else:
                self.velocity = (self.velocity[0], self.velocity[1] + GRAVITY)

            # considering keys

            keys_list = keys[:]

            if 'up' in keys_list and 'down' in keys_list:
                keys_list.remove('up')
                keys_list.remove('down')

            if 'left' in keys_list and 'right' in keys_list:
                keys_list.remove('left')
                keys_list.remove('right')

            for key in keys_list:
                if key == "up":
                    self.velocity = (self.velocity[0], PLAYER_JUMP_SPEED + GRAVITY)
                if key == "down":
                    self.velocity = (self.velocity[0], -MAX_DOWNWARD_SPEED)
                if key == "right":
                    self.velocity = (self.velocity[0] + PLAYER_HORIZONTAL_ACCELERATION, self.velocity[1])
                if key == "left":
                    self.velocity = (self.velocity[0] - PLAYER_HORIZONTAL_ACCELERATION, self.velocity[1])
            
            # horizontal drag

            horizontal_velocity = self.velocity[0]
            
            if horizontal_velocity < 0:
                horizontal_velocity = horizontal_velocity + PLAYER_DRAG
                if horizontal_velocity < -PLAYER_MAX_HORIZONTAL_SPEED:
                    horizontal_velocity = -PLAYER_MAX_HORIZONTAL_SPEED
                if horizontal_velocity > 0:
                    horizontal_velocity = 0

            if horizontal_velocity > 0:
                horizontal_velocity = horizontal_velocity - PLAYER_DRAG
                if horizontal_velocity > PLAYER_MAX_HORIZONTAL_SPEED:
                    horizontal_velocity = PLAYER_MAX_HORIZONTAL_SPEED
                if horizontal_velocity < 0:
                    horizontal_velocity = 0

            self.velocity = (horizontal_velocity, self.velocity[1])

            self.level_map['player'] = (self.level_map['player'][0] + self.velocity[0], self.level_map['player'][1] + self.velocity[1])

            self.resolve_collision()


    def resolve_collision(self):

        dynamic = {'player': self.level_map['player']}
        static = self.level_map.copy()
        del static['player']
        
        def update_position(axis):
            for key, locs in static.items():
                if key != "player":
                    for loc in locs:
                        sprite = Rectangle(loc[0], loc[1], TILE_SIZE, TILE_SIZE)

                        for char, position in dynamic.items():

                            player_r = Rectangle(position[0], position[1], TILE_SIZE, TILE_SIZE)
                            vec = Rectangle.translation_vector(sprite, player_r)

                            if vec is not None:
                                if key == 'castle':
                                    self.status = 'victory'
                                if key == 'cactus':
                                    self.status = 'defeat'

                                if axis == "vertical": 
                                    if vec[0] == 0:
                                        self.level_map[char] = (position[0] + vec[0], position[1] + vec[1])
                                        if (vec[1] < 0 and self.velocity[1] > 0) or (vec[1] > 0 and self.velocity[1] < 0):
                                            self.velocity = (self.velocity[0], 0)
                                        
                                if axis == "horizontal":
                                    
                                    self.level_map[char] = (position[0] + vec[0], position[1] + vec[1])
                                    if (vec[1] < 0 and self.velocity[1] > 0) or (vec[1] > 0 and self.velocity[1] < 0): 
                                        self.velocity = (self.velocity[0], 0)
                                    if (vec[0] < 0 and self.velocity[0] > 0) or (vec[0] > 0 and self.velocity[0] < 0) :
                                        self.velocity = (0, self.velocity[1])                           
                                        
        update_position('vertical')
        dynamic = {'player': self.level_map['player']}
        update_position('horizontal')
        self.state()
                 
    def state(self):
        player_loc = self.level_map["player"]
        if player_loc[1] < -TILE_SIZE:
            self.status = 'defeat'

        '''
        else:
            player_r = Rectangle(player_loc[0], player_loc[1], TILE_SIZE, TILE_SIZE)

            for loc in self.level_map.get('cactus', set()):
                cactus = Rectangle(loc[0], loc[1], TILE_SIZE, TILE_SIZE)
                if Rectangle.intersects(cactus, player_r):
                    self.status = 'defeat'
                    break

            if self.status == 'ongoing':
                castle_locs = self.level_map.get('castle', None)
                if castle_locs is not None:
                    for castle_loc in castle_locs:
                        castle = Rectangle(castle_loc[0], castle_loc[1], TILE_SIZE, TILE_SIZE)
                        if Rectangle.intersects(castle, player_r):
                            self.status = 'victory'
                            break
                        '''

    def render(self, w, h):
        """
        Report status and list of sprite dictionaries for sprites with a
        horizontal distance of w//2 from player.  See writeup for details.
        """
                
        player_loc = self.level_map["player"]

        if self.status == 'ongoing':
            if self.num_steps >= PLAYER_BORED_THRESHOLD:
                player_sprite = {'texture': 'sleeping', 'pos': player_loc, 'player': True}
            else:
                player_sprite = {'texture': 'slight_smile', 'pos': player_loc, 'player': True}
        if self.status == 'victory':
            player_sprite = {'texture': 'partying_face', 'pos': player_loc, 'player': True}
        if self.status == 'defeat':
            player_sprite = {'texture': 'injured', 'pos': player_loc, 'player': True} 

        w_l = player_loc[0] - w//2 - TILE_SIZE
        w_u = player_loc[0] + w//2

        h_l = -TILE_SIZE
        h_u = h
        
        sprites_list = []
        if player_loc[1] < h and player_loc[1] > -TILE_SIZE:
            sprites_list.append(player_sprite)
        
        def texture(s): # returns corresponding texture given sprite
            if s == "building":
                texture = 'classical_building'
            if s == "cactus":
                texture = 'cactus'
            if s == "castle":
                texture = 'castle'
            if s == "cloud":
                texture = 'cloud'
            if s == "floor":
                texture = 'black_large_square'
            if s == "tree":
                texture = 'tree'
            return texture

        for sprite, locs in self.level_map.items():
            if sprite != 'player':
                for loc in locs:
                    if w_l < loc[0] < w_u and h_l < loc[1] < h_u:
                        sprites_list.append({'texture': texture(sprite), 'pos': loc, 'player': False})

        return (self.status, sprites_list)

if __name__ == "__main__":
    pass
