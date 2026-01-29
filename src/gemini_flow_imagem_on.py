# -*- coding: utf-8 -*-
from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass
from typing import Any, Dict, Optional, Tuple

from dotenv import load_dotenv
from google import genai  # google-genai SDK


def _strip_code_fences(text: str) -> str:
    t = text.strip()
    # Remove ```json ... ``` or ``` ... ``` fences if present
    t = re.sub(r"^```(?:json)?\s*", "", t, flags=re.IGNORECASE)
    t = re.sub(r"\s*```$", "", t)
    return t.strip()


@dataclass
class GeminiOutputs:
    scenario: Dict[str, Any]
    visual_description: str


class GeminiCaseGenerator:
    """
    Gera cenário (JSON) + descrição visual via Gemini.
    Lê a chave do ambiente: GEMINI_API_KEY (recomendado via .env)
    """

    def __init__(self, model: str = "gemini-3-flash-preview"):
        load_dotenv()  # carrega .env se existir
        # O client pega GEMINI_API_KEY automaticamente do ambiente
        self.client = genai.Client()
        self.model = model

    def generate_scenario_json(self) -> Dict[str, Any]:
        prompt = (
            "Gere um cenário de ferida crônica fictícia em formato JSON. Inclua os seguintes parâmetros:\n"
            "{\n"
            '  "etiologia": "string (escolha entre \'Arterial\', \'Venosa\', \'Diabética\', \'Pressão\')",\n'
            '  "itb": "float (valor entre 0.0 e 1.5; use null se etiologia não for Arterial ou Venosa)",\n'
            '  "tecido": "string (escolha entre \'Necrose\', \'Esfacelo\', \'Granulação\')",\n'
            '  "infeccao": "boolean (true ou false)",\n'
            '  "exsudato": "string (escolha entre \'Seco\', \'Moderado\', \'Muito Molhado\')",\n'
            '  "bordas": "string (escolha entre \'Estagnada\', \'Avançando\')"\n'
            "}\n"
            "Certifique-se de que o ITB seja nulo se a etiologia não for Arterial ou Venosa. "
            "Por exemplo, se a etiologia for 'Diabética' ou 'Pressão', defina itb como null. "
            "Retorne APENAS o JSON."
        )

        resp = self.client.models.generate_content(model=self.model, contents=prompt)
        text = _strip_code_fences(resp.text or "")
        return json.loads(text)

    def generate_visual_description(self, scenario: Dict[str, Any]) -> str:
        prompt = (
            "Crie uma descrição visual detalhada e realista de uma ferida crônica, baseada nos seguintes dados:\n"
            f"{json.dumps(scenario, indent=2, ensure_ascii=False)}\n\n"
            "Descreva a aparência geral da ferida, o leito da ferida, as bordas, a pele perilesional, "
            "e quaisquer sinais de infecção ou exsudato conforme os parâmetros dados. "
            "Seja descritivo como se estivesse observando a ferida."
        )
        resp = self.client.models.generate_content(model=self.model, contents=prompt)
        return (resp.text or "").strip()

    def generate_case(self) -> GeminiOutputs:
        scenario = self.generate_scenario_json()
        visual = self.generate_visual_description(scenario)
        return GeminiOutputs(scenario=scenario, visual_description=visual)


