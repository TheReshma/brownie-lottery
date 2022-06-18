import time
from brownie import network
import pytest
from scripts.deploy import get_account, fund_with_link, deploy_contract, LOCAL_BLOCKCHAIN_ENVIRONMENTS

def test_can_pick_winner():
    if network.show_active() in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip()
    lottery = deploy_contract()
    account = get_account()
    lottery.startLottery({"from": account})
    fee = lottery.getEntrancefee()
    lottery.enter({"from": account, "value": fee})
    lottery.enter({"from": account, "value": fee})
    fund_with_link(lottery)
    lottery.endLottery({"from": account})
    time.sleep(180)
    assert lottery.recentWinner() == account
    assert lottery.balance() == 0