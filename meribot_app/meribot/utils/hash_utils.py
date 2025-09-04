"""
utils/hash_utils.py
Funciones utilitarias para el cálculo de hash de contenido.
"""
import hashlib
from typing import Union


def calculate_sha256(text: Union[str, bytes]) -> str:
    """
    Calcula el hash SHA-256 de un texto o bytes.
    :param text: Texto o bytes a hashear
    :return: Hash hexadecimal SHA-256
    """
    if isinstance(text, str):
        text = text.encode('utf-8')
    return hashlib.sha256(text).hexdigest()


# --- Persistencia de hashes en JSON ---
import json
import os
from typing import Dict

def load_hash_db(json_path: str) -> Dict[str, str]:
    """
    Carga la base de datos de hashes desde un archivo JSON.
    :param json_path: Ruta al archivo JSON
    :return: Diccionario {doc_id: hash}
    """
    if not os.path.exists(json_path):
        return {}
    with open(json_path, 'r', encoding='utf-8') as f:
        try:
            return json.load(f)
        except Exception:
            return {}

def save_hash_db(hash_db: Dict[str, str], json_path: str):
    """
    Guarda la base de datos de hashes en un archivo JSON.
    :param hash_db: Diccionario {doc_id: hash}
    :param json_path: Ruta al archivo JSON
    """
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(hash_db, f, ensure_ascii=False, indent=2)
