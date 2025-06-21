from flask import Flask, render_template, request
import uuid
import requests
from urllib.parse import urlparse
from google.cloud import storage
import os

app = Flask(__name__)

# Ensure your environment has the correct credentials set
# And the bucket name exists in your project
bucket_name = "simple-vuln-results"
client = storage.Client()
bucket = client.bucket(bucket_name)

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        target = request.form.get("target")
        if not target:
            return render_template("index.html", message="Please enter a valid target.")

        # Ensure target starts with http or https
        if not target.startswith("http://") and not target.startswith("https://"):
            target = "http://" + target

        result_id = str(uuid.uuid4())
        filename = f"{result_id}.txt"
        local_path = f"/tmp/{filename}"

        try:
            response = requests.get(target, timeout=5)
            result = f"Status Code: {response.status_code}\nHeaders:\n{response.headers}\n\n"
        except Exception as e:
            result = f"Error: {str(e)}\n"

        # Save result to file
        with open(local_path, "w") as f:
            f.write(f"Scan result for: {target}\n\n")
            f.write(result)

        # Upload file to bucket
        try:
            blob = bucket.blob(filename)
            blob.upload_from_filename(local_path)
            message = "Scan completed!"
        except Exception as upload_error:
            message = f"Upload failed: {str(upload_error)}"
            filename = None

        return render_template("index.html", message=message, result_file=filename)

    return render_template("index.html")
