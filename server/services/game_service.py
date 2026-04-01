import random
from server.models.game import Game
from server.models.vocabulary import VOCABULARY
from server.database.game_repo import create_game as save_game
from server.database.game_repo import find_game, update_game
import uuid

class GameService:
    
    def _success(self, data):
        return {"status": "success", **data}, 200

    def _created(self, data):
        return {"status": "success", **data}, 201

    def _error(self, message, code=400):
        return {"status": "error", "message": message}, code

    def _conflict(self, message):
        return {"status": "error", "message": message}, 409

    def _not_found(self):
        return {"status": "error", "message": "Game not found."}, 404
    

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

    def create_game(self, player_1: str, category: str):
        """
        Creates a game. If category is 'RANDOM', the server picks one automatically.
        """
        room_id = str(uuid.uuid4())[:6]
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
            player_1=player_1
        )
        save_game({
                "room_id": room_id,
                "owner": player_1,
                "players": [player_1],
                "player_errors": {
                    player_1: 0
                },
                "player_status": {
                    player_1: "ALIVE"
                },
                "secret_word": secret_word,
                "guessed_letters": [],
                "status": "WAITING",
                "current_turn": 0
            }) 

        return self._created({
            "room_id": room_id,
            "message": f"Game created with {chosen_category} category!",
            "category": chosen_category,
            "word_length": len(secret_word),
            "masked_word": self._get_masked_word(new_game)
        })
    
    def join_game(self, room_id: str, player: str):
        game_data = find_game(room_id)

        if not game_data:
            return self._not_found()

        if player in game_data["players"]:
            return self._conflict("Player already in game.")

        game_data["players"].append(player)

        if player not in game_data["player_errors"]:
            game_data["player_errors"][player] = 0

        if player not in game_data["player_status"]:
            game_data["player_status"][player] = "ALIVE"

        update_game(room_id, {
            "players": game_data["players"],
            "player_errors": game_data["player_errors"],
            "player_status": game_data["player_status"]
        })

        return {
            "status": "success",
            "players": game_data["players"]
        }

    def start_game(self, room_id: str, player: str):
        game_data = find_game(room_id)

        if not game_data:
            return self._not_found()

        if player != game_data["owner"]:
            return self._conflict("Only the owner can start the game.")

        if len(game_data["players"]) < 2:
            return self._error("Need at least 2 players.")

        update_game(room_id, {
            "status": "IN_PROGRESS"
        })

        return {
            "status": "success",
            "current_player": game_data["players"][0]
        }


    def guess_letter(self, room_id: str, player: str, letter: str):
        """
        Processes a letter guess, updates the game state, and checks for win/lose conditions.
        """
        game_data = find_game(room_id)

        if not game_data:
            return self._not_found()

        game = Game(
            secret_word=game_data["secret_word"],
            player_1=game_data["owner"]
        )

        game.players = game_data["players"]
        game.guessed_letters = game_data["guessed_letters"]
        game.player_errors = game_data["player_errors"]
        game.player_status = game_data["player_status"]
        game.status = game_data["status"]
        game.current_turn = game_data["current_turn"]


        if game.status != "IN_PROGRESS":
            return self._conflict("Game already finished.")
        
        
        if game.player_status.get(player) == "ELIMINATED":
            return self._conflict("You are eliminated.")
        
        current_player = game.players[game.current_turn]
        if player != current_player:
            return self._conflict(f"Not your turn. Current player: {current_player}")
        
        letter = letter.upper()

        # Check if letter was already guessed
        if letter in game.guessed_letters:
            return self._conflict("Letter already guessed.")

        # Add letter to guessed list
        game.guessed_letters.append(letter)

        # Check for error
        if letter not in game.secret_word:
            game.player_errors[player] += 1

        # Check Win Condition (All letters guessed, ignoring spaces)
        if all((char in game.guessed_letters or char == " ") for char in game.secret_word):
            game.status = "FINISHED"
            
        # Check Lose Condition (Max 6 errors)
        elif game.player_errors[current_player] >= 6:
            game.player_status[current_player] = "ELIMINATED"
            alive_players = [
                p for p in game.players if game.player_status[p] == "ALIVE"
            ]
            if len(alive_players) == 1:
                game.status = "FINISHED"


        if game.status == "IN_PROGRESS":
            self._next_turn(game)

        update_game(room_id, {
            "guessed_letters": game.guessed_letters,
            "player_errors": game.player_errors,
            "player_status": game.player_status,
            "status": game.status,
            "current_turn": game.current_turn
        })

        if game.status == "FINISHED":
            masked = " ".join(list(game.secret_word))
        else:
            masked = self._get_masked_word(game)

        return self._success({
            "message": "Guess processed.",
            "game_status": game.status,
            "current_player": game.players[game.current_turn],
            "player_errors": game.player_errors,
            "guessed_letters": game.guessed_letters,
            "masked_word": masked
        })
    

    def guess_word(self, room_id: str, player: str, word: str):
        game_data = find_game(room_id)

        if not game_data:
            return self._not_found()

        # recria objeto Game a partir do banco
        game = Game(
            secret_word=game_data["secret_word"],
            player_1=game_data["owner"]
        )

        game.players = game_data["players"]
        game.guessed_letters = game_data["guessed_letters"]
        game.player_errors = game_data["player_errors"]
        game.player_status = game_data["player_status"]
        game.status = game_data["status"]
        game.current_turn = game_data["current_turn"]

        if game.status != "IN_PROGRESS":
            return self._conflict("Game already finished.")

        current_player = game.players[game.current_turn]
        if player != current_player:
            return self._conflict("Not your turn.")

        if game.player_status.get(player) == "ELIMINATED":
            return self._conflict("You are eliminated.")
        
        word = word.upper()

        if word == game.secret_word:
            game.status = "FINISHED"
        else:
            game.player_errors[player] += 1

            if game.player_errors[player] >= 6:
                game.player_status[player] = "ELIMINATED"

                alive_players = [
                    p for p in game.players if game.player_status[p] == "ALIVE"
                ]

                if len(alive_players) == 1:
                    game.status = "FINISHED"

        if game.status == "FINISHED":
            masked = " ".join(list(game.secret_word))
        else:
            masked = self._get_masked_word(game)

        if game.status == "IN_PROGRESS":
            self._next_turn(game)

        update_game(room_id, {
            "guessed_letters": game.guessed_letters,
            "player_errors": game.player_errors,
            "player_status": game.player_status,
            "status": game.status,
            "current_turn": game.current_turn
        })

        return self._success({
            "game_status": game.status,
            "player_errors": game.player_errors,
            "masked_word": masked
        })
    
    def _next_turn(self, game):
        total_players = len(game.players)

        for _ in range(total_players):
            game.current_turn = (game.current_turn + 1) % total_players
            next_player = game.players[game.current_turn]

            if game.player_status.get(next_player) == "ALIVE":
                return

        game.status = "FINISHED"