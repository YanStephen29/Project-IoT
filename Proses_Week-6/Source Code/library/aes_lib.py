# aes_lib.py - AES 128-bit Manual, mode ECB untuk UID RFID
import ubinascii

S_BOX = [
    0x63, 0x7c, 0x77, 0x7b, 0xf2, 0x6b, 0x6f, 0xc5,
    0x30, 0x01, 0x67, 0x2b, 0xfe, 0xd7, 0xab, 0x76,
    0xca, 0x82, 0xc9, 0x7d, 0xfa, 0x59, 0x47, 0xf0,
    0xad, 0xd4, 0xa2, 0xaf, 0x9c, 0xa4, 0x72, 0xc0,
    0xb7, 0xfd, 0x93, 0x26, 0x36, 0x3f, 0xf7, 0xcc,
    0x34, 0xa5, 0xe5, 0xf1, 0x71, 0xd8, 0x31, 0x15,
    0x04, 0xc7, 0x23, 0xc3, 0x18, 0x96, 0x05, 0x9a,
    0x07, 0x12, 0x80, 0xe2, 0xeb, 0x27, 0xb2, 0x75,
    0x09, 0x83, 0x2c, 0x1a, 0x1b, 0x6e, 0x5a, 0xa0,
    0x52, 0x3b, 0xd6, 0xb3, 0x29, 0xe3, 0x2f, 0x84,
    0x53, 0xd1, 0x00, 0xed, 0x20, 0xfc, 0xb1, 0x5b,
    0x6a, 0xcb, 0xbe, 0x39, 0x4a, 0x4c, 0x58, 0xcf,
    0xd0, 0xef, 0xaa, 0xfb, 0x43, 0x4d, 0x33, 0x85,
    0x45, 0xf9, 0x02, 0x7f, 0x50, 0x3c, 0x9f, 0xa8,
    0x51, 0xa3, 0x40, 0x8f, 0x92, 0x9d, 0x38, 0xf5,
    0xbc, 0xb6, 0xda, 0x21, 0x10, 0xff, 0xf3, 0xd2,
    0xcd, 0x0c, 0x13, 0xec, 0x5f, 0x97, 0x44, 0x17,
    0xc4, 0xa7, 0x7e, 0x3d, 0x64, 0x5d, 0x19, 0x73,
    0x60, 0x81, 0x4f, 0xdc, 0x22, 0x2a, 0x90, 0x88,
    0x46, 0xee, 0xb8, 0x14, 0xde, 0x5e, 0x0b, 0xdb,
    0xe0, 0x32, 0x3a, 0x0a, 0x49, 0x06, 0x24, 0x5c,
    0xc2, 0xd3, 0xac, 0x62, 0x91, 0x95, 0xe4, 0x79,
    0xe7, 0xc8, 0x37, 0x6d, 0x8d, 0xd5, 0x4e, 0xa9,
    0x6c, 0x56, 0xf4, 0xea, 0x65, 0x7a, 0xae, 0x08,
    0xba, 0x78, 0x25, 0x2e, 0x1c, 0xa6, 0xb4, 0xc6,
    0xe8, 0xdd, 0x74, 0x1f, 0x4b, 0xbd, 0x8b, 0x8a,
    0x70, 0x3e, 0xb5, 0x66, 0x48, 0x03, 0xf6, 0x0e,
    0x61, 0x35, 0x57, 0xb9, 0x86, 0xc1, 0x1d, 0x9e,
    0xe1, 0xf8, 0x98, 0x11, 0x69, 0xd9, 0x8e, 0x94,
    0x9b, 0x1e, 0x87, 0xe9, 0xce, 0x55, 0x28, 0xdf,
    0x8c, 0xa1, 0x89, 0x0d, 0xbf, 0xe6, 0x42, 0x68,
    0x41, 0x99, 0x2d, 0x0f, 0xb0, 0x54, 0xbb, 0x16
]

INV_S_BOX = [0] * 256
for i in range(256):
    INV_S_BOX[S_BOX[i]] = i

