def handle_message(self, client_socket, payload: dict) -> dict:
        action = payload.get("action")
        data = payload.get("data", {})

        if action == "REGISTER":
            return self.auth_service.register(data.get("username"), data.get("password"))
            
        elif action == "LOGIN":
            return self.auth_service.login(data.get("username"), data.get("password"))


        elif action == "CREATE_GAME":
            return self.game_service.create_game(
                room_id=data.get("room_id"),
                player_1=data.get("player_1"),
                category=data.get("category")
            )

        else:
            return {"status": "error", "message": "Unknown action."}