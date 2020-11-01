from typing import Tuple

from participant import *
from config import *
from scripts import *


class BondIssuer(Participant):
    funding_tx: Transaction
    premium_dep_tx: Transaction
    redemption_tx: Transaction
    premium_dep_ser: str
    funding_ser: str
    redemption_ser: str
    _redemption_txout_script: Script
    _redemption_output: int
    refund_tx: Transaction

    def __init__(self, funding_secret: Secret, **kwargs):
        super().__init__(**kwargs)
        self.funding_secret = funding_secret

    def make_alice_refund_tx(self,
                             funding_utxo: UTXO,
                             network: str = "btc-test3",
                             fee: int = DEFAULT_TX_FEE
                             ) -> Transaction:
        amount_to_send = funding_utxo.value - fee
        txout = TxOutput(
            amount_to_send,
            self.p2pkh_script_pubkey(network=network)
        )
        txin = funding_utxo.create_tx_in()
        transaction = Transaction([txin], [txout], has_segwit=True)
        self.refund_tx = transaction

        return self.refund_tx

    def make_alice_funding_tx(
            self,
            recipient_pubkey: PublicKey,
            utxo: UTXO = alice_utxo_to_spend,
            fee: int = DEFAULT_TX_FEE
    ) -> Tuple[Transaction, UTXO]:
        amount_to_send = utxo.value - fee
        txout_script = funding_script(
            sender_address=self.pubkey_hash(),
            sender_pubkey=self.public_key,
            recipient_pubkey=recipient_pubkey,
            secret=self.funding_secret.digest_hex(),
            locktime=alice_funding_locktime
        )
        txout = TxOutput(
            amount_to_send,
            txout_script.to_p2wsh_script_pub_key()
        )
        txin = utxo.create_tx_in()

        transaction = new_tx([txin], [txout], has_segwit=True)
        new_utxo = UTXO(
            txid=transaction.get_txid(),
            output_idx=0,
            value=amount_to_send,
            redeem_script=txout_script,
        )

        self.funding_tx = transaction
        print("Alice funding transaction made. TXID:", self.funding_tx.get_txid())
        return transaction, new_utxo

    def make_prem_deposit_tx(
            self,
            recipient_pubkey: PublicKey,
            recipient_pubkeyhash: str,
            utxo: UTXO,
            locktime: int = alice_redemption_locktime,
            fee: int = DEFAULT_TX_FEE,
    ) -> Tuple[Transaction, UTXO]:
        amount_to_send = utxo.value - fee
        txout_script = premium_dep_script(
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
        self.premium_dep_tx = transaction

        print("Alice premium deposition transaction made. TXID:", self.premium_dep_tx.get_txid())
        return transaction, new_utxo

    def make_redemption_tx(
            self,
            recipient_pubkeyhash: str,
            bob_principal_utxo: UTXO,
            utxo: UTXO,
            locktime: int,
            fee: int = DEFAULT_TX_FEE,
    ) -> Transaction:
        self._redemption_output = alice_principal_amount-fee
        self._redemption_txout_script = HTLC_script(
            sender_address=self.pubkey_hash(network="btc-test3"),
            recipient_address=recipient_pubkeyhash,
            secret_hash=bob_principal_utxo.redeem_script.script[11],
            locktime=locktime,
        )

        txin = utxo.create_tx_in()
        txout = TxOutput(self._redemption_output, self._redemption_txout_script)

        self.redemption_tx = Transaction([txin], [txout], has_segwit=True)

        print("Alice premium redemption transaction made. TXID:", self.redemption_tx.get_txid())
        return self.redemption_tx

    def fulfill_redemption(
            self,
            redemption_tx: Transaction,
            utxo: UTXO,
    ) -> [Transaction, UTXO]:
        txin = utxo.create_tx_in()
        self.redemption_tx.inputs.append(txin)
        new_utxo = UTXO(
            txid=self.redemption_tx.get_txid(),
            output_idx=0,
            value=self._redemption_output,
            redeem_script=self._redemption_txout_script
        )
        print("Alice redemption transaction fulfilled.")
        return redemption_tx, new_utxo

    def get_redemption_utxo(self) -> UTXO:
        return UTXO(
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
            Script([alice_sig, self.public_key.to_hex()])
        )
        self.funding_tx = Transaction.copy(self.funding_tx)
        self.funding_ser = self.funding_tx.serialize()

    def commit_refund(self,
                      alice_sig: str,
                      funding_utxo: UTXO):
        self.refund_tx.witnesses.append(
            Script([alice_sig, self.public_key.to_hex(), 1, funding_utxo.redeem_script.to_hex()])
        )
        self.refund_tx = Transaction.copy(self.refund_tx)
        self.refund_ser = self.refund_tx.serialize()
        print("Alice refund transaction created.")

    def commit_premium_dep(self, alice_sig, bob_sig, alice_funding_script):
        self.premium_dep_tx.witnesses.append(
            Script([
                'OP_FALSE',
                alice_sig,
                bob_sig,
                self.funding_secret.hex(),
                'OP_FALSE',
                alice_funding_script
            ]))
        self.premium_dep_tx = Transaction.copy(self.premium_dep_tx)
        self.premium_dep_ser = self.premium_dep_tx.serialize()

    def commit_redemption(self, premium_alice_sig, premium_bob_sig, alice_sig_ff, alice_premium_dep_utxo: UTXO):
        self.redemption_tx.witnesses.append(Script(
            [
                'OP_FALSE',
                premium_alice_sig,
                premium_bob_sig,
                'OP_FALSE',
                alice_premium_dep_utxo.redeem_script.to_hex()
            ]
        ))

        self.redemption_tx.witnesses.append(
            Script([alice_sig_ff, self.public_key.to_hex()])
        )
        self.redemption_tx = Transaction.copy(self.redemption_tx)
        self.redemption_ser = self.redemption_tx.serialize()

