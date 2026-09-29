import google.genai as genai
import json
from typing import Optional, List

class AgentePlanejador:
    """
    Agente responsável por receber um tema complexo e decompô-lo
    em um plano de pesquisa com perguntas específicas.
    """
    def __init__(self, client: genai.Client):
        self.client = client

    def executar(self, tema: str) -> Optional[List[str]]:
        print(f"\n[AGENTE PLANEJADOR] Criando plano de pesquisa para: '{tema}'...")
        prompt = f"""
        Você é um analista de pesquisa sênior e objetivo. Sua tarefa é receber um tópico amplo e criar um plano
        de pesquisa detalhado e abrangente, quebrando-o em 10 perguntas estritamente factuais e neutras.
        Você deve pesquisar na internet assuntos relacionados ao tema em questão.
        O objetivo é que cada pergunta possa ser respondida de forma independente por outro agente de pesquisa.
        A sua saída DEVE ser apenas uma lista em formato JSON contendo as perguntas.
        
        Tópico: "{tema}"

        Instrução de segurança: Foque apenas em aspectos econômicos e noticias.
        Evite qualquer linguagem sensível.
        A resposta deve ser puramente técnica e informativa.
        """
        try:
            response = self.client.models.generate_content(
                model="models/gemini-2.5-flash",
                contents=prompt
            )
            json_text = response.text.replace("```json", "").replace("```", "").strip()
            plano_de_pesquisa = json.loads(json_text)
            print("[AGENTE PLANEJADOR] Plano de pesquisa concluído.")
            return plano_de_pesquisa
        except Exception as e:
            print(f"[AGENTE PLANEJADOR] ERRO: {e}")
            return None

