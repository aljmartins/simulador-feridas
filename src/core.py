# -*- coding: utf-8 -*-
"""
core.py — Núcleo do simulador (Python puro)

Este arquivo contém apenas a lógica de decisão (sem Tkinter, sem Colab, sem chamadas de API).
Entrada: dict com chaves:
  - etiologia: "Arterial" | "Venosa" | "Diabética" | "Pressão"
  - itb: float/str/None (quando aplicável)
  - tecido: "Necrose" | "Esfacelo" | "Granulação"
  - infeccao: bool
  - exsudato: "Seco" | "Moderado" | "Muito Molhado" | "Equilibrado"
  - bordas: "Estagnada" | "Avançando"

Saída: string com relatório (linhas separadas por \n)
"""

from __future__ import annotations

from typing import Any, Dict


class SimuladorLogica:
    def _to_float(self, value: Any, default: float = 1.0) -> float:
        try:
            if value is None or value == "":
                return default
            return float(value)
        except (TypeError, ValueError):
            return default

    def _norm(self, value: Any, default: str) -> str:
        if value is None:
            return default
        s = str(value).strip()
        return s if s else default

    def avaliar(self, dados: Dict[str, Any]) -> str:
        relatorio = []

        # Normalização de entrada (evita KeyError e entradas vazias)
        etiologia = self._norm(dados.get("etiologia"), "Venosa")
        tecido = self._norm(dados.get("tecido"), "Granulação")
        exsudato = self._norm(dados.get("exsudato"), "Equilibrado")
        bordas = self._norm(dados.get("bordas"), "Avançando")
        infeccao = bool(dados.get("infeccao", False))

        # ITB só é clínico para arterial/venosa; default 1.0
        itb_default = 1.0
        itb = self._to_float(dados.get("itb"), default=itb_default)

        relatorio.append(f"📋 DIAGNÓSTICO: Úlcera {etiologia.upper()} (ITB: {itb})")
        relatorio.append("-" * 50)

        pode_desbridar = True
        pode_comprimir = False

        # 1) ANÁLISE ETIOLÓGICA (CAUSA)
        if etiologia == "Arterial":
            if itb < 0.5:
                relatorio.append("🚫 [PERIGO] ITB < 0.5: ISQUEMIA CRÍTICA")
                relatorio.append("   • AÇÃO: Encaminhar ao Cirurgião Vascular URGENTE")
                relatorio.append("   • PROIBIDO: Desbridamento (risco de gangrena)")
                relatorio.append("   • PROIBIDO: Compressão")
                pode_desbridar = False
            elif itb < 0.9:
                relatorio.append("⚠️ [ALERTA] Doença Arterial Periférica")
                relatorio.append("   • AÇÃO: Avaliação Vascular necessária")
                relatorio.append("   • AÇÃO: Não usar compressão")
            else:
                # Pode acontecer por calcificação (ITB falsamente alto/normal) — manter atenção.
                relatorio.append("⚠️ [ATENÇÃO] Ferida Arterial (Confirmar diagnóstico / considerar calcificação)")

        elif etiologia == "Venosa":
            if itb < 0.8:
                relatorio.append("⚠️ [CUIDADO] Doença Mista (Venosa + Arterial)")
                relatorio.append("   • AÇÃO: Compressão leve/supervisionada apenas")
            else:
                relatorio.append("✅ [CONDUTA] Fluxo Arterial Normal")
                relatorio.append("   • AÇÃO OURO: Compressão (30–40 mmHg) + Elevação")
                pode_comprimir = True

        elif etiologia == "Diabética":
            relatorio.append("🦶 [PÉ DIABÉTICO]")
            relatorio.append("   • AÇÃO: OFFLOADING (retirar carga/peso do local)")
            if infeccao:
                relatorio.append("   • AÇÃO: Teste 'Probe-to-Bone' para suspeita de osteomielite")

        elif etiologia == "Pressão":
            relatorio.append("🛏️ [ÚLCERA POR PRESSÃO]")
            relatorio.append("   • AÇÃO: Mudança de decúbito a cada 2 horas")
            relatorio.append("   • AÇÃO: Colchão pneumático/almofada de ar")

        else:
            relatorio.append("⚠️ [ATENÇÃO] Etiologia não reconhecida — revisar entrada.")

        relatorio.append("\n--- PROTOCOLO T.I.M.E. (TRATAMENTO LOCAL) ---")

        # T — TISSUE
        if tecido in ["Necrose", "Esfacelo"]:
            if pode_desbridar:
                relatorio.append(f"🛡️ T (Tecido): {tecido} detectado")
                relatorio.append("   -> CONDUTA: Desbridamento (remoção de tecido inviável)")
            else:
                relatorio.append(f"🛑 T (Tecido): {tecido} presente")
                relatorio.append("   -> CONDUTA: NÃO DESBRIDAR (isquemia). Manter seco (ex.: PVPI)")
        elif tecido == "Granulação":
            relatorio.append("❤️ T (Tecido): Granulação (vermelho vivo)")
            relatorio.append("   -> CONDUTA: Proteger o leito (não friccionar)")
        else:
            relatorio.append(f"🩹 T (Tecido): {tecido}")
            relatorio.append("   -> CONDUTA: Registrar e reavaliar (categoria não padrão)")

        # I — INFECTION
        if infeccao:
            relatorio.append("🦠 I (Infecção): Sinais presentes")
            relatorio.append("   -> CONDUTA: Cobertura antimicrobiana (prata, PHMB, cadexômero)")
            if etiologia in ["Diabética", "Arterial"]:
                relatorio.append("   -> ALERTA: Considerar antibiótico sistêmico (maior risco)")
        else:
            relatorio.append("✨ I (Infecção): Ferida limpa")

        # M — MOISTURE
        if exsudato == "Seco":
            if pode_desbridar:
                relatorio.append("🌵 M (Umidade): Leito seco")
                relatorio.append("   -> CONDUTA: Hidrogel (hidratar)")
            else:
                relatorio.append("🌵 M (Umidade): Seco e isquêmico")
                relatorio.append("   -> CONDUTA: MANTER SECO (evitar infecção)")
        elif exsudato == "Muito Molhado":
            relatorio.append("🌊 M (Umidade): Exsudato excessivo")
            relatorio.append("   -> CONDUTA: Espumas ou alginatos (absorção)")
        else:
            relatorio.append("💧 M (Umidade): Equilibrado")
            relatorio.append("   -> CONDUTA: Manter curativo atual / monitorar")

        # E — EDGE
        if bordas == "Estagnada":
            relatorio.append("⏹️ E (Bordas): Paradas/Enroladas")
            relatorio.append("   -> CONDUTA: Reavaliar diagnóstico ou considerar terapia avançada")
        else:
            relatorio.append("⏩ E (Bordas): Avançando (epitelizando)")

        # Nota final de compressão (quando aplicável)
        if etiologia == "Venosa":
            if pode_comprimir:
                relatorio.append("\n✅ Compressão: Liberada (conforme ITB e etiologia).")
            else:
                relatorio.append("\n⚠️ Compressão: Evitar / apenas leve e supervisionada (doença mista).")

        return "\n".join(relatorio)
