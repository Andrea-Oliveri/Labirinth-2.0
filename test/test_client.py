# -*- coding: utf-8 -*-

"""Module that tests the module client."""

import unittest
from unittest.mock import patch
import socket
import threading
import time
import io

import client
import server
from src.communication import port, codons_end, codons



def stub_server_successfull():
    """Function that simulates a server that simply sets up and accepts the connection,
    then sends a confirmation message to the client and quits."""
    # Set up of the connection.
    main_link = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    main_link.bind((server.host_name, port))
    main_link.listen(5)
    
    # Acceptance and sending message to client.
    client_link, link_infos = main_link.accept()    
    client_link.send((codons['aknowledge']+codons_end).encode())
    
    # Closing sockets.
    client_link.close()
    main_link.close()
    
def stub_server_timeout_error():
    """Function that simulates a server that simply sets up and accepts the connection,
    but does not send a confirmation message and quits."""
    # Set up of the connection.
    main_link = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    main_link.bind((server.host_name, port))
    main_link.listen(5)
    
    # Acceptance and waiting.
    client_link, link_infos = main_link.accept()    
    time.sleep(1.)
    
    # Closing sockets.
    client_link.close()
    main_link.close()
    
def stub_server_repeater(message_dict):
    """Function that simulates a server that simply sets up and accepts the connection,
    then receives message and puts it in the variable given as parameter."""
    # Set up of the connection.
    main_link = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    main_link.bind((server.host_name, port))
    main_link.listen(5)
    
    # Acceptance and reception of message.
    client_link, link_infos = main_link.accept()    
    client_link.send((codons['aknowledge']+codons_end).encode())   
    message_dict['message'] = client_link.recv(1024).decode()
    
    # Closing sockets.
    client_link.close()
    main_link.close()



class TestClientConnectToServer(unittest.TestCase):
    """Test case used to test function client.connect_to_server."""
    
    def setUp(self):
        """Set up of the test class."""
        # Creation of a link to connect to server.
        self.server_link = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        
    def tearDown(self):
        """Method called after test each test."""
        # Closing both the server_main_link and the link between client and server.
        self.server_link.close()
    

    def test_connect_to_server_successfull(self):
        """Test of a successfull connection in function client.connect_to_server."""
        thread_server = threading.Thread(target=stub_server_successfull)
        thread_server.start()
        client.connect_to_server(self.server_link)
        thread_server.join()


    def test_connect_to_server_timeout_error(self):
        """Test of the confirmation timeout error in function client.connect_to_server."""
        thread_server = threading.Thread(target=stub_server_timeout_error)
        thread_server.start()
        with self.assertRaises(socket.timeout), patch('socket.socket.recv', side_effect = socket.timeout):
            client.connect_to_server(self.server_link)
        thread_server.join()
           
        
    def test_connect_to_server_ConnectionAbortedError(self):
        """Test of the ConnectionAbortedError in function client.connect_to_server."""
        with self.assertRaises(ConnectionError):
            client.connect_to_server(self.server_link)
           


class TestTreatServerMessage(unittest.TestCase):
    """Test case used to test function client.treat_server_message."""

    def test_treat_server_message(self):
        """Test of function client.treat_server_message."""
        level = "OOOO\nO  O\nOOOO"
        user_commands_stub = {'my turn': False}
        
        with self.assertRaises(ConnectionAbortedError):
            client.treat_server_message(codons['server quit'] + codons_end, user_commands_stub)
        
        with patch('sys.stdout', new_callable=io.StringIO) as mock_output:
            expected_message = "\nGame starts now:\n" + '\n' + level + '\n'
            client.treat_server_message(codons['start'] + codons_end + level, user_commands_stub)
            self.assertEqual(expected_message, mock_output.getvalue())
            
        with patch('sys.stdout', new_callable=io.StringIO) as mock_output:
            expected_message = "\nA new player joined:\n" + '\n' + level + '\n'
            client.treat_server_message(codons['new player'] + codons_end + level, user_commands_stub)
            self.assertEqual(expected_message, mock_output.getvalue())

        with patch('sys.stdout', new_callable=io.StringIO) as mock_output:
            expected_message = "\nA player left:\n" + '\n' + level + '\n'
            client.treat_server_message(codons['player left'] + codons_end + level, user_commands_stub)
            self.assertEqual(expected_message, mock_output.getvalue())
            
        with patch('sys.stdout', new_callable=io.StringIO) as mock_output:
            expected_message = "\nGame updated:\n" + '\n' + level + '\n'
            client.treat_server_message(codons['step'] + codons_end + level, user_commands_stub)
            self.assertEqual(expected_message, mock_output.getvalue())

        with patch('sys.stdout', new_callable=io.StringIO) as mock_output:
            expected_message = "\nIt's your turn:" + '\n'
            client.treat_server_message(codons['your turn'] + codons_end, user_commands_stub)
            self.assertEqual(expected_message, mock_output.getvalue())
            self.assertTrue(user_commands_stub['my turn'])



