# -*- coding: utf-8 -*-

"""Module that defines some constants for the communication between client and server."""

port = 19000

codons_end = '&'
codons = {'server quit': '000', 'start': '001', 'new player': '002', 'player left': '003',
          'game end': '004', 'step': '005', 'move': '006', 'wall': '007', 'door': '008',
          'up': 'n', 'down': 's', 'right': 'e', 'left': 'o'}