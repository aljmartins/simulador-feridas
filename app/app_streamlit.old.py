# -*- coding: utf-8 -*-
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT))

import streamlit as st
from dotenv import load_dotenv

from src.core import SimuladorLogica
from src.gemini_flow import GeminiCaseGenerator, GeminiFeedbackGenerator

load_dotenv()

st.set_page_config(page_title="Simulador TIME", layout="centered")
st.title("Simulador TIME – Feridas Crônicas")

tabs = st.tabs(["Simulador (manual)", "Treino (Gemini)", "Estudante: inserir caso"])

# ---------- TAB 1: Manual ----------
with tabs[0]:
    st.subheader("Simulador clínico (entrada manual)")
    col1, col2 = st.columns(2)

    with col1:
        etiologia = st.selectbox("Etiologia", ["Arterial", "Venosa", "Diabética", "Pressão"], key="m_etiologia")
        itb = st.text_input("ITB (ex: 0.9)", value="1.0", key="m_itb")
        tecido = st.selectbox("Tecido", ["Necrose", "Esfacelo", "Granulação"], key="m_tecido")

    with col2:
        infeccao = st.checkbox("Sinais de infecção", key="m_infeccao")
        exsudato = st.selectbox("Exsudato", ["Seco", "Equilibrado", "Muito Molhado"], key="m_exsudato")
        bordas = st.selectbox("Bordas", ["Estagnada", "Avançando"], key="m_bordas")

    if st.button("Avaliar (manual)"):
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

# ---------- TAB 1: Training with Gemini ----------
with tabs[1]:
    st.subheader("Treino: gerar caso via Gemini + resposta do aluno + feedback")

    if "case" not in st.session_state:
        st.session_state.case = None
        st.session_state.visual = ""
        st.session_state.ideal = ""

    colA, colB = st.columns([1, 1])

    with colA:
        model_case = st.text_input("Modelo (caso/descrição)", value="gemini-3-flash-preview")
    with colB:
        model_feedback = st.text_input("Modelo (feedback)", value="gemini-3-flash-preview")

    if st.button("Gerar caso (Gemini)"):
        try:
            gen = GeminiCaseGenerator(model=model_case)
            out = gen.generate_case()
            st.session_state.case = out.scenario
            st.session_state.visual = out.visual_description

            sim = SimuladorLogica()
            st.session_state.ideal = sim.avaliar(out.scenario)

            st.success("Caso gerado. Agora o aluno responde e você gera o feedback.")
        except Exception as e:
            st.error(f"Falhou ao gerar caso. Verifique GEMINI_API_KEY no .env. Detalhe: {e}")

    if st.session_state.case:
        st.markdown("### Cenário (JSON)")
        st.json(st.session_state.case)

        st.markdown("### Descrição visual")
        st.write(st.session_state.visual)

        st.markdown("### Resposta do estudante")
        student_plan = st.text_area(
            "Digite o plano do aluno (TIME + condutas específicas):",
            height=180,
            key="student_plan",
        )

        col1, col2 = st.columns(2)
        with col1:
            if st.button("Mostrar plano ideal (core)"):
                st.markdown("### Plano ideal (core)")
                st.text(st.session_state.ideal)

        with col2:
            if st.button("Gerar feedback (Gemini)"):
                if not student_plan.strip():
                    st.warning("O aluno ainda não escreveu nada.")
                else:
                    try:
                        fb = GeminiFeedbackGenerator(model=model_feedback)
                        feedback = fb.generate_feedback(
                            scenario=st.session_state.case,
                            visual_description=st.session_state.visual,
                            student_plan=student_plan,
                            ideal_plan=st.session_state.ideal,
                        )
                        st.markdown("### Feedback ao estudante")
                        st.write(feedback)
                    except Exception as e:
                        st.error(f"Falhou ao gerar feedback. Verifique GEMINI_API_KEY no .env. Detalhe: {e}")
    else:
        st.info("Clique em 'Gerar caso (Gemini)' para iniciar o treino.")


# ---------- TAB 2: Training with Gemini ----------

