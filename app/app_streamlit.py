# -*- coding: utf-8 -*-
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT))

import streamlit as st
from dotenv import load_dotenv

# caminho relativo (robusto)
LOGO = Path(__file__).parent / "assets" / "logos.jpeg"

# mostra no topo
st.image(str(LOGO), use_container_width=True)
st.divider()  # opcional: uma linha separando

from src.core import SimuladorLogica
# IMAGENS DESATIVADAS TEMPORARIAMENTE (crédito Gemini / NumPy / Python 3.14)
from src.gemini_flow import GeminiCaseGenerator, GeminiFeedbackGenerator
# from src.pdf_report import gerar_pdf_relatorio  # DESATIVADO: exportação PDF (mantido como referência)
# import tempfile  # DESATIVADO: exportação PDF (mantido como referência)
# from datetime import datetime  # DESATIVADO: exportação PDF (mantido como referência)

load_dotenv()

st.set_page_config(page_title="Simulador TIMERS", layout="centered")
st.markdown(
    "<h2>Simulador TIMERS – Feridas Crônicas. PET G10 UFPel</h2>",
    unsafe_allow_html=True
)


# ---------- SIDEBAR: Exportar PDF (global) ----------
# st.sidebar.subheader("Exportar PDF")
# ep = st.session_state.get("export_payload", {})
# 
# st.sidebar.caption("O PDF usa o último conteúdo gerado em qualquer aba (Simulador, Treino ou Estudante).")
# 
# origem = ep.get("origem") or "—"
# st.sidebar.write(f"**Fonte atual:** {origem}")
# 
# Campos (mostra o que já existe)
# has_caso = bool(ep.get("caso"))
# has_resp = bool(str(ep.get("resposta_estudante", "")).strip())
# has_fb = bool(str(ep.get("feedback", "")).strip())
# 
# st.sidebar.write("**Conteúdo disponível:**")
# st.sidebar.write(f"- Caso: {'✅' if has_caso else '—'}")
# st.sidebar.write(f"- Resposta do estudante: {'✅' if has_resp else '—'}")
# st.sidebar.write(f"- Feedback: {'✅' if has_fb else '—'}")
# 
# if st.sidebar.button("Gerar PDF agora", key="global_pdf_btn"):
#     from datetime import datetime
#     import tempfile
# 
#     ts = datetime.now().strftime("%Y%m%d-%H%M")
#     caso = ep.get("caso") or {}
#     eti = (caso.get("etiologia") if isinstance(caso, dict) else "caso") or "caso"
#     nome_arquivo = f"relatorio_{eti}_{ts}.pdf".replace(" ", "_")
# 
    # Monta strings (garante que nada quebre)
#     conteudo_caso = caso if isinstance(caso, dict) else {"caso": str(caso)}
#     resposta = ep.get("resposta_estudante", "") or "—"
#     plano_ideal = ep.get("plano_ideal", "") or "—"
#     feedback = ep.get("feedback", "") or "—"
# 
#     with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
#         gerar_pdf_relatorio(
#             path=tmp.name,
#             caso=conteudo_caso,
#             resposta_estudante=str(resposta),
#             plano_ideal=str(plano_ideal),
#             feedback=str(feedback),
#         )
#         with open(tmp.name, "rb") as f:
#             st.sidebar.download_button(
#                 label="📄 Baixar PDF",
#                 data=f,
#                 file_name=nome_arquivo,
#                 mime="application/pdf",
#                 key="global_pdf_download",
#             )
# 
# st.sidebar.divider()

# Prefixos de keys (evita StreamlitDuplicateElementId)
K_MANUAL = "manual"
K_TREINO = "treino"
K_ESTUDANTE = "estudante"

# ==============================
# EXPORTAÇÃO GLOBAL (PDF)
# A ideia: qualquer aba pode atualizar estes campos, e o PDF pode ser gerado a qualquer momento.
# ==============================
if "export_payload" not in st.session_state:
    st.session_state["export_payload"] = {
        "origem": "",
        "caso": None,
        "descricao_visual": "",
        "resposta_estudante": "",
        "plano_ideal": "",
        "feedback": "",
    }

def _set_export_payload(**kwargs):
    st.session_state["export_payload"].update({k: v for k, v in kwargs.items() if v is not None})


tabs = st.tabs(["Simulador (manual)", "Treino (Gemini)", "Estudante: inserir caso"])

