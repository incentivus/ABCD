class ContractBuilder:

    def make_HTLC(self,
                  recipient_pubkeyhash: str,
                  utxo: UTXO,
                  locktime: int,
                  secret_hash: str,
                  fee: int = DEFAULT_TX_FEE,
                  ) -> Tuple[Transaction, UTXO]:
        amount_to_send = utxo.value - fee
        txout_script = HTLC_script(
            sender_address=self.pubkey_hash(network="bcy-tst"),
            recipient_address=recipient_pubkeyhash,
            secret_hash=secret_hash,
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
