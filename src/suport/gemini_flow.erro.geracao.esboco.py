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


class GeminiImageGenerator:
    """
    Gera um esboço didático (imagem) do caso de ferida crônica.
    - Requer um modelo de geração de imagens (ex.: "imagen-3.0-generate-002").
    - Usa o google-genai SDK. A disponibilidade depende do seu plano/conta/região.
    Retorna bytes (PNG/JPEG) para uso direto no Streamlit e no PDF.
    """

    def __init__(self, model: str = "imagen-3.0-generate-002"):
        load_dotenv()
        self.client = genai.Client()
        self.model = model

    def generate_image(self, scenario: Dict[str, Any], visual_description: str) -> bytes:
        prompt = (
            "Crie um ESBOÇO DIDÁTICO, estilo ilustração simples/diagramática (não foto realista), "
            "para representar uma ferida crônica em perna/pé conforme o caso abaixo. "
            "Mostre apenas: localização aproximada, formato geral, coloração simplificada (granulação vs esfacelo/necrose), "
            "bordas e exsudato de forma simbólica. Fundo branco, sem sangue explícito, sem elementos chocantes.\n\n"
            "CENÁRIO (JSON):\n"
            f"{json.dumps(scenario, indent=2, ensure_ascii=False)}\n\n"
            "DESCRIÇÃO VISUAL:\n"
            f"{visual_description}\n"
        )

        # O google-genai expõe geração de imagens em algumas versões via client.models.generate_images
        gen_images = getattr(getattr(self.client, "models", None), "generate_images", None)
        if callable(gen_images):
            resp = gen_images(model=self.model, prompt=prompt)
            # Tentativas de extrair bytes em formatos comuns
            for attr_path in [
                ("generated_images", 0, "image", "image_bytes"),
                ("generated_images", 0, "image_bytes"),
                ("images", 0, "image_bytes"),
                ("images", 0, "bytes"),
                ("data", 0),
            ]:
                try:
                    obj = resp
                    for p in attr_path:
                        if isinstance(p, int):
                            obj = obj[p]
                        else:
                            obj = getattr(obj, p)
                    if isinstance(obj, (bytes, bytearray)) and obj:
                        return bytes(obj)
                except Exception:
                    continue

        # Fallback: algumas versões retornam base64 em campos conhecidos
        for key in ["image_base64", "b64_json", "base64_data"]:
            try:
                val = getattr(resp, key)  # type: ignore[name-defined]
                if isinstance(val, str) and val.strip():
                    return base64.b64decode(val)
            except Exception:
                pass

        raise RuntimeError(
            "Geração de imagem não disponível neste ambiente/conta/modelo. "
            "Verifique se o modelo de imagem está habilitado (ex.: imagen-3.0-generate-002) "
            "e se o google-genai SDK/credenciais suportam generate_images."
        )



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
