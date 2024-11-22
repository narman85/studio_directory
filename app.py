from flask import Flask

app = Flask(__name__)

@app.route('/')
def home():
    return 'Hello from Studio Directory! App is working!'

if __name__ == '__main__':
    app.run()
