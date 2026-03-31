class User:
    def __init__(self, username, password, is_online=False):
        self.username = username
        self.password = password
        self.is_online = is_online

    def to_dict(self):
        return {
            "username": self.username,
            "password": self.password,
            "is_online": self.is_online
        }