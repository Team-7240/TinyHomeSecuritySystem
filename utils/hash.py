import hashlib


def md5(string):
    return hashlib.md5(string.encode(encoding='UTF-8')).hexdigest()