// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

interface IERC20 {
    function transfer(address to, uint256 amount) external returns (bool);
    function transferFrom(address from, address to, uint256 amount) external returns (bool);
    function balanceOf(address account) external view returns (uint256);
}

contract GIWAPair {
    IERC20 public token0;
    IERC20 public token1;
    uint256 public reserve0;
    uint256 public reserve1;
    uint256 public totalLiquidity;
    address public factory;

    mapping(address => uint256) public liquidity;

    event Swap(address indexed sender, address indexed tokenIn, uint256 amountIn, uint256 amountOut);
    event LiquidityAdded(address indexed provider, uint256 amount0, uint256 amount1, uint256 liquidity);
    event LiquidityRemoved(address indexed provider, uint256 amount0, uint256 amount1);

    modifier onlyFactory() {
        require(msg.sender == factory, "Not factory");
        _;
    }

    constructor(address _token0, address _token1) {
        token0 = IERC20(_token0);
        token1 = IERC20(_token1);
        factory = msg.sender;
    }

    // ─── Add Liquidity ───
    function addLiquidity(uint256 amount0, uint256 amount1) external returns (uint256 liquidityMinted) {
        require(amount0 > 0 && amount1 > 0, "Amounts must be > 0");
        token0.transferFrom(msg.sender, address(this), amount0);
        token1.transferFrom(msg.sender, address(this), amount1);

        if (reserve0 == 0 && reserve1 == 0) {
            liquidityMinted = sqrt(amount0 * amount1) - 1000;
        } else {
            uint256 li0 = (amount0 * totalLiquidity) / reserve0;
            uint256 li1 = (amount1 * totalLiquidity) / reserve1;
            liquidityMinted = li0 < li1 ? li0 : li1;
        }

        require(liquidityMinted > 0, "Insufficient liquidity minted");
        liquidity[msg.sender] += liquidityMinted;
        totalLiquidity += liquidityMinted;
        reserve0 += amount0;
        reserve1 += amount1;

        emit LiquidityAdded(msg.sender, amount0, amount1, liquidityMinted);
    }

    // ─── Remove Liquidity ───
    function removeLiquidity(uint256 liAmount) external returns (uint256 amount0, uint256 amount1) {
        require(liAmount > 0 && liquidity[msg.sender] >= liAmount, "Insufficient liquidity");
        amount0 = (liAmount * reserve0) / totalLiquidity;
        amount1 = (liAmount * reserve1) / totalLiquidity;

        unchecked {
            liquidity[msg.sender] -= liAmount;
            totalLiquidity -= liAmount;
            reserve0 -= amount0;
            reserve1 -= amount1;
        }

        token0.transfer(msg.sender, amount0);
        token1.transfer(msg.sender, amount1);
        emit LiquidityRemoved(msg.sender, amount0, amount1);
    }

    // ─── Swap ───
    function swap(address tokenIn, uint256 amountIn) external returns (uint256 amountOut) {
        require(amountIn > 0, "Amount must be > 0");
        (IERC20 tokenIn_, IERC20 tokenOut_, uint256 reserveIn, uint256 reserveOut) =
            tokenIn == address(token0) ? (token0, token1, reserve0, reserve1) : (token1, token0, reserve1, reserve0);

        require(tokenIn == address(token0) || tokenIn == address(token1), "Invalid token");

        uint256 amountInWithFee = amountIn * 997; // 0.3% fee
        amountOut = (amountInWithFee * reserveOut) / (reserveIn * 1000 + amountInWithFee);
        require(amountOut > 0, "Insufficient output amount");
        require(amountOut < reserveOut, "Exceeds reserve");

        tokenIn_.transferFrom(msg.sender, address(this), amountIn);
        tokenOut_.transfer(msg.sender, amountOut);

        // Update reserves
        if (tokenIn == address(token0)) {
            reserve0 += amountIn;
            reserve1 -= amountOut;
        } else {
            reserve1 += amountIn;
            reserve0 -= amountOut;
        }

        emit Swap(msg.sender, tokenIn, amountIn, amountOut);
    }

    // ─── View: Get Output Amount ───
    function getAmountOut(address tokenIn, uint256 amountIn) external view returns (uint256 amountOut) {
        (uint256 reserveIn, uint256 reserveOut) = tokenIn == address(token0) ? (reserve0, reserve1) : (reserve1, reserve0);
        uint256 amountInWithFee = amountIn * 997;
        amountOut = (amountInWithFee * reserveOut) / (reserveIn * 1000 + amountInWithFee);
    }

    // ─── View: Price ───
    function getPrice() external view returns (uint256 price) {
        if (reserve0 == 0 || reserve1 == 0) return 0;
        return (reserve1 * 1e18) / reserve0; // price in terms of token1 per token0
    }

    // ─── Utility ───
    function sqrt(uint256 x) internal pure returns (uint256 y) {
        if (x == 0) return 0;
        uint256 z = (x + 1) / 2;
        y = x;
        while (z < y) { y = z; z = (x / z + z) / 2; }
    }
}
