# -*- coding: utf-8 -*-

"""Main module for the Client of Labirinth 2.0"""

import socket
import select
import sys
from threading import Thread, RLock

from src.communication import port, codons_end, codons
import src.client.user_interface as user_interface
from src.client.user_interface import commands

host_name = 'localhost'


def print_connection_error_and_quit(message):
    """Function called in case of a connection error (connection can't be 
    established or is lost). Prints the message passed as parameter, closes
    the socket and terminates execution"""
    print(message)
    server_link.close()
    sys.exit()    
            
            
def wait_for_start(user_commands):
    """Function that periodically checks if there are new messages from the
    server and treats the commands by the user. Returns only once the server
    sent the start codon."""
    server_message = ''
    while codons['start'] not in server_message:
        read_server, wlist, xlist = select.select([server_link], [], [], 0.05)
        if read_server:
            server_message = server_link.recv(1024).decode()
            with print_lock:
                if codons['server quit'] in server_message:
                    raise ConnectionAbortedError
                elif codons['start'] in server_message:
                    print("\nGame starts now: \n")
                elif codons['new player'] in server_message:
                    print("\nA new player joined: \n")
                elif codons['player left'] in server_message:
                    print("\nA player left: \n")
                print(server_message[server_message.index(codons_end)+len(codons_end):])
        
        with user_commands_lock:
            if user_commands['start game']:
                # This could send a second request to the server to start the game
                # (if two clients ask to start almost simultaneously), but it will
                # be up to the server to ignore any following game start requests. 
                server_link.send(codons['start'].encode())
                user_commands['start game'] = False
            if user_commands['print rules']:
                user_interface.print_rules()
                user_commands['print rules'] = False
            if user_commands['leave']:
                raise KeyboardInterrupt


def run_game(user_commands):
    """Function that periodically checks if there are new messages from the
    server and treats the commands by the user. For the commands involving a
    game action, it first waits until the server asks for the command, then prints
    a message asking the player for the command and then sends it. Returns only 
    once the server sent the game end codon."""
    server_message = ''
    while codons['game end'] not in server_message:
        read_server, wlist, xlist = select.select([server_link], [], [], 0.05)
        if read_server:
            server_message = server_link.recv(1024).decode()
            with print_lock:
                if codons['server quit'] in server_message:
                    raise ConnectionAbortedError
                elif codons['player left'] in server_message:
                    print("\nA player left: \n")
                elif codons['step'] in server_message:
                    print("\nGame updated: \n")
                elif codons['your turn'] in server_message:
                    user_commands['my turn'] = True
                    print("\nIt's your turn: ", end='')
                print(server_message[server_message.index(codons_end)+len(codons_end):])
                
        with user_commands_lock:
            if user_commands['print rules']:
                user_interface.print_rules()
                user_commands['print rules'] = False
            if user_commands['leave']:
                raise KeyboardInterrupt
            # We check that it's our turn and that the player actually moved.
            # If it's a move command, we first send it and then decrease the distance
            # we still have to move. If the remaining distance is zero, the command
            # is deleted. Otherwise the new distance is memorised. If it's a wall or door
            # command, it is sent and forgot anyways.
            if user_commands['game action'] and user_commands['my turn']:
                if user_commands['game action']['command'] in commands['directions']:
                    server_link.send((codons['move']+user_commands['game action']['command']).encode())
                    user_commands['game action']['distance'] -= 1
                    if user_commands['game action']['distance'] == 0:
                        user_commands['game action'] = None
                elif user_commands['game action']['command'] == commands['wall']:
                    server_link.send((codons['wall']+user_commands['game action']['direction']).encode())
                    user_commands['game action'] = None
                elif user_commands['game action']['command'] == commands['door']:
                    server_link.send((codons['door']+user_commands['game action']['direction']).encode())
                    user_commands['game action'] = None
                user_commands['my turn'] = False
    
    
    
class GetPlayerCommands(Thread):
    """Thread that takes all user inputs and modifies user_commands accordingly."""
    
    def __init__(self, user_commands):
        """Constructor of class GetPlayerCommands."""
        Thread.__init__(self)
        self.user_commands = user_commands
        self.game_started = False
        self.game_ended = False
        
        
    def run(self):
        """Run method of the thread. Modifies user_commands accordingly to the
        user input. All possible repetitions or command conflicts are dealt with
        here before changing user_commands."""
        while True:
            command = input().lower().strip()
            if self.game_ended:
                return
            with print_lock, user_commands_lock:
                # No matter if the game started or not, no matter if it's our
                # turn, we accept the 'print rules' and 'leave' commands.
                if command == commands['print rules']:
                    self.user_commands['print rules'] = True
                elif command == commands['leave']:
                    self.user_commands['leave'] = True
                else:
                    # Only if the game did not start, we accept the 'start game' command.
                    if not self.game_started: 
                        if command == commands['start game']:
                            self.user_commands['start game'] = True
                        else:
                            # Invalid command inserted.
                            print("Press C to start the game, H for the rules or Q to leave.")
                    # Only if the game started, it's our turn and no previous commands are
                    # still pending we accept 'game action' command.
                    else:
                        if user_commands['my turn']:
                            if not self.user_commands['game action']:
                                game_action = user_interface.interpret_game_action(command)
                                if game_action:
                                    self.user_commands['game action'] = game_action
                                else:
                                    # Invalid command inserted.
                                    print("Insert the command (n/s/o/e/m/p/h/q).")
                            else:
                                print('You have game actions that are still pending.')
                        else:
                            print("It's not your turn to move yet.")
        

print("Welcome to Labirinth 2.0")

server_link = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

print("Connecting to server on port:", port)
# We try to connect and we quit if server is not active or does not respnd within
# 3 seconds (game already started).
try:
    server_link.connect((host_name, port))
    server_link.settimeout(3.)
    confirmation_message = server_link.recv(1024).decode()
    server_link.settimeout(None)
    if codons['aknowledge'] not in confirmation_message:
        raise ConnectionAbortedError    
except:
    print_connection_error_and_quit('Server is not active or a game is already running. Connection Failed. Exiting.')

print("Connected to the server on port:", port)

# Declaration of a dictionary of commands that is going to be filled by the thread
# interacting with the player and treated by the main thread.
user_commands = {'start game': False, 'print rules': False, 'leave': False, 'game action': None, 'my turn': False}

# We create a daemon thread that fills user_commands with the commands from the user.
print_lock = RLock()
user_commands_lock = RLock()
thread_get_player_commands = GetPlayerCommands(user_commands)
print("\nPress C to start the game, H for the rules or Q to leave.")
thread_get_player_commands.start()

try:
    wait_for_start(user_commands)
    thread_get_player_commands.game_started = True
    print("Insert the command (n/s/o/e/m/p/h/q).")
    run_game(user_commands)
    thread_get_player_commands.game_ended = True

except (ConnectionAbortedError, ConnectionResetError):
    # In case of connection with server lost we want to inform the user and quit.
    thread_get_player_commands.game_ended = True
    with print_lock:
        print_connection_error_and_quit('Connection with the Server lost. Exiting.')
except KeyboardInterrupt:
    # In case of a keyboard interrupt, we want to inform the server that a player disconnected.
    thread_get_player_commands.game_ended = True
    server_link.send(codons['player left'].encode())
    server_link.close()