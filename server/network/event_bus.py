import json
from server.services.auth_service import login, register
from shared.events import ACTION_LOGIN, ACTION_REGISTER

def handle_event(data):
    payload = json.loads(data)

    action = payload.get("action")

    if action == ACTION_LOGIN:
        return login(payload["username"], payload["password"])

    if action == ACTION_REGISTER:
        return register(payload["username"], payload["password"])

    return {"error": "Ação desconhecida"}