import hashlib
import random
import string

def salter():
    return ''.join([random.choice(string.ascii_letters) for x in range(5)])

def hash_pwd(password, salt=None):
    if not salt:
        salt = salter()
    hash = hashlib.sha256(str.encode(password + salt)).hexdigest()

    return '{0},{1}'.format(hash,salt)

def check_hash_pwd(password, hash):
    salt = hash.split(',')[1]
    if hash_pwd(password, salt) == hash:
        return True
    return False

