#!/usr/bin/env python3
# coding : utf-8
# Date : 2022/5/4
# Author: knight2008
# QQ&Wechat: 496966425
# TG: @knight2008
# Filename: get_dex_price.py
# Github: https://github.com/knight2008
# 版权：自由转载-开源免费-禁止商用

# 功能: 查询 pancake 交易池中 token 的价格
# 版本: Python 3.8.6
# 依赖库:
# pip install web3


from web3 import Web3
from datetime import datetime
from eth_abi.packed import encode_abi_packed
import time


# BSC mainnet RPC
WEB3_RPC_URL = "https://bsc-dataseed.binance.org"

# pancake factory contract info
DEX_FACTORY_CONTRACT_ADDRESS = "0xca143ce32fe78f1f7019d7d551a6402fc5350c73"
INIT_CODE_HASH = '0x00fb7f630766e6a796048ea87d01acd3068e8ff67d078148a3fa3f4a84f69bd5'
DEX_FEE_RATE = 0.25 # 0.25%

# BUSD token contract
TOKEN0_CONTRACT_ADDRESS = "0xe9e7cea3dedca5984780bafc599bd69add087d56"
TOKEN0_DECIMALS = 18

# i.e., Dalarnia (DAR)
TOKEN1_CONTRACT_ADDRESS = "0x23ce9e926048273ef83be0a3a8ba9cb6d45cd978"
TOKEN1_DECIMALS = 6


# 本地计算2个token的 pair address
def calc_pair_address(token0, token1):
    (token0, token1) = (token0, token1) if (token0 < token1) else (token1, token0)
    factory_address = Web3.toChecksumAddress(DEX_FACTORY_CONTRACT_ADDRESS)

    abi_packed_1 = encode_abi_packed(['address', 'address'], (token0, token1))
    salt = Web3.solidityKeccak(['bytes'], ['0x' + abi_packed_1.hex()])
    abi_packed_2 = encode_abi_packed(['address', 'bytes32'], (factory_address, salt))
    pair_address = Web3.solidityKeccak(['bytes', 'bytes'], ['0xff' + abi_packed_2.hex(), INIT_CODE_HASH])[12:]
    # print(f"{pair_address.hex()}")
    return Web3.toChecksumAddress(pair_address)


# 从 pair 合约中查询 token 的数量
def get_token_reserves(pair_address):
    w3 = Web3(Web3.HTTPProvider(WEB3_RPC_URL))
    abi = '''[{
        "inputs": [],
        "name": "getReserves",
        "outputs": [{
            "internalType": "uint112",
            "name": "_reserve0",
            "type": "uint112"
        }, {
            "internalType": "uint112",
            "name": "_reserve1",
            "type": "uint112"
        }, {
            "internalType": "uint32",
            "name": "_blockTimestampLast",
            "type": "uint32"
        }],
        "stateMutability": "view",
        "type": "function"
        }]
    '''

    pair_contract_address = w3.toChecksumAddress(pair_address)
    pair_instance = w3.eth.contract(address=pair_contract_address, abi=abi)
    (reserve0, reserve1, ts_date) = pair_instance.functions.getReserves().call()
    # print(f'raw result: {reserve0}, {reserve1}, {ts_date}')
    return (reserve0, reserve1, ts_date)


def calc_token_price_busd(_reserve0, _reserve1):
    decimals_diff = TOKEN0_DECIMALS - TOKEN1_DECIMALS
    if token0 == TOKEN0_CONTRACT_ADDRESS:
        swap_price = _reserve0 / _reserve1 * pow(10, decimals_diff)
    else:
        swap_price = _reserve1 / _reserve0 * pow(10, -decimals_diff)
    return swap_price


def get_token_price_forever():
    while 1:
        (token0_amount, token1_amount, ts_date) = get_token_reserves(the_pair_address)
        print(f'#开始查询价格数据')
        print(f'raw result: {token0_amount}, {token1_amount}, {ts_date}')

        print(f'last_time: {datetime.fromtimestamp(ts_date).strftime("%Y-%m-%d %H:%M:%S")}')
        swap_price = calc_token_price_busd(token0_amount, token1_amount)
        print(f'swap_price: {swap_price}')
        print(f'price after dex fee: ({DEX_FEE_RATE}%): {swap_price * (1 - DEX_FEE_RATE / 100)}')
        print(f'#等待10秒后继续获取价格\n')
        time.sleep(10)


if __name__ == '__main__':
    token0 = Web3.toChecksumAddress(TOKEN0_CONTRACT_ADDRESS)
    token1 = Web3.toChecksumAddress(TOKEN1_CONTRACT_ADDRESS)
    # sort
    (token0, token1) = (token0, token1) if (token0 < token1) else (token1, token0)

    # address: 0xed71CeF3517Fb764A8e03359e54cC88020e39857
    the_pair_address = calc_pair_address(token0, token1)
    # print(f"the_pair_address: {the_pair_address}")

    # 启动无限次获取价格信息
    get_token_price_forever()
