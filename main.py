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
            return render_template("index.html", message="⚠️ Please enter a valid target.")

        if not target.startswith("http://") and not target.startswith("https://"):
            target = "http://" + target

        parsed_url = urlparse(target)
        domain = parsed_url.netloc.replace(":", "_").replace(".", "_")
        timestamp = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
        filename = f"{domain}_{timestamp}.txt"
        local_path = f"/tmp/{filename}"

        try:
            response = requests.get(target, timeout=5)
            result = f"Status Code: {response.status_code}\nHeaders:\n{response.headers}\n\n"
        except Exception as e:
            result = f"Error: {str(e)}\n"

        with open(local_path, "w") as f:
            f.write(f"Scan result for: {target}\n\n{result}")

        try:
            blob = bucket.blob(filename)
            blob.upload_from_filename(local_path)
            message = "✅ Scan completed successfully!"
        except Exception as upload_error:
            message = f"❌ Upload failed: {upload_error}"
            filename = None

        if os.path.exists(local_path):
            os.remove(local_path)

        return render_template("index.html", message=message, result_file=filename)

    return render_template("index.html")

# ✅ CRUCIAL for Cloud Run
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
