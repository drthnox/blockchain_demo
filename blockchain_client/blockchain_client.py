from flask import Flask, render_template

import Crypto.PublicKey
from Crypto import Random
from Crypto.PublicKey import RSA
from flask import jsonify
import binascii


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
    return render_template('../../blockchain_client/templates/create_transaction.html')


@app.route("/transaction/viewAll")
def view_transactions():
    return render_template('../../blockchain_client/templates/view_transactions.html')


@app.route("/wallet/create")
def create_wallet():
    random_generator = Random.new().read
    private_key = Crypto.PublicKey.RSA.generate(1024, random_generator)
    public_key = private_key.public_key()
    response = {
        'private_key': binascii.hexlify(private_key.exportKey(format('DER'))).decode('ascii'),
        'public_key': binascii.hexlify(public_key.exportKey(format('DER'))).decode('ascii')
    }
    return jsonify(response), 200


if __name__ == '__main__':
    from argparse import ArgumentParser

    parser = ArgumentParser()
    parser.add_argument('-p', '--port', default=8081,
                        type=int, help="Port to listen to")
    args = parser.parse_args()
    port = args.port
    app.run(host='127.0.01', port=port, debug=True)
