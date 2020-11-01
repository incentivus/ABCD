from utxo import *

alice_premium_amount = 41432  # 0.00110721
alice_principal_amount = 41432 + alice_premium_amount   # 0.00050000
bob_principal_amount = 69000 # + alice_premium_amount

DEFAULT_TX_FEE = 10000  # 0.00010000

payback_locktime = 10
bcy_height = 3109190
btc_height = 1865819
minimum_locktime = 2

bob_principal_locktime = payback_locktime + 2 * minimum_locktime + btc_height
alice_redemption_locktime = payback_locktime + minimum_locktime + btc_height
alice_premium_locktime = payback_locktime + btc_height
alice_funding_locktime = 2 * minimum_locktime + btc_height
bob_funding_locktime = minimum_locktime + btc_height
carol_htlc_locktime = alice_redemption_locktime

alice_utxo_to_spend = UTXO(
    # txid="090c1899cd46f4cb64c11c108ca97cc3165a96457b3a624f3fe205cdad6e31c5",
    txid="bbb1992be7e5642874fe3fac604048263531aa1e396d7d8f9c825cafd9aed8e4",
    output_idx=16,
    value=41432,  # 0.00120721
    redeem_script=None,
)

# BCY network
carol_utxo_to_spend = UTXO(
    txid="280f6b3f36ead225f86d22d6e5c4569d0c118265f1d576a29b5ffc01af05c225",
    output_idx=6,
    value=98000,  # 0.00099
    redeem_script=None,
)

alice_fulfillment_utxo = UTXO(
    # txid="c4543cfa2ce6675bbf1ca1ea1ce05eeb7acbd2a43e528ac92e06b438b7271a98",
    # txid="090c1899cd46f4cb64c11c108ca97cc3165a96457b3a624f3fe205cdad6e31c5",
    txid="bbb1992be7e5642874fe3fac604048263531aa1e396d7d8f9c825cafd9aed8e4",
    output_idx=17,
    value=41432,  # 0.00100721
    redeem_script=None  # should this be something?
)

bob_utxo_to_spend = UTXO(
    txid="1897e153c74bf86489c52d1f19c256911388979f8494ffb89344ca826cea6f03",
    output_idx=26,
    value=49833,  # 0.00049833
    redeem_script=None  # should this be something?
)
bob_fulfillment_utxo = UTXO(
    txid="1897e153c74bf86489c52d1f19c256911388979f8494ffb89344ca826cea6f03",
    output_idx=27,
    value=49833,  # 0.00049833
    redeem_script=None  # should this be something?
)