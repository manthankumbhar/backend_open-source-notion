from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/', methods=['POST', 'GET'])
def hello_world():
    return jsonify({'success': 'Hello, World!'}), 200    

if __name__ == '__main__':
    app.run(debug=True)