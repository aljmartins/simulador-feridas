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
      <img src="data:image/jpeg;base64,{data}" style="height:160px; width:auto;" />
    </div>
    """,
    unsafe_allow_html=True
)

st.markdown("<div style='height:25px;'></div>", unsafe_allow_html=True)


# INSERE Imagem
LOGO = Path(__file__).parent / "assets" / "imagem.jpeg"
IMAGEM = Path(__file__).resolve().parent / "assets" / "imagem.jpeg"
data = base64.b64encode(LOGO.read_bytes()).decode("utf-8")
st.markdown(
    f"""
    <div style="text-align:center;">
      <img src="data:image/jpeg;base64,{data}" style="height:120px; width:auto;" />
    </div>
    """,
    unsafe_allow_html=True
)

# INSERE Imagem Fim



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

# st.set_page_config(page_title="Simulador TIMERS", layout="centered")  # já definido no topo
st.markdown(
    "<h2>Simulador TIMERS – Feridas Crônicas. PET G10 UFPel</h3>",
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

    # Banner/logo do PDF (coloque o arquivo em /assets; se não existir, segue sem logo)
    # Dica: um banner horizontal funciona melhor (ex: 1600x300)
    PDF_BANNER = LOGO_PDF_BANNER
    if not PDF_BANNER.exists():
        # fallback para o logo já existente no app
        PDF_BANNER = LOGO_WEB

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


    c.save()
    buf.seek(0)
    return buf.getvalue()



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

    # Exportar PDF (também no modo Treino)
    ep = st.session_state.get("export_payload", {})
    tem_algo = any([
        bool(ep.get("caso")),
        bool(str(ep.get("plano_ideal", "")).strip()),
        bool(str(ep.get("feedback", "")).strip()),
        bool(str(ep.get("resposta_estudante", "")).strip()),
        bool(str(ep.get("descricao_visual", "")).strip()),
        bool(ep.get("images")),
    ])

    colp1, colp2 = st.columns([1, 2])
    with colp1:
        st.caption("Exportar")
    with colp2:
        if not tem_algo or (ep.get("origem") not in ["Treino (Gemini)"] and not str(ep.get("origem","")).startswith("Treino")):
            st.info("Gere um caso (e opcionalmente imagem/feedback) nesta aba para liberar o PDF do treino.")
        else:
            pdf_bytes = _pdf_bytes_from_export_payload(ep)
            eti = "caso"
            caso = ep.get("caso")
            if isinstance(caso, dict) and caso.get("etiologia"):
                eti = str(caso.get("etiologia")).strip().lower()

            st.download_button(
                "📄 Baixar PDF do treino (pronto pra imprimir)",
                data=pdf_bytes,
                file_name=f"relatorio_treino_{eti}.pdf".replace(" ", "_"),
                mime="application/pdf",
                key=f"{K_TREINO}_baixar_pdf_tab2",
                use_container_width=True,
            )

    if f"{K_TREINO}_case" not in st.session_state:
        st.session_state[f"{K_TREINO}_case"] = None
        st.session_state[f"{K_TREINO}_visual"] = ""
        st.session_state[f"{K_TREINO}_ideal"] = ""
        st.session_state[f"{K_TREINO}_feedback"] = ""
        st.session_state[f"{K_TREINO}_img_bytes"] = b""

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

            # reseta feedback/imagem anteriores
            st.session_state[f"{K_TREINO}_feedback"] = ""
            st.session_state[f"{K_TREINO}_img_bytes"] = b""

            _set_export_payload(
                origem="Treino (Gemini)",
                caso=out.scenario,
                descricao_visual=out.visual_description,
                plano_ideal=ideal,
                feedback="",
                resposta_estudante="",
                images=[],
            )

            st.success("Caso gerado. Agora você pode (opcionalmente) gerar a imagem e depois gerar o feedback.")
        except Exception as e:
            st.error(f"Falhou ao gerar caso. Verifique GEMINI_API_KEY no .env. Detalhe: {e}")

    case = st.session_state.get(f"{K_TREINO}_case")
    if not case:
        st.info("Clique em **Gerar caso (Gemini)** para iniciar o treino.")
    else:
        st.markdown("### Cenário (JSON)")
        st.json(case)

        st.markdown("### Descrição visual")
        st.write(st.session_state.get(f"{K_TREINO}_visual", ""))

        # --------- IMAGEM (Treino) ---------
        enable_img = st.toggle(
            "Ativar imagem (treino) – gerar esboço rápido via Gemini",
            value=False,
            key=f"{K_TREINO}_enable_img",
        )

        if enable_img:
            st.caption("A imagem é um esboço didático (não diagnóstico). Se sua conta/modelo não suportar imagem, o app vai avisar.")
            if st.button("Gerar imagem (Gemini)", key=f"{K_TREINO}_gerar_img"):
                try:
                    from src.gemini_flow import GeminiImageGenerator
                    ig = GeminiImageGenerator(model="imagen-3.0-generate-002")
                    img_bytes = ig.generate_image(
                        scenario=case,
                        visual_description=st.session_state.get(f"{K_TREINO}_visual", ""),
                    )
                    st.session_state[f"{K_TREINO}_img_bytes"] = img_bytes
                    _set_export_payload(images=[{"name": "imagem_treino.png", "bytes": img_bytes}])
                    st.success("Imagem gerada e anexada ao PDF do treino.")
                except Exception as e:
                    st.error(f"Não consegui gerar a imagem. Detalhe: {e}")

            img_bytes_now = st.session_state.get(f"{K_TREINO}_img_bytes") or b""
            if img_bytes_now:
                st.image(img_bytes_now, caption="Imagem do caso (Gemini) – esboço didático", use_container_width=True)

        st.divider()
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
                if not estudante_plano.strip():
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

                        # Atualiza payload do PDF do treino
                        _set_export_payload(
                            origem="Treino (Gemini)",
                            caso=case,
                            descricao_visual=st.session_state.get(f"{K_TREINO}_visual",""),
                            resposta_estudante=estudante_plano,
                            plano_ideal=st.session_state.get(f"{K_TREINO}_ideal",""),
                            feedback=feedback,
                        )

                        st.markdown("### Feedback ao estudante")
                        st.write(feedback)
                    except Exception as e:
                        st.error(f"Falhou ao gerar feedback. Verifique GEMINI_API_KEY no .env. Detalhe: {e}")


# ---------- TAB 3: Estudante insere caso + feedback robusto ----------
with tabs[2]:
    st.subheader("Estudante: inserir caso clínico")

    # Exportar PDF (robusto): gera arquivo e o usuário imprime pelo leitor de PDF (evita página em branco do iframe)
    ep = st.session_state.get("export_payload", {})
    tem_algo = any([
        bool(ep.get("caso")),
        bool(str(ep.get("plano_ideal", "")).strip()),
        bool(str(ep.get("feedback", "")).strip()),
        bool(str(ep.get("resposta_estudante", "")).strip()),
        bool(str(ep.get("descricao_visual", "")).strip()),
    ])

    colp1, colp2 = st.columns([1, 2])
    with colp1:
        st.caption("Exportar")
    with colp2:
        if not tem_algo:
            st.info("Gere algum conteúdo (caso/relatório/feedback) para liberar o PDF.")
        else:
            pdf_bytes = _pdf_bytes_from_export_payload(ep)
            eti = "caso"
            caso = ep.get("caso")
            if isinstance(caso, dict) and caso.get("etiologia"):
                eti = str(caso.get("etiologia")).strip().lower()

            st.download_button(
                "📄 Baixar PDF (pronto pra imprimir)",
                data=pdf_bytes,
                file_name=f"relatorio_timers_{eti}.pdf".replace(" ", "_"),
                mime="application/pdf",
                key=f"{K_ESTUDANTE}_baixar_pdf_tab3",
                use_container_width=True,
            )

            # Abrir PDF em nova aba (evita impressão em branco / frame)
            # Observação: o código abaixo foi desativado para evitar problemas com iframe/visualização.
            # Se quiser habilitar, remova os comentários e certifique-se de que `b64` esteja definido:
            # b64 = base64.b64encode(pdf_bytes).decode("utf-8")
            # st.markdown(
            #     f"""
            #     <a href="data:application/pdf;base64,{b64}" target="_blank"
            #        style="text-decoration:none; font-weight:600;">
            #        🖨️ Abrir PDF em nova aba (e imprimir)
            #     </a>
            #     """,
            #     unsafe_allow_html=True,
            # )


    if f"{K_ESTUDANTE}_dados" not in st.session_state:
        st.session_state[f"{K_ESTUDANTE}_dados"] = None
        st.session_state[f"{K_ESTUDANTE}_ideal"] = ""
        st.session_state[f"{K_ESTUDANTE}_feedback"] = ""
        st.session_state[f"{K_ESTUDANTE}_parsed_texto"] = None
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
            st.session_state[f"{K_ESTUDANTE}_perguntas_caso"] = ""

            st.markdown("### Relatório (core / TIME)")
            st.text(st.session_state[f"{K_ESTUDANTE}_ideal"])

            _set_export_payload(
                origem="Estudante: inserir caso (formulário)",
                caso=dados,
                plano_ideal=st.session_state[f"{K_ESTUDANTE}_ideal"],
            )

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
                if not caso_txt.strip():
                    st.warning("Você ainda não descreveu o caso.")
                else:
                    try:
                        from src.gemini_flow import GeminiCaseFromTextExtractor

                        ex = GeminiCaseFromTextExtractor(model=modelo_caso)
                        parsed = ex.extract_or_ask(caso_txt)

                        st.session_state[f"{K_ESTUDANTE}_parsed_texto"] = parsed

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

                            st.success("Caso entendido. Relatório gerado pelo core.")

                            _set_export_payload(
                                origem="Estudante: inserir caso (texto corrido)",
                                caso=dados,
                                plano_ideal=st.session_state[f"{K_ESTUDANTE}_ideal"],
                            )
                    except Exception as e:
                        st.error(f"Falhou ao interpretar o texto. Detalhe: {e}")

        if st.session_state.get(f"{K_ESTUDANTE}_perguntas_caso"):
            st.markdown("### Perguntas do sistema (para completar o caso)")
            st.write(st.session_state[f"{K_ESTUDANTE}_perguntas_caso"])


        # --- Resultado salvo da análise (não some ao avançar) ---
        parsed_saved = st.session_state.get(f"{K_ESTUDANTE}_parsed_texto")
        if parsed_saved:
            st.markdown("### Resultado: Analisar caso (Gemini)")
            if parsed_saved.get("status") == "NEED_MORE_INFO":
                st.info("Faltam dados para estruturar o caso com segurança.")
                st.write(parsed_saved.get("questions", ""))
            else:
                st.success("Caso estruturado (JSON) e relatório core preservados abaixo.")

        # Mostra novamente o caso interpretado + relatório core se já existirem (para impressão)
        if st.session_state.get(f"{K_ESTUDANTE}_dados"):
            st.markdown("### Caso interpretado (interno)")
            st.json(st.session_state[f"{K_ESTUDANTE}_dados"])

            st.markdown("### Relatório (core / TIME)")
            st.text(st.session_state[f"{K_ESTUDANTE}_ideal"])


