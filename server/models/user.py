class User:
    def __init__(self, username, password_hash, is_online=False):
        self.username = username
        self.password_hash = password_hash
        self.is_online = is_online

    def to_dict(self):
        return {
            "username": self.username,
            "password_hash": self.password_hash,
            "is_online": self.is_online
        }