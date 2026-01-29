# -*- coding: utf-8 -*-
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT))

import streamlit as st
from dotenv import load_dotenv

from src.core import SimuladorLogica
from src.gemini_flow import GeminiCaseGenerator, GeminiFeedbackGenerator, GeminiImageGenerator, GeminiConsistencyChecker


load_dotenv()

st.set_page_config(page_title="Simulador TIMERS", layout="centered")
st.title("Simulador TIMERS – Feridas Crônicas. PET G10 UFPel")

# Prefixos de keys (evita StreamlitDuplicateElementId)
K_MANUAL = "manual"
K_TREINO = "treino"
K_ESTUDANTE = "estudante"

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
        st.text(sim.avaliar(dados))

# ---------- TAB 2: Treino com Gemini ----------
with tabs[1]:
    st.subheader("Treino: gerar caso via Gemini + resposta do estudante + feedback")

    if f"{K_TREINO}_case" not in st.session_state:
        st.session_state[f"{K_TREINO}_case"] = None
        st.session_state[f"{K_TREINO}_visual"] = ""
        st.session_state[f"{K_TREINO}_ideal"] = ""

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
            st.session_state[f"{K_TREINO}_ideal"] = sim.avaliar(out.scenario)

            st.success("Caso gerado. Agora o estudante responde e você gera o feedback.")
        except Exception as e:
            st.error(f"Falhou ao gerar caso. Verifique GEMINI_API_KEY no .env. Detalhe: {e}")

    case = st.session_state[f"{K_TREINO}_case"]
    if case:
        st.markdown("### Descrição visual")
        st.write(st.session_state[f"{K_TREINO}_visual"])

# --------- IMAGEM SINTÉTICA (GEMINI) ---------
if f"{K_TREINO}_img" not in st.session_state:
    st.session_state[f"{K_TREINO}_img"] = None

model_image = st.text_input(
    "Modelo Gemini (imagem)",
    value="gemini-2.5-flash-image",
    key=f"{K_TREINO}_model_image",
)

if st.button("Gerar imagem sintética (Gemini)", key=f"{K_TREINO}_gerar_img"):
    try:
        ig = GeminiImageGenerator(model=model_image)
        img_bytes = ig.generate_image_bytes(
            scenario=case,
            visual_description=st.session_state[f"{K_TREINO}_visual"],
        )
        st.session_state[f"{K_TREINO}_img"] = img_bytes
        st.success("Imagem sintética gerada.")
    except Exception as e:
        st.error(f"Falhou ao gerar imagem: {e}")

if st.session_state.get(f"{K_TREINO}_img"):
    st.image(
        st.session_state[f"{K_TREINO}_img"],
        caption="Imagem sintética (IA) – uso educacional",
        use_container_width=True,
    )
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
            if st.button("Gerar feedback (Gemini)", key=f"{K_TREINO}_feedback"):
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
                        st.markdown("### Feedback ao estudante")
                        st.write(feedback)
                    except Exception as e:
                        st.error(f"Falhou ao gerar feedback. Verifique GEMINI_API_KEY no .env. Detalhe: {e}")
else:
    st.info("Clique em 'Gerar caso (Gemini)' para iniciar o treino.")

# ---------- TAB 3: Estudante insere caso + feedback robusto ----------
with tabs[2]:
    st.subheader("Estudante: inserir caso clínico")

    # Estado para caso inserido pelo estudante
    if f"{K_ESTUDANTE}_dados" not in st.session_state:
        st.session_state[f"{K_ESTUDANTE}_dados"] = None
        st.session_state[f"{K_ESTUDANTE}_ideal"] = ""

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
            except Exception as e:
                st.error(f"JSON inválido ou incompleto. Detalhe: {e}")

    st.markdown("### Imagem (opcional) – checar consistência")
img = st.file_uploader(
    "Envie uma imagem para checagem (png/jpg/webp)",
    type=["png", "jpg", "jpeg", "webp"],
    key=f"{K_ESTUDANTE}_img_up",
)

if img:
    st.image(img, caption="Imagem enviada pelo estudante", use_container_width=True)

    modelo_check = st.text_input(
        "Modelo Gemini (checagem imagem×parâmetros)",
        value="gemini-3-flash-preview",
        key=f"{K_ESTUDANTE}_model_check",
    )

    if st.button("Checar consistência (Gemini)", key=f"{K_ESTUDANTE}_check_btn"):
        try:
            checker = GeminiConsistencyChecker(model=modelo_check)
            result = checker.check(
                scenario=st.session_state[f"{K_ESTUDANTE}_dados"],
                image_bytes=img.getvalue(),
                mime_type=img.type,
            )
            st.markdown("### Checagem de consistência (Gemini)")
            st.json(result)
        except Exception as e:
            st.error(f"Falhou na checagem: {e}")
    
    
    # --------- FEEDBACK ROBUSTO (GEMINI) ---------
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
                        st.markdown("### Feedback ao estudante")
                        st.write(feedback)
                    except Exception as e:
                        st.error(f"Falhou ao gerar feedback. Verifique GEMINI_API_KEY no .env. Detalhe: {e}")
