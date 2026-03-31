from server.database.connection import DatabaseConnection
from server.models.user import User

db = DatabaseConnection.get_db()
collection = db["users"]

class UserRepository:
    def create_user(self, user: User):
        collection.insert_one(user.to_dict())
        return True

    def find_by_username(self, username: str):
        data = collection.find_one({"username": username})

        if data:
            data.pop("_id", None) 
            return User(**data)

        return None

    def set_user_online(self, username, status: bool):
        collection.update_one(
            {"username": username},
            {"$set": {"is_online": status}}
        )




