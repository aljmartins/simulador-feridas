# -*- coding: utf-8 -*-
import sys
from pathlib import Path

import streamlit as st

# Menos margem início
import streamlit as st

st.set_page_config(
    page_title="Simulador TIMERS",
    layout="centered"
)

st.markdown(
    """
    <style>
    .block-container {
        padding-top: 1rem !important;
    }
    h2 {
        margin-top: 0.2rem !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)
# Menos margem início fim


# Inserido Diminuir letra #
st.markdown(
    """
    <style>
    h1 {
        font-size: 1.6rem !important;
    }
    p {
        font-size: 0.95rem !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)
# Fim Inserido #


ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT))


from dotenv import load_dotenv

# Caminhos de imagens (separa web x PDF)
ASSETS_DIR = Path(__file__).resolve().parent / "assets"
LOGO_WEB = ASSETS_DIR / "logo.all.jpeg"
LOGO_PDF_BANNER = ASSETS_DIR / "logo_pdf_banner.png"  # banner horizontal para o PDF

# caminho relativo (robusto)
LOGO = LOGO_WEB
# mostra no topo
import base64

from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm
from reportlab.lib.utils import ImageReader
from datetime import datetime
from zoneinfo import ZoneInfo
from reportlab.lib.utils import ImageReader
from datetime import datetime
from zoneinfo import ZoneInfo
from pathlib import Path
import streamlit as st


data = base64.b64encode(LOGO.read_bytes()).decode("utf-8")
st.markdown(
    f"""
    <div style="text-align:center;">
      <img src="data:image/jpeg;base64,{data}" style="max-width:100%; height:auto;" />
    </div>
    """,
    unsafe_allow_html=True
)

st.markdown("<div style='height:25px;'></div>", unsafe_allow_html=True)



import streamlit as st
import os

# ==============================
# CONTROLE DE ACESSO (DESATIVADO)
# ==============================
# def check_password():
#     if "auth" not in st.session_state:
#         st.session_state.auth = False
#
#     if not st.session_state.auth:
#         st.title("Acesso restrito")
#         pwd = st.text_input("Senha", type="password")
#
#         if st.button("Entrar"):
#             if pwd == os.getenv("APP_PASSWORD"):
#                 st.session_state.auth = True
#                 st.rerun()
#             else:
#                 st.error("Senha incorreta")
#
#         st.stop()
#
# check_password()

st.divider()  # opcional: uma linha separando

from src.core import SimuladorLogica
# IMAGENS DESATIVADAS TEMPORARIAMENTE (crédito Gemini / NumPy / Python 3.14)
from src.gemini_flow import GeminiCaseGenerator, GeminiFeedbackGenerator
# from src.pdf_report import gerar_pdf_relatorio  # DESATIVADO: exportação PDF (mantido como referência)
# import tempfile  # DESATIVADO: exportação PDF (mantido como referência)
# from datetime import datetime  # DESATIVADO: exportação PDF (mantido como referência)

load_dotenv()

# ==============================
# AVISO DE CONFIGURAÇÃO (GEMINI)
# ==============================
try:
    GEMINI_API_KEY = st.secrets.get("GEMINI_API_KEY")
except Exception:
    GEMINI_API_KEY = None
GEMINI_API_KEY = (GEMINI_API_KEY or os.getenv("GEMINI_API_KEY") or "").strip() or None
if not GEMINI_API_KEY:
    st.warning(
        "⚠️ Funções com IA (Gemini) estão indisponíveis.\n\n"
        "A chave de acesso (GEMINI_API_KEY) não está configurada no ambiente/Secrets. "
        "Você ainda pode usar o simulador manual e gerar PDFs."
    )


# st.set_page_config(page_title="Capacita TIMERS", layout="centered")  # já definido no topo
st.markdown(
    "<h3>Capacita TIMERS – Feridas Crônicas</h3>",
    unsafe_allow_html=True
)

