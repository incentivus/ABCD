from bondbuyer import *
from bondissuer import *
from exchange import *

setup('testnet')

# secret used for HTLCs
ALICE_SECRET = Secret("thisIsASecretPasswordForAlice")
BOB_SECRET = Secret("thisIsASecretPasswordForBob")

# secret wifs
ALICE = BondIssuer(wif='cPz2tG7YN1BD6WT4R65J5LnTUtZqgYMBaWGerp75GF2nP14aKtyW',
                   funding_secret=ALICE_SECRET, network="btc-test3", name="Alice")
ALICE.load_keys(wif='BrhJV1kuGHxiL39kFFkRP5jj9okys645Jsp9DK9jvKdYhZCpMEZZ', network="bcy-tst")

BOB = BondBuyer(wif='cQVqxrx5bPLNnpTv87uWnfJ4dZawnKchKDLFkYdA5tZYRmAzoV5G',
                network="btc-test3", principal_secret=BOB_SECRET, name="Bob")

CAROL = Exchange(wif="Bqj17XDLkQA11SJcihX3qwwVC4PJWfQXxGh8V2gM1C8RCs5zxooi", network="bcy-tst", name="Carol")
CAROL.load_keys(wif='cTTf7ZSZRGP5RijYy1M5Tgd2RwdnxtWJqgFwKAyThAumn7s4s2GQ', network="btc-test3")

