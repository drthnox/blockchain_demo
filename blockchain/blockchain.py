from collections import OrderedDict

from flask import Flask, render_template, jsonify, request
from time import time
from flask_cors import CORS


class Blockchain:
    def __init__(self):
        self.transactions = []  # list of transactions
        self.chain = []  # list of blocks
        # create the genesis block
        self.create_block(0, '00')

    def create_block(self, nonce, prev_hash):
        block = {
            'block_number': len(self.chain) + 1,
            'nonce': nonce,
            'prev_hash': prev_hash,
            'timestamp': time(),  # when this block was mined
            'transactions': self.transactions
        }
        # reset the current list of transactions
        self.transactions = []
        # append to the chain
        self.chain.append(block)

    def submit_transaction(self, sender_public_key, receiver_public_key, signature, amount):
        # TODO reward the miner
        # TODO Validate signature
        transaction = OrderedDict({
            'sender_public_key': sender_public_key,
            'receiver_public_key': receiver_public_key,
            'signature': signature,
            'amount': amount
        })
        signature_verification = True
        if signature_verification:
            self.transactions.append(transaction)
            return len(self.chain) + 1
        else:
            return False


# instantiate the blockchain
blockchain = Blockchain()

# instantiate a node
app = Flask(__name__)
CORS(app)


@app.route("/")
def index():
    return render_template('index.html')  # Flask will look inside templates/


@app.route('/transaction/new', methods=['POST'])
def new_transaction():
    print("new_transaction")
    values = request.form

    # TODO: Check the required fields
    transaction_results = blockchain.submit_transaction(
        values['confirmation_sender_public_key'],
        values['confirmation_receiver_public_key'],
        values['transaction_signature'],
        values['confirmation_amount']
    )
    if transaction_results == False:
        response = {'message': 'Invalid transaction'}
        return jsonify(response), 406
    else:
        response = {'message': 'Transaction will be added to the block ' + str(transaction_results)}
        return jsonify(response), 201

    response = {'message': 'ok'}
    return jsonify(response), 201


if __name__ == '__main__':
    from argparse import ArgumentParser

    parser = ArgumentParser()
    parser.add_argument('-p', '--port', default=5001,
                        type=int, help="Port to listen to")
    args = parser.parse_args()
    port = args.port

    app.run(host='127.0.01', port=port, debug=True)
