import random
from server.models.game import Game
from server.models.vocabulary import VOCABULARY

class GameService:
    def __init__(self):
        self.active_games = {} 

    def get_categories(self):
        return list(VOCABULARY.keys())

    def create_game(self, room_id: str, player_1: str, category: str):
        """
        Creates a game. If category is 'RANDOM', the server picks one automatically.
        """
        chosen_category = category.upper()
        
        # Logic for Random Selection
        if chosen_category == "RANDOM":
            chosen_category = random.choice(list(VOCABULARY.keys()))
            print(f"🎲 Random mode: Server picked {chosen_category}")

        # Validation
        if chosen_category not in VOCABULARY:
            return {"status": "error", "message": "Invalid category selection."}

        # Pick the secret word
        secret_word = random.choice(VOCABULARY[chosen_category])

        new_game = Game(
            secret_word=secret_word,
            player_1=player_1,
            player_2="" 
        )

        self.active_games[room_id] = new_game

        # Create masked word (Hiding letters)
        masked_word = " ".join(["_" if char != " " else " " for char in secret_word])

        return {
            "status": "success", 
            "message": f"Game created with {chosen_category} category!",
            "category": chosen_category,
            "word_length": len(secret_word),
            "masked_word": masked_word
        }