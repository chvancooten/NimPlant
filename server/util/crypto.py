import base64, string, random
from Crypto.Cipher import AES
from Crypto.Util import Counter

# XOR function to transmit key securely. Matches nimplant XOR function in 'client/util/crypto.nim'
def xorString(value, key):
    k = key
    result = []
    for c in value:
        character = ord(c)
        for f in [0, 8, 16, 24]:
            character = character ^ (k >> f) & 0xFF
        result.append(character)
        k = k + 1
    # Return a bytes-like object constructed from the iterator to prevent chr()/encode() issues
    return bytes(result)


def randString(size, chars=string.ascii_letters + string.digits + string.punctuation):
    return "".join(random.choice(chars) for _ in range(size))


# https://stackoverflow.com/questions/3154998/pycrypto-problem-using-aesctr
def encryptData(plaintext, key):
    iv = randString(16).encode("UTF-8")
    ctr = Counter.new(128, initial_value=int.from_bytes(iv, byteorder="big"))
    aes = AES.new(key.encode("UTF-8"), AES.MODE_CTR, counter=ctr)
    try:
        ciphertext = iv + aes.encrypt(plaintext.encode("UTF-8"))
    except AttributeError:
        ciphertext = iv + aes.encrypt(plaintext)
    enc = base64.b64encode(ciphertext).decode("UTF-8")
    return enc


def decryptData(blob, key):
    ciphertext = base64.b64decode(blob)
    iv = ciphertext[:16]
    ctr = Counter.new(128, initial_value=int.from_bytes(iv, byteorder="big"))
    aes = AES.new(key.encode("UTF-8"), AES.MODE_CTR, counter=ctr)
    dec = aes.decrypt(ciphertext[16:]).decode("UTF-8")
    return dec


def decryptBinaryData(blob, key):
    ciphertext = base64.b64decode(blob)
    iv = ciphertext[:16]
    ctr = Counter.new(128, initial_value=int.from_bytes(iv, byteorder="big"))
    aes = AES.new(key.encode("UTF-8"), AES.MODE_CTR, counter=ctr)
    dec = aes.decrypt(ciphertext[16:])
    return dec
