
from flask import Flask, render_template


class Transaction:
    def __init__(self, sender_address, sender_private_key, receiver_address, value):
        self.sender_address = sender_address
        self.sender_private_key = sender_private_key
        self.receiver_address = receiver_address
        self.value = value


app = Flask(__name__)


@app.route("/")
def index():
    return render_template('index.html')  # Flask will look inside templates/


@app.route("/transaction/create")
def create_transaction():
    # Flask will look inside templates/
    return render_template('create_transaction.html')


@app.route("/transaction/viewAll")
def view_transactions():
    # Flask will look inside templates/
    return render_template('view_transactions.html')


@app.route("/wallet/create")
def create_wallet():
    # Flask will look inside templates/
    return render_template('create_wallet.html')


if __name__ == '__main__':
    from argparse import ArgumentParser
    parser = ArgumentParser()
    parser.add_argument('-p', '--port', default=8081,
                        type=int, help="Port to listen to")
    args = parser.parse_args()
    port = args.port
    app.run(host='127.0.01', port=port, debug=True)
