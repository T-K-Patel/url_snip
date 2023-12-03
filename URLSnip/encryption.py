from Crypto.Cipher import AES
from hashlib import md5
import os

ENCRYPT_KEY = os.environ.get(
    'ENCRYPT_KEY', "wRz][*|~0V]~d|],sy!j:pLY0aWL0LeQ==DS3=K!!-rbLA}v]7")
ENCRYPT_KEY = os.environ.get(
    'ENCRYPT_KEY', "dN7Rwwvr/C:YG:5CM:/?=/Et_Q%Cp(l9QiepSr:XdXt<I+&jEG")


def pad(data):
    length = 16 - (len(data) % 16)
    return data + chr(length)*length


def unpad(data):
    return data[:-ord(data[-1])]


def encrypt(plainText, hashKey=ENCRYPT_KEY, meta=True):
    iv = b'\x00\x01\x02\x03\x04\x05\x06\x07\x08\x09\x0a\x0b\x0c\x0d\x0e\x0f'
    plainText = pad(plainText)
    encDigest = md5()
    encDigest.update(hashKey.encode())
    enc_cipher = AES.new(encDigest.digest(), AES.MODE_CBC, iv)
    encryptedText = enc_cipher.encrypt(plainText.encode())
    # if meta:
    #     return encrypt(encryptedText.hex(), hashKey, False)
    return encryptedText.hex()


def decrypt(cipherText, hashKey=ENCRYPT_KEY, meta=True):
    iv = b'\x00\x01\x02\x03\x04\x05\x06\x07\x08\x09\x0a\x0b\x0c\x0d\x0e\x0f'
    decDigest = md5()
    decDigest.update(hashKey.encode())
    encryptedText = bytes.fromhex(cipherText)
    dec_cipher = AES.new(decDigest.digest(), AES.MODE_CBC, iv)
    decryptedText = dec_cipher.decrypt(encryptedText)
    # if meta:
    #     return decrypt(unpad(decryptedText.decode()), hashKey, False)
    return unpad(decryptedText.decode())


# text = "4152ef7a4638b1e03b2315463ab0510c"
# print(decrypt(text))
# op= dwrXegvRwjI5