# ===== Caminhos robustos para assets (todos em app/assets) =====
APP_DIR = Path(__file__).resolve().parent        # .../app
ASSETS_DIR = APP_DIR / "assets"                  # .../app/assets

def _img_to_b64(path: Path) -> str:
    """Lê um arquivo de imagem e devolve base64. Se não existir, devolve string vazia (não quebra o app)."""
    try:
        if path.exists():
            return base64.b64encode(path.read_bytes()).decode("utf-8")
    except Exception:
        pass
    return ""

insta_path = ASSETS_DIR / "instagram.png"
enf_path   = ASSETS_DIR / "logo.enfermagem.png"

insta_b64 = _img_to_b64(insta_path)
enf_b64   = _img_to_b64(enf_path)

st.markdown(
    f"""
    <div style="display:flex; align-items:center; gap:12px; margin-top:-10px; margin-bottom:12px;">
        <img src="data:image/png;base64,{insta_b64}" width="24">
        <a href="https://www.instagram.com/amorapele_ufpel/" target="_blank"
           style="text-decoration:none; font-weight:500;">
           Amor à Pele
        </a>
        <span>|</span>
        <a href="https://www.instagram.com/g10petsaude/" target="_blank"
           style="text-decoration:none; font-weight:500;">
           PET G10
        </a>
        <span>|</span>
        <img src="data:image/png;base64,{enf_b64}" width="24">
        <a href="https://wp.ufpel.edu.br/fen/" target="_blank"
           style="text-decoration:none; font-weight:500;">
           Faculdade de Enfermagem – UFPel
        </a>
    </div>
    """,
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
        "images": [],
    }

def _set_export_payload(**kwargs):
    st.session_state["export_payload"].update({k: v for k, v in kwargs.items() if v is not None})