class GeminiFeedbackGenerator:
    """
    Gera feedback pedagógico comparando resposta do aluno vs plano ideal.
    """

    def __init__(self, model: str = "gemini-3-flash-preview"):
        load_dotenv()
        self.client = genai.Client()
        self.model = model

    def generate_feedback(
        self,
        scenario: Dict[str, Any],
        visual_description: str,
        student_plan: str,
        ideal_plan: str,
    ) -> str:
        prompt = (
            "Dados do cenário da ferida (JSON):\n"
            f"{json.dumps(scenario, indent=2, ensure_ascii=False)}\n\n"
            "Descrição visual detalhada da ferida:\n"
            f"{visual_description}\n\n"
            "Proposta de tratamento do estudante:\n"
            f"{student_plan}\n\n"
            "Plano de tratamento ideal (gerado pelo simulador):\n"
            f"{ideal_plan}\n\n"
            "Compare a proposta do estudante com o plano ideal, focando no protocolo T.I.M.E. "
            "(Tecido, Infecção, Umidade, Bordas) e nas condutas específicas para a etiologia.\n\n"
            "Forneça feedback construtivo ao estudante, abordando:\n"
            "1) O que está correto/relevante\n"
            "2) O que está incorreto ou incompleto\n"
            "3) Condutas específicas que faltaram e por quê\n"
            "4) Linguagem clara, pedagógica e encorajadora (priorize segurança do paciente)\n\n"
            "Formate com títulos e marcadores, como um professor faria."
        )
        resp = self.client.models.generate_content(model=self.model, contents=prompt)
        return (resp.text or "").strip()

from google.genai import types
import base64

class GeminiImageGenerator:
    """
    Gera uma imagem sintética a partir do cenário + descrição visual.
    Modelo recomendado:
      - gemini-2.5-flash-image (rápido)  [Nano Banana]
      - gemini-3-pro-image-preview (mais caprichado)
    """
    def __init__(self, model: str = "gemini-2.5-flash-image"):
        load_dotenv()
        self.client = genai.Client()
        self.model = model

    def generate_image_bytes(self, scenario: dict, visual_description: str) -> bytes:
        prompt = (
            "Gere UMA imagem sintética, estilo fotografia clínica, para fins educacionais. "
            "NÃO inclua texto na imagem. Fundo neutro. "
            "Baseie-se no cenário e descrição abaixo.\n\n"
            f"CENÁRIO (JSON): {json.dumps(scenario, ensure_ascii=False)}\n\n"
            f"DESCRIÇÃO VISUAL: {visual_description}\n"
        )

        resp = self.client.models.generate_content(
            model=self.model,
            contents=prompt,
        )

        # O SDK pode devolver partes multimodais. Procuramos a parte de imagem.
        for c in getattr(resp, "candidates", []) or []:
            for p in getattr(getattr(c, "content", None), "parts", []) or []:
                inline = getattr(p, "inline_data", None)
                if inline and getattr(inline, "data", None):
                    return inline.data  # bytes

        raise RuntimeError("Não encontrei bytes de imagem na resposta do modelo.")

class GeminiConsistencyChecker:
    """
    Analisa imagem enviada e compara com parâmetros do caso inserido pelo estudante.
    Retorna JSON estruturado (melhor para rubrica).
    """
    def __init__(self, model: str = "gemini-3-flash-preview"):
        load_dotenv()
        self.client = genai.Client()
        self.model = model

    def check(self, scenario: dict, image_bytes: bytes, mime_type: str) -> dict:
        prompt = (
            "Você é um avaliador clínico-educacional. "
            "Compare a imagem da ferida com os parâmetros fornecidos pelo estudante.\n"
            "Retorne APENAS um JSON com:\n"
            "{\n"
            '  "resumo_visual": "texto curto do que aparece na imagem",\n'
            '  "coerente": true/false,\n'
            '  "inconsistencias": [ {"campo": "...", "parametro": "...", "imagem_sugere": "...", "impacto": "alto|medio|baixo"} ],\n'
            '  "perguntas_ao_estudante": ["..."],\n'
            '  "confianca": "alta|media|baixa"\n'
            "}\n\n"
            f"PARÂMETROS DO ESTUDANTE (JSON): {json.dumps(scenario, ensure_ascii=False)}"
        )

        part = types.Part.from_bytes(data=image_bytes, mime_type=mime_type)

        resp = self.client.models.generate_content(
            model=self.model,
            contents=[prompt, part],
        )
        text = _strip_code_fences(resp.text or "")
        return json.loads(text)
