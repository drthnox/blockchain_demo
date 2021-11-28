import unittest
from Crypto.PublicKey import RSA
from Crypto import Random


class PublicKeyGeneratorTest(unittest.TestCase):

    def test_crypto(self):
        random_generator = Random.new().read
        key = RSA.generate(1024, random_generator)
        print('----->>>>>> ', key)


if __name__ == '__main__':
    unittest.main()
