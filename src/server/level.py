# -*- coding: utf-8 -*-

"""Module that contains the class Level."""

from src.server.player import Player
from src.graphic import symbols


class Level:
    """Class Level. It contains a 2D list of characters that represent the
    state of the map currently. This attribute can't be deleted.
    The Level does not include the player."""
    
    def __init__(self, list_2D):
        """Constructor for the class Level."""
        self._list_2D = list(list_2D)
        
        
    def __repr__(self):
        """Special function that shows how to print the Level class on screen."""
        return "\n".join(self._list_2D)
    
    
    def __getitem__(self, index):
        """Special function that allows to get items of attribute _list_2D
        from the exterior."""
        return self._list_2D[index]


    def __setitem__(self, index, val):
        """Special function that allows to set items of attribute _list_2D
        from the exterior."""
        self._list_2D[index] = val
        return


    def _get_list_2D(self):
        """Special function that allows to get the attribute _list_2D from the
        exterior."""
        return self._list_2D
    
    """Definition of a properties for parameter _list_2D. This parameter can
    only be get from the exteriour, not set nor deleted. (items can be
    individually set)."""
    list_2D = property(_get_list_2D)
    
    
    def __add__(self, object_to_add):
        """Special function that allows to merge a class player and level
        into one Level."""
        if not isinstance(object_to_add, Player):
            raise TypeError("unsupported operand type(s) for +: '{}' and 'Level'".format(type(object_to_add).__name__))
        
        level_with_player = Level(self.list_2D)
        player_symbol = symbols['player'] if object_to_add.draw_as_main else symbols['other player']
        level_with_player[object_to_add.lin_coord] = self[object_to_add.lin_coord][:object_to_add.col_coord] + player_symbol + self[object_to_add.lin_coord][object_to_add.col_coord + 1:]
        return level_with_player
        
    
    def __radd__(self, object_to_add):
        """Special function that is the reciprocal of __add__."""
        return self + object_to_add
    
    
    def __sub__(self, object_to_sub):
        """Special function that allows to eliminate a class player from a level."""
        if not isinstance(object_to_sub, Player):
            raise TypeError("unsupported operand type(s) for -: '{}' and 'Level'".format(type(object_to_sub).__name__))
        
        level_without_player = Level(self.list_2D)
        level_without_player[object_to_sub.lin_coord] = self[object_to_sub.lin_coord][:object_to_sub.col_coord] + symbols['empty'] + self[object_to_sub.lin_coord][object_to_sub.col_coord + 1:]
        return level_without_player
    
    def wall(self, case_lin_coord, case_col_coord, direction):
        """Allows to wall a door adjacent to the case of case_lin_coord and case_col_coord
        given as parameters in direction given as parameter.
        Checks if there is a door adjacent to the player in that direction."""        
        if direction == 'n':
            case_lin_coord -= 1
        elif direction == 's':
            case_lin_coord += 1
        elif direction == 'o':
            case_col_coord -= 1
        elif direction == 'e':
            case_col_coord += 1
        
        if self[case_lin_coord][case_col_coord] == symbols['door']:
            self[case_lin_coord] = self[case_lin_coord][:case_col_coord] + symbols['wall'] + self[case_lin_coord][case_col_coord + 1:]
        return
    
    def door(self, case_lin_coord, case_col_coord, direction):
        """Allows to door a wall adjacent to the case of case_lin_coord and case_col_coord
        given as parameters in direction given as parameter.
        Checks if there is a wall adjacent to the player in that direction and that it's
        not an exterior wall."""
        if direction == 'n':
            case_lin_coord -= 1
        elif direction == 's':
            case_lin_coord += 1
        elif direction == 'o':
            case_col_coord -= 1
        elif direction == 'e':
            case_col_coord += 1
        
        if self[case_lin_coord][case_col_coord] == symbols['wall'] and case_lin_coord not in (0, len(self[0])-1) and case_col_coord not in (0, len(self[0])-1):
            self[case_lin_coord] = self[case_lin_coord][:case_col_coord] + symbols['wall'] + self[case_lin_coord][case_col_coord + 1:]
        return