import bcrypt
from server.database.user_repo import UserRepository
from server.models.user import User

class AuthService:
    def __init__(self):
        self.user_repo = UserRepository()

    def register(self, username, password):
        if self.user_repo.find_by_username(username):
            return {"status": "error", "message": "Username is already taken."}

        salt = bcrypt.gensalt()
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

        new_user = User(username=username, password_hash=hashed_password)
        success = self.user_repo.create_user(new_user)

        if success:
            return {"status": "success", "message": "User registered successfully!"}
        return {"status": "error", "message": "Failed to save user to the database."}

    def login(self, username, password):
        user = self.user_repo.find_by_username(username)
        
        if not user:
            return {"status": "error", "message": "User not found."}

        if bcrypt.checkpw(password.encode('utf-8'), user.password_hash.encode('utf-8')):
            return {"status": "success", "message": f"Welcome, {username}!", "username": username}
        
        return {"status": "error", "message": "Incorrect password."}

# Standalone functions for easy importing
_auth_service = AuthService()

def register(username, password):
    return _auth_service.register(username, password)

def login(username, password):
    return _auth_service.login(username, password)
