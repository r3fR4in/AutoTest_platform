import base64

import requests
import uuid
from Crypto.Cipher import AES
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_v1_5 as Cipher_pkcs1_v1_5


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


# 从接口获取rsaKey和uniqueId
# secretKey_api = 'http://172.30.22.143:9000/crm_api/crm-portal-server/n/buddy/secretKey?language=zh-TW'
secretKey_api = 'http://172.30.22.139/crm_api/crm-portal-server/n/buddy/secretKey?language=zh-TW'
secretKey_header = {
    'Content-Type': 'application/json'
}
secretKey_res = requests.request('get', secretKey_api, headers=secretKey_header)

secretKey_res_json = secretKey_res.json()
rsaKey = '-----BEGIN RSA PRIVATE KEY-----\n' + secretKey_res_json['data']['rsaKey'] + '\n-----END RSA PRIVATE KEY-----'
uniqueId = secretKey_res_json['data']['uniqueId']
print('--------------------rsaKey---------------------')
print(rsaKey)
print('--------------------uniqueId---------------------')
print(uniqueId)

# 生成16位随机数randomKey
randomKey = str(uuid.uuid4().int >> 64)[0:16]
print('--------------------randomKey---------------------')
print(randomKey)

# 需要调的接口
# api = 'http://172.30.22.143:9000/crm_api/crm-oa-server-nelson/p/by/usage/infos'
api = 'http://172.30.22.139/crm_api/crm-oa-server/p/by/usage/infos'
api_header = {
    'Content-Type': 'application/json',
    'Authorization': 'Bearer eyJhbGciOiJIUzUxMiJ9.eyJzdWIiOiJlQ2hhbm5lbFRlbXBVc2VyOjY5OTkxMzA3OmQxY2IyOTgxLWI1OTAtNGU4OC05NGI2LTAzNDhjZDNkZjNjOTk6MTY1MjE3MzYwMTU0MiJ9.4w1EdQtJQwYI5YaqoiWCV-X9zGcvkZbNoS538Cu80sQgkh1Ytj1fWciz6qJvTJs_GrwGF0uh42KLCMwe7LWwRw',
    'versionCode': '204'
}
api_body = {
    'serviceCategoryCode': 1,
    'serviceNumber': '69991307'
}

# RSA加密randomKey得到secretKey
secretKey = encrypt_by_rsa(randomKey, rsaKey)
print('--------------------secretKey---------------------')
print(secretKey)

# 请求体AES加密
iv = 'tdrdadq59tbss5Y5'
encrypt_api_body = encrypt_by_aes(str(api_body), randomKey.encode('utf-8'), iv.encode('utf-8'))
print('--------------------encryptData---------------------')
print(encrypt_api_body)

# 发送请求
real_api_body = {
    'encryptData': encrypt_api_body,
    'secretKey': secretKey,
    'uniqueId': uniqueId
}
# header不传versionCode，response就不会加密
res = requests.request('get', api, headers=api_header, params=real_api_body)
print('--------------------response---------------------')
# print(res.json())
# print(res.text)
print(res.text[8:])

# 响应解密
dec_res = decrypt_by_aes(res.text[8:], 'hrerujfgjsrtasfr'.encode('utf-8'), 'tdrdadq59tbss5Y5'.encode('utf-8'))
print('--------------------decrypt response---------------------')
print(dec_res)


