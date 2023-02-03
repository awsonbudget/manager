from flask import Flask, jsonify, request, Response
from typing import Optional
from flask_cors import CORS
import requests

app = Flask(__name__)
app.debug = True
CORS(app)

CLUSTER = "http://localhost:5555"


@app.route("/")
def hello_world():
    r = requests.get(CLUSTER)
    return jsonify(r.json())


@app.route("/cloud/pod/<string:name>", methods=["POST", "DELETE"])
def pod(name: Optional[str] = None) -> Response:
    if request.method == "POST":
        assert name != None
        data = requests.post(CLUSTER + "/cloud/pod/" + name)
        return data.json()

    if request.method == "DELETE":
        assert name != None
        data = requests.delete(CLUSTER + "/cloud/pod/" + name)
        return data.json()

    return jsonify(status=False, msg="manager: what the hell is happenning")


if __name__ == "__main__":
    app.run(port=5556)