# ---------- TAB 1: Manual ----------
with tabs[0]:
    st.subheader("Simulador clínico (entrada manual)")

    col1, col2 = st.columns(2)
    with col1:
        etiologia = st.selectbox(
            "Etiologia",
            ["Arterial", "Venosa", "Diabética", "Pressão"],
            key=f"{K_MANUAL}_etiologia",
        )
        itb = st.text_input("ITB (ex: 0.9)", value="1.0", key=f"{K_MANUAL}_itb")
        tecido = st.selectbox(
            "Tecido",
            ["Necrose", "Esfacelo", "Granulação"],
            key=f"{K_MANUAL}_tecido",
        )

    with col2:
        infeccao = st.checkbox("Sinais de infecção", key=f"{K_MANUAL}_infeccao")
        exsudato = st.selectbox(
            "Exsudato",
            ["Seco", "Equilibrado", "Muito Molhado"],
            key=f"{K_MANUAL}_exsudato",
        )
        bordas = st.selectbox(
            "Bordas",
            ["Estagnada", "Avançando"],
            key=f"{K_MANUAL}_bordas",
        )

    if st.button("Avaliar (manual)", key=f"{K_MANUAL}_avaliar"):
        dados = {
            "etiologia": etiologia,
            "itb": itb,
            "tecido": tecido,
            "infeccao": infeccao,
            "exsudato": exsudato,
            "bordas": bordas,
        }
        sim = SimuladorLogica()
        rel = sim.avaliar(dados)
        st.text(rel)
        _set_export_payload(origem="Simulador (manual)", caso=dados, plano_ideal=rel, feedback="")

# ---------- TAB 2: Treino com Gemini ----------
with tabs[1]:
    st.subheader("Treino: gerar caso via Gemini + resposta do estudante + feedback")

    if f"{K_TREINO}_case" not in st.session_state:
        st.session_state[f"{K_TREINO}_case"] = None
        st.session_state[f"{K_TREINO}_visual"] = ""
        st.session_state[f"{K_TREINO}_ideal"] = ""
        st.session_state[f"{K_TREINO}_feedback"] = ""

    colA, colB = st.columns(2)
    with colA:
        model_case = st.text_input(
            "Modelo (caso/descrição)",
            value="gemini-3-flash-preview",
            key=f"{K_TREINO}_model_case",
        )
    with colB:
        model_feedback = st.text_input(
            "Modelo (feedback)",
            value="gemini-3-flash-preview",
            key=f"{K_TREINO}_model_feedback",
        )

    if st.button("Gerar caso (Gemini)", key=f"{K_TREINO}_gerar"):
        try:
            gen = GeminiCaseGenerator(model=model_case)
            out = gen.generate_case()
            st.session_state[f"{K_TREINO}_case"] = out.scenario
            st.session_state[f"{K_TREINO}_visual"] = out.visual_description

            sim = SimuladorLogica()
            ideal = sim.avaliar(out.scenario)
            st.session_state[f"{K_TREINO}_ideal"] = ideal
            _set_export_payload(origem="Treino (Gemini)", caso=out.scenario, descricao_visual=out.visual_description, plano_ideal=ideal)

            st.success("Caso gerado. Agora o estudante responde e você gera o feedback.")
        except Exception as e:
            st.error(f"Falhou ao gerar caso. Verifique GEMINI_API_KEY no .env. Detalhe: {e}")

    case = st.session_state[f"{K_TREINO}_case"]
    if case:
        st.markdown("### Cenário (JSON)")
        st.json(case)

        st.markdown("### Descrição visual")
        st.write(st.session_state[f"{K_TREINO}_visual"])

        # --------- IMAGEM SINTÉTICA (GEMINI) ---------
        # DESATIVADA TEMPORARIAMENTE
        st.info("Imagem sintética desativada temporariamente (crédito Gemini / NumPy / Python 3.14).")

        st.markdown("### Resposta do estudante")
        estudante_plano = st.text_area(
            "Digite o plano do estudante (TIME + condutas específicas):",
            height=180,
            key=f"{K_TREINO}_plano",
        )

        col1, col2 = st.columns(2)
        with col1:
            if st.button("Mostrar plano ideal (core)", key=f"{K_TREINO}_mostrar_ideal"):
                st.markdown("### Plano ideal (core)")
                st.text(st.session_state[f"{K_TREINO}_ideal"])

        with col2:
            if st.button("Gerar feedback (Gemini)", key=f"{K_TREINO}_feedback_btn"):
                if not estudante_plano.strip():
                    st.warning("O estudante ainda não escreveu nada.")
                else:
                    try:
                        fb = GeminiFeedbackGenerator(model=model_feedback)
                        feedback = fb.generate_feedback(
                            scenario=case,
                            visual_description=st.session_state[f"{K_TREINO}_visual"],
                            student_plan=estudante_plano,
                            ideal_plan=st.session_state[f"{K_TREINO}_ideal"],
                        )
                        st.session_state[f"{K_TREINO}_feedback"] = feedback
                        _set_export_payload(origem="Treino (Gemini)", caso=case, descricao_visual=st.session_state.get(f"{K_TREINO}_visual",""), resposta_estudante=estudante_plano, plano_ideal=st.session_state.get(f"{K_TREINO}_ideal",""), feedback=feedback)
                        st.markdown("### Feedback ao estudante")
                        st.write(feedback)
                    except Exception as e:
                        st.error(f"Falhou ao gerar feedback. Verifique GEMINI_API_KEY no .env. Detalhe: {e}")
    else:
        st.info("Clique em 'Gerar caso (Gemini)' para iniciar o treino.")

