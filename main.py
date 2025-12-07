from flask import Flask, send_from_directory

app = Flask(__name__, static_folder=".", static_url_path="")

@app.route("/")
def home():
    # This will serve your Food.html when someone opens the site
    return send_from_directory(".", "Food.html")

# (Optional) If later you add images, CSS, JS in this folder,
# they will also be served automatically because of static_folder above.

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
