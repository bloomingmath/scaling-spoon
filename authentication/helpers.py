import hashlib, binascii, os

def get_salt():
    return hashlib.sha256(os.urandom(60)).hexdigest()

def hash_password(salt, password):
    """Hash a password for storing."""
    pwdhash = hashlib.pbkdf2_hmac('sha512', password.encode('utf-8'),
                                salt.encode('ascii'), 100000)
    pwdhash = binascii.hexlify(pwdhash)
    return pwdhash.decode('ascii')

def verify_password(salt, stored_password, provided_password):
    """Verify a stored password against one provided by user"""
    pwdhash = hashlib.pbkdf2_hmac('sha512',
                                  provided_password.encode('utf-8'),
                                  salt.encode('ascii'),
                                  100000)
    pwdhash = binascii.hexlify(pwdhash).decode('ascii')
    return pwdhash == stored_password

def get_serial(string):
    return hashlib.blake2b(string.encode('utf-8'), digest_size=16).hexdigest().upper()