#!/usr/bin/env python

# WS server example that synchronizes state across clients

import asyncio
import json
import logging
from core.config import *
# import core.config as conf
import websockets

logging.basicConfig()

STATE = {"value": 0}

USERS = set()
TRANSACTION_COUNTER = 1000
MESSAGES_COUNTER = 0

TRANSACTIONS = []
MESSAGES = []
BALANCES = dict()
BALANCES["alice"] = {}
BALANCES["bob"] = {}
BALANCES["carol"] = {}

#
# def state_event():
#     return json.dumps({"type": "state", **STATE})
#
#
# def users_event():
#     return json.dumps({"type": "users", "count": len(USERS)})


# async def notify_state():
#     if USERS:  # asyncio.wait doesn't accept an empty list
#         message = state_event()
#         await asyncio.wait([user.send(message) for user in USERS])

def create_new_message(type, party, value):
    if USERS:  # asyncio.wait doesn't accept an empty list
        global MESSAGES, MESSAGES_COUNTER
        message = {"type": type, "party": party, "value": value, "id": MESSAGES_COUNTER}
        MESSAGES.append(message)
        MESSAGES_COUNTER += 1
        return message


def notify_new_msg(msg, party):
    return notify_users(json.dumps(create_new_message(type="new-message", party=party, value=msg)))


def notify_finish():
    return notify_users(json.dumps({"type": "finish"}))


def notify_update_balance(msg, party):
    global BALANCES
    BALANCES[party] = msg
    message = {"type": "update-balance", "party": party, "value": msg}
    return notify_users(json.dumps(message))


async def ask_alice_reveals():
    if USERS:  # asyncio.wait doesn't accept an empty list
        await asyncio.wait([
            user.send(json.dumps(create_new_message("question", "alice",
                                                    "Would you want to reveal funding key?")))
            for user in USERS])


async def ask_bob_defaults():
    if USERS:  # asyncio.wait doesn't accept an empty list
        await asyncio.wait([
            user.send(json.dumps(create_new_message("question", "bob",
                                                    "Would you want to default or not? (Bob)")))
            for user in USERS])


async def ask_bob_cheats():
    if USERS:  # asyncio.wait doesn't accept an empty list
        await asyncio.wait([
            user.send(json.dumps(create_new_message("question", "bob",
                                                    "Would you want to cheat or not?")))
            for user in USERS])


async def ask_alice_defaults():
    if USERS:  # asyncio.wait doesn't accept an empty list
        await asyncio.wait([
            user.send(json.dumps(create_new_message("question", "alice",
                                                    "Would you want to default or not? (Alice)")))
            for user in USERS])


async def notify_users(message):
    if USERS:  # asyncio.wait doesn't accept an empty list
        await asyncio.wait([user.send(message) for user in USERS])


async def register(websocket):
    USERS.add(websocket)
    print("new user", websocket)
    # await notify_users()


async def update_user(user):
    # if len(MESSAGES):
    #     print("Here")
    #     await asyncio.wait([user.send(msg) for msg in MESSAGES])
    # if len(TRANSACTIONS):
    #     await asyncio.wait([user.send(trx) for trx in TRANSACTIONS])
    if asyncState.start == 'T':
        await user.send(json.dumps({"type": "late"}))
        unregister(user)


def unregister(websocket):
    USERS.remove(websocket)
    # await notify_users()

def notify_new_trx(trx):
    return json.dumps({"type": "new-transaction", "value": trx["value"], "id": trx["id"]})


def notify_update_trx(trx):
    return json.dumps({"type": "update-transaction", "value": trx["value"], "id": trx["id"]})


def notify_update_msg(msg):
    return notify_users(json.dumps({"type": "update-message", "value": msg["value"], "id": msg["id"]}))


def new_trx(tid):
    global TRANSACTION_COUNTER
    trx = {"value": tid, "id": TRANSACTION_COUNTER}
    TRANSACTION_COUNTER += 1
    TRANSACTIONS.append(trx)
    return trx


def update_trx(iid, value):
    print(TRANSACTIONS)
    for i in range(len(TRANSACTIONS)):
        if TRANSACTIONS[i]["id"] == iid:
            TRANSACTIONS[i]["value"] = value
            return TRANSACTIONS[i]


def update_msg(iid, msg):
    # print(MESSAGES)
    for i in range(len(MESSAGES)):
        # print(MESSAGES[i]["id"])
        # print(iid)
        if MESSAGES[i]["id"] == iid:
            MESSAGES[i]['value'] = msg['question'] + ("Yes" if msg['ans'] == 'T' else "No")
            return MESSAGES[i]


async def counter(websocket, path):
    # register(websocket) sends user_event() to websocket
    # try:
    #     await register(websocket)
    #     print(websocket)
    #         # await notify_users(notify_new_trx(tid))
    # finally:
    #     await unregister(websocket)
    await register(websocket)
    try:
        # await websocket.send(state_event())
        print(websocket)
        await update_user(websocket)
        async for message in websocket:
            data = json.loads(message)
            if data["type"] == "answer":
                if data["question"] == "Would you want to reveal funding key?":
                    await notify_users(json.dumps({"type": "btn-remove", "party": "alice"}))
                    await notify_update_msg(update_msg(int(data["id"]), data))
                    asyncState.alice_reveals = data["ans"]
                    continue
                elif data["question"] == "Would you want to default or not? (Bob)":
                    await notify_users(json.dumps({"type": "btn-remove", "party": "bob"}))
                    await notify_update_msg(update_msg(int(data["id"]), data))
                    asyncState.bob_defaults = data["ans"]
                    continue
                elif data["question"] == "Would you want to default or not? (Alice)":
                    await notify_users(json.dumps({"type": "btn-remove", "party": "alice"}))
                    await notify_update_msg(update_msg(int(data["id"]), data))
                    asyncState.alice_defaults = data["ans"]
                    continue
                elif data["question"] == "Would you want to cheat or not?":
                    await notify_users(json.dumps({"type": "btn-remove", "party": "bob"}))
                    await notify_update_msg(update_msg(int(data["id"]), data))
                    asyncState.bob_cheats = data["ans"]
                    continue
                else:
                    continue

            elif data["type"] == "next":
                if data["value"] == "T":
                    asyncState.next = 'T'
                    continue
            elif data["type"] == "start":
                if data["value"] == "T":
                    asyncState.start = 'T'
                    global MESSAGES, MESSAGES_COUNTER
                    MESSAGES.append({'type': 'start-done', 'id': MESSAGES_COUNTER})
                    MESSAGES_COUNTER += 1
                    await notify_users(json.dumps({'type': 'start-done'}))
                    # conf.start = 'T'
                    continue
            else:
                logging.error("unsupported event: {}", data)
    finally:
        unregister(websocket)


# @asyncio.coroutine
# async def main():
#     while True:
#         await asyncio.sleep(1)
#         command = input("command")
#         if command == "tx":
#             tid = input("Trx ")
#             await asyncio.sleep(1)
#             trx = new_trx(tid)
#             print(trx)
#             await notify_users(notify_new_trx(trx))
#         elif command == "change":
#             id = input("ID?")
#             value = input("VALUE?")
#             trx = update_trx(int(id), value)
#             print("here", trx)
#             await notify_users(notify_update_trx(trx))


# start_server = websockets.serve(counter, "localhost", 6789)
# asyncio.get_event_loop().run_until_complete(start_server)
# asyncio.ensure_future(main())
# asyncio.get_event_loop().run_forever()
#