def _pdf_bytes_from_export_payload(ep: dict) -> bytes:
    """Gera um PDF (bytes) a partir do export_payload, com cabeçalho (logo + data/hora)."""
    buf = BytesIO()
    c = canvas.Canvas(buf, pagesize=A4)
    w, h = A4

    tz = ZoneInfo("America/Sao_Paulo")
    printed_at = datetime.now(tz).strftime("%d/%m/%Y %H:%M")

    FOOTER_TEXT = "PET G10 UFPel - Telemonitoramento de Feridas Crônicas"


    # Banner/logo do PDF (coloque o arquivo em /assets; se não existir, segue sem logo)
    # Dica: um banner horizontal funciona melhor (ex: 1600x300)
    PDF_BANNER = LOGO_PDF_BANNER
    if not PDF_BANNER.exists():
        # fallback para o logo já existente no app
        PDF_BANNER = LOGO_WEB

    def _draw_footer():
        """Rodapé em todas as páginas (texto + número da página no canto inferior direito)."""
        y_footer = 1.2*cm
        c.setFont("Helvetica", 8)
        c.drawString(2*cm, y_footer, FOOTER_TEXT)
        c.drawRightString(w - 2*cm, y_footer, f"Página {c.getPageNumber()}")

    def _draw_header():
        """Cabeçalho em todas as páginas."""
        top_y = h - 1.3*cm

        # tenta desenhar o banner, se existir
        if PDF_BANNER.exists():
            try:
                img = ImageReader(str(PDF_BANNER))
                # banner com altura fixa e largura até a margem
                max_w = w - 4*cm
                banner_h = 2.0*cm
                c.drawImage(
                    img,
                    2*cm,
                    top_y - banner_h,
                    width=max_w,
                    height=banner_h,
                    preserveAspectRatio=True,
                    mask='auto'
                )
                y_after_banner = top_y - banner_h - 0.35*cm
            except Exception:
                y_after_banner = top_y - 0.2*cm
        else:
            y_after_banner = top_y - 0.2*cm

        # título + timestamp
        c.setFont("Helvetica-Bold", 12)
        c.drawString(2*cm, y_after_banner, "Simulador TIMERS – Relatório")
        c.setFont("Helvetica", 9)
        c.drawRightString(w - 2*cm, y_after_banner, f"Impresso em: {printed_at}")

        # linha separadora
        c.line(2*cm, y_after_banner - 0.25*cm, w - 2*cm, y_after_banner - 0.25*cm)

        # y inicial do conteúdo (abaixo do cabeçalho)
        return y_after_banner - 0.75*cm

    def _new_page():
        _draw_footer()
        c.showPage()
        return _draw_header()

    def draw_block(label, text, y):
        c.setFont("Helvetica-Bold", 11)
        c.drawString(2*cm, y, label)
        y -= 0.6*cm
        c.setFont("Helvetica", 10)

        raw = (text or "—")
        raw = str(raw).replace("\r\n", "\n").replace("\r", "\n")
        lines = raw.split("\n")

        for ln in lines:
            ln = ln.rstrip()

            # Quebra linhas muito longas (simples e seguro)
            while len(ln) > 110:
                if y < 2*cm:
                    y = _new_page()
                c.drawString(2*cm, y, ln[:110])
                ln = ln[110:]
                y -= 0.45*cm

            if y < 2*cm:
                y = _new_page()
            c.drawString(2*cm, y, ln if ln else " ")
            y -= 0.45*cm

        return y - 0.35*cm

    origem = ep.get("origem") or "—"
    caso = ep.get("caso") or {}
    descricao_visual = ep.get("descricao_visual") or ""
    resposta = ep.get("resposta_estudante") or ""
    plano_ideal = ep.get("plano_ideal") or ""
    feedback = ep.get("feedback") or ""
    sketch_prompt = ep.get("sketch_prompt") or ""
    images = ep.get("images") or []  # lista de dicts: {name, bytes}

    if isinstance(caso, dict):
        caso_txt = "\n".join([f"{k}: {v}" for k, v in caso.items()])
    else:
        caso_txt = str(caso)

    y = _draw_header()
    y = draw_block("Fonte:", origem, y)
    y = draw_block("Caso:", caso_txt, y)

    if str(descricao_visual).strip():
        y = draw_block("Descrição visual:", descricao_visual, y)
    if str(resposta).strip():
        y = draw_block("Resposta do estudante:", resposta, y)
    if str(plano_ideal).strip():
        y = draw_block("Plano ideal (core / TIME):", plano_ideal, y)
    if str(feedback).strip():
        y = draw_block("Feedback (Gemini):", feedback, y)

    if str(sketch_prompt).strip():
        y = draw_block("Prompt de esboço (PT-BR):", sketch_prompt, y)


    # --- Imagens anexadas (para constar no relatório) ---
    if images:
        # título
        if y < 4*cm:
            y = _new_page()
        c.setFont("Helvetica-Bold", 11)
        c.drawString(2*cm, y, "Imagens anexadas")
        y -= 0.7*cm

        max_w = w - 4*cm
        max_h = 7*cm  # altura máxima por imagem

        for item in images[:2]:
            try:
                img_bytes = item.get("bytes") if isinstance(item, dict) else None
                if not img_bytes:
                    continue
                img = ImageReader(BytesIO(img_bytes))

                # quebra página se precisar
                if y - max_h < 2*cm:
                    y = _new_page()

                c.drawImage(
                    img,
                    2*cm,
                    y - max_h,
                    width=max_w,
                    height=max_h,
                    preserveAspectRatio=True,
                    mask='auto'
                )

                # legenda opcional
                name = (item.get("name") if isinstance(item, dict) else "") or ""
                if name:
                    c.setFont("Helvetica", 8)
                    c.drawString(2*cm, y - max_h - 0.3*cm, f"Arquivo: {name}")
                    y -= (max_h + 0.9*cm)
                else:
                    y -= (max_h + 0.6*cm)

                c.setFont("Helvetica", 10)
            except Exception:
                continue


    _draw_footer()
    c.save()
    buf.seek(0)
    return buf.getvalue()


