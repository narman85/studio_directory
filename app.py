from flask import Flask, render_template, send_from_directory
import os

app = Flask(__name__, 
    static_folder='static',
    template_folder='templates'
)

@app.route('/')
def home():
    try:
        return render_template('index.html')
    except Exception as e:
        return f"Hello from Studio Directory! App is working! Error: {str(e)}"

@app.route('/static/<path:path>')
def serve_static(path):
    return send_from_directory('static', path)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
