# -*- coding: utf-8 -*-
from dotenv import load_dotenv
from src.core import SimuladorLogica
from src.gemini_flow import GeminiCaseGenerator, GeminiFeedbackGenerator

def main():
    load_dotenv()
    gen = GeminiCaseGenerator()
    out = gen.generate_case()

    print("\n--- CENÁRIO (JSON) ---\n")
    import json
    print(json.dumps(out.scenario, indent=2, ensure_ascii=False))

    print("\n--- DESCRIÇÃO VISUAL ---\n")
    print(out.visual_description)

    sim = SimuladorLogica()
    ideal = sim.avaliar(out.scenario)

    print("\n--- RESPOSTA DO ESTUDANTE ---\n")
    student = input("Digite o plano do aluno (TIME + condutas):\n")

    fb = GeminiFeedbackGenerator()
    feedback = fb.generate_feedback(out.scenario, out.visual_description, student, ideal)

    print("\n--- FEEDBACK ---\n")
    print(feedback)

if __name__ == "__main__":
    main()
