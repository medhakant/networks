import Crypto
from Crypto.PublicKey import RSA
from Crypto import Random
import ast

random_generator = Random.new().read
key = RSA.generate(1024, random_generator)
publickey = key.publickey()
encrypted = str(publickey.encrypt('hello'.encode(), 32))
print(type(encrypted))
print ('encrypted message:', encrypted) #ciphertext
decrypted = key.decrypt(ast.literal_eval(str(encrypted)))
print ('decrypted message', decrypted)