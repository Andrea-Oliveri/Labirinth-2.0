# -*- coding: utf-8 -*-

"""Module ..............................."""

import socket
import select
import os
import sys
from threading import Thread, RLock

from src.communication import port, codons_end, codons
import src.client.user_interface as user_interface
from src.client.user_interface import commands

host_name = 'localhost'


def print_connection_error_and_quit(message):
    """.............................."""
    print(message)
    server_link.close()
    os.system('pause')
    sys.exit()    
            
            
def wait_for_start(commands_list):
    """..........................."""
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
        
        with commands_list_lock:
            for command in commands_list:
                if command == commands['start game']:
                # This could send a second request to the server to start the game
                # (if two clients ask to start almost simultaneously), but it will
                # be up to the server to ignore any following game start requests. 
                    server_link.send(codons['start'].encode())
                elif command == commands['print rules']:
                    user_interface.print_rules()
                elif command == commands['leave']:
                    raise KeyboardInterrupt
            commands_list.clear()


def run_game(commands_list):
    """..........................."""
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
                print(server_message[server_message.index(codons_end)+len(codons_end):])
        
        with commands_list_lock:
            asked_leave = False
            asked_print = False
            game_action = None
            
            for command in commands_list:                   
                if command[0] == commands['leave']:
                    asked_leave = True
                elif command[0] == commands['print rules']:
                    asked_print = True
                else:
                    # When we append the command in the list we already ensure
                    # there is are no duplicates nor  conflicting actioons within
                    # a turn. So there is only one element which is a game action.
                    game_action = command
    
            if asked_leave:
                raise KeyboardInterrupt
            if asked_print:
                user_interface.print_rules()
            if game_action:
                if game_action[0] in command['directions']:
                    server_link.send((codons['move']+game_action[0]).encode())
                    game_action[1] -= 1
                    if game_action[1] == 0:
                        game_action = None
                elif game_action[0] == commands['wall']:
                    server_link.send((codons['wall']+game_action[1]).encode())
                elif game_action[0] == commands['door']:
                    server_link.send((codons['door']+game_action[1]).encode())                
            
            commands_list.clear()
            # In case of a command with multiple moves, we append again the
            # command with a distance decreased by one.
            if game_action:
                commands_list.append(game_action)

    
    
    
    
    
class GetPlayerCommands(Thread):
    """...................."""
    
    def __init__(self, commands_list):
        """................"""
        Thread.__init__(self)
        self.commands_list = commands_list
        self.daemon = True
        self.game_started = False
        
        
    def run(self):
        """........deals with repetition of commands, ignoring repeating commands............"""
        while True:
            command = input().lower().strip()
            with print_lock:
                if not self.game_started:
                    if command not in (commands['start game'], commands['print rules'], commands['leave']):
                        print("Press C to start the game, H for the rules or Q to leave.")
                    elif command not in self.commands_list:
                        with commands_list_lock:
                            self.commands_list.append(command)
                else:
                    command_arg_tuple = user_interface.interpret_command(command)
                    if command_arg_tuple:
                        if command_arg_tuple[0] in (commands['print rules'], commands['leave']) and command_arg_tuple not in self.commands_list:
                            self.commands_list.append(command_arg_tuple)
                        elif not any(command_tuple[0] in tuple(commands['directions'].values()) + (commands['wall'], commands['door']) for command_tuple in commands_list):
                            self.commands_list.append(command_arg_tuple)
                        else:
                            print('You have game actions that are still pending.')
                    else:
                        print("Insert the command (n/s/o/e/m/p/h/q).")
        return
            
        

print("Welcome to Labirinth 2.0")

server_link = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
print("Connecting to server on port:", port)
# We try to connect and we quit if server is not active.
try:
    server_link.connect((host_name, port))
except:
    print_connection_error_and_quit('Server is not active. Connection Failed. Exiting.')

print("Connected to the server on port:", port)

# Declaration of a list of commands that is going to be filled by the thread
# interacting with the player and treated by the main thread.
commands_list = []

# We create a daemon thread that fills commands_list with the commands from the user.
print_lock = RLock()
commands_list_lock = RLock()
thread_get_player_commands = GetPlayerCommands(commands_list)
print("\nPress C to start the game, H for the rules or Q to leave.")
thread_get_player_commands.start()

try:
    wait_for_start(commands_list)
    thread_get_player_commands.game_started = True
    print("Insert the command (n/s/o/e/m/p/h/q).")
    run_game(commands_list)  

except (ConnectionAbortedError, ConnectionResetError):
    # In case of connection with server lost we want to inform the user and quit.
    with print_lock:
        print_connection_error_and_quit('Connection with the Server lost. Exiting.')
except KeyboardInterrupt:
    # In case of a keyboard interrupt, we want to inform the server that a player disconnected.
    server_link.send(codons['player left'].encode())
    server_link.close()