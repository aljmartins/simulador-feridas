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
            "Você é um professor clínico exigente, justo e pedagógico.\n\n"
            "REGRA IMPORTANTE:\n"
            "- Sempre forneça feedback ao estudante, mesmo que o plano esteja incompleto ou superficial.\n"
            "- NÃO bloqueie a avaliação por falta de dados.\n"
            "- Se faltar informação relevante, aponte isso como lacuna no feedback.\n\n"
            "Dados do cenário da ferida (JSON):\n"
            f"{json.dumps(scenario, indent=2, ensure_ascii=False)}\n\n"
            "Descrição visual detalhada da ferida:\n"
            f"{visual_description}\n\n"
            "Proposta de tratamento do estudante:\n"
            f"{student_plan}\n\n"
            "Plano de tratamento ideal (gerado pelo simulador):\n"
            f"{ideal_plan}\n\n"
            "Compare a proposta do estudante com o plano ideal, considerando T.I.M.E. "
            "(Tecido, Infecção, Umidade, Bordas) e a etiologia da ferida.\n\n"
            "Se o estudante não abordar algum desses pontos, registre como lacuna pedagógica, "
            "sem interromper a avaliação.\n\n"
            "Formato do feedback:\n"
            "1) Pontos fortes do plano apresentado\n"
            "2) Aspectos ausentes ou pouco desenvolvidos\n"
            "3) Riscos potenciais e considerações de segurança\n"
            "4) Sugestões práticas de melhoria\n\n"
            "Use linguagem clara, direta, encorajadora e tecnicamente correta."
        )

        resp = self.client.models.generate_content(model=self.model, contents=prompt)
        return (resp.text or "").strip()

from google.genai import types
import base64


# ==============================
# IMAGEM (DESATIVADA TEMPORARIAMENTE)
# Motivo: crédito Gemini / NumPy / Python 3.14
# Reativar quando ambiente estiver estável
# ==============================

# INÍCIO TRECHO ADICIONADO 

class GeminiCaseFromTextExtractor:
    """
    Lê um texto corrido (descrição do caso) e:
    - ou extrai um scenario JSON no formato do simulador
    - ou retorna perguntas objetivas quando faltar dado essencial.
    """

    def __init__(self, model: str = "gemini-3-flash-preview"):
        load_dotenv()
        self.client = genai.Client()
        self.model = model

    def extract_or_ask(self, case_text: str) -> Dict[str, Any]:
        prompt = (
            "Você é um professor clínico. Você vai ler uma descrição em texto corrido de um caso de ferida crônica.\n\n"
            "TAREFA:\n"
            "1) Se o texto tiver informação suficiente, extraia um JSON com o formato EXATO abaixo.\n"
            "2) Se faltar informação essencial para preencher o JSON com confiança, NÃO invente. Em vez disso, retorne status NEED_MORE_INFO e uma lista curta de perguntas.\n\n"
            "FORMATO DE SAÍDA (retorne APENAS JSON, sem texto extra):\n"
            "{\n"
            '  "status": "OK" ou "NEED_MORE_INFO",\n'
            '  "scenario": {\n'
            '    "etiologia": "Arterial|Venosa|Diabética|Pressão",\n'
            '    "itb": number ou null,\n'
            '    "tecido": "Necrose|Esfacelo|Granulação",\n'
            '    "infeccao": true|false,\n'
            '    "exsudato": "Seco|Equilibrado|Muito Molhado",\n'
            '    "bordas": "Estagnada|Avançando"\n'
            "  },\n"
            '  "questions": "string com perguntas (somente se NEED_MORE_INFO)"\n'
            "}\n\n"
            "REGRAS IMPORTANTES:\n"
            "- itb só faz sentido para etiologia Arterial ou Venosa; caso contrário, use null.\n"
            "- Se houver dúvida real entre opções (ex.: tecido), use NEED_MORE_INFO.\n"
            "- Perguntas devem ser diretas e poucas (no máximo 6), priorizando segurança.\n\n"
            "TEXTO DO CASO:\n"
            f"{case_text}"
        )

        resp = self.client.models.generate_content(model=self.model, contents=prompt)
        raw = _strip_code_fences(resp.text or "")
        data = json.loads(raw)

        # sanity-check leve: se OK sem scenario, força NEED_MORE_INFO
        if data.get("status") == "OK" and not isinstance(data.get("scenario"), dict):
            return {
                "status": "NEED_MORE_INFO",
                "scenario": None,
                "questions": "Não consegui estruturar o caso. Informe etiologia, tecido, infecção, exsudato e bordas (e ITB se arterial/venosa).",
            }
        return data


