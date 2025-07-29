from cryptography.fernet import Fernet
import base64, hashlib
from .modules.executor import load_newjson_data

def derive_key(key_str):
    return base64.urlsafe_b64encode(hashlib.sha256(key_str.encode()).digest())

keys = load_newjson_data('keys.json')
key = derive_key(keys['encryption_key'])
f = Fernet(key)

token = f.encrypt(keys['auth'].encode()).decode()

def getAuthKey():
    return token