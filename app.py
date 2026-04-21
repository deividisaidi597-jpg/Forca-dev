import os
from flask import Flask, request, render_template
from flask_socketio import SocketIO
from server.services.auth_service import AuthService
from server.services.game_service import GameService
from server.utils.jwt_handler import decode_token

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

app = Flask(
    __name__,
    template_folder=os.path.join(BASE_DIR, "client/templates"),
    static_folder=os.path.join(BASE_DIR, "client/static")
)
socketio = SocketIO(app)
auth_service = AuthService()
game_service = GameService()

# =========================
# 🔐 AUTH
# =========================
def get_current_user(request):
    auth_header = request.headers.get("Authorization")

    if not auth_header or not auth_header.startswith("Bearer "):
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
    response, status = auth_service.register(
        data["username"],
        data["password"]
    )
    return response, status


@app.route("/login", methods=["POST"])
def login_route():
    data = request.json
    response, status = auth_service.login(
        data["username"],
        data["password"]
    )
    return response, status


# =========================
# 🎮 GAME (HTTP)
# =========================
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

    return response, status


@app.route("/game/<room_id>", methods=["GET"])
def get_game(room_id):
    from server.database.game_repo import find_game
    from server.models.game import Game

    game = find_game(room_id)

    if not game:
        return {"message": "Game not found"}, 404

    # 🔧 ajustes para frontend
    game["_id"] = str(game["_id"])
    game["word_length"] = len(game["secret_word"])
    game["owner"] = game.get("owner")
    game["game_status"] = game["status"]

    # jogador atual
    if game.get("current_turn") is not None:
        game["current_player"] = game["players"][game["current_turn"]]
    else:
        game["current_player"] = None

    # categorias restantes
    game["categories_status"] = game_service.get_all_categories_status(
        game.get("used_words", [])
    )

    # palavra mascarada
    temp_game = Game(
        secret_word=game["secret_word"],
        player_1=game["owner"]
    )
    temp_game.guessed_letters = game.get("guessed_letters", [])

    game["masked_word"] = game_service._get_masked_word(temp_game)

    # palavra correta quando termina
    if game["status"] == "ROUND_FINISHED":
        game["correct_word"] = game["secret_word"]

    return game, 200


# =========================
# 🎮 GAME ACTIONS (HTTP)
# =========================
@app.route("/game/start", methods=["POST"])
def start_game():
    player = get_current_user(request)
    if not player:
        return {"status": "error", "message": "Unauthorized"}, 401

    data = request.json

    response, status = game_service.start_game(
        data["room_id"],
        player
    )

    return response, status


@app.route("/game/guess-letter", methods=["POST"])
def guess_letter():
    player = get_current_user(request)
    if not player:
        return {"status": "error", "message": "Unauthorized"}, 401

    data = request.json

    response, status = game_service.guess_letter(
        data["room_id"],
        player,
        data["letter"]
    )

    return response, status


@app.route("/game/guess-word", methods=["POST"])
def guess_word():
    player = get_current_user(request)
    if not player:
        return {"status": "error", "message": "Unauthorized"}, 401

    data = request.json

    response, status = game_service.guess_word(
        data["room_id"],
        player,
        data["word"]
    )

    return response, status


@app.route("/game/restart", methods=["POST"])
def restart_game():
    player = get_current_user(request)
    if not player:
        return {"status": "error", "message": "Unauthorized"}, 401

    data = request.json

    response, status = game_service.restart_round(
        data["room_id"],
        player
    )

    return response, status


@app.route("/game/change-category", methods=["POST"])
def change_category():
    player = get_current_user(request)
    if not player:
        return {"status": "error", "message": "Unauthorized"}, 401

    data = request.json

    response, status = game_service.change_category(
        data["room_id"],
        player,
        data["category"]
    )

    return response, status


@app.route("/categories", methods=["GET"])
def categories():
    return {"categories": game_service.get_categories()}, 200


@app.route("/games", methods=["GET"])
def list_games():
    from server.database.game_repo import list_games
    games = list_games()
    return {"games": games}, 200


# =========================
# 📄 PAGES
# =========================
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


@app.route("/winner")
def winner_page():
    return render_template("winner.html")


# =========================
# 🚀 RUN
# =========================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    socketio.run(app, host="0.0.0.0", port=port)
