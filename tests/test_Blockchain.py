from blockchain import blockchain

def test_create_block():
    bc = blockchain.Blockchain()
    nonce = 12345
    bc.create_block(nonce)
    assert bc.nonce == nonce
