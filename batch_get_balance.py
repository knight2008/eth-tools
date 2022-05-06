#!/usr/bin/env python3
# coding : utf-8
# Date : 2022/5/6
# Author: knight2008
# QQ&Wechat: 496966425
# TG: @knight2008
# Filename: batch_get_balance.py
# Github: https://github.com/knight2008
# 版权：自由转载-开源免费-任意使用

# 功能: 批量查询 EVM chain 基础币余额 或 ERC20 token 余额
# 版本: Python 3.8.6
# 依赖库:
# pip install argparse
# pip install web3


from decimal import Decimal
from web3 import Web3


abi_json = '''[{
	"constant": true,
	"inputs": [{
		"name": "_owner",
		"type": "address"
	}],
	"name": "balanceOf",
	"outputs": [{
		"name": "",
		"type": "uint256"
	}],
	"payable": false,
	"stateMutability": "view",
	"type": "function"},
	{
	"constant": true,
	"inputs": [],
	"name": "decimals",
	"outputs": [{
		"name": "",
		"type": "uint8"
	}],
	"payable": false,
	"stateMutability": "view",
	"type": "function"
}]'''


def get_token_balance(input_file, erc20_contract, web3_rpc_url):
    w3 = Web3(Web3.HTTPProvider(web3_rpc_url))
    contract_addresss = Web3.toChecksumAddress(erc20_contract)
    erc20 = w3.eth.contract(address=contract_addresss, abi=abi_json)
    with open(input_file) as fin:
        addr_list = fin.readlines()
        decimals = erc20.functions.decimals().call()
        for addr in addr_list:
            addr = addr.strip()
            addr_checksum = Web3.toChecksumAddress(addr)
            raw_balance = erc20.functions.balanceOf(addr_checksum).call()
            token_balance = raw_balance / Decimal(10 ** decimals)
            print(f"{addr},{token_balance}")


def get_eth_balance(input_file, web3_rpc_url):
    w3 = Web3(Web3.HTTPProvider(web3_rpc_url))
    with open(input_file) as fin:
        addr_list = fin.readlines()
        for addr in addr_list:
            addr = addr.strip()
            addr_checksum = Web3.toChecksumAddress(addr)
            raw_balance = w3.eth.getBalance(addr_checksum)
            eth_balance = raw_balance / Decimal(10 ** 18)
            print(f"{addr},{eth_balance}")


if __name__ == '__main__':
    import sys
    import argparse

    parser = argparse.ArgumentParser(
        usage="-c -i -w", description="-r web3 rpc url, -c contract address, -i file name for address.")
    parser.add_argument("-r", "--rpc_url", default="", help="web3 rpc url")
    parser.add_argument("-c", "--contract", default="", help="base coin balance if null")
    parser.add_argument("-i", "--input", default="address.txt", help="file name for address")
    args = parser.parse_args()

    # print("contract: {0}".format(args.contract))
    # print("input: {0}".format(args.input))
    if "" == args.rpc_url.strip():
        print(parser.print_help())
        sys.exit(-1)
    else:
        web3_rpc_url = args.rpc_url

    if "" == args.contract.strip():
        get_eth_balance(args.input, web3_rpc_url)
    else:
        get_token_balance(args.input, args.contract, web3_rpc_url)
