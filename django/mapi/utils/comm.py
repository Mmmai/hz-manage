import os,string,secrets
def generate_random_key(length=32):
    characters = string.ascii_letters + string.digits
    random_key = ''.join(secrets.choice(characters) for _ in range(length))
    return random_key
def get_uuid():
     import uuid
     return str(uuid.uuid4()).replace("-","")[0:16]