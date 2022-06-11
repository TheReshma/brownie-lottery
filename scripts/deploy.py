from brownie import accounts, Lottery, config, network

def deploy_contract():
    account = accounts[0]
    lottery = Lottery.deploy(config["networks"][network.show_active()]["eth_usd_price_feed"],
    {"from": account})
    txn = lottery.getEntrancefee({"from": account})
    print(txn)



def main():
    deploy_contract()