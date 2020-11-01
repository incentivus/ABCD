# unspent transaction output
from typing import Optional
from bitcoinutils.transactions import *


def new_tx(
    inputs=None,
    outputs=None,
    witnesses=None,
    **kwargs,
) -> Transaction:
    return Transaction(
        inputs=inputs if inputs is not None else [],
        outputs=outputs if outputs is not None else [],
        witnesses=witnesses if witnesses is not None else [],
        **kwargs,
    )


class UTXO:
    txid: str
    output_idx: int
    value: int
    redeem_script: Optional[Script]

    def __init__(
        self,
        txid: str,
        output_idx: int,
        value: int,
        redeem_script: Optional[Script]
    ):
        self.txid = txid
        self.output_idx = output_idx
        self.value = value
        self.redeem_script = \
            None if redeem_script is None else Script.copy(redeem_script)

    def create_tx_in(self) -> TxInput:
        return TxInput(self.txid, self.output_idx)
