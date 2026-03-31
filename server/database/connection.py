import os
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
from dotenv import load_dotenv

load_dotenv()

class DatabaseConnection:
    _client = None
    _db = None

    @classmethod
    def connect(cls):
        """
        Establishes connection with MongoDB using the Singleton Pattern.
        """
        if cls._client is None:
            try:
                uri = os.getenv("DB_URI")
                db_name = os.getenv("DB_NAME")

                print("🔄 Attempting to connect to MongoDB...")
                
                cls._client = MongoClient(uri)
                cls._client.admin.command('ping')
                print("✅ Successfully connected to MongoDB!")

                cls._db = cls._client[db_name]

                # Initialize database and 'users' collection if they don't exist
                if "users" not in cls._db.list_collection_names():
                    cls._db.create_collection("users")
                    print(f"📦 Database '{db_name}' and 'users' collection initialized!")

            except ConnectionFailure as e:
                print(f"❌ Fatal error connecting to MongoDB: {e}")
                raise e

    @classmethod
    def get_db(cls):
        """
        Returns the database instance to be used by Repositories.
        """
        if cls._db is None:
            cls.connect()
        return cls._db

if __name__ == "__main__":
    DatabaseConnection.connect()