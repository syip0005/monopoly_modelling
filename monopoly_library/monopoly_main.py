import random
import re
import csv
import logging

logging.basicConfig(filename='player_test.log', level=logging.DEBUG)

""""
    Name: Monopoly Library (Board, Cards and Player)
    Author: Scott Y
    Date: 11 July 2021
    Description: To create a library which can mimic the Monopoly board and cards
"""


# TODO implement all money features

class Dice:
    """Simple Dice class to simulate dice roll"""

    def __init__(self, no_dice=2, rigged=False, rigged_list=None):

        self.no_dice = no_dice

        self.rigged = rigged
        if rigged_list is None:
            rigged_list = []
        self.rigged_list = rigged_list

    def roll(self):
        """Roll method to roll dice.
        :returns tuple with integer (total sum) and list (all rolls)"""

        if self.rigged:
            return sum(self.rigged_list), self.rigged_list

        total_rolls = list()
        for i in range(self.no_dice):
            total_rolls.append(random.randint(1, 6))
        return sum(total_rolls), total_rolls


class Monopoly:
    """Monopoly class. Holds instance of game. Game will keep track of state of houses, actions for players,
    and cards (holding sequence and also card interpretation). Note, Player class keeps track of player state items (
    position, jail state, money) """

    def __init__(self, board_file_instance, chance_cards, community_cards, jail_length=3, jail_position=10):
        self.board_file = self.board_processing(board_file_instance)
        self.number_tiles = len(self.board_file)
        self.jail_length = jail_length
        self.jail_position = jail_position

        self.chance_cards = CardCollection('Chance', chance_cards)
        self.community_cards = CardCollection('Community Cards', community_cards)

    @staticmethod
    # TODO: change boardprocessing to process .csv file instead like the cards
    def board_processing(board_file):
        with open(board_file, 'r') as f:
            board_data_dump = f.readlines()

        colour_dump = [item.strip() for item in board_data_dump[1].split(',')]
        location_dump = [item.strip().title() for item in board_data_dump[0].split(',')]

        board_dict = dict(enumerate(zip(location_dump, colour_dump)))

        return board_dict

    def get_action(self, position, roll, jail_state, jail_turn):

        """Provides action for player by returning:
        (position, jail_state, jail_turn)
        :rtype: tuple(int, bool, int)"""

        logging.info('current position: {}'.format(position))

        # Initialise standard parameters
        current_location = self.board_file[position]

        # Initialise outputs
        output_position = position
        output_jail_state = jail_state

        # Check if in jail
        if jail_state:

            output_position = position - roll[0]

            logging.info('in jail, jail turn: {}'.format(jail_turn + 1))

            # If player rolls a double
            if len(set(roll[1])) == 1:

                output_jail_state = False
                output_position = (output_position + roll[0]) % self.number_tiles
                jail_turn = 0

                logging.info('rolled a double, going to position {}'.format(output_position))

                # get action of latest position (no re-roll) using self call (1 level recurision)
                output_position, output_jail_state, jail_turn = self.get_action(output_position, roll,
                                                                                output_jail_state, jail_turn)

            elif jail_turn == self.jail_length - 1:

                output_jail_state = False
                jail_turn = 0

            else:

                jail_turn += 1

            return output_position, output_jail_state, jail_turn

        # Check if Go to Jail
        if re.match(r'.*(to jail).*', current_location[0], flags=re.I):
            output_position = self.jail_position
            output_jail_state = True

        # Check if Chance or Community Chest
        if current_location[0].lower() == 'chance':

            current_card = self.chance_cards.next_card()

            output_position, output_jail_state = self.card_action(current_card, position)

        elif current_location[0].lower() == 'community chest':

            current_card = self.community_cards.next_card()

            output_position, output_jail_state = self.card_action(current_card, position)

        return output_position, output_jail_state, jail_turn

    def card_action(self, card, position):

        # Initialise output variables
        card_position = position
        card_jail_state = False
        # card_money_delta = int()

        logging.info('hit a card, card is {}'.format(card.description))

        if card.card_type == 'move':

            # TODO haven't implemented if we pass go, but maybe can implement in player??
            if card.move_type == 'loc':

                # TODO: think about implementing a dual-side dictionary for ease (note that this is one to many)

                # If we're searching for location, search dictionary and use first part of tuple
                # as remember our dictionary format is {location_num:(name, type)}

                loc_idx = val_search(self.board_file, card.move_loc, idx=0)

                if loc_idx is None:
                    raise ValueError('Could not find location of Card in Board')
                else:
                    card_position = loc_idx

            elif card.move_type == 'num':

                card_position = position + int(card.move_loc)

            elif card.move_type == 'type':
                # type means search for next station or utilities
                # if type, we need to check current position and move only forwards

                found = False
                while not found:
                    loc_idx = val_search(self.board_file, card.move_loc, idx=1, start_pos=position)
                    if loc_idx is not None:
                        card_position = loc_idx
                        found = True

                if not found:
                    raise ValueError('Could not find station or utility')

        elif card.card_type == 'go_jail':

            card_jail_state = True
            card_position = self.jail_position

        # elif card.card_type == 'jail_free':
        # TODO implement later

        return card_position, card_jail_state


