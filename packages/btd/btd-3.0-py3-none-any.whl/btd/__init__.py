from typing import Union, Any
import struct

class BTD:
    def __init__(self, key: bytes = b'mysecretkey'):
        self.key = key

    def _xor(self, data: bytes) -> bytes:
        return bytes([b ^ self.key[i % len(self.key)] for i, b in enumerate(data)])

    # Serializa dados recursivamente para linhas no formato:
    # <path> \t <tipo> \t <valor_serializado>
    def _serialize(self, data: Any, prefix=[]) -> list[str]:
        lines = []

        if data is None:
            lines.append("\t".join(prefix + ['none', 'None']))
        elif isinstance(data, bool):
            lines.append("\t".join(prefix + ['bool', str(data)]))
        elif isinstance(data, int):
            lines.append("\t".join(prefix + ['int', str(data)]))
        elif isinstance(data, float):
            lines.append("\t".join(prefix + ['float', repr(data)]))
        elif isinstance(data, str):
            lines.append("\t".join(prefix + ['str', data]))
        elif isinstance(data, list):
            lines.append("\t".join(prefix + ['list', str(len(data))]))
            for i, item in enumerate(data):
                lines.extend(self._serialize(item, prefix + [f"item{i}"]))
        elif isinstance(data, dict):
            lines.append("\t".join(prefix + ['dict', str(len(data))]))
            for k, v in data.items():
                if not isinstance(k, str):
                    raise TypeError("Only str keys are supported in dict")
                lines.extend(self._serialize(v, prefix + [k]))
        else:
            raise TypeError(f"Unsupported data type: {type(data)}")

        return lines

    def _serialize_dict(self, d: dict) -> bytes:
        lines = self._serialize(d, [])
        return "\n".join(lines).encode('utf-8')

    # Desserializa linhas tabuladas para reconstruir dados recursivamente
    def _deserialize(self, lines: list[str]) -> Any:
        def parse_path(path_parts, d, value_type, value):
            if not path_parts:
                # raiz (não deve acontecer)
                return

            key = path_parts[0]
            if len(path_parts) == 1:
                # valor final
                if value_type == 'none':
                    d[key] = None
                elif value_type == 'bool':
                    d[key] = (value == 'True')
                elif value_type == 'int':
                    d[key] = int(value)
                elif value_type == 'float':
                    d[key] = float(value)
                elif value_type == 'str':
                    d[key] = value
                elif value_type == 'list':
                    d[key] = []
                elif value_type == 'dict':
                    d[key] = {}
                else:
                    raise ValueError(f"Unknown type {value_type}")
                return

            # chave intermediária
            if key not in d:
                if value_type == 'list':
                    d[key] = []
                elif value_type == 'dict':
                    d[key] = {}
                else:
                    d[key] = {}

            parse_path(path_parts[1:], d[key], value_type, value)

        # Primeiro, vamos armazenar as linhas com estrutura para processar após
        # Mas o formato atual não guarda ordem para preencher listas automaticamente
        # Então vamos montar uma árvore auxiliar

        tree = {}
        types_map = {}

        for line in lines:
            parts = line.strip().split("\t")
            if len(parts) < 3:
                continue
            *path_parts, value_type, value = parts
            # Registra o tipo do nó na árvore para construir depois
            cursor = tree
            for i, p in enumerate(path_parts):
                if p not in cursor:
                    cursor[p] = {}
                cursor = cursor[p]
            # Armazena tipo e valor no nível final
            cursor["_type"] = value_type
            cursor["_value"] = value

        def build(obj):
            if not isinstance(obj, dict):
                return obj
            if "_type" not in obj:
                # Não é um nó terminal, monta dict recursivamente
                res = {}
                for k, v in obj.items():
                    if k.startswith("_"):
                        continue
                    res[k] = build(v)
                return res

            t = obj["_type"]
            v = obj["_value"]
            if t == 'none':
                return None
            elif t == 'bool':
                return v == "True"
            elif t == 'int':
                return int(v)
            elif t == 'float':
                return float(v)
            elif t == 'str':
                return v
            elif t == 'list':
                # Construir lista dos itemX ordenados
                lst = []
                # pega keys item0, item1, ...
                items = [(k, obj[k]) for k in obj if k.startswith("item")]
                # ordena por índice
                items.sort(key=lambda x: int(x[0][4:]))
                for _, val in items:
                    lst.append(build(val))
                return lst
            elif t == 'dict':
                d = {}
                for k, val in obj.items():
                    if k.startswith("_"):
                        continue
                    if not k.startswith("item"):
                        d[k] = build(val)
                return d
            else:
                raise ValueError(f"Unknown type {t}")

        return build(tree)

    def _deserialize_dict(self, data: bytes) -> dict:
        text = data.decode('utf-8')
        lines = text.strip().split('\n')
        return self._deserialize(lines)

    def save(self, data: Union[str, dict, list, int, float, bool, None], path: str, chunk_size: int = None):
        if isinstance(data, str):
            type_byte = b'\x01'
            raw = data.encode('utf-8')
        else:
            type_byte = b'\x02'
            raw = self._serialize_dict(data)

        encrypted = self._xor(raw)

        if chunk_size is None:
            with open(path, 'wb') as f:
                f.write(type_byte)
                f.write(len(encrypted).to_bytes(4, 'big'))
                f.write(encrypted)
        else:
            chunks = [encrypted[i:i+chunk_size] for i in range(0, len(encrypted), chunk_size)]
            with open(path, 'wb') as f:
                f.write(type_byte)
                f.write(len(chunks).to_bytes(4, 'big'))
                for chunk in chunks:
                    f.write(len(chunk).to_bytes(4, 'big'))
                    f.write(chunk)

    def load(self, path: str) -> Union[str, dict, list, int, float, bool, None]:
        with open(path, 'rb') as f:
            type_byte = f.read(1)
            # Descobre se arquivo está chunked lendo próximo 4 bytes
            # Se esses 4 bytes forem tamanho > 0 (normal) ou número chunks
            # Para manter compatibilidade vamos assumir que sempre tem num_chunks
            num_chunks = int.from_bytes(f.read(4), 'big')
            encrypted = b''
            for _ in range(num_chunks):
                size = int.from_bytes(f.read(4), 'big')
                chunk = f.read(size)
                encrypted += chunk

        decrypted = self._xor(encrypted)

        if type_byte == b'\x01':
            return decrypted.decode('utf-8')
        elif type_byte == b'\x02':
            return self._deserialize_dict(decrypted)
        else:
            raise ValueError("Unknown data type in BTD file")

    def get_size(self, data: Union[str, dict, list, int, float, bool, None]) -> int:
        if isinstance(data, str):
            raw = data.encode('utf-8')
        else:
            raw = self._serialize_dict(data)
        encrypted = self._xor(raw)
        return len(encrypted)

    def is_btd(self, path: str) -> bool:
        try:
            with open(path, 'rb') as f:
                type_byte = f.read(1)
                num_chunks_bytes = f.read(4)
                num_chunks = int.from_bytes(num_chunks_bytes, 'big')
                content_len = 0
                for _ in range(num_chunks):
                    chunk_size_bytes = f.read(4)
                    chunk_size = int.from_bytes(chunk_size_bytes, 'big')
                    f.seek(chunk_size, 1)
                    content_len += chunk_size
            return type_byte in (b'\x01', b'\x02') and content_len > 0
        except Exception:
            return False

    def to_bin(self, text: str) -> str:
        return ' '.join(f'{b:08b}' for b in text.encode('utf-8'))

    def from_bin(self, binary: str) -> str:
        bytes_list = binary.split()
        return bytes(int(b, 2) for b in bytes_list).decode('utf-8')