# --------- IMAGENS DO ESTUDANTE (somente para constar no PDF) ---------
if modo == "Texto corrido":
    imgs = st.file_uploader(
        "Anexar 1–2 imagens (opcional) — entram no PDF",
        type=["png", "jpg", "jpeg"],
        accept_multiple_files=True,
        key=f"{K_ESTUDANTE}_imgs_pdf",
    )
    if imgs:
        if len(imgs) > 2:
            st.warning("Máximo de 2 imagens. Vou usar apenas as 2 primeiras.")
            imgs = imgs[:2]
        images_payload = [{"name": f.name, "bytes": f.getvalue()} for f in imgs]
        _set_export_payload(images=images_payload)
        st.caption("As imagens não são analisadas; ficam apenas no relatório PDF.")
        for f in imgs:
            st.image(f, caption=f.name, use_container_width=True)

    st.divider()
    st.subheader("Feedback robusto (Gemini)")

    if not st.session_state.get(f"{K_ESTUDANTE}_dados"):
        st.info("Primeiro finalize o caso (Formulário ou Texto corrido). Depois escreva seu plano e gere o feedback.")
    else:
        modelo_fb = st.text_input(
            "Modelo Gemini (feedback)",
            value="gemini-3-flash-preview",
            key=f"{K_ESTUDANTE}_model_feedback_tab3",
        )

        st.markdown("### Plano de cuidado proposto pelo estudante (texto corrido)")
        estudante_plano = st.text_area(
            "Explique seu raciocínio e o plano (TIME + condutas específicas):",
            height=180,
            key=f"{K_ESTUDANTE}_plano_tab3",
        )

        colx, coly = st.columns(2)
        with colx:
            if st.button("Mostrar plano ideal (core)", key=f"{K_ESTUDANTE}_mostrar_ideal_tab3"):
                st.session_state[f"{K_ESTUDANTE}_show_ideal"] = True
                st.rerun()

        with coly:
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
                        st.session_state["feedback_estudante"] = feedback

                        # após gerar feedback, também mostrar o plano ideal automaticamente
                        st.session_state[f"{K_ESTUDANTE}_show_ideal"] = True

                        _set_export_payload(
                            origem="Estudante: inserir caso",
                            caso=st.session_state.get(f"{K_ESTUDANTE}_dados"),
                            resposta_estudante=estudante_plano,
                            plano_ideal=st.session_state.get(f"{K_ESTUDANTE}_ideal", ""),
                            feedback=feedback,
                        )

                        st.rerun()

                    except Exception as e:
                        st.error(f"Falhou ao gerar feedback. Verifique GEMINI_API_KEY no .env. Detalhe: {e}")

        # --------- Resultados persistentes (não somem ao clicar em outros botões) ---------
        feedback_salvo = st.session_state.get(f"{K_ESTUDANTE}_feedback", "")
        if feedback_salvo:
            if str(feedback_salvo).strip().startswith("PRECISO DE MAIS DADOS:"):
                st.warning("Seu texto ainda está incompleto. Responda o que falta e rode novamente.")
            st.markdown("### Retorno do professor (Gemini)")
            st.write(feedback_salvo)

        if st.session_state.get(f"{K_ESTUDANTE}_show_ideal"):
            st.info("Plano ideal já está no relatório (acima).")
    # ---------- EXPORTAR RELATÓRIO (PDF) ----------
    # st.divider()
    # st.subheader("Exportar relatório (PDF)")
    #
    # Dados necessários
    # caso = st.session_state.get(f"{K_ESTUDANTE}_dados")
    # plano_ideal = st.session_state.get(f"{K_ESTUDANTE}_ideal", "")
    # resposta_estudante = st.session_state.get(f"{K_ESTUDANTE}_plano_tab3", "")
    # feedback_pdf = st.session_state.get("feedback_estudante") or st.session_state.get(f"{K_ESTUDANTE}_feedback", "")
    #
    # pronto = bool(caso) and bool(plano_ideal.strip()) and bool(str(resposta_estudante).strip()) and bool(str(feedback_pdf).strip())
    #
    # if not pronto:
    #     st.info("Para exportar o PDF, complete: caso + resposta do estudante + feedback.")
    # else:
    #     if st.button("Gerar PDF", key=f"{K_ESTUDANTE}_pdf_btn"):
    #         # Nome amigável
    #         ts = datetime.now().strftime("%Y%m%d-%H%M")
    #         eti = (caso.get("etiologia") if isinstance(caso, dict) else "caso") or "caso"
    #         nome_arquivo = f"relatorio_{eti}_{ts}.pdf".replace(" ", "_")
    #
    #         with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
    #             gerar_pdf_relatorio(
    #                 path=tmp.name,
    #                 caso=caso,
    #                 resposta_estudante=str(resposta_estudante),
    #                 plano_ideal=str(plano_ideal),
    #                 feedback=str(feedback_pdf),
    #             )
    #             with open(tmp.name, "rb") as f:
    #                 st.download_button(
    #                     label="📄 Baixar PDF",
    #                     data=f,
    #                     file_name=nome_arquivo,
    #                     mime="application/pdf",
    #                     key=f"{K_ESTUDANTE}_pdf_download",
    #                 )
