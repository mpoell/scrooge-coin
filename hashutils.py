import hashlib


def hash_sha256(encoded_str):
    """
    Return the hexidecimal sha256 hash of an 
    encoded string passed as parameter.
    """
    hashfunc = hashlib.sha256()
    hashfunc.update(encoded_str)
    return hashfunc.hexdigest()


def hash_object(obj):
    """
    Return the sha256 hash of the encoded string
    of the object passed as parameter.
    """
    return hash_sha256(str(obj).encode('utf-8'))


def encoded_hash_obj(obj):
    """
    Return the utf-8 encoded hash of the encoded
    string of the object passed as paramater.
    """
    return hash_object(obj).encode('utf-8')
