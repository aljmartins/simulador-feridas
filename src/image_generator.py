# -*- coding: utf-8 -*-
"""
src/image_generator.py
Geração de imagem didática de ferida crônica para o Simulador TIMERS.

Provedores suportados:
  - Gemini Imagen 3  (usa GEMINI_API_KEY já configurada no app)
  - fal.ai FLUX.1    (usa FAL_KEY; requer `pip install fal-client`)

Uso básico:
    from src.image_generator import generate_wound_image_gemini, generate_wound_image_fal
    img_bytes = generate_wound_image_gemini(scenario=caso, visual_description=descricao)
    # img_bytes é PNG em bytes, pronto para st.image() ou st.download_button()
"""

import os
import base64
import requests
from typing import Optional


# ---------------------------------------------------------------------------
# Mapeamentos clínicos → termos em inglês para o prompt
# ---------------------------------------------------------------------------
_ETIOLOGY_MAP = {
    "Venosa":    "chronic venous leg ulcer on lower leg",
    "Arterial":  "arterial ulcer on foot/ankle",
    "Diabética": "diabetic foot ulcer, neuropathic",
    "Pressão":   "pressure injury stage 3, sacral or heel region",
}

_TISSUE_MAP = {
    "Necrose":    "black eschar/necrotic tissue covering the wound bed",
    "Esfacelo":   "yellow slough tissue in the wound bed",
    "Granulação": "healthy red granulation tissue filling the wound bed",
}

_EXUDATE_MAP = {
    "Seco":         "minimal to no exudate, dry wound surface",
    "Equilibrado":  "moderate serous exudate, moist wound environment",
    "Muito Molhado": "heavy serous/seropurulent exudate, macerated periwound skin",
}


def _build_wound_prompt(scenario: dict, visual_description: str = "") -> str:
    """
    Monta prompt em inglês para geração de imagem médica didática.
    Enquadrado como 'medical illustration' para reduzir bloqueios de conteúdo.
    """
    etiologia = scenario.get("etiologia", "chronic")
    tecido    = scenario.get("tecido",    "mixed tissue")
    exsudato  = scenario.get("exsudato",  "moderate exudate")
    infeccao  = bool(scenario.get("infeccao", False))

    wound_type   = _ETIOLOGY_MAP.get(etiologia,  f"{etiologia} chronic wound")
    tissue_txt   = _TISSUE_MAP.get(tecido,        tecido)
    exudate_txt  = _EXUDATE_MAP.get(exsudato,     exsudato)
    infection_txt = (
        "surrounding erythema, warmth and induration indicating local infection, "
        if infeccao else ""
    )

    extra = f" Additional context from clinical description: {visual_description.strip()}." \
        if visual_description.strip() else ""

    prompt = (
        f"Medical education illustration for nursing students: {wound_type}, "
        f"{tissue_txt}, {exudate_txt}, {infection_txt}"
        f"irregular wound margins, clinical diagram style, "
        f"labeled anatomical drawing on clean white background, "
        f"no patient identity visible, professional medical textbook illustration, "
        f"educational use only, no graphic gore, diagram labels in English."
        f"{extra}"
    )
    return prompt.strip()


# ---------------------------------------------------------------------------
# Provedor 1 — Gemini Imagen 3
# ---------------------------------------------------------------------------
def generate_wound_image_gemini(
    scenario: dict,
    visual_description: str = "",
    api_key: Optional[str] = None,
) -> Optional[bytes]:
    """
    Gera imagem via Google Gemini Imagen 3 (imagen-3.0-generate-001).

    Parâmetros
    ----------
    scenario : dict
        Dicionário do caso clínico (etiologia, tecido, exsudato, infeccao …)
    visual_description : str
        Descrição visual textual gerada pelo Gemini (campo visual_description do GeminiCaseGenerator).
    api_key : str, opcional
        GEMINI_API_KEY. Se omitido, lê de os.environ["GEMINI_API_KEY"].

    Retorna
    -------
    bytes
        PNG em bytes, ou None se o modelo não retornar imagem (ex.: bloqueio de conteúdo).

    Levanta
    -------
    ValueError
        Se a chave API não estiver configurada.
    requests.HTTPError
        Para erros HTTP da API.
    """
    api_key = (api_key or os.getenv("GEMINI_API_KEY", "")).strip()
    if not api_key:
        raise ValueError(
            "GEMINI_API_KEY não configurada. "
            "Defina em st.secrets ou na variável de ambiente GEMINI_API_KEY."
        )

    prompt = _build_wound_prompt(scenario, visual_description)

    url = (
        "https://generativelanguage.googleapis.com/v1beta/models/"
        f"imagen-3.0-generate-001:predict?key={api_key}"
    )
    payload = {
        "instances": [{"prompt": prompt}],
        "parameters": {
            "sampleCount": 1,
            "aspectRatio": "1:1",
        },
    }

    resp = requests.post(url, json=payload, timeout=90)
    resp.raise_for_status()
    data = resp.json()

    predictions = data.get("predictions") or []
    if not predictions:
        return None

    b64 = predictions[0].get("bytesBase64Encoded") or predictions[0].get("b64_json")
    if not b64:
        return None

    return base64.b64decode(b64)


# ---------------------------------------------------------------------------
# Provedor 2 — fal.ai FLUX.1-schnell (fallback)
# ---------------------------------------------------------------------------
def generate_wound_image_fal(
    scenario: dict,
    visual_description: str = "",
    api_key: Optional[str] = None,
) -> Optional[bytes]:
    """
    Gera imagem via fal.ai usando o modelo FLUX.1-schnell.

    Requer instalação: pip install fal-client

    Parâmetros
    ----------
    scenario : dict
        Dicionário do caso clínico.
    visual_description : str
        Descrição visual textual do caso.
    api_key : str, opcional
        FAL_KEY. Se omitido, lê de os.environ["FAL_KEY"].

    Retorna
    -------
    bytes
        PNG/JPEG em bytes, ou None em caso de falha silenciosa.

    Levanta
    -------
    ValueError
        Se a chave API não estiver configurada.
    ImportError
        Se fal-client não estiver instalado.
    """
    try:
        import fal_client  # noqa: F401 — import explícito para mensagem de erro clara
    except ImportError as exc:
        raise ImportError(
            "fal-client não instalado. Execute: pip install fal-client"
        ) from exc

    import fal_client as fc  # type: ignore

    api_key = (api_key or os.getenv("FAL_KEY", "")).strip()
    if not api_key:
        raise ValueError(
            "FAL_KEY não configurada. "
            "Defina em st.secrets ou na variável de ambiente FAL_KEY."
        )

    os.environ["FAL_KEY"] = api_key
    prompt = _build_wound_prompt(scenario, visual_description)

    result = fc.run(
        "fal-ai/flux/schnell",
        arguments={
            "prompt": prompt,
            "image_size": "square_hd",
            "num_images": 1,
            "num_inference_steps": 4,
            "enable_safety_checker": False,  # conteúdo médico/educacional
        },
    )

    images = (result or {}).get("images") or []
    if not images:
        return None

    image_url = images[0].get("url")
    if not image_url:
        return None

    img_resp = requests.get(image_url, timeout=60)
    img_resp.raise_for_status()
    return img_resp.content
