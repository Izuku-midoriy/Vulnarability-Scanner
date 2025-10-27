from flask import Flask, render_template, request
import uuid
import requests
from urllib.parse import urlparse
from google.cloud import storage
import os
from datetime import datetime

app = Flask(__name__)

# Google Cloud Storage bucket name
bucket_name = "simple-vuln-results"

# Initialize the GCS client
client = storage.Client()
bucket = client.bucket(bucket_name)


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        target = request.form.get("target")
        if not target:
            return render_template("index.html", message="⚠️ Please enter a valid target.")

        # Ensure URL starts with http/https
        if not target.startswith("http://") and not target.startswith("https://"):
            target = "http://" + target

        # Extract domain for file naming
        parsed_url = urlparse(target)
        domain = parsed_url.netloc.replace(":", "_").replace(".", "_")

        # Timestamp for uniqueness
        timestamp = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")

        filename = f"{domain}_{timestamp}.txt"
        local_path = f"/tmp/{filename}"

        try:
            # Perform a simple HTTP request (basic scan)
            response = requests.get(target, timeout=5)
            result = f"Status Code: {response.status_code}\nHeaders:\n{response.headers}\n\n"
        except Exception as e:
            result = f"Error: {str(e)}\n"

        # Write results to a temp file
        with open(local_path, "w") as f:
            f.write(f"Scan result for: {target}\n\n")
            f.write(result)

        # Upload results to Cloud Storage
        try:
            blob = bucket.blob(filename)
            blob.upload_from_filename(local_path)
            message = "✅ Scan completed successfully!"
        except Exception as upload_error:
            message = f"❌ Upload failed: {str(upload_error)}"
            filename = None

        # Clean up temporary file
        if os.path.exists(local_path):
            os.remove(local_path)

        return render_template("index.html", message=message, result_file=filename)

    # GET request
    return render_template("index.html")


# ---- ✅ Cloud Run Entry Point ----
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
