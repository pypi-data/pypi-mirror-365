from chaincash.core.blockchain_client import BlockchainClient
from chaincash.core.models import DepositEvent
from chaincash.utils.logger import logger
from eth_utils import to_hex
import asyncio

def run_worker(start_block: int, end_block: int, config: dict):
    asyncio.run(_run_worker_async(start_block, end_block, config))

async def _run_worker_async(start_block: int, end_block: int, config: dict):
    client        = BlockchainClient()
    usdt_contract = client.usdt_contract
    address_map   = {k: v.lower() for k, v in config["address_map"].items()}
    on_deposit    = config["on_deposit"]

    for block_number in range(start_block, end_block + 1):
        try:
            block = await client.web3.eth.get_block(block_number, full_transactions=True)
            await _process_block(block, client, address_map, usdt_contract, on_deposit)
        except Exception as e:
            logger.error(f"[Worker] Block {block_number} failed: {e}")

async def _process_block(block, client, address_map, usdt_contract, on_deposit):
    async def _process_transaction(tx):
        to = (tx.get("to") or "").lower()

        if to in address_map.values():
            user_id = next(uid for uid, addr in address_map.items() if addr == to)
            amount  = float(client.web3.from_wei(tx["value"], "ether"))
            tx_hash = to_hex(tx["hash"])
            logger.success(f"[BNB] User {user_id} deposited {amount:.6f} BNB - {tx_hash}")
            if on_deposit:
                await on_deposit(DepositEvent(user_id, "BNB", amount, tx_hash))
            return

        if to == usdt_contract.address.lower():
            try:
                receipt = await client.web3.eth.get_transaction_receipt(tx["hash"])
                for log in receipt["logs"]:
                    try:
                        event = usdt_contract.events.Transfer().process_log(log)
                        to_addr = event["args"]["to"].lower()

                        if to_addr in address_map.values():
                            user_id = next(uid for uid, addr in address_map.items() if addr == to_addr)
                            amount  = event["args"]["value"] / 1e18
                            tx_hash = to_hex(tx["hash"])
                            logger.success(f"[USDT] User {user_id} deposited {amount:.6f} USDT - {tx_hash}")
                            if on_deposit:
                                await on_deposit(DepositEvent(user_id, "USDT", amount, tx_hash))
                    except:
                        continue
            except:
                pass

    await asyncio.gather(*[asyncio.create_task(_process_transaction(tx)) for tx in block["transactions"]])
