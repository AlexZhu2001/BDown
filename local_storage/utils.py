import platform

from Crypto.Hash import MD5


class NotSupport(Exception):
    def __init__(self):
        super().__init__()


def get_machine_id() -> bytes:
    system = platform.system()
    if system == 'Windows':
        import winreg
        REG_KEY = winreg.HKEY_LOCAL_MACHINE
        REG_SUBKEY = r'SOFTWARE\Microsoft\Cryptography'
        try:
            key = winreg.OpenKey(REG_KEY, REG_SUBKEY)
            val, _ = winreg.QueryValueEx(key, 'MachineGuid')
            mid = str(val).encode('utf8')
            md5 = MD5.new(mid)
            return md5.digest()
        except OSError:
            raise NotSupport()
    elif system == 'Linux':
        try:
            with open('/etc/machine-id', 'rt') as f:
                mid = f.read()
                md5 = MD5.new(mid.encode('utf8'))
                return md5.digest()
        except FileNotFoundError:
            raise NotSupport()
    else:
        raise NotSupport()


def zero_padding(data: bytes) -> bytes:
    if (x := len(data) % 16) != 0:
        x = 16 - x
        data = data + b'\x00' * x
    return data


def remove_zero_padding(data: bytes) -> bytes:
    data = data.rstrip(b'\x00')
    return data
