import json
import os
from typing import Optional

from Crypto.Cipher import AES
from loguru import logger

from local_storage.utils import get_machine_id, remove_zero_padding, zero_padding

__all__ = ['LocalStorage']


class LocalStorageError(Exception):
    def __init__(self):
        super().__init__()


class LocalStorage:
    def __init__(self, local_filename: str):
        """
        Init a local storage with given filename

        Will raise **NotSupport** error when obtaining the machine-id fails

        In Linux, machine-id is the md5 of the content in /etc/machine-id file,

        In Windows, machine-id is the md5 of the reg value in
        HKEY_LOCAL_MACHINE\\\\SOFTWARE\\\\Microsoft\\\\Cryptography\\\\MachineGuid

        The localstorage file will **ONLY** be decrypted successfully on the same machine, if decrypt fails,
        file will be removed and re-create with a warning message

        :param local_filename: storage filename
        """
        self._data: dict[str, str] = {}
        self._local_filename = local_filename
        self._read_file()

    def _encode_data(self) -> bytes:
        data_json = json.dumps(self._data)
        aes = AES.new(get_machine_id(), AES.MODE_ECB)
        data = data_json.encode('utf8')
        data = zero_padding(data)
        data = aes.encrypt(data)
        return data

    def _decode_data(self, data):
        aes = AES.new(get_machine_id(), AES.MODE_ECB)
        try:
            data = aes.decrypt(data)
            data = remove_zero_padding(data)
            data_json = data.decode('utf8')
            self._data = json.loads(data_json)
        except ValueError:
            raise LocalStorageError

    def _read_file(self):
        def create_new_file():
            _f = open(self._local_filename, 'wb')
            _f.write(self._encode_data())
            _f.close()

        if not os.path.exists(self._local_filename):
            create_new_file()
            return
        with open(self._local_filename, 'rb') as f:
            try:
                data = f.read()
                self._decode_data(data)
            except LocalStorageError:
                logger.warning("Cannot decrypt localstorage file, old file will be clear")
                create_new_file()

    def put(self, key: str, value: str):
        self._data[key] = value

    def get(self, key: str, default: Optional[str] = None) -> Optional[str]:
        return self._data.get(key, default)

    def pop(self, key: str, default: Optional[str] = None) -> Optional[str]:
        return self._data.pop(key, default)

    def save(self):
        with open(self._local_filename, 'wb') as f:
            f.write(self._encode_data())

    def __len__(self):
        return len(self._data)