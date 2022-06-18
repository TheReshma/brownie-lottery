from brownie import network, exceptions
import pytest
from web3 import Web3
from scripts.deploy import deploy_contract, get_account, fund_with_link, LOCAL_BLOCKCHAIN_ENVIRONMENTS, get_contract

def test_entrance_fee():
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip()
    lottery = deploy_contract()
    expected_fee = Web3.toWei(0.025,"ether")
    fee = lottery.getEntrancefee()
    assert fee == expected_fee

def test_enter_without_starting():
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip()
    lottery = deploy_contract()
    fee = lottery.getEntrancefee()
    with pytest.raises(exceptions.VirtualMachineError):
        lottery.enter({"from": get_account(), "value": fee})

def test_enter_after_starting():
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip()
    lottery = deploy_contract()
    account = get_account()
    fee = lottery.getEntrancefee()
    lottery.startLottery({"from": account})
    lottery.enter({"from": account, "value": fee})
    assert lottery.players(0) == account

def test_can_end_lottery():
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip()
    lottery = deploy_contract()
    account = get_account()
    fee = lottery.getEntrancefee()
    lottery.startLottery({"from": account})
    lottery.enter({"from": account, "value": fee})
    fund_with_link(lottery)
    lottery.endLottery({"from": account})
    assert lottery.lottery_state() == 2

def test_can_pick_winner():
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip()
    lottery = deploy_contract()
    account = get_account()
    fee = lottery.getEntrancefee()
    lottery.startLottery({"from": account})
    lottery.enter({"from": account, "value": fee})
    lottery.enter({"from": get_account(index=1), "value": fee})
    lottery.enter({"from": get_account(index=2), "value": fee})
    fund_with_link(lottery)
    txn = lottery.endLottery({"from": account})
    req_id = txn.events["RequestedRandomness"]["requestId"]
    STATIC_RANDOM = 777
    get_contract("vrf_coordinator").callBackWithRandomness( req_id, STATIC_RANDOM, lottery.address, {"from": account})
    starting_balance_of_account = account.balance()
    balance_of_lottery = lottery.balance()
    assert lottery.recentWinner() == account
    assert lottery.balance() == 0
    assert account.balance() == starting_balance_of_account + balance_of_lottery
