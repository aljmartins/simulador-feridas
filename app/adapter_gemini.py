import os

def get_gemini_api_key():
    """
    Lê a chave da API do ambiente.
    NUNCA coloque a chave diretamente no código.
    """
    key = os.getenv("GEMINI_API_KEY")
    if not key:
        raise RuntimeError("GEMINI_API_KEY não definida no ambiente.")
    return key
