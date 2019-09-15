import Crypto.Hash.MD5 as MD5
import Crypto.PublicKey.RSA as RSA
from Crypto import Random

plaintext = 'The rain in Spain falls mainly on the Plain'
hash = 'message'.encode()
random_generator = Random.new().read

key = RSA.generate(1024, random_generator)
signature = key.sign(hash, '')
pubkey = key.publickey()
print(pubkey.verify(hash, signature))
