# PROBLEMS TO FIX: CURRENTLY, PLAYERS ARE WRITTEN ON THE LEVEL. THIS MAKES IT NOT POSSIBLE FOR THEM
# TO MOVE, AS MOVE FUNCTION ONLY CHANGES PLAYERS COORDINATES, DOESN'T REDRAW THEM. THIS ALSO WOULD CAUSES
# DOORS TO DISAPPEAR AFTER A PLAYER PASSED.
# WHEN THIS IS FIXED, WE SHOULD AVOID PLAYERS SPAWNING IN SAME CASE, EACH TIME WE'D HAVE TO REDRAW ALL
# PLAYERS (A SIMPLE FOR LOOP)

# ALSO BUG COMMENT ON LINE 153





# -*- coding: utf-8 -*-

"""Main module for the Server of Labirinth 2.0"""

import socket
import select
import signal
import random
import sys

import src.server.files as files
import src.graphic as graphic
from src.server.player import Player
from src.server.level import Level
from src.communication import port, codons_end, codons

host_name = ''


def keyboard_interrupt(sig, feame):
    """Fonction called by the signal module if the client's window is closed
    via Ctrl+C. If the server is closed, we want to close the connection."""
    tell_clients('server quit', level)
    main_link.close()
    sys.exit()
    
    
def choose_random_empty_case(level):
    """Returns the line index and col index of a randomly chosen empty case
    in parameter level."""
    random_lin = random.randrange(len(level.list_2D))
    while not graphic.symbols['empty'] in level[random_lin]:
        random_lin = random.randrange(len(level.list_2D))
        
    n_empty_cells = level[random_lin].count(graphic.symbols['empty'])
    random_empty_cell = random.randrange(n_empty_cells)
    
    random_col = 0
    for cell in level[random_lin]:
        if cell == graphic.symbols['empty']:
            random_empty_cell -= 1 
        if random_empty_cell < 0:
            break
        random_col += 1
        
    return random_lin, random_col


def tell_clients(codon, level):
    """.............................."""
    if codon == 'server quit':
        print("Server shuts down.")
    elif codon == 'start':
        print("Game started with", len(connected_clients), "players.")
    elif codon == 'new player':
        print("A new player joined: ")
    elif codon == 'player left':
        print("A player disconnected: ")
    elif codon == 'step':
        print("All players moved a step: ")
    
    graphic.draw_all(level)
    
    for client in connected_clients:
        player = players[client]
        player.draw_as_main = True 
        level_with_main_player = level - player + player
        player.draw_as_main = False 
        message = codons[codon] + codons_end + str(level_with_main_player)
        client.send(message.encode())
    return


def player_on_exit(level, player):
    """Tests whether a player is currently on one exit. Returns True if
    it's the case, False otherwise."""
    if level[player.lin_coord][player.col_coord] == graphic.symbols['exit']:
        return True
    return False


def wait_for_players(connected_clients, players, level):
    """Function that periodically tests if there are new clients that want to join
    the game, for each new client spawns a player in the game. It also periodically
    checks if a client wants to talk with the server and if so, we get and treat
    the message (can be either a start request or a player left info). For every
    change, we write a message on the console and inform all connected clients."""
    start_asked = False
    while not start_asked:
        # We test wether there are any clients wanting to connect on the server socket.
        asked_links, wlist, xlist = select.select([main_link], [], [], 0.05)
        
        # For each client that asked to connect, we add their socket to the list
        # and we create a new player for him.
        for link in asked_links:
            client_link, link_infos = link.accept()
            connected_clients.append(client_link)      
            lin, col = choose_random_empty_case(level)
            new_player = Player(lin, col)
            players[client_link] = new_player
            level = level + new_player
            tell_clients('new player', level)
        
        # For each connected client, we check whether they want to be read.
        # The try block is because if connected_clients is empty, an exception is raised.
        try:
            clients_to_read, wlist, xlist = select.select(connected_clients, [], [], 0.05)
        except select.error:
            pass
        else:
            # For each client waiting to be read; we read what he has to say.
            for client in clients_to_read:
                # This line may launch an exception if the message contains
                # special characters. It launches an exception if the client
                # is closed abruptly (in which case we forget him).
                try:
                    message = client.recv(1024).decode()
                except (ConnectionAbortedError, ConnectionResetError):
                    message = codons['player left']
                    
                if message == codons['start']:
                    start_asked = True

                elif message == codons['player left']:
                    level = level - players[client]
                    players.pop(client)
                    connected_clients.remove(client)
                    tell_clients('player left', level)
    tell_clients('start', level)
    return
        

def run_game(connected_clients, players, level):
    """............................"""    
    while not any(player_on_exit(level, player) for player in players.values()):
        if not connected_clients:
            print("All the players left. Game is over.")
            return
        
        #
        #
        #
        # /!\ FOR NOW, PLAYERS MOVE ASYNCHRNOUSLY: EACH PLAYER CAN MOVE INDEPENDENTLY AND THERE ARE NO TURNS.
        # ALSO, INACTIVE CLIENTS SHOULD BE DISCONNECTED IN FUTURE. ALSO, MAIN_LINK SOCKET SHOULD BE CHECKED
        # AND IF NEW CONNECTIONS ARE REQUESTED, A CONNECTION REFUSED COMMAND SHOULD BE SENT. CLIENT WOULD THEN NEED TO INFORM PLAYER.
        #
        #
        #
        
        # We check if any connected client wants to send a command. 
        # The try block is because if connected_clients is empty, an exception is raised.
        try:
            clients_to_read, wlist, xlist = select.select(connected_clients, [], [], 2.)
        except select.error:
            pass
        else:
            # For each client that wants to send a command, we read his command.
            for client in clients_to_read:
                # This line may launch an exception if the message contains
                # special characters. It launches an exception if the client
                # is closed abruptly (in which case we forget him).
                try:
                    message = client.recv(1024).decode()
                except (ConnectionAbortedError, ConnectionResetError):
                    message = codons['player left']
                    
                if codons['player left'] in message:
                    level = level - players[client]
                    players.pop(client)
                    connected_clients.remove(client)
                    
                if codons['move'] in message:
                    players[client].move(level, message[len(codons['move']):])
                    
                if codons['wall'] in message:
                    level.wall(players[client].lin_coord, players[client].col_coord, message[len(codons['wall']):])
                
                if codons['door'] in message:
                    level.door(players[client].lin_coord, players[client].col_coord, message[len(codons['door']):])
                    
        tell_clients('step', level)
    
    
    for client in connected_clients:
        if player_on_exit(level, players[client]):
            client.send(codons['game end']+codons_end+'Congratulations, you won!')
        else:
            client.send(codons['game end']+codons_end+'Sorry, you lost...')
    return


print("Server for Labirinth 2.0")
    
level = Level(files.import_map(files.choose_level()))
graphic.draw_all(level)
    
main_link = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
main_link.bind((host_name, port))
main_link.listen(5)

# In case of a keyboard interrupt, we want to close the socket.
signal.signal(signal.SIGINT, keyboard_interrupt)

print("The server waits for a connection on port:", port)
    
connected_clients = []
players = {}
wait_for_players(connected_clients, players, level)
run_game(connected_clients, players, level)
