from brownie import (
    accounts,
    Lottery,
    MockV3Aggregator,
    LinkToken,
    VRFCoordinatorMock,
    config,
    network,
    Contract,
    interface
)
import time

FORKED_LOCAL_ENVIRONMENTS = ["mainnet-fork", "mainnet-fork-dev"]
LOCAL_BLOCKCHAIN_ENVIRONMENTS = ["development", "ganache-local"]
DECIMALS = 8
INITIAL_VALUE = 200000000000

contract_to_mock = {
    "eth_usd_price_feed": MockV3Aggregator,
    "vrf_coordinator": VRFCoordinatorMock,
    "link_token": LinkToken,
}

def deploy_mocks(decimals=DECIMALS, initial_value=INITIAL_VALUE):
    account = get_account()
    MockV3Aggregator.deploy(decimals, initial_value, {"from": account})
    link_token = LinkToken.deploy({"from": account})
    VRFCoordinatorMock.deploy(link_token.address, {"from": account})
    print("Deployed!")

def get_account():
    if (
        network.show_active() in LOCAL_BLOCKCHAIN_ENVIRONMENTS
        or network.show_active() in FORKED_LOCAL_ENVIRONMENTS
    ):
        return accounts[0]
    return accounts.add(config["wallets"]["from_key"])

def get_contract(contract_name):
    contract_type = contract_to_mock[contract_name]
    if network.show_active() in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        if len(contract_type)<=0:
            #MockV3Aggregator.length <= 0
            deploy_mocks()
        contract = contract_type[-1]
    else:
        contract_address = config["networks"][network.show_active()][contract_name]
        contract = Contract.from_abi(contract_type._name, contract_address, contract_type.abi)
    return contract

def fund_with_link( contract_address, account=None, link_token=None ,amount=100000000000000000):
    account = account if account else get_account()
    link_token = link_token if link_token else get_contract("link_token")
    tx = link_token.transfer(contract_address, amount, {"from": account})
    # link_token_contract = interface.LinkTokenInterface(link_token.address)
    # tx = link_token_contract.transfer(contract_address, amount, {"from": account})
    tx.wait(1)
    print("Funding Contract !")

def deploy_contract():
    account = get_account()
    Lottery.deploy(
        get_contract("eth_usd_price_feed").address,
        get_contract("vrf_coordinator").address,
        get_contract("link_token").address,
        config["networks"][network.show_active()]["keyhash"],
        config["networks"][network.show_active()]["fee"],
        {"from": account},
        publish_source=config["networks"][network.show_active()].get("verify", False))
    print("Lottery deployed !")

def start_lottery():
    account =  get_account()
    lottery = Lottery[-1]
    start = lottery.startLottery({"from": account})
    start.wait(1)
    print("Lottery started !!")

def enter_lottery():
    account =  get_account()
    lottery = Lottery[-1]
    fee = lottery.getEntrancefee({"from": account})
    enter = lottery.enter({"from": account, "value": fee})
    enter.wait(1)
    print("You have entered the lottery !!")

def end_lottery():
    account =  get_account()
    lottery = Lottery[-1]
    fund_with_link(lottery.address)
    end = lottery.endLottery({"from": account})
    end.wait(1)
    time.sleep(60)
    print(f"{lottery.recentWinner()} is the new winner")

def main():
    deploy_contract()
    start_lottery()
    enter_lottery()
    end_lottery()