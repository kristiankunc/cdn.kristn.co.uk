import random
import string
from flask import Flask, render_template, request, jsonify
from firebase_admin import credentials, initialize_app, storage

app = Flask(__name__)
cred = credentials.Certificate("./creds/kristn-cdn-firebase-adminsdk.json")
initialize_app(cred, {"storageBucket": "kristn-cdn.appspot.com"})

with open("./creds/token.txt", "r") as f:
    token = f.read()

@app.route("/upload", methods=["POST"])
def index():
    if "Authorization" in request.headers and "file" in request.files:
        user_token = request.headers["Authorization"]
        uploaded_file = request.files["file"]

        if user_token == token:
            
            filename = "".join(random.choice(string.ascii_lowercase + string.digits) for _ in range(5))

            bucket = storage.bucket()
            blob = bucket.blob(filename)
            blob.upload_from_file(uploaded_file, content_type=uploaded_file.content_type)
            
            blob.make_public()

            return jsonify({"success": True, "filename": filename, "file_url": blob.public_url, "url": f"https://cdn.kristn.co.uk/i/{filename}"})

        else:
            return jsonify({"message": "403 Forbidden, invalid token"}), 403
    else:
        return jsonify({"message": "400 Forbidden, token or file missing"}), 400

@app.route("/i/<filename>", methods=["GET"])
def image(filename):
    return render_template("embed.html", filename=filename, url=f"https://cdn.kristn.co.uk/i/{filename}", img_url=f"https://storage.googleapis.com/kristn-cdn.appspot.com/{filename}")

    
if __name__ == "__main__":
    from waitress import serve
    print(f"Running\nhttp://localhost:5000")
    serve(app, port=5000)