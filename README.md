# manager

## Setup

Make sure you have [Poetry](https://python-poetry.org/docs/) installed locally on your machine and you can find `poetry` on your path.
You can double check by using `poetry --version`

Within this directory, use `postry install` to install all dependencies.

Once that is done, use `poetry shell` to activate the environment.

In order to run the manager, you need 1 command:

- To start the FastAPI server: `uvicorn src.main:app --reload --port 5000`

## McGill VM

If there is no ssl-certfile, then `mkcert 10.140.17.117`

- `uvicorn src.main:app --port 5000 --ssl-keyfile=./10.140.17.117-key.pem --ssl-certfile=./10.140.17.117.pem`


Monitor HAProxy

- `watch 'echo "show stat" | sudo socat stdio /var/run/haproxy/admin.sock | cut -d "," -f 1-2,5-10,34-36 | column -s, -t'`