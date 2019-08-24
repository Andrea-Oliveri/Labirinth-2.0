# -*- coding: utf-8 -*-

"""Module that tests the module server."""

import unittest
from unittest.mock import patch
import socket
import threading

import server
import client
from src.communication import port, codons_end, codons
import src.server.player as player
import src.server.level as level
from src.graphic import symbols

    

def stub_client_empty():
    """Function that simulates a client that simply requests a connection
    (expects a confirmation message to consider connection successfull) and quits."""
    server_link = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect_to_server(server_link)   
    server_link.close()
    
def stub_client_receive_message(messages_list):
    """Function that simulates a client that simply requests a connection
    (expects a confirmation message to consider connection successfull) and
    then waits for message that it appends to messages_list and quits."""
    server_link = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect_to_server(server_link)    
    messages_list.append(server_link.recv(1024).decode())
    server_link.close()
    


class TestPlayerLevelInteraction(unittest.TestCase):
    """Test case used to test function server.add_players_to_level,
    server.choose_random_empty_case and server.player_on_exit."""
    
    def setUp(self):
        """Set up of the test class."""
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
        
        # Creation of a dictionary with unimportant keys and player instances as values.
        self.players = {0: player.Player(1,1), 1: player.Player(3,1), 2: player.Player(3,6), 3: player.Player(9,6), 4: player.Player(7,6)}
        

    def test_add_players_to_level(self):
        """Test of function server.add_players_to_level."""
        # Test add_players_to_level with no players drawn as main.
        level_with_players = server.add_players_to_level(self.level, self.players)
        self.assertEqual(['OOOOOOOOOO',
                          'OxO    O O',
                          'O . OO   O',
                          'OxO O x  O',
                          'O OOOO O.O',
                          'O O O    U',
                          'O OOOOOO.O',
                          'O O   x  O',
                          'O O OOOOOO',
                          'O . O x  O',
                          'OOOOOOOOOO'], level_with_players.list_2D)
    
        # Test add_players_to_level with one player drawn as main.
        self.players[0].draw_as_main = True
        level_with_players = server.add_players_to_level(self.level, self.players)
        self.assertEqual(['OOOOOOOOOO',
                          'OXO    O O',
                          'O . OO   O',
                          'OxO O x  O',
                          'O OOOO O.O',
                          'O O O    U',
                          'O OOOOOO.O',
                          'O O   x  O',
                          'O O OOOOOO',
                          'O . O x  O',
                          'OOOOOOOOOO'], level_with_players.list_2D)

    
    def test_choose_random_empty_case(self):
        """Test of function server.choose_random_empty_case."""
        level_with_players = server.add_players_to_level(self.level, self.players)
        for _ in range(10):
            lin, col = server.choose_random_empty_case(level_with_players)
            self.assertEqual(symbols['empty'], level_with_players[lin][col])


    def test_player_on_exit(self):
        """Test of function server.player_on_exit."""
        for player_not_on_exit in self.players.values():
            self.assertFalse(server.player_on_exit(self.level, player_not_on_exit))
            
        player_on_exit = player.Player(5,9)
        self.assertTrue(server.player_on_exit(self.level, player_on_exit))



class TestAcceptClient(unittest.TestCase):
    """Test case used to test function server.accept_client."""
        
    def setUp(self):
        """Set up of the test class."""
        # Creation of the parameters passed to server.accept_client.
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
        self.connected_clients = []
        self.players = {}
        
        # Set up of the socket connection.
        self.main_link = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.main_link.bind((server.host_name, port))
        self.main_link.listen(5)
        
        # Creation of 1 stub clients.
        self.thread_client = threading.Thread(target = stub_client_empty)
        self.thread_client.start()    
    
    def tearDown(self):
        """Method called after test each test."""
        # Closing the links with clients and the main_link.
        for client_link in self.connected_clients:
            client_link.close()
        self.main_link.close()      
        
    def test_accept_client(self):
        """Test of function server.accept_client."""
        server.accept_client(self.main_link, self.connected_clients, self.level, self.players)
        self.assertTrue(self.connected_clients)
        self.assertTrue(self.players)
        self.thread_client.join()



class TestTellClients(unittest.TestCase):
    """Test case used to test function server.tell_clients."""
    
    def setUp(self):
        """Set up of the test class."""
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
    
        # Set up of the socket connection.
        self.main_link = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.main_link.bind((server.host_name, port))
        self.main_link.listen(5)
        
        # Creation and connection to n_stub_clients stub clients.
        self.n_stub_clients = 3
        self.threads_stub_clients = []
        self.connected_clients = []
        self.players = {}
        self.messages_list = []
        for _ in range(self.n_stub_clients):
            thread_client = threading.Thread(target = stub_client_receive_message, args = (self.messages_list,))
            self.threads_stub_clients.append(thread_client)
            thread_client.start()
            server.accept_client(self.main_link, self.connected_clients, self.level, self.players)
        
        # Patching time.sleep to run tests faster and print in tell_clients.
        self.time_patch = patch('time.sleep')
        self.time_patch.start()
        self.print_patch = patch('builtins.print')
        self.print_patch.start()
    
    
    def tearDown(self):
        """Method called after test each test."""
        # Closing the links with clients and the main_link.
        for client_link in self.connected_clients:
            client_link.close()
        self.main_link.close()      
        
        # Stopping patching time.sleep and print in tell_clients.
        self.time_patch.stop()
        self.print_patch.stop()

    
    def test_tell_clients_each_received_message(self):
        """Test that each client receives a message and the message contains the
        correct codon and codon_end for server.tell_clients."""
        server.tell_clients('server quit', self.connected_clients, self.level, self.players)
        for thread_client in self.threads_stub_clients:
            thread_client.join()
        
        for message in self.messages_list:
            self.assertIn(codons['server quit'] + codons_end, message)
               
            
    def test_tell_clients_deconnected_client(self):
        """Test that no error is produced when a client quits abruptly the
        connection for server.tell_clients."""
        server.tell_clients('server quit', self.connected_clients, self.level, self.players)
        server.tell_clients('start', self.connected_clients, self.level, self.players)