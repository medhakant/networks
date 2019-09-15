import Crypto.Hash.MD5 as MD5
import Crypto.PublicKey.RSA as RSA
from Crypto import Random
from base64 import b64decode,b64encode
import ast

plaintext = 'The rain in Spain falls mainly on the Plain'
random_generator = Random.new().read
key = RSA.generate(1024, random_generator)

message = str(key.encrypt(plaintext.encode(), 32))
print(message)
hash = MD5.new(message.encode()).digest()
print(hash)
# message = key.decrypt(ast.literal_eval(message)).decode()
# print(message)

signature = str(key.sign(hash, ''))
pubkey = key.publickey()
print(pubkey.verify(hash, ast.literal_eval(signature)))
