# -*- coding: utf-8 -*-

"""Module that tests the module player."""


import unittest

import src.server.player as player
import src.server.level as level



class TestPlayer(unittest.TestCase):
    """Test case used to test functions in module player."""

    def setUp(self):
        """Set up of the test class."""
        # We choose an init_lin_coord and init_col_coord that allow testing moves
        # in all directions without encountering doors nor walls not exits.
        self.init_lin_coord = 3
        self.init_col_coord = 8
        self.player = player.Player(self.init_lin_coord, self.init_col_coord)
        self.level = level.Level(['OOOOOOOOOO',
                                  'O O    O O',
                                  'O . OO   O',
                                  'O O O    O',
                                  'O OOOO O.O',
                                  'O O O    U',
                                  'O OOOOOO.O',
                                  'O O      O',
                                  'O O OOOOOO',
                                  'O . O    O',
                                  'OOOOOOOOOO'])
    
    def test_properties(self):
        """Test the properties of the class player."""
        # Getter properties test.
        self.assertEqual(self.init_lin_coord, self.player.lin_coord)
        self.assertEqual(self.init_col_coord, self.player.col_coord)
        self.assertFalse(self.player.draw_as_main)
        
        # Setter properties test.
        with self.assertRaises(AttributeError):
            self.player.lin_coord = 5
        with self.assertRaises(AttributeError):
            self.player.col_coord = 5
        self.player.draw_as_main = True
        self.assertTrue(self.player.draw_as_main)
        
        # Destructor properties test.
        with self.assertRaises(AttributeError):
            del self.player.lin_coord
        with self.assertRaises(AttributeError):
            del self.player.col_coord
        with self.assertRaises(AttributeError):
            del self.player.draw_as_main
            
    def test_move(self):
        """Tests the functioning of the method move."""
        # Tests of moving directions.
        self.player.move(self.level, 'n')
        self.assertEqual(self.init_lin_coord-1, self.player.lin_coord) 
        self.assertEqual(self.init_col_coord, self.player.col_coord)
        self.player.move(self.level, 's')
        self.assertEqual(self.init_lin_coord, self.player.lin_coord) 
        self.assertEqual(self.init_col_coord, self.player.col_coord)
        self.player.move(self.level, 'o')
        self.assertEqual(self.init_lin_coord, self.player.lin_coord) 
        self.assertEqual(self.init_col_coord-1, self.player.col_coord)
        self.player.move(self.level, 'e')
        self.assertEqual(self.init_lin_coord, self.player.lin_coord) 
        self.assertEqual(self.init_col_coord, self.player.col_coord)

        # Test of moving on door.
        self.player.move(self.level, 's')
        self.assertEqual(self.init_lin_coord+1, self.player.lin_coord) 
        self.assertEqual(self.init_col_coord, self.player.col_coord)
        
        # Test of blocking on wall.
        self.player.move(self.level, 'o')
        self.assertEqual(self.init_lin_coord+1, self.player.lin_coord) 
        self.assertEqual(self.init_col_coord, self.player.col_coord)
        
        # Test of moving on exit.
        self.player.move(self.level, 's')
        self.player.move(self.level, 'e')
        self.assertEqual(self.init_lin_coord+2, self.player.lin_coord) 
        self.assertEqual(self.init_col_coord+1, self.player.col_coord)