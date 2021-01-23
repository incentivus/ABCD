# unspent transaction output
from typing import Optional
import bitcoinutils.transactions as btctrans
import litecoinutils.transactions as ltctrans


def get_network(network="btctest3"):
    return btctrans if network == "btc-test3" else ltctrans


def new_tx(
        inputs=None,
        outputs=None,
        witnesses=None,
        network="btc-test3",
        **kwargs
):
    return get_network(network).Transaction(
        inputs=inputs if inputs is not None else [],
        outputs=outputs if outputs is not None else [],
        witnesses=witnesses if witnesses is not None else [],
        **kwargs
    )


class UTXO:
    # txid: str
    # output_idx: int
    # value: int
    # redeem_script: Optional[Script]

    def __init__(
            self,
            txid: str,
            output_idx: int,
            value: int,
            redeem_script,
            network="btc-test3"
    ):
        self.network = network
        self.txid = txid
        self.output_idx = output_idx
        self.value = value
        self.redeem_script = \
            None if redeem_script is None else get_network(network).Script.copy(redeem_script)

    def create_tx_in(self, network="btc-test3", **kwargs):
        return get_network(network).TxInput(self.txid, self.output_idx, **kwargs)
