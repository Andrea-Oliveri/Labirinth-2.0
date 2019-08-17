# -*- coding: utf-8 -*-

"""Module that contains the class Player."""

from src.graphic import symbols


class Player:
    """Class Player. It contains a line and a column coordinate, which can't be
    deleted nor set. If they are to be modified, move function must be called.
    It also has an attribute draw_as_main that specifies whether it is to
    be drawn as the main player or as another player."""
    
    def __init__(self, lin_coord, col_coord):
        """Constructor of the class Player."""
        self._lin_coord = lin_coord
        self._col_coord = col_coord
        self._draw_as_main = False
    
    
    def move(self, level, direction):
        """Allows to modify the line and column coordinates of the player by 
        changing them by one unit. Checks if the player can move in the new
        position using the level parameter. Returns True if the player moved
        and False otherwise."""
        new_lin_coord = self._lin_coord
        new_col_coord = self._col_coord
        
        if direction == 'n':
            new_lin_coord -= 1
        elif direction == 's':
            new_lin_coord += 1
        elif direction == 'o':
            new_col_coord -= 1
        elif direction == 'e':
            new_col_coord += 1

        if level[new_lin_coord][new_col_coord] in [ symbols['door'], symbols['exit'], symbols['empty'] ]:
            self._lin_coord = new_lin_coord
            self._col_coord = new_col_coord
            return True
        else:
            return False
    
    
    def _get_lin_coord(self):
        """Getter for the parameter _lin_coord."""
        return self._lin_coord
    
    
    def _get_col_coord(self):
        """Getter for the parameter _col_coord."""
        return self._col_coord
    
    
    def _get_draw_as_main(self):
        """Getter for the parameter _draw_as_main."""
        return self._draw_as_main
    
    
    def _set_draw_as_main(self, val):
        """Getter for the parameter _draw_as_main."""
        self._draw_as_main = val
        return
    
    
    """Definition of a properties for each parameter: _lin_coord, _col_coord
    and _draw_as_main. The first two parameters get from the exteriour, not
    set nor deleted. The third one can be get and set, but not deleted."""
    lin_coord = property(_get_lin_coord)
    col_coord = property(_get_col_coord)    
    draw_as_main  = property(_get_draw_as_main, _set_draw_as_main)
