# -*- coding: utf-8 -*-

"""Module that interacts with files."""

import os

from src.graphic import symbols


levels_folder_name = "levels"
levels_extension = ".txt"
saved_game_name = "saved game"


def choose_level():
    """Function that gathers all the levels in the levels folder and asks which
    level the user would like to play. To select a level, the user must insert
    its full name."""
    
    #levels_list is a dictionary with level_name as key and level_path as value
    levels_list = {}
    for level_name in os.listdir(levels_folder_name):
        if level_name.endswith(levels_extension):
            level_path = os.path.join(levels_folder_name, level_name)
            level_name = level_name[:-len(levels_extension)].lower()
            levels_list[level_name] = level_path
    
    print("These are the available maps:")
    for index, name in enumerate(levels_list.keys()):
        print(index+1, "-", name)

    chosen_name = input("Write the name of the map you'd like to play: ").lower().strip()
    while chosen_name not in levels_list.keys():
        chosen_name = input("Invalid map name entered. Please try again: ").lower().strip()
    return levels_list[chosen_name]


def import_map(file_path):
    """Function that reads the file found at the path passed as parameter and
    performs two basic checks to test the validity of the map: the map is
    rectangular and the border of the map only contains walls or escape points.
    In case of error, an exception is launched and execution is terminated.
    Otherwise, this function returns the 2D list representing the level and
    player."""
    with open(file_path, 'r') as file:
        file = file.read()
        file = file.split('\n')
    list_2D = [line.strip() for line in file]
        
    possible_borders = [symbols['wall'], symbols['exit']]
                          
    if all(len(line) == len(list_2D[0]) for line in list_2D):
        if not ( all(piece in possible_borders for piece in list_2D[0]) and \
                 all(piece in possible_borders for piece in list_2D[-1]) and \
                 all(line[0] in possible_borders for line in list_2D) and \
                 all(line[-1] in possible_borders for line in list_2D) ):
            raise RuntimeError("Invalid map format: borders must contain only walls or exits.")
    else:
        raise RuntimeError("Invalid map format: map must be rectangular.")
      
    return list_2D