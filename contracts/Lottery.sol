// SPDX-License-Identifier: MIT

pragma solidity ^0.8.0;

import "@chainlink/contracts/src/v0.8/interfaces/AggregatorV3Interface.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "@chainlink/contracts/src/v0.8/VRFConsumerBase.sol";

contract Lottery is VRFConsumerBase, Ownable{

    address payable[] public players;
    address payable public recentWinner;
    uint256 public usdEntryFee;
    AggregatorV3Interface internal ethUSDPriceFeed;
    enum LOTTERY_STATE {
        OPEN,
        CLOSED,
        CALCULATING_WINNER
    }
    LOTTERY_STATE public lottery_state;
    bytes32 public keyhash;
    uint256 public fee;
    uint256 public randomness;
    event RequestedRandomness(bytes32 requestId);

    constructor(address _priceFeed,
        address _vrfCoordinator,
        address _link,
        bytes32 _keyhash,
        uint256 _fee)
        VRFConsumerBase(_vrfCoordinator, _link) {
        usdEntryFee = 50 * 10**18;
        ethUSDPriceFeed = AggregatorV3Interface(_priceFeed);
        lottery_state = LOTTERY_STATE.CLOSED;
        keyhash = _keyhash;
        fee = _fee;
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
        lottery_state = LOTTERY_STATE.CALCULATING_WINNER;
        bytes32 requestId = requestRandomness( keyhash, fee);
        emit RequestedRandomness(requestId);
    }
    function fulfillRandomness( bytes32 _requestId, uint256 _randomness) internal override{
        require(lottery_state == LOTTERY_STATE.CALCULATING_WINNER, "You aren't there yet" );
        require(_randomness > 0, "random not found");
        uint256 indexOfWinner = _randomness % players.length;
        recentWinner = players[indexOfWinner];
        recentWinner.transfer(address(this).balance);
        players = new address payable[](0);
        lottery_state = LOTTERY_STATE.CLOSED;
        randomness = _randomness;
    }
}