# ==============================
# PROMPT DE ESBOÇO (SEM GERAR IMAGEM)
# Disponível em qualquer aba; gera um texto em PT-BR para o usuário copiar/colar em um gerador de imagens.
# ==============================
def _build_sketch_prompt(ep: dict) -> str:
    """Monta um prompt em português (PT-BR) para gerar um ESBOÇO didático baseado no conteúdo do export_payload.
    Não chama nenhuma API de imagem. É só texto, com wrap via st.text_area.
    """
    origem = (ep.get("origem") or "").strip() or "Simulador TIMERS"
    caso = ep.get("caso") or {}
    descricao_visual = (ep.get("descricao_visual") or "").strip()
    plano_ideal = (ep.get("plano_ideal") or "").strip()
    feedback = (ep.get("feedback") or "").strip()
    resposta_estudante = (ep.get("resposta_estudante") or "").strip()

    # Serializa caso (curto e legível)
    if isinstance(caso, dict) and caso:
        caso_txt = "; ".join([f"{k}={v}" for k, v in caso.items() if v is not None])
    else:
        caso_txt = str(caso).strip()

    # Contexto mais rico (para Treino/Estudante)
    contexto = []
    if caso_txt:
        contexto.append(f"Caso (resumo): {caso_txt}")
    if descricao_visual:
        contexto.append(f"Descrição visual (texto): {descricao_visual}")
    if plano_ideal:
        contexto.append(f"Pontos essenciais do plano ideal (core/TIME): {plano_ideal}")
    if resposta_estudante:
        contexto.append(f"Plano proposto pelo estudante (resumo): {resposta_estudante}")
    if feedback:
        contexto.append(f"Feedback ao estudante (resumo): {feedback}")

    contexto_txt = "\n".join(contexto).strip()

    prompt = f"""Crie um ESBOÇO didático (estilo infográfico simples), sem sangue explícito e sem conteúdo chocante.

Objetivo: ajudar a entender o caso e o raciocínio TIMERS/TIME.
Fonte: {origem}

INSTRUÇÕES VISUAIS:
- Layout limpo, fundo claro, traços simples, foco didático (não fotorealista).
- Use rótulos curtos em português (PT-BR).
- Evite detalhes clínicos sensacionalistas; o foco é educação e segurança do paciente.
- Se fizer sentido, use comparação lado a lado (ex.: conduta adequada vs inadequada) ou um fluxograma curto.

CONTEÚDO (baseado no caso/relatório):
{contexto_txt if contexto_txt else "—"}

ENTREGA:
- 1 imagem única (formato quadrado ou paisagem), com títulos e setas/caixas quando necessário.
"""
    return prompt.strip()


def _render_sketch_prompt_ui(ep: dict, key_prefix: str):
    """UI padrão (wrap + download).

    Regra:
    - O prompt só entra no PDF se o usuário ATIVAR (checkbox) neste fluxo.
    """
    # Exigência mínima: ter caso ou plano ideal/feedback (alguma coisa concreta)
    tem_algo = any([
        bool(ep.get("caso")),
        bool(str(ep.get("plano_ideal", "")).strip()),
        bool(str(ep.get("feedback", "")).strip()),
        bool(str(ep.get("descricao_visual", "")).strip()),
        bool(str(ep.get("resposta_estudante", "")).strip()),
    ])
    if not tem_algo:
        st.info("Gere algum conteúdo primeiro para liberar o prompt de esboço.")
        return

    flag_key = f"{key_prefix}_sketch_enabled"
    enabled = st.checkbox(
        "Incluir prompt de esboço no PDF (opcional)",
        value=bool(st.session_state.get(flag_key, False)),
        key=flag_key,
    )

    if not enabled:
        # Garante que o PDF NÃO inclua esboço se o usuário não ativar.
        ep.pop("sketch_prompt", None)
        st.caption("Ative a opção acima se quiser gerar o prompt e incluí-lo no PDF.")
        return

    prompt_txt = _build_sketch_prompt(ep).strip()
    if not prompt_txt:
        st.info("Ainda não há conteúdo suficiente para montar um prompt de esboço.")
        ep.pop("sketch_prompt", None)
        return

    # Guarda no export_payload para que o PDF inclua (apenas quando enabled=True).
    ep["sketch_prompt"] = prompt_txt

    st.text_area(
        "Prompt do esboço (PT-BR) — copie e cole no seu gerador de imagens",
        value=prompt_txt,
        height=220,
        key=f"{key_prefix}_sketch_text",
    )
    st.download_button(
        "Baixar prompt (.txt)",
        data=prompt_txt.encode("utf-8"),
        file_name="prompt_esboco.txt",
        mime="text/plain; charset=utf-8",
        key=f"{key_prefix}_sketch_download",
    )
