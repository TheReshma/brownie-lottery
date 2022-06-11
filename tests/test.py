from brownie import accounts, Lottery, config, network
from web3 import Web3

def test_entrance_fee():
    account = accounts[0]
    lottery = Lottery.deploy(config["networks"][network.show_active()]["eth_usd_price_feed"],
    {"from": account})
    assert lottery.getEntrancefee() > Web3.toWei(0.03,"ether")
    assert lottery.getEntrancefee() < Web3.toWei(0.035,"ether")