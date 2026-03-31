import bcrypt
from server.database.user_repo import create_user, find_user_by_username
from server.models.user import User

def register(username, password_hash):
    if find_user_by_username(username):
        return {"success": False, "message": "Usuário já existe"}

    hashed = bcrypt.hashpw(password_hash.encode(), bcrypt.gensalt())

    user = User(username, hashed.decode())

    create_user(user)

    return {"success": True}


def login(username, password_hash):
    user = find_user_by_username(username)

    if not user:
        return {"success": False, "message": "Usuário não encontrado"}

    if bcrypt.checkpw(password_hash.encode(), user.password.encode()):
        return {"success": True}

    return {"success": False, "message": "Senha inválida"}