if __name__ == '__main__':

    # Alice creates funding     *
    # Alice shows Bob funding   *
    # Alice signs funding       *
    # Alice creates premium dep *
    # Bob signs premium dep     *
    # Alice signs premium dep   *
    # Alice creates redemption  *
    # Bob signs redemption      *
    # Alice signs redemption    *
    # Bob creates funding
    # Bob shows Alice funding
    # Bob signs funding
    # Bob creates margin
    # Alice signs margin
    # Bob creates principal
    # Alice signs principal

    # Alice broadcasts funding  *
    # Bob broadcasts funding
    # Alice broadcasts margin
    # Bob broadcasts premium    *
    # Bob fulfils principal
    # Bob broadcasts principal
    # Carol broadcasts HTLC
    # Alice fulfils redemption
    # Alice broadcasts redemp   *
    # Bob outputs redemption
    # Alice outputs Carol's principal
    # Carol outputs Bob's principal

    # --------------------------------- #

    # Alice creates funding
    alice_funding_tx, alice_funding_utxo = ALICE.make_alice_funding_tx(recipient_pubkey=BOB.public_key)

    # Alice shows Bob funding
    BOB.audit_transaction(alice_funding_tx, alice_funding_utxo)

    # Alice signs funding
    alice_sig = ALICE.make_segwit_signature(
        alice_funding_tx,
        0,
        alice_utxo_to_spend
    )
    ALICE.commit_funding(alice_sig)

    ################################### ALICE refund section ###################################
    # Alice creates refund
    alice_refund_tx = ALICE.make_alice_refund_tx(funding_utxo=alice_funding_utxo)

    # Alice signs refund
    alice_sig = ALICE.make_segwit_signature(
        alice_refund_tx,
        0,
        alice_funding_utxo
    )
    ALICE.commit_refund(alice_sig, funding_utxo=alice_funding_utxo)

    ############################################################################################

    # Bob creates funding
    bob_funding_tx, bob_funding_utxo = BOB.make_bob_funding_tx(recipient_pubkey=ALICE.public_key,
                                                               alice_funding_utxo=alice_funding_utxo,
                                                               utxo=bob_utxo_to_spend)
    # Bob shows Alice funding
    ALICE.audit_transaction(bob_funding_tx, bob_funding_utxo)

    # Bob signs funding
    bob_sig = BOB.make_segwit_signature(
        bob_funding_tx,
        0,
        bob_utxo_to_spend
    )
    BOB.commit_funding(bob_sig)

    # Alice creates premium dep
    alice_premium_dep_tx, alice_premium_dep_utxo = \
        ALICE.make_prem_deposit_tx(
            recipient_pubkey=BOB.public_key,
            recipient_pubkeyhash=BOB.pubkey_hash(),
            utxo=alice_funding_utxo,
            fee=(2 * DEFAULT_TX_FEE),
        )

    # Bob signs premium dep
    bob_sig = BOB.make_segwit_signature(
        alice_premium_dep_tx,
        0,
        alice_funding_utxo
    )

    # Alice signs premium dep
    alice_sig = ALICE.make_segwit_signature(
        alice_premium_dep_tx,
        0,
        alice_funding_utxo
    )
    ALICE.commit_premium_dep(alice_sig, bob_sig, alice_funding_utxo.redeem_script.to_hex())

    # Bob creates margin dep
    bob_margin_dep_tx, bob_margin_dep_utxo = \
        BOB.make_margin_deposit_tx(
            recipient_pubkey=ALICE.public_key,
            recipient_pubkeyhash=ALICE.pubkey_hash(),
            utxo=bob_funding_utxo,
            fee=(2 * DEFAULT_TX_FEE),
        )

    # Alice signs margin dep
    alice_sig_bob_margin = ALICE.make_segwit_signature(
        bob_margin_dep_tx,
        0,
        bob_funding_utxo
    )
    # Bob signs margin dep
    bob_sig_bob_margin = BOB.make_segwit_signature(
        bob_margin_dep_tx,
        0,
        bob_funding_utxo
    )

    # Bob creates principal
    bob_principal_tx, bob_principal_utxo = \
        BOB.make_principal_tx(
            recipient_pubkeyhash=CAROL.pubkey_hash("btc-test3"),
            utxo=bob_margin_dep_utxo,
            locktime=bob_principal_locktime,
            fee=3 * DEFAULT_TX_FEE,
        )

    # Alice signs principal
    alice_sig_bob_principal = ALICE.make_segwit_signature(
        tx=bob_principal_tx,
        input_idx=0,
        utxo=bob_margin_dep_utxo,
        sighash=(SIGHASH_ALL | SIGHASH_ANYONECANPAY)
    )

    # Bob signs principal
    bob_sig_bob_principal = BOB.make_segwit_signature(
        bob_principal_tx,
        0,
        bob_margin_dep_utxo,
        sighash=(SIGHASH_ALL | SIGHASH_ANYONECANPAY),
    )

    # Alice creates redemption
    alice_redm_tx = \
        ALICE.make_redemption_tx(
            recipient_pubkeyhash=BOB.pubkey_hash(network="btc-test3"),
            utxo=alice_premium_dep_utxo,
            locktime=payback_locktime,
            bob_principal_utxo=bob_principal_utxo,
            fee=3 * DEFAULT_TX_FEE,
        )

    # Bob signs redemption
    bob_sig_alice_redemption = BOB.make_segwit_signature(
        tx=alice_redm_tx,
        input_idx=0,
        utxo=alice_premium_dep_utxo,
        sighash=(SIGHASH_ALL | SIGHASH_ANYONECANPAY)
    )

    # Alice signs redemption
    alice_sig_alice_redemption = ALICE.make_segwit_signature(
        alice_redm_tx,
        0,
        alice_premium_dep_utxo,
        sighash=(SIGHASH_ALL | SIGHASH_ANYONECANPAY),
    )
    ALICE.broadcast_transaction(ALICE.funding_ser, transaction_name="FUNDING")
    BOB.broadcast_transaction(BOB.funding_ser, transaction_name="FUNDING")
    ALICE.broadcast_transaction(ALICE.premium_dep_ser, transaction_name="PREMIUM DEPOSITION")
    BOB.commit_margin_dep(bob_sig_bob_margin, alice_sig_bob_margin, bob_funding_utxo.redeem_script.to_hex(),
                          ALICE_SECRET)
    BOB.broadcast_transaction(BOB.margin_dep_ser, transaction_name="MARGIN DEPOSITION")

    # Bob fulfills principal
    bob_principal_tx = BOB.fulfill_principal(
        principal_tx=bob_principal_tx,
        utxo=bob_fulfillment_utxo,
    )

    bob_sig_ff = BOB.make_segwit_signature(bob_principal_tx, 1, bob_fulfillment_utxo)
    BOB.commit_principal(margin_bob_sig=bob_sig_bob_principal, margin_alice_sig=alice_sig_bob_principal,
                         bob_sig_ff=bob_sig_ff, bob_margin_dep_utxo=bob_margin_dep_utxo)
    BOB.broadcast_transaction(BOB.principal_ser, transaction_name="PRINCIPAL")

    carol_HTLC_tx, carol_HTLC_utxo = CAROL.make_HTLC(utxo=carol_utxo_to_spend,
                                                     recipient_pubkeyhash=ALICE.pubkey_hash(network="bcy-tst"),
                                                     bob_principal_utxo=bob_principal_utxo,
                                                     locktime=carol_htlc_locktime)
    CAROL.commit_HTLC()
    CAROL.broadcast_transaction(CAROL.HTLC_ser, network="bcy-tst", transaction_name="HTLC")

    # Alice fulfills redemption
    alice_redm_tx, alice_redm_utxo = ALICE.fulfill_redemption(
        redemption_tx=alice_redm_tx,
        utxo=alice_fulfillment_utxo,
    )

    alice_sig_ff = ALICE.make_segwit_signature(alice_redm_tx, 1, alice_fulfillment_utxo)
    ALICE.commit_redemption(premium_alice_sig=alice_sig_alice_redemption, premium_bob_sig=bob_sig_alice_redemption,
                            alice_sig_ff=alice_sig_ff, alice_premium_dep_utxo=alice_premium_dep_utxo)
    ALICE.broadcast_transaction(ALICE.redemption_ser, transaction_name="REDEMPTION")

    bob_redemption_output_tx = BOB.make_HTLC_output_tx(utxo=ALICE.get_redemption_utxo(), network="btc-test3")
    bob_sig_redemption_output = BOB.secret_key.sign_input(tx=bob_redemption_output_tx, txin_index=0,
                                                          script=alice_redm_utxo.redeem_script)
    BOB.commit_HTLC_output(bob_sig_redemption_output, BOB_SECRET, network="btc-test3")
    BOB.broadcast_transaction(BOB.HTLC_output_ser, network="btc-test3", transaction_name="HTLC OUTPUT")

    alice_HTLC_output_tx = ALICE.make_HTLC_output_tx(utxo=carol_HTLC_utxo, network="bcy-tst")
    alice_sig_htlc_output = ALICE.secret_key_BCY.sign_input(tx=alice_HTLC_output_tx, txin_index=0,
                                                            script=carol_HTLC_utxo.redeem_script)
    ALICE.commit_HTLC_output(alice_sig_htlc_output, BOB_SECRET, network="bcy-tst")
    ALICE.broadcast_transaction(ALICE.HTLC_output_ser, network="bcy-tst", transaction_name="HTLC OUTPUT")

    carol_principal_output_tx = CAROL.make_HTLC_output_tx(utxo=BOB.get_principal_utxo(), network="btc-test3")
    carol_sig_principal_output = CAROL.secret_key.sign_input(tx=carol_principal_output_tx, txin_index=0,
                                                             script=BOB.get_principal_utxo().redeem_script)
    CAROL.commit_HTLC_output(carol_sig_principal_output, BOB_SECRET, network="btc-test3")
    CAROL.broadcast_transaction(CAROL.HTLC_output_ser, network="btc-test3", transaction_name="HTLC OUTPUT")