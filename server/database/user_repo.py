from server.database.connection import DatabaseConnection
from server.models.user import User

class UserRepository:
    def __init__(self):
        self.db = DatabaseConnection.get_db()
        self.collection = self.db["users"]

    def create_user(self, user: User) -> bool:
        """
        Inserts a new user into the database.
        Returns True if successful, False if the username already exists.
        """
        if self.find_by_username(user.username):
            return False 
        
        user_doc = {
            "username": user.username,
            "password_hash": user.password_hash,
            "is_online": user.is_online,
            "games_won": user.games_won,
            "games_played": user.games_played
        }
        
        result = self.collection.insert_one(user_doc)
        return result.inserted_id is not None

    def find_by_username(self, username: str) -> User | None:
        """
        Searches for a user by username.
        """
        user_doc = self.collection.find_one({"username": username})
        
        if user_doc:
            return User(
                username=user_doc["username"],
                password_hash=user_doc["password_hash"],
                is_online=user_doc.get("is_online", False),
                games_won=user_doc.get("games_won", 0),
                games_played=user_doc.get("games_played", 0)
            )
        return None