# FIM TRECHO ADICIONADO


# ==============================
# IMAGEM (GERAÇÃO DE ESBOÇO)
# - NÃO usa upload do usuário
# - gera uma imagem simples (didática) a partir de um prompt
# ==============================

class GeminiImageGenerator:
    """Gera uma imagem (esboço didático) via modelos de imagem.

    Retorna bytes PNG/JPEG (dependendo do modelo). O app pode exibir e embutir no PDF.
    A implementação tenta múltiplas rotas do SDK para ficar resiliente a versões.
    """

    def __init__(self, model: str = "imagen-3.0-generate-002"):
        load_dotenv()
        self.client = genai.Client()
        self.model = model

    def generate_image_bytes(self, prompt: str) -> bytes:
        # Tentativa 1: client.models.generate_images (algumas versões)
        if hasattr(self.client, "models") and hasattr(self.client.models, "generate_images"):
            try:
                resp = self.client.models.generate_images(
                    model=self.model,
                    prompt=prompt,
                    config=types.GenerateImagesConfig(number_of_images=1) if hasattr(types, "GenerateImagesConfig") else None,
                )
                # Resp pode trazer imagens em resp.generated_images ou resp.images
                imgs = None
                for attr in ("generated_images", "images", "data"):
                    if hasattr(resp, attr):
                        imgs = getattr(resp, attr)
                        break
                if imgs:
                    item = imgs[0]
                    # item pode ter .image_bytes, .bytes, .data (base64)
                    for a in ("image_bytes", "bytes", "data"):
                        if hasattr(item, a) and getattr(item, a) is not None:
                            v = getattr(item, a)
                            if isinstance(v, (bytes, bytearray)):
                                return bytes(v)
                            if isinstance(v, str):
                                import base64
                                return base64.b64decode(v)
                raise RuntimeError("Resposta de imagem inesperada (generate_images).")
            except Exception as e:
                # cai para a próxima tentativa
                last_err = e
        else:
            last_err = None

        # Tentativa 2: alguns SDKs expõem client.images.generate
        if hasattr(self.client, "images") and hasattr(self.client.images, "generate"):
            try:
                resp = self.client.images.generate(model=self.model, prompt=prompt)
                # resp pode ter bytes/base64
                if hasattr(resp, "images") and resp.images:
                    item = resp.images[0]
                    if hasattr(item, "image_bytes") and item.image_bytes is not None:
                        return bytes(item.image_bytes)
                    if hasattr(item, "data") and isinstance(item.data, str):
                        import base64
                        return base64.b64decode(item.data)
                raise RuntimeError("Resposta de imagem inesperada (images.generate).")
            except Exception as e:
                last_err = e

        # Tentativa 3: fallback — não suportado
        msg = "SDK/modelo não suportou geração de imagem neste ambiente."
        if last_err:
            msg += f" Detalhe: {last_err}"
        raise RuntimeError(msg)

    def build_prompt_from_case(self, scenario: dict, visual_description: str) -> str:
        # Prompt curto e seguro: 'esboço' didático, sem gore
        return (
            "Crie um esboço didático e simples (estilo ilustração clínica neutra) de uma ferida crônica "+
            "para fins educacionais. Não mostre sangue excessivo nem detalhes gráficos. "
            "Use fundo claro. "
            "Baseie-se nesta descrição: "
            f"{visual_description}" 
        )

    def generate_case_sketch(self, scenario: dict, visual_description: str) -> bytes:
        prompt = self.build_prompt_from_case(scenario, visual_description)
        return self.generate_image_bytes(prompt)
