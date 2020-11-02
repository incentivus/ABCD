from bitcoinutils.keys import P2pkhAddress
from bitcoinutils.setup import setup
from bitcoinutils.transactions import *
from bitcoinutils.utils import to_satoshis

from core.participant import Participant

setup("testnet")

pool_plain_private_key = 'cVuaAqw1LEscfc4RKHE7ysFLaDor5tW6argWGxJNGb4o67GYNrCL'
bob_plain_private_key = 'cQVqxrx5bPLNnpTv87uWnfJ4dZawnKchKDLFkYdA5tZYRmAzoV5G'

BOB = Participant(wif=bob_plain_private_key, network="btc-test3", name="Bob")
POOL = Participant(wif=pool_plain_private_key, network="btc-test3", name="POOL")
ALICE = Participant(wif="cPz2tG7YN1BD6WT4R65J5LnTUtZqgYMBaWGerp75GF2nP14aKtyW", name="Alice")

print(ALICE.secret_key.get_public_key().get_address().to_string())
print(ALICE.secret_key.get_public_key().get_address().hash160)
print(ALICE.pubkey_hash())
exit(0)
# myL5oK5WQL9ohhAV5bYqxeEoehjmqrbpn4
txids = ["a686584dca6ffa8b1ff07987d3b60adbbc394db3b05f1454e2711b8e389f07f9", # 1
         "d3e947f07c480d256658e7322928bb29459b6e775f2ab246f6bd7b99565e04f4", # 1
         "f8f02ed31116c1b8265a730a496f4d89ec50f87e6118cba3dd478e911f6bb6d1", # 30
         "896945b74d55ad34700986a8bd9858ec19ad1a382fcf01b4353073c5c208fac5", # 20 - 30
         ]


def send_to_p2wpkh(txid_to_spend, utxo_index, amount_to_send):
    transaction = Transaction([], [])
    addr = ALICE.public_key.get_segwit_address()
    from_addr = P2pkhAddress(POOL.public_key.get_address().to_string())
    print(from_addr.to_hash160())
    for i in range(0, 30):
        txin = TxInput(txid_to_spend, i)
        # sk = PrivateKey('cTALNpTpRbbxTCJ2A5Vq88UxT44w1PE2cYqiB3n4hRvzyCev1Wwo')
        # print(sk.get_public_key().get_address().to_string())
        # print(alice_public_key_BTC.get_address().to_string())
        transaction.inputs.append(txin)
    for i in range(60):
        txout = TxOutput(to_satoshis(amount_to_send), addr.to_script_pub_key())
        transaction.outputs.append(txout)

    for i in range(0, 30):
        sig = POOL.secret_key.sign_input(transaction, i, Script(['OP_DUP', 'OP_HASH160',
                                                                         from_addr.to_hash160(), 'OP_EQUALVERIFY',
                                                                         'OP_CHECKSIG']))
        transaction.inputs[i].script_sig = Script([sig, POOL.public_key.to_hex()])
        # transaction = Transaction([txin], [txout])


    # print(txin.script_sig.to_bytes())
    return transaction


# "asm": "OP_DUP OP_HASH160 33ddf354e785e99bdaae630e3aaf2ec44629e9aa OP_EQUALVERIFY OP_CHECKSIG",

txid = "f8f02ed31116c1b8265a730a496f4d89ec50f87e6118cba3dd478e911f6bb6d1"
transaction = send_to_p2wpkh(txid, 0, (0.0249594 - 0.0001)/60)
response = BOB.broadcast_transaction(transaction.serialize(), network="btc-test3", transaction_name="INITIAL FUND")
