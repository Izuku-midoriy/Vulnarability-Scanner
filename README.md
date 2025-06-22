# 🔍 Simple Vulnerability Scanner

This is a lightweight web-based vulnerability scanner that allows users to enter a URL and scan it for basic HTTP header information. The scan results are saved to a Google Cloud Storage bucket and accessible through a clean web UI.

---

## 🚀 Features

- Simple web interface built with Flask
- Sends HTTP GET requests to check response status and headers
- Stores scan results in Google Cloud Storage
- Supports deployment to Google Cloud Run
- Secure and scalable 

---

## 🛠️ Technologies Used

- Python (Flask)
- Google Cloud Run
- Google Cloud Storage
- HTML/CSS for frontend

 --- 

## ⚒️ How it Works (Flow):

1. User enters a URL on the web page.
2. Flask verifies and ensures the URL begins with http:// or https://.
3. It parses the domain and adds a UTC timestamp for unique filenames.
4. Sends an HTTP GET request using the requests library.
5. Captures status code and headers, formats the result.
6. Saves the result as a text file in /tmp/.
7. Uploads the file to a GCS bucket named "simple-vuln-results".
8. Displays a confirmation message and filename to the user.

 ---   

## Note
It simply checks HTTP availability and headers for initial diagnostics.
