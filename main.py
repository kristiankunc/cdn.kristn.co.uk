import random
import string
from flask import Flask, render_template, request, jsonify, redirect
from firebase_admin import credentials, initialize_app, storage

app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False
cred = credentials.Certificate("./creds/kristn-cdn-firebase-adminsdk.json")
initialize_app(cred, {"storageBucket": "kristn-cdn.appspot.com"})

with open("./creds/token.txt", "r") as f:
    token = f.read()

def genFilename():
    filename = "".join(random.choice(string.ascii_lowercase + string.digits) for _ in range(5))

    bucket = storage.bucket()
    blob = bucket.blob(filename)

    if not blob.exists():
        return filename
    else:
        return genFilename()

@app.route("/", methods=["GET"])
def index():
    bucket = storage.bucket()

    return jsonify({
        "status": "ok",
        "total_files": len(list(bucket.list_blobs())),
    })

@app.route("/upload", methods=["POST"])
def upload():
    if "Authorization" in request.headers and "file" in request.files:
        user_token = request.headers["Authorization"]
        uploaded_file = request.files["file"]

        if user_token == token:
            
            filename = genFilename()

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
    bucket = storage.bucket()
    blob = bucket.get_blob(filename)

    if blob:
        kb = blob.size / 1024
        mb = kb / 1024

        if mb < 0.1:
            size = f"{kb:.2f} KB"
        else:
            size = f"{mb:.2f} MB"

        metadata = {
            "filename": blob.name,
            "size": size,
            "content_type": blob.content_type,
            "time_created": blob.time_created.strftime("%d.%m.%Y %H:%M:%S"),
        }

        return render_template("preview.html", metadata=metadata)
    else:
        return redirect("https://shattereddisk.github.io/rickroll/rickroll.mp4")

    
if __name__ == "__main__":
    from waitress import serve
    print(f"Running\nhttp://localhost:5000")
    serve(app, port=5000)