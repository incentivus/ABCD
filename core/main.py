from core.bondbuyer import *
from core.exchange import *
from website.webapp import *
import asyncio


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


async def main():
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
    # Bob creates funding 2
    # Bob shows Alice funding
    # Bob signs funding
    # Bob signs funding 2
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

    while True:
        await asyncio.sleep(1)
        print(asyncState.start)
        if asyncState.start == 'P':
            continue
        else:
            break
    print("Start passed")

    await ALICE.update_balance("Premium")
    await BOB.update_balance("Margin")
    await CAROL.update_balance("HTLC amount")

    await wait_until_next_interrupt()

    # Alice creates funding
    alice_funding_tx, alice_funding_utxo = ALICE.make_alice_funding_tx(recipient_pubkey=BOB.public_key)
    await ALICE.new_message("Funding transaction created.")

    # Alice shows Bob funding
    BOB.audit_transaction(alice_funding_tx, alice_funding_utxo)
    await BOB.new_message("Audited Alice's funding transaction.")

    # Alice signs funding
    alice_sig = ALICE.make_segwit_signature(
        alice_funding_tx,
        0,
        alice_utxo_to_spend
    )
    await ALICE.new_message("Funding transaction signed.")
    ALICE.commit_funding(alice_sig)

    ################################### ALICE refund section ###################################
    # Alice creates refund
    alice_refund_tx = ALICE.make_refund_tx(funding_utxo=alice_funding_utxo, locktime=alice_refund_locktime)
    await ALICE.new_message("Refund transaction created.")
    # Alice signs refund
    alice_sig = ALICE.make_segwit_signature(
        alice_refund_tx,
        0,
        alice_funding_utxo
    )
    await ALICE.new_message("Refund transaction is signed.")
    ALICE.commit_refund(alice_sig, funding_script=alice_funding_utxo.redeem_script.to_hex())
    #############################################################################################

    # Bob creates funding 1
    bob_funding_tx, bob_funding_utxo = BOB.make_bob_funding_tx(recipient_pubkey=ALICE.public_key,
                                                               alice_funding_utxo=alice_funding_utxo,
                                                               utxo=bob_utxo_to_spend)
    await BOB.new_message("Funding transaction is created.")

    # Bob shows Alice funding
    ALICE.audit_transaction(bob_funding_tx, bob_funding_utxo)
    await ALICE.new_message("Audited Bob's funding transaction.")

    # Bob signs funding
    bob_sig = BOB.make_segwit_signature(
        bob_funding_tx,
        0,
        bob_utxo_to_spend
    )
    BOB.commit_funding(bob_sig)
    print(BOB.funding_ser)
    await BOB.new_message("Funding transaction is signed.")


    ################################### BOB refund section ###################################
    # Bob creates refund
    bob_refund_tx = BOB.make_refund_tx(funding_utxo=bob_funding_utxo, locktime=bob_refund_locktime)
    await BOB.new_message("Refund transaction is created.")

    # Bob signs refund
    bob_sig = BOB.make_segwit_signature(
        bob_refund_tx,
        0,
        bob_funding_utxo
    )
    await BOB.new_message("Refund transaction is signed.")

    BOB.commit_refund(bob_sig, funding_script=bob_funding_utxo.redeem_script.to_hex())
    ##########################################################################################

    # Bob creates funding 2
    bob_funding_2_tx, bob_funding_2_utxo = BOB.make_bob_funding_2_tx(recipient_pubkey=ALICE.public_key,
                                                                     alice_funding_utxo=alice_funding_utxo,
                                                                     utxo=bob_guarantee_utxo)
    await BOB.new_message("Funding transaction number two is created.")

    # Bob shows Alice funding 2
    ALICE.audit_transaction(bob_funding_2_tx, bob_funding_2_utxo)
    await ALICE.new_message("Audited Bob's second funding transaction.")

    # Bob signs funding 2
    bob_sig = BOB.make_segwit_signature(
        bob_funding_2_tx,
        0,
        bob_guarantee_utxo
    )
    BOB.commit_funding_2(bob_sig)
    await BOB.new_message("Second funding transaction is signed.")

    ################################### BOB refund section ###################################
    # Bob creates refund 2
    bob_refund_2_tx = BOB.make_refund_2_tx(funding_utxo=bob_funding_2_utxo, locktime=bob_refund_locktime)
    await BOB.new_message("Second refund transaction is created.")

    # Bob signs refund 2
    bob_sig = BOB.make_segwit_signature(
        bob_refund_2_tx,
        0,
        bob_funding_2_utxo
    )
    await BOB.new_message("Second refund transaction is signed.")

    BOB.commit_refund_2(bob_sig, funding_script=bob_funding_2_utxo.redeem_script.to_hex())
    ##########################################################################################

    # Alice creates guarantee
    bob_guarantee_dep_tx, bob_guarantee_dep_utxo = \
        ALICE.make_guarantee_deposit_tx(
            bob_pubkey=BOB.public_key,
            utxo=bob_funding_2_utxo,  # todo: this has to be Bob's
            fee=DEFAULT_TX_FEE,
            bob_address=BOB.pubkey_hash("btc-test3")
        )
    await BOB.new_message("Guarantee deposition transaction is created.")
    # Bob signs guarantee dep
    bob_sig_gu = BOB.make_segwit_signature(
        bob_guarantee_dep_tx,
        0,
        bob_funding_2_utxo
    )
    await BOB.new_message("Guarantee deposition transaction is signed.")

    # Alice signs guarantee dep
    alice_sig_gu = ALICE.make_segwit_signature(
        bob_guarantee_dep_tx,
        0,
        bob_funding_2_utxo
    )
    await ALICE.new_message("Guarantee deposition transaction is signed.")
    ALICE.commit_guarantee_dep(alice_sig_gu, bob_sig_gu, bob_funding_2_utxo.redeem_script.to_hex())

    # Bob creates guarantee withdrawal
    bob_withdraw_tx = BOB.make_withdraw_tx(guarantee_utxo=bob_guarantee_dep_utxo, locktime=bob_guarantee_locktime)
    await BOB.new_message("Guarantee withdrawal transaction is created.")

    # Bob signs guarantee withdrawal
    bob_sig = BOB.make_segwit_signature(
        bob_withdraw_tx,
        0,
        bob_guarantee_dep_utxo
    )
    await BOB.new_message("Guarantee withdrawal transaction is signed.")

    BOB.commit_withdraw(bob_sig, guarantee_script=bob_guarantee_dep_utxo.redeem_script.to_hex())

    # Alice creates margin dep
    bob_margin_dep_tx, bob_margin_dep_utxo = \
        ALICE.make_margin_deposit_tx(
            bob_pubkey=BOB.public_key,
            utxo=bob_funding_utxo,   # todo: this has to be Bob's
            fee=DEFAULT_TX_FEE
        )
    await BOB.new_message("Margin deposition transaction is created.")
    # Bob signs margin dep
    bob_sig = BOB.make_segwit_signature(
        bob_margin_dep_tx,
        0,
        bob_funding_utxo
    )
    await BOB.new_message("Margin deposition transaction is signed.")

    # Alice signs margin dep
    alice_sig = ALICE.make_segwit_signature(
        bob_margin_dep_tx,
        0,
        bob_funding_utxo
    )
    await ALICE.new_message("Margin deposition transaction is signed.")
    ALICE.commit_margin_dep(alice_sig, bob_sig, bob_funding_utxo.redeem_script.to_hex())

    print(ALICE.margin_dep_ser)

    ################################ Bob defaults section ##################################
    # Alice creates Bob defaults
    bob_defaults_tx = ALICE.make_defaults_tx(prev_utxo=bob_margin_dep_utxo, locktime=bob_defaults_locktime)
    await ALICE.new_message("Bob defaults transaction is created.")
    # Alice signs default
    alice_sig = ALICE.make_segwit_signature(
        bob_defaults_tx,
        0,
        bob_margin_dep_utxo
    )
    await ALICE.new_message("Bob defaults transaction is signed.")
    ALICE.commit_defaults(alice_sig, prev_script=bob_margin_dep_utxo.redeem_script.to_hex())
