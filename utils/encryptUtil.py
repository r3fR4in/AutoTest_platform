import base64
from Crypto.Cipher import AES
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_v1_5 as Cipher_pkcs1_v1_5

# AES pkcs5padding补位
def pkcs5padding(text):
    b_text = text.encode('utf-8')
    needSize = 16-len(text) % 16
    if needSize == 0:
        needSize = 16
    return b_text + needSize.to_bytes(1, 'little')*needSize

# AES加密
def encrypt_by_aes(text, key, iv):
    aes = AES.new(key, AES.MODE_CBC, iv)
    text = pkcs5padding(text)
    en_text = aes.encrypt(text)
    return base64.b64encode(en_text).decode('utf-8')

# AES解密
def decrypt_by_aes(text, key, iv):
    aes = AES.new(key, AES.MODE_CBC, iv)
    b64_text = base64.b64decode(text)
    den_text = aes.decrypt(b64_text).decode('utf-8')
    return den_text.rstrip('utf-8')

# RSA加密
def encrypt_by_rsa(text, key):
    rsa_key = RSA.importKey(key)
    cipher = Cipher_pkcs1_v1_5.new(rsa_key)
    cipher_text = base64.b64encode(cipher.encrypt(text.encode('utf-8')))
    return cipher_text.decode('utf-8')
