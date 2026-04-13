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

    def _conflict(self, message, code=409):
        return {"status": "error", "message": message}, code

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
                masked.append("␣") # Keep spaces between words
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
            return self._error("Invalid category selection.")

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
                "score": {
                    player_1: 0
                },
                "player_status": {
                    player_1: "ALIVE"
                },
                "used_words": [secret_word],
                "secret_word": secret_word,
                "guessed_letters": [],
                "status": "WAITING",
                "current_turn": 0,
                "category": chosen_category
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

        if game_data["status"] == "IN_PROGRESS" and player not in game_data["players"]:
            return self._conflict("Game already started.")

        if game_data["status"] == "FINISHED":
            return self._conflict("Game already finished.")

        if len(game_data["players"]) >= 2 and player not in game_data["players"]:
            return self._conflict("Room is full.")

        if player not in game_data["players"]:
            game_data["players"].append(player)

        if player not in game_data["player_errors"]:
            game_data["player_errors"][player] = 0

        if player not in game_data["player_status"]:
            game_data["player_status"][player] = "ALIVE"

        if "score" not in game_data:
            game_data["score"] = {}

        if player not in game_data["score"]:
            game_data["score"][player] = 0

        update_game(room_id, {
            "players": game_data["players"],
            "player_errors": game_data["player_errors"],
            "player_status": game_data["player_status"],
            "score": game_data["score"]
        })

        return self._success({
            "players": game_data["players"]
        })


    def start_game(self, room_id: str, player: str):
        game_data = find_game(room_id)

        if not game_data:
            return self._not_found()

        if player != game_data["owner"]:
            return self._conflict("Only the owner can start the game.")


        update_game(room_id, {
            "status": "IN_PROGRESS",
            "score": game_data["score"],
            "guessed_letters": game_data.get("guessed_letters", []),
            "player_errors": game_data.get("player_errors", {})
        })

        return self._success({
            "current_player": game_data["players"][0],
            "category": game_data.get("category"),
            "masked_word": self._get_masked_word(
                Game(secret_word=game_data["secret_word"], player_1=game_data["owner"])
            ),
            "word_length": len(game_data["secret_word"]),
            "players": game_data["players"],
            "score": game_data["score"],
            "player_errors": game_data["player_errors"],
            "game_status": game_data["status"],
            "categories_status": self.get_all_categories_status(
                game_data.get("used_words", [])
            ),
            "category_info": self.get_category_status(
                game_data["category"],
                game_data.get("used_words", [])
            )
        })


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

        # Não permitir chutar espaço
        if letter == " ":
            return self._conflict("You cannot guess a space character.")

        # Check if letter was already guessed
        if letter in game.guessed_letters:
            return self._conflict("Letter already guessed.")

        # Add letter to guessed list
        game.guessed_letters.append(letter)

        # Check for error
        if letter not in game.secret_word:
            game.player_errors[player] += 1

        # Check Win Condition (All letters guessed, ignoring spaces)
        # Get all unique letters in the word (excluding spaces)
        word_letters = set(char for char in game.secret_word if char != " ")
        guessed_letters_set = set(game.guessed_letters)
        
        if word_letters.issubset(guessed_letters_set):
            game_data["score"][player] += 1
            self._check_winner(game, game_data)
            game.guessed_letters = list(set(game.secret_word.replace(" ", "")))

            game.status = "ROUND_FINISHED"

            update_game(room_id, {
                "score": game_data["score"],
                "status": "ROUND_FINISHED",
                "categories_status": self.get_all_categories_status(
                    game_data.get("used_words", [])
                ),
                "guessed_letters": game.guessed_letters,
                "current_turn": None
            })

            return self._success({
                "message": "You completed the word!",
                "correct_word": game.secret_word,
                "game_status": "ROUND_FINISHED",
                "players": game.players,
                "player_errors": game.player_errors,
                "player_status": game.player_status,
                "score": game_data["score"],
                "current_player": player
            })
            
            
        # Check Lose Condition (Max 6 errors)
        elif game.player_errors[current_player] >= 6:
            game.player_status[current_player] = "ELIMINATED"
            game_data["score"][current_player] = max(
                0, game_data["score"].get(current_player, 0) - 1
            )
            alive_players = [
                p for p in game.players if game.player_status[p] == "ALIVE"
            ]
             # ninguém vivo → fim da rodada
            if len(alive_players) == 0:
                update_game(room_id, {
                    "player_status": game.player_status,
                    "score": game_data["score"],
                    "status": "ROUND_FINISHED",
                    "current_turn": None, 
                    "categories_status": self.get_all_categories_status(
                        game_data.get("used_words", [])
                    )
                })

                return self._success({
                    "message": "All players eliminated!",
                    "game_status": "ROUND_FINISHED",
                    "score": game_data["score"],
                    "players": game.players,
                    "player_status": game.player_status,
                    "player_errors": game.player_errors,
                    "current_player": None 
                })


        if game.status == "IN_PROGRESS":
            self._next_turn(game, game_data)

        update_game(room_id, {
            "guessed_letters": game.guessed_letters,
            "player_errors": game.player_errors,
            "player_status": game.player_status,
            "status": game.status,
            "score": game_data["score"],
            "current_turn": game.current_turn
        })

        if game.status == "ROUND_FINISHED":
            masked = " ".join(list(game.secret_word.replace(" ", "␣")))
        else:
            masked = self._get_masked_word(game)

        return self._success({
            "message": "Guess processed.",
            "game_status": game.status,
            "current_player": game.players[game.current_turn],
            "player_errors": game.player_errors,
            "guessed_letters": game.guessed_letters,
            "masked_word": masked,
            "player_status": game.player_status,
            "players": game.players,
            "score": game_data["score"]
        })
    

    def guess_word(self, room_id: str, player: str, word: str):
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

        current_player = game.players[game.current_turn]
        if player != current_player:
            return self._conflict("Not your turn.", 403)

        if game.player_status.get(player) == "ELIMINATED":
            return self._conflict("You are eliminated.")

        # Normalize the guessed word: remove extra spaces and convert to uppercase
        word = word.upper().strip()
        # Remove multiple spaces between words (keep single spaces)
        word = " ".join(word.split())

         # Normalize the secret word for comparison (ensure consistent spacing)
        secret_word_normalized = " ".join(game.secret_word.split())

        # ACERTOU A PALAVRA
        if word == secret_word_normalized or word == game.secret_word:
            game_data["score"][player] = game_data.get("score", {}).get(player, 0) + 1
            self._check_winner(game, game_data)
            result = self._get_new_word(game_data)

            if not result:
                update_game(room_id, {
                    "score": game_data["score"],
                    "status": "ROUND_FINISHED",
                    "categories_status": self.get_all_categories_status(
                        game_data.get("used_words", [])
                    ),
                    "player_errors": game.player_errors,
                    "player_status": game.player_status
                })

                return self._success({
                    "message": "Category completed!",
                    "correct_word": game.secret_word,
                    "game_status": "ROUND_FINISHED",
                    "score": game_data["score"],
                    "player_status": game.player_status,
                    "player_errors": game.player_errors,
                    "players": game.players,
                    "categories_status": self.get_all_categories_status(
                        game_data.get("used_words", [])
                    )
                })
            
            new_word, used_words, _ = result

            update_game(room_id, {
                "score": game_data["score"],
                "status": "ROUND_FINISHED",
                "categories_status": self.get_all_categories_status(
                    game_data.get("used_words", [])
                ),
                "player_errors": game.player_errors,
                "player_status": game.player_status,
                "current_turn": None
            })
            return self._success({
                "message": "You guessed the word!",
                "correct_word": game.secret_word,
                "masked_word": self._get_masked_word(game),
                "game_status": "ROUND_FINISHED",
                "players": game.players,
                "player_errors": game.player_errors,
                "player_status": game.player_status,
                "score": game_data["score"],
                "current_player": player
            })

        # ERROU
        game.player_errors[player] += 1

        if game.player_errors[player] >= 6:
            game.player_status[player] = "ELIMINATED"
            game_data["score"][player] = max(
                0, game_data["score"].get(player, 0) - 1
            )

            alive_players = [
                p for p in game.players if game.player_status[p] == "ALIVE"
            ]

            if len(alive_players) == 0:
                update_game(room_id, {
                    "player_status": game.player_status,
                    "score": game_data["score"],
                    "status": "ROUND_FINISHED",
                    "categories_status": self.get_all_categories_status(
                        game_data.get("used_words", [])
                    ),
                    "current_turn": None
                })

                return self._success({
                    "message": "All players eliminated!",
                    "game_status": "ROUND_FINISHED",
                    "score": game_data["score"],
                    "players": game.players,
                    "player_status": game.player_status,
                    "player_errors": game.player_errors,
                    "current_player": None
                })

        # próximo turno
        if game.status == "IN_PROGRESS":
            self._next_turn(game, game_data)

        update_game(room_id, {
            "player_errors": game.player_errors,
            "player_status": game.player_status,
            "current_turn": game.current_turn,
            "score": game_data["score"]
        })

        return self._success({
            "message": "Incorrect word!",
            "game_status": game.status,
            "players": game.players,
            "player_errors": game.player_errors,
            "player_status": game.player_status,
            "score": game_data["score"],
            "current_player": game.players[game.current_turn],
            "masked_word": self._get_masked_word(game)
        })


    def _get_new_word(self, game_data):
        current_category = game_data["category"]
        # used = game_data.get("used_words", [])
        used = game_data.get("used_words") or []

        available_words = [
            w for w in VOCABULARY[current_category]
            if w not in used
        ]

        if not available_words:
            return None  # NÃO troca categoria

        new_word = random.choice(available_words)
        used.append(new_word)

        return new_word, used, current_category


    def _check_winner(self, game, game_data):
        for player, points in game_data["score"].items():
            if points >= 10:
                game.status = "FINISHED"
                return player
        return None
    

    def restart_round(self, room_id: str, player: str):
        game_data = find_game(room_id)

        if not game_data:
            return self._not_found()

        if game_data["status"] == "FINISHED":
            return self._conflict("Game already finished.")

        current_category = game_data["category"]
        used_words = game_data.get("used_words", [])

        # pega lista de palavras disponíveis na categoria atual
        available_words = [
            w for w in VOCABULARY[current_category]
            if w not in used_words
        ]

        # Se ainda houver palavras → só pula a palavra
        if available_words:
            new_word = random.choice(available_words)
            used_words.append(new_word)

            update_game(room_id, {
                "secret_word": new_word,
                "used_words": used_words,
                "guessed_letters": [],
                "player_errors": {p: 0 for p in game_data["players"]},
                "player_status": {p: "ALIVE" for p in game_data["players"]},
                "status": "IN_PROGRESS",
                "current_turn": 0,
                "score": game_data["score"]
            })

            return self._success({
                "message": "New round started!",
                "category": current_category,
                "word_length": len(new_word),
                "masked_word": self._get_masked_word(
                    Game(secret_word=new_word, player_1=game_data["owner"])
                ),
                "players": game_data["players"],
                "player_errors": {p: 0 for p in game_data["players"]},
                "player_status": {p: "ALIVE" for p in game_data["players"]},
                "score": game_data["score"],
                "current_player": game_data["players"][0],
                "category_info": self.get_category_status(
                    current_category,
                    used_words
                )
            })

        # Se acabou a categoria → mostra seletor, não muda categoria sozinho
        update_game(room_id, {
            "status": "ROUND_FINISHED",
        })

        return self._success({
            "message": "Category completed! Choose another.",
            "finished_category": current_category,
            "score": game_data["score"],
            "game_status": "ROUND_FINISHED",
            "categories": self.get_all_categories_status(used_words)
        })


    def _next_turn(self, game, game_data):
        total_players = len(game.players)

        alive_players = [
            p for p in game.players if game.player_status[p] == "ALIVE"
        ]

        # NINGUÉM VIVO
        if len(alive_players) == 0:
            for p in game.players:
                game_data["score"][p] = max(0, game_data["score"].get(p, 0) - 1)

            return self.restart_round(game_data["room_id"], None)

        # próximo jogador vivo
        for _ in range(total_players):
            game.current_turn = (game.current_turn + 1) % total_players
            next_player = game.players[game.current_turn]

            if game.player_status.get(next_player) == "ALIVE":
                return
            
    def change_category(self, room_id: str, player: str, new_category: str):
        game_data = find_game(room_id)

        if not game_data:
            return self._not_found()

        if player != game_data["owner"]:
            return self._conflict("Only the owner can change category.")

        new_category = new_category.upper()
        if new_category not in VOCABULARY:
            return self._error("Invalid category.")

        used_words = game_data.get("used_words", [])
        available_words = [w for w in VOCABULARY[new_category] if w not in used_words]

        if not available_words:
            return self._error("No words available in this category.")

        new_word = random.choice(available_words)
        used_words.append(new_word)

        update_game(room_id, {
            "category": new_category,
            "secret_word": new_word,
            "used_words": used_words,
            "guessed_letters": [],
            "player_errors": {p: 0 for p in game_data["players"]},
            "player_status": {p: "ALIVE" for p in game_data["players"]},
            "status": "IN_PROGRESS",
            "current_turn": 0
        })

        return self._success({
            "message": f"Categoria alterada para {new_category}",
            "category": new_category,
            "masked_word": self._get_masked_word(
                Game(secret_word=new_word, player_1=game_data["owner"])
            ),
            "word_length": len(new_word),
            "players": game_data["players"],
            "player_errors": {p: 0 for p in game_data["players"]},
            "score": game_data.get("score", {}),
            "current_player": game_data["players"][0]
        })

    def get_all_categories_status(self, used_words):
        used_words = used_words or []

        result = []

        for category, words in VOCABULARY.items():
            total = len(words)
            used = len([w for w in used_words if w in words])
            remaining = total - used

            result.append({
                "category": category,
                "remaining": remaining,
                "total": total
            })

        return result
    
    def get_category_status(self, category, used_words):
        used_words = used_words or []

        if category not in VOCABULARY:
            return {
                "category": category,
                "total_words": 0,
                "used_words": 0,
                "remaining_words": 0
            }

        total = len(VOCABULARY[category])
        used = len([w for w in used_words if w in VOCABULARY[category]])
        remaining = total - used

        return {
            "category": category,
            "total_words": total,
            "used_words": used,
            "remaining_words": remaining
        }
    
