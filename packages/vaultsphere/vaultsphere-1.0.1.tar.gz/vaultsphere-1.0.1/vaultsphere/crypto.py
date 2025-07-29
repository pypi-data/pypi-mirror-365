from cryptography.fernet import Fernet, InvalidToken
import base64
from typing import Union


def generate_key(encoded: bool = False) -> Union[bytes, str]:
    """
    Genera una clave segura para cifrado simétrico.
    Si `encoded=True`, devuelve la clave como string Base64.
    """
    key = Fernet.generate_key()
    return key.decode() if encoded else key


def encrypt(data: Union[str, bytes], key: Union[str, bytes], output_b64: bool = True) -> Union[bytes, str]:
    """
    Cifra datos con la clave dada. Devuelve por defecto Base64 (str).
    Lanza ValueError si los tipos de datos no son válidos.
    """
    if isinstance(data, str):
        data = data.encode()
    if isinstance(key, str):
        key = key.encode()

    if not isinstance(data, bytes) or not isinstance(key, bytes):
        raise ValueError("Los datos y la clave deben ser 'str' o 'bytes'.")

    f = Fernet(key)
    encrypted = f.encrypt(data)
    return encrypted.decode() if output_b64 else encrypted


def decrypt(token: Union[str, bytes], key: Union[str, bytes], input_b64: bool = True) -> str:
    """
    Descifra un token cifrado. Lanza ValueError si la clave es inválida o hay corrupción.
    Retorna el resultado como string.
    """
    if isinstance(token, str):
        token = token.encode()
    if isinstance(key, str):
        key = key.encode()

    if not isinstance(token, bytes) or not isinstance(key, bytes):
        raise ValueError("El token y la clave deben ser 'str' o 'bytes'.")

    f = Fernet(key)
    try:
        decrypted = f.decrypt(token)
        return decrypted.decode()
    except InvalidToken:
        raise ValueError("Clave inválida o datos corruptos, no se pudo descifrar.")
