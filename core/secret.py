from bitcoin.core import Hash160


def int_to_le_hex(number: int) -> str:
    byte_len = (number.bit_length() + 7) // 8
    return number.to_bytes(byte_len, 'little').hex()


class Secret:
    # secret: bytes

    def __init__(self, secret: str):
        self.secret = secret.encode('utf8')

    def hex(self) -> str:
        return self.secret.hex()

    def digest(self) -> bytes:
        return Hash160(self.secret)

    def digest_hex(self) -> str:
        return self.digest().hex()
