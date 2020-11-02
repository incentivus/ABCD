from core.utxo import *

alice_premium_amount = 41432  # 0.00110721
alice_principal_amount = 41432 + alice_premium_amount   # 0.00050000
bob_principal_amount = 69000  # + alice_premium_amount

DEFAULT_TX_FEE = 15000  # 0.00010000

payback_preiod = 10 # P
bob_deposition_preiod = 2 # M
bcy_height = 3109190
btc_height = 1865986 #1866007
minimum_locktime = 1 # T

alice_refund_locktime = 2 * minimum_locktime + btc_height
bob_refund_locktime = minimum_locktime + btc_height
bob_defaults_locktime = bob_deposition_preiod + btc_height
alice_defaults_locktime = payback_preiod + btc_height
bob_principal_deposit_locktime = payback_preiod + minimum_locktime + btc_height
alice_redemption_locktime = payback_preiod + 2 * minimum_locktime + btc_height
carol_htlc_locktime = alice_redemption_locktime

alice_reveals = True
bob_defaults = False # TODO
alice_defaults = False
bob_cheats = True

alice_utxo_to_spend = UTXO(
    # txid="090c1899cd46f4cb64c11c108ca97cc3165a96457b3a624f3fe205cdad6e31c5",
    txid="bbb1992be7e5642874fe3fac604048263531aa1e396d7d8f9c825cafd9aed8e4",
    output_idx=19,
    value=41432,  # 0.00120721
    redeem_script=None,
)

alice_fulfillment_utxo = UTXO(
    # txid="c4543cfa2ce6675bbf1ca1ea1ce05eeb7acbd2a43e528ac92e06b438b7271a98",
    # txid="090c1899cd46f4cb64c11c108ca97cc3165a96457b3a624f3fe205cdad6e31c5",
    txid="bbb1992be7e5642874fe3fac604048263531aa1e396d7d8f9c825cafd9aed8e4",
    output_idx=20,
    value=41432,  # 0.00100721
    redeem_script=None  # should this be something?
)

bob_utxo_to_spend = UTXO(
    txid="1897e153c74bf86489c52d1f19c256911388979f8494ffb89344ca826cea6f03",
    output_idx=29,
    value=49833,  # 0.00049833
    redeem_script=None  # should this be something?
)
bob_fulfillment_utxo = UTXO(
    txid="1897e153c74bf86489c52d1f19c256911388979f8494ffb89344ca826cea6f03",
    output_idx=30,
    value=49833,  # 0.00049833
    redeem_script=None  # should this be something?
)

# BCY network
carol_utxo_to_spend = UTXO(
    txid="280f6b3f36ead225f86d22d6e5c4569d0c118265f1d576a29b5ffc01af05c225",
    output_idx=14,
    value=98000,  # 0.00099
    redeem_script=None,
)