def xor_bytes(a, b): return [x ^ y for x, y in zip(a, b)]
def sub_bytes(state): return [S_BOX[b] for b in state]
def inv_sub_bytes(state): return [INV_S_BOX[b] for b in state]
def shift_rows(s): return [s[0], s[5], s[10], s[15], s[4], s[9], s[14], s[3], s[8], s[13], s[2], s[7], s[12], s[1], s[6], s[11]]
def inv_shift_rows(s): return [s[0], s[13], s[10], s[7], s[4], s[1], s[14], s[11], s[8], s[5], s[2], s[15], s[12], s[9], s[6], s[3]]
def xtime(a): return ((a << 1) ^ 0x1b) & 0xff if a & 0x80 else a << 1

def mix_columns(state):
    for i in range(4):
        t = state[i] ^ state[i+4] ^ state[i+8] ^ state[i+12]
        u = state[i]
        state[i] ^= t ^ xtime(state[i] ^ state[i+4])
        state[i+4] ^= t ^ xtime(state[i+4] ^ state[i+8])
        state[i+8] ^= t ^ xtime(state[i+8] ^ state[i+12])
        state[i+12] ^= t ^ xtime(state[i+12] ^ u)
    return state

def inv_mix_columns(state):
    def mul(a, b):
        p = 0
        for _ in range(8):
            if b & 1: p ^= a
            hi = a & 0x80
            a = ((a << 1) & 0xFF)
            if hi: a ^= 0x1b
            b >>= 1
        return p

    for i in range(4):
        a = state[i]
        b = state[i+4]
        c = state[i+8]
        d = state[i+12]
        state[i] = mul(a,14)^mul(b,11)^mul(c,13)^mul(d,9)
        state[i+4] = mul(a,9)^mul(b,14)^mul(c,11)^mul(d,13)
        state[i+8] = mul(a,13)^mul(b,9)^mul(c,14)^mul(d,11)
        state[i+12] = mul(a,11)^mul(b,13)^mul(c,9)^mul(d,14)
    return state

def key_expansion(key):
    def sub_word(w): return [S_BOX[b] for b in w]
    def rot_word(w): return w[1:] + w[:1]

    rcon = 1
    w = [list(key[i:i+4]) for i in range(0, 16, 4)]
    for i in range(4, 44):
        temp = w[i-1]
        if i % 4 == 0:
            temp = xor_bytes(sub_word(rot_word(temp)), [rcon, 0, 0, 0])
            rcon = xtime(rcon)
        w.append(xor_bytes(w[i-4], temp))
    return [b for word in w for b in word]

def pad(text):
    pad_len = 16 - (len(text) % 16)
    return text + chr(pad_len) * pad_len

def unpad(text):
    pad_len = ord(text[-1])
    return text[:-pad_len]

KEY = b'ThisIsASecretKey'

def encrypt_uid(uid):
    padded = pad(uid)
    state = list(padded.encode())
    round_keys = key_expansion(KEY)
    state = xor_bytes(state, round_keys[:16])
    for i in range(1, 10):
        state = sub_bytes(state)
        state = shift_rows(state)
        state = mix_columns(state)
        state = xor_bytes(state, round_keys[i*16:(i+1)*16])
    state = sub_bytes(state)
    state = shift_rows(state)
    state = xor_bytes(state, round_keys[160:])
    return ubinascii.hexlify(bytes(state)).decode()

def decrypt_uid(hex_str):
    state = list(ubinascii.unhexlify(hex_str))
    round_keys = key_expansion(KEY)
    state = xor_bytes(state, round_keys[160:])
    for i in range(9, 0, -1):
        state = inv_shift_rows(state)
        state = inv_sub_bytes(state)
        state = xor_bytes(state, round_keys[i*16:(i+1)*16])
        state = inv_mix_columns(state)
    state = inv_shift_rows(state)
    state = inv_sub_bytes(state)
    state = xor_bytes(state, round_keys[:16])
    try:
        return unpad(bytes(state).decode())
    except:
        return "[DECRYPT ERR]"

