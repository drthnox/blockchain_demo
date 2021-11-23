
from flask import Flask, render_template


class Blockchain:
    def __init__(self):
        self.transactions = []  # list of transactions
        self.chain = []  # list of blocks

    def create_block(self, nonce):
        self.nonce = nonce


# instantiate the blockchain
blockchain = Blockchain()

# instantiate a node
app = Flask(__name__)


@app.route("/")
def index():
    return render_template('index.html')  # Flask will look inside templates/


if __name__ == '__main__':
    from argparse import ArgumentParser
    parser = ArgumentParser()
    parser.add_argument('-p', '--port', default=5001,
                        type=int, help="Port to listen to")
    args = parser.parse_args()
    port = args.port
    app.run(host='127.0.01', port=port, debug=True)