tabs = st.tabs(["Simulador (manual)", "Capacitação (Gemini)", "Estudante: inserir caso"])

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
        st.markdown("### Relatório (core / TIME)")
        st.text(rel)
        _set_export_payload(origem="Simulador (manual)", caso=dados, plano_ideal=rel, feedback="", resposta_estudante="")

    st.divider()
    st.subheader("Finalizar")

    ep = st.session_state.get("export_payload", {})
    pronto = (
        (ep.get("origem") == "Simulador (manual)")
        and bool(ep.get("caso"))
        and bool(str(ep.get("plano_ideal", "")).strip())
    )

    if pronto:
        # (a) Esboço: após avaliar caso (formulário/manual)
        with st.expander("🖼️ Prompt de esboço (opcional)", expanded=False):
            _render_sketch_prompt_ui(ep, key_prefix=f"{K_MANUAL}_final")

        # PDF SEMPRE POR ÚLTIMO
        pdf_bytes = _pdf_bytes_from_export_payload(ep)
        eti = "caso"
        caso = ep.get("caso")
        if isinstance(caso, dict) and caso.get("etiologia"):
            eti = str(caso.get("etiologia")).strip().lower()
        st.download_button(
            "📄 Baixar PDF (pronto pra imprimir)",
            data=pdf_bytes,
            file_name=f"relatorio_manual_{eti}.pdf".replace(" ", "_"),
            mime="application/pdf",
            key=f"{K_MANUAL}_pdf_final",
            width="stretch",
        )
    else:
        st.info("Primeiro clique em **Avaliar (manual)**. Depois aparecem esboço e PDF (no final).")


