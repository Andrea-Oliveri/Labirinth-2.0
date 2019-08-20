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
        self.assertEqual(user_interface.interpret_game_action('n'), {'command': 'n', 'distance': 1})
        self.assertEqual(user_interface.interpret_game_action('s'), {'command': 's', 'distance': 1})
        self.assertEqual(user_interface.interpret_game_action('o'), {'command': 'o', 'distance': 1})
        self.assertEqual(user_interface.interpret_game_action('e'), {'command': 'e', 'distance': 1})
        self.assertEqual(user_interface.interpret_game_action('n2'), {'command': 'n', 'distance': 2})
        self.assertEqual(user_interface.interpret_game_action('s    2'), {'command': 's', 'distance': 2})
        self.assertEqual(user_interface.interpret_game_action('o\t2'), {'command': 'o', 'distance': 2})
        
        # Test wall and door commands. 
        self.assertEqual(user_interface.interpret_game_action('p'), None)
        self.assertEqual(user_interface.interpret_game_action('m'), None)
        self.assertEqual(user_interface.interpret_game_action('pn'), {'command': 'p', 'direction': 'n'})
        self.assertEqual(user_interface.interpret_game_action('ps'), {'command': 'p', 'direction': 's'})
        self.assertEqual(user_interface.interpret_game_action('pe'), {'command': 'p', 'direction': 'e'})
        self.assertEqual(user_interface.interpret_game_action('po'), {'command': 'p', 'direction': 'o'})
        self.assertEqual(user_interface.interpret_game_action('mn'), {'command': 'm', 'direction': 'n'})
        self.assertEqual(user_interface.interpret_game_action('ms'), {'command': 'm', 'direction': 's'})
        self.assertEqual(user_interface.interpret_game_action('me'), {'command': 'm', 'direction': 'e'})
        self.assertEqual(user_interface.interpret_game_action('mo'), {'command': 'm', 'direction': 'o'})
        self.assertEqual(user_interface.interpret_game_action('p      n'), {'command': 'p', 'direction': 'n'})
        self.assertEqual(user_interface.interpret_game_action('m\ts'), {'command': 'm', 'direction': 's'})
        
        # Test invalid commands.
        self.assertEqual(user_interface.interpret_game_action('a'), None)
        self.assertEqual(user_interface.interpret_game_action('1'), None)
        self.assertEqual(user_interface.interpret_game_action('p1'), None)
        self.assertEqual(user_interface.interpret_game_action('m3'), None)
        self.assertEqual(user_interface.interpret_game_action('na'), None)
        self.assertEqual(user_interface.interpret_game_action('s^'), None)