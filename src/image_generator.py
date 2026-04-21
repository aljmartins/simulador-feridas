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
import io
import requests
from typing import Optional


# ---------------------------------------------------------------------------
# Mapeamentos PT-BR para a legenda sobreposta (Pillow)
# ---------------------------------------------------------------------------
_ETIOLOGY_LABEL = {
    "Venosa":    "Úlcera Venosa",
    "Arterial":  "Úlcera Arterial",
    "Diabética": "Úlcera Diabética",
    "Pressão":   "Lesão por Pressão",
}
_TISSUE_LABEL = {
    "Necrose":    "Tecido: Necrose",
    "Esfacelo":   "Tecido: Esfacelo",
    "Granulação": "Tecido: Granulação",
}
_EXUDATE_LABEL = {
    "Seco":          "Exsudato: Seco",
    "Equilibrado":   "Exsudato: Equilibrado",
    "Muito Molhado": "Exsudato: Abundante",
}


def _add_caption_bar(img_bytes: bytes, scenario: dict) -> bytes:
    """
    Adiciona uma barra de legenda em PT-BR na parte inferior da imagem.
    A imagem original não é reprocessada — apenas recebe uma faixa extra.

    Requer: pillow (já presente no requirements.txt como 'pillow').
    """
    from PIL import Image, ImageDraw, ImageFont

    # Monta as linhas da legenda a partir do cenário
    etiologia = scenario.get("etiologia", "")
    tecido    = scenario.get("tecido", "")
    exsudato  = scenario.get("exsudato", "")
    infeccao  = bool(scenario.get("infeccao", False))
    bordas    = scenario.get("bordas", "")

    linha1_parts = [
        _ETIOLOGY_LABEL.get(etiologia, etiologia),
        _TISSUE_LABEL.get(tecido, f"Tecido: {tecido}") if tecido else None,
    ]
    linha2_parts = [
        _EXUDATE_LABEL.get(exsudato, f"Exsudato: {exsudato}") if exsudato else None,
        f"Bordas: {bordas}" if bordas else None,
        "⚠ Sinais de infecção" if infeccao else None,
    ]

    linha1 = "  |  ".join(p for p in linha1_parts if p)
    linha2 = "  |  ".join(p for p in linha2_parts if p)
    linhas = [l for l in [linha1, linha2] if l]

    # Abre a imagem original
    img = Image.open(io.BytesIO(img_bytes)).convert("RGB")
    w, h = img.size

    # Dimensiona a barra proporcional à imagem
    font_size = max(18, w // 45)
    padding   = font_size // 2
    bar_height = (font_size + padding) * len(linhas) + padding * 2

    # Tenta carregar fonte; cai para padrão se não achar
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", font_size)
        font_small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", font_size)
    except Exception:
        font = ImageFont.load_default()
        font_small = font

    # Cria nova imagem com barra embaixo
    new_img = Image.new("RGB", (w, h + bar_height), color=(255, 255, 255))
    new_img.paste(img, (0, 0))

    draw = ImageDraw.Draw(new_img)

    # Fundo da barra (azul-escuro do projeto)
    draw.rectangle([(0, h), (w, h + bar_height)], fill=(30, 58, 138))  # #1e3a8a

    # Linha separadora
    draw.line([(0, h), (w, h)], fill=(37, 99, 235), width=3)  # #2563eb

    # Textos
    y = h + padding
    for i, linha in enumerate(linhas):
        f = font if i == 0 else font_small
        draw.text((padding * 2, y), linha, fill=(255, 255, 255), font=f)
        y += font_size + padding

    # Rodapé direito: "Imagem didática – Simulador TIMERS"
    rodape = "Imagem didática – Simulador TIMERS / UFPel"
    try:
        font_tiny = ImageFont.truetype(
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", max(12, font_size - 4)
        )
    except Exception:
        font_tiny = font_small
    bbox = draw.textbbox((0, 0), rodape, font=font_tiny)
    tw = bbox[2] - bbox[0]
    draw.text((w - tw - padding * 2, h + padding), rodape, fill=(147, 197, 253), font=font_tiny)

    # Salva como PNG sem perda
    out = io.BytesIO()
    new_img.save(out, format="PNG", optimize=False)
    return out.getvalue()


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
        f"educational use only, no graphic gore, all labels and annotations in Portuguese (PT-BR)."
        f"{extra}"
    )
    return prompt.strip()


