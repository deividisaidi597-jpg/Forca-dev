from server.database.connection import DatabaseConnection

db = DatabaseConnection.get_db()
collection = db["games"]

def create_game(data):
    collection.insert_one(data)

def find_game(room_id):
    return collection.find_one({"room_id": room_id})

def update_game(room_id, data):
    collection.update_one(
        {"room_id": room_id},
        {"$set": data}
    )