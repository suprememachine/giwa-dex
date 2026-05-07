# GIWA DEX

Decentralized Exchange (DEX) on GIWA L2 — an OP Stack Layer 2 by Upbit.

![License](https://img.shields.io/badge/license-MIT-blue)

## Features

- **AMM Swap** — Constant product formula (x*y=k), 0.3% fee
- **Liquidity Pools** — Add/remove liquidity for ETH/GIWA pairs
- **Real-time Pool Data** — Reserves, price, TVL
- **WalletConnect** — MetaMask, Coinbase Wallet, WalletConnect QR
- **GIWA Sepolia Testnet** — Chain ID 91342

## Tech Stack

- **Frontend**: Alpine.js + ethers.js
- **Backend**: FastAPI + Python 3.12
- **Smart Contracts**: Solidity 0.8.20
- **Chain**: GIWA Sepolia (OP Stack L2)
- **Deploy**: Railway (Docker)

## Quick Start

### 1. Clone & Install
```bash
git clone https://github.com/YOUR_USER/giwa-dex.git
cd giwa-dex
pip install -r requirements.txt
```

### 2. Run Locally
```bash
python -m app.main
# Open http://localhost:8000
```

### 3. Deploy Contracts
```bash
# Get testnet ETH from: https://sepolia-faucet.giwa.io
export DEPLOYER_PRIVATE_KEY=0x...
python scripts/deploy.py
```

### 4. Deploy to Railway
```bash
railway init
railway up
```

## Environment Variables

| Variable | Description | Default |
|---|---|---|
| `CHAIN_ID` | GIWA chain ID | 91342 |
| `RPC_URL` | GIWA RPC endpoint | https://sepolia-rpc.giwa.io |
| `FACTORY_ADDRESS` | Pair factory contract | 0x000... |
| `DEPLOYER_PRIVATE_KEY` | Wallet private key | — |

## Smart Contracts

### GIWAToken.sol
ERC-20 token with minting controls. Deploy your own GIWA token.

### GIWAPair.sol  
AMM pair with constant product formula:
- Add/remove liquidity
- Swap with 0.3% fee
- Real-time price from reserves

### GIWAPairFactory.sol
Factory pattern — creates new pairs for any token combination.

## GIWA Chain Info

| Property | Value |
|---|---|
| Chain Name | GIWA Sepolia |
| Chain ID | 91342 |
| RPC | https://sepolia-rpc.giwa.io |
| Explorer | https://sepolia-explorer.giwa.io |
| Currency | ETH |
| Block Time | 1 second |
| L2 Type | OP Stack |

## License

MIT
