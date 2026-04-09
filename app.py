from flask import Flask, request, render_template
from flask_socketio import SocketIO, emit, join_room, leave_room

from server.services.auth_service import AuthService
from server.services.game_service import GameService
from server.utils.jwt_handler import decode_token

app = Flask(
    __name__,
    template_folder="client/templates",
    static_folder="client/static"
)

# SOCKET.IO
socketio = SocketIO(app, cors_allowed_origins="*", async_mode="threading")

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
    response, status = auth_service.register(data["username"], data["password"])
    return response, status


@app.route("/login", methods=["POST"])
def login_route():
    data = request.json
    response, status = auth_service.login(data["username"], data["password"])
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

    game = find_game(room_id)

    if not game:
        return {"message": "Game not found"}, 404

    game["_id"] = str(game["_id"])
    game["word_length"] = len(game["secret_word"])
    game["owner"] = game.get("owner")
    game["game_status"] = game["status"]

    if game.get("current_turn") is not None:
        game["current_player"] = game["players"][game["current_turn"]]
    else:
        game["current_player"] = None
    
    game["categories_status"] = game_service.get_all_categories_status(
        game.get("used_words", [])
    )

    from server.models.game import Game

    temp_game = Game(
        secret_word=game["secret_word"],
        player_1=game["owner"]
    )
    temp_game.guessed_letters = game.get("guessed_letters", [])

    game["masked_word"] = game_service._get_masked_word(temp_game)

    if game["status"] == "ROUND_FINISHED":
        game["correct_word"] = game["secret_word"]

    return game, 200


# =========================
# SOCKET EVENTS
# =========================

# 👥 entrar na sala
@socketio.on("join_room")
def handle_join(data):
    room_id = data["room_id"]
    username = data["username"]

    join_room(room_id)

    emit("player_joined", {
        "message": f"{username} joined the room",
        "player": username
    }, room=room_id)


# sair da sala
@socketio.on("leave_room")
def handle_leave(data):
    room_id = data["room_id"]
    username = data["username"]

    leave_room(room_id)

    emit("player_left", {
        "message": f"{username} left the room"
    }, room=room_id)


# iniciar jogo
@socketio.on("start_game")
def handle_start(data):
    room_id = data["room_id"]
    player = data["player"]

    response, status = game_service.start_game(room_id, player)

    emit("game_started", response, room=room_id)


# chute de letra
@socketio.on("guess_letter")
def handle_guess_letter(data):
    room_id = data["room_id"]
    player = data["player"]
    letter = data["letter"]

    response, status = game_service.guess_letter(room_id, player, letter)

    # ERRO → só jogador
    if response.get("status") == "error":
        emit("private_message", {
            "message": response.get("message")
        }, to=request.sid)
        return

    # FEEDBACK → só jogador
    if response.get("message"):
        emit("private_message", {
            "message": response.get("message")
        }, to=request.sid)

    # EVENTO GLOBAL
    global_message = f"{player} guessed '{letter.upper()}'"

    # se rodada acabou → muda mensagem
    if response.get("game_status") == "ROUND_FINISHED":
        global_message = f"🎉 Round finished!"

    emit("game_update", {
        **response,
        "message": global_message
    }, room=room_id)


# chute de palavra
@socketio.on("guess_word")
def handle_guess_word(data):
    room_id = data["room_id"]
    player = data["player"]
    word = data["word"]

    response, status = game_service.guess_word(room_id, player, word)

    # ERRO → só jogador
    if response.get("status") == "error":
        emit("private_message", {
            "message": response.get("message")
        }, to=request.sid)
        return

    # FEEDBACK → só jogador
    if response.get("message"):
        emit("private_message", {
            "message": response.get("message")
        }, to=request.sid)

    # EVENTO GLOBAL
    global_message = f"{player} guessed '{word.upper()}'"

    # se rodada acabou → muda mensagem
    if response.get("game_status") == "ROUND_FINISHED":
        global_message = f"🎉 Round finished!"

    emit("game_update", {
        **response,
        "message": global_message
    }, room=room_id)


# próxima rodada
@socketio.on("restart_game")
def handle_restart(data):
    room_id = data["room_id"]
    player = data["player"]

    response, status = game_service.restart_round(room_id, player)

    message = "New round started!"

    if response.get("finished_category"):
        message = "🏆 Category finished!"

    emit("round_restart", {
        **response,
        "message": message
    }, room=room_id)


# mudar categoria
@socketio.on("change_category")
def handle_change_category(data):
    room_id = data["room_id"]
    player = data["player"]
    category = data["category"]

    response, status = game_service.change_category(room_id, player, category)

    emit("category_changed", response, room=room_id)

@app.route("/categories", methods=["GET"])
def categories():
    return {"categories": game_service.get_categories()}, 200


@app.route("/games", methods=["GET"])
def list_games():
    from server.database.game_repo import list_games
    games = list_games()
    return {"games": games}, 200
# =========================
# PAGES
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


# =========================
# RUN
# =========================
if __name__ == "__main__":
    socketio.run(app, port=5000, debug=True)