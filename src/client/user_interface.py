# -*- coding: utf-8 -*-

"""Module that interacts with the user."""


commands = {'start game': 'c', 'print rules': 'h', 'leave': 'q',
            'directions': {'up': 'n', 'down': 's', 'right': 'e', 'left': 'o'},
            'wall': 'm', 'door': 'p'}


def print_rules():
    """Function that asks whether to print the rules and eventually prints them."""            
    print()
    print(u"\u2022", "You control a robot and you play against other players to escape the labirinth. Each turn you have 30 seconds to make your move or you'll be eliminated.")
    print(u"\u2022", "Objects in the labirinth:")
    print("\t O: wall (blocks robot)\n\t .: door (robot can pass)\n\t U: exit\n\t X: your robot\n\t x: adversaries' robots")
    print(u"\u2022", "Controls:")
    print("\t Q: quit\n\t N: move up\n\t S: move down\n\t E: move right\n\t O: move left\n\t All move commands can be followed by a number to express how far to move.")
    print("\t M{d}: turn the door adjacent to the robot in direction {d} into a wall.\n\t P{d} turn the wall adjacent to the robot in direction {d} into a door\n\n")
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


def interpret_command(command):
    """Function that interprets the command inserted by the user.
    Returns a tuple with the command and evenctually an argument (depending on
    the command) if reading happened correctly, and returns None otherwise."""
    
    if command == '':
        return None
    
    elif command == commands['print rules'] or command == commands['leave']:
        return (command,)
    
    elif command[0] in commands['directions']:
        if string_is_positive_integer_or_empty(command[1:]):
            distance = 1
            if command[1:]:
                distance = int(command[1:])
            command = command[0]
            return (command, distance)
        
    elif command[0] in (commands['wall'], commands['door']) and command[1:].strip() in commands['directions']:
            direction = command[1:].strip()
            command = command[0]
            return (command, direction)
    
    return None