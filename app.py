from flask import Flask, jsonify
import requests

app = Flask(__name__)
app.debug = True


@app.route("/")
def hello_world():
    r = requests.get("http://localhost:5555")
    return jsonify(r.json())


if __name__ == "__main__":
    app.run(port=5556)
