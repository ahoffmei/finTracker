from flask import Flask, jsonify
from flask_cors import CORS
from routes.cc_data import cc_bp 


app = Flask(__name__)
app.register_blueprint(cc_bp, url_prefix="/bofaCreditCardInfo")

if __name__ == "__main__":
    app.run(debug=True)
