import os
import streamlit as st
from google import genai
from google.genai import types

# =========================
# Configuração do app
# =========================
st.set_page_config(page_title="Ensina Feridas (Gemini)", layout="centered")
st.title("🩹 Ensina Feridas – Gemini")
st.caption("Streamlit + Google GenAI (SDK novo: `google-genai`).")

# =========================
# Pega API key (secrets > env)
# Aceita GOOGLE_API_KEY (preferido) ou GEMINI_API_KEY (legado)
# =========================
def get_api_key() -> str | None:
    # secrets.toml (recomendado)
    for k in ("GOOGLE_API_KEY", "GEMINI_API_KEY"):
        if k in st.secrets:
            v = st.secrets.get(k)
            if v:
                return v

    # variáveis de ambiente
    return os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")

api_key = get_api_key()
if not api_key:
    st.error(
        "Faltou a chave da API.

"
        "Defina em `.streamlit/secrets.toml` como `GOOGLE_API_KEY = "..."` "
        "(ou `GEMINI_API_KEY`, se preferir) — ou crie a variável de ambiente `GOOGLE_API_KEY`."
    )
    st.stop()

# Cliente (SDK novo)
client = genai.Client(api_key=api_key)

# =========================
# Modelos disponíveis (cache)
# =========================
@st.cache_data(ttl=3600, show_spinner=False)
def list_generate_models() -> list[str]:
    models: list[str] = []
    try:
        for m in client.models.list():
            actions = getattr(m, "supported_actions", None) or []
            if "generateContent" in actions and getattr(m, "name", None):
                models.append(m.name)
    except Exception:
        # Fallback “na unha” (se a listagem falhar por rede/permissão etc.)
        models = [
            "models/gemini-2.0-flash",
            "models/gemini-2.5-flash",
            "models/gemini-2.5-pro",
            "models/gemini-2.0-flash-lite",
        ]
    # evita lista vazia
    return models or [
        "models/gemini-2.0-flash",
        "models/gemini-2.5-flash",
        "models/gemini-2.5-pro",
    ]

available_models = list_generate_models()

# =========================
# Controles do usuário
# =========================
col1, col2 = st.columns([2, 1])
with col1:
    model_name = st.selectbox("Modelo", available_models, index=0)
with col2:
    temperature = st.slider("Temperatura", 0.0, 1.0, 0.3, 0.05)

system_hint = st.text_area(
    "Contexto/Persona (opcional)",
    value=(
        "Você é um especialista em feridas crônicas e protocolos de cuidado (TIME/TIMERS). "
        "Responda com orientação clínica segura e prática. "
        "Se faltarem dados, faça perguntas objetivas. "
        "Evite prescrever doses/condutas de alto risco sem contexto clínico."
    ),
    height=140,
)

prompt = st.text_area(
    "Descreva o caso clínico ou faça uma pergunta:",
    height=220,
    placeholder="Ex.: Paciente com úlcera venosa há 8 meses, exsudato moderado, bordas maceradas...",
)

# =========================
# Execução
# =========================
def build_prompt(user_text: str) -> str:
    # Mantém compatível com modelos que não têm 'system role' nativo nesse caminho
    return f"""INSTRUÇÕES (contexto):
{system_hint}

SOLICITAÇÃO DO USUÁRIO:
{user_text}

REGRAS:
- Seja prático e didático.
- Se houver risco (ex.: sinais de infecção sistêmica, isquemia grave, dor desproporcional), recomende avaliação presencial.
"""

if st.button("Enviar para o Gemini", type="primary"):
    if not prompt.strip():
        st.warning("Escreve algo antes. O modelo não lê pensamento (ainda). 😄")
        st.stop()

    with st.spinner("Gerando resposta..."):
        try:
            resp = client.models.generate_content(
                model=model_name,
                contents=build_prompt(prompt),
                config=types.GenerateContentConfig(
                    temperature=temperature,
                ),
            )

            st.subheader("Resposta:")
            text = getattr(resp, "text", None)
            if text:
                st.write(text)
            else:
                # Se vier em outro formato, mostramos o objeto para debug
                st.write(resp)

        except Exception as e:
            st.error("Erro ao chamar o Gemini:")
            st.exception(e)

st.divider()
st.caption("Dica: um projeto = um .venv. E, se der erro estranho, reinicie o terminal/VS Code.")
