from Crypto.Hash import SHA, SHA256
from flask import Flask, render_template, request
import Crypto.PublicKey
from Crypto import Random
from Crypto.PublicKey import RSA
from flask import jsonify
import binascii
from collections import OrderedDict
from werkzeug.exceptions import HTTPException
from Crypto.Signature import PKCS1_v1_5

debug = True  # global variable setting the debug config


class Transaction:
    def __init__(self, sender_public_key='', sender_private_key='', receiver_public_key='', amount='0.0'):
        self.sender_public_key = sender_public_key
        self.sender_private_key = sender_private_key
        self.receiver_public_key = receiver_public_key
        self.amount = amount

    def to_dict(self):
        return OrderedDict({
            'sender_public_key': self.sender_public_key,
            'sender_private_key': self.sender_private_key,
            'receiver_public_key': self.receiver_public_key,
            'amount': self.amount
        })

    def sign(self):
        key = binascii.unhexlify(self.sender_private_key)
        private_key = RSA.importKey(key)
        signer = PKCS1_v1_5.new(private_key)
        encoded_transaction = str(self.to_dict()).encode('utf8')
        signed_hash = signer.sign(SHA256.new(encoded_transaction))
        signature = binascii.hexlify(signed_hash).decode('ascii')
        return signature


app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')  # Flask will look inside templates/


@app.errorhandler(Exception)
def handle_exception(e):
    if isinstance(e, HTTPException):
        return e

    res = {'code': 500,
           'errorType': 'Internal Server Error',
           'errorMessage': "Something went really wrong!"}
    if debug:
        res['errorMessage'] = e.message if hasattr(e, 'message') else f'{e}'

    return jsonify(res), 500


@app.route('/transaction/create')
def create_transaction():
    print("create_transaction")
    return render_template('create_transaction.html')


@app.route('/transaction/generate', methods=['POST'])
def generate_transaction():
    print("generate_transaction")
    sender_public_key = request.form['sender_public_key']
    sender_private_key = request.form['sender_private_key']
    receiver_public_key = request.form['receiver_public_key']
    amount = request.form['amount']
    transaction = Transaction(sender_public_key, sender_private_key, receiver_public_key, amount)
    response = {
        'transaction': transaction.to_dict(),
        'signature': transaction.sign()
    }
    print('sender_public_key = ', transaction.sender_public_key)
    print('sender_private_key = ', transaction.sender_private_key)
    print('receiver_public_key = ', transaction.receiver_public_key)
    print('amount = ', transaction.amount)
    return jsonify(response), 200


@app.route('/transaction/history')
def view_transactions():
    return ''


@app.route('/wallet/create')
def create_wallet():
    print("create_wallet")
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
