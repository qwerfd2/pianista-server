from base64 import b64decode
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad

# Provided Key (converting the list of integers to bytes)
key = bytes([71, 43, 75, 98, 80, 101, 83, 104, 86, 109, 89, 113, 51, 115, 54, 118])

def decrypt(base64_encrypted_str):
    encrypted_data = b64decode(base64_encrypted_str)
    
    # Create cipher object with ECB mode (no IV required for ECB)
    cipher = AES.new(key, AES.MODE_ECB)
    decrypted_data = unpad(cipher.decrypt(encrypted_data), AES.block_size)
    
    return decrypted_data.decode('utf-8')

# Example usage
base64_string = input("Enter the base64 string to decrypt: ")
decrypted_data = decrypt(base64_string)

# Print the decrypted data (assuming it's a string)
print(decrypted_data)
