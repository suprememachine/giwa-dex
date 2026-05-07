// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

interface IERC20 {
    function totalSupply() external view returns (uint256);
    function balanceOf(address account) external view returns (uint256);
    function transfer(address to, uint256 amount) external returns (bool);
    function allowance(address owner, address spender) external view returns (uint256);
    function approve(address spender, uint256 amount) external returns (bool);
    function transferFrom(address from, address to, uint256 amount) external returns (bool);
}

contract GIWAToken is IERC20 {
    string public name;
    string public symbol;
    uint8 public decimals = 18;
    uint256 private _totalSupply;
    address public owner;

    mapping(address => uint256) private _balances;
    mapping(address => mapping(address => uint256)) private _allowances;

    bool public mintingEnabled = true;
    uint256 public constant MAX_SUPPLY = 1_000_000_000 * 10**18; // 1B tokens

    event Transfer(address indexed from, address indexed to, uint256 value);
    event Approval(address indexed owner, address indexed spender, uint256 value);

    constructor(string memory _name, string memory _symbol) {
        name = _name;
        symbol = _symbol;
        owner = msg.sender;
    }

    modifier onlyOwner() {
        require(msg.sender == owner, "Not owner");
        _;
    }

    function totalSupply() external view override returns (uint256) { return _totalSupply; }
    function balanceOf(address account) external view override returns (uint256) { return _balances[account]; }
    function allowance(address _owner, address spender) external view override returns (uint256) { return _allowances[_owner][spender]; }

    function approve(address spender, uint256 amount) external override returns (bool) {
        _allowances[msg.sender][spender] = amount;
        emit Approval(msg.sender, spender, amount);
        return true;
    }

    function transfer(address to, uint256 amount) external override returns (bool) {
        _transfer(msg.sender, to, amount);
        return true;
    }

    function transferFrom(address from, address to, uint256 amount) external override returns (bool) {
        uint256 currentAllowance = _allowances[from][msg.sender];
        require(currentAllowance >= amount, "Insufficient allowance");
        unchecked { _allowances[from][msg.sender] = currentAllowance - amount; }
        _transfer(from, to, amount);
        return true;
    }

    function mint(address to, uint256 amount) external onlyOwner {
        require(mintingEnabled, "Minting disabled");
        require(_totalSupply + amount <= MAX_SUPPLY, "Exceeds max supply");
        _balances[to] += amount;
        unchecked { _totalSupply += amount; }
        emit Transfer(address(0), to, amount);
    }

    function disableMinting() external onlyOwner { mintingEnabled = false; }

    function _transfer(address from, address to, uint256 amount) internal {
        require(_balances[from] >= amount, "Insufficient balance");
        require(to != address(0), "Transfer to zero address");
        unchecked {
            _balances[from] -= amount;
            _balances[to] += amount;
        }
        emit Transfer(from, to, amount);
    }
}
