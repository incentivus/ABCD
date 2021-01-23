# from core.participant import *
from core.secret import *
import bitcoinutils.script as btcscript
import litecoinutils.script as ltcscript


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

def script_builder(script: list,
                   network="btc-test3"):
    return btcscript.Script(script) if network == "btc-test3" else ltcscript.Script(script)


def HTLC_script(
        sender_address: str,
        recipient_address: str,
        secret_hash: str,
        locktime: int,
        network="btc-test3"
):
    return script_builder(
        network=network,
        script=[
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
        sender_pubkey,
        recipient_pubkey,
        secret: str,
        locktime: int,
        network="btc-test3"
):
    return script_builder(
        network=network,
        script=[
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


def margin_dep_script(**kwargs):
    return guarantee_dep_script(**kwargs)


def guarantee_dep_script(
        sender_pubkey,
        recipient_pubkey,
        recipient_address: str,
        locktime: int,
        network="btc-test3"
):
    return script_builder(
        network=network,
        script=[
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
        locktime: int,
        network="btc-test3"
):
    return script_builder(
        network=network,
        script=[
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
