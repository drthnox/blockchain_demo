import binascii
import hashlib
import json
import urllib.parse
import uuid
from collections import OrderedDict

import requests
from Crypto.Hash import SHA256
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5
from flask import Flask, render_template, jsonify, request
from time import time
from flask_cors import CORS

MINING_SENDER = "the-blockchain"
MINING_REWARD = 1
MINING_DIFFICULTY = 2


class Blockchain:
    def __init__(self):
        self.transactions = []  # list of transactions
        self.chain = []  # list of blocks
        self.node_id = str(uuid.uuid4()).replace('-', '')
        self.nodes = set()
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
        return block

    @staticmethod
    def verify_transaction_signature(sender_public_key, signature, transaction):
        # extract the unhexified public key
        public_key = RSA.importKey(binascii.unhexlify(sender_public_key))

        # create a new verifier from the public key
        verifier = PKCS1_v1_5.new(public_key)

        # get the transaction hashed value
        _hash = SHA256.new(str(transaction).encode('utf-8'))
        try:
            verifier.verify(_hash, binascii.unhexlify(signature))
            return True
        except ValueError:
            return False

    @staticmethod
    def sender_is_a_miner(sender_public_key):
        return True

    def submit_transaction(self, sender_public_key, receiver_public_key, signature, amount):
        print("submit_transaction ", amount)
        transaction = OrderedDict({
            'sender_public_key': sender_public_key,
            'receiver_public_key': receiver_public_key,
            'amount': amount
        })

        if self.sender_is_a_miner(sender_public_key):
            self.transactions.append(transaction)
            return len(self.chain) + 1
        else:
            signature_verification = self.verify_transaction_signature(sender_public_key, signature, transaction)
            if signature_verification:
                self.transactions.append(transaction)
                return len(self.chain) + 1

        return False

    @staticmethod
    def hashify(string_data):
        hasher = hashlib.new('sha256')
        hasher.update(string_data.encode('utf8'))
        return hasher.hexdigest()

    def hash_block(self, block):
        # Must ensure that the dictionary is ORDERED,
        # otherwise will result in inconsistent hashes
        block_string = json.dumps(block, sort_keys=True)
        return self.hashify(block_string)

    def valid_proof(self, transactions, last_hash, nonce, difficulty=MINING_DIFFICULTY):
        guess = str(transactions) + str(last_hash) + str(nonce)
        guess_hash = self.hashify(guess)
        return guess_hash[:difficulty] == '0' * difficulty

    def proof_of_work(self):
        # Need to find the nonce
        nonce = 0
        last_block = self.chain[-1]
        last_hash = self.hashify(str(last_block))
        while (self.valid_proof(self.transactions, last_hash, nonce)) is False:
            nonce += 1
        print("PoW nonce: ", nonce)
        return nonce

    def resolve_conflicts(self):
        neighbours = self.nodes
        max_length = len(self.chain)
        new_chain = None

        # Iterate through the neighbouring nodes
        for node in neighbours:
            response = requests.get("http://" + node + "/chain")
            if response.status_code == 200:
                json = response.json()
                length = json['length']
                chain = json['chain']
                if length > max_length and self.valid_chain(chain):
                    # Replace our chain with the longer chain
                    max_length = length
                    new_chain = chain
        if new_chain is not None:
            self.chain = new_chain
            return True

        return False

    def valid_chain(self, _chain):
        last_block = self.chain[0]
        current_index = 1
        while current_index < len(_chain):
            block = _chain[current_index]
            last_hash = self.hash_block(last_block)
            if block['prev_hash'] != last_hash:
                return False
            # Get all transactions except last one, which will be the mining block
            transactions = block['transactions'][:-1]
            transaction_elements = ['sender_public_key', 'receiver_public_key', 'amount']
            transactions = [OrderedDict((k, transaction[k]) for k in transaction_elements) for transaction in
                            transactions]
            prev_hash = block['prev_hash']
            nonce = block['nonce']
            if not self.valid_proof(transactions, prev_hash, nonce):
                return False
            last_block = block
            current_index = current_index + 1
        return True

    def register_node(self, node_url):
        print("register_node: ", node_url)
        # check that URL is valid
        parsed_url = urllib.parse.urlparse(node_url)
        print("parsed_url: ", parsed_url)
        if parsed_url.netloc:
            self.nodes.add(parsed_url.netloc)
        elif parsed_url.path:
            self.nodes.add(parsed_url.path)
        else:
            raise ValueError('Invalid URL')
        print("registered nodes: ", self.nodes)


