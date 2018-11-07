# -*- coding: utf-8 -*-
"""
    SwarmOps.utils.aes_cbc
    ~~~~~~~~~~~~~~

    AES加密的实现模式CBC。
    CBC使用密码和salt（起扰乱作用）按固定算法（md5）产生key和iv。然后用key和iv（初始向量，加密第一块明文）加密（明文）和解密（密文）。

    :copyright: (c) 2018 by staugur.
    :license: MIT, see LICENSE for more details.
"""

from Crypto.Cipher import AES
from binascii import b2a_hex, a2b_hex
from config import SYSTEM


class CBC():
    """密钥生成器"""

    def __init__(self):
        # key长度要求16的倍数
        self.key = SYSTEM["AES_CBC_KEY"]
        self.mode = AES.MODE_CBC

    def encrypt(self, text):
        # 加密函数，如果text不是16的倍数【加密文本text必须为16的倍数！】，那就补足为16的倍数
        cryptor = AES.new(self.key, self.mode, self.key)
        # 这里密钥key 长度必须为16（AES-128）、24（AES-192）、或32（AES-256）Bytes 长度.目前AES-128足够用
        length = 16
        count = len(text)
        add = length - (count % length)
        text = text + ('\0' * add)
        self.ciphertext = cryptor.encrypt(text)
        # 因为AES加密时候得到的字符串不一定是ascii字符集的，输出到终端或者保存时候可能存在问题
        # 所以这里统一把加密后的字符串转化为16进制字符串
        return b2a_hex(self.ciphertext)

    def decrypt(self, text):
        # 解密后，去掉补足的空格用strip() 去掉
        cryptor = AES.new(self.key, self.mode, self.key)
        plain_text = cryptor.decrypt(a2b_hex(text))
        return plain_text.rstrip('\0')
