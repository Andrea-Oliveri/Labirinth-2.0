# -*- coding: utf-8 -*-

"""Module that defines some constants for the communication between client and server."""

port = 25000

codons_end = '&'
codons = {'server quit': '000', 'aknowledge': '001', 'refused': '002',
          'start': '003', 'new player': '004', 'player left': '005',
          'game end': '006', 'step': '007', 'move': '008', 'wall': '009', 'door': '010',
          'up': 'n', 'down': 's', 'right': 'e', 'left': 'o'}