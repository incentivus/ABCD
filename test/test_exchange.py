from unittest import TestCase

# secret used for HTLCs
from bitcoinutils.script import Script
from bitcoinutils.setup import setup
from bitcoinutils.transactions import TxOutput, Transaction, TxInput
from bitcoinutils.utils import to_satoshis

from core.bondissuer import BondIssuer
from core.config import DEFAULT_TX_FEE
from core.exchange import Exchange
from core.participant import Participant
from core.scripts import HTLC_script
from core.secret import Secret
from core.utxo import UTXO

BOB_SECRET = Secret("thisIsASecretPasswordForBob")
ALICE_SECRET = Secret("thisIsASecretPasswordForAlice")

# secret wifs
ALICE = BondIssuer(wif='cPz2tG7YN1BD6WT4R65J5LnTUtZqgYMBaWGerp75GF2nP14aKtyW', funding_secret=ALICE_SECRET)
ALICE.load_keys(wif='BsAupz3NaLSGQD83dL8h9QpC1SzGvZJbC8RCQyVztct8VqPvPRig', network="bcy-tst")
BOB = Participant(wif='cRTBStSdJeYt3BV2JGfdJb46m8T67Ht7zm2pkKup6gwV6EqZkzvQ', network="btc-test3")
CAROL = Exchange(wif="Bqj17XDLkQA11SJcihX3qwwVC4PJWfQXxGh8V2gM1C8RCs5zxooi", network="bcy-tst")
# BCY network
carol_utxo_to_spend = UTXO(
    txid="280f6b3f36ead225f86d22d6e5c4569d0c118265f1d576a29b5ffc01af05c225",
    output_idx=2,
    value=98000,  # 0.00099
    redeem_script=None,
)

carol_htlc_utxo = UTXO(
    txid="0e581acea0303f144286874cc7b6323e8f8bbc6e7ea7542b9cb77bfbea0e1662",
    output_idx=0,
    value=to_satoshis(0.00088000),  # 0.00099
    redeem_script=None,
)


class TestExchange(TestCase):

    def test_make_htlc(self):
        setup('testnet')
        HTLC_tx, HTLC_utxo = CAROL.make_HTLC(utxo=carol_utxo_to_spend,
                                                     recipient_pubkeyhash=ALICE.pubkey_hash(network="bcy-tst"),
                                                     secret_hash=BOB_SECRET.digest_hex(), locktime=10)
        CAROL.commit_HTLC()
        CAROL.broadcast_transaction(CAROL.HTLC_ser, network="bcy-tst")
        HTLC_output_tx = ALICE.make_HTLC_output_tx(utxo=HTLC_utxo, network="bcy-tst")
        print(HTLC_utxo.redeem_script.script)
        print(HTLC_tx.serialize())
        alice_sig = ALICE.secret_key_BCY.sign_input(tx=HTLC_output_tx, txin_index=0, script=HTLC_utxo.redeem_script)
        ALICE.commit_HTLC_output(alice_sig, BOB_SECRET)
        ALICE.broadcast_transaction(ALICE.HTLC_output_ser, network="bcy-tst")
        print(CAROL.HTLC_ser)
        print(ALICE.HTLC_output_ser)



# curl -X POST \
#   https://api.cryptoapis.io/v1/bc/btc/testnet/txs/send/ \
#   -H 'Content-Type: application/json' \
#   -H 'X-API-Key: c186f1a43625f540e474a1653f4e5ccfe6003c3a' \
#   -d '{
#     "hex" : "02000000012ef6ff4aaa76aaff4bea235df134923a830a89d2fbdea5fdc330c9a42eb920a8010000006a47304402205c44fb58b3eaa907cccb2cac87749f00cb52f0d050d183ebba80d672413b9a540220749c8b53665db9f36d5e760ad627b0e22072a6cf91a5d77d35ac2b95d4c1ea54012102275753690ab58df3c923001e94d407e30b03e60b1f2461729a1dd4f37ebe2469ffffffff02c8320000000000001976a914481e003d23566c1789dc9362085c3a0876570c7c88ac80380100000000001976a9147b9a627a184897f10d31d73d87c2eea191d8f50188ac00000000"
#   }'