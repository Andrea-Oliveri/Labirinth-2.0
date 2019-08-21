# -*- coding: utf-8 -*-

"""Module that defines some constants for the communication between client and server."""

port = 32000

codons_end = '&'
codons = {'server quit': '000', 'aknowledge': '001',
          'start': '002', 'new player': '003', 'player left': '004',
          'step': '005', 'your turn': '006', 'game end': '007', 
          'move': '008', 'wall': '009', 'door': '010',
          'up': 'n', 'down': 's', 'right': 'e', 'left': 'o'}