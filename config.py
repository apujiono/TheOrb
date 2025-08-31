# config.py
from cryptography.fernet import Fernet
import base64
import os

def generate_key_from_id(agent_id: str) -> bytes:
    key = base64.urlsafe_b64encode((agent_id[:32].ljust(32, '0')).encode())
    return key

def encrypt_data(data: str, agent_id: str) -> str:
    f = Fernet(generate_key_from_id(agent_id))
    return f.encrypt(data.encode()).decode()

def decrypt_data(token: str, agent_id: str) -> str:
    try:
        f = Fernet(generate_key_from_id(agent_id))
        return f.decrypt(token.encode()).decode()
    except:
        return None