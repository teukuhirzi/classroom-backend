def encrypt(plaintext):
    """Encrypt the string and return the ciphertext"""
    result = ''
    n = 3
    key = 'abcdefghijklmnopqrstuvwxyz'
    for l in plaintext.lower():
        try:
            i = (key.index(l) + n) % 26
            result += key[i]
        except ValueError:
            result += l

    return result.lower()

def decrypt(ciphertext):
    """Decrypt the string and return the plaintext"""
    result = ''
    n = 3
    key = 'abcdefghijklmnopqrstuvwxyz'
    for l in ciphertext: 
        try:
            i = (key.index(l) - n) % 26
            result += key[i]
        except ValueError:
            result += l

    return result