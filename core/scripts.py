from core.participant import *
from core.secret import *


# def redemption_script(
#         sender_pubkey: PublicKey,
#         recipient_pubkeyhash: str,
#         secret_hash: str,
#         locktime: int
# ) -> Script:
#     return Script([
#         # fill this in!
#         'OP_IF',
#         int_to_le_hex(locktime),
#         'OP_CHECKLOCKTIMEVERIFY',
#         'OP_DROP',
#         'OP_DUP',
#         'OP_HASH160',
#         sender_pubkey.to_hex(),
#         'OP_EQUALVERIFY',
#         'OP_CHECKSIG',
#         'OP_ELSE',
#         'OP_HASH160',
#         secret_hash,
#         'OP_EQUALVERIFY',
#         'OP_DUP',
#         'OP_HASH160',
#         recipient_pubkeyhash,
#         'OP_EQUALVERIFY',
#         'OP_CHECKSIG',
#         'OP_ENDIF'
#     ])


def HTLC_script(
        sender_address: str,
        recipient_address: str,
        secret_hash: str,
        locktime: int
) -> Script:
    return Script([
        # fill this in!
        'OP_IF',
        int_to_le_hex(locktime),
        'OP_CHECKLOCKTIMEVERIFY',
        'OP_DROP',
        'OP_DUP',
        'OP_HASH160',
        sender_address,
        'OP_EQUALVERIFY',
        'OP_CHECKSIG',
        'OP_ELSE',
        'OP_HASH160',
        secret_hash,
        'OP_EQUALVERIFY',
        'OP_DUP',
        'OP_HASH160',
        recipient_address,
        'OP_EQUALVERIFY',
        'OP_CHECKSIG',
        'OP_ENDIF'
    ])


def funding_script(
        sender_address: str,
        sender_pubkey: PublicKey,
        recipient_pubkey: PublicKey,
        secret: str,
        locktime: int,
) -> Script:
    return Script([
        'OP_0',
        'OP_EQUAL',
        'OP_NOTIF',
        int_to_le_hex(locktime),
        'OP_CHECKLOCKTIMEVERIFY',
        'OP_DROP',
        'OP_DUP',
        'OP_HASH160',
        sender_address,
        'OP_EQUALVERIFY',
        'OP_CHECKSIG',
        'OP_ELSE',
        'OP_HASH160',
        secret,
        'OP_EQUALVERIFY',
        2,
        sender_pubkey.to_hex(),
        recipient_pubkey.to_hex(),
        2,
        'OP_CHECKMULTISIG',
        'OP_ENDIF'
    ])


def margin_dep_script(**kwargs) -> Script:
    return premium_dep_script(**kwargs)


def premium_dep_script(
        sender_pubkey: PublicKey,
        recipient_pubkey: PublicKey,
        recipient_address: str,
        locktime: int
) -> Script:
    return Script([
        'OP_0',
        'OP_EQUAL',
        'OP_NOTIF',
        int_to_le_hex(locktime),
        'OP_CHECKLOCKTIMEVERIFY',
        'OP_DROP',
        'OP_DUP',
        'OP_HASH160',
        recipient_address,
        'OP_EQUALVERIFY',
        'OP_CHECKSIG',
        'OP_ELSE',
        2,
        sender_pubkey.to_hex(),
        recipient_pubkey.to_hex(),
        2,
        'OP_CHECKMULTISIG',
        'OP_ENDIF'
    ])


def carol_HTLC_script(
        sender_pubkeyhash: str,
        recipient_pubkeyhash: str,
        secret: Secret,
        locktime: int
) -> Script:
    return Script([
        'OP_IF',
        int_to_le_hex(locktime),
        'OP_CHECKLOCKTIMEVERIFY',
        'OP_DROP',
        'OP_DUP',
        'OP_HASH160',
        sender_pubkeyhash,
        'OP_EQUALVERIFY',
        'OP_CHECKSIG',
        'OP_ELSE',
        'OP_HASH160',
        secret.digest_hex(),
        'OP_EQUALVERIFY',
        'OP_DUP',
        'OP_HASH160',
        recipient_pubkeyhash,
        'OP_EQUALVERIFY',
        'OP_CHECKSIG',
        'OP_ENDIF'
    ])