with tabs[2]:
    st.subheader("aluno: inserir caso clínico (manual)")
    modo = st.radio(
    "Como você quer inserir o caso?",
    ["Formulário", "Colar JSON"],
    horizontal=True,
    key="aluno_modo"
)

    sim = SimuladorLogica()

    if modo == "Formulário":
        col1, col2 = st.columns(2)

        with col1:
            etiologia = st.selectbox("Etiologia", ["Arterial", "Venosa", "Diabética", "Pressão"])
            itb = st.text_input("ITB (deixe em branco se não aplicável)", value="")
            tecido = st.selectbox("Tecido", ["Necrose", "Esfacelo", "Granulação"])

        with col2:
            infeccao = st.checkbox("Sinais de infecção")
            exsudato = st.selectbox("Exsudato", ["Seco", "Equilibrado", "Muito Molhado"])
            bordas = st.selectbox("Bordas", ["Estagnada", "Avançando"])

        if st.button("Avaliar caso do aluno"):
            dados = {
                "etiologia": etiologia,
                "itb": itb if itb.strip() else None,
                "tecido": tecido,
                "infeccao": infeccao,
                "exsudato": exsudato,
                "bordas": bordas,
            }

            st.session_state["aluno_dados"] = dados
            st.session_state["aluno_ideal"] = sim.avaliar(dados)

            st.markdown("### Relatório (core / TIME)")
            st.text(st.session_state["aluno_ideal"])

    else:
        st.caption("Cole um JSON com as chaves: etiologia, itb, tecido, infeccao, exsudato, bordas.")

        raw = st.text_area("JSON do caso", height=220)

        if st.button("Avaliar JSON do aluno"):
            import json
            try:
                dados = json.loads(raw)

                st.session_state["aluno_dados"] = dados
                st.session_state["aluno_ideal"] = sim.avaliar(dados)

                st.markdown("### Relatório (core / TIME)")
                st.text(st.session_state["aluno_ideal"])

            except Exception as e:
                st.error(f"JSON inválido ou incompleto. Detalhe: {e}")

with tabs[2]:
    st.subheader("Aluno: inserir caso clínico (manual)")

    modo = st.radio(
        "Como você quer inserir o caso?",
        ["Formulário", "Colar JSON"],
        horizontal=True
    )

    sim = SimuladorLogica()

    if modo == "Formulário":
        col1, col2 = st.columns(2)

        with col1:
            etiologia = st.selectbox("Etiologia", ["Arterial", "Venosa", "Diabética", "Pressão"])
            itb = st.text_input("ITB (deixe em branco se não aplicável)", value="")
            tecido = st.selectbox("Tecido", ["Necrose", "Esfacelo", "Granulação"])

        with col2:
            infeccao = st.checkbox("Sinais de infecção")
            exsudato = st.selectbox("Exsudato", ["Seco", "Equilibrado", "Muito Molhado"])
            bordas = st.selectbox("Bordas", ["Estagnada", "Avançando"])

        if st.button("Avaliar caso do aluno"):
            dados = {
                "etiologia": etiologia,
                "itb": itb if itb.strip() else None,
                "tecido": tecido,
                "infeccao": infeccao,
                "exsudato": exsudato,
                "bordas": bordas,
            }

            st.session_state["aluno_dados"] = dados
            st.session_state["aluno_ideal"] = sim.avaliar(dados)

            st.markdown("### Relatório (core / TIME)")
            st.text(st.session_state["aluno_ideal"])

    else:
        st.caption("Cole um JSON com as chaves: etiologia, itb, tecido, infeccao, exsudato, bordas.")

        raw = st.text_area("JSON do caso", height=220)

        if st.button("Avaliar JSON do aluno"):
            import json
            try:
                dados = json.loads(raw)

                st.session_state["aluno_dados"] = dados
                st.session_state["aluno_ideal"] = sim.avaliar(dados)

                st.markdown("### Relatório (core / TIME)")
                st.text(st.session_state["aluno_ideal"])

            except Exception as e:
                st.error(f"JSON inválido ou incompleto. Detalhe: {e}")