##########################################################################################

    # Bob creates premium dep
    alice_premium_dep_tx, alice_premium_dep_utxo = \
        BOB.make_prem_deposit_tx(
            recipient_pubkey=BOB.public_key,
            utxo=alice_funding_utxo,
            fee=DEFAULT_TX_FEE,
        )
    await BOB.new_message("Premium deposition transaction is created.")

    # Alice signs margin dep
    alice_sig_alice_premium = ALICE.make_segwit_signature(
        alice_premium_dep_tx,
        0,
        alice_funding_utxo
    )
    await ALICE.new_message("Premium deposition transaction is signed.")

    # Bob signs margin dep
    bob_sig_alice_premium = BOB.make_segwit_signature(
        alice_premium_dep_tx,
        0,
        alice_funding_utxo
    )
    await BOB.new_message("Premium deposition transaction is signed.")

    ################################ Alice defaults section ##################################
    # Bob creates alice defaults
    # alice_defaults_tx = BOB.make_defaults_tx(prev_utxo=alice_premium_dep_utxo, locktime=alice_defaults_locktime)
    # await BOB.new_message("Alice defaults transaction is created.")
    # # Bob signs premium deposition
    # bob_sig = BOB.make_segwit_signature(
    #     alice_defaults_tx,
    #     0,
    #     alice_premium_dep_utxo
    # )
    # await BOB.new_message("Alice defaults transaction is signed.")
    # BOB.commit_defaults(bob_sig, prev_script=alice_premium_dep_utxo.redeem_script.to_hex())
    ##########################################################################################

    # Bob creates principal
    bob_principal_tx, bob_principal_utxo = \
        BOB.make_principal_tx(
            recipient_pubkeyhash=CAROL.pubkey_hash("btc-test3"),
            utxo=bob_margin_dep_utxo,
            locktime=bob_principal_deposit_locktime,
            fee=3 * DEFAULT_TX_FEE,
        )
    await BOB.new_message("Principal deposition transaction is created.")
    # Alice signs principal
    alice_sig_bob_principal = ALICE.make_segwit_signature(
        tx=bob_principal_tx,
        input_idx=0,
        utxo=bob_margin_dep_utxo,
        sighash=(SIGHASH_ALL | SIGHASH_ANYONECANPAY)
    )
    await ALICE.new_message("Principal deposition transaction is signed.")

    # Bob signs principal
    bob_sig_bob_principal = BOB.make_segwit_signature(
        bob_principal_tx,
        0,
        bob_margin_dep_utxo,
        sighash=(SIGHASH_ALL | SIGHASH_ANYONECANPAY),
    )
    await BOB.new_message("Principal deposition transaction is signed.")

    # Alice creates redemption
    alice_redm_tx = \
        ALICE.make_redemption_tx(
            recipient_pubkeyhash=BOB.pubkey_hash(network="btc-test3"),
            utxo=bob_guarantee_dep_utxo,  # todo: this was alice_premium_dep_utxo, I changed it to this
            locktime=alice_redemption_locktime,
            bob_principal_utxo=bob_principal_utxo,
            fee=3 * DEFAULT_TX_FEE,
        )
    await ALICE.new_message("Redemption transaction is created.")

    # Bob signs redemption
    bob_sig_alice_redemption = BOB.make_segwit_signature(
        tx=alice_redm_tx,
        input_idx=0,
        utxo=bob_guarantee_dep_utxo,
        sighash=(SIGHASH_ALL | SIGHASH_ANYONECANPAY)
    )
    await BOB.new_message("Redemption transaction is signed.")

    # Alice signs redemption
    alice_sig_alice_redemption = ALICE.make_segwit_signature(
        alice_redm_tx,
        0,
        bob_guarantee_dep_utxo,
        sighash=(SIGHASH_ALL | SIGHASH_ANYONECANPAY),
    )
    await ALICE.new_message("Redemption transaction is signed.")

    await ALICE.broadcast_transaction(ALICE.funding_ser,
                                      transaction_name="FUNDING", send_to_websocket=True, txid=ALICE.funding_tx.get_txid())

    await ALICE.update_balance("Nothing (Premium is locked)")

    await ALICE.new_message("Funding transaction is broadcasted.")
    await BOB.broadcast_transaction(BOB.funding_ser,
                                    transaction_name="FUNDING", send_to_websocket=True, txid=BOB.funding_tx.get_txid())
    await BOB.broadcast_transaction(BOB.funding_2_ser,
                                    transaction_name="FUNDING 2", send_to_websocket=True, txid=BOB.funding_2_tx.get_txid())
    await BOB.update_balance("Nothing (Margin is locked)")

    await BOB.new_message("Funding transaction is broadcasted.")

    await ask_alice_reveals()
    while True:
        await asyncio.sleep(1)
        # print(asyncState.alice_reveals)
        if asyncState.alice_reveals == 'P':
            continue
        else:
            break
    if asyncState.alice_reveals == 'F':
        await ALICE.broadcast_transaction(ALICE.refund_ser, "REFUND",
                                          send_to_websocket=True, txid=ALICE.refund_tx.get_txid())
        await ALICE.update_balance("Premium (Premium returned back)")
        await ALICE.new_message("Refund transaction is broadcasted.")

        await BOB.broadcast_transaction(BOB.refund_ser, "REFUND", send_to_websocket=True, txid=BOB.refund_tx.get_txid())
        await BOB.broadcast_transaction(BOB.refund_2_ser, "REFUND 2", send_to_websocket=True, txid=BOB.refund_2_tx.get_txid())

        await BOB.update_balance("Margin (Margin returned back)")

        await BOB.new_message("Refund transaction is broadcasted.", end=True)

        exit(0)

    await ALICE.broadcast_transaction(ALICE.margin_dep_ser, transaction_name="MARGIN DEPOSITION",
                                      send_to_websocket=True, txid=ALICE.margin_dep_tx.get_txid())
    await ALICE.new_message("Margin deposition transaction is broadcasted.")

    await ALICE.broadcast_transaction(ALICE.guarantee_dep_ser, transaction_name="GUARANTEE DEPOSITION",
                                      send_to_websocket=True, txid=ALICE.guarantee_dep_tx.get_txid())
    await ALICE.new_message("Guarantee deposition transaction is broadcasted.")

    BOB.commit_premium_dep(alice_sig_alice_premium, bob_sig_alice_premium, alice_funding_utxo.redeem_script.to_hex(),
                           ALICE_SECRET)
    await BOB.new_message("I found the funding key.")

    await BOB.broadcast_transaction(BOB.premium_dep_ser, transaction_name="PREMIUM DEPOSITION",
                                    send_to_websocket=True, txid=BOB.premium_dep_tx.get_txid())
    await BOB.new_message("Premium deposition transaction is broadcasted.")

    await ask_bob_defaults()
    while True:
        await asyncio.sleep(1)
        # print(asyncState.alice_reveals)
        if asyncState.bob_defaults == 'P':
            continue
        else:
            break
    if asyncState.bob_defaults == 'T':
        await ALICE.broadcast_transaction(ALICE.defaults_ser, "BOB DEFAULTS", send_to_websocket=True,
                                          txid=ALICE.defaults_tx.get_txid())
        await ALICE.update_balance("Margin (Bob's punishment)")

        await ALICE.new_message("Bob defaults transaction is broadcasted.")

        await BOB.broadcast_transaction(BOB.withdraw_ser, "WITHDRAW GUARANTEE",
                                        send_to_websocket=True, txid=BOB.withdraw_tx.get_txid())
        await BOB.update_balance("Premium + Guarantee")

        await BOB.new_message("Guarantee withdrawal transaction is broadcasted.", end=True)
        exit(0)

    # Bob fulfills principal
    bob_principal_tx = BOB.fulfill_principal(
        principal_tx=bob_principal_tx,
        utxo=bob_fulfillment_utxo,
    )

    bob_sig_ff = BOB.make_segwit_signature(bob_principal_tx, 1, bob_fulfillment_utxo)

    BOB.commit_principal(margin_bob_sig=bob_sig_bob_principal, margin_alice_sig=alice_sig_bob_principal,
                         bob_sig_ff=bob_sig_ff, bob_margin_dep_utxo=bob_margin_dep_utxo)
    await BOB.broadcast_transaction(BOB.principal_ser, transaction_name="PRINCIPAL",
                                    send_to_websocket=True, txid=BOB.principal_tx.get_txid())
    await BOB.update_balance("Nothing (Principal is locked)")

    await BOB.new_message("Principal is fulfilled and broadcasted.")

    bob_second_HTLC_output_tx = BOB.make_second_HTLC_output_tx(utxo=BOB.get_principal_utxo(), network="btc-test3",
                                                               locktime=bob_principal_deposit_locktime)
    await BOB.new_message("Principal self-output transaction is created. For the case of not revealing leader key.")

    bob_sig_second_htlc_output = BOB.secret_key.sign_input(tx=bob_second_HTLC_output_tx, txin_index=0,
                                                           script=bob_principal_utxo.redeem_script)
    await BOB.new_message("Principal self-output transaction is signed.")

    BOB.commit_second_HTLC_output(bob_sig_second_htlc_output, network="btc-test3")

    carol_HTLC_tx, carol_HTLC_utxo = CAROL.make_HTLC(utxo=carol_utxo_to_spend,
                                                     recipient_pubkeyhash=ALICE.pubkey_hash(network="bcy-tst"),
                                                     bob_principal_utxo=bob_principal_utxo,
                                                     locktime=carol_htlc_locktime)
    await CAROL.new_message("HTLC transaction is created. The other parties HTLC is visible.")

    CAROL.commit_HTLC()
    await CAROL.broadcast_transaction(CAROL.HTLC_ser, network="bcy-tst", transaction_name="HTLC",
                                      send_to_websocket=True, txid=CAROL.HTLC_tx.get_txid())
    await CAROL.update_balance("Nothing (HTLC amount is locked)")

    await CAROL.new_message("HTLC transaction is broadcasted.")

    carol_htlc_output_tx = CAROL.make_second_HTLC_output_tx(utxo=carol_HTLC_utxo, network="bcy-tst",
                                                            locktime=carol_htlc_locktime)
    await CAROL.new_message("HTLC self-output transaction is created. For the case of not revealing leader key.")

    carol_sig_htlc_output = CAROL.secret_key_BCY.sign_input(tx=carol_htlc_output_tx, txin_index=0,
                                                            script=carol_HTLC_utxo.redeem_script)
    await CAROL.new_message("HTLC self-output transaction is signed.")

    CAROL.commit_second_HTLC_output(carol_sig_htlc_output, network="bcy-tst")

    await ask_alice_defaults()
    while True:
        await asyncio.sleep(1)
        # print(asyncState.alice_reveals)
        if asyncState.alice_defaults == 'P':
            continue
        else:
            break
    if asyncState.alice_defaults == 'T':
        await BOB.broadcast_transaction(BOB.second_HTLC_output_ser, "RETURN PRINCIPAL BACK (ALICE DEFAULTS)",
                                        send_to_websocket=True, txid=BOB.second_HTLC_output_tx.get_txid())
        await BOB.update_balance("Principal (Principal returned back)")

        await BOB.new_message("Principal self-output transaction is broadcasted.")

        # await BOB.broadcast_transaction(BOB.defaults_ser, "ALICE DEFAULTS",
        #                                 send_to_websocket=True, txid=BOB.defaults_tx.get_txid())

        await BOB.broadcast_transaction(BOB.withdraw_ser, "WITHDRAW GUARANTEE",
                                        send_to_websocket=True, txid=BOB.withdraw_tx.get_txid())

        await BOB.update_balance("Principal + Premium + Guarantee")

        await BOB.new_message("Guarantee withdrawal transaction is broadcasted.", end=True)

        exit(0)


    # Alice fulfills redemption
    alice_redm_tx, alice_redm_utxo = ALICE.fulfill_redemption(
        redemption_tx=alice_redm_tx,
        utxo=alice_fulfillment_utxo,
    )
    await ALICE.new_message("Redemption is fulfilled  and broadcasted.")

    alice_sig_ff = ALICE.make_segwit_signature(alice_redm_tx, 1, alice_fulfillment_utxo)
    ALICE.commit_redemption(gu_alice_sig=alice_sig_alice_redemption, gu_bob_sig=bob_sig_alice_redemption,
                            alice_sig_ff=alice_sig_ff, bob_guarantee_dep_utxo=bob_guarantee_dep_utxo)
    await ALICE.broadcast_transaction(ALICE.redemption_ser, transaction_name="REDEMPTION",
                                      send_to_websocket=True, txid=ALICE.redemption_tx.get_txid())
    await ALICE.update_balance("Nothing (Payback is locked)")

    alice_second_HTLC_output_tx = ALICE.make_second_HTLC_output_tx(utxo=ALICE.get_redemption_utxo(),
                                                                   network="btc-test3", locktime=alice_redemption_locktime)
    await ALICE.new_message("HTLC self-output transaction is created. For the case of not revealing leader key.")

    alice_sig_second_htlc_output = ALICE.secret_key.sign_input(tx=alice_second_HTLC_output_tx, txin_index=0,
                                                               script=alice_redm_utxo.redeem_script)
    await ALICE.new_message("HTLC self-output transaction is signed.")

    ALICE.commit_second_HTLC_output(alice_sig_second_htlc_output, network="btc-test3")

    await ask_bob_cheats()
    while True:
        await asyncio.sleep(1)
        if asyncState.bob_cheats == 'P':
            continue
        else:
            break
    if asyncState.bob_cheats == 'T':
        await ALICE.broadcast_transaction(ALICE.second_HTLC_output_ser, network="btc-test3",
                                          transaction_name="RETURN REDEMPTION BACK", send_to_websocket=True,
                                          txid=ALICE.second_HTLC_output_tx.get_txid())
        await ALICE.update_balance("Payback + Premium (Payback returned back)")

        await ALICE.new_message("Redemption self-output transaction is broadcasted.")

        await BOB.broadcast_transaction(BOB.second_HTLC_output_ser, network="btc-test3",
                                        transaction_name="RETURN PRINCIPAL BACK (BOB CHEATS)", send_to_websocket=True,
                                        txid=BOB.second_HTLC_output_tx.get_txid())
        await BOB.update_balance("Principal (Principal returned back)")

        await BOB.new_message("Principal self-output transaction is broadcasted.")

        await CAROL.broadcast_transaction(CAROL.second_HTLC_output_ser, network="bcy-tst",
                                          transaction_name="RETURN HTLC BACK", send_to_websocket=True,
                                          txid=CAROL.second_HTLC_output_tx.get_txid())
        await CAROL.update_balance("HTLC amount (HTLC amount returned back)")

        await CAROL.new_message("HTLC self-output transaction is broadcasted.", end=True)

        exit(0)

    bob_redemption_output_tx = BOB.make_HTLC_output_tx(utxo=ALICE.get_redemption_utxo(), network="btc-test3")
    bob_sig_redemption_output = BOB.secret_key.sign_input(tx=bob_redemption_output_tx, txin_index=0,
                                                          script=alice_redm_utxo.redeem_script)

    BOB.commit_HTLC_output(bob_sig_redemption_output, BOB_SECRET, network="btc-test3")
    await BOB.broadcast_transaction(BOB.HTLC_output_ser, network="btc-test3", transaction_name="HTLC OUTPUT",
                                    send_to_websocket=True, txid=BOB.HTLC_output_tx.get_txid())
    await BOB.update_balance("Payback amount + Premium")

    await BOB.new_message("Redemption output transaction is created and broadcasted. The leader key is revealed")

    alice_HTLC_output_tx = ALICE.make_HTLC_output_tx(utxo=carol_HTLC_utxo, network="bcy-tst")
    alice_sig_htlc_output = ALICE.secret_key_BCY.sign_input(tx=alice_HTLC_output_tx, txin_index=0,
                                                            script=carol_HTLC_utxo.redeem_script)
    ALICE.commit_HTLC_output(alice_sig_htlc_output, BOB_SECRET, network="bcy-tst")
    await ALICE.broadcast_transaction(ALICE.HTLC_output_ser, network="bcy-tst", transaction_name="HTLC OUTPUT",
                                      send_to_websocket=True, txid=ALICE.HTLC_output_tx.get_txid())
    await ALICE.update_balance("HTLC amount")

    await ALICE.new_message("HTLC output transaction is created and broadcasted.")

    carol_principal_output_tx = CAROL.make_HTLC_output_tx(utxo=BOB.get_principal_utxo(), network="btc-test3")
    carol_sig_principal_output = CAROL.secret_key.sign_input(tx=carol_principal_output_tx, txin_index=0,
                                                             script=BOB.get_principal_utxo().redeem_script)
    CAROL.commit_HTLC_output(carol_sig_principal_output, BOB_SECRET, network="btc-test3")
    await CAROL.broadcast_transaction(CAROL.HTLC_output_ser, network="btc-test3", transaction_name="HTLC OUTPUT",
                                      send_to_websocket=True, txid=CAROL.HTLC_output_tx.get_txid())
    await CAROL.update_balance("Principal")

    await CAROL.new_message("Principal output transaction is created and broadcasted.", end=True)


if __name__ == '__main__':
    print(BOB.public_key.get_address().to_string())
    exit(0)
    start_server = websockets.serve(counter, "0.0.0.0", 6789)
    ALICE.set_websocket(start_server)
    BOB.set_websocket(start_server)
    CAROL.set_websocket(start_server)
    asyncio.get_event_loop().run_until_complete(start_server)
    asyncio.ensure_future(main())
    asyncio.get_event_loop().run_forever()

