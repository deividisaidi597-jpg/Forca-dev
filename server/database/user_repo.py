from server.database.connection import DatabaseConnection
from server.models.user import User

db = DatabaseConnection.get_db()
collection = db["users"]

def create_user(user: User):
    collection.insert_one(user.to_dict())

def find_user_by_username(username: str):
    data = collection.find_one({"username": username})

    if data:
        data.pop("_id", None) 
        return User(**data)

    return None

def set_user_online(username, status: bool):
    collection.update_one(
        {"username": username},
        {"$set": {"is_online": status}}
    )
