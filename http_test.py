from flask import Flask, request, jsonify
from server.services.auth_service import AuthService

app = Flask(__name__)
auth_service = AuthService()


@app.route("/register", methods=["POST"])
def register_route():
    data = request.json
    result = auth_service.register(data["username"], data["password"])

    if result["status"] == "success":
        return jsonify(result), 201  # CREATED

    if result["message"] == "Username is already taken.":
        return jsonify(result), 409  # CONFLICT

    return jsonify(result), 500


@app.route("/login", methods=["POST"])
def login_route():
    data = request.json
    result = auth_service.login(data["username"], data["password"])

    if result["status"] == "success":
        return jsonify(result), 200

    if result["message"] == "User not found.":
        return jsonify(result), 404

    if result["message"] == "Incorrect password.":
        return jsonify(result), 401

    return jsonify(result), 500


if __name__ == "__main__":
    app.run(port=5000, debug=True)