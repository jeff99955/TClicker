from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
import binascii


def _encrypt(keyPair, str):
    encryptor = PKCS1_OAEP.new(keyPair.publickey())
    encrypted = encryptor.encrypt(str)
    return encrypted

def _decrypt(keyPair, enc):
    d = PKCS1_OAEP.new(keyPair)
    r = d.decrypt(enc)
    return r

def get_username(keyPair):
    f = open('pub', 'rb')
    return _decrypt(keyPair, f.read())

def get_pwd(keyPair):
    f = open('puk', 'rb')
    return _decrypt(keyPair, f.read())

def main():
    f = open('key', 'r')
    keyPair = RSA.importKey(f.read())
    f.close()

    u = get_username(keyPair)
    usr = u.decode('utf-8')
    p = get_pwd(keyPair)
    pwd = p.decode('utf-8')
    print(usr,  pwd)


if  __name__ == "__main__":
    main()