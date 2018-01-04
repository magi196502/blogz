import hashlib
import random
import string

# Define the salt portion of the password hasher
def salter():
    # Generate a random string to append to the hashed password
    return ''.join([random.choice(string.ascii_letters) for x in range(5)])

def hash_pwd(password, salt=None):
    # Check to see if the salt string exists and add if it doesn't
    if not salt:
        salt = salter()
    
    # Create the hashed password
    hash = hashlib.sha256(str.encode(password + salt)).hexdigest()

    # Return the hashed password wit the salt separated by a comma
    return '{0},{1}'.format(hash,salt)

# Verify the password entered by the user and compare to the password
# in the database and return a True if they match and False if not
def check_hash_pwd(password, hash):

    # Split the hashed password in the database to get the salt
    salt = hash.split(',')[1]

    # Compare the hashed password entered by the user against
    # the hashed password in the database and return True if a
    # match is found and False if not
    if hash_pwd(password, salt) == hash:
        return True

    # The default is to return False
    return False