# ---------- TAB 2: Treino ----------
with tabs[1]:
    st.subheader("Capacitação: gerar caso via Gemini + resposta do estudante + feedback")

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
        if not GEMINI_API_KEY:
            st.warning("GEMINI_API_KEY não configurada. Configure secrets/.env para usar o Treino.")
        else:
            try:
                gen = GeminiCaseGenerator(model=model_case)
                out = gen.generate_case()

                sim = SimuladorLogica()
                ideal = sim.avaliar(out.scenario)

                st.session_state[f"{K_TREINO}_case"] = out.scenario
                st.session_state[f"{K_TREINO}_visual"] = out.visual_description
                st.session_state[f"{K_TREINO}_ideal"] = ideal
                st.session_state[f"{K_TREINO}_feedback"] = ""

                _set_export_payload(
                    origem="Capacitação (Gemini)",
                    caso=out.scenario,
                    descricao_visual=out.visual_description,
                    plano_ideal=ideal,
                    feedback="",
                    resposta_estudante="",
                    images=[],
                )

                st.success("Caso gerado. Agora escreva a resposta do estudante e gere o feedback.")
            except Exception as e:
                st.error(f"Falhou ao gerar caso. Detalhe: {e}")

    case = st.session_state.get(f"{K_TREINO}_case")
    if not case:
        st.info("Clique em **Gerar caso (Gemini)** para iniciar a capacitação.")
    else:
        st.markdown("### Cenário (JSON)")
        st.json(case)

        st.markdown("### Descrição visual")
        st.write(st.session_state.get(f"{K_TREINO}_visual", ""))

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
                st.text(st.session_state.get(f"{K_TREINO}_ideal", ""))

        with col2:
            if st.button("Gerar feedback (Gemini)", key=f"{K_TREINO}_feedback_btn"):
                if not GEMINI_API_KEY:
                    st.warning("GEMINI_API_KEY não configurada. Configure secrets/.env para usar o feedback.")
                elif not estudante_plano.strip():
                    st.warning("O estudante ainda não escreveu nada.")
                else:
                    try:
                        fb = GeminiFeedbackGenerator(model=model_feedback)
                        feedback = fb.generate_feedback(
                            scenario=case,
                            visual_description=st.session_state.get(f"{K_TREINO}_visual", ""),
                            student_plan=estudante_plano,
                            ideal_plan=st.session_state.get(f"{K_TREINO}_ideal", ""),
                        )
                        st.session_state[f"{K_TREINO}_feedback"] = feedback

                        _set_export_payload(
                            origem="Capacitação (Gemini)",
                            caso=case,
                            descricao_visual=st.session_state.get(f"{K_TREINO}_visual", ""),
                            resposta_estudante=estudante_plano,
                            plano_ideal=st.session_state.get(f"{K_TREINO}_ideal", ""),
                            feedback=feedback,
                        )

                        st.markdown("### Feedback ao estudante")
                        st.write(feedback)
                    except Exception as e:
                        st.error(f"Falhou ao gerar feedback. Detalhe: {e}")

    # (b) Esboço: após gerar caso (Treino) — pode ficar mais rico depois do feedback
    st.divider()
    st.subheader("Finalizar")

    ep = st.session_state.get("export_payload", {})
    tem_caso_treino = (str(ep.get("origem", "")).startswith("Capacitação") and bool(ep.get("caso")))

    if tem_caso_treino:
        with st.expander("🖼️ Prompt de esboço (opcional)", expanded=False):
            _render_sketch_prompt_ui(ep, key_prefix=f"{K_TREINO}_final")
    else:
        st.info("Gere um caso na capacitação para liberar o prompt de esboço.")

    # PDF da capacitação só no fim (depois de feedback)
    pronto_pdf = (
        tem_caso_treino
        and bool(str(ep.get("resposta_estudante", "")).strip())
        and bool(str(ep.get("feedback", "")).strip())
    )
    if pronto_pdf:
        pdf_bytes = _pdf_bytes_from_export_payload(ep)
        eti = "caso"
        caso = ep.get("caso")
        if isinstance(caso, dict) and caso.get("etiologia"):
            eti = str(caso.get("etiologia")).strip().lower()
        st.download_button(
            "📄 Baixar PDF da capacitação (pronto pra imprimir)",
            data=pdf_bytes,
            file_name=f"relatorio_capacitacao_{eti}.pdf".replace(" ", "_"),
            mime="application/pdf",
            key=f"{K_TREINO}_pdf_final",
            width="stretch",
        )
    else:
        st.caption("O PDF da capacitação aparece só no final: depois da resposta do estudante e do feedback.")


