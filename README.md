# Equipe 4

```bash
projeto_forca_capstone/
│
├── server/                     # Backend: Gerencia conexões, regras de negócio e banco
│   ├── main.py                 # Ponto de entrada: inicia o servidor e a escuta do socket
│   │
│   ├── models/                 # (SRP/KISS) Entidades puras do domínio
│   │   ├── user.py             # Classe User (username, password_hash, is_online)
│   │   └── game.py             # Classe Game (palavra_secreta, letras_tentadas, status)
│   │
│   ├── database/               # (SRP) Apenas persistência e comunicação com MongoDB
│   │   ├── connection.py       # Inicia o cliente MongoClient e retorna o banco
│   │   └── user_repo.py        # Recebe/Retorna o Model User, faz insert_one e find_one
│   │
│   ├── services/               # (SRP) Regras de negócio puras
│   │   ├── auth_service.py     # Recebe dados da rede, faz o hash (bcrypt) e chama o repo
│   │   └── game_service.py     # Lógica da forca (sortear palavra, validar chute, turnos)
│   │
│   └── network/                # (SRP/DIP) Lida apenas com entrada/saída de dados via TCP/IP
│       ├── socket_server.py    # Aceita conexões e gerencia a lista de clientes online
│       └── event_bus.py        # Recebe o payload JSON e "roteia" para o service correto
│
├── client/                     # Frontend: O aplicativo que roda na máquina do jogador
│   ├── main.py                 # Ponto de entrada: inicia a primeira tela
│   │
│   ├── models/                 # Opcional: Representação local dos dados para a UI
│   │   └── game_state.py       # Guarda o estado atual (ex: a palavra mascarada) para a tela ler
│   │
│   ├── network/                # Isolamento da lógica de rede do cliente
│   │   └── socket_client.py    # Classe que conecta ao servidor e lida com send() e recv()
│   │
│   └── ui/                     # Telas isoladas para não criar "código espaguete"
│       ├── auth_screen.py      # Interface de Cadastro e Login (input de user/senha)
│       ├── lobby_screen.py     # Interface com a lista de usuários online e convites
│       └── game_screen.py      # Interface do jogo (desenho da forca e input de letras)
│
├── shared/                     # Código comum para os dois lados (Evita duplicação - DRY)
│   ├── config.py               # Variáveis globais de ambiente (HOST = '127.0.0.1', PORT = 5050)
│   └── events.py               # Constantes de roteamento (ex: ACTION_LOGIN = "LOGIN")
│
├── docs/                       # Documentação exigida pelo Capstone [cite: 67, 68]
│   └── diagramas/              # Diagramas de rede, prints do Wireshark, etc. [cite: 69, 70]
│
├── .env                        # Variáveis seguras (ex: DB_URI do MongoDB). NÃO VAI PARA O GIT!
├── .gitignore                  # Impede que o .env, a pasta __pycache__ e o venv subam pro GitLab
└── requirements.txt            # Dependências do Python (pymongo, bcrypt, python-dotenv)
```

## Instalação das Dependências

```bash
pip install -r requirements.txt
```
