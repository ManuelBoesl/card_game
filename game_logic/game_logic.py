from game_logic.strategies.simple_strategy import SimpleStrategy
from game_logic.strategies.strategycontext import StrategyContext
from play_areas.computer_card_sprites_area import ComputerCardSpritesArea
from play_areas.main_card_sprites_playing_area import MainCardSpritesPlayingArea
from play_areas.not_active_cards import NotActiveCards
from play_areas.players_card_sprites_area import PlayersCardSpritesArea

class GameLogic:
    def __init__(self, player: PlayersCardSpritesArea, computer: ComputerCardSpritesArea,
                 main: MainCardSpritesPlayingArea, not_active_cards: NotActiveCards):
        self.player = player
        self.computer = computer
        self.main = main
        self.strategy = SimpleStrategy(computer, main, not_active_cards)
        self.strategy_context = StrategyContext(self.strategy, self.main, self.computer)

    def validate_player_defence(self, bottom_card, top_card):
        self.strategy_context.validate_defence_move(bottom_card, top_card)

    def gameplay(self):
        self.strategy_context.make_computer_move()
        pass


