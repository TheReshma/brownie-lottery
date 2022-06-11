// SPDX-License-Identifier: MIT

pragma solidity ^0.8.0;

import "@chainlink/contracts/src/v0.8/interfaces/AggregatorV3Interface.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

contract Lottery is Ownable{

    address payable[] public players;
    uint256 public usdEntryFee;
    AggregatorV3Interface internal ethUSDPriceFeed;
    enum LOTTERY_STATE {
        OPEN,
        CLOSED,
        CALCULATING_WINNER
    }
    LOTTERY_STATE public lottery_state;

    constructor(address _priceFeed) public{
        usdEntryFee = 50 * 10**18;
        ethUSDPriceFeed = AggregatorV3Interface(_priceFeed);
        lottery_state = LOTTERY_STATE.CLOSED;
    }

    function enter() public payable {
        require(lottery_state == LOTTERY_STATE.OPEN);
        require(msg.value >= getEntrancefee(), "Not enough ETH" );
        players.push(payable(msg.sender));
    }
    function getEntrancefee() public view returns(uint256) {
        ( ,int price, , , ) = ethUSDPriceFeed.latestRoundData();
        uint256 adjustedPrice = uint256(price) * 10**10;
        uint256 costToEnter = (usdEntryFee * 10**18)/adjustedPrice ;
        return costToEnter;
    }
    function startLottery() public onlyOwner{
        require(lottery_state == LOTTERY_STATE.CLOSED, "Can't start a new lottery yet");
        lottery_state = LOTTERY_STATE.OPEN;
    }
    function endLottery() public onlyOwner{
    }
}