import os
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
from dotenv import load_dotenv

# Carrega as variáveis de ambiente do arquivo .env para a memória
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
                
                # Inicia o cliente do MongoDB
                cls._client = MongoClient(uri)

                # Dispara um 'ping' para confirmar se o servidor do banco está mesmo online
                cls._client.admin.command('ping')
                print("✅ Successfully connected to MongoDB!")

                # Seleciona o banco de dados
                cls._db = cls._client[db_name]

                # TRUQUE PARA FORÇAR A CRIAÇÃO DO BANCO AO LIGAR O PROJETO
                # Verifica se a coleção 'users' já existe. Se não, cria ela vazia.
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