from typing import Tuple

from core.config import *
from core.scripts import *


class BondBuyer(Participant):
    funding_tx: Transaction
    margin_dep_tx: Transaction
    principal_tx: Transaction
    margin_dep_ser: str
    funding_ser: str
    principal_ser: str
    _principal_amount: int
    _principal_script: Script

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

    def make_margin_deposit_tx(
            self,
            recipient_pubkey: PublicKey,
            recipient_pubkeyhash: str,
            utxo: UTXO,
            locktime: int = bob_principal_deposit_locktime,
            fee: int = DEFAULT_TX_FEE,
    ) -> Tuple[Transaction, UTXO]:
        amount_to_send = utxo.value - fee
        txout_script = margin_dep_script(
            sender_pubkey=self.public_key,
            recipient_pubkey=recipient_pubkey,
            recipient_address=recipient_pubkeyhash,
            locktime=locktime
        )

        txin = utxo.create_tx_in()
        txout = TxOutput(
            amount_to_send,
            txout_script.to_p2wsh_script_pub_key()
        )

        transaction = new_tx([txin], [txout], has_segwit=True)

        new_utxo = UTXO(
            txid=transaction.get_txid(),
            output_idx=0,
            value=amount_to_send,
            redeem_script=txout_script,
        )
        self.margin_dep_tx = transaction

        print("Bob margin deposition transaction made. TXID:", self.margin_dep_tx.get_txid())
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

    def commit_margin_dep(self, bob_sig, alice_sig, bob_funding_script, funding_secret: Secret):
        self.margin_dep_tx.witnesses.append(
            Script([
                'OP_FALSE',
                bob_sig,
                alice_sig,
                funding_secret.hex(),  # todo: needs to get it from Alice
                'OP_FALSE',
                bob_funding_script
            ]))
        self.margin_dep_tx = Transaction.copy(self.margin_dep_tx)
        self.margin_dep_ser = self.margin_dep_tx.serialize()

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
