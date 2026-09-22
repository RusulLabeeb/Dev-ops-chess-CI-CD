from flask import Flask, request, abort
import hashlib
import hmac
import subprocess

app = Flask(__name__)

SECRET = b"YOUR_SECRET"


@app.post("/webhook")
def webhook():
    signature = request.headers.get("X-Hub-Signature-256", "")

    if not signature.startswith("sha256="):
        abort(401)

    body = request.get_data()

    expected = "sha256=" + hmac.new(
        SECRET,
        body,
        hashlib.sha256
    ).hexdigest()

    if not hmac.compare_digest(signature, expected):
        abort(401)

    subprocess.run(
        ["/home/student/chess/deploy.simple"],
        cwd="/home/student/chess",
        check=True
    )

    return "Deployment triggered\n", 200


app.run(host="127.0.0.1", port=5000)