from __future__ import annotations
from enum import Enum
from flask import Flask, jsonify, request, Response
from typing import Optional
from flask_cors import CORS
import requests
import time
import multiprocessing
import atexit

app = Flask(__name__)
app.debug = True
CORS(app)

CLUSTER = "http://localhost:5555"


class Status(str, Enum):
    IDLE = "idle"
    RUNNING = "running"
    REGISTERED = "registered"
    COMPLETED = "completed"
    ABORTED = "aborted"
    FAILED = "failed"


class Job(object):
    def __init__(self, name: str, id: str, status: Status = Status.REGISTERED):
        self.name: str = name
        self.id: str = id
        self.status: Status = status


class Manager(object):
    def __init__(self):
        self.queue: list[Job] = list()


manager = Manager()


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


process = None


def worker():
    while True:
        time.sleep(3)
        if manager.queue:
            job = manager.queue.pop()
            print(job.id)
        else:
            print("waiting for jobs")


def start_worker():
    global process
    process = multiprocessing.Process(target=worker)
    process.start()


def stop_worker():
    global process
    if process != None:
        process.terminate()
    else:
        print("worker is not running")


if __name__ == "__main__":
    start_worker()
    atexit.register(stop_worker)
    app.run(port=5556)
