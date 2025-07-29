from ..cipher import encrypt_block, decrypt_block
from ..padding import pad, unpad
from ..utils import partition_text_to_blocks


def ecb_encrypt(plaintext: bytes, key: bytes) -> bytes:
    assert len(key) == 64, "Key length must be 512 bits."
    
    ciphertext = b""
    padded = pad(plaintext, key)
    for block in partition_text_to_blocks(padded):
        ciphertext += encrypt_block(block, key)
    
    return ciphertext


def ecb_decrypt(ciphertext: bytes, key: bytes) -> bytes:
    assert len(key) == 64, "Key length must be 512 bits."

    plaintext = b""
    for block in partition_text_to_blocks(ciphertext):
        plaintext += decrypt_block(block, key)
         
    return unpad(plaintext)
