import arcade
import arcade.gui

from game_logic.game_logic import GameLogic
from gui.buttons.finish_move_buton import FinishMoveButton
from gui.buttons.take_cards_button import TakeCardsButton
from gui.card import Card

from play_areas.playground import Playground
from play_areas.not_active_cards import NotActiveCards
from play_areas.player_area import PlayerArea
from gui.screen_configuration import ScreenConfiguration
from Constants import WIN, LOSE
import gui.view_manager
from gui.Animations.animation import Animation

class GameView(arcade.View):
    """ Main application class. """

    def __init__(self, screen_config: ScreenConfiguration, difficulty: int):
        self.config = screen_config
        super().__init__()

        self.view_manager = gui.view_manager.ViewManager()

        arcade.set_background_color(arcade.color.AMAZON)
        # Show buttons if needed
        self.show_btn = False
        #Do animation
        self.do_animation = False
        #Card to move around
        self.animated_card = None
        #Init Animations class
        self.animation = None
        # List of unused_cards we are dragging with the mouse
        self.held_card = None

        # Original location of unused_cards we are dragging with the mouse in case
        # they have to go back.
        self.held_card_original_position = None

        # Sprite list with all the mats that unused_cards lay on.
        self.mat_list: arcade.SpriteList = arcade.SpriteList()

        # Flag for checking if card was moved to new area
        self.card_moved = False

        # Initialize the sprite lists
        self.playground = Playground(self.config)
        self.human_player = PlayerArea(self.config.start_x_bottom, self.config.bottom_y,
                                       self.config.x_spacing)
        self.computer_player = PlayerArea(self.config.start_x_top, self.config.top_y,
                                          -self.config.x_spacing)
        self.not_active_cards = NotActiveCards(self.config)

        # Initialize the utils so we can use helper functions
        self.game_logic = GameLogic(self.human_player, self.computer_player, self.playground,
                                    self.not_active_cards, difficulty)
        # --- Required for all code that uses UI element,
        # a UIManager to handle the UI.
        self.manager = arcade.gui.UIManager()
        self.manager.enable()

        # Create a vertical BoxGroup to align buttons
        self.v_box = arcade.gui.UIBoxLayout()

        # Create the buttons
        self.finish_move_button = FinishMoveButton(self.playground, self.game_logic, self.human_player,
                                                   self.computer_player)
        self.v_box.add(self.finish_move_button.with_space_around(bottom=20))

        self.take_cards_button = TakeCardsButton(self.playground, self.game_logic, self.human_player)
        self.v_box.add(self.take_cards_button.with_space_around(bottom=20))

        self.manager.add(
            arcade.gui.UIAnchorWidget(
                align_y=self.config.bottom_y - self.config.card_height * 2,
                child=self.v_box)
        )
        self.hint_text = "Your turn!\nAttack!"
        self.computer_text = ""

        self.setup()

    def setup(self):
        """ Set up the game here. Call this function to restart the game. """

        # List of unused_cards we are dragging with the mouse
        self.held_card = arcade.Sprite

        # Original location of unused_cards we are dragging with the mouse in case
        # they have to go back.
        self.held_card_original_position = ()

        # init main playing area with one sprite
        self.playground.add_new_sprite()

        # Create every card
        for card_suit in self.config.card_suites:
            for card_value in self.config.card_values:
                card = Card(card_suit, card_value, self.config.card_scale)
                card.position = self.config.start_x, self.config.middle_y
                self.not_active_cards.add_new_card(card)

        # Shuffle the unused_cards
        self.not_active_cards.get_unused_cards().shuffle()

        for index in range(0, 12):
            card = self.not_active_cards.remove_last_card()
            if index < 6:
                card.face_up()
                self.human_player.add_new_card(card)
            else:
                self.computer_player.add_new_card(card)

        # Pick the trump card
        trump_card: Card = self.not_active_cards.get_unused_cards()[0]
        self.not_active_cards.set_trump_card(trump_card)
        trump_card.face_up()
        trump_card.angle = 90
        trump_card.center_x = self.config.card_width * 1.2

    def finish_turn(self):
        if self.computer_player.is_taking:
            self.game_logic.computer_take_cards()
            self.computer_player.is_taking = False
            self.human_player.is_turn = True

        elif self.human_player.is_turn:
            self.human_player.is_turn = False

            self.game_logic.finish_turn()

    def on_draw(self):
        """ Render the screen. """
        # Clear the screen
        self.clear()

        # Draw the mats for the main card area
        self.playground.get_mats().draw()

        # if any cards placed in the playground draw them
        self.playground.get_all_cards().draw()

        # draw not active cards
        self.not_active_cards.get_unused_cards().draw()

        # draw played cards
        self.not_active_cards.get_played_cards().draw()

        # draw computer cards
        self.computer_player.get_cards().draw()

        # draw the label
        arcade.draw_text(self.hint_text, self.config.start_x, self.config.bottom_y + self.config.card_height,
                         arcade.color.BLACK, 24)
        # draw the label
        arcade.draw_text(self.computer_text, self.config.start_x, self.config.top_y - (self.config.card_height * 1.5),
                         arcade.color.BLACK, 24)

        if self.show_btn:
            # Draw v_box with buttons
            self.manager.draw()

        # draw player cards
        self.human_player.get_cards().draw()

        if self.animated_card is not None:
            self.animated_card.draw()

    def on_mouse_press(self, x, y, button, key_modifiers):
        """ Called when the user presses a mouse button. """

        # Get list of unused_cards we've clicked on
        cards: list[arcade.Sprite] = arcade.get_sprites_at_point((x, y), self.human_player.get_cards())

        # Have we clicked on a card?
        if len(cards) > 0:
            # Might be a stack of unused_cards, get the top one
            self.held_card = cards[-1]

            # Get original position
            self.held_card_original_position = self.held_card.position

    def on_mouse_release(self, x: float, y: float, button: int,
                         modifiers: int):
        """ Called when the user presses a mouse button. """

        # If we don't have any unused_cards, who cares
        if not isinstance(self.held_card, Card):
            return

        # Find the closest mat, in case we are in contact with more than one
        mat, distance = arcade.get_closest_sprite(self.held_card, self.playground.get_mats())
        reset_position = True

        # See if we are in contact with the closest mat
        if arcade.check_for_collision(self.held_card, mat):
            # Take index of the mat the player wants to put his card on
            mat_index = self.playground.get_mats().index(mat)

            # Check if the card can be placed on the mat
            reset_position = self.game_logic.player_move(mat_index, self.held_card)

        # Check if the card must be put back
        if reset_position:
            # Where-ever we were dropped, it wasn't valid. Reset the card's position
            # to its original spot.
            self.held_card.position = self.held_card_original_position
        else:
            # Add the card and mat to the main unused_cards list
            self.playground.add_new_card(self.held_card)

            # remove card from human player
            self.human_player.remove_card(self.held_card)
            self.human_player.is_turn = False
            self.show_btn = True

        # We are no longer holding unused_cards
        self.held_card = None

    def on_mouse_motion(self, x: float, y: float, dx: float, dy: float):
        """ User moves mouse """
        # If we are holding a card , move them with the mouse
        if isinstance(self.held_card, Card):
            self.held_card.center_x += dx
            self.held_card.center_y += dy

    def on_key_press(self, symbol: int, modifiers: int):
        if symbol == arcade.key.ESCAPE:
            self.view_manager.show_menu_view()
        if symbol == arcade.key.ENTER:
            pass
            # self.init_Animation()

    def on_update(self, delta_time: 1):
        """ Movement and game logic """
        print(len(self.playground.get_mats()))
        print("list von cards", len(self.playground.get_cards()))
        # self.card_list.update()
        # if isinstance(self.held_card, Card):
        #     if self.held_card.collides_with_list(self.playground.get_mats()):
        #         print("Collides with main mat")
        if self.do_animation:
           # print(str(self.animation.get_dx()) + " " + str(self.animation.get_dy()))

            self.do_animation,self.animated_card = self.animation.do_animation(self.animated_card, self.playground)

        else:

            if self.computer_player.is_taking:
                self.hint_text = "Add more cards or finish turn"
                if len(self.playground.get_cards()[-1]) == 1:
                    self.playground.add_new_sprite()
            elif self.human_player.is_taking:
                self.playground.add_new_sprite()
                if self.game_logic.make_computer_attack_move() == None:
                    self.human_player.is_turn = False
                    self.human_player.is_taking = False
                    self.game_logic.finish_turn()

            else:
                playground_cards = self.playground.get_cards()[-1]

                if len(playground_cards) == 0:
                    if not self.human_player.is_turn:
                        self.computer_text = "Computer attacked"
                        card = self.game_logic.make_computer_attack_move()
                        if card == None or len(self.computer_player.get_cards()) == 0:
                            self.game_logic.finish_turn()
                            self.human_player.is_turn = True
                            self.computer_text = "Computer finished his turn"
                            self.show_btn = False
                        else:
                            self.animated_card = card

                            self.animation = Animation(self.playground.get_mats()[-1].position, card.position)
                            self.do_animation = True
                    else:
                        self.hint_text = "Your turn!\nAttack"


                elif len(playground_cards) == 1:
                    if not self.human_player.is_turn:
                        self.computer_text = "Computer defended"
                        card = self.game_logic.make_computer_defence_move()
                        if card == None:
                            # self.game_logic.finish_turn()
                            self.computer_player.is_taking = True
                            self.human_player.is_turn = True
                            self.computer_text = "Computer is taking the cards"
                            if len(self.computer_player.get_cards()) == 0:
                                self.game_logic.finish_player_turn()
                        else:
                            self.animated_card = card
                            self.animation = Animation(playground_cards[0].position, card.position)
                            self.do_animation = True

                    else:
                        self.hint_text = "Your turn!\nDefend or take cards"
                        if len(self.computer_player.get_cards()) == 0:
                            self.game_logic.finish_player_turn()

                elif len(self.playground.get_cards()[-1]) == 2:
                    self.playground.add_new_sprite()

        if len(self.not_active_cards.get_unused_cards()) == 0 and len(self.human_player.get_cards()) == 0:
            self.view_manager.show_win_lose_view(WIN, self.config)
        elif len(self.not_active_cards.get_unused_cards()) == 0 and len(self.computer_player.get_cards()) == 0:
            self.view_manager.show_win_lose_view(LOSE, self.config)