# manager

## Setup

Make sure you have [Poetry](https://python-poetry.org/docs/) installed locally on your machine and you can find `poetry` on your path.
You can double check by using `poetry --version`

Within this directory, use `postry install` to install all dependencies.

Once that is done, use `poetry shell` to activate the environment.

In order to run the manager, you need 1 command:

- To start the FastAPI server: `uvicorn main:app --reload --port 5550`
