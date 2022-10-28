import random

import arcade

from card import Card

from main_card_sprites_playing_area import MainCardSpritesPlayingArea
from players_card_sprites_area import PlayersCardSpritesArea
from screen_configuration import ScreenConfiguration


class MyGame(arcade.Window):
    """ Main application class. """

    def __init__(self, screen_config: ScreenConfiguration):
        self.__config = screen_config
        super().__init__(self.__config.width, self.__config.height, self.__config.screen_title, fullscreen=True)

        self.__config.init_current_screen()

        # Sprite list with all the cards, no matter what pile they are in.
        self.card_list = None

        arcade.set_background_color(arcade.color.CADET)

        # List of cards we are dragging with the mouse
        self.held_cards = None

        # Original location of cards we are dragging with the mouse in case
        # they have to go back.
        self.held_cards_original_position = None

        # Sprite list with all the mats tha cards lay on.
        self.pile_mat_list: arcade.SpriteList = arcade.SpriteList()

        self.main_cars_sprites_playing_area = MainCardSpritesPlayingArea(self.pile_mat_list, self.__config)
        self.players_card_sprites_area = PlayersCardSpritesArea(self.pile_mat_list, self.__config)

    def setup(self):
        """ Set up the game here. Call this function to restart the game. """

        # List of cards we are dragging with the mouse
        self.held_cards = []

        # Original location of cards we are dragging with the mouse in case
        # they have to go back.
        self.held_cards_original_position = []

        # init main playing area with one sprite
        self.main_cars_sprites_playing_area.add_new_sprite()

        # Sprite list with all the cards, no matter what pile they are in.
        self.card_list = arcade.SpriteList()

        # Create every card
        for card_suit in self.__config.card_suites:
            for card_value in self.__config.card_values:
                card = Card(card_suit, card_value, self.__config.card_scale)
                card.position = self.__config.start_x, self.__config.middle_y
                self.card_list.append(card)




    #define Shuffle function because the native arcade function throws an exeption I cannot deal with
    # Shuffle the cards
    def shuffle_Cards(self):
        #temporary list fo the cards
        temp_list = arcade.SpriteList()

        #randomize number between 1 - 52 (no duplicates)
        self.list_rand = random.sample(range(len(self.card_list)), len(self.card_list))

        #use random,shuffle to shuffle the list of random numbers
        random.shuffle(self.list_rand)

        print(self.list_rand)
        for n in self.list_rand :
            temp_list.append(self.card_list[n])


        self.card_list = temp_list


    def on_draw(self):
        """ Render the screen. """
        # Clear the screen
        self.clear()

        # Draw the mats the cards go on to
        self.pile_mat_list.draw()

        # Draw the cards
        self.card_list.draw()

    def pull_to_top(self, card: arcade.Sprite):
        """ Pull card to top of rendering order (last to render, looks on-top) """

        # Remove, and append to the end
        self.card_list.remove(card)
        self.card_list.append(card)

    def on_mouse_press(self, x, y, button, key_modifiers):
        """ Called when the user presses a mouse button. """

        # Get list of cards we've clicked on
        cards = arcade.get_sprites_at_point((x, y), self.card_list)

        # Have we clicked on a card?
        if len(cards) > 0:
            # Might be a stack of cards, get the top one
            primary_card = cards[-1]

            # All other cases, grab the face-up card we are clicking on
            self.held_cards = [primary_card]
            # Save the position
            self.held_cards_original_position = [self.held_cards[0].position]
            # Put on top in drawing order
            self.pull_to_top(self.held_cards[0])

    def on_mouse_release(self, x: float, y: float, button: int,
                         modifiers: int):
        """ Called when the user presses a mouse button. """

        # If we don't have any cards, who cares
        if len(self.held_cards) == 0:
            return

        # Find the closest pile, in case we are in contact with more than one
        pile, distance = arcade.get_closest_sprite(self.held_cards[0], self.pile_mat_list)
        reset_position = True

        # See if we are in contact with the closest pile
        if arcade.check_for_collision(self.held_cards[0], pile):

            # For each held card, move it to the pile we dropped on
            for i, dropped_card in enumerate(self.held_cards):
                # Move cards to proper position
                dropped_card.position = pile.center_x, pile.center_y

            # Success, don't reset position of cards
            reset_position = False

            # Release on top play pile? And only one card held?
        if reset_position:
            # Where-ever we were dropped, it wasn't valid. Reset the card's position
            # to its original spot.
            for pile_index, card in enumerate(self.held_cards):
                card.position = self.held_cards_original_position[pile_index]

        # We are no longer holding cards
        self.held_cards = []

    def on_mouse_motion(self, x: float, y: float, dx: float, dy: float):
        """ User moves mouse """

        # If we are holding cards, move them with the mouse
        for card in self.held_cards:
            card.center_x += dx
            card.center_y += dy

    def on_key_press(self, symbol: int, modifiers: int):
        if symbol == arcade.key.ESCAPE:
            arcade.close_window()

    #init the players with 6 cards each
    #def init_Cars(self):



def main():
    """ Main function """
    config = ScreenConfiguration()
    window = MyGame(config)
    window.setup()
    window.shuffle_Cards()
    arcade.run()


if __name__ == "__main__":
    main()