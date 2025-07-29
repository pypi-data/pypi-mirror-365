# ChainCash

🚀 **ChainCash** — A Python library for building crypto payment solutions on Binance Smart Chain (BEP20).  

With ChainCash, you can easily create wallets for your users, monitor deposits (BNB & USDT), and process outgoing transactions asynchronously.

---

## ✨ Features

✅ Create unique wallets for each user  
✅ Monitor incoming deposits with a callback mechanism  
✅ Transfer BNB and USDT tokens  
✅ Fully async, built on top of `AsyncWeb3`  
✅ Default support for BSC Mainnet

---

## 📦 Installation

Install the package:
```bash
pip install chaincash
```
---

## 🔷 Requirements


- Python >= 3.9

## Usage/Examples

```python
from chaincash.core.blockchain_client import BlockchainClient
from chaincash.core.wallet_manager import WalletManager
from chaincash.core.monitor import Monitor
from chaincash.core.transfer_service import TransferService

# Initialize blockchain client
client = BlockchainClient()

# Create a wallet
wallet = WalletManager.create_wallet(user_id=1)
print(wallet)

# Monitor deposits
async def on_deposit(event):
    print(f"📥 Deposit detected: {event}")

monitor = Monitor(client, address_map={1: wallet.address})
await monitor.start(on_deposit)

# Send BNB
transfer_service = TransferService(client, wallet.private_key)
await transfer_service.send_bnb(to_address="0x...", amount=0.1)

```


## 🤝 Contributing

Pull requests and issues are welcome!
If you have ideas, improvements, or bug reports — feel free to open a PR or issue. 🌟

## Support

For support, email noroozisaeed7@gmail.com.


## License

[MIT](https://choosealicense.com/licenses/mit/)

