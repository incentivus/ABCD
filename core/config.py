from core.utxo import *

alice_premium_amount = 41432  # 0.00110721
alice_principal_amount = 41432 + alice_premium_amount   # 0.00050000
bob_principal_amount = 69000  # + alice_premium_amount
bob_margin_amount = 49833
bob_guarantee_amount = 49833
carol_htlc_amount = 98000

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
bob_principal_deposit_locktime = payback_preiod + 2 * minimum_locktime + btc_height
alice_redemption_locktime = payback_preiod + minimum_locktime + btc_height
carol_htlc_locktime = alice_redemption_locktime
bob_guarantee_locktime = payback_preiod + btc_height

asyncState = type('', (), {})()
asyncState.start = ['T', 'F', 'P'][2]
asyncState.alice_reveals = ['T', 'F', 'P'][2] # True False Pending
asyncState.bob_defaults = ['T', 'F', 'P'][2]
asyncState.alice_defaults = ['T', 'F', 'P'][2]
asyncState.bob_cheats = ['T', 'F', 'P'][2]
asyncState.next = ['T', 'F', 'P'][2]

alice_utxo_to_spend = UTXO(
    # txid="090c1899cd46f4cb64c11c108ca97cc3165a96457b3a624f3fe205cdad6e31c5",
    txid="bbb1992be7e5642874fe3fac604048263531aa1e396d7d8f9c825cafd9aed8e4",
    # txid="6a5a0831134059126f10d45200d6c4723dc502572926a00c7958467649a42fbd",
    output_idx=41,
    # output_idx=0,
    value=41432,  # 0.00120721
    # value=11432,
    redeem_script=None,
)

alice_fulfillment_utxo = UTXO(
    # txid="c4543cfa2ce6675bbf1ca1ea1ce05eeb7acbd2a43e528ac92e06b438b7271a98",
    # txid="090c1899cd46f4cb64c11c108ca97cc3165a96457b3a624f3fe205cdad6e31c5",
    txid="bbb1992be7e5642874fe3fac604048263531aa1e396d7d8f9c825cafd9aed8e4",
    output_idx=42,
    value=41432,  # 0.00100721
    redeem_script=None  # should this be something?
)

bob_utxo_to_spend = UTXO(
    txid="1897e153c74bf86489c52d1f19c256911388979f8494ffb89344ca826cea6f03",
    output_idx=43, # 43
    value=49833,  # 0.00049833
    redeem_script=None  # should this be something?
)
bob_fulfillment_utxo = UTXO(
    txid="1897e153c74bf86489c52d1f19c256911388979f8494ffb89344ca826cea6f03",
    output_idx=44, # 44
    value=49833,  # 0.00049833
    redeem_script=None  # should this be something?
)
bob_guarantee_utxo = UTXO(
    txid="1897e153c74bf86489c52d1f19c256911388979f8494ffb89344ca826cea6f03",
    output_idx=45, # 44
    value=49833,  # 0.00049833
    redeem_script=None  # should this be something?
)
# BCY network
carol_utxo_to_spend = UTXO(
    txid="280f6b3f36ead225f86d22d6e5c4569d0c118265f1d576a29b5ffc01af05c225",
    output_idx=16,
    value=98000,  # 0.00099
    redeem_script=None,
)
