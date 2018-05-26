import sys


KEY = "#Y&$HEYHJ$*^I4u5w6h64k086Dbhw4T%$fdvsdfvrgh467j"

def do_xor(key, data):
    dout = []
    for i in range(len(data)):
        dout.append( chr(ord(data[i]) ^ ord(key[i % len(key)])))

    return ''.join(dout)


with open(sys.argv[1], 'rb') as fin, open(sys.argv[2], 'wb') as fout:
    dd = do_xor(KEY, fin.read())
    fout.write(dd)

