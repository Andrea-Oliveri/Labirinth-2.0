# -*- coding: utf-8 -*-

"""Main module for the Server of Labirinth 2.0"""

import socket
import select
import random
import os
import time

import src.server.files as files
import src.graphic as graphic
from src.server.player import Player
from src.server.level import Level
from src.communication import port, codons_end, codons

host_name = ''


    

def add_players_to_level(level, players):
    """Function that takes as parameter a level and a dictionaire with players
    as values and returns the level with the players inserted in it."""
    level_with_players = Level(level.list_2D)
    for player in players.values():
        level_with_players = level_with_players + player
    return level_with_players
    
    
def choose_random_empty_case(level_with_players):
    """Returns the line index and col index of a randomly chosen empty case
    in parameter level_with_players."""
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


def tell_clients(codon, level, players):
    """Function that prints a short message on the server screen to inform about
    a change in status and also informs all the clients about it. For both the clients
    and the server, the level is redrawn."""
    if codon == 'server quit':
        print("Server shuts down.")
    elif codon == 'start':
        print("Game started with", len(connected_clients), "players.")
    elif codon == 'new player':
        print("A new player joined: ")
    elif codon == 'player left':
        print("A player disconnected: ")
    elif codon == 'step':
        print("A player moved a step: ")
    
    graphic.draw_all(add_players_to_level(level, players))
    
    for client in connected_clients:
        player = players[client]
        player.draw_as_main = True 
        message = codons[codon] + codons_end + str(add_players_to_level(level, players))
        # The try block here is in case a player disconnected abruptly. For now
        # we don't do anything. The treatement will happen during this player's turn.
        try:
            client.send(message.encode())
        except ConnectionError:
            pass
        player.draw_as_main = False 
    
    # Prevents two messages sent from server from overlapping: client might read them as one.
    time.sleep(0.25)
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
        
        # For each client that asked to connect, we add their socket to the list,
        # we send a confirmation message, we create a new player for him and we
        # inform all clients.
        for link in asked_links:
            client_link, link_infos = link.accept()
            confirmation_message = codons['aknowledge'] + codons_end
            client_link.send(confirmation_message.encode())
            connected_clients.append(client_link)
            lin, col = choose_random_empty_case(add_players_to_level(level, players))
            new_player = Player(lin, col)
            players[client_link] = new_player
            tell_clients('new player', level, players)
        
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
                except ConnectionError:
                    message = codons['player left']
                    
                if message == codons['start']:
                    start_asked = True

                elif message == codons['player left']:
                    players.pop(client)
                    connected_clients.remove(client)
                    tell_clients('player left', level, players)
                    
    tell_clients('start', level, players)
    return
        

def run_game(connected_clients, players, level):
    """Function that, as long as no player is on the exit and there are still players
    connected for each player sends a message asking for the move and then waits a max
    number of seconds for the answer, after which the player is eliminated. If the player
    left abruptly, we forget him. If a new player tries to connect, we don't do anything:
    the absence of the confirmation message will make the client understand that the
    connection failed."""    
    
    # We put a timeout to the sockets after which we consider the client as disconnected.
    for client in connected_clients:
        client.settimeout(30.)

    while not any(player_on_exit(level, player) for player in players.values()):
        if not connected_clients:
            print("All the players left. Game is over.")
            return
        
        for client in connected_clients:
            # These lines may launch an exception if the message contains
            # special characters. It launches an exception if the client
            # is closed abruptly (in which case we forget him). It also
            # launches an exception if the client does not respond within
            # the timeout.
            try:
                your_turn_message = codons['your turn'] + codons_end
                client.send(your_turn_message.encode())
                message = client.recv(1024).decode()
            except ConnectionError:
                message = codons['player left']
            # If the player was disconnected due to inactivity, we try to tell
            # the client he has been disconnected. If we can't for any reason, 
            # we don't worry anymore. 
            except socket.timeout:
                message = codons['player left']
                try:
                    disconnected_message = codons['server quit'] + codons_end
                    client.send(disconnected_message.encode())
                except:
                    pass
        
            if codons['player left'] in message:
                players.pop(client)
                connected_clients.remove(client)
                client.close()
                tell_clients('player left', level, players)
                
            if codons['move'] in message:
                players[client].move(level, message[len(codons['move']):])
                tell_clients('step', level, players)
                
            if codons['wall'] in message:
                level.wall(players[client].lin_coord, players[client].col_coord, message[len(codons['wall']):])
                tell_clients('step', level, players)
                
            if codons['door'] in message:
                level.door(players[client].lin_coord, players[client].col_coord, message[len(codons['door']):])
                tell_clients('step', level, players)
                
    # Once the game is over, we inform the clients and also send a string to
    # tell the players if they won or not.
    for client in connected_clients:
        message= ''
        if player_on_exit(level, players[client]):
            message = codons['game end']+codons_end+'Congratulations, you won!'
        else:
            message = codons['game end']+codons_end+'Sorry, you lost...'
        client.send(message.encode())
        
    print("A player left the labirinth. Game is over.")
    return

if __name__ == "__main__":
    print("Server for Labirinth 2.0")
        
    # Choice of the labirinth to play.
    level = Level(files.import_map(files.choose_level()))
    graphic.draw_all(level)
        
    # Set up of the socket connection.
    main_link = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    main_link.bind((host_name, port))
    main_link.listen(5)
    
    print("The server waits for a connection on port:", port)
        
    try:
        connected_clients = []
        players = {}
        wait_for_players(connected_clients, players, level)
        run_game(connected_clients, players, level)
        main_link.close()
        os.system('pause')
        
    except KeyboardInterrupt:
        # In case of a keyboard interrupt, we want to close the socket.
        tell_clients('server quit', level, players)
        main_link.close()
