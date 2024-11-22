from flask import Flask, Response
import json

app = Flask(__name__)

@app.route('/')
def home():
    return Response(
        json.dumps({"message": "Hello from Flask!"}),
        mimetype='application/json'
    )

if __name__ == '__main__':
    app.run()