# ---------- TAB 3: Estudante insere caso + feedback robusto ----------
with tabs[2]:
    st.subheader("Estudante: inserir caso clínico")

    if f"{K_ESTUDANTE}_dados" not in st.session_state:
        st.session_state[f"{K_ESTUDANTE}_dados"] = None
        st.session_state[f"{K_ESTUDANTE}_ideal"] = ""
        st.session_state[f"{K_ESTUDANTE}_feedback"] = ""

    modo = st.radio(
        "Como você quer inserir o caso?",
        ["Formulário", "Colar JSON"],
        horizontal=True,
        key=f"{K_ESTUDANTE}_modo",
    )

    sim = SimuladorLogica()

    if modo == "Formulário":
        col1, col2 = st.columns(2)

        with col1:
            etiologia = st.selectbox(
                "Etiologia",
                ["Arterial", "Venosa", "Diabética", "Pressão"],
                key=f"{K_ESTUDANTE}_etiologia",
            )
            itb = st.text_input(
                "ITB (deixe em branco se não aplicável)",
                value="",
                key=f"{K_ESTUDANTE}_itb",
            )
            tecido = st.selectbox(
                "Tecido",
                ["Necrose", "Esfacelo", "Granulação"],
                key=f"{K_ESTUDANTE}_tecido",
            )

        with col2:
            infeccao = st.checkbox("Sinais de infecção", key=f"{K_ESTUDANTE}_infeccao")
            exsudato = st.selectbox(
                "Exsudato",
                ["Seco", "Equilibrado", "Muito Molhado"],
                key=f"{K_ESTUDANTE}_exsudato",
            )
            bordas = st.selectbox(
                "Bordas",
                ["Estagnada", "Avançando"],
                key=f"{K_ESTUDANTE}_bordas",
            )

        if st.button("Avaliar caso do estudante", key=f"{K_ESTUDANTE}_avaliar_form"):
            dados = {
                "etiologia": etiologia,
                "itb": itb if itb.strip() else None,
                "tecido": tecido,
                "infeccao": infeccao,
                "exsudato": exsudato,
                "bordas": bordas,
            }
            st.session_state[f"{K_ESTUDANTE}_dados"] = dados
            st.session_state[f"{K_ESTUDANTE}_ideal"] = sim.avaliar(dados)

            st.markdown("### Relatório (core / TIME)")
            st.text(st.session_state[f"{K_ESTUDANTE}_ideal"])

    else:
        st.caption("Cole um JSON com as chaves: etiologia, itb, tecido, infeccao, exsudato, bordas.")
        raw = st.text_area("JSON do caso", height=220, key=f"{K_ESTUDANTE}_json")

