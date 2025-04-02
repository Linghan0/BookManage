# -*- coding: utf-8 -*-

from flask import Flask,jsonify
from flask_cors import CORS

from extention import db # type: ignore

app = Flask(__name__)


app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///books.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)


CORS(app,resources={r"/api/*": {"origins": "http://localhost:5173"}})    # 允许跨域

@app.route('/api/hello')
def hello():
    return jsonify({'message': 'Hello, World!'})

if __name__ == '__main__':
    app.run(debug=True)
