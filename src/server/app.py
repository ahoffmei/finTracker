from flask import Flask, jsonify

app = Flask(__name__)


@app.route('/api/expenseByStore')
def expenseByStore(): 
    # Dummy data for now
    data = {
        "payee"  : ["Store1", "Store2", "Store3"],
        "amount" : [1, 2, 3],
        "date"   : [1, 2, 3],
    } 

    return jsonify(data)


# @app.route('/api/idkyet')

if __name__ == "__main__":
    app.run(debug=True)
