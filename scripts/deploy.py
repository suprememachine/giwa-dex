#!/usr/bin/env python3
"""
GIWA DEX — Contract Deploy Script
Deploys GIWAToken + PairFactory to GIWA Sepolia Testnet
"""
import json
import os
import subprocess
import sys

# ─── Config ───
RPC_URL = os.getenv("RPC_URL", "https://sepolia-rpc.giwa.io")
EXPLORER = "https://sepolia-explorer.giwa.io"
PRIVATE_KEY = os.getenv("DEPLOYER_PRIVATE_KEY", "")
CHAIN_ID = 91342

# ─── ABI paths ───
ABI_DIR = "abis"

def install_solc():
    """Install solc compiler"""
    subprocess.run(["pip", "install", "solcx"], check=True)
    subprocess.run(["python", "-m", "solcx", "install", "0.8.20"], check=True)
    subprocess.run(["python", "-m", "solcx", "select", "0.8.20"], check=True)

def compile_contract(path):
    """Compile a Solidity contract"""
    result = subprocess.run(
        ["solc", "--abi", "--bin", "--optimize", "-o", ABI_DIR, "--overwrite", path],
        capture_output=True, text=True
    )
    if result.returncode != 0:
        print(f"❌ Compile error: {result.stderr}")
        sys.exit(1)
    print(f"✅ Compiled {path}")

def deploy(abi_path, bin_path, constructor_args=None, value=None):
    """Deploy a contract and return the address"""
    from web3 import Web3

    w3 = Web3(Web3.HTTPProvider(RPC_URL))
    account = w3.eth.account.from_key(PRIVATE_KEY)

    with open(bin_path) as f:
        bytecode = f.read().strip()
    with open(abi_path) as f:
        abi = json.load(f)

    contract = w3.eth.contract(abi=abi, bytecode=bytecode)

    # Build constructor tx
    if constructor_args:
        tx = contract.constructor(*constructor_args).build_transaction({
            'from': account.address,
            'nonce': w3.eth.get_transaction_count(account.address),
            'gas': 5_000_000,
            'gasPrice': w3.eth.gas_price,
            'chainId': CHAIN_ID,
            'value': value or 0,
        })
    else:
        tx = contract.constructor().build_transaction({
            'from': account.address,
            'nonce': w3.eth.get_transaction_count(account.address),
            'gas': 5_000_000,
            'gasPrice': w3.eth.gas_price,
            'chainId': CHAIN_ID,
        })

    signed = account.sign_transaction(tx)
    tx_hash = w3.eth.send_raw_transaction(signed.raw_transaction)
    print(f"⏳ Deploying... Tx: {tx_hash.hex()}")

    receipt = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=120)
    address = receipt.contractAddress
    print(f"✅ Deployed at: {address}")
    print(f"   Explorer: {EXPLORER}/address/{address}")
    return address

def main():
    if not PRIVATE_KEY:
        print("❌ Set DEPLOYER_PRIVATE_KEY env var first")
        print("   export DEPLOYER_PRIVATE_KEY=0x...")
        sys.exit(1)

    os.makedirs(ABI_DIR, exist_ok=True)

    print("=== GIWA DEX — Deploying to GIWA Sepolia ===\n")

    # 1. Compile
    print("📝 Compiling contracts...")
    compile_contract("contracts/GIWAToken.sol")
    compile_contract("contracts/GIWAPair.sol")
    compile_contract("contracts/GIWAPairFactory.sol")

    # 2. Deploy GIWA Token
    print("\n🦎 Deploying GIWA Token...")
    token_addr = deploy(
        "abis/GIWAToken.abi",
        "abis/GIWAToken.bin",
        constructor_args=["GIWA Token", "GIWA"]
    )

    # 3. Deploy Pair Factory
    print("\n🏭 Deploying Pair Factory...")
    factory_addr = deploy(
        "abis/GIWAPairFactory.abi",
        "abis/GIWAPairFactory.bin"
    )

    # 4. Create ETH/GIWA Pair
    print("\n🔗 Creating ETH/GIWA pair...")
    from web3 import Web3
    w3 = Web3(Web3.HTTPProvider(RPC_URL))
    account = w3.eth.account.from_key(PRIVATE_KEY)

    with open("abis/GIWAPairFactory.abi") as f:
        factory_abi = json.load(f)
    factory = w3.eth.contract(address=factory_addr, abi=factory_abi)

    # Use a dummy address for WETH or wrapped ETH
    wrapped_eth = os.getenv("WRAPPED_ETH", "0x0000000000000000000000000000000000000000")

    tx = factory.functions.createPair(wrapped_eth, token_addr).build_transaction({
        'from': account.address,
        'nonce': w3.eth.get_transaction_count(account.address),
        'gas': 2_000_000,
        'gasPrice': w3.eth.gas_price,
        'chainId': CHAIN_ID,
    })
    signed = account.sign_transaction(tx)
    tx_hash = w3.eth.send_raw_transaction(signed.raw_transaction)
    receipt = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=120)

    # Extract pair address from event
    pair_addr = factory.events.PairCreated().process_receipt(receipt)['args']['pair']
    print(f"✅ Pair created: {pair_addr}")

    # 5. Save addresses
    config = {
        "token_address": token_addr,
        "factory_address": factory_addr,
        "pair_address": pair_addr,
        "wrapped_eth": wrapped_eth,
        "chain_id": CHAIN_ID,
        "rpc_url": RPC_URL,
    }
    with open("deployed_addresses.json", "w") as f:
        json.dump(config, f, indent=2)

    print("\n" + "="*50)
    print("🎉 DEPLOYMENT COMPLETE!")
    print("="*50)
    print(f"\n📋 Addresses saved to deployed_addresses.json")
    print(f"\n   Token:     {token_addr}")
    print(f"   Factory:   {factory_addr}")
    print(f"   Pair:      {pair_addr}")
    print(f"\n🌐 View on explorer:")
    print(f"   {EXPLORER}/address/{token_addr}")
    print(f"   {EXPLORER}/address/{factory_addr}")
    print(f"\n🔧 Set env vars on Railway:")
    print(f"   FACTORY_ADDRESS={factory_addr}")
    print(f"   WRAPPED_ETH={wrapped_eth}")

if __name__ == "__main__":
    main()
