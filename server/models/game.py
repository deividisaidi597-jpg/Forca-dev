from dataclasses import dataclass, field
from typing import List

@dataclass
class Game:
    secret_word: str
    player_1: str
    player_2: str
    guessed_letters: List[str] = field(default_factory=list)
    errors: int = 0
    status: str = "IN_PROGRESS" # Can be: IN_PROGRESS, VICTORY, DEFEAT