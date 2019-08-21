# -*- coding: utf-8 -*-

"""Module that tests the module user_interface."""

import unittest

import src.client.user_interface as user_interface



class TestUserInterface(unittest.TestCase):
    """Test case used to test functions in module user_interface."""

    def test_string_is_positive_integer_or_empty(self):
        """Test the function user_interface.string_is_positive_integer_or_empty."""
        good_string = ['', '    10', '\t\t10   ']
        bad_string = ['-10', '     -10', '\t\t-10   ', 'a' ]
        
        for string in good_string:
            self.assertTrue(user_interface.string_is_positive_integer_or_empty(string))
        for string in bad_string:
            self.assertFalse(user_interface.string_is_positive_integer_or_empty(string))
            
    def test_interpret_game_action(self):
        """Test the function user_interface.interpret_command."""      
        # Test move commands.
        self.assertEqual({'command': 'n', 'distance': 1}, user_interface.interpret_game_action('n'))
        self.assertEqual({'command': 's', 'distance': 1}, user_interface.interpret_game_action('s'))
        self.assertEqual({'command': 'o', 'distance': 1}, user_interface.interpret_game_action('o'))
        self.assertEqual({'command': 'e', 'distance': 1}, user_interface.interpret_game_action('e'))
        self.assertEqual({'command': 'n', 'distance': 2}, user_interface.interpret_game_action('n2'))
        self.assertEqual({'command': 's', 'distance': 2}, user_interface.interpret_game_action('s    2'))
        self.assertEqual({'command': 'o', 'distance': 2}, user_interface.interpret_game_action('o\t2'))
        
        # Test wall and door commands. 
        self.assertEqual(None, user_interface.interpret_game_action('p'))
        self.assertEqual(None, user_interface.interpret_game_action('m'))
        self.assertEqual({'command': 'p', 'direction': 'n'}, user_interface.interpret_game_action('pn'))
        self.assertEqual({'command': 'p', 'direction': 's'}, user_interface.interpret_game_action('ps'))
        self.assertEqual({'command': 'p', 'direction': 'e'}, user_interface.interpret_game_action('pe'))
        self.assertEqual({'command': 'p', 'direction': 'o'}, user_interface.interpret_game_action('po'))
        self.assertEqual({'command': 'm', 'direction': 'n'}, user_interface.interpret_game_action('mn'))
        self.assertEqual({'command': 'm', 'direction': 's'}, user_interface.interpret_game_action('ms'))
        self.assertEqual({'command': 'm', 'direction': 'e'}, user_interface.interpret_game_action('me'))
        self.assertEqual({'command': 'm', 'direction': 'o'}, user_interface.interpret_game_action('mo'))
        self.assertEqual({'command': 'p', 'direction': 'n'}, user_interface.interpret_game_action('p      n'))
        self.assertEqual({'command': 'm', 'direction': 's'}, user_interface.interpret_game_action('m\ts'))
        
        # Test invalid commands.
        self.assertEqual(None, user_interface.interpret_game_action('a'))
        self.assertEqual(None, user_interface.interpret_game_action('1'))
        self.assertEqual(None, user_interface.interpret_game_action('p1'))
        self.assertEqual(None, user_interface.interpret_game_action('m3'))
        self.assertEqual(None, user_interface.interpret_game_action('na'))
        self.assertEqual(None, user_interface.interpret_game_action('s^'))