import os
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
from dotenv import load_dotenv

# Carrega .env (funciona local, no Render usa Environment Variables)
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
                # 🔥 pega variáveis de ambiente
                uri = os.getenv("DB_URI")
                db_name = os.getenv("DB_NAME")

                if not uri:
                    raise Exception("❌ DB_URI not found in environment variables")

                if not db_name:
                    raise Exception("❌ DB_NAME not found in environment variables")

                print("🔄 Attempting to connect to MongoDB...")

                # 🔥 conexão robusta (IMPORTANTE pro Render)
                cls._client = MongoClient(
                    uri,
                    serverSelectionTimeoutMS=5000,
                    connectTimeoutMS=10000,
                    socketTimeoutMS=10000
                )

                # 🔥 testa conexão
                cls._client.admin.command('ping')
                print("✅ Successfully connected to MongoDB!")

                # seleciona banco
                cls._db = cls._client[db_name]

                # 🔥 cria coleção se não existir (opcional)
                if "users" not in cls._db.list_collection_names():
                    cls._db.create_collection("users")
                    print(f"📦 Database '{db_name}' and 'users' collection initialized!")

            except ConnectionFailure as e:
                print(f"❌ Fatal error connecting to MongoDB: {e}")
                raise e

            except Exception as e:
                print(f"❌ Configuration error: {e}")
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