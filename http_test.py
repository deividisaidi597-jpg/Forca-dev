from flask import Flask, request, jsonify
from server.services.auth_service import AuthService

app = Flask(__name__)
auth_service = AuthService()

@app.route("/register", methods=["POST"])
def register_route():
    data = request.json
    result = auth_service.register(data["username"], data["password"])
    return jsonify(result)


@app.route("/login", methods=["POST"])
def login_route():
    data = request.json
    result = auth_service.login(data["username"], data["password"])
    return jsonify(result)


if __name__ == "__main__":
    app.run(port=5000, debug=True)