## 简单实例

from flask import Flask,jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)    # 允许跨域

@app.route('/api/hello')
def hello():
    return jsonify({'message': 'Hello, World!'})

if __name__ == '__main__':
    app.run(debug=True)
