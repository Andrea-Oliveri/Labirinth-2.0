# -*- coding: utf-8 -*-

import unittest
import src.client.user_interface as user_interface

"""Module that tests the module user_interface."""


class TestUserInterface(unittest.TestCase):
    """Test case used to test functions in module user_interface."""

    def test_string_is_positive_integer_or_empty(self):
        """Test the function user_interface.string_is_positive_integer_or_empty."""
        good_string = ['', '    10', '\t\t10   ']
        bad_string = ['-10', '     -10', '\t\t-10   ', 'a' ]
        
        for string in good_string:
            assertTrue(user_interface.string_is_positive_integer_or_empty(string))
        for string in bad_string:
            assertFalse(user_interface.string_is_positive_integer_or_empty(string))
            
    def test_interpret_command(self):
        """Test the function user_interface.interpret_command."""      
        good_string = ['', '    10', '\t\t10   ']
        bad_string = ['-10', '     -10', '\t\t-10   ', 'a' ]
        
        for string in good_string:
            assertTrue(user_interface.string_is_positive_integer_or_empty(string))
        for string in bad_string:
            assertFalse(user_interface.string_is_positive_integer_or_empty(string))



def interpret_command(command):
    """Function that interprets the command inserted by the user.
    Returns a tuple with the command and evenctually an argument (depending on
    the command) if reading happened correctly, and returns None otherwise."""
    
    if command == '':
        return None
    
    elif command == commands['print rules'] or command == commands['leave']:
        return (command,)
    
    elif command[0] in commands['directions']:
        if string_is_positive_integer_or_empty(command[1:]):
            distance = 1
            if command[1:]:
                distance = int(command[1:])
            command = command[0]
            return (command, distance)
        
    elif command[0] in (commands['wall'], commands['door']) and command[1:].strip() in commands['directions']:
            direction = command[1:].strip()
            command = command[0]
            return (command, direction)
    
    return None