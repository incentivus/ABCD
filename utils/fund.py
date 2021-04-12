from bitcoinutils.keys import P2pkhAddress
from bitcoinutils.setup import setup
from bitcoinutils.transactions import *
from bitcoinutils.utils import to_satoshis

from core.participant import Participant, broadcast_transaction

setup("testnet")

# pool_plain_private_key = 'cVuaAqw1LEscfc4RKHE7ysFLaDor5tW6argWGxJNGb4o67GYNrCL'
# pool_plain_private_key = '93AqUCwmbi4b92nsXWN77AwD9XQ7oJ8TmzGV9L3ddbpGu78XgXM'
# bob_plain_private_key = 'cQVqxrx5bPLNnpTv87uWnfJ4dZawnKchKDLFkYdA5tZYRmAzoV5G'
#
# BOB = Participant(wif=bob_plain_private_key, network="btc-test3", name="Bob")
# POOL = Participant(wif=pool_plain_private_key, network="btc-test3", name="POOL")
# ALICE = Participant(wif="cPz2tG7YN1BD6WT4R65J5LnTUtZqgYMBaWGerp75GF2nP14aKtyW", name="Alice")
BOB = Participant(wif="cQVqxrx5bPLNnpTv87uWnfJ4dZawnKchKDLFkYdA5tZYRmAzoV5G", name="Bob")
ALICE = Participant(wif="cPz2tG7YN1BD6WT4R65J5LnTUtZqgYMBaWGerp75GF2nP14aKtyW", name="Bob")

print(BOB.secret_key.get_public_key().get_address().to_string())
print(BOB.secret_key.get_public_key().get_address().hash160)
print(BOB.pubkey_hash())
# exit(0)
# myL5oK5WQL9ohhAV5bYqxeEoehjmqrbpn4
utxos = [
    # ("a686584dca6ffa8b1ff07987d3b60adbbc394db3b05f1454e2711b8e389f07f9", 0)
    ("9f2ff49b2a382e2335f6006e65e86642c7a917259fcc0cf01214bc92340e2dba", 0), # 0.00140721
    ("d9882491e068d85116642f945a66f0cbfdfcbd97a2f0ef00531c60ef9115dd94", 0), # 0.00022864
    ("3f24a2a6d98b4f5dab8e1b8bb5622b92f01655ddcdf5ed75debe3ed8b2de9e00", 0), # 0.00022864
    ("929341f99e4769a22b6d047467c611e9366fb7db8b7b5dc8a36d20a261e04ae6", 0), # 0.00001432
    ("12d48a1b2035616d284e94a66e3784037e42d761abc977b95185bb0084e9f5b7", 0), # 0.00001432
    ("bb5534564336e3bb2f5a579f15dbd388f7c23e9cd85a1de2ef36e0cd42959d41", 0), # 0.00011432
    ("95b180d5aeac59177e358eb88ed1952167d3daf4fda7dda9085c495434e9a67c", 0), # 0.00022864
    ("bfc89056c5d510d5928e3b5d90a357ebc4b238cb5abcb6bc6be57dd36ac7845e", 0), # 0.00011432
    ("f5129a91a9e75b0203f2797130b5c1188cefac11ff6832e3d961e3eea143d022", 0), # 0.00011432
    ("d76eac4119c2899273b23edc3993e4d2b67698efef750010bb11affdfeaebaeb", 0), # 0.000535
    ("eb73d2e3b0e226f2d4bde06edc3bdbf55bd5d442df137e769bc80d85c601d8c3", 1), # 0.01459763
    ("02afeee1aff167d549dbea0bf1df989011866a67f96d65fab503036a60666596", 0), # 0.0001
    # ("dad4deed8234666a35133d309a5a7f119e4234774491a09ae2f94ee03b5dd292", 1),
    # ("986a7d9cb44453114e7bb1e76e63a0211cdc7beeb26928b0c3de1ceb8f3b6f36", 1),
    # ("d76eac4119c2899273b23edc3993e4d2b67698efef750010bb11affdfeaebaeb", 0),
    # ("041796d1c451d93022e4a1549bec5074dbbdbf5c7ac261432d0258167eebbbf0", 0),
    # ("f5129a91a9e75b0203f2797130b5c1188cefac11ff6832e3d961e3eea143d022", 0)
    # ("2374aaf8ffe2805218afcb9b19a1fe530f327c60901f7dfbaeef91d24c6b9155", 1), # 1
    # ("af886bc6f3ccd788dcc8bd3d6f343ae1f50325e1ea5e88599a938f7f0883616e", 0), # 1
    # ("8cee47855ce7b7b1dbc100581f2b20aceffc32133c14c398a5326e95ec6d3641", 1), # 1
    # ("a2a90cc5a2ce2c7ac4cdf1e7987cabb1614295ee77103205a3265903d23faee7", 0), # 1
    # ("f4b4e6dab96c98ffb5f56a23e73fc3d0eb27bd7bfc82d5706b598cc14ae26eb4", 0), # 1
    # ("509c61fc747d4e9a441ced6bce1fb03e63099df36e2761f087e8044c262b3980", 0), # 1
    # ("8dc383ec7fb359477305cf83e1c7e713fd339dca5addbdec4b2ee14f1cc7f92e", 0), # 1
    # ("b78036c921c38822b55544bf8124a187a5cc0544928e3b1328d0cf07cebf93d5", 0), # 1
    # ("986a7d9cb44453114e7bb1e76e63a0211cdc7beeb26928b0c3de1ceb8f3b6f36", 1), # 1
    # ("dad4deed8234666a35133d309a5a7f119e4234774491a09ae2f94ee03b5dd292", 1), # 1
    # ("a2a90cc5a2ce2c7ac4cdf1e7987cabb1614295ee77103205a3265903d23faee7", 0) # 1
]


def send_to_p2wpkh(amount_to_send, fee):
    transaction = Transaction([], [])
    addr = BOB.public_key.get_segwit_address()
    from_addr = P2pkhAddress(BOB.public_key.get_address().to_string())
    print(from_addr.to_hash160())
    for i in range(len(utxos)):
        txin = TxInput(utxos[i][0], utxos[i][1])
        # sk = PrivateKey('cTALNpTpRbbxTCJ2A5Vq88UxT44w1PE2cYqiB3n4hRvzyCev1Wwo')
        # print(sk.get_public_key().get_address().to_string())
        # print(alice_public_key_BTC.get_address().to_string())
        transaction.inputs.append(txin)
    for i in range(0, 19):
        txout = TxOutput(to_satoshis((amount_to_send - fee)/19), addr.to_script_pub_key())
        transaction.outputs.append(txout)
        # txout = TxOutput(to_satoshis(0.425/2), POOL.p2pkh_script_pubkey("btc-test3"))
        # transaction.outputs.append(txout)
    for i in range(len(utxos)):
        sig = BOB.secret_key.sign_input(transaction, i, Script(['OP_DUP', 'OP_HASH160',
                                                                         from_addr.to_hash160(), 'OP_EQUALVERIFY',
                                                                         'OP_CHECKSIG']))
        transaction.inputs[i].script_sig = Script([sig, BOB.public_key.to_hex()]) # , BOB.p2pkh_script_pubkey().to_hex()])
        # transaction = Transaction([txin], [txout])


    # print(txin.script_sig.to_bytes())
    return transaction


# txid = "d0b6a914f3c9a4b7bb7da433e0530e6669b41ded9742c1bc78c6512907dc94c8"
transaction = send_to_p2wpkh(amount_to_send=0.01769736, fee=0.00015000)
response = broadcast_transaction(transaction.serialize(), network="btc-test3")
print(response.text)
