# -*- coding: utf-8 -*-

from __future__ import annotations

from abc import ABC, abstractmethod

from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes


class ICipher(ABC):
    """ Base class for all cypher implementations """

    def __init__(
            self, key: bytes = None, mode: int = AES.MODE_GCM,
            encoding: str = "UTF-8") -> None:

        if not key:
            key = get_random_bytes(32 if mode == AES.MODE_SIV else 16)

        self.key = key
        self.encoding = encoding
        self.mode = mode

    @abstractmethod
    def encrypt(self, data, *args, **kwargs):
        """ Encrypt the data """

    @abstractmethod
    def decrypt(self, data, *args, **kwargs):
        """ Decrypt the data """
