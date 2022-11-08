from abc import ABC, abstractmethod

from gui.card import Card
from play_areas.main_card_sprites_playing_area import MainCardSpritesPlayingArea
from play_areas.not_active_cards import NotActiveCards
from play_areas.player_area import PlayerArea


class Strategy(ABC):

    def __init__(self, computer_area: PlayerArea, main_card_sprites_playing_area: MainCardSpritesPlayingArea,
                 not_active_cards: NotActiveCards):
        super().__init__()
        self.computer_area = computer_area
        self.main_card_sprites_playing_area = main_card_sprites_playing_area
        self.not_active_cards = not_active_cards

    @abstractmethod
    def compute_best_attack_move(self):
        pass

    @abstractmethod
    def compute_best_defense_move(self):
        pass

    def validate_defence_move(self, bottom_card, top_card):
        if bottom_card.suit == top_card.suit:
            if top_card.value > bottom_card.value:
                return True
        elif top_card.suit == self.not_active_cards.trump_card.suit and bottom_card.suit != self.not_active_cards.trump_card.suit:
            return True
        return False

    def validate_attack_move(self, top_card):
        if len(self.main_card_sprites_playing_area.cards[0]) == 0 and isinstance(top_card, Card):
            return True
        else:
            # Get all the unused_cards from the main area
            cards = self.main_card_sprites_playing_area.get_all_cards()
            # create a set with all the values from the unused_cards
            values = {card.value for card in cards}
            if top_card.value in values:
                return True
        return False
