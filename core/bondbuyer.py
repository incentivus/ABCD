from typing import Tuple

from core.scripts import *
from bitcoinutils.transactions import *


class BondBuyer(Participant):
    funding_tx: Transaction
    principal_tx: Transaction
    funding_2_tx: Transaction
    refund_2_tx: Transaction
    premium_dep_tx: Transaction
    withdraw_tx = Transaction
    premium_dep_ser: str
    funding_ser: str
    funding_2_ser: str
    refund_2_ser: str
    principal_ser: str
    _principal_amount: int
    _principal_script: Script
    guarantee_dep_tx: Transaction
    guarantee_dep_ser: str
    withdraw_ser: str

    def __init__(self, principal_secret: Secret, **kwargs):
        super().__init__(**kwargs)
        self.principal_secret = principal_secret

    def make_bob_funding_tx(
            self,
            recipient_pubkey: PublicKey,
            alice_funding_utxo: UTXO,
            utxo: UTXO = bob_utxo_to_spend,
            fee: int = DEFAULT_TX_FEE
    ) -> Tuple[Transaction, UTXO]:
        amount_to_send = utxo.value - fee
        txout_script = funding_script(
            sender_address=self.pubkey_hash(),
            sender_pubkey=self.public_key,
            recipient_pubkey=recipient_pubkey,
            secret=alice_funding_utxo.redeem_script.script[13],
            locktime=bob_refund_locktime
        )
        txout = TxOutput(amount_to_send, txout_script.to_p2wsh_script_pub_key())
        txin = utxo.create_tx_in()

        transaction = new_tx([txin], [txout], has_segwit=True)

        new_utxo = UTXO(
            txid=transaction.get_txid(),
            output_idx=0,
            value=amount_to_send,
            redeem_script=txout_script,
        )

        self.funding_tx = transaction
        print("Bob funding transaction made. TXID:", self.funding_tx.get_txid())
        return transaction, new_utxo

    def make_bob_funding_2_tx(
            self,
            recipient_pubkey: PublicKey,
            alice_funding_utxo: UTXO,
            utxo: UTXO = bob_utxo_to_spend,
            fee: int = DEFAULT_TX_FEE
    ) -> Tuple[Transaction, UTXO]:
        amount_to_send = utxo.value - fee
        txout_script = funding_script(
            sender_address=self.pubkey_hash(),
            sender_pubkey=self.public_key,
            recipient_pubkey=recipient_pubkey,
            secret=alice_funding_utxo.redeem_script.script[13],
            locktime=bob_refund_locktime
        )
        txout = TxOutput(amount_to_send, txout_script.to_p2wsh_script_pub_key())
        txin = utxo.create_tx_in()

        transaction = new_tx([txin], [txout], has_segwit=True)

        new_utxo = UTXO(
            txid=transaction.get_txid(),
            output_idx=0,
            value=amount_to_send,
            redeem_script=txout_script,
        )

        self.funding_2_tx = transaction
        print("Bob funding 2 transaction made. TXID:", self.funding_2_tx.get_txid())
        return transaction, new_utxo

    def make_principal_tx(
            self,
            recipient_pubkeyhash: str,
            utxo: UTXO,
            locktime: int,
            fee: int = DEFAULT_TX_FEE,
    ) -> Tuple[Transaction, UTXO]:
        self._principal_amount = bob_principal_amount-fee
        self._principal_script = HTLC_script(
            sender_address=self.pubkey_hash(network="btc-test3"),
            recipient_address=recipient_pubkeyhash,
            secret_hash=self.principal_secret.digest_hex(),
            locktime=locktime
        )

        txin = utxo.create_tx_in()
        txout = TxOutput(
            self._principal_amount,
            self._principal_script
        )

        self.principal_tx = Transaction([txin], [txout], has_segwit=True)
        new_utxo = UTXO(
            txid=self.principal_tx.get_txid(),
            output_idx=0,
            value=self._principal_amount,
            redeem_script=self._principal_script,
        )

        print("Bob principal deposition transaction made. TXID:", self.principal_tx.get_txid())
        return self.principal_tx, new_utxo

    def fulfill_principal(
            self,
            principal_tx: Transaction,
            utxo: UTXO,
    ) -> Transaction:
        txin = utxo.create_tx_in()
        self.principal_tx.inputs.append(txin)

        print("Bob principal deposition transaction fulfilled.")
        return principal_tx

    def get_principal_utxo(self) -> UTXO:
        return UTXO(
            txid=self.principal_tx.get_txid(),
            output_idx=0,
            value=self._principal_amount,
            redeem_script=self._principal_script,
        )

    '''
    Commit to a transaction by early serializing. We need this due to lack of immutable 
    transaction support on underlying library.
    '''
    def commit_funding(self, alice_sig):
        self.funding_tx.witnesses.append(
            Script([alice_sig, self.public_key.to_hex()])
        )
        self.funding_tx = Transaction.copy(self.funding_tx)
        self.funding_ser = self.funding_tx.serialize()

    def commit_funding_2(self, alice_sig):
        self.funding_2_tx.witnesses.append(
            Script([alice_sig, self.public_key.to_hex()])
        )
        self.funding_2_tx = Transaction.copy(self.funding_2_tx)
        self.funding_2_ser = self.funding_2_tx.serialize()

    def commit_principal(self, margin_bob_sig, margin_alice_sig, bob_sig_ff, bob_margin_dep_utxo: UTXO):
        self.principal_tx.witnesses.append(Script(
            [
                'OP_FALSE',
                margin_bob_sig,
                margin_alice_sig,
                'OP_FALSE',
                bob_margin_dep_utxo.redeem_script.to_hex()
            ]
        ))

        self.principal_tx.witnesses.append(
            Script([bob_sig_ff, self.public_key.to_hex()])
        )
        self.principal_tx = Transaction.copy(self.principal_tx)
        print(self.principal_tx.get_txid())
        self.principal_ser = self.principal_tx.serialize()

    def commit_refund_2(self,
                      sig: str,
                      funding_script: hex,
                      network="btc-test3"):
        if network == "btc-test3":
            self.refund_2_tx.witnesses.append(
                Script([sig, self.public_key.to_hex(), self.public_key.to_hex(), funding_script])
            )
        elif network == "bcy-tst":
            self.refund_2_tx.witnesses.append(
                Script([sig, self.public_key_BCY.to_hex(), self.public_key_BCY.to_hex(), funding_script])
            )
        self.refund_2_tx = Transaction.copy(self.refund_2_tx)
        self.refund_2_ser = self.refund_2_tx.serialize()
        print(self.name, "refund transaction created.")

    def make_refund_2_tx(self,
                       locktime: int,
                       funding_utxo: UTXO,
                       network: str = "btc-test3",
                       fee: int = DEFAULT_TX_FEE,
                       ) -> Transaction:
        amount_to_send = funding_utxo.value - fee
        txout = TxOutput(
            amount_to_send,
            self.p2pkh_script_pubkey(network=network)
        )
        txin = funding_utxo.create_tx_in(sequence=0xFFFFFFFE.to_bytes(4, "little"))
        transaction = new_tx([txin], [txout], has_segwit=True, locktime=locktime.to_bytes(4, "little"))
        self.refund_2_tx = transaction

        return self.refund_2_tx

    def make_withdraw_tx(self,
                       locktime: int,
                       guarantee_utxo: UTXO,
                       network: str = "btc-test3",
                       fee: int = DEFAULT_TX_FEE,
                       ) -> Transaction:
        amount_to_send = guarantee_utxo.value - fee
        txout = TxOutput(
            amount_to_send,
            self.p2pkh_script_pubkey(network=network)
        )
        txin = guarantee_utxo.create_tx_in(sequence=0xFFFFFFFE.to_bytes(4, "little"))
        transaction = new_tx([txin], [txout], has_segwit=True, locktime=locktime.to_bytes(4, "little"))
        self.withdraw_tx = transaction

        return self.withdraw_tx

    def commit_withdraw(self,
                      sig: str,
                      guarantee_script: hex,
                      network="btc-test3"):
        if network == "btc-test3":
            self.withdraw_tx.witnesses.append(
                Script([sig, self.public_key.to_hex(), self.public_key.to_hex(), guarantee_script])
            )
        elif network == "bcy-tst":
            self.withdraw_tx.witnesses.append(
                Script([sig, self.public_key_BCY.to_hex(), self.public_key_BCY.to_hex(), guarantee_script])
            )
        self.withdraw_tx = Transaction.copy(self.withdraw_tx)
        self.withdraw_ser = self.withdraw_tx.serialize()
        print(self.name, "withdraw transaction created.")

    def make_prem_deposit_tx(
            self,
            recipient_pubkey: PublicKey,
            utxo: UTXO,
            fee: int = DEFAULT_TX_FEE,
    ) -> Tuple[Transaction, UTXO]:
        amount_to_send = utxo.value - fee
        txout_script = recipient_pubkey.get_address().to_script_pub_key()

        txin = utxo.create_tx_in()
        txout = TxOutput(
            amount_to_send,
            txout_script.to_hex()
        )

        transaction = new_tx([txin], [txout], has_segwit=True)

        new_utxo = UTXO(
            txid=transaction.get_txid(),
            output_idx=0,
            value=amount_to_send,
            redeem_script=txout_script,
        )
        self.premium_dep_tx = transaction

        print("Alice premium deposition transaction made. TXID:", self.premium_dep_tx.get_txid())
        return transaction, new_utxo

    def commit_premium_dep(self, alice_sig, bob_sig, alice_funding_script, secret: Secret):
        self.premium_dep_tx.witnesses.append(
            Script([
                'OP_FALSE',
                alice_sig,
                bob_sig,
                secret.hex(),
                'OP_FALSE',
                alice_funding_script
            ]))
        self.premium_dep_tx = Transaction.copy(self.premium_dep_tx)
        self.premium_dep_ser = self.premium_dep_tx.serialize()

    # def make_guarantee_deposit_tx(
    #         self,
    #         recipient_pubkey: PublicKey,
    #         recipient_pubkeyhash: str,
    #         utxo: UTXO,
    #         locktime: int = bob_guarantee_locktime,
    #         fee: int = DEFAULT_TX_FEE,
    # ) -> Tuple[Transaction, UTXO]:
    #     amount_to_send = utxo.value - fee
    #     txout_script = guarantee_dep_script(
    #         sender_pubkey=self.public_key,
    #         recipient_pubkey=self.public_key,
    #         recipient_address=self.public_key.get_address(),
    #         locktime=locktime
    #     )
    #
    #     txin = utxo.create_tx_in()
    #     txout = TxOutput(
    #         amount_to_send,
    #         txout_script.to_p2wsh_script_pub_key()
    #     )
    #
    #     transaction = new_tx([txin], [txout], has_segwit=True)
    #
    #     new_utxo = UTXO(
    #         txid=transaction.get_txid(),
    #         output_idx=0,
    #         value=amount_to_send,
    #         redeem_script=txout_script,
    #     )
    #     self.guarantee_dep_tx = transaction
    #
    #     print("Bob margin deposition transaction made. TXID:", self.guarantee_dep_tx.get_txid())
    #     return transaction, new_utxo
    #
    # def commit_guarantee_dep(self, bob_sig, alice_sig, bob_funding_script):
    #     self.guarantee_dep_tx.witnesses.append(
    #         Script([
    #             'OP_FALSE',
    #             bob_sig,
    #             alice_sig,
    #             self.funding_secret.hex(),  # todo: needs to get it from Alice
    #             'OP_FALSE',
    #             bob_funding_script
    #         ]))
    #     self.guarantee_dep_tx = Transaction.copy(self.guarantee_dep_tx)
    #     self.guarantee_dep_ser = self.guarantee_dep_tx.serialize()
