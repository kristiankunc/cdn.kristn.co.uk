import random
import string
from waitress import serve
from flask import Flask, jsonify, request, redirect

app = Flask(__name__)

with open("./token.txt", "r") as f:
    token = f.read()

@app.route("/")
def index():
    return redirect("https://kristn.tech")

@app.route("/upload", methods=["POST"])
def upload():
    if "token" in request.form and "file" in request.files:
        user_token = request.headers["token"]
        file = request.files["file"]

        if user_token == token:
            file.save("./storage/" + ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(5)))
            return jsonify({"success": True})

        else:
            return jsonify({"message": "403 Forbidden, invalid token"}), 403
    else:
        return jsonify({"message": "403 Forbidden, token or file missing"}), 403

if __name__ == "__main__":
    port = 5000

    print(f"serving on port {port}")
    serve(app, port=port)