// SPDX-License-Identifier: MIT

pragma solidity ^0.8.0;

import "@chainlink/contracts/src/v0.8/interfaces/AggregatorV3Interface.sol";

contract Lottery{

    address payable[] public players;
    uint256 public usdEntryFee;
    AggregatorV3Interface internal ethUSDPriceFeed;

    constructor(address _priceFeed) public{
        usdEntryFee = 50 * 10**18;
        ethUSDPriceFeed = AggregatorV3Interface(_priceFeed);
    }
    function enter() public payable {
        players.push(payable(msg.sender));
    }
    function getEntrancefee() public view returns(uint256) {
        ( ,int price, , , ) = ethUSDPriceFeed.latestRoundData();
        uint256 adjustedPrice = uint256(price) * 10**10;
        uint256 costToEnter = (usdEntryFee * 10**18)/adjustedPrice ;
        return costToEnter;
    }
    function startLottery() public { }
    function endLottery() public { }
}