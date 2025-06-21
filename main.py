from flask import Flask, render_template, request
import uuid
import requests
from google.cloud import storage

app = Flask(__name__)
client = storage.Client()
bucket = client.bucket("vulnarability-results")  # Change to your bucket name

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        target = request.form.get("target")
        if not target:
            return render_template("index.html", message="Please enter a valid target.")

        result_id = str(uuid.uuid4())
        filename = f"{result_id}.txt"
        local_path = f"/tmp/{filename}"

        try:
            response = requests.get(f"http://{target}", timeout=5)
            result = f"Status Code: {response.status_code}\nHeaders:\n{response.headers}\n\n"
        except Exception as e:
            result = f"Error: {str(e)}\n"

        with open(local_path, "w") as f:
            f.write(f"Scan result for: {target}\n\n")
            f.write(result)

        blob = bucket.blob(filename)
        blob.upload_from_filename(local_path)

        return render_template("index.html", message="Scan completed!", result_file=filename)

    return render_template("index.html")
