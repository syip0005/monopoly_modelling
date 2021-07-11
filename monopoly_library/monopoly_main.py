import random
import re

""""
    Name: Monopoly Library (Board and Cards)
    Author: Scott Y
    Date: 11 July 2021
    Description: To create a library which can mimic the Monopoly board and cards
"""


class Monopoly:

    def __init__(self, board_file_instance, jail_length = 3):
        self.board_file = self.board_processing(board_file_instance)
        self.number_tiles = len(self.board_file)
        self.jail_length = jail_length

    @staticmethod
    def board_processing(board_file):
        with open(board_file, 'r') as f:
            board_data_dump = f.readlines()

        colour_dump = [item.strip() for item in board_data_dump[1].split(',')]
        location_dump = [item.strip().title() for item in board_data_dump[0].split(',')]

        board_dict = dict(enumerate(zip(location_dump, colour_dump)))

        return board_dict

    def get_action(self, position, roll, jail_state, jail_turn):

        """Provides action for player by returning:
        (position, jail_state)"""

        # Initiliase standard parameters
        current_location = self.board_file[position]

        # Initialise outputs
        output_position = int()
        output_jail_state = bool()

        # Check if in jail
        if jail_state:

            # If player rolls a double
            if len(set(roll)) == 1:

                output_jail_state = False
                output_position = (position + roll) % self.number_tiles

            elif jail_turn == 3:

                output_jail_state = False

        # Check if Go to Jail
        if re.match(r'.*(to jail).*', current_location, flags=re.I):

            output_position = 30 # hard key for now
            output_jail_state = True

        # Check if Chance or Community Chest
        if current_location.lower == 'chance':
            


        elif current_location.lower == 'community chest':


        return output_position, output_jail_state


class Player:
    pass


class Cards:

    def __init__(self, chance_file_instance, comm_file_instance):

        pass

    def card_processing(self, card_file):

        with open(card_file, 'r') as f:

            card_dump = f.readlines()

        
            


class Dice:
    """Simple Dice class to simulate dice roll"""

    def __init__(self, no_dice=2):
        self.no_dice = no_dice

    def roll(self):
        """Roll method to roll dice.
        :returns tuple with integer (total sum) and list (all rolls)"""

        total_rolls = list()
        for i in range(self.no_dice):
            total_rolls.append(random.randint(1, 6))
        return sum(total_rolls), total_rolls


def main():
    x = Monopoly('monopoly_board_aus.txt')
    print(x.board_file)


if __name__ == "__main__":
    main()