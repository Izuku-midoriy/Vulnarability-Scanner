from flask import Flask, render_template, request
import uuid
import requests
from urllib.parse import urlparse
from google.cloud import storage
import os
from datetime import datetime

app = Flask(__name__)


bucket_name = "simple-vuln-results"
client = storage.Client()
bucket = client.bucket(bucket_name)

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        target = request.form.get("target")
        if not target:
            return render_template("index.html", message="Please enter a valid target.")

        # Check if target starts with http or https
        if not target.startswith("http://") and not target.startswith("https://"):
            target = "http://" + target

        # Extract domain for naming
        parsed_url = urlparse(target)
        domain = parsed_url.netloc.replace(":", "_").replace(".", "_")  # Avoid invalid characters

        # Timestamp to keep file unique
        timestamp = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")

        filename = f"{domain}_{timestamp}.txt"
        local_path = f"/tmp/{filename}"

        try:
            response = requests.get(target, timeout=5)
            result = f"Status Code: {response.status_code}\nHeaders:\n{response.headers}\n\n"
        except Exception as e:
            result = f"Error: {str(e)}\n"

        # Save result to local file
        with open(local_path, "w") as f:
            f.write(f"Scan result for: {target}\n\n")
            f.write(result)

        # Upload file to GCS
        try:
            blob = bucket.blob(filename)
            blob.upload_from_filename(local_path)
            message = "Scan completed!"
        except Exception as upload_error:
            message = f"Upload failed: {str(upload_error)}"
            filename = None

        return render_template("index.html", message=message, result_file=filename)

    return render_template("index.html")
