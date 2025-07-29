from typing import Callable, Dict
from multiprocessing import Process
from chaincash.core.models import DepositEvent
from chaincash.core.worker import run_worker
import asyncio

class Monitor:
    def __init__(self, blockchain_client, address_map: Dict[int, str], poll_interval: int = 10):
        self.blockchain_client = blockchain_client
        self.address_map = {k: v.lower() for k, v in address_map.items()}
        self.poll_interval = poll_interval
        self.usdt_contract = self.blockchain_client.usdt_contract
        self.usdt_address = self.usdt_contract.address

    async def start(self, on_deposit: Callable[[DepositEvent], None]):
        self.on_deposit = on_deposit
        await self._run_main_loop()

    async def _run_main_loop(self):
        last_block = await self.blockchain_client.web3.eth.block_number

        while True:
            current_block = await self.blockchain_client.web3.eth.block_number

            if current_block > last_block:
                for chunk_start in range(last_block + 1, current_block + 1, 10):
                    chunk_end = min(chunk_start + 9, current_block)
                    self._spawn_worker(chunk_start, chunk_end)

                last_block = current_block

            await asyncio.sleep(self.poll_interval)

    def _spawn_worker(self, start_block: int, end_block: int):
        config = {
            "address_map" : self.address_map,
            "on_deposit"  : self.on_deposit
        }

        p = Process(target=run_worker, args=(start_block, end_block, config))
        p.start()
