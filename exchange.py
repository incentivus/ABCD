from typing import Tuple

from bitcoinutils.utils import to_satoshis

from bondissuer import BondIssuer
from config import DEFAULT_TX_FEE
from participant import *
from bitcoinutils.setup import setup

from scripts import *

utxos = [
    "5ff91695b039a7f38b70b65e0f371156f7394051de235335b1e5cc821ec5c74a",
    "66964fb0dd3ef7fe92cc1ac1b6acf00a500c7e8289418f8830b638b6244d1c9d",
    "7d3636702838ae05b708ebf789258b6507f65b2d80fdb4764e744e5c6df6cdc1",
    "db30a977a11273891dc9d9abe028c0205de2ba7a204d169c13fe59c2a1f86ef1",
    "ac9c46b046729f7b2043597bb0bf40b5a97242da448ba22b1e6557d9a90dc97c",
    "cfd9bc8b2c9d90ead1801e5c3f3f4670aeae75f5efdb37e0c14803173209a974",
    "0f1c04260ac1dc3472579f893ee5cfeb65ce2b7c56f9f70aad5f420bd5b9c025",
    "726a7c822d550b7292f94178820f954c2f39dbb31f99380ed766504d9cbf8554",
    "9b232a582a59fa8924a8e82ffff2cf61ae6333fe3c72a5bf4699d5c28a6a745b",
    "fe67face64981e5af34d40f16d42d5edc423564754ed97297c94149958015495",
    "666b873f128c78b200a3f5d322475d9973d107e576bb07149b82321e5f1fcd2d",
    "f32e36fc004c1536a21ef074b6f218d499a20a8c9c43d2f4f13ae7b79a3b7998",
    "500a5fd6d47a851a26123adf6e91150a03f4442a826f200e31e98a200a828c3a",
    "f00c433ee829f448be79f35eb87792d1c2c125deedc7e485da291f988d6fd84b",
    "fd913ef30b003f3e4895ba958234004f53fb1d25f905ebdb043e6c053a18a1d2",
    "08f75674285199ad0d4d722290818c6eef23713c05616d2951bebedfb6dba82a",
    "1a6cd9830d6e95ed773e2893849ed5235a88b8e9158a832f49ae1d178a252691",
    "34b33cc7be5aece1c4a25d6fc000ebd085606454f91df6be09dac9e67f1d7f83",
    "494e443866027532d8cb76be736c863a18e1a7ad660ae6b8fc838c40421efbcd",
    "200900629d304e310f0d0d625eaf8b53823c4a06c99a4ff916465a7e57c1d232",
    "615736c83df68cfbcb3b39838347e728621632c9d804166634828b84f0bdca81",
    "f680a1136b5974f4bcef0b0e610f818cfdb71d2693e0f246cf8120a12b589889",
    "33a5bd991a1a2af5356f3ab017f4d6368cf6096ba7d599f8d6ee9da1a8af792c",
    "6c7a46940bb3aa3fec8b416e77845c56d77489d2656de76f808fea1ef610b92c",
    "7578cfe2e63a932f01b12361f4abb0af9e159768471569c6efe339cbb7636199",
    "bf4e4ae11bd9f14d6af539675c88ec0d7e899b70da56e109d7d119eb26ebfbfb",
    "24d3596d4d1a1b8da6a606397763f798987f484f3328790ed120b8151f24456a",
    "feb99fe776061a4bf2f6b32bc6218e8e3536cb7de477672fe67036b06986f790",
    "063916fd1d81a62a8ef16c042920c2a1d164dc0324f0f94d6d617cb5e29261aa",
    "844c65beadf6c05d176f8beb2d89e7f8b2bd03456ad09cb5100119082b38272d",
    "a8d207ea796c043d78458d971499331a86cc0e775ee2770884fb8a8217e29ca9",
    "93eb61c76d0af1b75fbac191128e70906ef548cf9743385796177d6f3589bce6",
    "e45031224c87b369dd9503a833adbf2877c0c94c40380df57d7cdf48c409df8b",
    "05bbc2dc91b516e85e420f0983dccaa7945daab5218f1d68f4d158470e410f95",
    "98c293ac8de8b4db259b2952be7c5caa5542d572527f7f9c85cea4583c167ae6",
    "7f402585b5cbf2e04d8e05975050d746a0a3a87b31077ad973edd3df0bc12829",
    "ad440da3a77a367a92b794348e356646425ec33aa3da0f405c8333096a8b8dec",
    "9be84c2a1bba9bba6ed07670259ebdd50355ee11ab0ce32b7a3ce8c3ab75bafa",
    "49be0738d6de553c17c7de1c5c4ca548ebfb22f701d23a13a07824b5c34d3eec",
    "d7e7b8626753ca9a2bdb305737ff48b7fc19eef618e37a15f4aa06d72f6e4303",
    "968b44d88e2300b1b23683c6a03d049437bfecaeda2ba5234e3ccb17864628ac",
    "ed26a51e4905f544a4ffbdbb1a767329676aa9302e55a02dc42fa69edd600f37",
    "c3755e745ce3c80fe39024805ac4dca425694de59c3ec8c5c0ff7c65aff39ff0",
    "94e4db36a0a496f4443630e7f09ff3870a66192183c7fdc8a3a0feccd6f0521c",
    "a5e1c2f634e24dbfc6b4984ac4984ff3b7810517e1e7cac0cd99a4f79acae55d",
    "61540178b81df436d1813e3f65f72cb05bcad57fc6bfc71110aedfa6e5e112ef",
    "0ec13830f28c956d46dcae11545143bf5655cd7b14ada7928a35cba98b3bf088",
    "9a4bd9d9f8195ff52f7af64256bfba4dbf3b269a369735b43c91a8957582dbe7",
    "39f5b4e375ab42a2a04ce985832ca591aa73ca870a439c8c9814ffd24a8783bc",
    "d533f10c001ccab84541b91f4a98bbc607494136bd5a35cad92c8fb7b4b4196c",
    "65397c51b0725991c83a2f4e67dc0b6707b725aefeb24c594cd1f2e6909928b5",
]