class TestTreatUserCommands(unittest.TestCase):
    """Test case used to test function client.treat_user_commands."""
    
    def setUp(self):
        """Set up of the test class."""
        # Creation of a link to connect to server.
        self.server_link = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.message_dict = {'message': ''}
        self.thread_server = threading.Thread(target=stub_server_repeater, args=(self.message_dict,))
        
        # Creation of user_commands and game_status dictionary.
        self.user_commands = {'start game': False, 'print rules': False, 'leave': False, 'game action': None, 'my turn': False}
        self.game_status = {'started': False, 'ended': False}


    def tearDown(self):
        """Method called after test each test."""
        # Closing both the server_main_link and the link between client and server.
        self.server_link.close()


    def test_treat_user_commands_print_rules(self):
        """Test of command print rules for client.treat_user_commands."""
        self.user_commands['print rules'] = True
        with patch('src.client.user_interface.print_rules'):
            client.treat_user_commands(self.server_link, self.user_commands, self.game_status)
            self.assertFalse(self.user_commands['print rules'])


    def test_treat_user_commands_quit(self):
        """Test of command quit for client.treat_user_commands."""
        self.user_commands['leave'] = True
        with self.assertRaises(KeyboardInterrupt):
            client.treat_user_commands(self.server_link, self.user_commands, self.game_status)


    def test_treat_user_commands_start(self):
        """Test of command start for client.treat_user_commands."""
        self.user_commands['start game'] = True
        self.thread_server.start()
        client.connect_to_server(self.server_link)
        client.treat_user_commands(self.server_link, self.user_commands, self.game_status)
        self.thread_server.join()
        self.assertEqual(codons['start'], self.message_dict['message'])
        self.assertFalse(self.user_commands['start game'])


    def test_treat_user_commands_move_distance_1(self):
        """Test of command move a distance 1 for client.treat_user_commands."""
        game_action = {'command': 'n', 'distance': 1}
        self.user_commands['game action'] = game_action
        self.user_commands['my turn'] = True
        self.game_status['started'] = True
        self.thread_server.start()
        client.connect_to_server(self.server_link)
        client.treat_user_commands(self.server_link, self.user_commands, self.game_status)
        self.thread_server.join()
        self.assertEqual(codons['move']+game_action['command'], self.message_dict['message'])
        self.assertEqual(None, self.user_commands['game action'])


    def test_treat_user_commands_move_distance_2(self):
        """Test of command move a distance 2 for client.treat_user_commands."""
        game_action = {'command': 'n', 'distance': 2}
        self.user_commands['game action'] = game_action
        self.user_commands['my turn'] = True
        self.game_status['started'] = True
        self.thread_server.start()
        client.connect_to_server(self.server_link)
        client.treat_user_commands(self.server_link, self.user_commands, self.game_status)
        self.thread_server.join()
        self.assertEqual(codons['move']+game_action['command'], self.message_dict['message'])
        self.assertEqual({'command': 'n', 'distance': 1}, self.user_commands['game action'])


    def test_treat_user_commands_wall(self):
        """Test of command wall for client.treat_user_commands."""
        game_action = {'command': 'm', 'direction': 's'}
        self.user_commands['game action'] = game_action
        self.user_commands['my turn'] = True
        self.game_status['started'] = True
        self.thread_server.start()
        client.connect_to_server(self.server_link)
        client.treat_user_commands(self.server_link, self.user_commands, self.game_status)
        self.thread_server.join()
        self.assertEqual(codons['wall']+game_action['direction'], self.message_dict['message'])
        self.assertEqual(None, self.user_commands['game action'])


    def test_treat_user_commands_door(self):
        """Test of command door for client.treat_user_commands."""
        game_action = {'command': 'p', 'direction': 'e'}
        self.user_commands['game action'] = game_action
        self.user_commands['my turn'] = True
        self.game_status['started'] = True
        self.thread_server.start()
        client.connect_to_server(self.server_link)
        client.treat_user_commands(self.server_link, self.user_commands, self.game_status)
        self.thread_server.join()
        self.assertEqual(codons['door']+game_action['direction'], self.message_dict['message'])
        self.assertEqual(None, self.user_commands['game action'])