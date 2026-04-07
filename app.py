from flask import Flask, request
from server.services.auth_service import AuthService
from server.services.game_service import GameService
from server.utils.jwt_handler import decode_token
from flask import render_template

app = Flask(
    __name__,
    template_folder="client/templates",
    static_folder="client/static"
)

auth_service = AuthService()
game_service = GameService()


def get_current_user(request):
    auth_header = request.headers.get("Authorization")

    if not auth_header.startswith("Bearer "):
        return None

    try:
        token = auth_header.split(" ")[1]
        username = decode_token(token)
        return username
    except Exception:
        return None
    
@app.route("/register", methods=["POST"])
def register_route():
    data = request.json
    response, status = auth_service.register(data["username"], data["password"])

    return response, status


@app.route("/login", methods=["POST"])
def login_route():
    data = request.json
    response, status = auth_service.login(data["username"], data["password"])

    return response, status

@app.route("/game/create", methods=["POST"])
def create_game():
    player = get_current_user(request)

    if not player:
        return {"status": "error", "message": "Unauthorized"}, 401
    
    data = request.json

    response, status = game_service.create_game(
        player_1=player,
        category=data["category"]
    )

    return response, status

@app.route("/game/join", methods=["POST"])
def join_game():
    player = get_current_user(request)

    if not player:
        return {"status": "error", "message": "Unauthorized"}, 401

    data = request.json

    response, status = game_service.join_game(
        room_id=data["room_id"],
        player=player
    )

    return  response, status

@app.route("/game/start", methods=["POST"])
def start_game():
    player = get_current_user(request)

    if not player:
        return {"status": "error", "message": "Unauthorized"}, 401

    data = request.json

    response, status = game_service.start_game(
        room_id=data["room_id"],
        player=player
    )

    return response, status


@app.route("/game/restart", methods=["POST"])
def restart_game():
    player = get_current_user(request)

    if not player:
        return {"message": "Unauthorized"}, 401

    data = request.json

    response, status = game_service.restart_round(
        room_id=data["room_id"],
        player=player
    )

    return response, status


@app.route("/game/guess", methods=["POST"])
def guess_letter():
    player = get_current_user(request)

    if not player:
        return {"status": "error", "message": "Unauthorized"}, 401

    data = request.json

    response, status = game_service.guess_letter(
        room_id=data["room_id"],
        player=player,
        letter=data["letter"]
    )

    return response, status


@app.route("/game/guess-word", methods=["POST"])
def guess_word():
    player = get_current_user(request)

    if not player:
        return {"status": "error", "message": "Unauthorized"}, 401
    
    data = request.json

    response, status = game_service.guess_word(
        room_id=data["room_id"],
        player=player,
        word=data["word"]
    )

    return response, status


@app.route("/game/change-category", methods=["POST"])
def change_category():
    player = get_current_user(request)

    if not player:
        return {"status": "error", "message": "Unauthorized"}, 401

    data = request.json

    response, status = game_service.change_category(
        room_id=data["room_id"],
        player=player,
        new_category=data["category"]
    )

    return response, status


@app.route("/games", methods=["GET"])
def list_games():
    from server.database.game_repo import list_games

    games = list_games()

    return {"games": games}, 200


@app.route("/categories", methods=["GET"])
def categories():
    return {"categories": game_service.get_categories()}, 200


@app.route("/game/<room_id>", methods=["GET"])
def get_game(room_id):
    from server.database.game_repo import find_game

    game = find_game(room_id)

    if not game:
        return {"message": "Game not found"}, 404

    # CONVERTE ObjectId
    game["_id"] = str(game["_id"])
    
    game["categories_status"] = game_service.get_all_categories_status(
        game.get("used_words", [])
    )
    return game, 200


@app.route("/")
def login_page():
    return render_template("login.html")

@app.route("/register-page")
def register_page():
    return render_template("register.html")

@app.route("/dashboard")
def dashboard_page():
    return render_template("dashboard.html")

@app.route("/room")
def room_page():
    return render_template("room.html")

@app.route("/game")
def game_page():
    return render_template("game.html")



if __name__ == "__main__":
    app.run(port=5000, debug=True)