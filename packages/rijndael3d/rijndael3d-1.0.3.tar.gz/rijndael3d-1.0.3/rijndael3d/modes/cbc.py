from ..utils import partition_text_to_blocks, xor_bytes
from ..cipher import encrypt_block, decrypt_block
from ..padding import pad, unpad


def cbc_encrypt(plaintext: bytes, key: bytes, iv: bytes) -> bytes:
    assert len(key) == 64, "Key length must be 512 bits."
    assert len(iv)  == 64, "IV length must be 512 bits."

    ciphertext = b""
    padded = pad(plaintext, key)
    last_block = iv
    
    for block in partition_text_to_blocks(padded):
        in_block = xor_bytes(block, last_block)
        last_block = encrypt_block(in_block, key)
        ciphertext += last_block
    
    return ciphertext


def cbc_decrypt(ciphertext: bytes, key: bytes, iv: bytes) -> bytes:
    assert len(key) == 64, "Key length must be 512 bits."
    assert len(iv)  == 64, "IV length must be 512 bits."

    plaintext = b""
    blocks = partition_text_to_blocks(ciphertext)

    last_block = iv
    
    for i in range(len(blocks)):
        decrypted_block = decrypt_block(blocks[i], key)
        plaintext += xor_bytes(decrypted_block, last_block)
        last_block = blocks[i]
    
    return unpad(plaintext)
