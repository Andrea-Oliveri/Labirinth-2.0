# -*- coding: utf-8 -*-

"""Module that tests the module level."""

import unittest

import src.server.level as level
import src.server.player as player



class TestLevel(unittest.TestCase):
    """Test case used to test functions in module level."""
    
    def setUp(self):
        """Set up of the test class."""
        self.list_2D = ['OOOOOOOOOO',
                        'O O    O O',
                        'O . OO   O',
                        'O O O    O',
                        'O OOOO O.O',
                        'O O O    U',
                        'O OOOOOO.O',
                        'O O      O',
                        'O O OOOOOO',
                        'O . O    O',
                        'OOOOOOOOOO']
        self.level = level.Level(self.list_2D)
        self.player = player.Player(5, 8)
    
    
    def test_properties(self):
        """Tests the properties of the class Level"""
        # Getter properties test.
        self.assertEqual(self.list_2D, self.level.list_2D)
        # Setter properties test.
        with self.assertRaises(AttributeError):
            self.level.list_2D = []
        # Destructor properties test.
        with self.assertRaises(AttributeError):
            del self.level.list_2D
    
    def test__init__(self):
        """Tests the __init__ method of the class level.Level."""
        original_list_2D = list(self.list_2D)
        self.assertEqual(original_list_2D, self.level.list_2D)
    
    def test__repr__(self):
        """Tests the __repr__ method of the class level.Level."""
        self.assertEqual('\n'.join(self.list_2D), repr(self.level))

    def test__getitem__(self):
        """Tests the __getitem method of the class level.Level."""
        self.assertEqual('O . OO   O', self.level[2])
        self.assertEqual('O O O    U', self.level[5])
        self.assertEqual('U', self.level[5][9])

    def test__setitem__(self):
        """Tests the __setiitem__ method of the class level.Level."""
        self.level[0] = 'OXOOOUOUOO'
        self.assertEqual('OXOOOUOUOO', self.level[0])

    def test__add__(self):
        """Tests the __add__ method of the class level.Level."""
        list_with_player = list(self.list_2D)
        list_with_player[5] = 'O O O   xU'
        level_with_player = level.Level(list_with_player)
        self.assertEqual(level_with_player.list_2D, (self.level + self.player).list_2D)
        with self.assertRaises(TypeError):
            self.level + 2        

    def test__radd__(self):
        """Tests the __radd__ method of the class level.Level."""
        list_with_player = list(self.list_2D)
        list_with_player[5] = 'O O O   xU'
        level_with_player = level.Level(list_with_player)
        self.assertEqual(level_with_player.list_2D, (self.player + self.level).list_2D)
        with self.assertRaises(TypeError):
            2 + self.level 
        
    def test_wall(self):
        """Tests the method wall of the class level.Level."""        
        # Wall of a door.
        self.level.wall(5, 8, 'n')
        self.assertEqual('O', self.level[4][8])
        
        # Wall of an empty case.
        self.level.wall(5, 8, 'o')
        self.assertEqual(' ', self.level[5][7])
        
        # Wall of the exit.
        self.level.wall(5, 8, 'e')
        self.assertEqual('U', self.level[5][9])
        
        # Wall of a wall.
        self.level.wall(5, 7, 'n')
        self.assertEqual('O', self.level[4][7])
        
        
    def test_door(self):
        """Tests the method door of the class level.Level."""
        # Door of an internal wall.
        self.level.door(5, 7, 'n')
        self.assertEqual('.', self.level[4][7])
        
        # Door of a border wall.
        self.level.door(1, 1, 'n')
        self.assertEqual('O', self.level[0][1])
        
        # Door of an empty case.
        self.level.door(5, 8, 'o')
        self.assertEqual(' ', self.level[5][7])
        
        # Door of an exit.
        self.level.door(5, 8, 'e')
        self.assertEqual('U', self.level[5][9])
        
        # Door of a door.
        self.level.door(5, 8, 'n')
        self.assertEqual('.', self.level[4][8])