import base64
import six

# msg_text = '#include <stdio.h> void main(){printf(\'oi\')}'.rjust(32)
# secret_key = 'batatabatatabata' # create new & store somewhere safe

# cipher = AES.new(secret_key, AES.MODE_ECB) # never use ECB in strong systems obviously
# encoded = base64.b64encode(cipher.encrypt(msg_text))
# print encoded
# # ...
# decoded = cipher.decrypt(base64.b64decode(encoded))
# print decoded

key = 'secret'
# msg_text = '#include <stdio.h> void main(){printf(\'oi\')}'
msg_text = 'oioioi'



def encode(key, string):
    encoded_chars = []
    for i in range(len(string)):
        key_c = key[i % len(key)]
        encoded_c = chr(ord(string[i]) + ord(key_c) % 256)
        encoded_chars.append(encoded_c)
    encoded_string = ''.join(encoded_chars)
    encoded_string = encoded_string.encode('latin') if six.PY3 else encoded_string
    return base64.urlsafe_b64encode(encoded_string).rstrip(b'=')

def decode(key, string):
    string = base64.urlsafe_b64decode(string + b'===')
    string = string.decode('latin') if six.PY3 else string
    encoded_chars = []
    for i in range(len(string)):
        key_c = key[i % len(key)]
        encoded_c = chr((ord(string[i]) - ord(key_c) + 256) % 256)
        encoded_chars.append(encoded_c)
    encoded_string = ''.join(encoded_chars)    
    return encoded_string



e = encode(key, msg_text)
d = decode(key, msg_text)
print ([e])
print ([d])