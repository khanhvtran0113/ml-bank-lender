from flask import Flask
from flask_cors import CORS

app = Flask(__name__)
CORS(app, origins=["http://localhost:3000"])

@app.route('/')
def home():
    return "Hello, Flask!"

if __name__ == '__main__':
    app.run()
