from chaincash.core.blockchain_client import BlockchainClient
from chaincash.core.models import TransferResult
from chaincash.utils.logger import logger
from chaincash.utils.exceptions import TransferError

class TransferService:
    """
    Service class for transfering USDT or BNB to a recipient.
    """

    def __init__(self, blockchain_client: BlockchainClient, sender_private_key: str) -> None:
        """
        Initializes the TransferService instance.
        
        Args:
            blockchain_client (BlockchainClient): An instance of the BlockchainClient class.
            sender_private_key (str): The private key of the sender.
        """

        self.blockchain_client = blockchain_client
        self.sender_account    = self.blockchain_client.web3.eth.account.from_key(sender_private_key)
        self.usdt_contract     = self.blockchain_client.usdt_contract
    
    async def send_bnb(self, to_address: str, amount: float) -> TransferResult:
        """
        Send BNB to a recipient.

        Args:
            to_address (str): The address to send the BNB to.
            amount (float): The amount of BNB to send.

        Returns:
            transfer_result (TransferResult): The result of the transfer.
        """

        to_checksum = self.blockchain_client.web3.to_checksum_address(to_address)
        value_wei   = self.blockchain_client.web3.to_wei(amount, "ether")
        nonce       = await self.blockchain_client.web3.eth.get_transaction_count(self.sender_account.address)
        balance_wei = await self.blockchain_client.web3.eth.get_balance(self.sender_account.address)

        if balance_wei < value_wei:
            logger.error(f"Insufficient BNB balance for transfer: required {amount} BNB, available {self.blockchain_client.web3.from_wei(balance_wei, 'ether')}")
            raise TransferError("Insufficient balance to send BNB.")

        tx = {
            "nonce"    : nonce,
            "to"       : to_checksum,
            "value"    : value_wei,
            "gas"      : 21000,
            "gasPrice" : self.blockchain_client.web3.eth.gas_price,
        }

        signed_tx = self.sender_account.sign_transaction(tx)
        tx_hash   = await self.blockchain_client.web3.eth.send_raw_transaction(signed_tx.rawTransaction)

        logger.success(f"Sent {amount} BNB to {to_address} with transaction hash {tx_hash.hex()} successfully.")

        return TransferResult(
            to_address = to_address,
            token      = "BNB",
            amount     = amount,
            tx_hash    = tx_hash.hex()
        )

    async def send_usdt(self, to_address: str, amount: float) -> TransferResult:
        """
        Send USDT to a recipient.

        Args:
            to_address (str): The address to send the USDT to.
            amount (float): The amount of USDT to send.

        Returns:
            transfer_result (TransferResult): The result of the transfer.
        """

        to_checksum      = self.blockchain_client.web3.to_checksum_address(to_address)
        value            = int(amount * 1e18)
        nonce            = await self.blockchain_client.web3.eth.get_transaction_count(self.sender_account.address)
        usdt_balance_raw = await self.usdt_contract.functions.balanceOf(self.sender_account.address).call()
        usdt_balance     = usdt_balance_raw / 1e18
        
        if usdt_balance < amount:
            logger.error(f"Insufficient USDT balance for transfer: required {amount} USDT, available {usdt_balance}")
            raise TransferError("Insufficient balance to send USDT.")
        
        tx = self.usdt_contract.functions.transfer(to_checksum, value).build_transaction({
            "nonce"    : nonce,
            "gasPrice" : self.blockchain_client.web3.eth.gas_price,
            "from"     : self.sender_account.address
        })

        signed_tx = self.sender_account.sign_transaction(tx)
        tx_hash   = await self.blockchain_client.web3.eth.send_raw_transaction(signed_tx.rawTransaction)

        logger.success(f"Sent {amount} USDT to {to_address} with transaction hash {tx_hash.hex()} successfully.")

        return TransferResult(
            to_address = to_address,
            token      = "USDT",
            amount     = amount,
            tx_hash    = tx_hash.hex()
        )