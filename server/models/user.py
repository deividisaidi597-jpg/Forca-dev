from dataclasses import dataclass

@dataclass
class User:
    username: str
    password_hash: str
    is_online: bool = False
    games_won: int = 0
    games_played: int = 0