# ---------------------------------------------------------------------------
# Provedor 1 — Gemini (dois sub-métodos internos; a função pública tenta em cascata)
# ---------------------------------------------------------------------------

def _gemini_imagen4(prompt: str, api_key: str) -> Optional[bytes]:
    """
    Imagen 4 via endpoint :predict  (modelo dedicado de geração de imagem).
    Documentação: https://ai.google.dev/gemini-api/docs/imagen
    """
    url = (
        "https://generativelanguage.googleapis.com/v1beta/models/"
        f"imagen-4.0-generate-001:predict?key={api_key}"
    )
    payload = {
        "instances": [{"prompt": prompt}],
        "parameters": {"sampleCount": 1, "aspectRatio": "1:1"},
    }
    resp = requests.post(url, json=payload, timeout=90)
    resp.raise_for_status()
    predictions = resp.json().get("predictions") or []
    if not predictions:
        return None
    b64 = predictions[0].get("bytesBase64Encoded") or predictions[0].get("b64_json")
    return base64.b64decode(b64) if b64 else None


def _gemini_native_image(prompt: str, api_key: str) -> Optional[bytes]:
    """
    Gemini 3.1 Flash Image Preview via generateContent (geração de imagem nativa).
    Usa o campo inlineData da resposta multimodal.
    Documentação: https://ai.google.dev/gemini-api/docs/image-generation
    """
    url = (
        "https://generativelanguage.googleapis.com/v1beta/models/"
        f"gemini-2.5-flash-image:generateContent?key={api_key}"
    )
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"responseModalities": ["TEXT", "IMAGE"]},
    }
    resp = requests.post(url, json=payload, timeout=90)
    resp.raise_for_status()
    parts = (
        resp.json()
        .get("candidates", [{}])[0]
        .get("content", {})
        .get("parts", [])
    )
    for part in parts:
        inline = part.get("inlineData") or part.get("inline_data")
        if inline and inline.get("data"):
            return base64.b64decode(inline["data"])
    return None


def generate_wound_image_gemini(
    scenario: dict,
    visual_description: str = "",
    api_key: Optional[str] = None,
) -> Optional[bytes]:
    """
    Gera imagem via Google Gemini.

    Tenta em cascata:
      1. Imagen 4  (imagen-4.0-generate-001, endpoint :predict)
      2. Gemini 2.5 Flash Image  (gemini-2.5-flash-image, endpoint generateContent)

    Parâmetros
    ----------
    scenario : dict
        Dicionário do caso clínico (etiologia, tecido, exsudato, infeccao …)
    visual_description : str
        Descrição visual textual gerada pelo Gemini.
    api_key : str, opcional
        GEMINI_API_KEY. Se omitido, lê de os.environ["GEMINI_API_KEY"].

    Retorna
    -------
    bytes
        PNG em bytes, ou None se ambos os modelos falharem silenciosamente.

    Levanta
    -------
    ValueError
        Se a chave API não estiver configurada.
    Exception
        Propaga o último erro se ambas as tentativas levantarem exceção.
    """
    api_key = (api_key or os.getenv("GEMINI_API_KEY", "")).strip()
    if not api_key:
        raise ValueError(
            "GEMINI_API_KEY não configurada. "
            "Defina em st.secrets ou na variável de ambiente GEMINI_API_KEY."
        )

    prompt = _build_wound_prompt(scenario, visual_description)
    last_exc: Optional[Exception] = None

    # Tentativa 1: Imagen 4
    try:
        result = _gemini_imagen4(prompt, api_key)
        if result:
            return _add_caption_bar(result, scenario)
    except Exception as exc:
        last_exc = exc

    # Tentativa 2: Gemini 2.5 Flash Image (nativo)
    try:
        result = _gemini_native_image(prompt, api_key)
        if result:
            return _add_caption_bar(result, scenario)
    except Exception as exc:
        last_exc = exc

    if last_exc:
        raise last_exc
    return None


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
    return _add_caption_bar(img_resp.content, scenario)
