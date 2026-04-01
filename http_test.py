from flask import Flask, request
from server.services.auth_service import AuthService
from server.services.game_service import GameService
from server.utils.jwt_handler import decode_token

app = Flask(__name__)
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
if __name__ == "__main__":
    app.run(port=5000, debug=True)