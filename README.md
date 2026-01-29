# simulador-feridas (produção)

## Chave da API (Gemini)
Crie um arquivo `.env` na raiz (não vai para o GitHub):

1) Copie `.env.exemplo` -> `.env`
2) Edite `.env` e coloque:
   GEMINI_API_KEY=...sua chave...

O app lê automaticamente do ambiente (recomendação oficial do SDK).

## Instalação (Windows)
```bat
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## Rodar (web)
```bat
streamlit run app\app_streamlit.py
```

## Rodar (CLI treino)
```bat
python scripts\run_training_cli.py
```

## Notas importantes
- O **core** está em `src/core.py` (sem Tkinter, sem Colab, sem IA).
- A geração do caso + feedback via Gemini está em `src/gemini_flow.py`.
- `google.generativeai` está depreciado; usamos `google-genai` (SDK atual).

