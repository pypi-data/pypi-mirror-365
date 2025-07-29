from typing import List, Dict, Set, Optional, Union, Tuple

class IndexManager:
    def __init__(self):
        # Estructura: { tabla: { campo(s): set(valores) } }
        self.indices: Dict[str, Dict[Union[str, Tuple[str, ...]], Set]] = {}

    def create_index(self, table: str, fields: Union[str, List[str]]):
        """
        Crea un índice para uno o varios campos.
        """
        if table not in self.indices:
            self.indices[table] = {}

        if isinstance(fields, str):
            fields = [fields]

        key = tuple(fields) if len(fields) > 1 else fields[0]
        if key not in self.indices[table]:
            self.indices[table][key] = set()

    def drop_index(self, table: str, fields: Union[str, List[str]]):
        """
        Elimina un índice existente.
        """
        if isinstance(fields, str):
            fields = [fields]

        key = tuple(fields) if len(fields) > 1 else fields[0]

        if table in self.indices and key in self.indices[table]:
            del self.indices[table][key]

    def add_value(self, table: str, fields: Union[str, List[str]], value: Union[str, Tuple]):
        """
        Agrega un valor al índice.
        """
        if isinstance(fields, str):
            fields = [fields]
        key = tuple(fields) if len(fields) > 1 else fields[0]

        if table in self.indices and key in self.indices[table]:
            self.indices[table][key].add(value)

    def remove_value(self, table: str, fields: Union[str, List[str]], value: Union[str, Tuple]):
        """
        Elimina un valor del índice.
        """
        if isinstance(fields, str):
            fields = [fields]
        key = tuple(fields) if len(fields) > 1 else fields[0]

        if table in self.indices and key in self.indices[table]:
            self.indices[table][key].discard(value)

    def exists(self, table: str, fields: Union[str, List[str]], value: Union[str, Tuple]) -> bool:
        """
        Verifica si el valor existe en el índice.
        """
        if isinstance(fields, str):
            fields = [fields]
        key = tuple(fields) if len(fields) > 1 else fields[0]

        return (
            table in self.indices and
            key in self.indices[table] and
            value in self.indices[table][key]
        )

    def rebuild_index(self, table: str, fields: Union[str, List[str]], data: List[dict]):
        """
        Reconstruye un índice para un campo o combinación de campos dado.
        """
        if isinstance(fields, str):
            fields = [fields]
        key = tuple(fields) if len(fields) > 1 else fields[0]

        if table not in self.indices:
            self.indices[table] = {}

        self.indices[table][key] = set()

        for doc in data:
            try:
                if isinstance(key, tuple):
                    val = tuple(doc.get(f) for f in key)
                else:
                    val = doc.get(key)
                if all(v is not None for v in (val if isinstance(val, tuple) else [val])):
                    self.indices[table][key].add(val)
            except Exception as e:
                print(f"[IndexManager] Error reconstruyendo índice: {e}")
