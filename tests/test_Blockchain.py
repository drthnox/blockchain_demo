from blockchain import blockchain

def test_init():
    bc = blockchain.Blockchain()
    assert len(bc.chain) == 1
    assert bc.chain[0]['nonce'] == 0
    assert bc.chain[0]['prev_hash'] == '00'

def test_create_block():
    bc = blockchain.Blockchain()
    nonce = 12345
    bc.create_block(nonce, '0x01')
    assert len(bc.chain) == 2
    assert bc.chain[1]['nonce'] == nonce
    assert bc.chain[1]['prev_hash'] == '0x01'
