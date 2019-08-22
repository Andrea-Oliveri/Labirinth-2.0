# -*- coding: utf-8 -*-

"""Module that tests the module user_interface."""

import unittest
from unittest.mock import patch
import io

import src.client.user_interface as user_interface



class TestUserInterfaceInterpretGameAction(unittest.TestCase):
    """Test case used to test functions user_interface.string_is_positive_integer_or_empty and user_interface.interpret_game_action."""

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
        
        
        
class TestUserInterfaceInterpretUserCommand(unittest.TestCase):
    """Test case used to test functions user_interface.interpret_user_command."""
        
    def setUp(self):
        """Set up of the test class."""
        # Creation of user_commands and game_status dictionary.
        self.user_commands = {'start game': False, 'print rules': False, 'leave': False, 'game action': None, 'my turn': False}
        self.game_status = {'started': False, 'ended': False}


    def test_get_player_commands_print_rules(self):
        """Test of command print rules for client.GetPlayerCommands"""
        user_interface.interpret_user_command('h', self.user_commands, self.game_status)
        self.assertTrue(self.user_commands['print rules'])


    def test_get_player_commands_leave(self):
        """Test of command leave for client.GetPlayerCommands"""
        user_interface.interpret_user_command('q', self.user_commands, self.game_status)
        self.assertTrue(self.user_commands['leave'])


    def test_get_player_commands_start_game(self):
        """Test of command start game for client.GetPlayerCommands"""
        user_interface.interpret_user_command('c', self.user_commands, self.game_status)
        self.assertTrue(self.user_commands['start game'])
         
        
    def test_get_player_game_action(self):
        """Test of game action command when game started and player's turn and no game action pending for client.GetPlayerCommands"""
        self.game_status['started'] = True
        self.user_commands['my turn'] = True
        user_interface.interpret_user_command('pe', self.user_commands, self.game_status)

        
    def test_get_player_commands_invalid_1(self):
        """Test of invalid command when game not started for client.GetPlayerCommands"""
        with patch('sys.stdout', new_callable=io.StringIO) as mock_output:
            user_interface.interpret_user_command('n', self.user_commands, self.game_status)
            self.assertEqual("Press C to start the game, H for the rules or Q to leave.\n", mock_output.getvalue())
    
    
    def test_get_player_commands_invalid_2(self):
        """Test of invalid command not your turn for client.GetPlayerCommands"""
        self.game_status['started'] = True
        with patch('sys.stdout', new_callable=io.StringIO) as mock_output:
            user_interface.interpret_user_command('n', self.user_commands, self.game_status)
            self.assertEqual("It's not your turn to move yet.\n", mock_output.getvalue())
    
    
    def test_get_player_commands_invalid_3(self):
        """Test of invalid command not your turn for client.GetPlayerCommands"""
        self.game_status['started'] = True
        self.user_commands['my turn'] = True
        self.user_commands['game action'] = {'command': 'n', 'distance': 2}
        with patch('sys.stdout', new_callable=io.StringIO) as mock_output:
            user_interface.interpret_user_command('n', self.user_commands, self.game_status)
            self.assertEqual("You have game actions that are still pending.\n", mock_output.getvalue())


    def test_get_player_commands_invalid_4(self):
        """Test of invalid command when game started and player's turn and no game action pending for client.GetPlayerCommands"""
        self.game_status['started'] = True
        self.user_commands['my turn'] = True
        with patch('sys.stdout', new_callable=io.StringIO) as mock_output:
            user_interface.interpret_user_command('dsada', self.user_commands, self.game_status)
            self.assertEqual("Available commands: n/s/o/e/m/p/h/q.\n", mock_output.getvalue())
