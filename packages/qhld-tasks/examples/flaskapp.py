from flask import Flask
app = Flask(__name__)
import tipi_tasks

@app.route("/")
def hello():
    tipi_tasks.init()
    tipi_tasks.test_task.apply_async((3, 2))
    return "Hello World!"
