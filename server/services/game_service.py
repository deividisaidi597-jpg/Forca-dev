import random

WORDS = ["python", "mongodb", "socket", "backend"]

def create_game():
    word = random.choice(WORDS)

    return {
        "word": word,
        "guessed": [],
        "errors": 0,
        "status": "PLAYING"
    }

def guess_letter(game, letter):
    if letter in game["guessed"]:
        return game

    game["guessed"].append(letter)

    if letter not in game["word"]:
        game["errors"] += 1

    if all(l in game["guessed"] for l in game["word"]):
        game["status"] = "WIN"

    if game["errors"] >= 6:
        game["status"] = "LOSE"

    return game