from flask import Flask

app = Flask(__name__)

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def catch_all(path):
    return {
        'path': path or '/',
        'message': 'Hello from Flask on Vercel!'
    }

# Vercel requires a handler function
def handler(event, context):
    return app
