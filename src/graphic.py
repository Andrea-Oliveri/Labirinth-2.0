# -*- coding: utf-8 -*-

"""Module that draws the labyrinth."""


symbols = {'player':'X', 'other player': 'x', 'door': '.', 'wall': 'O', 'exit': 'U', 'empty': ' '}


def draw_all(level_with_players):
    """Function that draws the player and the map passed as parameter."""
    print('\n', level_with_players, '\n', sep='')