class Exchange(Participant):
    HTLC_tx: Transaction
    HTLC_ser: str

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def send_to_p2pkh(self):
        transaction = Transaction([], [])
        for utxo in utxos:
            txin = TxInput(utxo, 0)
            addr = self.public_key.get_address()
            txout = TxOutput(to_satoshis(0.00099), addr.to_script_pub_key())
            transaction.inputs.append(txin)
            transaction.outputs.append(txout)
            # transaction = Transaction([txin], [txout])
        for i in range(len(utxos)):
            self.sign_p2pkh(transaction, i)
        return transaction

    def make_HTLC(self,
                  recipient_pubkeyhash: str,
                  utxo: UTXO,
                  locktime: int,
                  bob_principal_utxo: UTXO,
                  fee: int = DEFAULT_TX_FEE,
                  ) -> Tuple[Transaction, UTXO]:
        amount_to_send = utxo.value - fee
        txout_script = HTLC_script(
            sender_address=self.pubkey_hash(network="bcy-tst"),
            recipient_address=recipient_pubkeyhash,
            secret_hash=bob_principal_utxo.redeem_script.script[11],
            locktime=locktime,
        )

        txin = utxo.create_tx_in()
        txout = TxOutput(
            amount_to_send,
            txout_script
        )
        self.HTLC_tx = Transaction([txin], [txout])
        self.sign_p2pkh(self.HTLC_tx, 0, network="bcy-tst")
        new_utxo = UTXO(
            txid=self.HTLC_tx.get_txid(),
            output_idx=0,
            value=amount_to_send,
            redeem_script=txout_script,
        )
        return self.HTLC_tx, new_utxo

    def commit_HTLC(self):
        self.HTLC_tx = Transaction.copy(self.HTLC_tx)
        self.HTLC_ser = self.HTLC_tx.serialize()


if __name__ == '__main__':

    # CAROL = Exchange(wif="Bqj17XDLkQA11SJcihX3qwwVC4PJWfQXxGh8V2gM1C8RCs5zxooi")
    # # CAROL.make_HTLC()
    # res = broadcast_transaction(CAROL.send_to_p2pkh().serialize(), "bcy-tst")
    # print(res.text)
    # print(res.status_code)
    BOB_SECRET = Secret("thisIsASecretPasswordForBob")
    ALICE_SECRET = Secret("thisIsASecretPasswordForAlice")

    # secret wifs
    ALICE = BondIssuer(wif='cPz2tG7YN1BD6WT4R65J5LnTUtZqgYMBaWGerp75GF2nP14aKtyW', funding_secret=ALICE_SECRET)
    ALICE.load_keys(wif='BsAupz3NaLSGQD83dL8h9QpC1SzGvZJbC8RCQyVztct8VqPvPRig', network="bcy-tst")
    BOB = Participant(wif='cRTBStSdJeYt3BV2JGfdJb46m8T67Ht7zm2pkKup6gwV6EqZkzvQ')
    CAROL = Exchange(wif="Bqj17XDLkQA11SJcihX3qwwVC4PJWfQXxGh8V2gM1C8RCs5zxooi")
    amount_to_send = 78000
    txin = TxInput("0e581acea0303f144286874cc7b6323e8f8bbc6e7ea7542b9cb77bfbea0e1662", 0.0008)

    txout = TxOutput(
        amount_to_send,
        ALICE.p2pkh_script_pubkey(network="bcy-tst")
    )
    script = Script(['OP_IF', '0a', 'OP_CHECKLOCKTIMEVERIFY', 'OP_DROP', 'OP_DUP', 'OP_HASH160',
                     '62bf547ee692288917084d1d388261395f102a10', 'OP_EQUALVERIFY', 'OP_CHECKSIG',
                     'OP_ELSE', 'OP_HASH160', '07b4173eaa22fae414733868111febf138c085ad', 'OP_EQUALVERIFY',
                     'OP_DUP', 'OP_HASH160', 'b7da4a15d5b8c2573da6981e75710d802888ed84', 'OP_EQUALVERIFY',
                     'OP_CHECKSIG', 'OP_ENDIF'])

    HTLC_output_tx = Transaction([txin], [txout])
    alice_sig = ALICE.secret_key_BCY.sign_input(tx=HTLC_output_tx, txin_index=0, script=script)
    HTLC_output_tx.inputs[0].script_sig = Script([alice_sig, ALICE.public_key_BCY.to_hex(), 'OP_0'])
    ALICE.broadcast_transaction(HTLC_output_tx.serialize(), "bcy-tst")

    print("Alice HTLC output transaction made. TXID:", HTLC_output_tx.get_txid())
