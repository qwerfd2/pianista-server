from base64 import b64encode, b64decode
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
import json

key = bytes([71, 43, 75, 98, 80, 101, 83, 104, 86, 109, 89, 113, 51, 115, 54, 118])

def encrypt(json_data):
    json_str = json.dumps(json_data)
    data = json_str.encode('utf-8')
    cipher = AES.new(key, AES.MODE_ECB)
    encrypted_data = cipher.encrypt(pad(data, AES.block_size))
    base64_encrypted_str = b64encode(encrypted_data).decode('utf-8')
    return base64_encrypted_str

def decrypt(base64_encrypted_str):
    encrypted_data = b64decode(base64_encrypted_str)
    cipher = AES.new(key, AES.MODE_ECB)
    decrypted_data = unpad(cipher.decrypt(encrypted_data), AES.block_size)
    json_str = decrypted_data.decode('utf-8')
    json_data = json.loads(json_str)
    return json_data