# instantiate the blockchain
blockchain = Blockchain()

# instantiate a node
app = Flask(__name__, static_folder="static")
CORS(app)


@app.route("/")
def index():
    return render_template('index.html')  # Flask will look inside templates/


@app.route("/configure")
def configure():
    return render_template('configure.html')  # Flask will look inside templates/


@app.route('/chain', methods=['GET'])
def chain():
    response = {
        'chain': blockchain.chain,
        'length': len(blockchain.chain)
    }
    return jsonify(response), 200


@app.route('/mine', methods=['GET'])
def mine():
    # Execute PoW algorithm
    nonce = blockchain.proof_of_work()
    # Reward work by submitting a transaction
    blockchain.submit_transaction(sender_public_key=MINING_SENDER,
                                  receiver_public_key=blockchain.node_id,
                                  signature='',
                                  amount=MINING_REWARD)
    last_block = blockchain.chain[-1]
    prev_hash = blockchain.hash_block(last_block)
    block = blockchain.create_block(nonce, prev_hash)

    response = {
        'message': 'New block created',
        'block_number': block['block_number'],
        'transactions': block['transactions'],
        'nonce': block['nonce'],
        'prev_hash': block['prev_hash'],
    }
    return jsonify(response), 200


@app.route('/transaction/fetchAll', methods=['GET'])
def fetch_transactions():
    transactions = blockchain.transactions
    response = {'transactions': transactions}
    return jsonify(response), 200


@app.route('/nodes/list', methods=['GET'])
def get_node_list():
    nodes = list(blockchain.nodes)
    response = {'nodes': nodes}
    return jsonify(response), 200


@app.route('/nodes/register', methods=['POST'])
def register_nodes():
    values = request.form
    print("values = ", values)
    # expected: 127.0.0.1:5002, 127.0.0.1:5003, 127.0.0.1:5004, ...
    nodes = values.get('nodes').replace(' ', '').split(',')
    print("nodes = ", nodes)
    if nodes is None:
        return 'Error: no nodes defined in request', 400
    for node in nodes:
        blockchain.register_node(node)
    response = {'message': 'Nodes have been added successfully',
                'total_nodes': [node for node in blockchain.nodes]}
    return jsonify(response), 200


@app.route('/transaction/new', methods=['POST'])
def new_transaction():
    print("new_transaction")
    values = request.form

    # Check the required fields
    required_parameters = {
        'confirmation_sender_public_key',
        'confirmation_receiver_public_key',
        'transaction_signature',
        'confirmation_amount'
    }
    if not all(param in values for param in required_parameters):
        return 'Missing Values', 400

    transaction_results = blockchain.submit_transaction(
        values['confirmation_sender_public_key'],
        values['confirmation_receiver_public_key'],
        values['transaction_signature'],
        values['confirmation_amount']
    )
    return_code = 406
    if not transaction_results:
        response = {'message': 'Invalid transaction'}
        return_code = 406
    else:
        response = {'message': 'Transaction will be added to the block ' + str(transaction_results)}
        return_code = 201

    return jsonify(response), return_code


if __name__ == '__main__':
    from argparse import ArgumentParser

    parser = ArgumentParser()
    parser.add_argument('-p', '--port', default=5001,
                        type=int, help="Port to listen to")
    args = parser.parse_args()
    port = args.port

    app.run(host='127.0.0.1', port=port, debug=True)
