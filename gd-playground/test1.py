from distutils.log import debug
from flask import Flask

app = Flask(__name__)

@app.route("/")
def hello():
    return "X"

if __name__ == '__main__':
    app.run(debug=True)
