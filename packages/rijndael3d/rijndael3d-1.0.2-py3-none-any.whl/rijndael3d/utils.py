def partition_text_to_blocks(source: bytes, assert_blocks = True) -> list[bytes]:
    if assert_blocks:
        assert len(source)%64 == 0, "Can only partition multiples of 64."

    blocks = []
    for start in range(0, len(source), 64):
        blocks.append(source[start:start+64])

    return blocks


def xor_bytes(b1: bytes, b2: bytes) -> bytes:
    assert len(b1) == len(b2), "Blocks are of not matching length."
    return (int(b1.hex(), 16) ^ int(b2.hex(), 16)).to_bytes(len(b1))
