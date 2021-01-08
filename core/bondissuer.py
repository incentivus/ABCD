from typing import Tuple

from core.scripts import *
from core.participant import *


class BondIssuer(Participant):
    funding_tx: btctrans.Transaction
    redemption_tx: btctrans.Transaction
    funding_ser: str
    redemption_ser: str
    _redemption_txout_script: btcscript.Script
    _redemption_output: int
    refund_tx: btctrans.Transaction
    margin_dep_tx: btctrans.Transaction
    margin_dep_ser: str
    guarantee_dep_tx = btctrans.Transaction  # todo: make serialized for guarantee and broadcast

    def __init__(self, funding_secret: Secret, **kwargs):
        super().__init__(**kwargs)
        self.funding_secret = funding_secret

    # def make_alice_refund_tx(self,
    #                          funding_utxo: UTXO,
    #                          network: str = "btc-test3",
    #                          fee: int = DEFAULT_TX_FEE
    #                          ) -> Transaction:
    #     amount_to_send = funding_utxo.value - fee
    #     txout = TxOutput(
    #         amount_to_send,
    #         self.p2pkh_script_pubkey(network=network)
    #     )
    #     txin = funding_utxo.create_tx_in()
    #     transaction = Transaction([txin], [txout], has_segwit=True)
    #     self.refund_tx = transaction
    #
    #     return self.refund_tx

    def make_alice_funding_tx(
            self,
            recipient_pubkey: btckeys.PublicKey,
            utxo: UTXO = alice_utxo_to_spend,
            fee: int = DEFAULT_TX_FEE
    ) -> Tuple[btctrans.Transaction, UTXO]:
        amount_to_send = utxo.value - fee
        txout_script = funding_script(
            network="btc-test3",
            sender_address=self.pubkey_hash(),
            sender_pubkey=self.public_key,
            recipient_pubkey=recipient_pubkey,
            secret=self.funding_secret.digest_hex(),
            locktime=alice_refund_locktime
        )
        txout = btctrans.TxOutput(
            amount_to_send,
            txout_script.to_p2wsh_script_pub_key()
        )
        txin = utxo.create_tx_in(network="btc-test3", sequence=(2 ** 32 - 1).to_bytes(4, "little"))

        transaction = new_tx([txin], [txout], has_segwit=True, network="btc-test3")
        new_utxo = UTXO(
            network="btc-test3",
            txid=transaction.get_txid(),
            output_idx=0,
            value=amount_to_send,
            redeem_script=txout_script,
        )

        self.funding_tx = transaction
        print("Alice funding transaction made. TXID:", self.funding_tx.get_txid())
        return transaction, new_utxo

    def make_redemption_tx(
            self,
            recipient_pubkeyhash: str,
            bob_principal_utxo: UTXO,
            # secret: str,
            utxo: UTXO,
            locktime: int,
            fee: int = DEFAULT_TX_FEE,
    ) -> btctrans.Transaction:
        self._redemption_output = alice_principal_amount - fee
        self._redemption_txout_script = HTLC_script(
            network="btc-test3",
            sender_address=self.pubkey_hash(network="btc-test3"),
            recipient_address=recipient_pubkeyhash,
            secret_hash=bob_principal_utxo.redeem_script.script[11],
            # secret_hash=secret,
            locktime=locktime,
        )

        txin = utxo.create_tx_in(network="btc-test3")
        txout = btctrans.TxOutput(self._redemption_output, self._redemption_txout_script)

        self.redemption_tx = btctrans.Transaction([txin], [txout], has_segwit=True)

        print("Alice premium redemption transaction made. TXID:", self.redemption_tx.get_txid())
        return self.redemption_tx

    def fulfill_redemption(
            self,
            redemption_tx: btctrans.Transaction,
            utxo: UTXO,
    ) -> [btctrans.Transaction, UTXO]:
        txin = utxo.create_tx_in(network="btc-test3")
        self.redemption_tx.inputs.append(txin)
        new_utxo = UTXO(
            txid=self.redemption_tx.get_txid(),
            output_idx=0,
            value=self._redemption_output,
            redeem_script=self._redemption_txout_script,
            network="btc-test3"
        )
        print("Alice redemption transaction fulfilled.")
        return redemption_tx, new_utxo

    def get_redemption_utxo(self) -> UTXO:
        return UTXO(
            network="btc-test3",
            txid=self.redemption_tx.get_txid(),
            output_idx=0,
            value=self._redemption_output,
            redeem_script=self._redemption_txout_script
        )

    '''
    Commit to a transaction by early serializing. We need this due to lack of immutable 
    transaction support on underlying library.
    '''

    def commit_funding(self, alice_sig):
        self.funding_tx.witnesses.append(
            btcscript.Script([alice_sig, self.public_key.to_hex()])
        )
        self.funding_tx = btctrans.Transaction.copy(self.funding_tx)
        self.funding_ser = self.funding_tx.serialize()

    def commit_redemption(self, gu_alice_sig, gu_bob_sig, alice_sig_ff, bob_guarantee_dep_utxo: UTXO):
        self.redemption_tx.witnesses.append(btcscript.Script(
            [
                'OP_FALSE',
                gu_bob_sig,
                gu_alice_sig,
                'OP_FALSE',
                bob_guarantee_dep_utxo.redeem_script.to_hex()
            ]
        ))

        self.redemption_tx.witnesses.append(
            btcscript.Script([alice_sig_ff, self.public_key.to_hex()])
        )
        self.redemption_tx = btctrans.Transaction.copy(self.redemption_tx)
        self.redemption_ser = self.redemption_tx.serialize()

    def make_margin_deposit_tx(
            self,
            bob_pubkey: btckeys.PublicKey,
            utxo: UTXO,
            locktime: int = bob_defaults_locktime,
            fee: int = DEFAULT_TX_FEE,
    ) -> Tuple[btctrans.Transaction, UTXO]:
        amount_to_send = utxo.value - fee
        txout_script = margin_dep_script(
            network="btc-test3",
            sender_pubkey=bob_pubkey,
            recipient_pubkey=self.public_key,
            recipient_address=self.pubkey_hash("btc-test3"),
            locktime=locktime
        )

        txin = utxo.create_tx_in(network="btc-test3")
        txout = btctrans.TxOutput(
            amount_to_send,
            txout_script.to_p2wsh_script_pub_key()
        )

        transaction = new_tx([txin], [txout], has_segwit=True, network="btc-test3")

        new_utxo = UTXO(
            network="btc-test3",
            txid=transaction.get_txid(),
            output_idx=0,
            value=amount_to_send,
            redeem_script=txout_script,
        )
        self.margin_dep_tx = transaction

        # print("Bob margin deposition transaction made. TXID:", self.margin_dep_tx.get_txid())
        return transaction, new_utxo

    def commit_margin_dep(self, bob_sig, alice_sig, bob_funding_script):
        self.margin_dep_tx.witnesses.append(
            btcscript.Script([
                'OP_FALSE',
                alice_sig,
                bob_sig,
                self.funding_secret.hex(),  # todo: needs to get it from Alice
                'OP_FALSE',
                bob_funding_script
            ]))
        self.margin_dep_tx = btctrans.Transaction.copy(self.margin_dep_tx)
        self.margin_dep_ser = self.margin_dep_tx.serialize()

    def make_guarantee_deposit_tx(
            self,
            bob_pubkey: btckeys.PublicKey,
            bob_address: str,
            utxo: UTXO,
            locktime: int = bob_guarantee_locktime,
            fee: int = DEFAULT_TX_FEE,
    ) -> Tuple[btctrans.Transaction, UTXO]:
        amount_to_send = utxo.value - fee
        txout_script = guarantee_dep_script(
            network="btc-test3",
            sender_pubkey=bob_pubkey,  # TODO here we made a mess ...  To be fixed later
            recipient_pubkey=self.public_key,
            recipient_address=bob_address,
            locktime=locktime
        )

        txin = utxo.create_tx_in(network="btc-test3")
        txout = btctrans.TxOutput(
            amount_to_send,
            txout_script.to_p2wsh_script_pub_key()
        )

        transaction = new_tx([txin], [txout], has_segwit=True, network="btc-test3")

        new_utxo = UTXO(
            network="btc-test3",
            txid=transaction.get_txid(),
            output_idx=0,
            value=amount_to_send,
            redeem_script=txout_script,
        )
        self.guarantee_dep_tx = transaction

        # print("Bob guarantee deposition transaction made. TXID:", self.margin_dep_tx.get_txid())
        return transaction, new_utxo

    def commit_guarantee_dep(self, bob_sig, alice_sig, bob_funding_2_script):
        self.guarantee_dep_tx.witnesses.append(
            btcscript.Script([
                'OP_FALSE',
                alice_sig,
                bob_sig,
                self.funding_secret.hex(),  # todo: needs to get it from Alice
                'OP_FALSE',
                bob_funding_2_script
            ]))
        self.guarantee_dep_tx = btctrans.Transaction.copy(self.guarantee_dep_tx)
        self.guarantee_dep_ser = self.guarantee_dep_tx.serialize()
