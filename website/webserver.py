from flask import Flask, request, send_from_directory

# set the project root directory as the static folder, you can set others.
app = Flask(__name__, static_url_path='/')


@app.route('/')
def send_js():
        return send_from_directory("/home/ubuntu/ABCD/merged", "index.html")


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=80)
