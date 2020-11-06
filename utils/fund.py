from bitcoinutils.keys import P2pkhAddress
from bitcoinutils.setup import setup
from bitcoinutils.transactions import *
from bitcoinutils.utils import to_satoshis

from core.participant import Participant, broadcast_transaction

setup("testnet")

pool_plain_private_key = 'cVuaAqw1LEscfc4RKHE7ysFLaDor5tW6argWGxJNGb4o67GYNrCL'
pool_plain_private_key = '93AqUCwmbi4b92nsXWN77AwD9XQ7oJ8TmzGV9L3ddbpGu78XgXM'
bob_plain_private_key = 'cQVqxrx5bPLNnpTv87uWnfJ4dZawnKchKDLFkYdA5tZYRmAzoV5G'

BOB = Participant(wif=bob_plain_private_key, network="btc-test3", name="Bob")
POOL = Participant(wif=pool_plain_private_key, network="btc-test3", name="POOL")
ALICE = Participant(wif="cPz2tG7YN1BD6WT4R65J5LnTUtZqgYMBaWGerp75GF2nP14aKtyW", name="Alice")
BOB = Participant(wif="cQVqxrx5bPLNnpTv87uWnfJ4dZawnKchKDLFkYdA5tZYRmAzoV5G", name="Bob")

print(BOB.secret_key.get_public_key().get_address().to_string())
print(BOB.secret_key.get_public_key().get_address().hash160)
print(BOB.pubkey_hash())
# exit(0)
# myL5oK5WQL9ohhAV5bYqxeEoehjmqrbpn4
txids = ["a686584dca6ffa8b1ff07987d3b60adbbc394db3b05f1454e2711b8e389f07f9", # 1
         "d3e947f07c480d256658e7322928bb29459b6e775f2ab246f6bd7b99565e04f4", # 1
         "f8f02ed31116c1b8265a730a496f4d89ec50f87e6118cba3dd478e911f6bb6d1", # 30
         "896945b74d55ad34700986a8bd9858ec19ad1a382fcf01b4353073c5c208fac5", # 20 - 30
         ]


def send_to_p2wpkh(txid_to_spend, utxo_index, amount_to_send):
    transaction = Transaction([], [])
    addr = BOB.public_key.get_segwit_address()
    from_addr = P2pkhAddress(POOL.public_key.get_address().to_string())
    print(from_addr.to_hash160())
    for i in range(0, 1):
        txin = TxInput(txid_to_spend, utxo_index)
        # sk = PrivateKey('cTALNpTpRbbxTCJ2A5Vq88UxT44w1PE2cYqiB3n4hRvzyCev1Wwo')
        # print(sk.get_public_key().get_address().to_string())
        # print(alice_public_key_BTC.get_address().to_string())
        transaction.inputs.append(txin)
    for i in range(0, 40):
        txout = TxOutput(to_satoshis(amount_to_send), addr.to_script_pub_key())
        transaction.outputs.append(txout)
    txout = TxOutput(to_satoshis(0.425/2), POOL.p2pkh_script_pubkey("btc-test3"))
    transaction.outputs.append(txout)
    for i in range(0, 1):
        sig = POOL.secret_key.sign_input(transaction, i, Script(['OP_DUP', 'OP_HASH160',
                                                                         from_addr.to_hash160(), 'OP_EQUALVERIFY',
                                                                         'OP_CHECKSIG']))
        transaction.inputs[i].script_sig = Script([sig, POOL.public_key.to_hex(), POOL.p2pkh_script_pubkey().to_hex()])
        # transaction = Transaction([txin], [txout])


    # print(txin.script_sig.to_bytes())
    return transaction


txid = "d0b6a914f3c9a4b7bb7da433e0530e6669b41ded9742c1bc78c6512907dc94c8"
transaction = send_to_p2wpkh(txid, 5, 0.425/80)
response = broadcast_transaction(transaction.serialize(), network="btc-test3")
print(response.text)
