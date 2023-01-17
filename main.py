import random
import string
from flask import Flask, render_template, request, jsonify, redirect
from firebase_admin import credentials, initialize_app, storage
from datetime import datetime

app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False
cred = credentials.Certificate("./creds/kristn-cdn-firebase-adminsdk.json")
initialize_app(cred, {"storageBucket": "kristn-cdn.appspot.com"})
last_ran = 0

with open("./creds/token.txt", "r") as f:
    token = f.read()


def genFilename():
    filename = "".join(random.choice(
        string.ascii_lowercase + string.digits) for _ in range(5))

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
        "total_size": f"{sum([blob.size for blob in bucket.list_blobs()]) / 1024 / 1024:.2f} MB",
        "upload_img": "https://cdn.kristn.co.uk/upload",
        "upload_file": "https://cdn.kristn.co.uk/file/upload",
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
            blob.upload_from_file(
                uploaded_file, content_type=uploaded_file.content_type)

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


@app.route("/file/<filename>", methods=["GET"])
def file(filename):
    bucket = storage.bucket()
    blob = bucket.get_blob(filename)

    if blob:
        return redirect(f"https://storage.googleapis.com/kristn-cdn.appspot.com/{filename}")
    else:
        return jsonify({"message": "404 Not Found, file not found"}), 404


@app.route("/file/upload", methods=["GET", "POST"])
def file_upload():
    if request.method == "GET":
        return render_template("file-upload.html")

    elif request.method == "POST":
        if request.form["password"] == token:
            uploaded_file = request.files["file"]

            bucket = storage.bucket()
            blob = bucket.blob(uploaded_file.filename)
            blob.upload_from_file(
                uploaded_file, content_type=uploaded_file.content_type)

            blob.make_public()

            return jsonify({"success": True, "filename": uploaded_file.filename, "file_url": blob.public_url, "url": f"https://cdn.kristn.co.uk/file/{uploaded_file.filename}"})
        else:
            return jsonify({"message": "403 Forbidden, invalid token"}), 403


@app.after_request
def after_request_callback(response):
    if last_ran + 86400 < datetime.datetime.now():
        last_ran = datetime.datetime.time()
        bucket = storage.bucket()
        for blob in bucket.list_blobs():
            # check if blob is image
            if blob.content_type.startswith("image/") or blob.content_type.startswith("application/octet-stream"):
                if blob.time_created + datetime.timedelta(days=14) < datetime.datetime.now():
                    blob.delete()


if __name__ == "__main__":
    from waitress import serve
    print(f"Running\nhttp://localhost:5000")
    serve(app, port=5000)
