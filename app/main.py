"""
GIWA DEX — Backend API
AMM Swap on GIWA Sepolia Testnet
"""
import os
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Optional
import json

app = FastAPI(title="GIWA DEX", version="1.0.0")

# ─── Config ───
GIWA_CONFIG = {
    "chain_name": "GIWA Sepolia",
    "chain_id": int(os.getenv("CHAIN_ID", "91342")),
    "rpc_url": os.getenv("RPC_URL", "https://sepolia-rpc.giwa.io"),
    "explorer": "https://sepolia-explorer.giwa.io",
    "currency": "ETH",
    "factory_address": os.getenv("FACTORY_ADDRESS", "0x0000000000000000000000000000000000000000"),
    "wrapped_eth": os.getenv("WRAPPED_ETH", "0x0000000000000000000000000000000000000000"),
}

# ─── In-memory state for demo (use DB in production) ───
swap_history = []

# ─── Models ───
class SwapRequest(BaseModel):
    wallet: str
    token_in: str
    token_out: str
    amount_in: float
    slippage: float = 0.5

class AddLiquidityRequest(BaseModel):
    wallet: str
    token_a: str
    token_b: str
    amount_a: float
    amount_b: float

# ─── Routes ───
@app.get("/")
async def root():
    with open("app/templates/index.html") as f:
        return HTMLResponse(f.read())

@app.get("/api/config")
async def get_config():
    return GIWA_CONFIG

@app.get("/api/pairs")
async def get_pairs():
    """Return known token pairs"""
    return [
        {
            "token0": {"symbol": "ETH", "name": "Ether", "address": GIWA_CONFIG["wrapped_eth"], "decimals": 18},
            "token1": {"symbol": "GIWA", "name": "GIWA Token", "address": "0x0000000000000000000000000000000000000000", "decimals": 18},
            "reserve0": 100.0,
            "reserve1": 50000.0,
            "price": 500.0,
        }
    ]

@app.post("/api/swap")
async def swap(req: SwapRequest):
    """Swap tokens"""
    # Validate
    if req.amount_in <= 0:
        raise HTTPException(400, "Amount must be > 0")
    if req.wallet == "0x0000000000000000000000000000000000000000":
        raise HTTPException(400, "Invalid wallet")

    # Simple mock swap for demo
    amount_out = req.amount_in * 0.997 * 500.0  # 0.3% fee, mock price
    slippage_factor = 1 - (req.slippage / 100)
    min_out = amount_out * slippage_factor

    record = {
        "wallet": req.wallet,
        "token_in": req.token_in,
        "token_out": req.token_out,
        "amount_in": req.amount_in,
        "amount_out": round(amount_out, 6),
        "min_out": round(min_out, 6),
        "fee": round(req.amount_in * 0.003, 6),
        "tx_hash": "0x" + "0" * 64,  # Placeholder
    }
    swap_history.append(record)

    return {
        "status": "ok",
        **record,
        "message": "Swap simulated. Deploy contracts to enable on-chain swaps."
    }

@app.get("/api/swap/history")
async def swap_history_api():
    return swap_history[-50:]

@app.get("/api/health")
async def health():
    return {
        "status": "ok",
        "service": "giwa-dex",
        "chain": GIWA_CONFIG["chain_name"],
        "chain_id": GIWA_CONFIG["chain_id"],
    }

# ─── Static files (optional) ───
if os.path.isdir("app/static"):
    app.mount("/static", StaticFiles(directory="app/static"), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", "8000")))
