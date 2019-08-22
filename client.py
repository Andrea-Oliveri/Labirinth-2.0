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



def connect_to_server(server_link):
    """Function that tries to connect to the server. If the link is not opened
    (server is not active) or the server does not respond with a confirmation
    message withing one second (the server is already running a game) we print
    an informative message on screen and terminate execution."""
    server_link.connect((host_name, port))
    server_link.settimeout(1.)
    confirmation_message = server_link.recv(1024).decode()
    server_link.settimeout(None)
    if codons['aknowledge'] not in confirmation_message:
        raise ConnectionAbortedError    
    return


def print_connection_error_and_quit(message):
    """Function called in case of a connection error (connection can't be 
    established or is lost). Prints the message passed as parameter, closes
    the socket and terminates execution"""
    print(message)
    server_link.close()
    sys.exit()    
            
            
def treat_server_message(server_message, user_commands):
    """Function that treats the server message passed as parameter."""
    if codons['server quit'] in server_message:
        raise ConnectionAbortedError
    elif codons['start'] in server_message:
        print("\nGame starts now:\n")
    elif codons['new player'] in server_message:
        print("\nA new player joined:\n")
    elif codons['player left'] in server_message:
        print("\nA player left:\n")
    elif codons['step'] in server_message:
        print("\nGame updated:\n")
    elif codons['your turn'] in server_message:
        user_commands['my turn'] = True
        print("\nIt's your turn:", end='')
    print(server_message[server_message.index(codons_end)+len(codons_end):])


def treat_user_commands(server_link, user_commands, game_status):
    """Function that treats the user commands."""   
    if user_commands['print rules']:
        user_interface.print_rules()
        user_commands['print rules'] = False
    if user_commands['leave']:
        raise KeyboardInterrupt
        
    if not game_status['started']:
        # This could send a second request to the server to start the game
        # (if two clients ask to start almost simultaneously), but it will
        # be up to the server to ignore any following game start requests. 
        if user_commands['start game']:
            server_link.send(codons['start'].encode())
            user_commands['start game'] = False
    else:
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
    

def wait_for_codon_from_server(codon, user_commands, game_status):
    """Function that periodically checks if there are new messages from the
    server and treats the commands by the user. Returns only once the server
    sent the codon with key passed as parameter."""
    server_message = ''
    while codons[codon] not in server_message:
        read_server, wlist, xlist = select.select([server_link], [], [], 0.05)
        if read_server:
            server_message = server_link.recv(1024).decode()
            with thread_lock:
                treat_server_message(server_message, user_commands)
        
        with thread_lock:
            treat_user_commands(server_link, user_commands, game_status)


class GetPlayerCommands(Thread):
    """Thread that takes all user inputs and modifies user_commands accordingly."""
    
    def __init__(self, user_commands, game_status):
        """Constructor of class GetPlayerCommands."""
        Thread.__init__(self)
        self.user_commands = user_commands
        self.game_status = game_status
    
    def run(self):
        """Run method of the thread."""
        while True:
            command = input().lower().strip()
            if self.game_status['ended']:
                return
            with thread_lock:
                user_interface.interpret_user_command(command, self.user_commands, self.game_status)
        
        
        
if __name__ == "__main__":
    print("Welcome to Labirinth 2.0")
    
    server_link = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print("Connecting to server on port:", port)
    try:
        connect_to_server(server_link)
    except (ConnectionError, socket.timeout):
        print_connection_error_and_quit('Server is not active or a game is already running. Connection Failed. Exiting.')
    print("Connected to the server on port:", port)
    
    # Declaration of two booleans in a dictionary that will define the status of the game.
    game_status = {'started': False, 'ended': False}
    
    # Declaration of a dictionary of commands that is going to be filled by the thread
    # interacting with the player and treated by the main thread.
    user_commands = {'start game': False, 'print rules': False, 'leave': False, 'game action': None, 'my turn': False}
    
    # We create a daemon thread that fills user_commands with the commands from the user.
    # We also create a lock to prevent simultaneous access to print and user_commands.
    thread_lock = RLock()
    thread_get_player_commands = GetPlayerCommands(user_commands, game_status)
    print("\nPress C to start the game, H for the rules or Q to leave.")
    thread_get_player_commands.start()
    
    try:
        wait_for_codon_from_server('start', user_commands, game_status)
        game_status['started'] = True
        print("Available commands: n/s/o/e/m/p/h/q.")
        wait_for_codon_from_server('game end', user_commands, game_status)
        game_status['ended'] = True
    
    except ConnectionError:
        # In case of connection with server lost we want to inform the user and quit.
        game_status['ended'] = True
        with thread_lock:
            print_connection_error_and_quit('Connection with the Server lost. Exiting.')
    except KeyboardInterrupt:
        # In case of a keyboard interrupt, we want to inform the server that a player disconnected.
        game_status['ended'] = True
        server_link.send(codons['player left'].encode())
        server_link.close()