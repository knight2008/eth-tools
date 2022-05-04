#!/usr/bin/env python3
# coding : utf-8
# Date : 2022/5/4
# Author: knight2008
# QQ&Wechat: 496966425
# TG: @knight2008
# Filename: create_eth_address.py
# Github: https://github.com/knight2008
# 版权：自由转载-开源免费-任意使用

# 功能: 根据助记词批量生成ETH地址, 并输出到文件
# 版本: Python 3.8.6
# 依赖库:
# pip install hdwallet


from hdwallet import BIP44HDWallet
from hdwallet.cryptocurrencies import EthereumMainnet
from hdwallet.derivations import BIP44Derivation
from hdwallet.utils import generate_mnemonic
import time

author_info = "#感谢使用, 如有问题请联系作者反馈, QQ&Wechat: 496966425, TG: @knight2008"
sleep_info = "#本程序30秒后自动退出"

# 默认地址数量
ADDRESS_COUNT: int = 5
# 助记词对应的密码, 主流钱包一般默认为空
PASSPHRASE = None

privatekey_list = []
address_list = []


def batch_create_address(_mnemonic, _address_count, _passphrase=PASSPHRASE):
    bip44_hdwallet: BIP44HDWallet = BIP44HDWallet(cryptocurrency=EthereumMainnet)
    bip44_hdwallet.from_mnemonic(mnemonic=_mnemonic, language="english", passphrase=_passphrase)
    bip44_hdwallet.clean_derivation()
    print(f"#本次助记词:\n{_mnemonic}")
    # print("HD 路径:  m/44'/60'/0'/0")
    print("#index,privatekey,address")
    for address_index in range(_address_count):
        bip44_derivation: BIP44Derivation = BIP44Derivation(
            cryptocurrency=EthereumMainnet, account=0, change=False, address=address_index
        )
        bip44_hdwallet.from_path(path=bip44_derivation)
        private_key = bip44_hdwallet.private_key()
        address = bip44_hdwallet.address()
        print(f"{address_index},{private_key},{address}")
        privatekey_list.append(private_key)
        address_list.append(address)

        bip44_hdwallet.clean_derivation()


if __name__ == "__main__":
    # 测试的助记词, 请不要使用在主链环境中
    # "hello mandate pool ignore hollow loop amateur sail dog inner pistol spell"
    input_words = input(f'>请粘贴助记词到此处(默认随机生成):')
    if input_words is None or 0 == len(input_words.strip()):
        # 随机产生助记词
        input_words = generate_mnemonic(language="english", strength=128)

    input_number = input(f'>请输入需要创建的地址数量(默认{ADDRESS_COUNT}):')
    if input_number is None or 0 == len(input_number.strip()):
        input_number = ADDRESS_COUNT

    input_number = int(input_number)
    # 开始生成地址
    print(f"#开始生成地址")
    batch_create_address(input_words, input_number)
    print("#生成地址完毕\n")

    print("#开始写入文件")
    privatekey_file = "privatekey.txt"
    address_file = "address.txt"

    with open(privatekey_file, "w") as fout1:
        fout1.writelines("\n".join(privatekey_list))
    with open(address_file, "w") as fout2:
        fout2.writelines("\n".join(address_list))

    print(f"#写入文件完毕")
    print(f"#私钥文件: {privatekey_file}, 地址文件: {address_file}\n")
    print(f"{author_info}")
    print(f"{sleep_info}")
    time.sleep(30)
