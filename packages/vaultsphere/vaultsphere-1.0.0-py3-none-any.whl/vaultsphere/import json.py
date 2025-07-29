import json
import pytest
from ..core import VaultSphere

# python

@pytest.fixture
def vault():
    key = b'0' * 32  # Dummy key for testing (not secure)
    tables = {
        "usuarios": {
            "schema": {
                "id": {"type": "integer"},
                "nombre": {"type": "string"},
                "edad": {"type": "integer"}
            },
            "primaryKey": "id",
            "unique": ["id"]
        }
    }
    # Use a dummy filename to avoid file I/O
    vault = VaultSphere(filename=":memory:", encryption_key=key, tables=tables, autosave=False)
    return vault

def test_export_table_to_json_basic(vault):
    doc1 = {"id": 1, "nombre": "Pedro", "edad": 18}
    doc2 = {"id": 2, "nombre": "Ana", "edad": 22}
    vault.insert("usuarios", doc1)
    vault.insert("usuarios", doc2)
    json_str = vault.export_table_to_json("usuarios")
    data = json.loads(json_str)
    # Should be a list of dicts
    assert isinstance(data, list)
    # Should contain both documents (with _createdAt/_updatedAt fields)
    ids = [d["id"] for d in data]
    assert set(ids) == {1, 2}
    # Check that extra fields exist
    for d in data:
        assert "_createdAt" in d
        assert "_updatedAt" in d

def test_export_table_to_json_invalid_table(vault):
    with pytest.raises(ValueError):
        vault.export_table_to_json("no_existe")