import binascii
import hashlib
import os


def generate_salt() -> str:
    """Generate a string with random digit in hex."""
    return hashlib.sha256(os.urandom(60)).hexdigest()


def hash_password(salt: str, password: str) -> str:
    """Hash a password for storing."""
    pwdhash = hashlib.pbkdf2_hmac('sha512', password.encode('utf-8'),
                                  salt.encode('ascii'), 100000)
    pwdhash = binascii.hexlify(pwdhash)
    return pwdhash.decode('ascii')


def verify_password(salt: str, stored_password: str, provided_password: str) -> str:
    """Verify a stored password against one provided by user"""
    pwdhash = hashlib.pbkdf2_hmac('sha512',
                                  provided_password.encode('utf-8'),
                                  salt.encode('ascii'),
                                  100000)
    pwdhash = binascii.hexlify(pwdhash).decode('ascii')
    return pwdhash == stored_password


def generate_serial(string: str) -> str:
    """Given a string, return a string with 16 digit long hex in uppercase that can be used as serial. The same input will return the same output."""
    return hashlib.blake2b(string.encode('utf-8'), digest_size=16).hexdigest().upper()
