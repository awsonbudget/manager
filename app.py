from __future__ import annotations
from enum import Enum
from flask import Flask, jsonify, request, Response
from flask_cors import CORS
import requests
import time
import multiprocessing
import atexit

app = Flask(__name__)
app.debug = True
CORS(app)

clusters = {"5551": "http://localhost:5551"}


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


@app.route("/cloud/", methods=["POST"])
def init():
    """management: 1. cloud init"""
    for name, url in clusters.items():
        res = requests.post(url + "/cloud").json()
        if res["status"] == False:
            return jsonify(
                status=False, msg=f"manager: cluster {name} failed to initialize"
            )

    return jsonify(status=True, msg="manager: all cluster initialized")


@app.route("/cloud/pod/", methods=["GET", "POST", "DELETE"])
def pod() -> Response:
    endpoint: str = "/cloud/pod"
    # TODO: remove the assumption of operating on one cluster
    pod_name = request.args.get("pod_name")

    """monitoring: 1. cloud pod ls"""
    if request.method == "GET":
        return requests.get(clusters["5551"] + endpoint).json()

    """management: 2. cloud pod register POD_NAME"""
    if request.method == "POST":
        if pod_name == None:
            return jsonify(status=False, msg=f"manager: you must specify a pod name")

        res = requests.post(
            clusters["5551"] + endpoint, params={"pod_name": pod_name}
        ).json()
        return jsonify(status=res["status"], msg="manager: " + res["msg"])

    """management: 3. cloud pod rm POD_NAME"""
    if request.method == "DELETE":
        if pod_name == None:
            return jsonify(status=False, msg=f"manager: you must specify a pod name")

        res = requests.delete(
            clusters["5551"] + endpoint, params={"pod_name": pod_name}
        ).json()
        return jsonify(status=res["status"], msg="manager: " + res["msg"])

    return jsonify(status=False, msg="manager: what the hell is happenning")


@app.route("/cloud/node/", methods=["GET", "POST", "DELETE"])
def node() -> Response:
    endpoint: str = "/cloud/node"
    node_name = request.args.get("node_name")
    pod_name = request.args.get("pod_name")

    """monitoring: 2. cloud node ls [RES_POD_ID]"""
    if request.method == "GET":
        res = requests.get(
            clusters["5551"] + endpoint, params={"pod_name": pod_name}
        ).json()
        if res["status"] == True:
            return jsonify(status=True, data=res["data"])
        return jsonify(status=False, msg="manager: " + res["msg"])

    """management: 4. cloud register NODE_NAME [POD_ID]"""
    if request.method == "POST":
        if node_name == None:
            return jsonify(status=False, msg=f"manager: you must specify a node name")

        res = requests.post(
            clusters["5551"] + endpoint,
            params={"node_name": node_name, "pod_name": pod_name},
        ).json()

        return jsonify(status=res['status'], msg="manager: "+res["msg"])

    """management: 5. cloud rm NODE_NAME"""
    if request.method == "DELETE":
        if node_name == None:
            return jsonify(status=False, msg=f"manager: you must specify a node name")
        
        res = requests.delete(
            clusters["5551"] + endpoint,
            params={"node_name": node_name},
        ).json()

        return jsonify(status=res['status'], msg="manager: "+res["msg"])

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
    app.run(port=5550)
