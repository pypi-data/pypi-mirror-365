# -*- coding: utf-8 -*-

from binascii import hexlify, unhexlify
from typing import Dict

from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad

from .base import ICipher


class AESCipher(ICipher):
    """
    Cipher that use AES (Advanced Encryption Standard) method with MODE_GCM

    This symmetric/reversible key encryption block clipper is equipped
    to handle 128-bit blocks, using keys sized at 128, 192, and 256
    bits.

    This block chipper is especially recognized for protecting data at rest,
    and it's widely regarded as the most secure symmetric key encryption cipher
    yet invented.

    AES Cipher Modes
    The cipher modes are required for a usual AES implementation. An incorrect
    implementation or application of modes may severely compromise the AES
    algorithm security. There are multiple chipper modes are available
    in AES, Some highly used AES cipher modes as follows:

        - ECB mode: Electronic Code Book mode
        - CBC mode: Cipher Block Chaining mode
        - CFB mode: Cipher Feedback mode
        - OFB mode: Output FeedBack mode
        - CTR mode: Counter mode
        - GCM mode: Galois/Counter mode

    CBC mode: Cipher Block Chaining mode
    In CBC the mode, every encryption of the same plaintext should result
    in a different ciphertext. The CBC mode does this with an initialization
    vector. The vector has the same size as the block that is encrypted.

    Problems in (CBC mode)
    One of the major problems an error of one plaintext block will affect all
    the following blocks. At the same time, Cipher Block Chaining mode(CBC) is
    vulnerable to multiple attack types:

        - Chosen Plaintext Attack(CPA)
        - Chosen Ciphertext Attack(CCA)
        - Padding oracle attacks

    AES-GCM instead of AES-CBC
    Both the AES-CBC and AES-GCM are able to secure your valuable data
    with a good implementation. but to prevent complex CBC attacks such
    as Chosen Plaintext Attack(CPA) and Chosen Ciphertext Attack(CCA)
    it is necessary to use Authenticated Encryption. So the best option
    is for that is GCM. AES-GCM is written in parallel which means throughput
    is significantly higher than AES-CBC by lowering encryption overheads.

    AES-GCM
    In simple terms, Galois Counter Mode (GCM) block clipper is a combination
    of Counter mode (CTR) and Authentication it’s faster and more secure with a
    better implementation for table-driven field operations. GCM has two
    operations, authenticated encryption and authenticated decryption.

    The GCM mode will accept pipelined and parallelized implementations
    and have minimal computational latency in order to be useful at high
    data rates. As a conclusion, we can choose the Galois Counter Mode (GCM)
    block clipper mode to achieve excellent security performance for
    data at rest.
    """

    iv_modes = (AES.MODE_CCM, AES.MODE_EAX, AES.MODE_GCM, AES.MODE_SIV, AES.MODE_OCB, AES.MODE_CTR)
    nonce_modes = (AES.MODE_CBC, AES.MODE_CFB, AES.MODE_OFB, AES.MODE_OPENPGP)
    BLOCK_SIZE = 32

    def encrypt(self, data: str, *args, **kwargs) -> Dict:
        """
        It encrypts the data and returns...

            { "ciphertext": ..., "tag": ..., "nonce or iv": ... }

        :param data: The data to encrypt.
        :return: A dictionary.
        """

        data = bytes(data, encoding=self.encoding)
        cipher = AES.new(self.key, self.mode)  # type: ignore

        if self.mode in (AES.MODE_ECB, ):
            data = pad(data, self.BLOCK_SIZE)

        ciphertext = cipher.encrypt(data)
        tag = cipher.digest() if self.mode != AES.MODE_ECB else None

        res = (
            ("ciphertext", ciphertext),
            ("tag", tag),
            ("nonce", getattr(cipher, "nonce", None)),
            ("iv", getattr(cipher, "iv", None))
        )

        return {
            key: hexlify(value).decode(encoding=self.encoding)
            for key, value in res if value
        }

    def decrypt(self, data: Dict, *args, **kwargs):
        """
        It decrypts the encrypted value...

        :param data: Dictionary that contains: ciphertext, tag and nonce or iv attrs.
        :return: The decrypted value.
        """

        for key, value in data.items():
            data[key] = unhexlify(value.encode(encoding=self.encoding))

        tag = data.get("tag")
        ciphertext = data.get("ciphertext")
        nonce, iv = data.get("nonce"), data.get("iv")

        args = [nonce or iv] if self.mode != AES.MODE_ECB else []
        cipher = AES.new(self.key, self.mode, *args)  # type: ignore

        res = cipher.decrypt(ciphertext)
        if self.mode in (AES.MODE_ECB, ):
            res = unpad(res, self.BLOCK_SIZE)

        if self.mode != AES.MODE_ECB:
            cipher.verify(tag)

        return res.decode(encoding=self.encoding)
