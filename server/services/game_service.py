import random
from server.models.game import Game
from server.models.vocabulary import VOCABULARY

class GameService:
    def __init__(self):
        self.active_games = {} 

    def get_categories(self):
        return list(VOCABULARY.keys())

    def _get_masked_word(self, game: Game) -> str:
        """
        Helper method to generate the word with underscores for unguesed letters.
        Example: 'A P P _ E'
        """
        masked = []
        for char in game.secret_word:
            if char == " ":
                masked.append(" ") # Keep spaces between words
            elif char in game.guessed_letters:
                masked.append(char) # Reveal guessed letter
            else:
                masked.append("_") # Hide unguessed letter
        return " ".join(masked)

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

        return {
            "status": "success", 
            "message": f"Game created with {chosen_category} category!",
            "category": chosen_category,
            "word_length": len(secret_word),
            "masked_word": self._get_masked_word(new_game)
        }

    def guess_letter(self, room_id: str, letter: str):
        """
        Processes a letter guess, updates the game state, and checks for win/lose conditions.
        """
        game = self.active_games.get(room_id)
        
        if not game:
            return {"status": "error", "message": "Game not found."}

        if game.status != "IN_PROGRESS":
            return {"status": "error", "message": f"Game already finished. Result: {game.status}"}

        letter = letter.upper()

        # Check if letter was already guessed
        if letter in game.guessed_letters:
            return {
                "status": "warning", 
                "message": "Letter already guessed.",
                "game_status": game.status,
                "errors": game.errors,
                "masked_word": self._get_masked_word(game)
            }

        # Add letter to guessed list
        game.guessed_letters.append(letter)

        # Check for error
        if letter not in game.secret_word:
            game.errors += 1

        # Check Win Condition (All letters guessed, ignoring spaces)
        if all((char in game.guessed_letters or char == " ") for char in game.secret_word):
            game.status = "VICTORY"
            
        # Check Lose Condition (Max 6 errors)
        elif game.errors >= 6:
            game.status = "DEFEAT"

        return {
            "status": "success",
            "message": "Guess processed.",
            "game_status": game.status,
            "errors": game.errors,
            "guessed_letters": game.guessed_letters,
            "masked_word": self._get_masked_word(game)
        }