class Player:
    """Player class which keeps track of player state items such as player position,
    player jail state, player money"""

    def __init__(self, player_name, board: Monopoly, start_money=1500):
        self.player_name = player_name
        self.money = start_money
        self.board = board
        self.jail_state = False
        self.jail_turn = 0
        self.position = 0
        self.player_dice = Dice(2)

    def roll_turn(self, double_rolls_so_far=0):

        # used to keep track of previous jail state, so we can't prevent rolling again
        prev_jail_state = self.jail_state

        if double_rolls_so_far == 3:  # can only roll 3 doubles
            logging.info('triple doubles! go to jail')
            return self.go_jail_state()

        current_roll = self.player_dice.roll()

        logging.info('roll: {}'.format(current_roll))

        logging.info(
            'start position: {}, name: {}, injail: {}, jailturn: {}'.format(self.position,
                                                                            self.board.board_file[self.position],
                                                                            self.jail_state, self.jail_turn))

        self.position = (self.position + current_roll[0]) % self.board.number_tiles

        self.position, self.jail_state, self.jail_turn = self.board.get_action(self.position, current_roll,
                                                                               self.jail_state, self.jail_turn)

        logging.info(
            'end position: {}, name: {}, injail: {}, jailturn: {}'.format(self.position,
                                                                          self.board.board_file[self.position],
                                                                          self.jail_state, self.jail_turn))

        if not prev_jail_state and not self.jail_state and len(set(current_roll[1])) == 1:  # if we didn't end up in jail and we rolled a double
            self.roll_turn(double_rolls_so_far=double_rolls_so_far + 1)

        return self.position

    def go_jail_state(self):
        self.jail_turn = 0
        self.jail_state = True
        self.position = self.board.jail_position

        return self.position


class CardCollection:
    """Stack-like datatype to hold all Cards for a collection"""

    def __init__(self, collection_name, collection_file_instance, shuffle=True):

        self.collection_name = collection_name
        self.collection_cards = self.card_processing(collection_file_instance)

        # Shuffle cards

        if shuffle: random.shuffle(self.collection_cards)

    def next_card(self):

        # Pop last card out
        temp = self.collection_cards.pop()

        # Insert into front of deck
        self.collection_cards.insert(0, temp)

        return temp

    @staticmethod
    def card_processing(file):

        # Initialise variables
        card_dump = list()
        output_collection = list()

        with open(file, newline='') as f:

            card_csv = csv.reader(f)

            for row in card_csv:
                card_dump.append(row)

        for row in card_dump:
            # Process so that empty strings become None datatypes
            row_wth_Nones = [None if i in row == '' else i for i in row]

            output_collection.append(Card(row_wth_Nones[0], row_wth_Nones[1], row_wth_Nones[2], row_wth_Nones[3]))

        return output_collection


class Card:
    """Card class just to store information of cards"""

    def __init__(self, description, card_type, move_type=None, move_loc=None):
        self.description = description
        self.card_type = card_type
        self.move_type = move_type
        self.move_loc = move_loc

    def __str__(self):
        return 'Description: {}'.format(self.description)

    def __repr__(self):
        return '<Card>. Description: {}...'.format(self.description[:20])


def val_search(x, val, idx, start_pos=0):
    i = 0
    start_pos = start_pos
    while i <= len(x):
        search_pos = (start_pos + i) % len(x)
        if x[search_pos][idx].lower() == val.lower():
            return search_pos
        i += 1


def main():
    game = Monopoly('monopoly_board_aus.txt', 'monopoly_chance_aus.csv', 'monopoly_community_aus.csv')

    player_1 = Player('scott', game)

    output_list = list()
    for i in range(100):

        logging.info('turn number: {}'.format(i))
        output_list.append(player_1.roll_turn())


    print(game.board_file)

    print(output_list)


if __name__ == "__main__":
    main()