# ---------- TAB 3: Estudante ----------
with tabs[2]:
    st.subheader("Estudante: inserir caso clínico")

    if f"{K_ESTUDANTE}_dados" not in st.session_state:
        st.session_state[f"{K_ESTUDANTE}_dados"] = None
        st.session_state[f"{K_ESTUDANTE}_ideal"] = ""
        st.session_state[f"{K_ESTUDANTE}_feedback"] = ""
        st.session_state[f"{K_ESTUDANTE}_perguntas_caso"] = ""
        st.session_state[f"{K_ESTUDANTE}_show_ideal"] = False

    modo = st.radio(
        "Como você quer inserir o caso?",
        ["Formulário", "Texto corrido"],
        horizontal=True,
        key=f"{K_ESTUDANTE}_modo",
    )

    sim = SimuladorLogica()

    # ----- Entrada do caso -----
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

        if st.button("Avaliar caso (formulário)", key=f"{K_ESTUDANTE}_avaliar_form"):
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
            st.session_state[f"{K_ESTUDANTE}_feedback"] = ""

            st.markdown("### Relatório (core / TIME)")
            st.text(st.session_state[f"{K_ESTUDANTE}_ideal"])

            _set_export_payload(
                origem="Estudante: inserir caso (formulário)",
                caso=dados,
                plano_ideal=st.session_state[f"{K_ESTUDANTE}_ideal"],
                feedback="",
                resposta_estudante="",
            )

        st.divider()
        st.subheader("Finalizar")

        ep = st.session_state.get("export_payload", {})
        pronto_form = (
            ("formulário" in str(ep.get("origem", "")).lower())
            and bool(ep.get("caso"))
            and bool(str(ep.get("plano_ideal", "")).strip())
        )

        if pronto_form:
            # (c) Esboço: após avaliar caso (formulário)
            with st.expander("🖼️ Prompt de esboço (opcional)", expanded=False):
                _render_sketch_prompt_ui(ep, key_prefix=f"{K_ESTUDANTE}_form_final")

            # PDF SEMPRE POR ÚLTIMO
            pdf_bytes = _pdf_bytes_from_export_payload(ep)
            eti = "caso"
            caso = ep.get("caso")
            if isinstance(caso, dict) and caso.get("etiologia"):
                eti = str(caso.get("etiologia")).strip().lower()
            st.download_button(
                "📄 Baixar PDF (pronto pra imprimir)",
                data=pdf_bytes,
                file_name=f"relatorio_estudante_form_{eti}.pdf".replace(" ", "_"),
                mime="application/pdf",
                key=f"{K_ESTUDANTE}_pdf_form_final",
                width="stretch",
            )
        else:
            st.caption("Finalize clicando em **Avaliar caso (formulário)**. Aí aparecem esboço e PDF (no final).")

    else:
        st.caption("Descreva o caso em texto corrido. Se faltar dado, o sistema vai te perguntar o que falta.")
        caso_txt = st.text_area(
            "Descrição do caso (texto corrido)",
            height=220,
            key=f"{K_ESTUDANTE}_caso_texto",
        )

        colA, colB = st.columns(2)
        with colA:
            modelo_caso = st.text_input(
                "Modelo Gemini (extrair caso)",
                value="gemini-3-flash-preview",
                key=f"{K_ESTUDANTE}_model_case_tab3",
            )
        with colB:
            if st.button("Analisar caso (Gemini)", key=f"{K_ESTUDANTE}_analisar_texto"):
                if not GEMINI_API_KEY:
                    st.warning("GEMINI_API_KEY não configurada. Configure secrets/.env para usar este modo.")
                elif not caso_txt.strip():
                    st.warning("Você ainda não descreveu o caso.")
                else:
                    try:
                        from src.gemini_flow import GeminiCaseFromTextExtractor

                        ex = GeminiCaseFromTextExtractor(model=modelo_caso)
                        parsed = ex.extract_or_ask(caso_txt)

                        if parsed.get("status") == "NEED_MORE_INFO":
                            st.session_state[f"{K_ESTUDANTE}_perguntas_caso"] = parsed.get("questions", "")
                            st.session_state[f"{K_ESTUDANTE}_dados"] = None
                            st.session_state[f"{K_ESTUDANTE}_ideal"] = ""
                            st.warning("Faltam informações. Responda às perguntas abaixo e rode de novo.")
                        else:
                            dados = parsed["scenario"]
                            st.session_state[f"{K_ESTUDANTE}_dados"] = dados
                            st.session_state[f"{K_ESTUDANTE}_ideal"] = sim.avaliar(dados)
                            st.session_state[f"{K_ESTUDANTE}_perguntas_caso"] = ""
                            st.session_state[f"{K_ESTUDANTE}_feedback"] = ""

                            st.success("Caso entendido. Relatório (core) gerado.")

                            _set_export_payload(
                                origem="Estudante: inserir caso (texto corrido)",
                                caso=dados,
                                plano_ideal=st.session_state[f"{K_ESTUDANTE}_ideal"],
                                feedback="",
                                resposta_estudante="",
                            )
                    except Exception as e:
                        st.error(f"Falhou ao interpretar o texto. Detalhe: {e}")

        if st.session_state.get(f"{K_ESTUDANTE}_perguntas_caso"):
            st.markdown("### Perguntas do sistema (para completar o caso)")
            st.write(st.session_state[f"{K_ESTUDANTE}_perguntas_caso"])

        # Mostra novamente o caso interpretado + relatório core se já existirem
        if st.session_state.get(f"{K_ESTUDANTE}_dados"):
            st.markdown("### Caso estruturado (interno)")
            st.json(st.session_state[f"{K_ESTUDANTE}_dados"])

            st.markdown("### Relatório (core / TIME)")
            st.text(st.session_state[f"{K_ESTUDANTE}_ideal"])

            st.divider()
            st.subheader("Feedback (Gemini)")

            modelo_fb = st.text_input(
                "Modelo Gemini (feedback)",
                value="gemini-3-flash-preview",
                key=f"{K_ESTUDANTE}_model_feedback_tab3",
            )

            estudante_plano = st.text_area(
                "Plano de cuidado proposto pelo estudante (texto corrido):",
                height=180,
                key=f"{K_ESTUDANTE}_plano_tab3",
            )

            if st.button("Gerar feedback (Gemini)", key=f"{K_ESTUDANTE}_gerar_feedback_tab3"):
                if not estudante_plano.strip():
                    st.warning("Você ainda não escreveu o plano.")
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

                        _set_export_payload(
                            origem="Estudante: inserir caso (texto corrido)",
                            caso=st.session_state.get(f"{K_ESTUDANTE}_dados"),
                            resposta_estudante=estudante_plano,
                            plano_ideal=st.session_state.get(f"{K_ESTUDANTE}_ideal", ""),
                            feedback=feedback,
                        )

                        st.markdown("### Feedback ao estudante")
                        st.write(feedback)
                    except Exception as e:
                        st.error(f"Falhou ao gerar feedback. Detalhe: {e}")

        # (d) Finalizar: esboço após avaliar caso + feedback; PDF por último
        st.divider()
        st.subheader("Finalizar")

        ep = st.session_state.get("export_payload", {})
        pronto_texto = (
            ("texto" in str(ep.get("origem", "")).lower())
            and bool(ep.get("caso"))
            and bool(str(ep.get("resposta_estudante", "")).strip())
            and bool(str(ep.get("feedback", "")).strip())
        )

        if pronto_texto:
            with st.expander("🖼️ Prompt de esboço (opcional)", expanded=False):
                _render_sketch_prompt_ui(ep, key_prefix=f"{K_ESTUDANTE}_text_final")

            pdf_bytes = _pdf_bytes_from_export_payload(ep)
            eti = "caso"
            caso = ep.get("caso")
            if isinstance(caso, dict) and caso.get("etiologia"):
                eti = str(caso.get("etiologia")).strip().lower()
            st.download_button(
                "📄 Baixar PDF (pronto pra imprimir)",
                data=pdf_bytes,
                file_name=f"relatorio_estudante_texto_{eti}.pdf".replace(" ", "_"),
                mime="application/pdf",
                key=f"{K_ESTUDANTE}_pdf_text_final",
                width="stretch",
            )
        else:
            st.caption("No modo **Texto corrido**, o esboço e o PDF aparecem só no final (depois do plano e do feedback).")

