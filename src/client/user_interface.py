# -*- coding: utf-8 -*-

"""Module that interacts with the user."""


commands = {'start game': 'c', 'print rules': 'h', 'leave': 'q',
            'directions': ('n', 's', 'e', 'o'), 'wall': 'm', 'door': 'p'}


def print_rules():
    """Function that asks whether to print the rules and eventually prints them."""            
    print()
    print(u"\u2022", "You control a robot and you play against other players to escape the labirinth. During your turn you have limited time to move, after which you will be eliminated.")
    print(u"\u2022", "Objects in the labirinth:")
    print("\t O: wall (blocks robot)\n\t .: door (robot can pass)\n\t U: exit\n\t X: your robot\n\t x: adversaries' robots")
    print(u"\u2022", "Controls:")
    print("\t Q: quit\n\t N: move up\n\t S: move down\n\t E: move right\n\t O: move left\n\t All move commands can be followed by a number to express how far to move.")
    print("\t M{d}: turn the door adjacent to the robot in direction {d} into a wall.\n\t P{d} turn the wall adjacent to the robot in direction {d} into a door (can't be done with exterior walls).\n\n")
    return


def string_is_positive_integer_or_empty(string):
    """Function that tests whether the string passed as parameter is empty or
    contains an integer >=0. Returns true if it's the case, False otherwise."""
    if not string:
        return True
    try:
        val = int(string)
        if val >= 0 :
            return True
        else:
            return False
    except ValueError:
        return False


def interpret_game_action(command):
    """Function that interprets the game action command inserted by the user.
    Returns a dictionnaire with the command and the argument (if it's a move command,
    argument is a distance and if it's a wall or door command, argument is the
    direction) if reading happened correctly, and returns None otherwise."""
    
    if command == '':
        return None
    
    elif command[0] in commands['directions']:
        if string_is_positive_integer_or_empty(command[1:]):
            distance = 1
            if command[1:]:
                distance = int(command[1:])
            direction = command[0]
            return {'command': direction, 'distance': distance}
        
    elif command[0] in (commands['wall'], commands['door']) and command[1:].strip() in commands['directions']:
            direction = command[1:].strip()
            command = command[0]
            return {'command': command, 'direction': direction}
    
    return None