if st.button("Avaliar JSON do estudante", key=f"{K_ESTUDANTE}_avaliar_json"):
    import json
    try:
        dados = json.loads(raw)
        st.session_state[f"{K_ESTUDANTE}_dados"] = dados
        st.session_state[f"{K_ESTUDANTE}_ideal"] = sim.avaliar(dados)

        st.markdown("### Relatório (core / TIME)")
        st.text(st.session_state[f"{K_ESTUDANTE}_ideal"])

        _set_export_payload(
            origem="Estudante: inserir caso",
            caso=st.session_state.get(f"{K_ESTUDANTE}_dados"),
            plano_ideal=st.session_state.get(f"{K_ESTUDANTE}_ideal",""),
        )
    except Exception as e:
        st.error(f"JSON inválido ou incompleto. Detalhe: {e}")

    # --------- IMAGEM DO ESTUDANTE ---------

    # DESATIVADA TEMPORARIAMENTE
    st.info("Upload de imagem desativado temporariamente (NumPy / Python 3.14).")

    st.divider()
    st.subheader("Feedback robusto (Gemini)")

    if not st.session_state.get(f"{K_ESTUDANTE}_dados"):
        st.info("Primeiro avalie um caso (Formulário ou JSON). Depois escreva o plano do estudante e gere o feedback.")
    else:
        modelo_fb = st.text_input(
            "Modelo Gemini (feedback)",
            value="gemini-3-flash-preview",
            key=f"{K_ESTUDANTE}_model_feedback",
        )

        st.markdown("### Plano de cuidado proposto pelo estudante")
        estudante_plano = st.text_area(
            "Escreva o plano do estudante (TIME + condutas específicas):",
            height=180,
            key=f"{K_ESTUDANTE}_plano",
        )

        colx, coly = st.columns(2)
        with colx:
            if st.button("Mostrar plano ideal (core)", key=f"{K_ESTUDANTE}_mostrar_ideal"):
                st.markdown("### Plano ideal (core)")
                st.text(st.session_state[f"{K_ESTUDANTE}_ideal"])

        with coly:
            if st.button("Gerar feedback robusto (Gemini)", key=f"{K_ESTUDANTE}_gerar_feedback"):
                if not estudante_plano.strip():
                    st.warning("O estudante ainda não escreveu o plano.")
                else:
                    try:
                        fb = GeminiFeedbackGenerator(model=modelo_fb)
                        feedback = fb.generate_feedback(
                            scenario=st.session_state[f"{K_ESTUDANTE}_dados"],
                            visual_description="Caso inserido pelo estudante (sem imagem).",
                            student_plan=estudante_plano,
                            ideal_plan=st.session_state[f"{K_ESTUDANTE}_ideal"],
                        )
                        st.session_state[f"{K_ESTUDANTE}_feedback"] = feedback
                        # Guarda uma cópia com nome fixo (facilita exportação PDF)
                        st.session_state["feedback_estudante"] = feedback
                        _set_export_payload(origem="Estudante: inserir caso", caso=st.session_state.get(f"{K_ESTUDANTE}_dados"), resposta_estudante=estudante_plano, plano_ideal=st.session_state.get(f"{K_ESTUDANTE}_ideal",""), feedback=feedback)
                        st.markdown("### Feedback ao estudante")
                        st.write(feedback)
                    except Exception as e:
                        st.error(f"Falhou ao gerar feedback. Verifique GEMINI_API_KEY no .env. Detalhe: {e}")

    # ---------- EXPORTAR RELATÓRIO (PDF) ----------
#     st.divider()
#     st.subheader("Exportar relatório (PDF)")
# 
    # Dados necessários
#     caso = st.session_state.get(f"{K_ESTUDANTE}_dados")
#     plano_ideal = st.session_state.get(f"{K_ESTUDANTE}_ideal", "")
#     resposta_estudante = st.session_state.get(f"{K_ESTUDANTE}_plano", "")
#     feedback_pdf = st.session_state.get("feedback_estudante") or st.session_state.get(f"{K_ESTUDANTE}_feedback", "")
# 
#     pronto = bool(caso) and bool(plano_ideal.strip()) and bool(str(resposta_estudante).strip()) and bool(str(feedback_pdf).strip())
# 
#     if not pronto:
#         st.info("Para exportar o PDF, complete: caso + resposta do estudante + feedback.")
#     else:
#         if st.button("Gerar PDF", key=f"{K_ESTUDANTE}_pdf_btn"):
            # Nome amigável
#             ts = datetime.now().strftime("%Y%m%d-%H%M")
#             eti = (caso.get("etiologia") if isinstance(caso, dict) else "caso") or "caso"
#             nome_arquivo = f"relatorio_{eti}_{ts}.pdf".replace(" ", "_")
# 
#             with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
#                 gerar_pdf_relatorio(
#                     path=tmp.name,
#                     caso=caso,
#                     resposta_estudante=str(resposta_estudante),
#                     plano_ideal=str(plano_ideal),
#                     feedback=str(feedback_pdf),
#                 )
#                 with open(tmp.name, "rb") as f:
#                     st.download_button(
#                         label="📄 Baixar PDF",
#                         data=f,
#                         file_name=nome_arquivo,
#                         mime="application/pdf",
#                         key=f"{K_ESTUDANTE}_pdf_download",
#                     )
# 
