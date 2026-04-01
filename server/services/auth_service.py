import bcrypt
from server.database.user_repo import UserRepository
from server.models.user import User
from server.utils.jwt_handler import generate_token

class AuthService:
    
    def _success(self, data):
        return {**data}, 200

    def _created(self, data):
        return {"status": "success", **data}, 201

    def _error(self, message, code=400):
        return {"status": "error", "message": message}, code

    def _conflict(self, message):
        return {"status": "error", "message": message}, 409

    def _not_found(self):
        return {"status": "error", "message": "User not found."}, 404
    

    def __init__(self):
        self.user_repo = UserRepository()

    def register(self, username, password):
        if self.user_repo.find_by_username(username):
            return self._conflict("Username is already taken.")

        salt = bcrypt.gensalt()
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

        new_user = User(username=username, password_hash=hashed_password)
        success = self.user_repo.create_user(new_user)

        if success:
            return self._created({
                "message": "User registered successfully!"
            })
        return self._error("Failed to save user to the database.",500)

    def login(self, username, password):
        user = self.user_repo.find_by_username(username)
        
        if not user:
            return self._not_found()

        if bcrypt.checkpw(password.encode(), user.password_hash.encode()):
            token = generate_token(username)

            return self._success({
                "message": "Login successful",
                "token": token
            })

        return {"status": "error", "message": "Invalid credentials"}, 401
