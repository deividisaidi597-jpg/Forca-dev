from dataclasses import dataclass, field
from typing import List

@dataclass
class Game:
    def __init__(self, secret_word, player_1):
        self.secret_word = secret_word

        self.owner = player_1
        self.players = [player_1]  
        
        self.current_turn = 0

        self.guessed_letters = []
        self.player_errors = {
            player_1: 0
        }
        self.max_errors = 6
        self.player_status = {
            player_1: "ALIVE"
        }
        self.status = "WAITING"  # WAITING | IN_PROGRESS | VICTORY | DEFEAT