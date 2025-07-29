# btd.py

from typing import Union

class BTD:
    def __init__(self, key: bytes = b'mysecretkey'):
        self.key = key

    def _xor(self, data: bytes) -> bytes:
        return bytes([b ^ self.key[i % len(self.key)] for i, b in enumerate(data)])

    def _serialize_dict(self, d: dict) -> bytes:
        # serialize dict to text lines: "key\tvalue\n"
        lines = [f"{k}\t{v}" for k, v in d.items()]
        text = "\n".join(lines)
        return text.encode('utf-8')

    def _deserialize_dict(self, data: bytes) -> dict:
        text = data.decode('utf-8')
        d = {}
        for line in text.strip().split("\n"):
            if '\t' in line:
                k, v = line.split('\t', 1)
                d[k] = v
        return d

    def save(self, data: Union[str, dict], path: str):
        if isinstance(data, str):
            type_byte = b'\x01'
            raw = data.encode('utf-8')
        elif isinstance(data, dict):
            type_byte = b'\x02'
            raw = self._serialize_dict(data)
        else:
            raise TypeError("Only str or dict supported")

        encrypted = self._xor(raw)
        length = len(encrypted).to_bytes(4, 'big')

        with open(path, 'wb') as f:
            f.write(type_byte)
            f.write(length)
            f.write(encrypted)

    def load(self, path: str) -> Union[str, dict]:
        with open(path, 'rb') as f:
            type_byte = f.read(1)
            length = int.from_bytes(f.read(4), 'big')
            encrypted = f.read(length)

        decrypted = self._xor(encrypted)

        if type_byte == b'\x01':
            return decrypted.decode('utf-8')
        elif type_byte == b'\x02':
            return self._deserialize_dict(decrypted)
        else:
            raise ValueError("Unknown data type in BTD file")

    def split_chunks(self, data: bytes, size: int = 1024) -> list[bytes]:
        return [data[i:i+size] for i in range(0, len(data), size)]

    def get_size(self, data: Union[str, dict]) -> int:
        if isinstance(data, str):
            raw = data.encode('utf-8')
        elif isinstance(data, dict):
            raw = self._serialize_dict(data)
        else:
            raise TypeError("Only str or dict supported")
        encrypted = self._xor(raw)
        return len(encrypted)

    def is_btd(self, path: str) -> bool:
        try:
            with open(path, 'rb') as f:
                type_byte = f.read(1)
                length_bytes = f.read(4)
                length = int.from_bytes(length_bytes, 'big')
                content = f.read(length)
            return type_byte in (b'\x01', b'\x02') and len(content) == length
        except Exception:
            return False

    def to_bin(self, text: str) -> str:
        return ' '.join(f'{b:08b}' for b in text.encode('utf-8'))

    def from_bin(self, binary: str) -> str:
        bytes_list = binary.split()
        return bytes(int(b, 2) for b in bytes_list).decode('utf-8')